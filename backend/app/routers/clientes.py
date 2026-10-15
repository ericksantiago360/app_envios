from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.cliente import Cliente
from app.models.user import User
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


@router.get("/", response_model=List[ClienteResponse])
def get_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de clientes"""
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes


@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener cliente por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def create_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo cliente"""
    # Solo el admin puede vincular el cliente a la cuenta de otro usuario
    if current_user.role != "admin" and cliente.user_id not in (None, current_user.id):
        raise HTTPException(status_code=403, detail="No puedes vincular el cliente a otro usuario")

    new_cliente = Cliente(**cliente.model_dump())
    db.add(new_cliente)
    db.commit()
    db.refresh(new_cliente)
    return new_cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Solo el admin o el propio cliente pueden editar el perfil
    if current_user.role != "admin" and cliente.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar este cliente")

    update_data = cliente_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)
    
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar cliente"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar clientes")
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(cliente)
    db.commit()
    return None
