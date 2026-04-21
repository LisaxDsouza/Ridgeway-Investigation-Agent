from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Log the connection target (masking credentials)
from urllib.parse import urlparse
parsed = urlparse(settings.sqlalchemy_database_url)
print(f"DEBUG: Connecting to database at {parsed.hostname}:{parsed.port} (database: {parsed.path[1:]})")

engine = create_engine(settings.sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
