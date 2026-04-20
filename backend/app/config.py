from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None
    DATABASE_URL: str
    
    @property
    def sqlalchemy_database_url(self) -> str:
        # Fly.io provide 'postgres://', but SQLAlchemy requires 'postgresql://'
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

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
        env_file = ".env"

settings = Settings()
