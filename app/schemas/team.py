import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from app.schemas.literals import Gender

class TeamBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    short_name: str = Field(min_length=1, max_length=3)
    headquarters: str | None = Field(default=None, max_length=120)
    fiba_position: int | None = Field(default=None, ge=0)
    players_gender: Gender


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
