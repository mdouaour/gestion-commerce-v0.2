from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(BASE_DIR, "sql_app.db")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestion Commerce POS"
    API_V1_STR: str = "/api/v1"
    
    # Database - Use absolute path for SQLite
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    
    # Security
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
