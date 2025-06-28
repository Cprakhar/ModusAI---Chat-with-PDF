from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from app.models import ErrorResponse
import logging

logger = logging.getLogger("chat_with_pdf_api")

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=exc.detail).dict(),
        )

    @app.exception_handler(FastAPIRequestValidationError)
    async def validation_exception_handler(request: Request, exc: FastAPIRequestValidationError):
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(detail=str(exc)).dict(),
        )
