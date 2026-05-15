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



def ejecutar_radon(subcomando: str, directorio_proyecto: Path):

    comando = [
        sys.executable,
        "-m",
        "radon",
        subcomando,
        str(directorio_proyecto)
    ]

    print(f"Comando ejecutado: ({subcomando})")
    print(comando)

    resltado = ejecutar_herramienta(comando)
    return resltado

def generar_bloque_resultado(nombre: str, descripcion: str, resultado) -> str:
    lineas = []
    lineas.append(f"========= RADON {nombre} ({descripcion}) ==========")
    lineas.append(f"Código de salida: {resultado.returncode}")
    lineas.append("")
    lineas.append("STDOUT:")
    if resultado.stdout.strip():
        lineas.append(resultado.stdout)
    else:
        lineas.append("No hubo salida estándar.")
    lineas.append("")
    lineas.append("STDERR:")
    if resultado.stderr.strip():
        lineas.append(resultado.stderr)
    else:
        lineas.append("No hubo errores.")
    lineas.append("")

    return "\n".join(lineas)

def generar_texto_resultado(directorio_proyecto: Path, resultado_cc, resultado_raw, resultado_mi, resultado_hal) -> str:
    lineas = []
    lineas.append("RESULTADO DE PRUEBA - RADON")
    lineas.append("")
    lineas.append(f"Proyecto analizador: {directorio_proyecto.name}")
    lineas.append(f"Ruta del proyecto: {directorio_proyecto}")   
    lineas.append("Lenguaje analizador: Pyhton")
    lineas.append("Herramienta: Radon")
    lineas.append("Subcomandos ejecutados: cc, raw, mi, hal")
    lineas.append("")
    lineas.append("")

    lineas.append(generar_bloque_resultado("CC", "Complejidad ciclomatica", resultado_cc))

    lineas.append(generar_bloque_resultado("RAW", "Metricas basicas del codigo", resultado_raw))

    lineas.append(generar_bloque_resultado("MI", "Indices de mantenibilidad", resultado_mi))

    lineas.append(generar_bloque_resultado("HAL", "Metricas de Halstead", resultado_hal))

    return "\n".join(lineas)

def ejecutar_analisis_radon(directorio_proyecto, carpeta_resultados) -> None:
    
    resultado_cc = ejecutar_radon("cc", directorio_proyecto)
    resultado_raw = ejecutar_radon("raw", directorio_proyecto)
    resultado_mi = ejecutar_radon("mi", directorio_proyecto)
    resultado_hal = ejecutar_radon("hal", directorio_proyecto)

    contenido = generar_texto_resultado(directorio_proyecto, resultado_cc, resultado_raw, resultado_mi, resultado_hal)

    ruta_resultado = guardar_resultado_txt(contenido, carpeta_resultados, "radon")

    print("Prueba competa correctamente")
    print(f"Archivo generado: {ruta_resultado}")

    return ruta_resultado

