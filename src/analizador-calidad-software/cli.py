import sys
from pathlib import Path


def main() -> int:
    # 1) Validación: comprobar que el usuario ha pasado una ruta
    if len(sys.argv) < 2:
        print("Uso: python -m analizador_calidad_software.cli <ruta_proyecto>")
        return 1

    # 2) Convertir el argumento a una ruta y validar que existe
    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print("Error: la ruta indicada no existe.")
        return 1

    # 3) Confirmación básica (por ahora no se ejecutan herramientas)
    print(f"Proyecto listo para analizar: {ruta.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
