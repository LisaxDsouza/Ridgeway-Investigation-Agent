from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None
    DATABASE_URL: str
    
    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.DATABASE_URL
        
        # Security Check: Prevent local DB connection in production
        import os
        if (os.getenv("RENDER") or os.getenv("FLY_APP_NAME")) and "localhost" in url:
            raise ValueError(
                "❌ CLOUD CONFIG ERROR: The app is using 'localhost' for the database on Render! "
                "Please check your Render Environment Variables and ensure DATABASE_URL is set "
                "to the Internal Database URL (starts with postgres://dpg-...)."
            )

        # Fix prefix
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    GROQ_MODEL: str = "llama3-groq-70b-8192-tool-use-preview"
    SEED_SCENARIO: str = "block_c_incident"
    LOG_LEVEL: str = "INFO"

    # MCP & Site Context
    MCP_TRANSPORT: str = "stdio"
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8001
    SITE_ID: str = "ridgeway-01"
    INVESTIGATION_WINDOW_HOURS: int = 12
    HOOK_DEFAULT_LOOKBACK_MINUTES: int = 120

    class Config:
        import os
        # Only load .env if we are NOT in the cloud
        if not os.getenv("RENDER") and not os.getenv("FLY_APP_NAME"):
            env_file = ".env"
        # Otherwise, stay strictly within the system environment

settings = Settings()
