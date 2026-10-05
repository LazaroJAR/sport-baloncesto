import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

SCHEMA = "basketball"


class SuiteEvent(Base):
    __tablename__ = "suite_events"
    __table_args__ = (
        UniqueConstraint("code", name="uq_basketball_suite_events_code"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, default="CUB")
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    scope: Mapped[str] = mapped_column(String(24), nullable=False, default="national")
    event_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="championship")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Player(Base):
    __tablename__ = "players"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deportistas.athletes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.teams.id", ondelete="RESTRICT"),
        nullable=True,
    )
    position: Mapped[str] = mapped_column(String(50), nullable=False) 
    number: Mapped[int] = mapped_column(Integer, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())





class Team(Base):
    __tablename__ = "teams"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    short_name: Mapped[str] = mapped_column(String(3), nullable=False)
    headquarters: Mapped[str] = mapped_column(String(120), nullable=True)
    fiba_position: Mapped[int] = mapped_column(Integer, nullable=True)
    players_gender: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Match(Base):
    __tablename__= "matchs"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.suite_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    red_team: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.teams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    blue_team: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.teams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    regulation: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.regulations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capture_mode: Mapped[str] = mapped_column(String(16), nullable=False)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft")
    winner_side: Mapped[str | None] = mapped_column(String(8), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Regulation(Base):
    __tablename__= "regulations"
    __table_args__= (
            UniqueConstraint("code", name="uq_basketball_regulations_code"), 
            {"schema": SCHEMA},
        )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    set_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=600)
    possesion_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    gender: Mapped[str | None] = mapped_column(String(12), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class MatchEvent(Base):
    __tablename__= "match_events"
    __table_args__ = (
        Index("ix_basketball_match_events_match", "match_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.matchs.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    current_set: Mapped[int] = mapped_column(Integer, nullable=False)
    set_elapsed_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __mapper_args__= { 
                    "polymorphic_on" : event_type,
                    "polymorphic_identity": "event",}
    
class PlayerEvent(MatchEvent):
    __abstract__= True
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.players.id", ondelete="CASCADE"),
        nullable=False,
    ) 
    side: Mapped[str] = mapped_column(String(8), nullable=False) 



class MatchScoringEvent(PlayerEvent):
    __tablename__="match_scoring_events"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.match_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    has_scored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    scoring_type: Mapped[str] = mapped_column(String(50), nullable=False) #Tiro libre, Tiro de cancha
    previous_action: Mapped[str] = mapped_column(String(50), nullable=True) #Catch & Shot, Dribling, Pick & Roll, Pick & Pop
    __mapper_args__ = {"polymorphic_identity": "scoring"}


class MatchReboundEvent(PlayerEvent):
    __tablename__="match_rebound_events"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.match_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rebound_type: Mapped[str] = mapped_column(String(20), nullable=False) #ofensivo o defensivo
    __mapper_args__ = {"polymorphic_identity": "rebound"}


class MatchFoulEvent(PlayerEvent):
    __tablename__ = "match_foul_events"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.match_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    foul_type: Mapped[str] = mapped_column(String(32), nullable=False)
    fouled_player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.players.id", ondelete="CASCADE"),
        nullable=False,
    ) 
    __mapper_args__ = {"polymorphic_identity": "foul"}


class MatchPassEvent(PlayerEvent):
    __tablename__="match_pass_events"
    __table_args__= {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.match_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    reciver_player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.players.id", ondelete="CASCADE"),
        nullable=False,
    ) 
    __mapper_args__ = {"polymorphic_identity": "pass"}

class MatchStealEvent(PlayerEvent):
    __tablename__="match_steal_events"
    __table_args__= {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.match_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    stolen_from_player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.players.id", ondelete="CASCADE"),
        nullable=False,
    ) 
    __mapper_args__ = {"polymorphic_identity": "steal"}


class MatchSideStats(Base):
    __tablename__= "match_side_stats"
    __table_args__ = (
        UniqueConstraint("match_id","side", name="uq_basketball_match_side_stats_match_side"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.matchs.id", ondelete="CASCADE"),
        nullable=False,
    )
    side: Mapped[str] = mapped_column(String(8), nullable=False) 
    total_scored_points: Mapped[int] = mapped_column(Integer, nullable=False) #PTS
    total_points_allowed: Mapped[int] = mapped_column(Integer, nullable=False) #PTP
    field_goals_attempted: Mapped[int] = mapped_column(Integer, nullable=False) #FGA
    field_goals_attempted_3_points: Mapped[int] = mapped_column(Integer, nullable=False) #FGA 3
    field_goals_scored: Mapped[int] = mapped_column(Integer, nullable=False) #FGS
    field_goals_scored_3_points: Mapped[int] = mapped_column(Integer, nullable=False) #FGS 3
    free_throws_attempted: Mapped[int] = mapped_column(Integer, nullable=False) #FTA
    free_throws_scored: Mapped[int] = mapped_column(Integer, nullable=False) #FTS
    offensive_rebound: Mapped[int] = mapped_column(Integer, nullable=False)  #ORB
    defensive_rebound: Mapped[int] = mapped_column(Integer, nullable=False)  #DRB
    fiba_ranking_position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
