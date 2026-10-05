from datetime import datetime, timezone
from turtle import position
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import basketball_read, basketball_write
from app.db.session import get_db
from app.models.athlete_mirror import AthleteMirror
from app.models.basketball import Player
from app.schemas.player import PlayerCreate, PlayerRead

router = APIRouter(prefix="/players", tags=["basketball-players"])

def _nombre_completo(a: AthleteMirror) -> str:
    parts = [a.primer_nombre, a.segundo_nombre, a.primer_apellido, a.segundo_apellido]
    return " ".join(p for p in parts if p)


@router.get("", response_model=list[PlayerRead])
async def list_players(
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
    solo_activos: bool = True,
    buscar: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    q = select(Player, AthleteMirror).join(AthleteMirror, Player.athlete_id == AthleteMirror.id)
    if solo_activos:
        q = q.where(Player.active.is_(True), AthleteMirror.activo.is_(True))
    if buscar and buscar.strip():
        pat = f"%{buscar.strip()}%"
        q = q.where(
            or_(
                AthleteMirror.primer_nombre.ilike(pat),
                AthleteMirror.primer_apellido.ilike(pat),
                AthleteMirror.documento_identidad.ilike(pat),
            )
        )
    q = q.order_by(AthleteMirror.primer_apellido, AthleteMirror.primer_nombre).offset(skip).limit(limit)
    r = await db.execute(q)
    out = []
    for j, a in r.all():
        out.append(
            PlayerRead(
                id=j.id,
                athlete_id=j.athlete_id,
                active=j.active,
                primer_nombre=a.primer_nombre,
                primer_apellido=a.primer_apellido,
                segundo_nombre=a.segundo_nombre,
                segundo_apellido=a.segundo_apellido,
                nombre_completo=_nombre_completo(a),
                documento_identidad=a.documento_identidad,
                number=j.number,
                position=j.position, 
                team_id= j.team_id
            )
        )
    return out


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
async def create_player_with_athlete(
    body: PlayerCreate,
    _: Annotated[dict, Depends(basketball_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if body.documento_identidad:
        ex = await db.scalar(
            select(AthleteMirror).where(AthleteMirror.documento_identidad == body.documento_identidad.strip())
        )
        if ex:
            raise HTTPException(status.HTTP_409_CONFLICT, "Documento ya registrado como deportista")

    now = datetime.now(timezone.utc)
    athlete = AthleteMirror(
        primer_nombre=body.primer_nombre.strip(),
        segundo_nombre=body.segundo_nombre.strip() if body.segundo_nombre else None,
        primer_apellido=body.primer_apellido.strip(),
        segundo_apellido=body.segundo_apellido.strip() if body.segundo_apellido else None,
        fecha_nacimiento=body.fecha_nacimiento,
        sexo=str(body.sexo).lower().strip(),
        lateralidad=body.lateralidad,
        documento_identidad=body.documento_identidad.strip() if body.documento_identidad else None,
        deporte_principal="basketball",
        notas=body.notas,
        activo=True,
        updated_at=now,
    )
    db.add(athlete)
    await db.flush()

    j = Player(
        athlete_id=athlete.id,
        active=True,
        updated_at=now,
    )
    db.add(j)
    await db.commit()
    await db.refresh(athlete)
    await db.refresh(j)

    return PlayerRead(
        id=j.id,
        athlete_id=j.athlete_id,
        active=j.active,
        primer_nombre=athlete.primer_nombre,
        primer_apellido=athlete.primer_apellido,
        segundo_nombre=athlete.segundo_nombre,
        segundo_apellido=athlete.segundo_apellido,
        nombre_completo=_nombre_completo(athlete),
        documento_identidad=athlete.documento_identidad,
        number=j.number,
        position=j.position,
        team_id=j.team_id
    )

@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(
    player_id: UUID,
    _: Annotated[dict, Depends(basketball_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    r = await db.execute(
        select(Player, AthleteMirror)
        .join(AthleteMirror, Player.athlete_id == AthleteMirror.id)
        .where(Player.id == player_id)
    )
    row = r.one_or_none()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Jugador no encontrado")
    j, a = row
    return PlayerRead(
        id=j.id,
        athlete_id=j.athlete_id,
        active=j.active,
        primer_nombre=a.primer_nombre,
        primer_apellido=a.primer_apellido,
        segundo_nombre=a.segundo_nombre,
        segundo_apellido=a.segundo_apellido,
        nombre_completo=_nombre_completo(a),
        documento_identidad=a.documento_identidad,
        number=j.number,
        position=j.position,
        team_id=j.team_id 
    )
