from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from .config import settings


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(exc.status, content=error_body(exc.code, exc.message))


async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", [])[1:]) or "body"
    return JSONResponse(422, content=error_body("VALIDATION_ERROR", f"Invalid value for '{field}'"))


async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
    if not settings.is_production:
        import traceback
        traceback.print_exc()
    return JSONResponse(HTTP_500_INTERNAL_SERVER_ERROR, content=error_body("INTERNAL_ERROR", "An unexpected error occurred."))
