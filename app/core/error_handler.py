from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAPIException
from app.utils.formatters import capitalize_first

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


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles Pydantic's RequestValidationError by transforming them into a
    structured dictionary of field-level errors or a simple string for a single error.
    """
    errors = {}
    
    for error in exc.errors():
        field_name = error['loc'][-1] if len(error['loc']) > 1 else 'general'
        if field_name not in errors:
            error_msg = error['msg']
            if error_msg.startswith("Value error, "):
                error_msg = error_msg[len("Value error, "):]
            errors[field_name] = capitalize_first(error_msg)
    
    # Simplify the response for a single error
    if len(errors) == 1:
        error_detail = next(iter(errors.values()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": error_detail},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors},
        )