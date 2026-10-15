from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.repartidor import Repartidor
from app.models.user import User
from app.schemas.repartidor import RepartidorCreate, RepartidorUpdate, RepartidorResponse
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/repartidores", tags=["Repartidores"])


@router.get("/", response_model=List[RepartidorResponse])
def get_repartidores(
    skip: int = 0,
    limit: int = 100,
    disponible: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de repartidores"""
    query = db.query(Repartidor)
    if disponible is not None:
        query = query.filter(Repartidor.disponible == disponible)
    repartidores = query.offset(skip).limit(limit).all()
    return repartidores


@router.get("/{repartidor_id}", response_model=RepartidorResponse)
def get_repartidor(
    repartidor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener repartidor por ID"""
    repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
    if not repartidor:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    return repartidor


@router.post("/", response_model=RepartidorResponse, status_code=status.HTTP_201_CREATED)
def create_repartidor(
    repartidor: RepartidorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo repartidor"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear repartidores")
    
    new_repartidor = Repartidor(**repartidor.model_dump())
    db.add(new_repartidor)
    db.commit()
    db.refresh(new_repartidor)
    return new_repartidor


@router.put("/{repartidor_id}", response_model=RepartidorResponse)
def update_repartidor(
    repartidor_id: int,
    repartidor_update: RepartidorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar repartidor"""
    repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
    if not repartidor:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")

    # Solo el admin o el propio repartidor pueden editar el perfil
    if current_user.role != "admin" and repartidor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este repartidor")

    update_data = repartidor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(repartidor, key, value)
    
    db.commit()
    db.refresh(repartidor)
    return repartidor


@router.delete("/{repartidor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repartidor(
    repartidor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar repartidor"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar repartidores")
    
    repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
    if not repartidor:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    
    db.delete(repartidor)
    db.commit()
    return None
