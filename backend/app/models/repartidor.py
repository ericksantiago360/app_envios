from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Repartidor(Base):
    __tablename__ = "repartidores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    vehiculo = Column(String(50))  # moto, auto, bicicleta, camioneta
    placa_vehiculo = Column(String(20))
    disponible = Column(Boolean, default=True)
    
    # Ubicación GPS en tiempo real
    lat_actual = Column(Float, nullable=True)
    lng_actual = Column(Float, nullable=True)
    ultima_actualizacion_gps = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="repartidor")
    envios = relationship("Envio", back_populates="repartidor")
    rutas = relationship("Ruta", back_populates="repartidor")
