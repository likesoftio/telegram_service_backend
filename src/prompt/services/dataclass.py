from typing import Dict, Any
from pydantic import BaseModel, Field, field_validator


class PromptParams(BaseModel):
    model: str = Field(default="gpt-3.5-turbo", description="OpenAI модель")
    max_tokens: int = Field(default=256, ge=1, le=4000, description="Максимальное количество токенов")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Температура (креативность)")

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('temperature must be between 0.0 and 2.0')
        return v

    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if not 1 <= v <= 4000:
            raise ValueError('max_tokens must be between 1 and 4000')
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the model, suitable for API requests."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptParams':
        """Creates an instance from a dictionary, filtering out unwanted fields."""
        filtered_data = {
            "model": data.get("model", "gpt-3.5-turbo"),
            "max_tokens": data.get("max_tokens", 256),
            "temperature": data.get("temperature", 0.7)
        }
        return cls(**filtered_data)