from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import random
import string
from app.db.database import get_db
from app.models.envio import Envio
from app.models.user import User
from app.schemas.envio import EnvioCreate, EnvioUpdate, EnvioResponse
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/envios", tags=["Envíos"])


def generar_numero_guia():
    """Generar número de guía único"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ENV-{timestamp}-{random_chars}"


@router.get("/", response_model=List[EnvioResponse])
def get_envios(
    skip: int = 0,
    limit: int = 100,
    estado: str = None,
    cliente_id: int = None,
    repartidor_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de envíos con filtros opcionales"""
    query = db.query(Envio)
    
    # Filtros basados en rol
    if current_user.role == "cliente":
        # Los clientes solo ven sus propios envíos
        if current_user.cliente:
            query = query.filter(
                (Envio.cliente_origen_id == current_user.cliente.id) | 
                (Envio.cliente_destino_id == current_user.cliente.id)
            )
        else:
            return []
    elif current_user.role == "repartidor":
        # Los repartidores solo ven sus envíos asignados
        if current_user.repartidor:
            query = query.filter(Envio.repartidor_id == current_user.repartidor.id)
        else:
            return []
    
    # Filtros adicionales
    if estado:
        query = query.filter(Envio.estado == estado)
    if cliente_id:
        query = query.filter(
            (Envio.cliente_origen_id == cliente_id) | 
            (Envio.cliente_destino_id == cliente_id)
        )
    if repartidor_id:
        query = query.filter(Envio.repartidor_id == repartidor_id)
    
    envios = query.offset(skip).limit(limit).all()
    return envios


@router.get("/tracking/{numero_guia}", response_model=EnvioResponse)
def track_envio(
    numero_guia: str,
    db: Session = Depends(get_db)
):
    """Rastrear envío por número de guía (público, sin autenticación)"""
    envio = db.query(Envio).filter(Envio.numero_guia == numero_guia).first()
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio


@router.get("/{envio_id}", response_model=EnvioResponse)
def get_envio(
    envio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener envío por ID"""
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
    
    return envio


@router.post("/", response_model=EnvioResponse, status_code=status.HTTP_201_CREATED)
def create_envio(
    envio: EnvioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo envío"""
    # Generar número de guía único
    numero_guia = generar_numero_guia()
    
    new_envio = Envio(
        numero_guia=numero_guia,
        estado="pendiente",
        **envio.dict()
    )
    
    db.add(new_envio)
    db.commit()
    db.refresh(new_envio)
    return new_envio


@router.put("/{envio_id}", response_model=EnvioResponse)
def update_envio(
    envio_id: int,
    envio_update: EnvioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar envío"""
    envio = db.query(Envio).filter(Envio.id == envio_id).first()
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    # Verificar permisos para actualización de estado
    if envio_update.estado:
        if current_user.role == "repartidor":
            # Repartidores solo pueden actualizar sus envíos asignados
            if current_user.repartidor and envio.repartidor_id != current_user.repartidor.id:
                raise HTTPException(status_code=403, detail="No puedes actualizar este envío")
        elif current_user.role == "cliente":
            # Los clientes no pueden actualizar el estado
            raise HTTPException(status_code=403, detail="No tienes permisos para actualizar el estado")
    
    update_data = envio_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(envio, key, value)
    
    # Actualizar fecha de entrega real si se marca como entregado
    if envio_update.estado == "entregado" and not envio.fecha_entrega_real:
        envio.fecha_entrega_real = datetime.utcnow()
    
    db.commit()
    db.refresh(envio)
    return envio


@router.delete("/{envio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_envio(
    envio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar envío"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar envíos")
    
    envio = db.query(Envio).filter(Envio.id == envio_id).first()
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    db.delete(envio)
    db.commit()
    return None
