# security.py — Handles password hashing and JWT token creation/verification

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context — uses bcrypt algorithm
# bcrypt is the industry standard for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── PASSWORD FUNCTIONS ──────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Converts a plain text password into a secure hash.
    Example: "password123" → "$2b$12$abc123..."
    The hash is different every time but always verifiable.
    """
    return pwd_context.hash(password[:72])  # bcrypt max is 72 bytes

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches a stored hash.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password[:72], hashed_password)

# ─── JWT TOKEN FUNCTIONS ─────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token containing the provided data.
    The token expires after a set time (default 30 minutes).
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    # Add expiration to the token payload
    to_encode.update({"exp": expire})

    # Create and return the signed JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verifies a JWT token and returns the username it contains.
    Returns None if the token is invalid or expired.
    """
    try:
        # Decode the token using our secret key
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        # "sub" (subject) is where we store the username
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None