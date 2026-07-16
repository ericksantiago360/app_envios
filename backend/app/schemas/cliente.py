from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None

    @field_validator('telefono', 'direccion', 'ciudad', 'codigo_postal', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v


class ClienteCreate(ClienteBase):
    user_id: Optional[int] = None


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None

    @field_validator('telefono', 'direccion', 'ciudad', 'codigo_postal', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v


class ClienteResponse(ClienteBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
