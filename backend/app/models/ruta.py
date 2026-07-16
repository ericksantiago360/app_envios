from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    repartidor_id = Column(Integer, ForeignKey("repartidores.id"), nullable=False)
    
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    
    # Zonas/ciudades que cubre
    zonas = Column(Text)  # Almacenar como JSON string o separado por comas
    
    # Horarios
    hora_inicio = Column(String(10))  # formato HH:MM
    hora_fin = Column(String(10))  # formato HH:MM
    
    # Días de la semana (como bits o lista)
    dias_activos = Column(String(50))  # lun,mar,mie,jue,vie,sab,dom
    
    # Estado
    activa = Column(Boolean, default=True)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    repartidor = relationship("Repartidor", back_populates="rutas")
