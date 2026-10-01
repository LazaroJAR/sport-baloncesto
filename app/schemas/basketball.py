import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# Tipos reutilizables
Side = Literal["red", "blue"]
Gender = Literal["masculino", "femenino"]
MatchStatus = Literal["draft", "scheduled", "live", "finished", "cancelled"]
CaptureMode = Literal["live", "video"]
Position = Literal["base", "escolta", "alero", "ala-pivot", "pivot"]
EventType = Literal["scoring", "rebound", "foul", "pass", "steal"]
ScoringType = Literal["tiro_libre", "tiro_de_cancha"]
PreviousAction = Literal["catch_and_shot", "dribbling", "pick_and_roll", "pick_and_pop"]
ReboundType = Literal["ofensivo", "defensivo"]
FoulType = Literal["personal", "en_tiro", "ofensiva", "tecnica", "antideportiva", "descalificante"]


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


class PlayerCreate(BaseModel):
    primer_nombre: str = Field(max_length=100)
    segundo_nombre: str | None = None
    primer_apellido: str = Field(max_length=100)
    segundo_apellido: str | None = None
    fecha_nacimiento: date
    sexo: Gender
    lateralidad: str | None = None
    documento_identidad: str | None = Field(default=None, max_length=32)
    notas: str | None = None
    position: Position
    number: int = Field(ge=0, le=99)
    team_id: uuid.UUID | None = None

    @field_validator("sexo", mode="before")
    @classmethod
    def norm_sexo(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("lateralidad")
    @classmethod
    def lat(cls, v: str | None):
        if v is None or v == "":
            return None
        x = v.strip().lower()
        if x not in {"zurdo", "diestro", "ambidiestro"}:
            raise ValueError("Lateralidad: zurdo, diestro o ambidiestro")
        return x


class PlayerRead(BaseModel):
    id: uuid.UUID
    athlete_id: uuid.UUID
    team_id: uuid.UUID | None
    active: bool
    primer_nombre: str
    primer_apellido: str
    segundo_nombre: str | None
    segundo_apellido: str | None
    nombre_completo: str
    documento_identidad: str | None
    number: int | None
    position: Position

    model_config = {"from_attributes": True}


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


class MatchBase(BaseModel):
    suite_event_id: uuid.UUID | None = None
    red_team: uuid.UUID
    blue_team: uuid.UUID
    regulation: uuid.UUID
    scheduled_at: datetime
    capture_mode: CaptureMode
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


class MatchEventBase(BaseModel):
    current_set: int = Field(ge=1, le=10)
    set_elapsed_sec: int = Field(ge=0)


class PlayerEventBase(MatchEventBase):
    player_id: uuid.UUID
    side: Side


class MatchScoringEventCreate(PlayerEventBase):
    has_scored: bool = False
    points: int = Field(default=0, ge=0, le=3)
    scoring_type: ScoringType
    previous_action: PreviousAction | None = None


class MatchReboundEventCreate(PlayerEventBase):
    rebound_type: ReboundType


class MatchFoulEventCreate(PlayerEventBase):
    foul_type: FoulType
    fouled_player_id: uuid.UUID


class MatchPassEventCreate(PlayerEventBase):
    reciver_player_id: uuid.UUID


class MatchStealEventCreate(PlayerEventBase):
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
