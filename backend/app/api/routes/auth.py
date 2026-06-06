# auth.py — Authentication endpoints
# Handles user registration and login

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, login_user
from app.core.dependencies import get_authenticated_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    Returns the created user (without password).
    """
    user = await register_user(db, user_data)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    Returns a JWT token to use for protected routes.
    """
    result = await login_user(db, user_data)
    return result

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_authenticated_user)
):
    """
    Protected route — returns the currently logged in user.
    Requires a valid JWT token in the Authorization header.
    """
    return current_user