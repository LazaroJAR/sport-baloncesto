from typing import Literal
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field
from literals import Side, ScoringType, FoulType, ReboundType, PreviousAction, EventType

class MatchEventBase(BaseModel):
    match_id: uuid.UUID
    event_type: EventType
    current_set: int = Field(ge=1, le=10)
    set_elapsed_sec: int = Field(ge=0)


class PlayerEventBase(MatchEventBase):
    player_id: uuid.UUID
    side: Side


class MatchScoringEventCreate(PlayerEventBase):
    event_type: Literal["scoring"] = "scoring"
    has_scored: bool = False
    points: int = Field(default=0, ge=0, le=3)
    scoring_type: ScoringType
    previous_action: PreviousAction | None = None


class MatchReboundEventCreate(PlayerEventBase):
    event_type: Literal["rebound"] = "rebound"
    rebound_type: ReboundType


class MatchFoulEventCreate(PlayerEventBase):
    event_type: Literal["foul"] = "foul"
    foul_type: FoulType
    fouled_player_id: uuid.UUID


class MatchPassEventCreate(PlayerEventBase):
    event_type: Literal["pass"] = "pass"
    reciver_player_id: uuid.UUID


class MatchStealEventCreate(PlayerEventBase):
    event_type: Literal["steal"] = "steal"
    stolen_from_player_id: uuid.UUID


class MatchEventRead(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID
    event_type: str
    current_set: int
    set_elapsed_sec: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerEventRead(MatchEventRead):
    player_id: uuid.UUID
    side: Side


class MatchScoringEventRead(PlayerEventRead):
    has_scored: bool
    points: int
    scoring_type: str
    previous_action: str | None


class MatchReboundEventRead(PlayerEventRead):
    rebound_type: str


class MatchFoulEventRead(PlayerEventRead):
    foul_type: str
    fouled_player_id: uuid.UUID


class MatchPassEventRead(PlayerEventRead):
    reciver_player_id: uuid.UUID


class MatchStealEventRead(PlayerEventRead):
    stolen_from_player_id: uuid.UUID
