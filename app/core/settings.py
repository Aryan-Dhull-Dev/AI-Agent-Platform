import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# decide environment
APP_ENV = os.getenv("APP_ENV", "local")

# load correct env file
if APP_ENV == "docker":
    load_dotenv(BASE_DIR / ".env")
else:
    load_dotenv(BASE_DIR / ".env.local")


class Settings(BaseSettings):
    DATABASE_URL: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_ENV: str = "local"

    class Config:
        extra = "ignore"


settings = Settings()