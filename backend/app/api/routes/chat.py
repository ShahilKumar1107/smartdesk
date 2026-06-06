# chat.py — Chat endpoints

import asyncio
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatHistoryResponse, ChatMessage
from app.services.chat_service import save_message, get_chat_history, generate_session_id
from app.agent.mcp_agent import run_mcp_agent as run_agent
from app.core.dependencies import get_authenticated_user
from app.models.models import User
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    session_id = request.session_id or generate_session_id()

    await save_message(
        db=db,
        session_id=session_id,
        role="user",
        content=request.message,
        user_id=current_user.id
    )

    async def generate():
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, run_agent, request.message
            )

            await save_message(
                db=db,
                session_id=session_id,
                role="assistant",
                content=response,
                user_id=current_user.id
            )

            words = response.split(" ")
            for i, word in enumerate(words):
                chunk = word if i == len(words) - 1 else word + " "
                yield f"data: {json.dumps({'content': chunk, 'session_id': session_id})}\n\n"
                await asyncio.sleep(0.05)

            yield f"data: {json.dumps({'content': '', 'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    messages = await get_chat_history(db, session_id)
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            ChatMessage(
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )

@router.get("/sessions")
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    from sqlalchemy import select
    from app.models.models import Conversation

    result = await db.execute(
        select(Conversation.session_id, Conversation.created_at)
        .where(Conversation.user_id == current_user.id)
        .distinct(Conversation.session_id)
        .order_by(Conversation.created_at.desc())
    )
    sessions = result.fetchall()
    return {
        "sessions": [
            {"session_id": s.session_id, "created_at": s.created_at}
            for s in sessions
        ]
    }