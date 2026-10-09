from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import basketball_read, basketball_write
from app.db.session import get_db
from app.models.basketball import SuiteEvent, Regulation
from app.schemas.suite_event import SuiteEventCreate, SuiteEventRead
from app.schemas.regulation import RegulationCreate, RegulationRead

router = APIRouter(tags=["basketball-catalogo"])

@router.post("/suite-events", response_model=SuiteEventRead, status_code=status.HTTP_201_CREATED)
async def create_suite_event(
    body: SuiteEventCreate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    s = SuiteEvent(**body.model_dump())
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s

@router.get("/suite-events", response_model=list[SuiteEventRead])
async def list_suite_events(
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    r = await db.execute(select(SuiteEvent).order_by(SuiteEvent.starts_on.desc()))
    return list(r.scalars().all())

@router.get("/suite-events/{suite_event_id}", response_model=SuiteEventRead)
async def get_suite_event(
    suite_event_id: UUID,
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    s = await db.get(SuiteEvent, suite_event_id)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento no encontrado")
    return s

@router.get("/regulations", response_model=list[RegulationRead])
async def list_regulations(
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    r = await db.execute(select(Regulation).order_by(Regulation.name))
    return list(r.scalars().all())

@router.post("/regulations", response_model=RegulationRead, status_code=status.HTTP_201_CREATED)
async def create_regulation(
    body: RegulationCreate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    reg = Regulation(**body.model_dump())
    db.add(reg)
    await db.commit()
    await db.refresh(reg)
    return reg

