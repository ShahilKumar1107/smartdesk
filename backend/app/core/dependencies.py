# dependencies.py — Reusable FastAPI dependencies
# These are functions that routes can "depend on" using Depends()

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import verify_token
from app.services.auth_service import get_current_user
from app.models.models import User

# HTTPBearer extracts the JWT token from the Authorization header
# The header looks like: "Authorization: Bearer eyJhbGc..."
security = HTTPBearer()

async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that protects routes — extracts and verifies the JWT token.
    
    Usage in a route:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_authenticated_user)):
            return {"message": f"Hello {current_user.username}"}
    
    If the token is missing or invalid, FastAPI automatically returns 401.
    """
    # Verify the token and get the username
    username = verify_token(credentials.credentials)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get the full user object from database
    user = await get_current_user(db, username)
    return user