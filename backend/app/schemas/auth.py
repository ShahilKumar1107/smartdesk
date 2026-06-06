# auth.py — Defines the data shapes for authentication endpoints
# Pydantic validates that incoming data matches these shapes exactly

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ─── REQUEST SCHEMAS (data coming IN) ───────────────────────

class UserRegister(BaseModel):
    """Data required to register a new user"""
    email: EmailStr        # Pydantic validates this is a real email format
    username: str
    password: str

    class Config:
        # Example data shown in /docs
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123"
            }
        }

class UserLogin(BaseModel):
    """Data required to log in"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }

# ─── RESPONSE SCHEMAS (data going OUT) ──────────────────────

class UserResponse(BaseModel):
    """User data returned to the client — never includes password!"""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        # Allows Pydantic to read data from SQLAlchemy models
        from_attributes = True

class TokenResponse(BaseModel):
    """JWT token returned after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse