from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[1]  # service/app -> parents[1] = service
ENV_PATH = SERVICE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")

    MODEL_ID: str = "black-forest-labs/FLUX.1-schnell"
    DB_URL: str = "sqlite:///./service.db"

    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"

    HISTORY_DELETE_TOKEN: str = "change-me-too"

    # супер-практично: чтобы сервис запускался даже без GPU
    USE_DUMMY_MODEL: bool = False

settings = Settings()
