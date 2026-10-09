from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import basketball_read, basketball_write
from app.db.session import get_db
from app.models.basketball import Match, MatchSideStats, Player, Regulation, Team
from app.schemas.match import (
    MatchCreate,
    MatchRead,
    MatchResultUpdate,
    MatchSideStatsPayload,
    MatchSideStatsRead,
    MatchUpdate, 
    MatchStatusUpdate,
    MatchStatsUpsert
)

router = APIRouter(prefix="/matches", tags=["basketball-partidos"])

async def _get_side_stats(db: AsyncSession, match_id: UUID) -> list[MatchSideStatsRead]:
    r = await db.execute(
        select(MatchSideStats).where(MatchSideStats.match_id == match_id).order_by(MatchSideStats.side)
    )
    return [MatchSideStatsRead.model_validate(x) for x in r.scalars().all()]

@router.get("", response_model=list[MatchRead])
async def list_matches(
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = None,
):
    q = select(Match).order_by(Match.scheduled_at.desc())
    if status_filter:
        q = q.where(Match.status == status_filter)
    r = await db.execute(q)
    return list(r.scalars().all())

@router.post("", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def create_match(
    body: MatchCreate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if body.red_team == body.blue_team:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "red_team y blue_team no pueden ser el mismo equipo")
    rt = await db.get(Team, body.red_team)
    bt = await db.get(Team, body.blue_team)
    if not rt or not bt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipos no encontrados")
    reg = await db.get(Regulation, body.regulation_id)
    if not reg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reglamento no encontrado")

    b = Match(
        suite_event_id=body.suite_event_id,
        regulation_id=body.regulation,
        red_team=body.red_team,
        blue_team=body.blue_team,
        scheduled_at=body.scheduled_at,
        capture_mode=body.capture_mode,
        video_url=body.video_url,
        notes=body.notes,
        status="draft",
        updated_at=datetime.now(timezone.utc),
    )
    db.add(b)
    await db.commit()
    await db.refresh(b)
    return b

@router.get("/{match_id}", response_model=MatchRead)
async def get_match(
    match_id: UUID,
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    m = await db.get(Match, match_id)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Partido no encontrado")
    return m

@router.get("/{match_id}/stats", response_model=list[MatchSideStatsRead])
async def get_match_stats(
    match_id: UUID,
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    b = await db.get(Match, match_id)
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Partido no encontrado")
    return await _get_side_stats(db, match_id)

@router.patch("/{match_id}/status", response_model=MatchRead)
async def update_match_status(
    match_id: UUID,
    body: MatchStatusUpdate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    b = await db.get(Match, match_id)
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Partido no encontrado")
    b.status = body.status
    b.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(b)
    return b

@router.patch("/{match_id}/result", response_model=MatchRead)
async def update_match_result(
    match_id: UUID,
    body: MatchResultUpdate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    b = await db.get(Match, match_id)
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Partido no encontrado")
    b.winner_side = body.winner_side
    b.status = "finished"
    b.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(b)
    return b
