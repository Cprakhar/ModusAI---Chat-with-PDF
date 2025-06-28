from fastapi import APIRouter, Body, Depends, HTTPException, Header
import logging
from app.services.vector_store import VectorStore
from app.services.llm_client import LLMClient
from app.services.rag_engine import RAGEngine
from app.models.conversation import ConversationSession
from app.utils.citations import extract_citations_from_chunks
from app.models import ChatMessageRequest, ChatMessageResponse, DeepQueryRequest, DeepQueryResponse, CitationModel, ErrorResponse
from .auth_utils import get_token_from_header

logger = logging.getLogger("chat_with_pdf_api")
chat_router = APIRouter()

def get_vector_store():
    return VectorStore()

def get_llm_client():
    return LLMClient()

@chat_router.post("/chat/message", summary="Multi-turn chat message", response_model=ChatMessageResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def chat_message(
    req: ChatMessageRequest = Body(...),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_client: LLMClient = Depends(get_llm_client),
    authorization: str = Header(...)
):
    user_token = get_token_from_header(authorization)
    if not req.conversation_id or not req.message or not req.message.strip():
        logger.warning(f"Chat message rejected: missing conversation_id or empty message")
        raise HTTPException(status_code=400, detail="conversation_id and non-empty message are required.")
    if len(req.message) > 2000:
        logger.warning(f"Chat message rejected: message too long")
        raise HTTPException(status_code=400, detail="Message too long (max 2000 characters).")
    try:
        session = ConversationSession.load(req.conversation_id, user_token=user_token)
        if not session:
            logger.warning(f"Chat message: conversation not found {req.conversation_id}")
            raise HTTPException(status_code=404, detail="Conversation not found")
        session.add_message("user", req.message)
        rag = RAGEngine(vector_store, session.document_id)
        retrieved = rag.retrieve(req.message)
        context = rag.aggregate_conversation_context(
            [m.content for m in session.history], retrieved
        )
        answer = llm_client.chat(req.message, context)
        session.add_message("assistant", answer)
        session.save(user_token=user_token)
        citations = [CitationModel(**c.to_dict()) for c in extract_citations_from_chunks(retrieved, answer)]
        logger.info(f"Chat message processed for conversation {session.session_id}")
        return ChatMessageResponse(response=answer, citations=citations, conversation_id=session.session_id)
    except Exception as e:
        logger.error(f"Error in chat_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/chat/deep-query", summary="Single deep-dive query", response_model=DeepQueryResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def deep_query(
    req: DeepQueryRequest = Body(...),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_client: LLMClient = Depends(get_llm_client)
):
    if not req.document_id or not req.query or not req.query.strip():
        logger.warning(f"Deep query rejected: missing document_id or empty query")
        raise HTTPException(status_code=400, detail="document_id and non-empty query are required.")
    if len(req.query) > 2000:
        logger.warning(f"Deep query rejected: query too long")
        raise HTTPException(status_code=400, detail="Query too long (max 2000 characters).")
    try:
        rag = RAGEngine(vector_store, req.document_id)
        retrieved = rag.retrieve(req.query)
        context = rag.aggregate_context(retrieved)
        answer = llm_client.deep_dive(req.query, context)
        if hasattr(answer, '__iter__') and not isinstance(answer, str):
            answer = "".join(list(answer))
        citations = [CitationModel(**c.to_dict()) for c in extract_citations_from_chunks(retrieved, answer)]
        logger.info(f"Deep query processed for document {req.document_id}")
        return DeepQueryResponse(response=answer, citations=citations)
    except Exception as e:
        logger.error(f"Error in deep_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
