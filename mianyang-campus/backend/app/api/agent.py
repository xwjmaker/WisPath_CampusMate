from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationMessage
from app.schemas.agent import ChatRequest
from app.services.agent_service import chat

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat")
async def chat_api(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv_id = req.conversation_id
    if conv_id:
        conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == user.id).first()
        if not conv:
            raise HTTPException(404, "对话不存在")
    else:
        conv = Conversation(user_id=user.id, title="新对话")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id

    # Save user message
    db.add(ConversationMessage(conversation_id=conv_id, role="user", content=req.message))
    db.commit()

    return StreamingResponse(
        chat(req.message, req.history, user, conv_id=conv_id, file_url=req.file_url),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
