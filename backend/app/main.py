from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base
from app.routers import auth, clientes, repartidores, envios, rutas, tracking
import sys, os
# Agregar /app al path para que 'cotizador' sea importable como paquete
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cotizador.router import cotizador_router
from app.models import user, cliente, repartidor, envio, ruta

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión de Envíos",
    description="API para gestión completa de envíos, clientes, repartidores y rutas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,  # La auth va en el header Authorization, no en cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(repartidores.router)
app.include_router(envios.router)
app.include_router(rutas.router)
app.include_router(tracking.router)
app.include_router(cotizador_router)


@app.get("/")
def root():
    return {
        "message": "Bienvenido al Sistema de Gestión de Envíos",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
