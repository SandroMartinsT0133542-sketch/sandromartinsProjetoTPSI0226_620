"""Authentication dependencies for protected endpoints."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

try:
    from src.database import get_db
    from src.repositories.user_repository import UserRepository
    from src.services.security_service import decode_access_token
except ModuleNotFoundError:
    from database import get_db
    from repositories.user_repository import UserRepository
    from services.security_service import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Return authenticated user from Bearer token."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    user = UserRepository(db).get_by_id(int(payload["user_id"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists.")
    return user
