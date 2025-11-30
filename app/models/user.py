from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Annotated
from datetime import datetime
import re

class UserBase(BaseModel):
    """Base model shared properties"""
    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9_-]+$",
            examples=["john_doe123"]
        )
    ]
    email: EmailStr = Field(examples=["user@example.com"])

class UserCreate(UserBase):
    """Properties to receive via API on creation"""
    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=128,
            examples=["SecurePass123Hoho!"]
        )
    ]
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserInDB(UserBase):
    """Properties stored in DB"""
    id: int = Field(examples=[1])
    is_admin: bool = False
    created_at: datetime = Field(examples=["2023-01-01T00:00:00"])
    updated_at: datetime = Field(examples=["2023-01-01T00:00:00"])
    
    class Config:
        from_attributes = True  # Allows ORM mode

class UserPublic(UserBase):
    """Safe to return via API (no sensitive data)"""
    id: int = Field(examples=[1])
    is_admin: bool = False
    created_at: datetime = Field(examples=["2023-01-01T00:00:00"])

class UserUpdate(BaseModel):
    """Allowed properties for update"""
    email: Optional[EmailStr] = Field(None, examples=["new@example.com"])
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        examples=["NewSecurePassM2123!"]
    )
    is_active: Optional[bool] = Field(None, examples=[True])
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return UserCreate.validate_password(v)

class Token(BaseModel):
    """JWT token response"""
    access_token: str = Field(examples=["eyJhbGciOi..."])
    refresh_token: str
    token_type: str = Field(default="bearer", examples=["bearer"])

class TokenData(BaseModel):
    """Data stored in JWT token"""
    username: Optional[str] = Field(None, examples=["john_doe"])

class UserLogin(BaseModel):
    """Login request model"""
    username: str = Field(examples=["john_doe"])
    password: str = Field(examples=["SecurePassM123!"])

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr = Field(examples=["user@example.com"])

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str = Field(examples=["reset_token_abc123"])
    new_password: str = Field(examples=["NewSecurePass123!"])
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        return UserCreate.validate_password(v)

class RefreshRequest(BaseModel):
    refresh_token: str