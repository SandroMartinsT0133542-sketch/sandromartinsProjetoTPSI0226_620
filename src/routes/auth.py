"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from src.database import get_db
    from src.dependencies.auth import get_current_user
    from src.repositories.user_repository import UserRepository
    from src.schemas.auth import AuthUserResponse, LoginRequest, RegisterRequest, TokenResponse
    from src.services.security_service import create_access_token, hash_password, verify_password
except ModuleNotFoundError:
    from database import get_db
    from dependencies.auth import get_current_user
    from repositories.user_repository import UserRepository
    from schemas.auth import AuthUserResponse, LoginRequest, RegisterRequest, TokenResponse
    from services.security_service import create_access_token, hash_password, verify_password


router = APIRouter()


@router.post("/register", response_model=AuthUserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    users = UserRepository(db)

    if users.exists_username(payload.username):
        raise HTTPException(status_code=400, detail="That username is already taken.")
    if users.exists_email(payload.email):
        raise HTTPException(status_code=400, detail="That email is already registered.")
    if users.exists_phone(payload.phone):
        raise HTTPException(status_code=400, detail="That phone number is already registered.")

    user = users.create(
        {
            "username": payload.username.strip(),
            "display_name": payload.display_name.strip(),
            "email": payload.email.strip(),
            "phone": payload.phone.strip(),
            "password_hash": hash_password(payload.password),
        }
    )
    return AuthUserResponse(
        user_id=user.user_id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        phone=user.phone,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and issue a JWT token."""
    users = UserRepository(db)
    user = users.get_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_access_token(user.user_id, user.username)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AuthUserResponse)
def me(user=Depends(get_current_user)):
    """Get profile information for the authenticated user."""
    return AuthUserResponse(
        user_id=user.user_id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        phone=user.phone,
    )
