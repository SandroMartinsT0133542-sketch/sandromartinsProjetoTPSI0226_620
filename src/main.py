"""FastAPI application entry point for the fitness management system."""

from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from services import (
        authenticate,
        compute_statistics,
        create_record,
        current_user,
        current_user_id,
        delete_record,
        find_by_id,
        initialize_auth,
        initialize_service,
        list_records,
        logout,
        register_user,
        save_state,
        search_records,
        sort_records,
        update_record,
    )
    from services.progress_service import (
        filter_body_fat_range,
        filter_calories_range,
        filter_weight_range,
        list_records_by_user,
    )
    from utils.validators import validate_date, validate_non_empty
except ModuleNotFoundError:
    from src.services import (
        authenticate,
        compute_statistics,
        create_record,
        current_user,
        current_user_id,
        delete_record,
        find_by_id,
        initialize_auth,
        initialize_service,
        list_records,
        logout,
        register_user,
        save_state,
        search_records,
        sort_records,
        update_record,
    )
    from src.services.progress_service import (
        filter_body_fat_range,
        filter_calories_range,
        filter_weight_range,
        list_records_by_user,
    )
    from src.utils.validators import validate_date, validate_non_empty


Record = dict[str, Any]
SearchAlgorithm = Literal["linear", "binary"]
SortAlgorithm = Literal["bubble", "insertion", "merge"]
SearchOperator = Literal["equals", "like", "greater", "less", "between", "any"]


class RegisterRequest(BaseModel):
    """Request body for account registration."""

    username: str
    display_name: str
    password: str
    email: str = ""
    phone: str = ""


class LoginRequest(BaseModel):
    """Request body for login."""

    username: str
    password: str


class RecordCreateRequest(BaseModel):
    """Request body for creating a fitness record."""

    user_id: int | None = None
    record_date: str
    weight_kg: float = Field(gt=0)
    body_fat_pct: float = Field(ge=0, le=100)
    daily_calories: int = Field(gt=0)
    notes: str


class RecordUpdateRequest(BaseModel):
    """Request body for partially updating a fitness record."""

    record_date: str | None = None
    weight_kg: float | None = Field(default=None, gt=0)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100)
    daily_calories: int | None = Field(default=None, gt=0)
    notes: str | None = None


def _validate_record_fields(payload: dict[str, Any], *, for_update: bool = False) -> None:
    """Run domain validation rules before service-layer persistence."""
    if "record_date" in payload:
        is_valid, message = validate_date(str(payload["record_date"]))
        if not is_valid:
            raise HTTPException(status_code=422, detail=message)

    if "notes" in payload:
        notes_value = str(payload["notes"])
        is_valid, message = validate_non_empty(notes_value, "Notes")
        if not is_valid:
            raise HTTPException(status_code=422, detail=message)
        payload["notes"] = notes_value

    if not for_update:
        required_fields = ["record_date", "weight_kg", "body_fat_pct", "daily_calories", "notes"]
        missing = [field for field in required_fields if field not in payload]
        if missing:
            raise HTTPException(status_code=422, detail=f"Missing required fields: {', '.join(missing)}")


def _records_for_scope(user_id: int | None) -> list[Record]:
    """Get records for current authenticated user or an explicit user ID."""
    if user_id is None:
        return list_records()
    return list_records_by_user(user_id)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize storage once when the API process starts."""
    initialize_auth()
    initialize_service()
    yield


app = FastAPI(
    title="Fitness Management API",
    description="API wrapper around the existing fitness services and JSON persistence.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Simple API welcome endpoint."""
    return {"message": "Fitness Management API is running."}


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Liveness endpoint for local development checks."""
    return {"status": "ok"}


@app.post("/auth/register")
def register(payload: RegisterRequest) -> dict[str, str]:
    """Create a new user account."""
    created, message = register_user(
        username=payload.username,
        display_name=payload.display_name,
        password=payload.password,
        email=payload.email,
        phone=payload.phone,
    )
    if not created:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, int | str]:
    """Authenticate the user and persist in-memory session state."""
    if not authenticate(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    username = current_user() or payload.username
    user_id = current_user_id() or 0
    return {"message": "Login successful.", "username": username, "user_id": user_id}


@app.post("/auth/logout")
def logout_user() -> dict[str, str]:
    """Clear active login session."""
    logout()
    return {"message": "Logout successful."}


@app.get("/auth/me")
def me() -> dict[str, int | str | None]:
    """Return the current authenticated user context."""
    return {"username": current_user(), "user_id": current_user_id()}


@app.get("/records")
def get_records(user_id: int | None = None) -> list[Record]:
    """List records for active user or explicit user ID."""
    return _records_for_scope(user_id)


@app.post("/records")
def add_record(payload: RecordCreateRequest) -> Record:
    """Create one fitness progress record and persist state."""
    data = payload.model_dump(exclude_none=True)
    _validate_record_fields(data)
    created = create_record(data)
    if not save_state():
        raise HTTPException(status_code=500, detail="Record was created but could not be saved.")
    return created


@app.get("/records/{record_id}")
def get_record(record_id: int, user_id: int | None = None) -> Record:
    """Get a single record by ID."""
    record = find_by_id(record_id, user_id=user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record


@app.put("/records/{record_id}")
def edit_record(record_id: int, payload: RecordUpdateRequest, user_id: int | None = None) -> dict[str, str]:
    """Update one record and persist state."""
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    _validate_record_fields(updates, for_update=True)
    updated = update_record(record_id, updates, user_id=user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found.")
    if not save_state():
        raise HTTPException(status_code=500, detail="Record was updated but could not be saved.")
    return {"message": "Record updated successfully."}


@app.delete("/records/{record_id}")
def remove_record(record_id: int, user_id: int | None = None) -> dict[str, str]:
    """Delete one record by ID and persist state."""
    deleted = delete_record(record_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found.")
    if not save_state():
        raise HTTPException(status_code=500, detail="Record was deleted but could not be saved.")
    return {"message": "Record deleted successfully."}


@app.get("/records/search")
def search_records_endpoint(
    field: str,
    target: str,
    algorithm: SearchAlgorithm = "linear",
    operator: SearchOperator = "equals",
    target_max: str | None = None,
    user_id: int | None = None,
) -> list[Record]:
    """Search records by field and operator using linear or binary search."""
    if operator == "between" and target_max is None:
        raise HTTPException(status_code=422, detail="target_max is required for 'between' operator.")

    base_records = _records_for_scope(user_id)
    return search_records(
        field=field,
        target=target,
        algorithm=algorithm,
        operator=operator,
        target_max=target_max,
        records=base_records,
    )


@app.get("/records/sort")
def sort_records_endpoint(
    field: str,
    algorithm: SortAlgorithm = "insertion",
    descending: bool = Query(False),
    user_id: int | None = None,
) -> list[Record]:
    """Sort records using manual bubble/insertion/merge algorithms."""
    base_records = _records_for_scope(user_id)
    try:
        return sort_records(field=field, algorithm=algorithm, descending=descending, records=base_records)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/records/filter/weight")
def filter_weight(minimum: float, maximum: float, user_id: int | None = None) -> list[Record]:
    """Filter records by weight range."""
    if minimum > maximum:
        raise HTTPException(status_code=400, detail="minimum cannot be greater than maximum.")
    return filter_weight_range(minimum, maximum, records=_records_for_scope(user_id))


@app.get("/records/filter/body-fat")
def filter_body_fat(minimum: float, maximum: float, user_id: int | None = None) -> list[Record]:
    """Filter records by body-fat percentage range."""
    if minimum > maximum:
        raise HTTPException(status_code=400, detail="minimum cannot be greater than maximum.")
    return filter_body_fat_range(minimum, maximum, records=_records_for_scope(user_id))


@app.get("/records/filter/calories")
def filter_calories(minimum: float, maximum: float, user_id: int | None = None) -> list[Record]:
    """Filter records by daily calories range."""
    if minimum > maximum:
        raise HTTPException(status_code=400, detail="minimum cannot be greater than maximum.")
    return filter_calories_range(minimum, maximum, records=_records_for_scope(user_id))


@app.get("/records/statistics")
def stats(user_id: int | None = None) -> dict[str, int | float]:
    """Return aggregate statistics for active user or explicit user ID."""
    if user_id is None:
        return compute_statistics()

    records = list_records_by_user(user_id)
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

