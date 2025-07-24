from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.accounts.api.v1.router import router as account_router
from src.projects.api.v1.router import router as projects_router
from src.telegram.api.v1.router import router as telegram_router
from src.prompt.api.v1.router import router as prompt_router
from src.ai_task.router import router as task_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account_router)
app.include_router(projects_router)
app.include_router(telegram_router)
app.include_router(prompt_router)
app.include_router(task_router)
