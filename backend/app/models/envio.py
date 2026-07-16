from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Envio(Base):
    __tablename__ = "envios"

    id = Column(Integer, primary_key=True, index=True)
    numero_guia = Column(String(50), unique=True, index=True, nullable=False)
    
    # Cliente origen y destino
    cliente_origen_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente_destino_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Repartidor asignado
    repartidor_id = Column(Integer, ForeignKey("repartidores.id"), nullable=True)
    
    # Detalles del envío
    descripcion = Column(Text)
    peso = Column(Float)  # en kg
    alto = Column(Float)  # en cm
    ancho = Column(Float)  # en cm
    largo = Column(Float)  # en cm
    
    # Direcciones
    direccion_origen = Column(String(255), nullable=False)
    ciudad_origen = Column(String(100), nullable=False)
    codigo_postal_origen = Column(String(10))
    lat_origen = Column(Float, nullable=True)  # Latitud origen
    lng_origen = Column(Float, nullable=True)  # Longitud origen
    
    direccion_destino = Column(String(255), nullable=False)
    ciudad_destino = Column(String(100), nullable=False)
    codigo_postal_destino = Column(String(10))
    lat_destino = Column(Float, nullable=True)  # Latitud destino
    lng_destino = Column(Float, nullable=True)  # Longitud destino
    
    # Estado y costos
    estado = Column(String(50), nullable=False)  # pendiente, en_transito, entregado, cancelado
    costo = Column(Float, nullable=False)
    tipo_pago = Column(String(20))  # efectivo, tarjeta, transferencia
    
    # Fechas
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_recoleccion = Column(DateTime, nullable=True)
    fecha_entrega_estimada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)
    
    # Observaciones
    notas = Column(Text)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    cliente_origen = relationship("Cliente", foreign_keys=[cliente_origen_id], back_populates="envios_origen")
    cliente_destino = relationship("Cliente", foreign_keys=[cliente_destino_id], back_populates="envios_destino")
    repartidor = relationship("Repartidor", back_populates="envios")
