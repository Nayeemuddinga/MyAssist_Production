from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_customer
from ..errors import ApiError
from ..models import ServiceRequest, User
from ..schemas import CreateRequestIn, RequestOut, StatusUpdateOut

router = APIRouter(prefix="/api/v1/customer", tags=["customer"])


def to_out(r: ServiceRequest) -> RequestOut:
    return RequestOut(id=r.id, customer_id=r.customer_id, assistant_id=r.assistant_id, assistant_name=r.assistant.full_name if r.assistant else None, service_type=r.service_type, description=r.description, pickup_address=r.pickup_address, pickup_lat=float(r.pickup_lat), pickup_lng=float(r.pickup_lng), destination_address=r.destination_address, destination_lat=float(r.destination_lat), destination_lng=float(r.destination_lng), status=r.status, created_at=r.created_at, updated_at=r.updated_at)


def _get_own_request(db: Session, request_id: int, customer: User) -> ServiceRequest:
    r = db.get(ServiceRequest, request_id)
    if r is None or r.customer_id != customer.id:
        raise ApiError(404, "REQUEST_NOT_FOUND", "Request not found.")
    return r

@router.post("/requests", response_model=RequestOut, status_code=201)
def create_request(body: CreateRequestIn, customer: User = Depends(require_customer), db: Session = Depends(get_db)):
    r = ServiceRequest(customer_id=customer.id, service_type=body.service_type.strip(), description=body.description.strip(), pickup_address=body.pickup.address, pickup_lat=body.pickup.lat, pickup_lng=body.pickup.lng, destination_address=body.destination.address, destination_lat=body.destination.lat, destination_lng=body.destination.lng, status="PENDING")
    db.add(r); db.commit(); db.refresh(r)
    return to_out(r)

@router.get("/requests", response_model=dict)
def list_requests(customer: User = Depends(require_customer), db: Session = Depends(get_db)):
    rows = db.scalars(select(ServiceRequest).where(ServiceRequest.customer_id == customer.id).order_by(ServiceRequest.created_at.desc())).all()
    return {"items": [to_out(r).model_dump() for r in rows]}

@router.get("/requests/{request_id}", response_model=RequestOut)
def get_request(request_id: int, customer: User = Depends(require_customer), db: Session = Depends(get_db)):
    return to_out(_get_own_request(db, request_id, customer))

@router.post("/requests/{request_id}/cancel", response_model=StatusUpdateOut)
def cancel_request(request_id: int, customer: User = Depends(require_customer), db: Session = Depends(get_db)):
    r = _get_own_request(db, request_id, customer)
    if r.status != "PENDING":
        raise ApiError(409, "INVALID_STATE_TRANSITION", f"A request with status {r.status} cannot be cancelled.")
    r.status = "CANCELLED"; db.commit(); db.refresh(r)
    return StatusUpdateOut(id=r.id, status=r.status, assistant_id=r.assistant_id, updated_at=r.updated_at)
