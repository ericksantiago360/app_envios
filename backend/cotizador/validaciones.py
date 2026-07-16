"""
cotizador/validaciones.py
=========================
Reglas de negocio y validaciones para el sistema de cotizaciones.
Cada función de validación devuelve (es_valido: bool, mensaje: str).
"""
from cotizador.modelos import SolicitudCotizacion, TipoVehiculo
from cotizador.tarifas import get_restricciones


# ─────────────────────────────────────────────
# Validaciones individuales
# ─────────────────────────────────────────────

def validar_distancia(solicitud: SolicitudCotizacion) -> tuple[bool, str]:
    """La distancia debe ser positiva y menor a 100 km para este corredor."""
    if solicitud.distancia_km <= 0:
        return False, "La distancia debe ser mayor a 0 km."
    if solicitud.distancia_km > 100:
        return False, f"La distancia máxima para envíos en el corredor es 100 km. Recibida: {solicitud.distancia_km:.1f} km."
    return True, ""


def validar_peso(solicitud: SolicitudCotizacion) -> tuple[bool, str]:
    """El peso no debe exceder el límite del vehículo seleccionado."""
    if solicitud.peso_kg is None:
        return True, ""  # Peso opcional, no validar si no se especifica
    restricciones = get_restricciones(solicitud.vehiculo)
    peso_max = restricciones["peso_max_kg"]
    if solicitud.peso_kg <= 0:
        return False, "El peso debe ser mayor a 0 kg."
    if solicitud.peso_kg > peso_max:
        return False, (
            f"El peso {solicitud.peso_kg:.1f} kg excede el límite "
            f"de {peso_max:.0f} kg para {solicitud.vehiculo.value}. "
            f"Considera usar un vehículo de mayor capacidad."
        )
    return True, ""


def validar_dimensiones(solicitud: SolicitudCotizacion) -> tuple[bool, str]:
    """Las dimensiones no deben exceder los límites del vehículo."""
    if not any([solicitud.alto_cm, solicitud.ancho_cm, solicitud.largo_cm]):
        return True, ""  # Si no se especifican dimensiones, no validar
    restricciones = get_restricciones(solicitud.vehiculo)
    errores = []
    if solicitud.alto_cm and solicitud.alto_cm > restricciones["alto_max_cm"]:
        errores.append(f"Alto {solicitud.alto_cm}cm > máximo {restricciones['alto_max_cm']}cm")
    if solicitud.ancho_cm and solicitud.ancho_cm > restricciones["ancho_max_cm"]:
        errores.append(f"Ancho {solicitud.ancho_cm}cm > máximo {restricciones['ancho_max_cm']}cm")
    if solicitud.largo_cm and solicitud.largo_cm > restricciones["largo_max_cm"]:
        errores.append(f"Largo {solicitud.largo_cm}cm > máximo {restricciones['largo_max_cm']}cm")
    if errores:
        return False, f"Dimensiones exceden el límite para {solicitud.vehiculo.value}: {'; '.join(errores)}."
    return True, ""


def validar_espera(solicitud: SolicitudCotizacion) -> tuple[bool, str]:
    """La espera no puede ser negativa ni exceder 4 horas."""
    if solicitud.espera_minutos < 0:
        return False, "El tiempo de espera no puede ser negativo."
    if solicitud.espera_minutos > 240:
        return False, "El tiempo máximo de espera es 240 minutos (4 horas)."
    return True, ""


def validar_zona_misma(solicitud: SolicitudCotizacion) -> tuple[bool, str]:
    """Información cuando origen = destino de zona. No genera advertencia — es comportamiento normal."""
    return True, ""


# ─────────────────────────────────────────────
# Advertencias (no bloquean, pero se notifican)
# ─────────────────────────────────────────────

def advertencia_peso_cercano_limite(solicitud: SolicitudCotizacion) -> str | None:
    """Advierte si el peso está en el 90% del límite del vehículo."""
    if solicitud.peso_kg is None:
        return None
    restricciones = get_restricciones(solicitud.vehiculo)
    umbral = restricciones["peso_max_kg"] * 0.90
    if solicitud.peso_kg >= umbral:
        return (
            f"El peso ({solicitud.peso_kg:.1f} kg) está cerca del límite "
            f"({restricciones['peso_max_kg']:.0f} kg). Verifica con el repartidor."
        )
    return None


def advertencia_distancia_larga(solicitud: SolicitudCotizacion) -> str | None:
    """Advierte para envíos mayores a 40 km — puede tomar más tiempo."""
    if solicitud.distancia_km > 40:
        return (
            f"Trayecto largo ({solicitud.distancia_km:.1f} km). "
            "El tiempo estimado puede variar por tráfico en el corredor."
        )
    return None


def advertencia_vehiculo_sugerido(solicitud: SolicitudCotizacion) -> str | None:
    """
    Sugiere un vehículo más económico si el paquete cabe en uno menor.
    Por ejemplo: solicitan SUV para 5kg — la moto alcanza.
    """
    if solicitud.peso_kg is None:
        return None

    ORDEN = [
        TipoVehiculo.MOTO,
        TipoVehiculo.AUTO,
        TipoVehiculo.SUV,
        TipoVehiculo.PICKUP,
        TipoVehiculo.CAMIONETA,
    ]
    idx_actual = ORDEN.index(solicitud.vehiculo)

    # Buscar el vehículo más pequeño que aguante el peso
    for v in ORDEN:
        restricciones = get_restricciones(v)
        if solicitud.peso_kg <= restricciones["peso_max_kg"]:
            idx_sugerido = ORDEN.index(v)
            if idx_sugerido < idx_actual:
                return (
                    f"El paquete ({solicitud.peso_kg:.1f} kg) cabe en un "
                    f"{v.value}. Podrías ahorrar usando un vehículo más pequeño."
                )
            break
    return None


# ─────────────────────────────────────────────
# Validador principal
# ─────────────────────────────────────────────

def validar_solicitud(solicitud: SolicitudCotizacion) -> tuple[list[str], list[str]]:
    """
    Ejecuta todas las validaciones y advertencias sobre una solicitud.

    Devuelve:
        errores:      lista de mensajes que impiden calcular la cotización
        advertencias: lista de avisos informativos (no bloquean)
    """
    errores: list[str] = []
    advertencias: list[str] = []

    # Validaciones bloqueantes
    validaciones = [
        validar_distancia,
        validar_peso,
        validar_dimensiones,
        validar_espera,
    ]
    for validar in validaciones:
        ok, mensaje = validar(solicitud)
        if not ok:
            errores.append(mensaje)

    # Advertencias informativas (solo si no hay errores críticos)
    if not errores:
        checks_adv = [
            advertencia_peso_cercano_limite,
            advertencia_distancia_larga,
            advertencia_vehiculo_sugerido,
        ]
        for check in checks_adv:
            msg = check(solicitud)
            if msg:
                advertencias.append(msg)

        _, msg_zona = validar_zona_misma(solicitud)
        if msg_zona:
            advertencias.append(msg_zona)

    return errores, advertencias
