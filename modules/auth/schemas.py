from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """
    Schema for the JWT token response.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Internal schema for token payload.
    """
    email: Optional[str] = None


class UserSignup(BaseModel):
    """
    Schema for a new user registration request.
    """
    email: EmailStr
    password: str
    farm_name: str
    latitude: float
    longitude: float
    location_name: str


class UserLogin(BaseModel):
    """
    Schema for user login request.
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for a user response, omitting sensitive information.
    """
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True