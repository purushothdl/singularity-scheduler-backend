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
    structured dictionary of field-level errors.
    """
    # This will store our formatted errors, e.g., {"email": "Error message", "password": "..."}
    errors = {}
    
    for error in exc.errors():
        # 'loc' is a tuple, e.g., ('body', 'email'). We want the field name.
        field_name = error['loc'][-1] if len(error['loc']) > 1 else 'general'
        
        # We only want to add the first error for any given field to keep it simple.
        if field_name not in errors:
            error_msg = error['msg']
            if error_msg.startswith("Value error, "):
                error_msg = error_msg[len("Value error, "):]
            errors[field_name] = capitalize_first(error_msg)
            
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )