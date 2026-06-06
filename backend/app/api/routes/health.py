# health.py — Health check routes
# These endpoints are used to verify the API and database are working

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db

# APIRouter is like a mini FastAPI app
# prefix means all routes here start with /health
# tags groups them together in the /docs page
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """Basic health check — confirms API is running"""
    return {
        "status": "ok",
        "service": "SmartDesk API"
    }

@router.get("/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check — confirms PostgreSQL connection works.
    
    Depends(get_db) means FastAPI will automatically:
    1. Create a database session
    2. Pass it to this function as 'db'
    3. Clean it up after the function finishes
    """
    try:
        # Run a simple query to test the connection
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "message": "PostgreSQL connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "message": str(e)
        }