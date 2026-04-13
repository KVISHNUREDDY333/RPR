from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "RPR"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "rpr_db"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    REDIS_URL: str = "redis://localhost:6379"

    UPLOAD_DIR: str = "data/uploads"
    OUTPUT_DIR: str = "data/outputs"
    TEMP_DIR: str = "data/temp"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
