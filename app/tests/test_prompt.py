import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_prompt_crud(monkeypatch):
    monkeypatch.setattr("app.api.auth.check_telegram_auth", lambda data, token: True)
    payload = {
        "id": 123458,
        "username": "promptuser",
        "first_name": "Prompt",
        "last_name": "User",
        "auth_date": 1700000002,
        "hash": "fakehash"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json=payload)
        tokens = resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        # Создать проект и подпроект
        project = (await ac.post("/projects", json={"name": "PromptProj"}, headers=headers)).json()
        subproject = (await ac.post("/subprojects", json={"name": "PromptSub", "project_id": project["id"]}, headers=headers)).json()
        # Создать промпт
        resp2 = await ac.post("/prompts", json={"name": "Prompt1", "description": "desc", "subproject_id": subproject["id"]}, headers=headers)
        assert resp2.status_code == 200
        prompt = resp2.json()
        # Добавить версию настроек
        resp3 = await ac.post(f"/prompts/{prompt['id']}/settings", json={"system_prompt": "You are a bot", "params": {"model": "gpt-3.5-turbo"}}, headers=headers)
        assert resp3.status_code == 200
        # Получить список версий
        resp4 = await ac.get(f"/prompts/{prompt['id']}/settings", headers=headers)
        assert resp4.status_code == 200
        assert len(resp4.json()) > 0 