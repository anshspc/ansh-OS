import logging
import sys
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s (req_id=%(request_id)s): %(message)s"))
handler.addFilter(RequestIdFilter())

logger = logging.getLogger("personalix")
logger.setLevel(logging.INFO)
logger.handlers = [handler]
logger.propagate = False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        
        if not request.url.path.startswith("/health") and not request.url.path.startswith("/api/v1/health"):
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({process_time:.1f}ms)",
                extra={"request_id": request_id}
            )
        return response
