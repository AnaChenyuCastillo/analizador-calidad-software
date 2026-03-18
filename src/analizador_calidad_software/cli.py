import sys
import subprocess
import shutil
from pathlib import Path


def obtener_ruta_herramienta(nombre: str) -> Path:
    #Prueba para ejecutar cloc.exe
    repo_root = Path(__file__).resolve().parents[2]
    ruta = repo_root / "herramientas" / nombre / f"{nombre}.exe"

    if not ruta.exists():
        raise RuntimeError(f"No se encontro el archivo '{nombre}.exe' en {ruta}")
    
    return ruta

def ejecutar_herramienta(nombre: str, argumentos: list[str]):
    #Ejecuta una de las herramientas del repositorio.

    #El parámetro nombre corresponde con el nombre de la herramienta
    #El parámetro argumento corrresponde con la lista de argumentos para lanzar el ejecutable

    ruta = obtener_ruta_herramienta(nombre)

    resultado = subprocess.run(
        [str(ruta)] + argumentos,
        capture_output=True,
        text=True,
    )

    return resultado


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
    
    
    #Prueba para ejecutar cloc.exe
    resultado= ejecutar_herramienta("cloc", ["--version"])

    print("Salida de cloc:")
    print(resultado.stdout)

    if ruta.is_dir():
        print(f"Analizando directorio: {ruta.resolve()}")
    elif ruta.is_file():
        print(f"Analizando fichero: {ruta.resolve()}")
    else:
        print("Error: la ruta indicada no es válida.")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
