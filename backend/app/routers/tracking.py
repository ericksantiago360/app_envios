from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from app.db.database import get_db
from app.models.repartidor import Repartidor
from app.models.envio import Envio
from app.models.user import User
from app.core.security import get_current_active_user, verificar_acceso_envio

router = APIRouter(prefix="/api/tracking", tags=["Tracking GPS"])


class UbicacionGPS(BaseModel):
    lat: float
    lng: float


class RepartidorUbicacion(BaseModel):
    id: int
    nombre: str
    apellido: str
    vehiculo: Optional[str] = None
    lat_actual: float
    lng_actual: float
    ultima_actualizacion_gps: Optional[datetime] = None
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
    """Obtener ubicaciones de repartidores visibles para el usuario.

    - admin: todos
    - repartidor: solo él mismo
    - cliente: solo los repartidores asignados a sus envíos en curso
    """
    query = db.query(Repartidor).filter(
        Repartidor.lat_actual.isnot(None),
        Repartidor.lng_actual.isnot(None)
    )

    if current_user.role == "repartidor":
        if not current_user.repartidor:
            return []
        query = query.filter(Repartidor.id == current_user.repartidor.id)
    elif current_user.role == "cliente":
        if not current_user.cliente:
            return []
        cliente_id = current_user.cliente.id
        repartidores_ids = db.query(Envio.repartidor_id).filter(
            Envio.repartidor_id.isnot(None),
            Envio.estado.in_(["pendiente", "en_transito"]),
            (Envio.cliente_origen_id == cliente_id) | (Envio.cliente_destino_id == cliente_id)
        )
        query = query.filter(Repartidor.id.in_(repartidores_ids))
    elif current_user.role != "admin":
        return []

    return query.all()


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
    
    verificar_acceso_envio(current_user, envio)

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
