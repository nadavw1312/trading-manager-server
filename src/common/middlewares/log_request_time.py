from time import perf_counter
import logging
from fastapi import Request


async def log_request_time(request: Request, call_next):
    start_time = perf_counter()  # Start timing

    response = await call_next(request)  # Process the request

    # Calculate the duration
    duration = perf_counter() - start_time
    logging.info(f"{request.method} {request.url.path} completed in {duration:.4f} seconds")

    return response
