from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from app.db.database import get_db
from app.models.repartidor import Repartidor
from app.models.envio import Envio
from app.models.user import User
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/tracking", tags=["Tracking GPS"])


class UbicacionGPS(BaseModel):
    lat: float
    lng: float


class RepartidorUbicacion(BaseModel):
    id: int
    nombre: str
    apellido: str
    vehiculo: str
    lat_actual: float
    lng_actual: float
    ultima_actualizacion_gps: datetime
    disponible: bool

    class Config:
        from_attributes = True


class EnvioMapa(BaseModel):
    id: int
    numero_guia: str
    descripcion: str
    estado: str
    direccion_origen: str
    ciudad_origen: str
    lat_origen: float = None
    lng_origen: float = None
    direccion_destino: str
    ciudad_destino: str
    lat_destino: float = None
    lng_destino: float = None
    repartidor_id: int = None

    class Config:
        from_attributes = True


@router.put("/repartidor/ubicacion", response_model=dict)
def actualizar_ubicacion_repartidor(
    ubicacion: UbicacionGPS,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar ubicación GPS del repartidor (solo para repartidores)"""
    if current_user.role != "repartidor" or not current_user.repartidor:
        raise HTTPException(status_code=403, detail="Solo repartidores pueden actualizar su ubicación")
    
    repartidor = current_user.repartidor
    repartidor.lat_actual = ubicacion.lat
    repartidor.lng_actual = ubicacion.lng
    repartidor.ultima_actualizacion_gps = datetime.utcnow()
    
    db.commit()
    
    return {
        "mensaje": "Ubicación actualizada",
        "lat": repartidor.lat_actual,
        "lng": repartidor.lng_actual,
        "timestamp": repartidor.ultima_actualizacion_gps
    }


@router.get("/repartidores", response_model=List[RepartidorUbicacion])
def obtener_repartidores_mapa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener ubicaciones de todos los repartidores activos"""
    repartidores = db.query(Repartidor).filter(
        Repartidor.lat_actual.isnot(None),
        Repartidor.lng_actual.isnot(None)
    ).all()
    
    return repartidores


@router.get("/envios", response_model=List[EnvioMapa])
def obtener_envios_mapa(
    estado: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener envíos para mostrar en el mapa"""
    query = db.query(Envio)
    
    # Filtros según rol
    if current_user.role == "cliente":
        if current_user.cliente:
            query = query.filter(
                (Envio.cliente_origen_id == current_user.cliente.id) | 
                (Envio.cliente_destino_id == current_user.cliente.id)
            )
        else:
            return []
    elif current_user.role == "repartidor":
        if current_user.repartidor:
            query = query.filter(Envio.repartidor_id == current_user.repartidor.id)
        else:
            return []
    
    if estado:
        query = query.filter(Envio.estado == estado)
    
    envios = query.all()
    return envios


@router.get("/envio/{envio_id}/ruta", response_model=dict)
def obtener_ruta_envio(
    envio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener ruta completa de un envío (origen -> repartidor -> destino)"""
    envio = db.query(Envio).filter(Envio.id == envio_id).first()
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    # Verificar permisos
    if current_user.role == "cliente":
        if current_user.cliente and (
            envio.cliente_origen_id != current_user.cliente.id and 
            envio.cliente_destino_id != current_user.cliente.id
        ):
            raise HTTPException(status_code=403, detail="No tienes acceso a este envío")
    elif current_user.role == "repartidor":
        if current_user.repartidor and envio.repartidor_id != current_user.repartidor.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este envío")
    
    ruta = {
        "envio_id": envio.id,
        "numero_guia": envio.numero_guia,
        "estado": envio.estado,
        "origen": {
            "direccion": envio.direccion_origen,
            "ciudad": envio.ciudad_origen,
            "lat": envio.lat_origen,
            "lng": envio.lng_origen
        },
        "destino": {
            "direccion": envio.direccion_destino,
            "ciudad": envio.ciudad_destino,
            "lat": envio.lat_destino,
            "lng": envio.lng_destino
        },
        "repartidor": None
    }
    
    if envio.repartidor:
        ruta["repartidor"] = {
            "id": envio.repartidor.id,
            "nombre": f"{envio.repartidor.nombre} {envio.repartidor.apellido}",
            "vehiculo": envio.repartidor.vehiculo,
            "lat_actual": envio.repartidor.lat_actual,
            "lng_actual": envio.repartidor.lng_actual,
            "ultima_actualizacion": envio.repartidor.ultima_actualizacion_gps
        }
    
    return ruta
