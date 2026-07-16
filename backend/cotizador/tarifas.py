"""
cotizador/tarifas.py
====================
Tablas de tarifas de EnvíosApp.
Centralizar aquí todos los precios facilita actualizarlos
sin tocar la lógica de cálculo.

Estructura:
  TARIFAS_VEHICULO  → base, km_extra y espera por vehículo y zona
  SOBRECARGOS       → cargo fijo por tipo de servicio
  CARGOS_ZONA       → cargo adicional por cruce intermunicipal
  COMISIONES        → tasa y membresía mensual por plan de repartidor
  RESTRICCIONES     → límites de peso y dimensiones por vehículo
"""
from cotizador.modelos import TipoVehiculo, Zona, TipoServicio, PlanRepartidor


# ─────────────────────────────────────────────
# Tarifas por vehículo y zona
# ─────────────────────────────────────────────
# Estructura por clave de vehículo:
#   base     → tarifa base que cubre los primeros KM_BASE_INCLUIDOS km
#   km_extra → precio por cada km que exceda KM_BASE_INCLUIDOS
#   espera   → precio por cada 10 minutos de espera

KM_BASE_INCLUIDOS = 5  # Los primeros 5 km van incluidos en la tarifa base

TARIFAS_VEHICULO: dict[TipoVehiculo, dict[Zona, dict]] = {
    TipoVehiculo.MOTO: {
        Zona.A: {"base": 45.0,  "km_extra": 5.0,  "espera": 15.0},
        Zona.B: {"base": 55.0,  "km_extra": 6.0,  "espera": 15.0},
        Zona.C: {"base": 50.0,  "km_extra": 6.0,  "espera": 15.0},
    },
    TipoVehiculo.AUTO: {
        Zona.A: {"base": 75.0,  "km_extra": 7.0,  "espera": 20.0},
        Zona.B: {"base": 90.0,  "km_extra": 8.0,  "espera": 20.0},
        Zona.C: {"base": 85.0,  "km_extra": 8.0,  "espera": 20.0},
    },
    TipoVehiculo.SUV: {
        Zona.A: {"base": 110.0, "km_extra": 10.0, "espera": 25.0},
        Zona.B: {"base": 130.0, "km_extra": 12.0, "espera": 25.0},
        Zona.C: {"base": 120.0, "km_extra": 11.0, "espera": 25.0},
    },
    TipoVehiculo.PICKUP: {
        Zona.A: {"base": 150.0, "km_extra": 12.0, "espera": 30.0},
        Zona.B: {"base": 175.0, "km_extra": 14.0, "espera": 30.0},
        Zona.C: {"base": 160.0, "km_extra": 13.0, "espera": 30.0},
    },
    TipoVehiculo.CAMIONETA: {
        Zona.A: {"base": 200.0, "km_extra": 15.0, "espera": 40.0},
        Zona.B: {"base": 235.0, "km_extra": 18.0, "espera": 40.0},
        Zona.C: {"base": 215.0, "km_extra": 16.0, "espera": 40.0},
    },
}


# ─────────────────────────────────────────────
# Sobrecargos por tipo de servicio
# ─────────────────────────────────────────────
# cargo_fijo   → monto adicional en pesos MXN
# descripcion  → texto para mostrar al cliente

SOBRECARGOS: dict[TipoServicio, dict] = {
    TipoServicio.ESTANDAR: {
        "cargo_fijo":  0.0,
        "descripcion": "Entrega en horario normal (mismo día)",
    },
    TipoServicio.EXPRESS: {
        "cargo_fijo":  30.0,
        "descripcion": "Entrega en menos de 45 minutos",
    },
    TipoServicio.PROGRAMADO: {
        "cargo_fijo":  20.0,
        "descripcion": "Entrega en hora exacta acordada",
    },
    TipoServicio.FRAGIL: {
        "cargo_fijo":  25.0,
        "descripcion": "Manejo especial para objetos frágiles",
    },
}


# ─────────────────────────────────────────────
# Cargos por cruce de zona (intermunicipal)
# ─────────────────────────────────────────────
# Solo aplica cuando zona_origen != zona_destino.
# La tarifa depende del tamaño del vehículo.

CARGOS_ZONA: dict[TipoVehiculo, float] = {
    TipoVehiculo.MOTO:      25.0,
    TipoVehiculo.AUTO:      35.0,
    TipoVehiculo.SUV:       35.0,
    TipoVehiculo.PICKUP:    50.0,
    TipoVehiculo.CAMIONETA: 50.0,
}


# ─────────────────────────────────────────────
# Comisiones y membresías por plan de repartidor
# ─────────────────────────────────────────────

PLANES_REPARTIDOR: dict[PlanRepartidor, dict] = {
    PlanRepartidor.LIBRE: {
        "membresia_mensual": 0.0,
        "tasa_comision":     0.22,   # 22%
        "descripcion":       "Sin membresía — ideal para empezar",
        "punto_equilibrio":  0,
    },
    PlanRepartidor.ESTANDAR: {
        "membresia_mensual": 299.0,
        "tasa_comision":     0.12,   # 12%
        "descripcion":       "Para 3–5 entregas diarias",
        "punto_equilibrio":  64,     # entregas/mes en tarifa base moto $45
    },
    PlanRepartidor.PRO: {
        "membresia_mensual": 549.0,
        "tasa_comision":     0.06,   # 6%
        "descripcion":       "Para repartidores de tiempo completo (6+ entregas/día)",
        "punto_equilibrio":  79,
    },
}


# ─────────────────────────────────────────────
# Restricciones por vehículo
# ─────────────────────────────────────────────

RESTRICCIONES: dict[TipoVehiculo, dict] = {
    TipoVehiculo.MOTO: {
        "peso_max_kg":  20.0,
        "alto_max_cm":  35.0,
        "ancho_max_cm": 40.0,
        "largo_max_cm": 40.0,
        "descripcion":  "Documentos, paquetes pequeños, alimentos",
    },
    TipoVehiculo.AUTO: {
        "peso_max_kg":  100.0,
        "alto_max_cm":  60.0,
        "ancho_max_cm": 80.0,
        "largo_max_cm": 90.0,
        "descripcion":  "Paquetes medianos, electrónicos",
    },
    TipoVehiculo.SUV: {
        "peso_max_kg":  300.0,
        "alto_max_cm":  80.0,
        "ancho_max_cm": 130.0,
        "largo_max_cm": 160.0,
        "descripcion":  "Múltiples paquetes, muebles pequeños",
    },
    TipoVehiculo.PICKUP: {
        "peso_max_kg":  700.0,
        "alto_max_cm":  51.0,
        "ancho_max_cm": 134.0,
        "largo_max_cm": 168.0,
        "descripcion":  "Carga pesada, ferretería, materiales",
    },
    TipoVehiculo.CAMIONETA: {
        "peso_max_kg":  1500.0,
        "alto_max_cm":  170.0,
        "ancho_max_cm": 200.0,
        "largo_max_cm": 200.0,
        "descripcion":  "Mudanzas, carga grande y voluminosa",
    },
}


# ─────────────────────────────────────────────
# Helpers para acceder a las tarifas
# ─────────────────────────────────────────────

def get_tarifa(vehiculo: TipoVehiculo, zona: Zona) -> dict:
    """Devuelve la tarifa base, km_extra y espera para un vehículo y zona."""
    return TARIFAS_VEHICULO[vehiculo][zona]


def get_sobrecargo(servicio: TipoServicio) -> dict:
    """Devuelve el cargo fijo y descripción de un tipo de servicio."""
    return SOBRECARGOS[servicio]


def get_cargo_zona(vehiculo: TipoVehiculo) -> float:
    """Devuelve el cargo intermunicipal para el vehículo dado."""
    return CARGOS_ZONA[vehiculo]


def get_plan(plan: PlanRepartidor) -> dict:
    """Devuelve la configuración de comisión y membresía de un plan."""
    return PLANES_REPARTIDOR[plan]


def get_restricciones(vehiculo: TipoVehiculo) -> dict:
    """Devuelve los límites de peso y dimensión para un vehículo."""
    return RESTRICCIONES[vehiculo]


def listar_vehiculos_disponibles() -> list[dict]:
    """Lista todos los vehículos con sus restricciones (útil para la API)."""
    return [
        {
            "vehiculo":    v.value,
            "descripcion": RESTRICCIONES[v]["descripcion"],
            "peso_max_kg": RESTRICCIONES[v]["peso_max_kg"],
            "tarifa_base_zona_a": TARIFAS_VEHICULO[v][Zona.A]["base"],
        }
        for v in TipoVehiculo
    ]
