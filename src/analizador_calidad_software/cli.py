import sys
import subprocess
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

def seleccionar_proyecto() -> Path:
    root = tk.Tk()
    root.withdraw()

    ruta = filedialog.askdirectory(
        title=("Seleccionar la carpeta del proyecto que quieres analizar")
    )

    if not ruta:
        raise RuntimeError("No se ha selecionado ninguna carpeta de proyecto")
    
    ruta_proyecto = Path(ruta).resolve()

    if not ruta_proyecto.exists():
        raise RecursionError("La ruta selecionada no existe")
    
    if not ruta_proyecto.is_dir():
        raise RuntimeError("La ruta selecionada no es una carpeta")
    
    return ruta_proyecto

def obtener_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def obtener_ruta_herramienta(nombre: str, nombre_fichero) -> Path:
    #Prueba para ejecutar cloc.exe
    repo_root = obtener_repo_root()
    if nombre == "cpd":
        ruta = repo_root / "herramientas" / nombre / "bin" /nombre_fichero
    else:
        ruta = repo_root / "herramientas" / nombre / nombre_fichero

    if not ruta.exists():
        raise RuntimeError(f"No se encontro el archivo '{nombre}.exe' en {ruta}")
    
    return ruta

def ejecutar_herramienta(argumentos: list[str], cwd=None):
    #Ejecuta una de las herramientas del repositorio.

    #El parámetro nombre corresponde con el nombre de la herramienta
    #El parámetro argumento corrresponde con la lista de argumentos para lanzar el ejecutable
    if cwd is None:
        resultado = subprocess.run(
            argumentos,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
    else:
        resultado = subprocess.run(
            argumentos,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(cwd) if cwd else None #Lo que hacemos es que si le pasamos un proyecto lo coge como referencia para la ejecución pero si no se lo pasamos siguimos tenienedo por defecto el proyecto en el que estamos trabajando
        )

    return resultado

def guardar_resultado_txt(contenido: str, carpeta_resultados, nombre_herramienta) -> Path:
    
    ruta_fichero = carpeta_resultados / f"reultado_{nombre_herramienta}.txt"

    with open(ruta_fichero, "w", encoding="utf-8") as f:
        f.write(contenido)

    return ruta_fichero



'''def main() -> int:
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
'''