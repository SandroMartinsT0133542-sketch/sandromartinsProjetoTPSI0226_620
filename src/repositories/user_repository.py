"""Data access for users."""

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from src.models import User
except ModuleNotFoundError:
    from models import User


class UserRepository:
    """Repository for user queries and mutations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def exists_username(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def exists_email(self, email: str) -> bool:
        return self.db.scalar(select(User).where(User.email == email)) is not None

    def exists_phone(self, phone: str) -> bool:
        return self.db.scalar(select(User).where(User.phone == phone)) is not None

    def create(self, payload: dict[str, str]) -> User:
        user = User(
            username=payload["username"],
            display_name=payload["display_name"],
            email=payload["email"],
            phone=payload["phone"],
            password_hash=payload["password_hash"],
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count_users(self) -> int:
        return len(self.db.scalars(select(User)).all())

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.scalar(select(User).where(User.user_id == user_id))
