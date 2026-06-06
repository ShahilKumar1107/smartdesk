# main.py — Entry point for the FastAPI application

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import api_router

# Create the FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI Customer Support Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ─── CORS MIDDLEWARE ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REGISTER ALL ROUTES ─────────────────────────────────────
# This single line adds ALL routes from all route files
app.include_router(api_router)

# ─── ROOT ENDPOINTS ──────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "message": f"{settings.app_name} API is running",
        "version": settings.app_version
    }