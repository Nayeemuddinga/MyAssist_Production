from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from .config import settings
from .middleware import RequestContextMiddleware
from .errors import ApiError, api_error_handler, validation_handler, unhandled_handler
from .routers import health, auth, customer, assistant

app = FastAPI(title="MyAssist API", version="1.0.0", docs_url=None if settings.is_production else "/docs", redoc_url=None if settings.is_production else "/redoc", openapi_url=None if settings.is_production else "/openapi.json")
app.add_middleware(RequestContextMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()], allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-Request-ID"])
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_handler)
app.add_exception_handler(Exception, unhandled_handler)
app.include_router(health.router); app.include_router(auth.router); app.include_router(customer.router); app.include_router(assistant.router)

@app.get("/")
def root():
    return {"service": "MyAssist API", "version": "1.0.0"}
