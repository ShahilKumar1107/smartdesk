# database.py — Sets up the connection to PostgreSQL
# SQLAlchemy is our ORM (Object Relational Mapper)
# An ORM lets us work with database tables as Python objects
# instead of writing raw SQL queries

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create the async engine — this is the actual connection to PostgreSQL
# The engine manages a "pool" of connections for efficiency
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Prints all SQL queries to terminal — helpful for debugging
)

# Session factory — a "session" is like a temporary workspace
# where you make database changes before committing them
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class — all our database models (tables) will inherit from this
class Base(DeclarativeBase):
    pass

# Dependency function — FastAPI calls this to give each
# API endpoint its own database session, then cleans it up after
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise