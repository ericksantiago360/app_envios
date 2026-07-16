from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class RepartidorBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    vehiculo: Optional[str] = None
    placa_vehiculo: Optional[str] = None
    disponible: bool = True

    @field_validator('telefono', 'vehiculo', 'placa_vehiculo', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v


class RepartidorCreate(RepartidorBase):
    user_id: Optional[int] = None


class RepartidorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    vehiculo: Optional[str] = None
    placa_vehiculo: Optional[str] = None
    disponible: Optional[bool] = None

    @field_validator('telefono', 'vehiculo', 'placa_vehiculo', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v


class RepartidorResponse(RepartidorBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
