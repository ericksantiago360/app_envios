"""
cotizador/modelos.py
====================
Modelos de datos para el sistema de cotizaciones de EnvíosApp.
Usa dataclasses estándar de Python — sin dependencias externas.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────────
# Enumeraciones del dominio
# ─────────────────────────────────────────────

class TipoVehiculo(str, Enum):
    MOTO      = "moto"
    AUTO      = "auto"
    SUV       = "suv"
    PICKUP    = "pickup"
    CAMIONETA = "camioneta"


class Zona(str, Enum):
    """
    A = Teotihuacán + San Martín de las Pirámides
    B = Texcoco + Tecámac
    C = Otumba
    """
    A = "A"
    B = "B"
    C = "C"


class TipoServicio(str, Enum):
    ESTANDAR   = "estandar"
    EXPRESS    = "express"
    PROGRAMADO = "programado"
    FRAGIL     = "fragil"


class PlanRepartidor(str, Enum):
    LIBRE    = "libre"
    ESTANDAR = "estandar"
    PRO      = "pro"


class EstadoCotizacion(str, Enum):
    VALIDA    = "valida"
    INVALIDA  = "invalida"
    ADVERTENCIA = "advertencia"


# ─────────────────────────────────────────────
# Modelos de entrada
# ─────────────────────────────────────────────

@dataclass
class SolicitudCotizacion:
    """
    Datos que el cliente o la app envían para generar una cotización.
    Campos obligatorios primero, opcionales al final con default.
    """
    vehiculo:       TipoVehiculo
    zona_origen:    Zona
    zona_destino:   Zona
    distancia_km:   float
    tipo_servicio:  TipoServicio   = TipoServicio.ESTANDAR
    plan_repartidor: PlanRepartidor = PlanRepartidor.LIBRE

    # Opcionales
    espera_minutos: int            = 0
    peso_kg:        Optional[float] = None
    alto_cm:        Optional[float] = None
    ancho_cm:       Optional[float] = None
    largo_cm:       Optional[float] = None
    notas:          Optional[str]   = None


# ─────────────────────────────────────────────
# Modelos de salida
# ─────────────────────────────────────────────

@dataclass
class DesgloseCotizacion:
    """Desglose línea por línea del cálculo del precio."""
    tarifa_base:      float = 0.0
    cargo_km:         float = 0.0
    cargo_espera:     float = 0.0
    cargo_servicio:   float = 0.0
    cargo_zona:       float = 0.0

    @property
    def subtotal(self) -> float:
        return (
            self.tarifa_base
            + self.cargo_km
            + self.cargo_espera
            + self.cargo_servicio
            + self.cargo_zona
        )


@dataclass
class DistribucionIngresos:
    """Cómo se distribuye el pago entre plataforma y repartidor."""
    total_cliente:        float = 0.0
    tasa_comision:        float = 0.0
    comision_plataforma:  float = 0.0
    ingreso_repartidor:   float = 0.0
    plan_aplicado:        PlanRepartidor = PlanRepartidor.LIBRE
    membresia_mensual:    float = 0.0


@dataclass
class ResultadoCotizacion:
    """
    Respuesta completa del sistema de cotizaciones.
    Contiene todo lo necesario para mostrar al cliente,
    registrar en BD y calcular ingresos del repartidor.
    """
    solicitud:    SolicitudCotizacion  = field(default_factory=SolicitudCotizacion)
    desglose:     DesgloseCotizacion   = field(default_factory=DesgloseCotizacion)
    distribucion: DistribucionIngresos = field(default_factory=DistribucionIngresos)

    estado:       EstadoCotizacion = EstadoCotizacion.VALIDA
    errores:      list[str]        = field(default_factory=list)
    advertencias: list[str]        = field(default_factory=list)

    # Metadatos para el cliente final
    es_intermunicipal:  bool = False
    tiempo_estimado_min: Optional[int] = None
    descripcion_ruta:   Optional[str] = None

    @property
    def es_valida(self) -> bool:
        # ADVERTENCIA significa válida pero con avisos informativos
        return self.estado in (EstadoCotizacion.VALIDA, EstadoCotizacion.ADVERTENCIA)

    @property
    def precio_final(self) -> float:
        return self.distribucion.total_cliente

    def resumen(self) -> str:
        """Representación legible para CLI o logs."""
        lineas = [
            f"{'='*48}",
            f"  COTIZACIÓN EnvíosApp",
            f"{'='*48}",
            f"  Vehículo  : {self.solicitud.vehiculo.value.upper()}",
            f"  Ruta      : Zona {self.solicitud.zona_origen.value} → Zona {self.solicitud.zona_destino.value}",
            f"  Distancia : {self.solicitud.distancia_km:.1f} km",
            f"  Servicio  : {self.solicitud.tipo_servicio.value}",
            f"{'-'*48}",
            f"  Tarifa base     : ${self.desglose.tarifa_base:>8.2f}",
            f"  Km adicionales  : ${self.desglose.cargo_km:>8.2f}",
            f"  Espera          : ${self.desglose.cargo_espera:>8.2f}",
            f"  Tipo servicio   : ${self.desglose.cargo_servicio:>8.2f}",
            f"  Cruce zona      : ${self.desglose.cargo_zona:>8.2f}",
            f"{'-'*48}",
            f"  TOTAL CLIENTE   : ${self.distribucion.total_cliente:>8.2f}",
            f"  Comisión ({self.distribucion.tasa_comision*100:.0f}%): ${self.distribucion.comision_plataforma:>8.2f}",
            f"  Neto repartidor : ${self.distribucion.ingreso_repartidor:>8.2f}",
            f"{'='*48}",
        ]
        if self.advertencias:
            for a in self.advertencias:
                lineas.append(f"  ⚠  {a}")
        if self.errores:
            for e in self.errores:
                lineas.append(f"  ✗  {e}")
        return "\n".join(lineas)
