"""
cotizador/calculadora.py
========================
Núcleo del sistema de cotizaciones de EnvíosApp.

Función principal:
    calcular_cotizacion(solicitud) → ResultadoCotizacion

Es una función pura — sin efectos secundarios, sin BD, sin HTTP.
Recibe una SolicitudCotizacion, devuelve un ResultadoCotizacion completo.
Fácil de testear y reusar desde la API, el CLI o cualquier contexto.

Fórmula:
    precio = tarifa_base(vehiculo, zona_origen)
    precio += max(0, distancia_km - KM_BASE) × km_extra
    precio += floor(espera_min / 10) × espera_rate
    precio += sobrecargo_servicio
    precio += cruce_zona (si zona_origen ≠ zona_destino)
    comision = precio × tasa_comision(plan)
    neto_repartidor = precio - comision
"""
import math
from cotizador.modelos import (
    SolicitudCotizacion,
    ResultadoCotizacion,
    DesgloseCotizacion,
    DistribucionIngresos,
    EstadoCotizacion,
)
from cotizador.tarifas import (
    get_tarifa,
    get_sobrecargo,
    get_cargo_zona,
    get_plan,
    KM_BASE_INCLUIDOS,
)
from cotizador.validaciones import validar_solicitud


# ─────────────────────────────────────────────
# Cálculos individuales (funciones privadas)
# ─────────────────────────────────────────────

def _calcular_tarifa_base(solicitud: SolicitudCotizacion) -> float:
    """Tarifa fija según vehículo y zona de origen."""
    tarifa = get_tarifa(solicitud.vehiculo, solicitud.zona_origen)
    return tarifa["base"]


def _calcular_cargo_km(solicitud: SolicitudCotizacion) -> float:
    """
    Cargo por kilómetros adicionales.
    Los primeros KM_BASE_INCLUIDOS km van en la tarifa base.
    """
    tarifa = get_tarifa(solicitud.vehiculo, solicitud.zona_origen)
    km_extra = max(0.0, solicitud.distancia_km - KM_BASE_INCLUIDOS)
    return round(km_extra * tarifa["km_extra"], 2)


def _calcular_cargo_espera(solicitud: SolicitudCotizacion) -> float:
    """
    Cargo por tiempo de espera.
    Se cobra en bloques de 10 minutos.
    """
    tarifa = get_tarifa(solicitud.vehiculo, solicitud.zona_origen)
    bloques = math.floor(solicitud.espera_minutos / 10)
    return round(bloques * tarifa["espera"], 2)


def _calcular_cargo_servicio(solicitud: SolicitudCotizacion) -> float:
    """Sobrecargo fijo por tipo de servicio (Express, Programado, Frágil)."""
    sobrecargo = get_sobrecargo(solicitud.tipo_servicio)
    return sobrecargo["cargo_fijo"]


def _calcular_cargo_zona(solicitud: SolicitudCotizacion) -> float:
    """Cargo adicional cuando el envío cruza de un municipio a otro."""
    if solicitud.zona_origen == solicitud.zona_destino:
        return 0.0
    return get_cargo_zona(solicitud.vehiculo)


def _calcular_tiempo_estimado(solicitud: SolicitudCotizacion) -> int:
    """
    Tiempo estimado en minutos para la entrega.
    Fórmula simple: (distancia × 3 min/km) + espera + buffer por servicio.
    """
    tiempo_ruta = solicitud.distancia_km * 3
    buffer = {
        "express":    -10,   # Repartidor prioriza la entrega
        "programado": 10,    # Tiene un horario específico
        "fragil":     15,    # Manejo más cuidadoso
        "estandar":   5,
    }
    b = buffer.get(solicitud.tipo_servicio.value, 5)
    return max(15, round(tiempo_ruta + solicitud.espera_minutos + b))


# ─────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────

def calcular_cotizacion(solicitud: SolicitudCotizacion) -> ResultadoCotizacion:
    """
    Calcula la cotización completa para un envío.

    Pasos:
    1. Validar la solicitud (errores bloquean el cálculo)
    2. Calcular cada componente del precio
    3. Calcular distribución de ingresos
    4. Armar y devolver ResultadoCotizacion

    Args:
        solicitud: SolicitudCotizacion con todos los parámetros del envío

    Returns:
        ResultadoCotizacion con desglose completo, estado y advertencias
    """
    resultado = ResultadoCotizacion(solicitud=solicitud)

    # ── Paso 1: Validar ──────────────────────
    errores, advertencias = validar_solicitud(solicitud)
    resultado.advertencias = advertencias

    if errores:
        resultado.errores = errores
        resultado.estado  = EstadoCotizacion.INVALIDA
        return resultado  # Retornar sin calcular precio

    # ── Paso 2: Calcular desglose ─────────────
    desglose = DesgloseCotizacion(
        tarifa_base    = _calcular_tarifa_base(solicitud),
        cargo_km       = _calcular_cargo_km(solicitud),
        cargo_espera   = _calcular_cargo_espera(solicitud),
        cargo_servicio = _calcular_cargo_servicio(solicitud),
        cargo_zona     = _calcular_cargo_zona(solicitud),
    )
    resultado.desglose = desglose

    # ── Paso 3: Distribución de ingresos ──────
    plan_config    = get_plan(solicitud.plan_repartidor)
    tasa_comision  = plan_config["tasa_comision"]
    total_cliente  = round(desglose.subtotal, 2)
    comision       = round(total_cliente * tasa_comision, 2)
    neto_repartidor = round(total_cliente - comision, 2)

    resultado.distribucion = DistribucionIngresos(
        total_cliente        = total_cliente,
        tasa_comision        = tasa_comision,
        comision_plataforma  = comision,
        ingreso_repartidor   = neto_repartidor,
        plan_aplicado        = solicitud.plan_repartidor,
        membresia_mensual    = plan_config["membresia_mensual"],
    )

    # ── Paso 4: Metadatos ─────────────────────
    resultado.es_intermunicipal   = solicitud.zona_origen != solicitud.zona_destino
    resultado.tiempo_estimado_min = _calcular_tiempo_estimado(solicitud)
    resultado.descripcion_ruta    = (
        f"Zona {solicitud.zona_origen.value} → Zona {solicitud.zona_destino.value} "
        f"({solicitud.distancia_km:.1f} km, {solicitud.vehiculo.value})"
    )

    # Estado final
    resultado.estado = (
        EstadoCotizacion.ADVERTENCIA if advertencias
        else EstadoCotizacion.VALIDA
    )

    return resultado


# ─────────────────────────────────────────────
# Función auxiliar: comparar planes
# ─────────────────────────────────────────────

def comparar_planes(solicitud: SolicitudCotizacion) -> list[dict]:
    """
    Calcula la cotización para los 3 planes de repartidor y devuelve
    una comparación. Útil para el dashboard de recomendación de plan.

    Returns:
        Lista de dicts con plan, comisión, neto_repartidor e ingreso_plataforma
    """
    from cotizador.modelos import PlanRepartidor, SolicitudCotizacion as _Sol
    from cotizador.tarifas import get_plan

    # Calcular el subtotal base (sin plan)
    base_solicitud = _Sol(
        vehiculo        = solicitud.vehiculo,
        zona_origen     = solicitud.zona_origen,
        zona_destino    = solicitud.zona_destino,
        distancia_km    = solicitud.distancia_km,
        tipo_servicio   = solicitud.tipo_servicio,
        espera_minutos  = solicitud.espera_minutos,
        peso_kg         = solicitud.peso_kg,
    )

    comparacion = []
    for plan in PlanRepartidor:
        base_solicitud.plan_repartidor = plan
        r = calcular_cotizacion(base_solicitud)
        if r.es_valida:
            plan_cfg = get_plan(plan)
            comparacion.append({
                "plan":               plan.value,
                "membresia_mensual":  plan_cfg["membresia_mensual"],
                "tasa_comision":      plan_cfg["tasa_comision"],
                "total_cliente":      r.distribucion.total_cliente,
                "comision":           r.distribucion.comision_plataforma,
                "neto_repartidor":    r.distribucion.ingreso_repartidor,
            })

    return comparacion
