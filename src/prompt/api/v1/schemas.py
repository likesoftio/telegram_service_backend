from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional


class PromptTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: int


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError("project_id must be positive")
        return v


class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PromptSettingsVersionRequest(BaseModel):
    prompt_template_id: int
    system_prompt: str
    params: dict = Field(default_factory=dict)


class PromptSettingsVersionResponse(BaseModel):
    id: int
    prompt_template_id: int
    system_prompt: str
    params: dict = Field(default_factory=dict)
    version: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageAddTemp(BaseModel):
    message_id: int
    prompt_template_id: int


class MessageResponse(BaseModel):
    id: int
    user_id: int
    integration_id: int
    project_id: int
    channel_id: str
    channel_title: Optional[str] = None
    message_id: str
    chat_id: Optional[int] = None
    message_text: str
    message_date: datetime
    ai_response: Optional[str] = None
    ai_response_status: str
    ai_response_sent: bool
    prompt_template_id: Optional[int] = None
    prompt_settings_version: Optional[int] = None
    openai_model: Optional[str] = None
    openai_token_usage: Optional[int] = None
    openai_latency: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageEdit(BaseModel):
    ai_response_edit: str


class MessageStatsResponse(BaseModel):
    date: date
    messages_scanned: int
    messages_with_ai_response: int
    messages_sent: int
    messages_with_errors: int
    avg_ai_generation_time: float
    total_tokens_used: int
    created_at: datetime