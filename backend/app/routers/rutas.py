from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.ruta import Ruta
from app.models.user import User
from app.schemas.ruta import RutaCreate, RutaUpdate, RutaResponse
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/rutas", tags=["Rutas"])


@router.get("/", response_model=List[RutaResponse])
def get_rutas(
    skip: int = 0,
    limit: int = 100,
    repartidor_id: int = None,
    activa: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de rutas"""
    query = db.query(Ruta)
    
    if repartidor_id:
        query = query.filter(Ruta.repartidor_id == repartidor_id)
    if activa is not None:
        query = query.filter(Ruta.activa == activa)
    
    rutas = query.offset(skip).limit(limit).all()
    return rutas


@router.get("/{ruta_id}", response_model=RutaResponse)
def get_ruta(
    ruta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener ruta por ID"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta


@router.post("/", response_model=RutaResponse, status_code=status.HTTP_201_CREATED)
def create_ruta(
    ruta: RutaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva ruta"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear rutas")
    
    new_ruta = Ruta(**ruta.dict())
    db.add(new_ruta)
    db.commit()
    db.refresh(new_ruta)
    return new_ruta


@router.put("/{ruta_id}", response_model=RutaResponse)
def update_ruta(
    ruta_id: int,
    ruta_update: RutaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar ruta"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar rutas")
    
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    update_data = ruta_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ruta, key, value)
    
    db.commit()
    db.refresh(ruta)
    return ruta


@router.delete("/{ruta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ruta(
    ruta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar ruta"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar rutas")
    
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    db.delete(ruta)
    db.commit()
    return None
