import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from app.schemas.literals import CaptureMode, MatchStatus, Side

class MatchBase(BaseModel):
    suite_event_id: uuid.UUID | None = None
    red_team: uuid.UUID
    blue_team: uuid.UUID
    regulation: uuid.UUID
    scheduled_at: datetime
    capture_mode: CaptureMode
    video_url: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _validate_teams(self) -> "MatchBase":
        if self.red_team == self.blue_team:
            raise ValueError("red_team y blue_team no pueden ser el mismo equipo")
        return self


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    suite_event_id: uuid.UUID | None = None
    red_team: uuid.UUID | None = None
    blue_team: uuid.UUID | None = None
    regulation: uuid.UUID | None = None
    scheduled_at: datetime | None = None
    capture_mode: CaptureMode | None = None
    status: MatchStatus | None = None
    winner_side: Side | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _validate_teams(self) -> "MatchUpdate":
        if self.red_team is not None and self.blue_team is not None and self.red_team == self.blue_team:
            raise ValueError("red_team y blue_team no pueden ser el mismo equipo")
        return self


class MatchRead(MatchBase):
    id: uuid.UUID
    status: MatchStatus
    winner_side: Side | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchStatusUpdate(BaseModel):
    status: MatchStatus


class MatchResultUpdate(BaseModel):
    winner_side: Side | None = None
    status: MatchStatus = "finished"

class MatchSideStatsPayload(BaseModel):
    total_scored_points: int = Field(default=0, ge=0)
    total_points_allowed: int = Field(default=0, ge=0)
    field_goals_attempted: int = Field(default=0, ge=0)
    field_goals_attempted_3_points: int = Field(default=0, ge=0)
    field_goals_scored: int = Field(default=0, ge=0)
    field_goals_scored_3_points: int = Field(default=0, ge=0)
    free_throws_attempted: int = Field(default=0, ge=0)
    free_throws_scored: int = Field(default=0, ge=0)
    offensive_rebound: int = Field(default=0, ge=0)
    defensive_rebound: int = Field(default=0, ge=0)
    fiba_ranking_position: int = Field(ge=0)


class MatchSideStatsRead(MatchSideStatsPayload):
    id: uuid.UUID
    match_id: uuid.UUID
    side: Side
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchStatsUpsert(BaseModel):
    red: MatchSideStatsPayload | None = None
    blue: MatchSideStatsPayload | None = None