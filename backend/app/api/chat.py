import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AiFeedback, Ticket
from app.schemas.schemas import ChatRequest, ChatResponse, FeedbackPayload, TicketCreate
from app.services.ai_service import ask_ai, stream_spark_ai

router = APIRouter(prefix="/chat", tags=["AI问答"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return ask_ai(db, payload)


@router.post("/stream")
def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    response, chunks = stream_spark_ai(db, payload)

    async def event_stream():
        meta = {"conversation_id": response.conversation_id, "confidence": response.confidence, "sources": response.sources}
        yield f"data: {json.dumps({'type': 'meta', 'data': meta}, ensure_ascii=False)}\n\n"
        for chunk in chunks:
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/feedback")
def feedback(payload: FeedbackPayload, db: Session = Depends(get_db)) -> dict:
    db.add(
        AiFeedback(
            conversation_id=payload.conversation_id,
            question=payload.question,
            answer=payload.answer,
            sentiment=payload.sentiment,
            suggestion=payload.suggestion,
        )
    )
    db.commit()
    return {"success": True}


@router.post("/tickets")
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> dict:
    row = Ticket(
        title=payload.title,
        category=payload.category,
        question=payload.question,
        contact=payload.contact,
        priority="普通",
        status="待处理",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"success": True, "id": row.id}
