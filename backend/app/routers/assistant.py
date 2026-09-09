from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_assistant
from ..errors import ApiError
from ..models import ServiceRequest, User
from ..schemas import RequestOut, StatusUpdateOut
from .customer import to_out

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])

@router.post("/online")
def go_online(assistant: User = Depends(require_assistant), db: Session = Depends(get_db)):
    assistant.is_online = True; db.commit()
    return {"assistant_id": assistant.id, "is_online": True}

@router.post("/offline")
def go_offline(assistant: User = Depends(require_assistant), db: Session = Depends(get_db)):
    assistant.is_online = False; db.commit()
    return {"assistant_id": assistant.id, "is_online": False}

@router.get("/jobs", response_model=dict)
def jobs(assistant: User = Depends(require_assistant), db: Session = Depends(get_db)):
    available = db.scalars(select(ServiceRequest).where(ServiceRequest.status == "PENDING").order_by(ServiceRequest.created_at.asc())).all()
    active = db.scalars(select(ServiceRequest).where(ServiceRequest.assistant_id == assistant.id, ServiceRequest.status == "ACCEPTED").order_by(ServiceRequest.created_at.asc())).all()
    completed = db.scalars(select(ServiceRequest).where(ServiceRequest.assistant_id == assistant.id, ServiceRequest.status == "COMPLETED").order_by(ServiceRequest.updated_at.desc())).all()
    return {"available": [to_out(r).model_dump() for r in available], "active": [to_out(r).model_dump() for r in active], "completed": [to_out(r).model_dump() for r in completed]}

@router.get("/jobs/{request_id}", response_model=RequestOut)
def get_job(request_id: int, assistant: User = Depends(require_assistant), db: Session = Depends(get_db)):
    r = db.get(ServiceRequest, request_id)
    if r is None or r.status == "CANCELLED":
        raise ApiError(404, "REQUEST_NOT_FOUND", "Request not found.")
    if r.status in ("ACCEPTED", "COMPLETED") and r.assistant_id != assistant.id:
        raise ApiError(403, "NOT_ASSIGNED", "You are not assigned to this job.")
    return to_out(r)

@router.post("/jobs/{request_id}/accept", response_model=StatusUpdateOut)
def accept_job(request_id: int, assistant: User = Depends(require_assistant), db: Session = Depends(get_db)):
    result = db.execute(update(ServiceRequest).where(ServiceRequest.id == request_id, ServiceRequest.status == "PENDING").values(assistant_id=assistant.id, status="ACCEPTED"))
    if result.rowcount == 0:
        if db.get(ServiceRequest, request_id) is None:
            raise ApiError(404, "REQUEST_NOT_FOUND", "Request not found.")
        raise ApiError(409, "ALREADY_ACCEPTED", "This job was just accepted by another assistant.")
    db.commit(); r = db.get(ServiceRequest, request_id)
    return StatusUpdateOut(id=r.id, status=r.status, assistant_id=r.assistant_id, updated_at=r.updated_at)

@router.post("/jobs/{request_id}/complete", response_model=StatusUpdateOut)
def complete_job(request_id: int, assistant: User = Depends(require_assistant), db: Session = Depends(get_db)):
    r = db.get(ServiceRequest, request_id)
    if r is None:
        raise ApiError(404, "REQUEST_NOT_FOUND", "Request not found.")
    if r.assistant_id != assistant.id:
        raise ApiError(403, "NOT_ASSIGNED", "You are not assigned to this job.")
    if r.status != "ACCEPTED":
        raise ApiError(409, "INVALID_STATE_TRANSITION", f"A request with status {r.status} cannot be completed.")
    r.status = "COMPLETED"; db.commit(); db.refresh(r)
    return StatusUpdateOut(id=r.id, status=r.status, assistant_id=r.assistant_id, updated_at=r.updated_at)
