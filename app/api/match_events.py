from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import basketball_read, basketball_write
from app.db.session import get_db
from app.models.basketball import MatchEvent
from app.schemas.match_event import (
    MatchScoringEventCreate, MatchScoringEventRead,
    MatchReboundEventCreate, MatchReboundEventRead,
    MatchFoulEventCreate, MatchFoulEventRead,
    MatchPassEventCreate, MatchPassEventRead,
    MatchStealEventCreate, MatchStealEventRead,
    MatchEventReadUnion
)
from app.services.match_events import record_event, delete_event

router = APIRouter(prefix="/matches/{match_id}/events", tags=["basketball: events"])

@router.get("", response_model=list[MatchEventReadUnion])
async def list_events(
    match_id: UUID,
     _: Annotated[dict,Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    type_filter: str | None = None,
):
    q = await db.query(MatchEvent).filter(MatchEvent.match_id == match_id).order_by(MatchEvent.current_set.asc(),MatchEvent.set_elapsed_sec.asc(),)
    if type_filter:
        q = q.where(MatchEvent.event_type == type_filter)
    r = await db.execute(q)
    return list(r.scalars().all())

@router.post("/scoring", response_model=MatchScoringEventRead, status_code=status.HTTP_201_CREATED,)
async def create_scoring_event(
    match_id: UUID,
    data: MatchScoringEventCreate,
     _: Annotated[dict,Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        event = await record_event(db, match_id, data)
        await db.commit()
        await db.refresh(event)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return event

@router.post("/rebound", response_model=MatchReboundEventRead, status_code=status.HTTP_201_CREATED,)
async def create_rebound_event(
    match_id: UUID,
    data: MatchReboundEventCreate,
     _: Annotated[dict,Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        event = await record_event(db, match_id, data)
        await db.commit()
        await db.refresh(event)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return event

@router.post("/pass", response_model=MatchPassEventRead, status_code=status.HTTP_201_CREATED,)
async def create_pass_event(
    match_id: UUID,
    data: MatchPassEventCreate,
     _: Annotated[dict,Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        event = await record_event(db, match_id, data)
        await db.commit()
        await db.refresh(event)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return event

@router.post("/foul", response_model=MatchFoulEventRead, status_code=status.HTTP_201_CREATED,)
async def create_foul_event(
    match_id: UUID,
    data: MatchFoulEventCreate,
     _: Annotated[dict,Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        event = await record_event(db, match_id, data)
        await db.commit()
        await db.refresh(event)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return event

@router.post("/steal", response_model=MatchStealEventRead, status_code=status.HTTP_201_CREATED,)
async def create_steal_event(
    match_id: UUID,
    data: MatchStealEventCreate,
     _: Annotated[dict,Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        event = await record_event(db, match_id, data)
        await db.commit()
        await db.refresh(event)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return event

@router.delete("/{event_id}", status_code=204)
async def delete_match_event(
    match_id: UUID,
    event_id: UUID,
     _: Annotated[dict,Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    event = await db.get(MatchEvent, event_id)
    if event is None or event.match_id != match_id:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    try:
        await delete_event(db, event_id)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))