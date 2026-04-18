from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

from .routers import investigate, incidents, hooks, events, debug, briefings

app = FastAPI(title="6:10 Assistant API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(investigate.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(hooks.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(debug.router, prefix="/api/v1")
app.include_router(briefings.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "6:10 Assistant API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
