from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class RutaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    zonas: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    dias_activos: Optional[str] = None
    activa: bool = True

    @field_validator('descripcion', 'zonas', 'hora_inicio', 'hora_fin', 'dias_activos', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v


class RutaCreate(RutaBase):
    repartidor_id: int


class RutaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    zonas: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    dias_activos: Optional[str] = None
    activa: Optional[bool] = None

    @field_validator('descripcion', 'zonas', 'hora_inicio', 'hora_fin', 'dias_activos', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v


class RutaResponse(RutaBase):
    id: int
    repartidor_id: int
    created_at: datetime

    class Config:
        from_attributes = True
