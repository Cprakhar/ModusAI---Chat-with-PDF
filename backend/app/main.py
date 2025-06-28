from fastapi import FastAPI

from app.api.endpoints import api_router
from app.api.endpoints.exception_handlers import add_exception_handlers

app = FastAPI(title="Chat-with-PDF API")

# Register all modular routers under /api/v1
app.include_router(api_router, prefix="/api/v1")

# Register global exception handlers
add_exception_handlers(app)
