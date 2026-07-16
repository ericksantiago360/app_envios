"""
test_cotizador.py
=================
Tests unitarios del sistema de cotizaciones.
Ejecutar: python -m pytest test_cotizador.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from modelos import (
    SolicitudCotizacion, TipoVehiculo, Zona,
    TipoServicio, PlanRepartidor, EstadoCotizacion,
)
from calculadora import calcular_cotizacion, comparar_planes
from tarifas import KM_BASE_INCLUIDOS


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def solicitud_basica():
    """Solicitud mínima válida: moto, zona A→A, 5 km, estándar."""
    return SolicitudCotizacion(
        vehiculo        = TipoVehiculo.MOTO,
        zona_origen     = Zona.A,
        zona_destino    = Zona.A,
        distancia_km    = 5.0,
        tipo_servicio   = TipoServicio.ESTANDAR,
        plan_repartidor = PlanRepartidor.LIBRE,
    )


@pytest.fixture
def solicitud_intermunicipal():
    """Moto de Zona A a Zona B, 15 km, express."""
    return SolicitudCotizacion(
        vehiculo        = TipoVehiculo.MOTO,
        zona_origen     = Zona.A,
        zona_destino    = Zona.B,
        distancia_km    = 15.0,
        tipo_servicio   = TipoServicio.EXPRESS,
        plan_repartidor = PlanRepartidor.ESTANDAR,
        espera_minutos  = 10,
    )


# ─────────────────────────────────────────────
# Tests: cálculo básico
# ─────────────────────────────────────────────

class TestCalculoBasico:

    def test_cotizacion_valida(self, solicitud_basica):
        r = calcular_cotizacion(solicitud_basica)
        assert r.es_valida
        assert r.estado == EstadoCotizacion.VALIDA

    def test_tarifa_base_moto_zona_a(self, solicitud_basica):
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.tarifa_base == 45.0

    def test_sin_cargo_km_en_distancia_base(self, solicitud_basica):
        """5 km = exactamente el límite, sin cargo extra."""
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_km == 0.0

    def test_cargo_km_extra(self, solicitud_basica):
        """10 km = 5 km extra a $5/km = $25."""
        solicitud_basica.distancia_km = 10.0
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_km == 25.0

    def test_cargo_espera_por_bloques(self):
        """30 minutos = 3 bloques × $15 = $45."""
        solicitud = SolicitudCotizacion(
            vehiculo       = TipoVehiculo.MOTO,
            zona_origen    = Zona.A,
            zona_destino   = Zona.A,
            distancia_km   = 5.0,
            espera_minutos = 30,
        )
        r = calcular_cotizacion(solicitud)
        assert r.desglose.cargo_espera == 45.0

    def test_espera_menor_a_10_min_sin_cargo(self):
        """9 minutos no completan un bloque — sin cargo."""
        solicitud = SolicitudCotizacion(
            vehiculo       = TipoVehiculo.MOTO,
            zona_origen    = Zona.A,
            zona_destino   = Zona.A,
            distancia_km   = 5.0,
            espera_minutos = 9,
        )
        r = calcular_cotizacion(solicitud)
        assert r.desglose.cargo_espera == 0.0


# ─────────────────────────────────────────────
# Tests: servicios
# ─────────────────────────────────────────────

class TestTipoServicio:

    def test_estandar_sin_cargo(self, solicitud_basica):
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_servicio == 0.0

    def test_express_cargo_30(self, solicitud_basica):
        solicitud_basica.tipo_servicio = TipoServicio.EXPRESS
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_servicio == 30.0

    def test_programado_cargo_20(self, solicitud_basica):
        solicitud_basica.tipo_servicio = TipoServicio.PROGRAMADO
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_servicio == 20.0

    def test_fragil_cargo_25(self, solicitud_basica):
        solicitud_basica.tipo_servicio = TipoServicio.FRAGIL
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_servicio == 25.0


# ─────────────────────────────────────────────
# Tests: zonas
# ─────────────────────────────────────────────

class TestZonas:

    def test_misma_zona_sin_cargo_intermunicipal(self, solicitud_basica):
        r = calcular_cotizacion(solicitud_basica)
        assert r.desglose.cargo_zona == 0.0
        assert not r.es_intermunicipal

    def test_zona_a_a_b_cargo_25_moto(self):
        solicitud = SolicitudCotizacion(
            vehiculo     = TipoVehiculo.MOTO,
            zona_origen  = Zona.A,
            zona_destino = Zona.B,
            distancia_km = 8.0,
        )
        r = calcular_cotizacion(solicitud)
        assert r.desglose.cargo_zona == 25.0
        assert r.es_intermunicipal

    def test_zona_a_a_b_cargo_35_auto(self):
        solicitud = SolicitudCotizacion(
            vehiculo     = TipoVehiculo.AUTO,
            zona_origen  = Zona.A,
            zona_destino = Zona.B,
            distancia_km = 8.0,
        )
        r = calcular_cotizacion(solicitud)
        assert r.desglose.cargo_zona == 35.0

    def test_tarifa_base_zona_b_es_mayor_que_zona_a(self):
        sol_a = SolicitudCotizacion(TipoVehiculo.MOTO, Zona.A, Zona.A, 5.0)
        sol_b = SolicitudCotizacion(TipoVehiculo.MOTO, Zona.B, Zona.B, 5.0)
        r_a = calcular_cotizacion(sol_a)
        r_b = calcular_cotizacion(sol_b)
        assert r_b.desglose.tarifa_base > r_a.desglose.tarifa_base


# ─────────────────────────────────────────────
# Tests: planes y comisiones
# ─────────────────────────────────────────────

class TestPlanesComisiones:

    def test_plan_libre_22_porciento(self, solicitud_basica):
        solicitud_basica.plan_repartidor = PlanRepartidor.LIBRE
        r = calcular_cotizacion(solicitud_basica)
        assert r.distribucion.tasa_comision == 0.22
        assert abs(r.distribucion.comision_plataforma - r.distribucion.total_cliente * 0.22) < 0.01

    def test_plan_estandar_12_porciento(self, solicitud_basica):
        solicitud_basica.plan_repartidor = PlanRepartidor.ESTANDAR
        r = calcular_cotizacion(solicitud_basica)
        assert r.distribucion.tasa_comision == 0.12

    def test_plan_pro_6_porciento(self, solicitud_basica):
        solicitud_basica.plan_repartidor = PlanRepartidor.PRO
        r = calcular_cotizacion(solicitud_basica)
        assert r.distribucion.tasa_comision == 0.06

    def test_comision_mas_neto_igual_a_total(self, solicitud_basica):
        """La suma de comisión + neto repartidor debe ser igual al total cliente."""
        r = calcular_cotizacion(solicitud_basica)
        total = r.distribucion.comision_plataforma + r.distribucion.ingreso_repartidor
        assert abs(total - r.distribucion.total_cliente) < 0.01

    def test_plan_pro_menor_comision_que_libre(self, solicitud_basica):
        sol_libre = SolicitudCotizacion(
            vehiculo=TipoVehiculo.MOTO, zona_origen=Zona.A, zona_destino=Zona.A,
            distancia_km=5.0, plan_repartidor=PlanRepartidor.LIBRE
        )
        sol_pro = SolicitudCotizacion(
            vehiculo=TipoVehiculo.MOTO, zona_origen=Zona.A, zona_destino=Zona.A,
            distancia_km=5.0, plan_repartidor=PlanRepartidor.PRO
        )
        r_libre = calcular_cotizacion(sol_libre)
        r_pro = calcular_cotizacion(sol_pro)
        assert r_pro.distribucion.comision_plataforma < r_libre.distribucion.comision_plataforma


# ─────────────────────────────────────────────
# Tests: validaciones
# ─────────────────────────────────────────────

class TestValidaciones:

    def test_distancia_cero_invalida(self, solicitud_basica):
        solicitud_basica.distancia_km = 0
        r = calcular_cotizacion(solicitud_basica)
        assert not r.es_valida
        assert len(r.errores) > 0

    def test_distancia_negativa_invalida(self, solicitud_basica):
        solicitud_basica.distancia_km = -5
        r = calcular_cotizacion(solicitud_basica)
        assert not r.es_valida

    def test_distancia_mayor_100_invalida(self, solicitud_basica):
        solicitud_basica.distancia_km = 101
        r = calcular_cotizacion(solicitud_basica)
        assert not r.es_valida

    def test_peso_excede_limite_moto_invalido(self, solicitud_basica):
        solicitud_basica.peso_kg = 25.0  # Moto max 20 kg
        r = calcular_cotizacion(solicitud_basica)
        assert not r.es_valida
        assert any("peso" in e.lower() for e in r.errores)

    def test_peso_dentro_limite_valido(self, solicitud_basica):
        solicitud_basica.peso_kg = 15.0
        r = calcular_cotizacion(solicitud_basica)
        assert r.es_valida

    def test_espera_negativa_invalida(self, solicitud_basica):
        solicitud_basica.espera_minutos = -10
        r = calcular_cotizacion(solicitud_basica)
        assert not r.es_valida

    def test_advertencia_peso_cercano_limite(self, solicitud_basica):
        solicitud_basica.peso_kg = 19.0  # 95% del límite de 20kg
        r = calcular_cotizacion(solicitud_basica)
        assert r.es_valida
        assert len(r.advertencias) > 0


# ─────────────────────────────────────────────
# Tests: comparar planes
# ─────────────────────────────────────────────

class TestCompararPlanes:

    def test_comparar_devuelve_3_planes(self, solicitud_basica):
        planes = comparar_planes(solicitud_basica)
        assert len(planes) == 3

    def test_plan_libre_mayor_comision(self, solicitud_basica):
        planes = comparar_planes(solicitud_basica)
        libre    = next(p for p in planes if p["plan"] == "libre")
        pro      = next(p for p in planes if p["plan"] == "pro")
        assert libre["comision"] > pro["comision"]

    def test_plan_pro_mayor_neto_repartidor(self, solicitud_basica):
        planes = comparar_planes(solicitud_basica)
        libre = next(p for p in planes if p["plan"] == "libre")
        pro   = next(p for p in planes if p["plan"] == "pro")
        assert pro["neto_repartidor"] > libre["neto_repartidor"]


# ─────────────────────────────────────────────
# Test de integración: caso real
# ─────────────────────────────────────────────

class TestCasoReal:

    def test_moto_express_intermunicipal_plan_estandar(self):
        """
        Caso real:
          Moto, Zona A→B, 15km, express, 10min espera, plan estándar
          Tarifa base A:  $55
          Km extra (10km): $60  → 10×$6
          Espera (1×$15): $15
          Express:        $30
          Zona A→B:       $25
          Subtotal:      $185

          Comisión 12%: $22.20
          Neto rep:    $162.80
        """
        solicitud = SolicitudCotizacion(
            vehiculo        = TipoVehiculo.MOTO,
            zona_origen     = Zona.A,
            zona_destino    = Zona.B,
            distancia_km    = 15.0,
            tipo_servicio   = TipoServicio.EXPRESS,
            plan_repartidor = PlanRepartidor.ESTANDAR,
            espera_minutos  = 10,
        )
        r = calcular_cotizacion(solicitud)

        assert r.es_valida
        assert r.desglose.tarifa_base    == 45.0   # base zona A
        assert r.desglose.cargo_km       == 50.0   # 10km × $5 (Zona A, moto)
        assert r.desglose.cargo_espera   == 15.0   # 1 bloque
        assert r.desglose.cargo_servicio == 30.0
        assert r.desglose.cargo_zona     == 25.0
        assert r.distribucion.total_cliente == 165.0
        assert abs(r.distribucion.comision_plataforma - 19.80) < 0.01
        assert abs(r.distribucion.ingreso_repartidor - 145.20) < 0.01
        assert r.tiempo_estimado_min is not None
