from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Atoms Demo API"
    app_version: str = "0.1.0"
    api_secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 60 * 24
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    llm_provider: str = "mock"


settings = Settings()
