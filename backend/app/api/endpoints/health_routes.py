from fastapi import APIRouter
import logging
from app.models import HealthCheckResponse

logger = logging.getLogger("chat_with_pdf_api")
health_router = APIRouter()

@health_router.get("/health", summary="Health check", response_model=HealthCheckResponse)
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}
