"""Application configuration helpers."""

from os import getenv

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Runtime settings loaded from environment variables."""

    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/fitness_db?connect_timeout=5",
    )
    jwt_secret_key: str = getenv("JWT_SECRET_KEY", "change-this-in-production")
    jwt_algorithm: str = getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
