import subprocess
import sys
from pathlib import Path

from cli import (obtener_repo_root)

def obtener_herramientas() -> Path:
    repo_root = obtener_repo_root()
    ruta = repo_root / "herramientas" / "herramientas.txt"

    if not ruta.exists():
        raise RuntimeError(f"No se encontro el fichero en {ruta}")
    
    return ruta

def instalar_herramientas(ruta_herramientas: Path) -> bool:
    print("Instalando dependencias")

    resultado = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(ruta_herramientas)],
        capture_output=True,
        text=True
    )

    print("Codigo de salida: ", resultado.returncode)

    if resultado.stdout.strip():
        print("STDOUT:")
        print(resultado.stdout)

    if resultado.stderr.strip():
        print("STDERR:")
        print(resultado.stderr)

    return resultado.returncode == 0


def main() -> None:
    ruta_herramientas = obtener_herramientas()
    exito = instalar_herramientas(ruta_herramientas)

    print("\nResumen de instalación:")
    if exito:
        print("Todas las dependencias de requirements.txt se han instalado correctamente.")
    else:
        print("Ha habido errores al instalar las dependencias de requirements.txt.")


if __name__ == "__main__":
    main()