"""CRUD routes for progress records."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from src.database import get_db
    from src.dependencies.auth import get_current_user
    from src.repositories.progress_repository import ProgressRepository
    from src.schemas.progress import RecordCreateRequest, RecordResponse, RecordUpdateRequest
except ModuleNotFoundError:
    from database import get_db
    from dependencies.auth import get_current_user
    from repositories.progress_repository import ProgressRepository
    from schemas.progress import RecordCreateRequest, RecordResponse, RecordUpdateRequest


router = APIRouter()


@router.get("", response_model=list[RecordResponse])
def list_records(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """List records for the authenticated user."""
    records = ProgressRepository(db).list_by_user(user.user_id)
    return [RecordResponse(**record.to_dict()) for record in records]


@router.post("", response_model=RecordResponse)
def create_record(payload: RecordCreateRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Create one record for the authenticated user."""
    record = ProgressRepository(db).create(user.user_id, payload.model_dump())
    return RecordResponse(**record.to_dict())


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get one record by ID for the authenticated user."""
    record = ProgressRepository(db).get_by_id_for_user(record_id, user.user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")
    return RecordResponse(**record.to_dict())


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(record_id: int, payload: RecordUpdateRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Update one record by ID for the authenticated user."""
    repository = ProgressRepository(db)
    record = repository.get_by_id_for_user(record_id, user.user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")

    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    updated = repository.update(record, updates)
    return RecordResponse(**updated.to_dict())


@router.delete("/{record_id}")
def delete_record(record_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete one record by ID for the authenticated user."""
    repository = ProgressRepository(db)
    record = repository.get_by_id_for_user(record_id, user.user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")

    repository.delete(record)
    return {"message": "Record deleted successfully."}
