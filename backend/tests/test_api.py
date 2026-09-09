import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_myassist.db")
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_ENGINE = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=TEST_ENGINE, autoflush=False, expire_on_commit=False)

def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_db

BASE = "http://test"
CUST = {"phone": "+911234567801", "full_name": "Test Customer", "password": "Password1!", "role": "CUSTOMER"}
ASST = {"phone": "+911234567802", "full_name": "Test Assistant", "password": "Password1!", "role": "ASSISTANT"}
ASST2 = {"phone": "+911234567803", "full_name": "Assistant Two", "password": "Password1!", "role": "ASSISTANT"}
REQ = {"service_type": "Shopping", "description": "Get rice from nearby store", "pickup": {"address": "Main Street", "lat": 12.971599, "lng": 77.594566}, "destination": {"address": "Customer Home", "lat": 12.935227, "lng": 77.624599}}

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(TEST_ENGINE)
    Base.metadata.create_all(TEST_ENGINE)
    yield
    Base.metadata.drop_all(TEST_ENGINE)

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE) as c:
        yield c

async def register(client, body):
    response = await client.post("/api/v1/auth/register", json=body)
    assert response.status_code == 201
    return response.json()

async def auth_headers(client, body):
    response = await client.post("/api/v1/auth/login", params={"phone": body["phone"], "password": body["password"]})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

@pytest.mark.anyio
async def test_register_login_and_me(client):
    await register(client, CUST)
    headers = await auth_headers(client, CUST)
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["role"] == "CUSTOMER"

@pytest.mark.anyio
async def test_duplicate_registration(client):
    await register(client, CUST)
    response = await client.post("/api/v1/auth/register", json=CUST)
    assert response.status_code == 409

@pytest.mark.anyio
async def test_customer_request_lifecycle(client):
    await register(client, CUST)
    await register(client, ASST)
    customer_headers = await auth_headers(client, CUST)
    assistant_headers = await auth_headers(client, ASST)
    response = await client.post("/api/v1/customer/requests", json=REQ, headers=customer_headers)
    assert response.status_code == 201
    request_id = response.json()["id"]
    response = await client.post(f"/api/v1/assistant/jobs/{request_id}/accept", headers=assistant_headers)
    assert response.status_code == 200
    response = await client.post(f"/api/v1/assistant/jobs/{request_id}/complete", headers=assistant_headers)
    assert response.json()["status"] == "COMPLETED"

@pytest.mark.anyio
async def test_cancel_pending_only(client):
    await register(client, CUST)
    headers = await auth_headers(client, CUST)
    request_id = (await client.post("/api/v1/customer/requests", json=REQ, headers=headers)).json()["id"]
    response = await client.post(f"/api/v1/customer/requests/{request_id}/cancel", headers=headers)
    assert response.json()["status"] == "CANCELLED"
    response = await client.post(f"/api/v1/customer/requests/{request_id}/cancel", headers=headers)
    assert response.status_code == 409

@pytest.mark.anyio
async def test_duplicate_accept_conflict(client):
    await register(client, CUST)
    await register(client, ASST)
    await register(client, ASST2)
    customer_headers = await auth_headers(client, CUST)
    first = await auth_headers(client, ASST)
    second = await auth_headers(client, ASST2)
    request_id = (await client.post("/api/v1/customer/requests", json=REQ, headers=customer_headers)).json()["id"]
    assert (await client.post(f"/api/v1/assistant/jobs/{request_id}/accept", headers=first)).status_code == 200
    assert (await client.post(f"/api/v1/assistant/jobs/{request_id}/accept", headers=second)).status_code == 409

@pytest.mark.anyio
async def test_wrong_assistant_cannot_complete(client):
    await register(client, CUST)
    await register(client, ASST)
    await register(client, ASST2)
    customer_headers = await auth_headers(client, CUST)
    first = await auth_headers(client, ASST)
    second = await auth_headers(client, ASST2)
    request_id = (await client.post("/api/v1/customer/requests", json=REQ, headers=customer_headers)).json()["id"]
    await client.post(f"/api/v1/assistant/jobs/{request_id}/accept", headers=first)
    assert (await client.post(f"/api/v1/assistant/jobs/{request_id}/complete", headers=second)).status_code == 403
