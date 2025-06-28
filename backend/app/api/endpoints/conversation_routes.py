from fastapi import APIRouter, HTTPException, Header
import logging
from app.models.conversation import ConversationSession
from app.models import MessageModel, ConversationHistoryResponse, ConversationDeleteResponse, ErrorResponse
from .auth_utils import get_token_from_header

logger = logging.getLogger("chat_with_pdf_api")
conversation_router = APIRouter()

@conversation_router.get("/conversations/{conversation_id}", summary="Get conversation history", response_model=ConversationHistoryResponse)
def get_conversation(conversation_id: str, authorization: str = Header(...)):
    user_token = get_token_from_header(authorization)
    try:
        session = ConversationSession.load(conversation_id, user_token=user_token)
        if not session:
            logger.warning(f"Get conversation: not found {conversation_id}")
            raise HTTPException(status_code=404, detail="Conversation not found")
        history = [MessageModel(**m.to_dict()) for m in session.history]
        logger.info(f"Fetched conversation history for {conversation_id}")
        return ConversationHistoryResponse(conversation_id=session.session_id, history=history)
    except Exception as e:
        logger.error(f"Error fetching conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversation_router.delete("/conversations/{conversation_id}", summary="Reset conversation", response_model=ConversationDeleteResponse)
def reset_conversation(conversation_id: str, authorization: str = Header(...)):
    user_token = get_token_from_header(authorization)
    try:
        import os
        db_path = ConversationSession._get_db_path()
        import sqlite3
        session = ConversationSession.load(conversation_id, user_token=user_token)
        if not session:
            logger.warning(f"Reset conversation: not found {conversation_id}")
            raise HTTPException(status_code=404, detail="Conversation not found")
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM sessions WHERE session_id = ?', (conversation_id,))
            c.execute('DELETE FROM messages WHERE session_id = ?', (conversation_id,))
            conn.commit()
        logger.info(f"Reset conversation {conversation_id}")
        return {"message": f"Conversation {conversation_id} reset."}
    except Exception as e:
        logger.error(f"Error resetting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
