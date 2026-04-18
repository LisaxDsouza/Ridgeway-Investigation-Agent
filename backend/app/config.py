from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None
    DATABASE_URL: str
    GROQ_MODEL: str = "llama3-groq-70b-8192-tool-use-preview"
    SEED_SCENARIO: str = "block_c_incident"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
