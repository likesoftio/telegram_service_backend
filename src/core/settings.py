from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_RO_USER_PASSWORD: str

    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    OPENAI_API_KEY: str

    ENCRYPTION_KEY: str

    telegram_session: str

    class Config:
        env_file = ".env"


ACCESS_TOKEN_EXPIRE = 60 * 60
REFRESH_TOKEN_EXPIRE = 60 * 60 * 24 * 14

settings = Settings()