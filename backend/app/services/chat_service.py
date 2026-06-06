import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Conversation

async def save_message(db, session_id, role, content, user_id=None):
    message = Conversation(
        session_id=session_id,
        role=role,
        content=content,
        user_id=user_id
    )
    db.add(message)
    await db.commit()
    return message

async def get_chat_history(db, session_id):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.asc())
    )
    return result.scalars().all()

def generate_session_id():
    return str(uuid.uuid4())
