from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAPIException

async def custom_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Global exception handler for custom API exceptions.

    Catches instances of BaseAPIException and formats them into a
    standard JSON error response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )