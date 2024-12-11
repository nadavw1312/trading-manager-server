# middlewares/exception_middleware.py
from fastapi import Request, Response, logger
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from common.utils.response import error_response
import traceback

class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch unhandled exceptions and return a formatted error response.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request and continue the chain
            response = await call_next(request)
            return response
        except Exception as exc:
            # Catch unhandled exceptions and format them as an error response
            logger.logger.error(f"Unhandled exception: {exc}")

            logger.logger.error(f"Error stack trace:\n{traceback.format_exc()}")
            
            return JSONResponse(
                status_code=500,
                content=error_response(
                    message=str(exc), 
                    code=500
                )
            )
