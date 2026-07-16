"""
cotizador/schemas.py
====================
Schemas Pydantic v2 para validación de entrada y serialización
de salida en la API FastAPI del cotizador.
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from cotizador.modelos import TipoVehiculo, Zona, TipoServicio, PlanRepartidor, EstadoCotizacion


# ─────────────────────────────────────────────
# Schema de entrada
# ─────────────────────────────────────────────

class SolicitudCotizacionSchema(BaseModel):
    """
    Body del request POST /api/cotizacion
    Todos los campos tienen validación automática vía Pydantic.
    """
    vehiculo:        TipoVehiculo    = Field(..., description="Tipo de vehículo")
    zona_origen:     Zona            = Field(..., description="Zona de recogida del paquete")
    zona_destino:    Zona            = Field(..., description="Zona de entrega")
    distancia_km:    float           = Field(..., gt=0, le=100, description="Distancia total en km")
    tipo_servicio:   TipoServicio    = Field(TipoServicio.ESTANDAR, description="Tipo de servicio")
    plan_repartidor: PlanRepartidor  = Field(PlanRepartidor.LIBRE, description="Plan del repartidor")
    espera_minutos:  int             = Field(0, ge=0, le=240, description="Tiempo de espera estimado en minutos")
    peso_kg:         Optional[float] = Field(None, gt=0, description="Peso del paquete en kg")
    alto_cm:         Optional[float] = Field(None, gt=0, description="Alto del paquete en cm")
    ancho_cm:        Optional[float] = Field(None, gt=0, description="Ancho del paquete en cm")
    largo_cm:        Optional[float] = Field(None, gt=0, description="Largo del paquete en cm")
    notas:           Optional[str]   = Field(None, max_length=500, description="Notas adicionales")

    @field_validator("distancia_km")
    @classmethod
    def redondear_distancia(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("peso_kg", "alto_cm", "ancho_cm", "largo_cm", mode="before")
    @classmethod
    def convertir_vacio_a_none(cls, v):
        if v == "" or v == 0:
            return None
        return v

    @model_validator(mode="after")
    def validar_combinacion(self):
        """Validación cruzada: si se especifica una dimensión, pedir todas."""
        dims = [self.alto_cm, self.ancho_cm, self.largo_cm]
        if any(d is not None for d in dims) and not all(d is not None for d in dims):
            raise ValueError(
                "Si especificas dimensiones del paquete, incluye alto, ancho Y largo."
            )
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "vehiculo":        "moto",
                "zona_origen":     "A",
                "zona_destino":    "B",
                "distancia_km":    12.5,
                "tipo_servicio":   "express",
                "plan_repartidor": "estandar",
                "espera_minutos":  10,
                "peso_kg":         8.0,
            }
        }


# ─────────────────────────────────────────────
# Schemas de salida
# ─────────────────────────────────────────────

class DesgloseSchema(BaseModel):
    tarifa_base:    float
    cargo_km:       float
    cargo_espera:   float
    cargo_servicio: float
    cargo_zona:     float
    subtotal:       float


class DistribucionSchema(BaseModel):
    total_cliente:       float
    tasa_comision:       float
    comision_plataforma: float
    ingreso_repartidor:  float
    plan_aplicado:       PlanRepartidor
    membresia_mensual:   float


class CotizacionResponseSchema(BaseModel):
    """
    Respuesta completa del endpoint POST /api/cotizacion
    """
    estado:              EstadoCotizacion
    es_valida:           bool
    desglose:            Optional[DesgloseSchema]    = None
    distribucion:        Optional[DistribucionSchema] = None
    es_intermunicipal:   bool                         = False
    tiempo_estimado_min: Optional[int]               = None
    descripcion_ruta:    Optional[str]               = None
    errores:             list[str]                   = []
    advertencias:        list[str]                   = []

    class Config:
        json_schema_extra = {
            "example": {
                "estado":    "valida",
                "es_valida": True,
                "desglose": {
                    "tarifa_base":    55.0,
                    "cargo_km":       45.0,
                    "cargo_espera":   15.0,
                    "cargo_servicio": 30.0,
                    "cargo_zona":     25.0,
                    "subtotal":       170.0,
                },
                "distribucion": {
                    "total_cliente":       170.0,
                    "tasa_comision":       0.12,
                    "comision_plataforma": 20.40,
                    "ingreso_repartidor":  149.60,
                    "plan_aplicado":       "estandar",
                    "membresia_mensual":   299.0,
                },
                "es_intermunicipal":   True,
                "tiempo_estimado_min": 42,
                "descripcion_ruta":    "Zona A → Zona B (12.5 km, moto)",
                "errores":             [],
                "advertencias":        [],
            }
        }


class ComparacionPlanesSchema(BaseModel):
    """Respuesta para comparar los 3 planes en una misma cotización."""
    planes: list[dict]
    recomendacion: str
    precio_base: float


# ─────────────────────────────────────────────
# Conversores (Dataclass → Schema)
# ─────────────────────────────────────────────

def resultado_a_response(resultado) -> CotizacionResponseSchema:
    """Convierte un ResultadoCotizacion (dataclass) a CotizacionResponseSchema (Pydantic)."""
    desglose = None
    if resultado.desglose and resultado.es_valida:
        desglose = DesgloseSchema(
            tarifa_base    = resultado.desglose.tarifa_base,
            cargo_km       = resultado.desglose.cargo_km,
            cargo_espera   = resultado.desglose.cargo_espera,
            cargo_servicio = resultado.desglose.cargo_servicio,
            cargo_zona     = resultado.desglose.cargo_zona,
            subtotal       = resultado.desglose.subtotal,
        )

    distribucion = None
    if resultado.distribucion and resultado.es_valida:
        distribucion = DistribucionSchema(
            total_cliente        = resultado.distribucion.total_cliente,
            tasa_comision        = resultado.distribucion.tasa_comision,
            comision_plataforma  = resultado.distribucion.comision_plataforma,
            ingreso_repartidor   = resultado.distribucion.ingreso_repartidor,
            plan_aplicado        = resultado.distribucion.plan_aplicado,
            membresia_mensual    = resultado.distribucion.membresia_mensual,
        )

    return CotizacionResponseSchema(
        estado              = resultado.estado,
        es_valida           = resultado.es_valida,
        desglose            = desglose,
        distribucion        = distribucion,
        es_intermunicipal   = resultado.es_intermunicipal,
        tiempo_estimado_min = resultado.tiempo_estimado_min,
        descripcion_ruta    = resultado.descripcion_ruta,
        errores             = resultado.errores,
        advertencias        = resultado.advertencias,
    )
