from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (CheckConstraint("role IN ('CUSTOMER','ASSISTANT')", name="ck_users_role"),)


class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    assistant_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    service_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    pickup_address: Mapped[str] = mapped_column(String(300), nullable=False)
    pickup_lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    pickup_lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    destination_address: Mapped[str] = mapped_column(String(300), nullable=False)
    destination_lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    destination_lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    customer = relationship("User", foreign_keys=[customer_id])
    assistant = relationship("User", foreign_keys=[assistant_id])
    __table_args__ = (
        CheckConstraint("status IN ('PENDING','ACCEPTED','COMPLETED','CANCELLED')", name="ck_requests_status"),
        CheckConstraint("pickup_lat BETWEEN -90 AND 90", name="ck_pickup_lat"),
        CheckConstraint("pickup_lng BETWEEN -180 AND 180", name="ck_pickup_lng"),
        CheckConstraint("destination_lat BETWEEN -90 AND 90", name="ck_dest_lat"),
        CheckConstraint("destination_lng BETWEEN -180 AND 180", name="ck_dest_lng"),
        Index("ix_requests_status_assistant", "status", "assistant_id"),
    )
