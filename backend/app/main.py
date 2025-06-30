from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.endpoints import api_router
from app.api.endpoints.exception_handlers import add_exception_handlers
from app.api.endpoints import auth_routes

app = FastAPI(title="Chat-with-PDF API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger("chat_with_pdf_api")
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
        return response

app.add_middleware(LoggingMiddleware)

app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_routes.router, prefix="/api/v1")

add_exception_handlers(app)

limiter = Limiter(key_func=get_remote_address, default_limits=["10/second"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
