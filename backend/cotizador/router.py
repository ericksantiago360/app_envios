"""
cotizador/router.py
===================
Router FastAPI para el sistema de cotizaciones.
Se integra al main.py existente con: app.include_router(cotizador_router)

Endpoints:
    POST /api/cotizacion          → Calcular cotización (público)
    POST /api/cotizacion/comparar → Comparar 3 planes (autenticado)
    GET  /api/cotizacion/vehiculos → Listar vehículos disponibles (público)
    GET  /api/cotizacion/tarifas  → Ver tabla de tarifas completa (público)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from cotizador.modelos import SolicitudCotizacion
from cotizador.calculadora import calcular_cotizacion, comparar_planes
from cotizador.schemas import (
    SolicitudCotizacionSchema,
    CotizacionResponseSchema,
    ComparacionPlanesSchema,
    resultado_a_response,
)
from cotizador.tarifas import listar_vehiculos_disponibles, TARIFAS_VEHICULO, PLANES_REPARTIDOR, SOBRECARGOS

cotizador_router = APIRouter(
    prefix="/api/cotizacion",
    tags=["Cotizaciones"],
)


# ─────────────────────────────────────────────
# Endpoint principal: calcular cotización
# ─────────────────────────────────────────────

@cotizador_router.post(
    "/",
    response_model=CotizacionResponseSchema,
    summary="Calcular cotización de envío",
    description=(
        "Calcula el precio de un envío basado en vehículo, zonas, distancia "
        "y tipo de servicio. Este endpoint es público — no requiere autenticación. "
        "Disponible en la landing page para que cualquier cliente cotice su envío."
    ),
)
def cotizar(solicitud_schema: SolicitudCotizacionSchema):
    """
    Calcula la cotización completa de un envío.

    - Si la solicitud tiene errores de validación, devuelve estado='invalida' con los mensajes.
    - Si es válida, devuelve el desglose completo, distribución de ingresos y tiempo estimado.
    """
    # Convertir schema Pydantic a dataclass del dominio
    solicitud = SolicitudCotizacion(
        vehiculo        = solicitud_schema.vehiculo,
        zona_origen     = solicitud_schema.zona_origen,
        zona_destino    = solicitud_schema.zona_destino,
        distancia_km    = solicitud_schema.distancia_km,
        tipo_servicio   = solicitud_schema.tipo_servicio,
        plan_repartidor = solicitud_schema.plan_repartidor,
        espera_minutos  = solicitud_schema.espera_minutos,
        peso_kg         = solicitud_schema.peso_kg,
        alto_cm         = solicitud_schema.alto_cm,
        ancho_cm        = solicitud_schema.ancho_cm,
        largo_cm        = solicitud_schema.largo_cm,
        notas           = solicitud_schema.notas,
    )

    resultado = calcular_cotizacion(solicitud)
    return resultado_a_response(resultado)


# ─────────────────────────────────────────────
# Endpoint: comparar planes
# ─────────────────────────────────────────────

@cotizador_router.post(
    "/comparar",
    response_model=ComparacionPlanesSchema,
    summary="Comparar cotización en los 3 planes de repartidor",
    description="Muestra cuánto ganaría el repartidor y cuánto retendría la plataforma según cada plan.",
)
def cotizar_comparar(
    solicitud_schema: SolicitudCotizacionSchema,
    current_user=Depends(get_current_active_user),
):
    """
    Recibe los mismos parámetros que /api/cotizacion pero devuelve
    la cotización calculada para los 3 planes (Libre, Estándar, Pro).
    """
    solicitud = SolicitudCotizacion(
        vehiculo        = solicitud_schema.vehiculo,
        zona_origen     = solicitud_schema.zona_origen,
        zona_destino    = solicitud_schema.zona_destino,
        distancia_km    = solicitud_schema.distancia_km,
        tipo_servicio   = solicitud_schema.tipo_servicio,
        plan_repartidor = solicitud_schema.plan_repartidor,
        espera_minutos  = solicitud_schema.espera_minutos,
        peso_kg         = solicitud_schema.peso_kg,
        alto_cm         = solicitud_schema.alto_cm,
        ancho_cm        = solicitud_schema.ancho_cm,
        largo_cm        = solicitud_schema.largo_cm,
        notas           = solicitud_schema.notas,
    )

    # Validar primero
    resultado_base = calcular_cotizacion(solicitud)
    if not resultado_base.es_valida:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resultado_base.errores,
        )

    planes = comparar_planes(solicitud)
    precio_base = resultado_base.distribucion.total_cliente

    # Recomendación automática: el plan con mayor neto para el repartidor
    mejor = max(planes, key=lambda p: p["neto_repartidor"])
    recomendacion = (
        f"Con {solicitud.distancia_km:.0f} km a ${precio_base:.0f} por entrega, "
        f"el {mejor['plan'].upper()} maximiza tu ingreso neto "
        f"(${mejor['neto_repartidor']:.0f} por entrega)."
    )

    return ComparacionPlanesSchema(
        planes         = planes,
        recomendacion  = recomendacion,
        precio_base    = precio_base,
    )


# ─────────────────────────────────────────────
# Endpoints informativos (GET)
# ─────────────────────────────────────────────

@cotizador_router.get(
    "/vehiculos",
    summary="Listar vehículos disponibles con restricciones",
)
def listar_vehiculos():
    """Devuelve todos los vehículos disponibles con sus límites de peso y tarifa base."""
    return {"vehiculos": listar_vehiculos_disponibles()}


@cotizador_router.get(
    "/tarifas",
    summary="Ver tabla completa de tarifas",
)
def ver_tarifas():
    """Devuelve la tabla de tarifas completa por vehículo, zona, servicio y plan."""
    tarifas_json = {}
    for vehiculo, zonas in TARIFAS_VEHICULO.items():
        tarifas_json[vehiculo.value] = {
            zona.value: datos
            for zona, datos in zonas.items()
        }

    servicios_json = {}
    from cotizador.tarifas import SOBRECARGOS
    for svc, datos in SOBRECARGOS.items():
        servicios_json[svc.value] = datos

    planes_json = {}
    for plan, datos in PLANES_REPARTIDOR.items():
        planes_json[plan.value] = datos

    return {
        "km_base_incluidos": 5,
        "vehiculos":         tarifas_json,
        "servicios":         servicios_json,
        "planes_repartidor": planes_json,
    }
