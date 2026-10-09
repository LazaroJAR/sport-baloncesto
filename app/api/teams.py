from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import basketball_read, basketball_write
from app.db.session import get_db
from app.models.basketball import Team
from app.schemas.team import TeamCreate, TeamRead

router = APIRouter(prefix="/teams", tags=["basketball-teams"])

@router.get("", response_model=list[TeamRead])
async def list_teams(
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
    buscar: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    q = select(Team).order_by(Team.scheduled_at.desc())
    if buscar and buscar.strip():
        pat = f"%{buscar.strip()}%"
        q = q.where(Team.name.ilike(pat))
    
    q = q.order_by(Team.name).offset(skip).limit(limit)
    r = await db.execute(q)
    return list(r.scalars().all())

@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    body: TeamCreate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    b = Team(
        name = body.name,
        short_name = body.short_name,
        headquarters = body.headquarters,
        fiba_position = body.fiba_position,
        players_gender = body.players_gender,
        updated_at=datetime.now(timezone.utc)
    )
    db.add(b)
    await db.commit()
    await db.refresh(b)
    return b

@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    team_id: UUID,
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    t = await db.get(Team, team_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return t

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    _: Annotated[dict, Depends(basketball_read)], 
    db: Annotated[AsyncSession, Depends(get_db)],
):
    t = await db.get(Team, team_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    db.delete(t)
    db.commit()