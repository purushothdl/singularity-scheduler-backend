import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.log_config import logger

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to measure the time taken for each request."""

    async def dispatch(self, request: Request, call_next):
        """
        Intercepts the request to measure the elapsed time and logs it.

        Args:
            request (Request): The incoming HTTP request.
            call_next: The next middleware or endpoint to call.

        Returns:
            Response: The HTTP response.
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Request to {request.url.path} took {elapsed_time:.4f} seconds.")
        
        return response
