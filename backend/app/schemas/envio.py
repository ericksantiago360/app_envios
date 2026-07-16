from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class EnvioBase(BaseModel):
    descripcion: Optional[str] = None
    peso: Optional[float] = None
    alto: Optional[float] = None
    ancho: Optional[float] = None
    largo: Optional[float] = None

    direccion_origen: str
    ciudad_origen: str
    codigo_postal_origen: Optional[str] = None
    lat_origen: Optional[float] = None
    lng_origen: Optional[float] = None

    direccion_destino: str
    ciudad_destino: str
    codigo_postal_destino: Optional[str] = None
    lat_destino: Optional[float] = None
    lng_destino: Optional[float] = None

    costo: float
    tipo_pago: Optional[str] = None
    notas: Optional[str] = None

    # Convertir strings vacíos a None automáticamente
    @field_validator(
        'descripcion', 'codigo_postal_origen', 'codigo_postal_destino',
        'tipo_pago', 'notas', mode='before'
    )
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    @field_validator('peso', 'alto', 'ancho', 'largo', 'lat_origen', 'lng_origen', 'lat_destino', 'lng_destino', mode='before')
    @classmethod
    def empty_str_to_none_float(cls, v):
        if v == '' or v is None:
            return None
        return v


class EnvioCreate(EnvioBase):
    cliente_origen_id: int
    cliente_destino_id: int
    repartidor_id: Optional[int] = None
    fecha_entrega_estimada: Optional[datetime] = None

    @field_validator('repartidor_id', mode='before')
    @classmethod
    def empty_int_to_none(cls, v):
        if v == '' or v == 0:
            return None
        return v


class EnvioUpdate(BaseModel):
    descripcion: Optional[str] = None
    peso: Optional[float] = None
    alto: Optional[float] = None
    ancho: Optional[float] = None
    largo: Optional[float] = None

    direccion_destino: Optional[str] = None
    ciudad_destino: Optional[str] = None
    codigo_postal_destino: Optional[str] = None

    repartidor_id: Optional[int] = None
    estado: Optional[str] = None
    costo: Optional[float] = None
    tipo_pago: Optional[str] = None
    fecha_recoleccion: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None
    notas: Optional[str] = None

    @field_validator('repartidor_id', mode='before')
    @classmethod
    def empty_int_to_none(cls, v):
        if v == '' or v == 0:
            return None
        return v


class EnvioResponse(EnvioBase):
    id: int
    numero_guia: str
    cliente_origen_id: int
    cliente_destino_id: int
    repartidor_id: Optional[int] = None
    estado: str
    fecha_creacion: datetime
    fecha_recoleccion: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None
    lat_origen: Optional[float] = None
    lng_origen: Optional[float] = None
    lat_destino: Optional[float] = None
    lng_destino: Optional[float] = None

    class Config:
        from_attributes = True
