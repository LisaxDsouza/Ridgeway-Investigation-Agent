from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Core API Keys
    GROQ_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None
    
    # NEW UNIQUE DB KEY
    SKYLARK_DATABASE_URL: Optional[str] = None
    
    # Fallback/Diagnostic Logic
    @property
    def sqlalchemy_database_url(self) -> str:
        # 1. Use the new unique key if present
        # 2. Fallback to DATABASE_URL only as a last resort
        url = self.SKYLARK_DATABASE_URL or os.getenv("DATABASE_URL")
        
        if not url:
             raise ValueError("❌ CRITICAL ERROR: SKYLARK_DATABASE_URL is not set in Render Environment Variables!")

        # 3. Block localhost in cloud
        if (os.getenv("RENDER") or os.getenv("FLY_APP_NAME")) and "localhost" in url:
             raise ValueError(f"❌ CLOUD ERROR: App is seeing 'localhost' (Length: {len(url)}). Please check SKYLARK_DATABASE_URL on Render!")

        # 4. Fix Postgres Dialect
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    # Default Settings
    GROQ_MODEL: str = "llama3-groq-70b-8192-tool-use-preview"
    SEED_SCENARIO: str = "block_c_incident"
    LOG_LEVEL: str = "INFO"
    SITE_ID: str = "ridgeway-01"
    
    # MCP & Other Settings
    MCP_TRANSPORT: str = "stdio"
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8001
    INVESTIGATION_WINDOW_HOURS: int = 12
    HOOK_DEFAULT_LOOKBACK_MINUTES: int = 120

    class Config:
        # Force Pydantic to ignore any extra variables it finds
        extra = "ignore"
        # Only load .env if we are local
        if not os.getenv("RENDER") and not os.getenv("FLY_APP_NAME"):
            env_file = ".env"

# Diagnostic Log
print(f"DEBUG: Starting Maya Engine...")
print(f"DEBUG: Found SKYLARK_DATABASE_URL: {'Yes' if os.getenv('SKYLARK_DATABASE_URL') else 'No'}")
print(f"DEBUG: Found DATABASE_URL: {'Yes' if os.getenv('DATABASE_URL') else 'No'}")

settings = Settings()
