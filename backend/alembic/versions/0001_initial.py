"""initial schema

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_online", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('CUSTOMER','ASSISTANT')", name="ck_users_role"),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_table(
        "service_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assistant_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("service_type", sa.String(80), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("pickup_address", sa.String(300), nullable=False),
        sa.Column("pickup_lat", sa.Numeric(9, 6), nullable=False),
        sa.Column("pickup_lng", sa.Numeric(9, 6), nullable=False),
        sa.Column("destination_address", sa.String(300), nullable=False),
        sa.Column("destination_lat", sa.Numeric(9, 6), nullable=False),
        sa.Column("destination_lng", sa.Numeric(9, 6), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('PENDING','ACCEPTED','COMPLETED','CANCELLED')", name="ck_requests_status"),
        sa.CheckConstraint("pickup_lat BETWEEN -90 AND 90", name="ck_pickup_lat"),
        sa.CheckConstraint("pickup_lng BETWEEN -180 AND 180", name="ck_pickup_lng"),
        sa.CheckConstraint("destination_lat BETWEEN -90 AND 90", name="ck_dest_lat"),
        sa.CheckConstraint("destination_lng BETWEEN -180 AND 180", name="ck_dest_lng"),
    )
    op.create_index("ix_requests_customer", "service_requests", ["customer_id"])
    op.create_index("ix_requests_assistant", "service_requests", ["assistant_id"])
    op.create_index("ix_requests_status", "service_requests", ["status"])
    op.create_index("ix_requests_status_assistant", "service_requests", ["status", "assistant_id"])
    op.create_index("ix_requests_customer_status", "service_requests", ["customer_id", "status"])


def downgrade():
    op.drop_table("service_requests")
    op.drop_table("users")
