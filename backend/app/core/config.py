from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Obligatorios: deben venir del entorno o de .env (ver .env.example)
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Orígenes permitidos para CORS, separados por coma en el .env
    CORS_ORIGINS: List[str] = ["http://localhost"]

    class Config:
        env_file = ".env"


settings = Settings()
