from pydantic import BaseModel
from datetime import datetime


class ProjectRequest(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
