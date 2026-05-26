"""Statistics routes for progress records."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from src.database import get_db
    from src.dependencies.auth import get_current_user
    from src.repositories.progress_repository import ProgressRepository
except ModuleNotFoundError:
    from database import get_db
    from dependencies.auth import get_current_user
    from repositories.progress_repository import ProgressRepository


router = APIRouter()


@router.get("/statistics")
def statistics(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Compute aggregate statistics for authenticated user records."""
    records = [record.to_dict() for record in ProgressRepository(db).list_by_user(user.user_id)]
    if not records:
        return {
            "count": 0,
            "avg_weight": 0.0,
            "avg_body_fat": 0.0,
            "min_weight": 0.0,
            "max_weight": 0.0,
            "total_calories": 0,
        }

    weights = [float(record["weight_kg"]) for record in records]
    body_fats = [float(record["body_fat_pct"]) for record in records]
    calories = [int(record["daily_calories"]) for record in records]

    return {
        "count": len(records),
        "avg_weight": sum(weights) / len(weights),
        "avg_body_fat": sum(body_fats) / len(body_fats),
        "min_weight": min(weights),
        "max_weight": max(weights),
        "total_calories": sum(calories),
    }
