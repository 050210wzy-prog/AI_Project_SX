import json
from collections.abc import Iterator

from openai import OpenAI
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import AiConversation, KnowledgeChunk, Major, Score, Ticket
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.campus_life_service import campus_life_answer
from app.services.vector_service import query_chroma


def _intent(question: str) -> str:
    if any(word in question for word in ["分", "录取", "能上", "位次", "分数线"]):
        return "分数推荐"
    if any(word in question for word in ["对比", "比较", "区别"]):
        return "专业对比"
    if any(word in question for word in ["专业", "就业", "课程", "学院"]):
        return "专业咨询"
    return "综合咨询"


def _local_answer(db: Session, question: str, intent: str) -> ChatResponse:
    vector_hits = query_chroma(question, n_results=4)
    terms = [item for item in question.replace("，", " ").replace("。", " ").split() if item]
    chunk_query = db.query(KnowledgeChunk)
    if terms:
        filters = [KnowledgeChunk.content.like(f"%{term}%") for term in terms[:6]]
        chunk_query = chunk_query.filter(or_(*filters))
    chunks = chunk_query.limit(5).all()

    sources = []
    for hit in vector_hits:
        sources.append({"source": hit.get("source") or hit.get("category") or "向量知识库", "preview": hit["content"][:120]})
    for row in chunks:
        sources.append({"source": row.source or row.category or "知识库", "preview": row.content[:120]})

    chunk_lines = [f"- [{hit.get('source') or hit.get('category')}] {hit['content'][:220]}" for hit in vector_hits]
    chunk_lines.extend(f"- [{row.source or row.category}] {row.content[:220]}" for row in chunks)
    chunk_text = "\n".join(dict.fromkeys(chunk_lines))

    if intent == "分数推荐":
        rows = db.query(Score).order_by(Score.year.desc(), Score.min_score.desc()).limit(8).all()
        if not rows:
            return ChatResponse(intent=intent, answer="数据库还没有录取分数数据，请先在后台导入分数线。", confidence=0.35, sources=sources)
        lines = ["根据当前数据库和知识库检索结果，最近录取分数可参考："]
        for row in rows:
            lines.append(f"- {row.year}年 {row.province or ''}{row.subject or ''} {row.major}：最低分 {row.min_score}，最高分 {row.max_score}。")
        if chunk_text:
            lines.append("\n知识库依据：")
            lines.append(chunk_text)
        lines.append("\n如果要判断能否报考，请补充分数、省份、科类和位次。")
        return ChatResponse(intent=intent, answer="\n".join(lines), confidence=0.72, sources=sources)

    majors = db.query(Major).limit(8).all()
    if majors:
        lines = ["我先按本地专业库为你整理："]
        for major in majors:
            lines.append(f"- {major.name}：{major.description or ''} 就业方向：{major.jobs or '待补充'}")
        if chunk_text:
            lines.append("\n知识库依据：")
            lines.append(chunk_text)
        return ChatResponse(intent=intent, answer="\n".join(lines), confidence=0.7, sources=sources)

    return ChatResponse(intent=intent, answer="知识库暂无资料，请管理员补充专业介绍、招生数据和官网采集内容。", confidence=0.35, sources=sources)


def _finalize_response(db: Session, question: str, response: ChatResponse) -> ChatResponse:
    conv = AiConversation(
        question=question,
        answer=response.answer,
        intent=response.intent,
        confidence=response.confidence,
        sources=json.dumps(response.sources, ensure_ascii=False),
    )
    db.add(conv)
    if response.confidence < 0.55:
        db.add(
            Ticket(
                title=f"低置信度咨询：{question[:30]}",
                category=response.intent,
                question=question,
                priority="高",
                status="待处理",
                answer=response.answer[:1000],
            )
        )
    db.commit()
    response.conversation_id = conv.id
    return response


def _spark_messages(payload: ChatRequest, local: ChatResponse) -> list[dict[str, str]]:
    if payload.assistant_mode == "campus_life":
        system_prompt = (
            "你是安徽交通职业技术学院校园生活百事通助手。"
            "只能根据本地校园生活规则库和工具结果回答学生问题。"
            "如果规则里没有相关信息，要说“我不确定，建议咨询辅导员”。"
            "回答要简洁、友好，不要编造学校政策。"
        )
    else:
        system_prompt = (
            "你是安徽交通职业技术学院官网与招生咨询 AI 助手。"
            "回答要准确、清晰、面向考生、家长、在校生和访客。"
            "优先依据本地官网数据、招生数据、专业数据和官方采集内容回答；"
            "如果资料不足，要明确说明暂未获取到官方数据，并给出下一步查询建议。"
            "不要编造学校政策、录取分数、电话、网址或办事入口。"
        )
    context = (
        "以下是本系统检索到的本地依据，请结合用户问题回答。\n"
        f"意图：{local.intent}\n"
        f"本地检索结果：\n{local.answer}"
    )
    messages = [{"role": "system", "content": system_prompt}]
    for item in payload.history[-8:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": str(content)[:4000]})
    messages.append({"role": "user", "content": f"{context}\n\n用户问题：{payload.question}"})
    return messages


def _spark_extra_body(payload: ChatRequest) -> dict:
    extra = {"thinking": {"type": payload.thinking or "auto"}}
    if payload.web_search:
        extra["tools"] = [
            {
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_mode": payload.search_mode if payload.search_mode in {"normal", "deep"} else "normal",
                },
            }
        ]
    return extra


def _provider_label(provider: str) -> str:
    return {
        "spark": "星火大模型",
        "zhipu": "智谱 GLM",
        "deepseek": "DeepSeek",
        "openai": "OpenAI 兼容模型",
    }.get(provider, "大模型")


def _provider_config(payload: ChatRequest) -> tuple[str, str, str]:
    if payload.provider == "deepseek":
        return (
            payload.api_key or settings.deepseek_api_key,
            payload.base_url or settings.deepseek_base_url,
            payload.model or settings.deepseek_model,
        )
    if payload.provider == "zhipu":
        return (
            payload.api_key or settings.zhipu_api_key,
            payload.base_url or settings.zhipu_base_url,
            payload.model or settings.zhipu_model,
        )
    if payload.provider == "spark":
        return (
            payload.api_key or settings.spark_api_password,
            payload.base_url or settings.spark_base_url,
            payload.model or settings.spark_model,
        )
    return (
        payload.api_key or settings.openai_api_key,
        payload.base_url or settings.openai_base_url,
        payload.model or settings.openai_model,
    )


def ask_ai(db: Session, payload: ChatRequest) -> ChatResponse:
    if payload.assistant_mode == "campus_life":
        local = campus_life_answer(payload)
        api_key, base_url, model = _provider_config(payload)
        if not api_key:
            return _finalize_response(db, payload.question, local)

        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            result = client.chat.completions.create(
                model=model,
                messages=_spark_messages(payload, local),
                temperature=0.2,
                extra_body=_spark_extra_body(payload) if payload.provider == "spark" else None,
            )
            content = result.choices[0].message.content or local.answer
            return _finalize_response(
                db,
                payload.question,
                ChatResponse(intent=local.intent, answer=content, confidence=max(local.confidence, 0.84), sources=local.sources),
            )
        except Exception as exc:
            return _finalize_response(
                db,
                payload.question,
                ChatResponse(
                    intent=local.intent,
                    answer=f"星火大模型调用失败，已返回校园生活规则库结果。\n\n{local.answer}\n\n错误信息：{exc}",
                    confidence=local.confidence,
                    sources=local.sources,
                ),
            )

    intent = _intent(payload.question)
    local = _local_answer(db, payload.question, intent)
    api_key, base_url, model = _provider_config(payload)

    if not api_key:
        return _finalize_response(
            db,
            payload.question,
            ChatResponse(
                intent=intent,
                answer=f"{_provider_label(payload.provider)} API Key 还没有配置，当前先返回本地知识库结果。\n\n{local.answer}",
                confidence=local.confidence,
                sources=local.sources,
            ),
        )

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        result = client.chat.completions.create(
            model=model,
            messages=_spark_messages(payload, local) if payload.provider in {"spark", "deepseek", "zhipu"} else [{"role": "user", "content": payload.question}],
            temperature=0.2,
            extra_body=_spark_extra_body(payload) if payload.provider == "spark" else None,
        )
        content = result.choices[0].message.content or local.answer
        return _finalize_response(
            db,
            payload.question,
            ChatResponse(intent=intent, answer=content, confidence=max(local.confidence, 0.78), sources=local.sources),
        )
    except Exception as exc:
        return _finalize_response(
            db,
            payload.question,
            ChatResponse(
                intent=intent,
                answer=f"{_provider_label(payload.provider)}调用失败，已返回本地检索结果。\n\n{local.answer}\n\n错误信息：{exc}",
                confidence=local.confidence,
                sources=local.sources,
            ),
        )


def stream_spark_ai(db: Session, payload: ChatRequest) -> tuple[ChatResponse, Iterator[str]]:
    if payload.assistant_mode == "campus_life":
        local = campus_life_answer(payload)
        intent = local.intent
    else:
        intent = _intent(payload.question)
        local = _local_answer(db, payload.question, intent)
    api_key, base_url, model = _provider_config(payload)
    meta = ChatResponse(intent=intent, answer="", confidence=max(local.confidence, 0.78), sources=local.sources)
    provider_label = _provider_label(payload.provider)

    if not api_key:
        fallback = f"{provider_label} API Key 还没有配置，当前先返回本地知识库结果。\n\n{local.answer}"
        meta.confidence = local.confidence
        return meta, iter([fallback])

    def generator() -> Iterator[str]:
        answer_parts = []
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            stream = client.chat.completions.create(
                model=model,
                messages=_spark_messages(payload, local),
                temperature=0.2,
                stream=True,
                extra_body=_spark_extra_body(payload) if payload.provider == "spark" else None,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    answer_parts.append(content)
                    yield content
        except Exception as exc:
            fallback = f"{provider_label}流式调用失败，已返回本地检索结果。\n\n{local.answer}\n\n错误信息：{exc}"
            answer_parts.clear()
            answer_parts.append(fallback)
            yield fallback
        finally:
            answer = "".join(answer_parts).strip() or local.answer
            _finalize_response(
                db,
                payload.question,
                ChatResponse(intent=intent, answer=answer, confidence=max(local.confidence, 0.78), sources=local.sources),
            )

    return meta, generator()
