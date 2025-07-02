import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_message_moderation(monkeypatch):
    monkeypatch.setattr("app.api.auth.check_telegram_auth", lambda data, token: True)
    payload = {
        "id": 123460,
        "username": "msguser",
        "first_name": "Msg",
        "last_name": "User",
        "auth_date": 1700000004,
        "hash": "fakehash"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json=payload)
        tokens = resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        # Создать проект, подпроект, промпт, версию, интеграцию, канал, сообщение
        project = (await ac.post("/projects", json={"name": "MsgProj"}, headers=headers)).json()
        subproject = (await ac.post("/subprojects", json={"name": "MsgSub", "project_id": project["id"]}, headers=headers)).json()
        prompt = (await ac.post("/prompts", json={"name": "MsgPrompt", "description": "desc", "subproject_id": subproject["id"]}, headers=headers)).json()
        (await ac.post(f"/prompts/{prompt['id']}/settings", json={"system_prompt": "You are a bot", "params": {"model": "gpt-3.5-turbo"}}, headers=headers))
        integration = (await ac.post("/telegram/integrations", json={"type": "bot", "name": "TestBot2", "bot_token": "123:ABC"}, headers=headers)).json()
        channel = (await ac.post("/channels", json={"integration_id": integration["id"], "subproject_id": subproject["id"], "channel_id": "@msgchan", "channel_title": "Msg Channel"}, headers=headers)).json()
        # Имитация создания сообщения (обычно воркер)
        msg_payload = {
            "user_id": project["id"],
            "integration_id": integration["id"],
            "subproject_id": subproject["id"],
            "channel_id": channel["channel_id"],
            "channel_title": channel["channel_title"],
            "message_id": "999999",
            "message_text": "Test message",
            "message_date": "2024-01-01T00:00:00",
            "ai_response_status": "PENDING",
            "created_at": "2024-01-01T00:00:00"
        }
        # Обычно сообщение создаёт воркер, здесь напрямую через БД или API (если есть)
        # ...
        # Проверить лайк
        # ... 