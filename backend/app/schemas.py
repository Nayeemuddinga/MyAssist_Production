from datetime import datetime
from pydantic import BaseModel, Field, field_validator


def _lat(v: float) -> float:
    if not -90 <= v <= 90:
        raise ValueError("latitude must be between -90 and 90")
    return v


def _lng(v: float) -> float:
    if not -180 <= v <= 180:
        raise ValueError("longitude must be between -180 and 180")
    return v


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20, pattern=r"^\+?[0-9]{7,19}$")
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(pattern=r"^(CUSTOMER|ASSISTANT)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    full_name: str


class LocationField(BaseModel):
    address: str = Field(min_length=1, max_length=300)
    lat: float
    lng: float
    _lat_validator = field_validator("lat")(_lat)
    _lng_validator = field_validator("lng")(_lng)


class CreateRequestIn(BaseModel):
    service_type: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=3, max_length=1000)
    pickup: LocationField
    destination: LocationField


class RequestOut(BaseModel):
    id: int
    customer_id: int
    assistant_id: int | None
    assistant_name: str | None
    service_type: str
    description: str
    pickup_address: str
    pickup_lat: float
    pickup_lng: float
    destination_address: str
    destination_lat: float
    destination_lng: float
    status: str
    created_at: datetime
    updated_at: datetime


class StatusUpdateOut(BaseModel):
    id: int
    status: str
    assistant_id: int | None
    updated_at: datetime
