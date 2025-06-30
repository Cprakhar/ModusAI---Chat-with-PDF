from fastapi import APIRouter, HTTPException, Depends
import logging
from app.models.conversation import ConversationSession
from app.models import MessageModel, ConversationHistoryResponse, ConversationDeleteResponse
from app.utils.deps import get_current_user

logger = logging.getLogger("chat_with_pdf_api")
conversation_router = APIRouter()

@conversation_router.get("/conversations/{conversation_id}", summary="Get conversation history", response_model=ConversationHistoryResponse)
def get_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    user_token = user["token"]
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
def reset_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    user_token = user["token"]
    try:
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

@conversation_router.get("/conversations/by-document/{document_id}", summary="Get conversation by document_id for current user")
def get_conversation_by_document(document_id: str, user: dict = Depends(get_current_user)):
    user_token = user["token"]
    user_id = user["payload"].get("user_id")
    try:
        session = ConversationSession.find_by_document_and_user(document_id, user_id, user_token=user_token)
        if not session:
            logger.warning(f"No conversation found for document {document_id} and user {user_id}")
            raise HTTPException(status_code=404, detail="Conversation not found for this document and user")
        return {"conversation_id": session.session_id}
    except Exception as e:
        logger.error(f"Error finding conversation for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversation_router.get("/conversations", summary="List all conversations for current user")
def list_conversations(user: dict = Depends(get_current_user)):
    user_token = user["token"]
    user_id = user["payload"].get("user_id")
    try:
        ConversationSession._init_db()
        db_path = ConversationSession._get_db_path()
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT session_id, document_id, updated_at FROM sessions WHERE user_id = ? ORDER BY updated_at DESC''', (user_id,))
            rows = c.fetchall()
            conversations = []
            for row in rows:
                session_id, document_id, updated_at = row
                c.execute('''SELECT content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 1''', (session_id,))
                last_msg_row = c.fetchone()
                last_message = last_msg_row[0] if last_msg_row else ""
                conversations.append({
                    "id": session_id,
                    "title": f"Document {document_id}",
                    "lastMessage": last_message,
                    "date": updated_at,
                })
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error listing conversations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
