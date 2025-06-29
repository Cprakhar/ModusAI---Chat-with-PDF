from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
import logging
from app.services.vector_store import VectorStore
from app.services.llm_client import LLMClient
from app.services.rag_engine import RAGEngine
from app.models.conversation import ConversationSession
from app.utils.citations import extract_citations_from_chunks
from app.utils.deps import get_current_user
import jwt
import os

logger = logging.getLogger("chat_with_pdf_api")
chat_ws_router = APIRouter()

JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

def verify_user_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except Exception:
        return None

@chat_ws_router.websocket("/chat/stream")
async def chat_stream(
    websocket: WebSocket,
    conversation_id: str = Query(...),
    message: str = Query(...),
    token: str = Query(...),
    user: dict = Depends(get_current_user)
):
    await websocket.accept()
    user_id = user["payload"].get("user_id")
    if not user_id:
        await websocket.send_json({"error": "Invalid or missing token"})
        await websocket.close()
        return
    try:
        session = ConversationSession.load(conversation_id, user_token=user["token"])
        if not session:
            await websocket.send_json({"error": "Conversation not found"})
            await websocket.close()
            return
        session.add_message("user", message)
        vector_store = VectorStore()
        rag = RAGEngine(vector_store, session.document_id)
        retrieved = rag.retrieve(message)
        context = rag.aggregate_conversation_context(
            [m.content for m in session.history], retrieved
        )
        llm_client = LLMClient()
        full_response = ""
        # Stream tokens/chunks if supported
        if hasattr(llm_client, 'chat_stream'):
            async for chunk in llm_client.chat_stream(message, context):
                await websocket.send_json({"token": chunk})
                full_response += chunk
        else:
            # Fallback: not streaming, just get the full answer
            full_response = llm_client.chat(message, context)
            await websocket.send_json({"token": full_response})
        # Save assistant response
        session.add_message("assistant", full_response)
        session.save(user_token=user["token"])
        citations = [c.to_dict() for c in extract_citations_from_chunks(retrieved, full_response)]
        await websocket.send_json({
            "citations": citations,
            "conversation_id": session.session_id,
            "done": True
        })
        await websocket.close()
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()
