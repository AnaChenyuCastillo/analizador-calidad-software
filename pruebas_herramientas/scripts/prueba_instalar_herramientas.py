import subprocess
import sys
from pathlib import Path

def obtener_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

def obtener_requirements() -> Path:
    repo_root = obtener_repo_root()
    ruta = repo_root / "herramientas" / "requirements.txt"

    if not ruta.exists():
        raise RuntimeError(f"No se encontro el fichero en {ruta}")
    
    return ruta

def instalar_requirements(ruta_requirements: Path) -> bool:
    print("INstalando dependencias")

    resultado = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(ruta_requirements)],
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
    ruta_requirements = obtener_requirements()
    exito = instalar_requirements(ruta_requirements)

    print("\nResumen de instalación:")
    if exito:
        print("Todas las dependencias de requirements.txt se han instalado correctamente.")
    else:
        print("Ha habido errores al instalar las dependencias de requirements.txt.")


if __name__ == "__main__":
    main()