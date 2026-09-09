import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("myassist")
logging.basicConfig(level=logging.INFO, format='%(message)s')
REDACTED_PATHS = ("/api/v1/auth/",)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        if not any(request.url.path.startswith(p) for p in REDACTED_PATHS):
            logger.info({"request_id": request_id, "method": request.method, "path": request.url.path, "status": response.status_code, "duration_ms": duration_ms})
        return response
