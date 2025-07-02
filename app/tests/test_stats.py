import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_stats(monkeypatch):
    monkeypatch.setattr("app.api.auth.check_telegram_auth", lambda data, token: True)
    payload = {
        "id": 123461,
        "username": "statuser",
        "first_name": "Stat",
        "last_name": "User",
        "auth_date": 1700000005,
        "hash": "fakehash"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json=payload)
        tokens = resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        # Создать проект, подпроект, промпт, версию
        project = (await ac.post("/projects", json={"name": "StatProj"}, headers=headers)).json()
        subproject = (await ac.post("/subprojects", json={"name": "StatSub", "project_id": project["id"]}, headers=headers)).json()
        prompt = (await ac.post("/prompts", json={"name": "StatPrompt", "description": "desc", "subproject_id": subproject["id"]}, headers=headers)).json()
        (await ac.post(f"/prompts/{prompt['id']}/settings", json={"system_prompt": "You are a bot", "params": {"model": "gpt-3.5-turbo"}}, headers=headers))
        # Получить статистику по промпту
        resp2 = await ac.get(f"/stats/prompt/{prompt['id']}" , headers=headers)
        assert resp2.status_code == 200
        # Получить статистику по проекту
        resp3 = await ac.get(f"/stats/project/{project['id']}" , headers=headers)
        assert resp3.status_code == 200 