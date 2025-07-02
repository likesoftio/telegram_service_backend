import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_auth_telegram(monkeypatch):
    # Мокаем функцию проверки подписи Telegram, чтобы не вычислять реальный hash
    monkeypatch.setattr("app.api.auth.check_telegram_auth", lambda data, token: True)
    payload = {
        "id": 123456,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "auth_date": 1700000000,
        "hash": "fakehash"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json=payload)
        assert resp.status_code == 200
        tokens = resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        # Проверяем refresh
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
        resp2 = await ac.post("/auth/refresh", headers=headers)
        assert resp2.status_code == 200
        assert "access_token" in resp2.json()
        # Проверяем /me
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        resp3 = await ac.get("/me", headers=headers)
        assert resp3.status_code == 200
        data = resp3.json()
        assert data["username"] == "testuser" 