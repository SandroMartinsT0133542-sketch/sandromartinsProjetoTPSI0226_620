"""Search, sort and filter routes for records."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

try:
    from src.algorithms import bubble_sort, insertion_sort, merge_sort
    from src.algorithms.searching import binary_search, linear_search
    from src.database import get_db
    from src.dependencies.auth import get_current_user
    from src.repositories.progress_repository import ProgressRepository
    from src.schemas.progress import SearchAlgorithm, SearchOperator, SortAlgorithm
except ModuleNotFoundError:
    from algorithms import bubble_sort, insertion_sort, merge_sort
    from algorithms.searching import binary_search, linear_search
    from database import get_db
    from dependencies.auth import get_current_user
    from repositories.progress_repository import ProgressRepository
    from schemas.progress import SearchAlgorithm, SearchOperator, SortAlgorithm


router = APIRouter()


def _resolve_field_name(field: str) -> str:
    normalized = field.strip().casefold().replace(" ", "_")
    aliases = {
        "id": "record_id",
        "recordid": "record_id",
        "record_id": "record_id",
        "date": "record_date",
        "record_date": "record_date",
        "weight": "weight_kg",
        "weight_kg": "weight_kg",
        "body_fat": "body_fat_pct",
        "body_fat_pct": "body_fat_pct",
        "calories": "daily_calories",
        "daily_calories": "daily_calories",
        "notes": "notes",
    }
    return aliases.get(normalized, normalized)


@router.get("/search")
def search_records(
    field: str,
    target: str,
    algorithm: SearchAlgorithm = "linear",
    operator: SearchOperator = "equals",
    target_max: str | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search records with the configured operator and algorithm."""
    if operator == "between" and target_max is None:
        raise HTTPException(status_code=422, detail="target_max is required for 'between' operator.")

    records = [record.to_dict() for record in ProgressRepository(db).list_by_user(user.user_id)]
    search_field = _resolve_field_name(field)

    if algorithm == "binary":
        ordered = insertion_sort(records, field=search_field, descending=False)
        return binary_search(ordered, field=search_field, target=target, operator=operator, target_max=target_max)

    return linear_search(records, field=search_field, target=target, operator=operator, target_max=target_max)


@router.get("/sort")
def sort_records(
    field: str,
    algorithm: SortAlgorithm = "insertion",
    descending: bool = Query(False),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sort records with manual sorting algorithms."""
    records = [record.to_dict() for record in ProgressRepository(db).list_by_user(user.user_id)]
    sort_field = _resolve_field_name(field)

    if algorithm == "bubble":
        return bubble_sort(records, field=sort_field, descending=descending)
    if algorithm == "merge":
        return merge_sort(records, field=sort_field, descending=descending)
    return insertion_sort(records, field=sort_field, descending=descending)


@router.get("/filter/weight")
def filter_weight(minimum: float, maximum: float, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Filter records by weight range."""
    if minimum > maximum:
        raise HTTPException(status_code=400, detail="minimum cannot be greater than maximum.")
    records = [record.to_dict() for record in ProgressRepository(db).list_by_user(user.user_id)]
    return [record for record in records if minimum <= float(record.get("weight_kg", 0)) <= maximum]


@router.get("/filter/body-fat")
def filter_body_fat(minimum: float, maximum: float, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Filter records by body-fat range."""
    if minimum > maximum:
        raise HTTPException(status_code=400, detail="minimum cannot be greater than maximum.")
    records = [record.to_dict() for record in ProgressRepository(db).list_by_user(user.user_id)]
    return [record for record in records if minimum <= float(record.get("body_fat_pct", 0)) <= maximum]


@router.get("/filter/calories")
def filter_calories(minimum: float, maximum: float, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Filter records by calories range."""
    if minimum > maximum:
        raise HTTPException(status_code=400, detail="minimum cannot be greater than maximum.")
    records = [record.to_dict() for record in ProgressRepository(db).list_by_user(user.user_id)]
    return [record for record in records if minimum <= float(record.get("daily_calories", 0)) <= maximum]
