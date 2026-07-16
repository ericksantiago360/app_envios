from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    direccion = Column(String(255))
    ciudad = Column(String(100))
    codigo_postal = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="cliente")
    envios_origen = relationship("Envio", foreign_keys="Envio.cliente_origen_id", back_populates="cliente_origen")
    envios_destino = relationship("Envio", foreign_keys="Envio.cliente_destino_id", back_populates="cliente_destino")
