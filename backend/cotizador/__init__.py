"""
cotizador — Módulo de cotizaciones para EnvíosApp
==================================================
Uso desde código externo:

    from cotizador.modelos import SolicitudCotizacion, TipoVehiculo, Zona
    from cotizador.calculadora import calcular_cotizacion

    solicitud = SolicitudCotizacion(
        vehiculo     = TipoVehiculo.MOTO,
        zona_origen  = Zona.A,
        zona_destino = Zona.B,
        distancia_km = 12.5,
    )
    resultado = calcular_cotizacion(solicitud)
    print(resultado.resumen())

Integración con FastAPI (en main.py):

    from cotizador.router import cotizador_router
    app.include_router(cotizador_router)
"""
from cotizador.calculadora import calcular_cotizacion, comparar_planes
from cotizador.modelos import (
    SolicitudCotizacion,
    ResultadoCotizacion,
    TipoVehiculo,
    Zona,
    TipoServicio,
    PlanRepartidor,
)

__all__ = [
    "calcular_cotizacion",
    "comparar_planes",
    "SolicitudCotizacion",
    "ResultadoCotizacion",
    "TipoVehiculo",
    "Zona",
    "TipoServicio",
    "PlanRepartidor",
]
