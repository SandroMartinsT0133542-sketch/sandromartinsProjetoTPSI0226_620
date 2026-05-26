"""Progress records schemas."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

try:
    from src.utils.validators import validate_date, validate_non_empty
except ModuleNotFoundError:
    from utils.validators import validate_date, validate_non_empty


class RecordBase(BaseModel):
    """Shared progress entry fields."""

    record_date: str
    weight_kg: float = Field(gt=0)
    body_fat_pct: float = Field(ge=0, le=100)
    daily_calories: int = Field(gt=0)
    notes: str

    @field_validator("record_date")
    @classmethod
    def validate_record_date(cls, value: str) -> str:
        valid, message = validate_date(value)
        if not valid:
            raise ValueError(message)
        return value

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str) -> str:
        valid, message = validate_non_empty(value, "Notes")
        if not valid:
            raise ValueError(message)
        return value


class RecordCreateRequest(RecordBase):
    """Create request for one progress entry."""


class RecordUpdateRequest(BaseModel):
    """Update request for one progress entry."""

    record_date: str | None = None
    weight_kg: float | None = Field(default=None, gt=0)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100)
    daily_calories: int | None = Field(default=None, gt=0)
    notes: str | None = None

    @field_validator("record_date")
    @classmethod
    def validate_record_date(cls, value: str | None) -> str | None:
        if value is None:
            return value
        valid, message = validate_date(value)
        if not valid:
            raise ValueError(message)
        return value

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        if value is None:
            return value
        valid, message = validate_non_empty(value, "Notes")
        if not valid:
            raise ValueError(message)
        return value


class RecordResponse(RecordBase):
    """Response payload for one progress entry."""

    record_id: int
    user_id: int


SearchAlgorithm = Literal["linear", "binary"]
SortAlgorithm = Literal["bubble", "insertion", "merge"]
SearchOperator = Literal["equals", "like", "greater", "less", "between", "any"]
