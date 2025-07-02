import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_channel_crud(monkeypatch):
    monkeypatch.setattr("app.api.auth.check_telegram_auth", lambda data, token: True)
    payload = {
        "id": 123459,
        "username": "chanuser",
        "first_name": "Chan",
        "last_name": "User",
        "auth_date": 1700000003,
        "hash": "fakehash"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json=payload)
        tokens = resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        # Создать проект, подпроект, интеграцию
        project = (await ac.post("/projects", json={"name": "ChanProj"}, headers=headers)).json()
        subproject = (await ac.post("/subprojects", json={"name": "ChanSub", "project_id": project["id"]}, headers=headers)).json()
        integration = (await ac.post("/telegram/integrations", json={"type": "bot", "name": "TestBot", "bot_token": "123:ABC"}, headers=headers)).json()
        # Создать канал
        resp2 = await ac.post("/channels", json={"integration_id": integration["id"], "subproject_id": subproject["id"], "channel_id": "@testchan", "channel_title": "Test Channel"}, headers=headers)
        assert resp2.status_code == 200
        channel = resp2.json()
        # Получить список каналов
        resp3 = await ac.get("/channels", headers=headers)
        assert resp3.status_code == 200
        assert any(c["channel_id"] == "@testchan" for c in resp3.json()) 