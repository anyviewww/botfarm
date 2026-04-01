import pytest
import httpx
from datetime import datetime, timezone
from main import app

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
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
async def test_duplicate_login(client):
    await client.post("/users", json={"id": "u2", "login": "dup", "password": "p"})
    resp = await client.post("/users", json={"id": "u3", "login": "dup", "password": "p"})
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_lock_and_free(client):
    await client.post("/users", json={"id": "u4", "login": "lockme", "password": "p"})

    future = datetime.now(timezone.utc).replace(year=2026, month=4, day=10, hour=12, minute=0, second=0)
    resp = await client.post("/users/lock", json={"user_id": "u4", "locktime": future.isoformat()})
    assert resp.status_code == 200

    resp = await client.post("/users/free?user_id=u4")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "freed"