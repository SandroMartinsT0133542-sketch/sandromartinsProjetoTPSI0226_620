"""Security helpers for password hashing and JWT tokens."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

try:
    from src.config import settings
except ModuleNotFoundError:
    from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash plain text password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain text password against stored hash."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: int, username: str) -> str:
    """Create a signed JWT access token."""
    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "user_id": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, str | int]:
    """Decode and validate one JWT token payload."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        username = payload.get("sub")
        if user_id is None or username is None:
            raise ValueError("Invalid token payload.")
        return {"user_id": int(user_id), "username": str(username)}
    except JWTError as error:
        raise ValueError("Invalid or expired token.") from error
