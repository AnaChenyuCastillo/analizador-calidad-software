import subprocess
import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def obtener_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def selecionar_directorio_proyecto() -> Path:
    root = tk.Tk()
    root.withdraw()

    ruta = filedialog.askdirectory(
        title="Selecciona la carpeta del proyecto java para analizar con Lizard"
    )

    if not ruta:
        raise RuntimeError("No se selecciono ninguna carpeta de proyecto")
    
    return Path(ruta)

def ejecutar_lizard(directorio_proyecto: Path):
    comando = [
        sys.executable,
        "-m",
        "lizard",
        str(directorio_proyecto)
    ]

    print("Comando ejecutado:")
    print(comando)

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    return resultado

def generar_texto_resultado(directorio_proyeto: Path, resultado) -> str:
    lineas = []
    lineas.append("RESULTADO DE LA PRUEBA DE - LIZARD")
    lineas.append("")
    lineas.append(f"Proyecto analizado: {directorio_proyeto.name}")
    lineas.append(f"Ruta del proyecto: {directorio_proyeto}")
    lineas.append("Herramienta: Lizard")
    lineas.append("Métrica principal: Coplejidad cicloatica")
    lineas.append("")
    lineas.append(f"Codigo de salida: {resultado.returncode}")
    lineas.append("")

    lineas.append("STDOUT")
    if resultado.stdout.strip():
        lineas.append(resultado.stdout)
    else:
        lineas.append("No se detecto duplicacion o no hubo salida estandar")

    lineas.append("")
    lineas.append("STDERR")
    if resultado.stderr.strip():
        lineas.append("ERRORES/ STDERR:")
        lineas.append(resultado.stderr)
    else:
        print("No hubo errores")

    return "\n".join(lineas)

def guardar_resultado_txt(contenido: str, nombre_proyecto: str) -> Path:
    repo_root = obtener_repo_root()
    carpeta_resultados =  repo_root / "pruebas_herramientas" / "resultados"
    carpeta_resultados.mkdir(parents=True, exist_ok=True)

    timestap = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ruta_fichero = carpeta_resultados / f"reultado_lizard_{nombre_proyecto}_{timestap}.txt"

    with open(ruta_fichero, "w", encoding="utf-8") as f:
        f.write(contenido)

    return ruta_fichero

def main() -> None:
    directorio_proyecto = selecionar_directorio_proyecto()
    print(f"Proyecto seleccionado: {directorio_proyecto}")

    resultado = ejecutar_lizard(directorio_proyecto)

    print("RETURN CODE: ", resultado.returncode)
    print("STDOUT")
    print(resultado.stdout)
    print("STDERR")
    print(resultado.stderr)

    contenido = generar_texto_resultado(directorio_proyecto, resultado)
    ruta_resultado = guardar_resultado_txt(contenido, directorio_proyecto.name)
    
    print("Prueba competa correctamente")
    print(f"Archivo generado: {ruta_resultado}")

if __name__ == "__main__":
    main()