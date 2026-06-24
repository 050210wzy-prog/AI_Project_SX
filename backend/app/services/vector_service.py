from __future__ import annotations

import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VECTOR_DIR = ROOT / "chroma_data"


class HashEmbeddingFunction:
    def __call__(self, input):  # Chroma calls this name in recent versions.
        return [self._embed(text) for text in input]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        values = [0.0] * 384
        for token in _tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:2], "little") % len(values)
            values[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]


def _tokens(text: str) -> list[str]:
    clean = "".join(ch if "\u4e00" <= ch <= "\u9fff" or ch.isalnum() else " " for ch in text.lower())
    words = clean.split()
    chars = [clean[i : i + 2] for i in range(max(0, len(clean) - 1)) if clean[i : i + 2].strip()]
    return words + chars


def chroma_collection(name: str = "admission_kb"):
    try:
        import chromadb

        VECTOR_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(VECTOR_DIR))
        return client.get_or_create_collection(name, embedding_function=HashEmbeddingFunction())
    except Exception:
        return None


def add_chunks_to_chroma(chunks: list[dict], collection_name: str = "admission_kb", reset: bool = False) -> None:
    collection = chroma_collection(collection_name)
    if not collection or not chunks:
        return
    ids = [str(item["id"]) for item in chunks]
    if reset:
        try:
            collection.delete(ids=ids)
        except Exception:
            pass
    collection.add(
        ids=ids,
        documents=[item["content"] for item in chunks],
        metadatas=[
            {
                "source": item.get("source", ""),
                "category": item.get("category", ""),
                "question": item.get("question", ""),
            }
            for item in chunks
        ],
    )


def query_chroma(question: str, n_results: int = 4, collection_name: str = "admission_kb") -> list[dict]:
    collection = chroma_collection(collection_name)
    if not collection:
        return []
    try:
        result = collection.query(query_texts=[question], n_results=n_results)
    except Exception:
        return []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    return [
        {
            "content": doc,
            "source": meta.get("source", ""),
            "category": meta.get("category", ""),
            "question": meta.get("question", ""),
        }
        for doc, meta in zip(docs, metas)
    ]
