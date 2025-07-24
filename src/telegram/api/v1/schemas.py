from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MTProtoRequest(BaseModel):
    name: str
    telegram_api_id: int
    telegram_api_hash: str
    phone_number: str


class MTProtoResponse(BaseModel):
    status: str
    phone_code_hash: str
    temp_session: str


class ConfirmCodeRequest(BaseModel):
    name: str
    temp_session: str
    phone_number: str
    telegram_api_id: int
    telegram_api_hash: str
    code: str
    phone_code_hash: str


class TelegramIntegrationResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone_number: str
    session_file: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelRequest(BaseModel):
    integration_id: int
    project_id: int
    channel_id: str
    channel_title: Optional[str] = None
    prompt_filter: Optional[str] = None


class ChannelUpdateRequest(BaseModel):
    channel_id: Optional[str] = None
    channel_title: Optional[str] = None
    prompt_filter: Optional[str] = None
    is_active: Optional[bool] = None


class ChannelResponse(BaseModel):
    id: int
    user_id: int
    integration_id: int
    project_id: int
    channel_id: str
    channel_title: Optional[str] = None
    prompt_filter: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True