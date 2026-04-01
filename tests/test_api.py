import pytest
import pytest_asyncio
import httpx
from datetime import datetime, timezone
from main import app

@pytest_asyncio.fixture(scope="function")
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c

@pytest.mark.asyncio
async def test_create_user(client):
    resp = await client.post("/users", json={
        "id": "u1",
        "login": "test1",
        "password": "pass",
        "env": "prod"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["login"] == "test1"
    assert data["env"] == "prod"

@pytest.mark.asyncio
async def test_create_user_duplicate(client):
    await client.post("/users", json={"id": "dup1", "login": "dup", "password": "p"})
    resp = await client.post("/users", json={"id": "dup2", "login": "dup", "password": "p"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Login already exists"

@pytest.mark.asyncio
async def test_get_users_empty(client):
    resp = await client.get("/users")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_get_users_with_data(client):
    await client.post("/users", json={"id": "list1", "login": "listuser", "password": "p"})
    resp = await client.get("/users")
    assert resp.status_code == 200
    users = resp.json()
    assert any(u["login"] == "listuser" for u in users)

@pytest.mark.asyncio
async def test_lock_user(client):
    await client.post("/users", json={"id": "lock1", "login": "lockuser", "password": "p"})
    
    future = datetime.now(timezone.utc).replace(year=2026, month=4, day=10, hour=12)
    resp = await client.post("/users/lock", json={
        "user_id": "lock1",
        "locktime": future.isoformat()
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "locked"

@pytest.mark.asyncio
async def test_lock_user_not_found(client):
    resp = await client.post("/users/lock", json={
        "user_id": "nonexistent",
        "locktime": "2026-04-10T12:00:00Z"
    })
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_lock_user_already_locked(client):
    await client.post("/users", json={"id": "lock2", "login": "lockuser2", "password": "p"})
    future1 = datetime.now(timezone.utc).replace(year=2026, month=4, day=10, hour=12)
    await client.post("/users/lock", json={
        "user_id": "lock2",
        "locktime": future1.isoformat()
    })
    
    future2 = datetime.now(timezone.utc).replace(year=2026, month=4, day=11, hour=12)
    resp = await client.post("/users/lock", json={
        "user_id": "lock2",
        "locktime": future2.isoformat()
    })
    assert resp.status_code == 409
    assert resp.json()["detail"] == "User already locked"

@pytest.mark.asyncio
async def test_free_user(client):
    await client.post("/users", json={"id": "free1", "login": "freeuser", "password": "p"})
    await client.post("/users/lock", json={
        "user_id": "free1",
        "locktime": "2026-04-10T12:00:00Z"
    })
    
    resp = await client.post("/users/free?user_id=free1")
    assert resp.status_code == 200
    assert resp.json()["status"] == "freed"

@pytest.mark.asyncio
async def test_free_user_not_found(client):
    resp = await client.post("/users/free?user_id=nonexistent")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

# === Тесты health и root эндпоинтов ===
@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "botofarma"}

@pytest.mark.asyncio
async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "Botofarma Microservice"
    assert "docs" in data
    assert "health" in data