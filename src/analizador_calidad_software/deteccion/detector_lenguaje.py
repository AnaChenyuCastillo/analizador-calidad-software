import json
from pathlib import Path
from typing import Literal
import re
import sys

repo_root = Path(__file__).resolve().parents[1]
src_path = repo_root / "src"
print(src_path)
sys.path.insert(0, str(src_path))
from analizador_calidad_software.cli import (
    ejecutar_herramienta,
    obtener_ruta_herramienta
)

LenguajeDetectado = Literal["java", "python", "desconocido"]

def obtener_lenguaje_principal(salida__json: str) -> str:
    datos = json.loads(salida__json)

    lenguajes = []
    for clave, valor in datos.items():
        if clave in ("header", "SUM"):
            continue

        if isinstance(valor, dict) and "code" in valor:
            lenguajes.append((clave, valor["code"]))
        
    if not lenguajes:
        return "Desconocido"
    
    lenguajes.sort(key=lambda x: x[1], reverse=True)

    return lenguajes[0][0].lower()

def obtener_ranking_lenguajes(salida__json: str) -> list[tuple[str, int]]:
    datos = json.loads(salida__json)

    lenguajes = []
    for clave, valor in datos.items():
        if clave in ("header", "SUM"):
            continue

        if isinstance(valor, dict) and "code" in valor:
            lenguajes.append((clave.lower(), valor["code"]))

    lenguajes.sort(key=lambda x: x[1], reverse=True)

    return lenguajes

def ejecutar_cloc_para_deteccion(ruta_proyecto: Path):
    ruta_cloc = obtener_ruta_herramienta("cloc", "cloc.exe")
    resultado = ejecutar_herramienta([str(ruta_cloc), str(ruta_proyecto), "--json"])
    if resultado.returncode != 0:
        raise RuntimeError(
            f"Error al ejecutar cloc.\nSTDOUT:\n{resultado.stdout}\nSTDERR:\n{resultado.stderr}"
        )

    return resultado


def detectar_lenguaje_proyecto(ruta_proyecto: Path) -> LenguajeDetectado:
    ruta_cloc = obtener_ruta_herramienta("cloc", "cloc.exe")
    resultado = ejecutar_herramienta([str(ruta_cloc), str(ruta_proyecto), "--json"])
    lenguaje = obtener_lenguaje_principal(resultado.stdout)

    if lenguaje in ("java", "python"):
        return lenguaje

    return "desconocido"


def obtener_ranking_lenguajes_proyecto(ruta_proyecto: Path) -> list[tuple[str, int]]:
    resultado = ejecutar_cloc_para_deteccion(ruta_proyecto)
    return obtener_ranking_lenguajes(resultado.stdout)