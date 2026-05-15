import subprocess
import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

from analizador_calidad_software.cli import (
    ejecutar_herramienta, 
    guardar_resultado_txt
    )


def ejecutar_pylint(directorio_proyecto: Path):
    comando = [
        sys.executable,
        "-m",
        "pylint",
        str(directorio_proyecto)
    ]

    print(f"Comando ejecutado: )")
    print(comando)

    resltado = ejecutar_herramienta(comando)

    return resltado

def generar_texto_resultado(directorio_proyeto: Path, resultado) -> str:
    lineas = []
    lineas.append("RESULTADO DE LA PRUEBA DE - LIZARD")
    lineas.append("")
    lineas.append(f"Proyecto analizado: {directorio_proyeto.name}")
    lineas.append(f"Ruta del proyecto: {directorio_proyeto}")
    lineas.append("Herramienta: Pylant")
    lineas.append("Lenguaje principal: Python")
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


def ejecutar_analisis_pylint(directorio_proyecto, carpeta_resultados) -> None:

    print(f"Proyecto seleccionado: {directorio_proyecto}")

    resultado = ejecutar_pylint(directorio_proyecto)

    print("RETURN CODE: ", resultado.returncode)
    print("STDOUT")
    print(resultado.stdout)
    print("STDERR")
    print(resultado.stderr)

    contenido = generar_texto_resultado(directorio_proyecto, resultado)
    ruta_resultado = guardar_resultado_txt(contenido, carpeta_resultados, "pylint")
    
    print("Prueba competa correctamente")
    print(f"Archivo generado: {ruta_resultado}")

    return ruta_resultado

