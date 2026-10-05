import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field

class SuiteEventBase(BaseModel):
    name: str = Field(max_length=200)
    code: str = Field(max_length=64)
    country_code: str = Field(default="CUB", max_length=3)
    city: str | None = Field(default=None, max_length=120)
    starts_on: date
    ends_on: date | None = None
    scope: Literal["national", "international", "regional", "club", "training"] = "national"
    event_kind: str = Field(default="championship", max_length=32)
    notes: str | None = None


class SuiteEventCreate(SuiteEventBase):
    pass


class SuiteEventRead(SuiteEventBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
