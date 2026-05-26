"""Authentication request/response schemas."""

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """Register a new user account."""

    username: str
    display_name: str
    password: str
    email: str = ""
    phone: str = ""


class LoginRequest(BaseModel):
    """Authenticate a user and receive an access token."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT response payload."""

    access_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseModel):
    """Authenticated user profile payload."""

    user_id: int
    username: str
    display_name: str
    email: str
    phone: str
