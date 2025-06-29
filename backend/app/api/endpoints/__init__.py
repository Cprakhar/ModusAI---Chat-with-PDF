from fastapi import APIRouter
from .document_routes import document_router
from .chat_routes import chat_router
from .conversation_routes import conversation_router
from .health_routes import health_router
from .chat_ws_routes import chat_ws_router
from .auth_routes import auth_router

api_router = APIRouter()
api_router.include_router(document_router)
api_router.include_router(chat_router)
api_router.include_router(conversation_router)
api_router.include_router(health_router)
api_router.include_router(chat_ws_router)
api_router.include_router(auth_router)
