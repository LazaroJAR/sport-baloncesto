import uuid

from pydantic import BaseModel, Field
from app.schemas.literals import Gender

class RegulationBase(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=120)
    sets: int = Field(default=4, ge=1, le=10)
    set_duration_sec: int = Field(default=600, ge=1)
    possesion_duration_sec: int = Field(default=24, ge=1)
    gender: Gender | None = None
    notes: str | None = None


class RegulationCreate(RegulationBase):
    pass


class RegulationRead(RegulationBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}
