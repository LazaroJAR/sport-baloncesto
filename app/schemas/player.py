import uuid
from datetime import date

from pydantic import BaseModel, Field, field_validator
from app.schemas.literals import Gender, Position

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
