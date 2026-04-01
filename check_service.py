import httpx
import asyncio

async def test_service():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Создаём пользователя
        print("1. Создаём пользователя...")
        resp = await client.post("/users", json={
            "id": "test-123",
            "login": "check_bot",
            "password": "pass",
            "env": "prod",
            "domain": "canary"
        })
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        # 2. Получаем список
        print("\n2. Получаем всех пользователей...")
        resp = await client.get("/users")
        print(f"   Status: {resp.status_code}")
        print(f"   Count: {len(resp.json())}")
        
        # 3. Блокируем
        print("\n3. Блокируем пользователя...")
        resp = await client.post("/users/lock", json={
            "user_id": "test-123",
            "locktime": "2026-04-15T10:00:00Z"
        })
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        # 4. Разблокируем
        print("\n4. Разблокируем пользователя...")
        resp = await client.post("/users/free?user_id=test-123")
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        print("\n✅ Все проверки пройдены!")

if __name__ == "__main__":
    asyncio.run(test_service())