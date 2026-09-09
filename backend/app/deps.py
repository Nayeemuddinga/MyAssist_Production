from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .errors import ApiError
from .models import User
from .security import ROLE_ASSISTANT, ROLE_CUSTOMER, decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise ApiError(401, "UNAUTHORIZED", "Authentication required.")
    payload = decode_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise ApiError(401, "TOKEN_INVALID", "Session expired or invalid. Please log in again.")
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise ApiError(401, "TOKEN_INVALID", "Session expired or invalid. Please log in again.")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise ApiError(401, "ACCOUNT_INACTIVE", "Account is inactive or no longer exists.")
    return user


def require_customer(user: User = Depends(get_current_user)) -> User:
    if user.role != ROLE_CUSTOMER:
        raise ApiError(403, "FORBIDDEN", "Customer access required.")
    return user


def require_assistant(user: User = Depends(get_current_user)) -> User:
    if user.role != ROLE_ASSISTANT:
        raise ApiError(403, "FORBIDDEN", "Assistant access required.")
    return user
