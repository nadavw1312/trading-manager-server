# utils/response.py
from typing import Any, Optional

def success_response(data: Any = None, message: str = "Success"):
    """
    Returns a standard success response.
    """
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def error_response(message: str, code: int, data: Optional[Any] = None):
    """
    Returns a standard error response.
    """
    return {
        "status": "error",
        "message": message,
        "code": code,
        "data": data
    }
