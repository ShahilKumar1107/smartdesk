# auth_service.py — Business logic for authentication
# This layer handles the "thinking" — routes just call these functions

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.models import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token

# ─── REGISTER ────────────────────────────────────────────────

async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
    """
    Creates a new user account.
    Checks for duplicate email/username before creating.
    """

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # Refresh to get the auto-generated id and created_at

    return new_user

# ─── LOGIN ───────────────────────────────────────────────────

async def login_user(db: AsyncSession, user_data: UserLogin) -> dict:
    """
    Verifies credentials and returns a JWT token.
    """

    # Find user by email
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()

    # Check if user exists and password is correct
    # We use a vague error message on purpose — never tell hackers
    # whether the email or password was wrong specifically
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled"
        )

    # Create JWT token with username as the subject
    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# ─── GET CURRENT USER ────────────────────────────────────────

async def get_current_user(db: AsyncSession, username: str) -> User:
    """
    Fetches the current user from the database using their username.
    Used by protected routes to identify who is making the request.
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user