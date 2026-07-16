"""
Script para inicializar datos de prueba en la base de datos

Ejecutar desde dentro del contenedor backend:
docker-compose exec backend python init_data.py
"""

import sys
import os
sys.path.append('/app')

from app.db.database import SessionLocal, engine, Base
from app.models import user, cliente, repartidor, envio, ruta  # importar todos los modelos
from app.models.user import User
from app.models.cliente import Cliente
from app.models.repartidor import Repartidor
from app.models.envio import Envio
from app.models.ruta import Ruta
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random


def init_data():
    # Crear todas las tablas si no existen
    print("🗄️  Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas listas\n")

    db = SessionLocal()

    try:
        print("🚀 Iniciando creación de datos de prueba...")
        
        # Crear usuarios
        print("\n👤 Creando usuarios...")
        
        # Admin
        admin_user = User(
            username="admin",
            email="admin@envios.com",
            full_name="Administrador del Sistema",
            role="admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        db.add(admin_user)
        
        # Repartidores
        repartidor1_user = User(
            username="carlos_rep",
            email="carlos@envios.com",
            full_name="Carlos Martínez",
            role="repartidor",
            hashed_password=get_password_hash("rep123"),
            is_active=True
        )
        db.add(repartidor1_user)
        
        repartidor2_user = User(
            username="maria_rep",
            email="maria@envios.com",
            full_name="María González",
            role="repartidor",
            hashed_password=get_password_hash("rep123"),
            is_active=True
        )
        db.add(repartidor2_user)
        
        # Clientes
        cliente1_user = User(
            username="juan_cliente",
            email="juan@cliente.com",
            full_name="Juan Pérez",
            role="cliente",
            hashed_password=get_password_hash("cliente123"),
            is_active=True
        )
        db.add(cliente1_user)
        
        cliente2_user = User(
            username="ana_cliente",
            email="ana@cliente.com",
            full_name="Ana López",
            role="cliente",
            hashed_password=get_password_hash("cliente123"),
            is_active=True
        )
        db.add(cliente2_user)
        
        db.commit()
        print("✅ Usuarios creados")
        
        # Crear clientes
        print("\n👥 Creando clientes...")
        
        cliente1 = Cliente(
            user_id=cliente1_user.id,
            nombre="Juan",
            apellido="Pérez",
            telefono="55-1234-5678",
            direccion="Av. Reforma 123",
            ciudad="Ciudad de México",
            codigo_postal="06600"
        )
        db.add(cliente1)
        
        cliente2 = Cliente(
            user_id=cliente2_user.id,
            nombre="Ana",
            apellido="López",
            telefono="55-8765-4321",
            direccion="Calle 5 de Mayo 456",
            ciudad="Guadalajara",
            codigo_postal="44100"
        )
        db.add(cliente2)
        
        cliente3 = Cliente(
            nombre="Roberto",
            apellido="Sánchez",
            telefono="81-1111-2222",
            direccion="Av. Universidad 789",
            ciudad="Monterrey",
            codigo_postal="64000"
        )
        db.add(cliente3)
        
        cliente4 = Cliente(
            nombre="Laura",
            apellido="Ramírez",
            telefono="33-3333-4444",
            direccion="Blvd. Ávila Camacho 321",
            ciudad="Puebla",
            codigo_postal="72000"
        )
        db.add(cliente4)
        
        db.commit()
        print("✅ Clientes creados")
        
        # Crear repartidores
        print("\n🚚 Creando repartidores...")
        
        repartidor1 = Repartidor(
            user_id=repartidor1_user.id,
            nombre="Carlos",
            apellido="Martínez",
            telefono="55-9999-1111",
            vehiculo="moto",
            placa_vehiculo="ABC-123",
            disponible=True
        )
        db.add(repartidor1)
        
        repartidor2 = Repartidor(
            user_id=repartidor2_user.id,
            nombre="María",
            apellido="González",
            telefono="55-8888-2222",
            vehiculo="camioneta",
            placa_vehiculo="XYZ-789",
            disponible=True
        )
        db.add(repartidor2)
        
        repartidor3 = Repartidor(
            nombre="Pedro",
            apellido="Hernández",
            telefono="55-7777-3333",
            vehiculo="auto",
            placa_vehiculo="DEF-456",
            disponible=False
        )
        db.add(repartidor3)
        
        db.commit()
        print("✅ Repartidores creados")
        
        # Crear rutas
        print("\n🗺️ Creando rutas...")
        
        ruta1 = Ruta(
            repartidor_id=repartidor1.id,
            nombre="Ruta Centro",
            descripcion="Cobertura del centro de la ciudad",
            zonas="Centro, Polanco, Condesa",
            hora_inicio="08:00",
            hora_fin="17:00",
            dias_activos="lun,mar,mie,jue,vie",
            activa=True
        )
        db.add(ruta1)
        
        ruta2 = Ruta(
            repartidor_id=repartidor2.id,
            nombre="Ruta Norte",
            descripcion="Zona norte y alrededores",
            zonas="Satélite, Lindavista, Indios Verdes",
            hora_inicio="09:00",
            hora_fin="18:00",
            dias_activos="lun,mar,mie,jue,vie,sab",
            activa=True
        )
        db.add(ruta2)
        
        db.commit()
        print("✅ Rutas creadas")
        
        # Crear envíos
        print("\n📦 Creando envíos...")
        
        estados = ["pendiente", "en_transito", "entregado"]
        descripciones = [
            "Documentos importantes",
            "Paquete pequeño",
            "Electrónica",
            "Ropa y accesorios",
            "Material de oficina"
        ]
        
        for i in range(10):
            estado = random.choice(estados)
            
            envio = Envio(
                numero_guia=f"ENV-20260427{i:06d}-TEST{i:02d}",
                cliente_origen_id=random.choice([cliente1.id, cliente2.id, cliente3.id]),
                cliente_destino_id=random.choice([cliente1.id, cliente2.id, cliente3.id, cliente4.id]),
                repartidor_id=random.choice([repartidor1.id, repartidor2.id]) if estado != "pendiente" else None,
                descripcion=random.choice(descripciones),
                peso=round(random.uniform(0.5, 15.0), 2),
                direccion_origen=f"Calle Origen {i+1}",
                ciudad_origen=random.choice(["Ciudad de México", "Guadalajara", "Monterrey"]),
                codigo_postal_origen=f"{random.randint(10000, 99999)}",
                direccion_destino=f"Calle Destino {i+1}",
                ciudad_destino=random.choice(["Ciudad de México", "Puebla", "Querétaro"]),
                codigo_postal_destino=f"{random.randint(10000, 99999)}",
                estado=estado,
                costo=round(random.uniform(50.0, 500.0), 2),
                tipo_pago=random.choice(["efectivo", "tarjeta", "transferencia"]),
                fecha_creacion=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                fecha_recoleccion=datetime.utcnow() - timedelta(days=random.randint(0, 20)) if estado != "pendiente" else None,
                fecha_entrega_estimada=datetime.utcnow() + timedelta(days=random.randint(1, 7)),
                fecha_entrega_real=datetime.utcnow() - timedelta(days=random.randint(0, 5)) if estado == "entregado" else None,
                notas=f"Envío de prueba número {i+1}"
            )
            db.add(envio)
        
        db.commit()
        print("✅ Envíos creados")
        
        print("\n" + "="*50)
        print("✨ Datos de prueba creados exitosamente!")
        print("="*50)
        print("\n📋 Credenciales de acceso:")
        print("\n👑 Administrador:")
        print("   Usuario: admin")
        print("   Password: admin123")
        print("\n🚚 Repartidor:")
        print("   Usuario: carlos_rep")
        print("   Password: rep123")
        print("\n📦 Cliente:")
        print("   Usuario: juan_cliente")
        print("   Password: cliente123")
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_data()
