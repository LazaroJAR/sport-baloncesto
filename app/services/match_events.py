import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.basketball import MatchSideStats, Match
from app.models.basketball import (
    MatchEvent, MatchScoringEvent, MatchReboundEvent,
    MatchFoulEvent, MatchPassEvent, MatchStealEvent,
)
from app.schemas import player
from app.schemas.match_event import MatchEventBase

async def _get_or_create_stats(db: Session, match_id: uuid.UUID, side: str) -> MatchSideStats:
    # Intenta crear la fila si no existe
    stmt = pg_insert(MatchSideStats).values(
        id=uuid.uuid4(),
        match_id=match_id,
        side=side,
        total_scored_points=0,
        total_points_allowed=0,
        field_goals_attempted=0,
        field_goals_attempted_3_points=0,
        field_goals_scored=0,
        field_goals_scored_3_points=0,
        free_throws_attempted=0,
        free_throws_scored=0,
        offensive_rebound=0,
        defensive_rebound=0,
        #fiba_ranking_position=0,   o el valor que corresponda
    ).on_conflict_do_nothing(index_elements=["match_id", "side"])
    await db.execute(stmt)

    # Bloquea la fila para actualizarla de forma segura
    return await db.execute(
        select(MatchSideStats)
        .where(MatchSideStats.match_id == match_id, MatchSideStats.side == side)
        .with_for_update()
    ).scalar_one()

def _build_event(match_id: uuid.UUID, data: MatchEventBase) -> MatchEvent:
    base = dict(
        match_id=match_id,
        event_type=data.event_type,
        current_set=data.current_set,
        set_elapsed_sec=data.set_elapsed_sec,
    )
    if data.event_type == "scoring":
        return MatchScoringEvent(
            **base,
            player_id=data.player_id,
            side=data.side,
            has_scored=data.has_scored,
            points=data.points,
            scoring_type=data.scoring_type,
            previous_action=data.previous_action,
        )
    elif data.event_type == "rebound":
        return MatchReboundEvent(
            **base,
            player_id=data.player_id,
            side=data.side,
            rebound_type=data.rebound_type,
        )
    elif data.event_type == "foul":
        return MatchFoulEvent(
            **base,
            player_id=data.player_id,
            side=data.side,
            foul_type=data.foul_type,
            fouled_player_id=data.fouled_player_id,
        )
    elif data.event_type == "pass":
        return MatchPassEvent(
            **base,
            player_id = data.player_id,
            side=data.side,
            reciver_player_id=data.reciver_player_id
        )
    elif data.event_type == "steal":
        return MatchStealEvent(
            **base,
            player_id = data.player_id,
            side=data.side,
            stolen_from_player_id=data.stolen_from_player_id
        )
    else:
        raise ValueError(f"Tipo de evento no soportado: {data.type}")


def _apply_scoring(stats_side: MatchSideStats, stats_opp: MatchSideStats, ev: MatchScoringEvent):
    if ev.has_scored:
        stats_side.total_scored_points += ev.points
        stats_opp.total_points_allowed += ev.points

    if ev.scoring_type == "tiro_libre":
        stats_side.free_throws_attempted += 1
        if ev.has_scored:
            stats_side.free_throws_scored += 1
    elif ev.scoring_type == "tiro_de_cancha":
        stats_side.field_goals_attempted += 1
        if ev.points == 3:
            stats_side.field_goals_attempted_3_points += 1
        if ev.has_scored:
            stats_side.field_goals_scored += 1
            if ev.points == 3:
                stats_side.field_goals_scored_3_points += 1


def _apply_event_to_stats(
    stats_red: MatchSideStats,
    stats_blue: MatchSideStats,
    event: MatchEvent,
):
    if event.side == "red":
        stats_side, stats_opp = stats_red, stats_blue
    else:
        stats_side, stats_opp = stats_blue, stats_red

    if isinstance(event, MatchScoringEvent):
        _apply_scoring(stats_side, stats_opp, event)
    elif isinstance(event, MatchReboundEvent):
        if event.rebound_type == "ofensivo":
            stats_side.offensive_rebound += 1
        elif event.rebound_type == "defensivo":
            stats_side.defensive_rebound += 1


async def record_event(db: Session, match_id: uuid.UUID, data: MatchEventBase) -> MatchEvent:
    # 1. Validar partido
    match = await db.get(Match, match_id)
    if not match:
        raise ValueError("Partido no encontrado")
    if match.status not in ("in_progress", "finished"):
        raise ValueError("El partido no está en curso")

    # 2. Bloquear stats en orden consistente para evitar deadlocks
    stats_red = _get_or_create_stats(db, match_id, "red")
    stats_blue = _get_or_create_stats(db, match_id, "blue")

    # 3. Crear e insertar el evento
    event = _build_event(match_id, data)
    db.add(event)
    await db.flush()  # para obtener el id si lo necesitas

    # 4. Actualizar estadísticas
    _apply_event_to_stats(stats_red, stats_blue, event)

    await db.flush()
    return event


async def recalculate_stats(db: Session, match_id: uuid.UUID):
    stats_red = _get_or_create_stats(db, match_id, "red")
    stats_blue = _get_or_create_stats(db, match_id, "blue")

    # Resetear todos los campos a cero
    for s in (stats_red, stats_blue):
        s.total_scored_points = 0
        s.total_points_allowed = 0
        s.field_goals_attempted = 0
        s.field_goals_attempted_3_points = 0
        s.field_goals_scored = 0
        s.field_goals_scored_3_points = 0
        s.free_throws_attempted = 0
        s.free_throws_scored = 0
        s.offensive_rebound = 0
        s.defensive_rebound = 0
        # ... etc.

    events = await db.execute(
        select(MatchEvent).where(MatchEvent.match_id == match_id)
    ).scalars().all()

    for ev in events:
        _apply_event_to_stats(stats_red, stats_blue, ev)

    await db.flush()

async def delete_event(db: Session, event_id: uuid.UUID):
    event = await db.get(MatchEvent, event_id)
    if not event:
        raise ValueError("Evento no encontrado")
    match_id = event.match_id
    await db.delete(event)
    await db.flush()
    await recalculate_stats(db, match_id)

