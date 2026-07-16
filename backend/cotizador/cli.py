"""
cotizador/cli.py
================
Herramienta de línea de comandos para calcular cotizaciones sin abrir el navegador.

Uso básico:
    python cli.py

Con parámetros directos:
    python cli.py --vehiculo moto --origen A --destino B --km 12 --servicio express

Modo comparación de planes:
    python cli.py --comparar --vehiculo auto --origen A --destino A --km 8
"""
import argparse
import sys
import os

# Agregar el directorio del módulo al path
sys.path.insert(0, os.path.dirname(__file__))

from modelos import TipoVehiculo, Zona, TipoServicio, PlanRepartidor
from calculadora import calcular_cotizacion, comparar_planes
from schemas import SolicitudCotizacion


# ─────────────────────────────────────────────
# Menú interactivo
# ─────────────────────────────────────────────

OPCIONES_VEHICULO = {
    "1": TipoVehiculo.MOTO,
    "2": TipoVehiculo.AUTO,
    "3": TipoVehiculo.SUV,
    "4": TipoVehiculo.PICKUP,
    "5": TipoVehiculo.CAMIONETA,
}

OPCIONES_ZONA = {
    "A": Zona.A,
    "B": Zona.B,
    "C": Zona.C,
}

OPCIONES_SERVICIO = {
    "1": TipoServicio.ESTANDAR,
    "2": TipoServicio.EXPRESS,
    "3": TipoServicio.PROGRAMADO,
    "4": TipoServicio.FRAGIL,
}

OPCIONES_PLAN = {
    "1": PlanRepartidor.LIBRE,
    "2": PlanRepartidor.ESTANDAR,
    "3": PlanRepartidor.PRO,
}


def menu_interactivo() -> SolicitudCotizacion:
    """Guía al usuario a través de un menú para construir la solicitud."""
    print("\n" + "="*50)
    print("  📦 COTIZADOR EnvíosApp")
    print("="*50)

    # Vehículo
    print("\n¿Qué tipo de vehículo necesitas?")
    print("  1) 🛵 Motocicleta  (hasta 20 kg)")
    print("  2) 🚗 Auto         (hasta 100 kg)")
    print("  3) 🚙 SUV          (hasta 300 kg)")
    print("  4) 🛻 Pickup       (hasta 700 kg)")
    print("  5) 🚚 Camioneta    (hasta 1,500 kg)")
    while True:
        opcion = input("Elige (1-5): ").strip()
        if opcion in OPCIONES_VEHICULO:
            vehiculo = OPCIONES_VEHICULO[opcion]
            break
        print("  Opción inválida, intenta de nuevo.")

    # Zonas
    print("\n¿Zona de ORIGEN?")
    print("  A) Teotihuacán + San Martín de las Pirámides")
    print("  B) Texcoco + Tecámac")
    print("  C) Otumba")
    while True:
        zo = input("Zona origen (A/B/C): ").strip().upper()
        if zo in OPCIONES_ZONA:
            zona_origen = OPCIONES_ZONA[zo]
            break
        print("  Opción inválida.")

    print("\n¿Zona de DESTINO?")
    print("  A) Teotihuacán + San Martín de las Pirámides")
    print("  B) Texcoco + Tecámac")
    print("  C) Otumba")
    while True:
        zd = input("Zona destino (A/B/C): ").strip().upper()
        if zd in OPCIONES_ZONA:
            zona_destino = OPCIONES_ZONA[zd]
            break
        print("  Opción inválida.")

    # Distancia
    while True:
        try:
            distancia_km = float(input("\nDistancia total en km: ").strip())
            if 0 < distancia_km <= 100:
                break
            print("  La distancia debe ser entre 0.1 y 100 km.")
        except ValueError:
            print("  Ingresa un número válido.")

    # Tipo de servicio
    print("\n¿Tipo de servicio?")
    print("  1) Estándar   (mismo día, sin cargo extra)")
    print("  2) Express    (menos de 45 min, +$30)")
    print("  3) Programado (hora exacta, +$20)")
    print("  4) Frágil     (manejo especial, +$25)")
    while True:
        opcion = input("Elige (1-4): ").strip()
        if opcion in OPCIONES_SERVICIO:
            tipo_servicio = OPCIONES_SERVICIO[opcion]
            break
        print("  Opción inválida.")

    # Espera
    while True:
        try:
            espera = int(input("\nTiempo de espera estimado en minutos (0 si no aplica): ").strip())
            if 0 <= espera <= 240:
                break
            print("  La espera debe ser entre 0 y 240 minutos.")
        except ValueError:
            print("  Ingresa un número entero.")

    # Plan del repartidor
    print("\n¿Plan del repartidor?")
    print("  1) Libre    (sin membresía, 22% comisión)")
    print("  2) Estándar ($299/mes, 12% comisión)")
    print("  3) Pro      ($549/mes, 6% comisión)")
    while True:
        opcion = input("Elige (1-3): ").strip()
        if opcion in OPCIONES_PLAN:
            plan = OPCIONES_PLAN[opcion]
            break
        print("  Opción inválida.")

    # Peso (opcional)
    peso = None
    resp = input("\n¿Deseas ingresar el peso del paquete? (s/n): ").strip().lower()
    if resp == "s":
        while True:
            try:
                peso = float(input("Peso en kg: ").strip())
                if peso > 0:
                    break
                print("  El peso debe ser positivo.")
            except ValueError:
                print("  Ingresa un número válido.")

    return SolicitudCotizacion(
        vehiculo        = vehiculo,
        zona_origen     = zona_origen,
        zona_destino    = zona_destino,
        distancia_km    = distancia_km,
        tipo_servicio   = tipo_servicio,
        plan_repartidor = plan,
        espera_minutos  = espera,
        peso_kg         = peso,
    )


# ─────────────────────────────────────────────
# Modo comparación de planes
# ─────────────────────────────────────────────

def mostrar_comparacion(solicitud: SolicitudCotizacion) -> None:
    """Muestra la cotización para los 3 planes en una tabla."""
    planes = comparar_planes(solicitud)
    if not planes:
        print("No se pudo calcular la comparación.")
        return

    print("\n" + "="*60)
    print("  COMPARACIÓN DE PLANES — una entrega")
    print("="*60)
    print(f"  {'Plan':<12} {'Membresía/mes':<16} {'Comisión':<12} {'Tú cobras':<12} {'Plataforma'}")
    print("-"*60)
    mejor_plan = max(planes, key=lambda p: p["neto_repartidor"])
    for p in planes:
        marca = " ★" if p["plan"] == mejor_plan["plan"] else ""
        print(
            f"  {p['plan'].upper():<12} "
            f"${p['membresia_mensual']:<14.0f} "
            f"{p['tasa_comision']*100:.0f}%{'':<9} "
            f"${p['neto_repartidor']:<10.2f} "
            f"${p['comision']:.2f}{marca}"
        )
    print("="*60)
    print(f"\n  ★ = Plan recomendado para esta entrega\n")


# ─────────────────────────────────────────────
# Parser de argumentos
# ─────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Cotizador de envíos EnvíosApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python cli.py
  python cli.py --vehiculo moto --origen A --destino B --km 12 --servicio express
  python cli.py --comparar --vehiculo auto --origen A --destino A --km 8
        """
    )
    parser.add_argument("--vehiculo",  choices=["moto","auto","suv","pickup","camioneta"])
    parser.add_argument("--origen",    choices=["A","B","C"])
    parser.add_argument("--destino",   choices=["A","B","C"])
    parser.add_argument("--km",        type=float)
    parser.add_argument("--servicio",  choices=["estandar","express","programado","fragil"], default="estandar")
    parser.add_argument("--plan",      choices=["libre","estandar","pro"], default="libre")
    parser.add_argument("--espera",    type=int, default=0)
    parser.add_argument("--peso",      type=float, default=None)
    parser.add_argument("--comparar",  action="store_true", help="Comparar los 3 planes")
    return parser.parse_args()


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────

def main():
    args = parse_args()

    # Si se pasan todos los argumentos necesarios, usar modo directo
    if all([args.vehiculo, args.origen, args.destino, args.km]):
        solicitud = SolicitudCotizacion(
            vehiculo        = TipoVehiculo(args.vehiculo),
            zona_origen     = Zona(args.origen),
            zona_destino    = Zona(args.destino),
            distancia_km    = args.km,
            tipo_servicio   = TipoServicio(args.servicio),
            plan_repartidor = PlanRepartidor(args.plan),
            espera_minutos  = args.espera,
            peso_kg         = args.peso,
        )
    else:
        # Modo interactivo
        solicitud = menu_interactivo()

    if args.comparar or (not args.vehiculo and input("\n¿Comparar los 3 planes? (s/n): ").strip().lower() == "s"):
        mostrar_comparacion(solicitud)
    else:
        resultado = calcular_cotizacion(solicitud)
        print("\n" + resultado.resumen())

        if resultado.tiempo_estimado_min:
            print(f"\n  ⏱  Tiempo estimado: ~{resultado.tiempo_estimado_min} minutos")

        if resultado.advertencias:
            print()
            for adv in resultado.advertencias:
                print(f"  ⚠  {adv}")

        if not resultado.es_valida:
            sys.exit(1)


if __name__ == "__main__":
    main()
