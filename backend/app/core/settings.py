from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "RPR"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "rpr_db"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"

    REDIS_URL: str = "redis://localhost:6379"

    UPLOAD_DIR: str = "data/uploads"
    OUTPUT_DIR: str = "data/outputs"
    TEMP_DIR: str = "data/temp"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
