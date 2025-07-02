import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_project_crud(monkeypatch):
    monkeypatch.setattr("app.api.auth.check_telegram_auth", lambda data, token: True)
    payload = {
        "id": 123457,
        "username": "projuser",
        "first_name": "Proj",
        "last_name": "User",
        "auth_date": 1700000001,
        "hash": "fakehash"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json=payload)
        tokens = resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        # Создать проект
        resp2 = await ac.post("/projects", json={"name": "Test Project"}, headers=headers)
        assert resp2.status_code == 200
        project = resp2.json()
        # Получить список проектов
        resp3 = await ac.get("/projects", headers=headers)
        assert resp3.status_code == 200
        assert any(p["name"] == "Test Project" for p in resp3.json())
        # Создать подпроект
        resp4 = await ac.post("/subprojects", json={"name": "Sub", "project_id": project["id"]}, headers=headers)
        assert resp4.status_code == 200
        subproject = resp4.json()
        # Получить список подпроектов
        resp5 = await ac.get("/subprojects", headers=headers)
        assert resp5.status_code == 200
        assert any(s["name"] == "Sub" for s in resp5.json()) 