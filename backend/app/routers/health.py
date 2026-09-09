from fastapi import APIRouter
from sqlalchemy import text
from ..database import engine

router = APIRouter(tags=["health"])

@router.get("/health/live")
def liveness():
    return {"status": "alive"}

@router.get("/health/ready")
def readiness():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"status": "database_unavailable"})
