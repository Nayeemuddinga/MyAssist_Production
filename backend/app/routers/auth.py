from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..errors import ApiError
from ..models import User
from ..ratelimit import rate_limit_auth
from ..schemas import RegisterRequest, TokenResponse
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201, dependencies=[Depends(rate_limit_auth)])
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.phone == body.phone)) is not None:
        raise ApiError(409, "PHONE_TAKEN", "An account with this phone number already exists.")
    user = User(phone=body.phone, full_name=body.full_name.strip(), password_hash=hash_password(body.password), role=body.role)
    db.add(user); db.commit(); db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id, user.role), user_id=user.id, role=user.role, full_name=user.full_name)

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_auth)])
def login(phone: str = Query(...), password: str = Query(...), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.phone == phone))
    if user is None or not verify_password(password, user.password_hash):
        raise ApiError(401, "INVALID_CREDENTIALS", "Invalid phone number or password.")
    if not user.is_active:
        raise ApiError(403, "ACCOUNT_INACTIVE", "This account has been deactivated.")
    return TokenResponse(access_token=create_access_token(user.id, user.role), user_id=user.id, role=user.role, full_name=user.full_name)

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "phone": user.phone, "full_name": user.full_name, "role": user.role, "is_online": user.is_online}
