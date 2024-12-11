# middlewares/response_middleware.py
import json
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from common.utils.response import success_response

async def ensure_success_response_middleware(request: Request, call_next):
    """
    Middleware to ensure that all non-exception responses are wrapped in a success_response.
    Skips processing for specific routes like '/docs' and '/redoc'.
    """
    # Skip documentation routes and static files
    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/openapi"):
        return await call_next(request)

    response = await call_next(request)

    if response.status_code == 200:  # Only wrap successful 200 responses
        try:
            # Get the response body
            response_body = [section async for section in response.body_iterator]
            
            # If the response body is empty, don't attempt to decode it
            if not response_body or not response_body[0].strip():
                return response  # Skip wrapping for empty responses

            # Try decoding the response body as JSON
            try:
                original_data = json.loads(response_body[0].decode())
            except json.JSONDecodeError:
                # If it's not valid JSON, skip wrapping
                return response

            # Transform '_id' to 'id' in the response data
            if isinstance(original_data, dict):
                if '_id' in original_data:
                    original_data['id'] = original_data.pop('_id')
            elif isinstance(original_data, list):
                for item in original_data:
                    if isinstance(item, dict) and '_id' in item:
                        item['id'] = item.pop('_id')

            # Check if the response is already in the success_response format
            if not isinstance(original_data, dict) or "status" not in original_data or original_data["status"] != "success":
                # Wrap the original response in the success_response format
                wrapped_data = success_response(data=original_data)
                return JSONResponse(content=wrapped_data, status_code=200)
            else:
                # If the response is already in success_response format, return it as is
                return response

        except Exception as e:
            # If any exception occurs during the process, let the ExceptionMiddleware handle it
            raise e
    else:
        # For non-200 status codes, return the response as is (will be handled by ExceptionMiddleware)
        return response
