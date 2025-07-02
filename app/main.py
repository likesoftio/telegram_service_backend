from fastapi import FastAPI
from app.api import auth, user, project, subproject, prompt, telegram_integration, channel, message, task, stats

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(project.router)
app.include_router(subproject.router)
app.include_router(prompt.router)
app.include_router(telegram_integration.router)
app.include_router(channel.router)
app.include_router(message.router)
app.include_router(task.router)
app.include_router(stats.router)