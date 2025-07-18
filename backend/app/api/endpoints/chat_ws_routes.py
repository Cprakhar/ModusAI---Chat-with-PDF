from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
import logging
from app.services.vector_store import VectorStore
from app.services.llm_client import LLMClient
from app.services.rag_engine import RAGEngine
from app.models.conversation import ConversationSession
from app.utils.citations import extract_citations_from_chunks
from app.utils.deps import verify_token
from app.models import CitationModel
import jwt
import os

logger = logging.getLogger("chat_with_pdf_api")
chat_ws_router = APIRouter()

JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")

def verify_user_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except Exception:
        return None

def get_vector_store():
    return VectorStore()

def get_llm_client():
    return LLMClient()

@chat_ws_router.websocket("/chat/stream")
async def chat_stream(
    websocket: WebSocket,
    conversation_id: str = Query(...),
    message: str = Query(...),
    token: str = Query(...),
):
    await websocket.accept()
    logger.debug(f"[MultiTurnWS] Token received: {token}")
    user_id = verify_user_jwt(token)
    if not user_id:
        await websocket.send_json({"error": "Invalid or missing token"})
        await websocket.close()
        return
    try:
        session = ConversationSession.load(conversation_id, user_token=token)
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
        if hasattr(llm_client, 'chat_stream'):
            async for chunk in llm_client.chat_stream(message, context):
                await websocket.send_json({"token": chunk})
                full_response += chunk
        else:
            full_response = llm_client.chat(message, context)
            await websocket.send_json({"token": full_response})
        session.add_message("assistant", full_response)
        session.save(user_token=token)
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


@chat_ws_router.websocket("/chat/deep_query/stream")
async def deep_query_stream(websocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        document_id = data.get("document_id")
        query = data.get("query")
        token = data.get("token")
        logger.debug(f"[DeepDiveWS] Token received: {token}")
        logger.debug(f"[DeepDiveWS] Received request: document_id={document_id}, query={query}")
        if not token:
            await websocket.send_json({"error": "Authentication token required."})
            await websocket.close()
            return
        try:
            user = verify_token(token)
        except Exception as e:
            logger.warning(f"[DeepDiveWS] Invalid token: {e}")
            await websocket.send_json({"error": "Invalid or expired token."})
            await websocket.close()
            return
        if not document_id or not query or not query.strip():
            await websocket.send_json({"error": "document_id and non-empty query are required."})
            await websocket.close()
            return
        vector_store = get_vector_store()
        llm_client = get_llm_client()
        rag = RAGEngine(vector_store, document_id)
        retrieved = rag.retrieve(query)
        context = rag.aggregate_context(retrieved)
        answer_gen = llm_client.deep_dive(query, context)
        answer = ""
        async for token in answer_gen:
            logger.debug(f"[DeepDiveWS] Streaming token: {token}")
            answer += token
            await websocket.send_json({"token": token})
        citations = [CitationModel(**c.to_dict()) for c in extract_citations_from_chunks(retrieved, answer)]
        logger.debug(f"[DeepDiveWS] Final answer: {answer}")
        logger.debug(f"[DeepDiveWS] Citations: {citations}")
        await websocket.send_json({"citations": [c.model_dump() for c in citations], "done": True})
        await websocket.close()
    except Exception as e:
        logger.error(f"[DeepDiveWS] Error: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()

