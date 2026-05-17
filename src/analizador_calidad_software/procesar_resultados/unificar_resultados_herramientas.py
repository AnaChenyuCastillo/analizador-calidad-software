from pathlib import Path
from typing import Any

from analizador_calidad_software.procesar_resultados.procesar_ckjm import procesar_ckjm
from analizador_calidad_software.procesar_resultados.procesar_cpd import procesar_cpd
from analizador_calidad_software.procesar_resultados.procesar_lizard import procesar_lizard
from analizador_calidad_software.procesar_resultados.procesar_radon import procesar_radon
from analizador_calidad_software.procesar_resultados.procesar_pylint import procesar_pylint
from analizador_calidad_software.procesar_resultados.referencias_metricas import (
    referencia_ckjm,
    referencia_cpd,
    referencia_lizard,
    referencia_radon,
    referencia_pylint,
)

def obtener_procesador(nombre_herramienta: str):
    nombre = nombre_herramienta.strip().upper()

    match nombre:
        case "CKJM":
            return procesar_ckjm
        case "CPD":
            return procesar_cpd
        case "LIZARD":
            return procesar_lizard
        case "RADON":
            return procesar_radon
        case "PYLINT":
            return procesar_pylint
        
    return None

def obtener_referencias(nombre_herramienta: str, lenguaje: str):
    nombre = nombre_herramienta.strip().upper()

    match nombre:
        case "CKJM":
            return referencia_ckjm()
        case "CPD":
            return referencia_cpd()
        case "LIZARD":
            return referencia_lizard(lenguaje)
        case "RADON":
            return referencia_radon()
        case "PYLINT":
            return referencia_pylint()
        
    return {}

def crear_tabla_error(nombre_herramienta: str, ruta_txt: Path) -> dict:
    return {
        "titulo" : f"Resultado no procesado - {nombre_herramienta}",
        "tabla_referencias": "",
        "observaciones_tabla": "No existe un procesardo definido para esta herramienta.",
        "cabeceras": ["Elemento analizado", "observacion"],
        "filas" : [[str(ruta_txt),"Ho existe un procesador definido para esta herramienta"]],
    }

def unificar_resultados_herramientas(nombre_proyecto: str, ruta_proyecto: Path, resultados_herramientas: list[dict], lenguaje: str) -> str:
    datos_proyecto = {
        "nombre_proyecto": nombre_proyecto,
        "ruta_proyecto": ruta_proyecto,
        "lenguaje": lenguaje
    }

    tablas_resultados = []

    for resultado in resultados_herramientas:
        nombre_herramienta = resultado["herramienta"]
        ruta_txt = Path(resultado["ruta_txt"])

        if nombre_herramienta.strip().upper() == "CKJM":
            errores_ckjm = resultado.get("errores_ckjm", resultado.get("errores", []))

            if errores_ckjm is None:
                errores_ckjm = []

        procesador = obtener_procesador(nombre_herramienta)

        if procesador is None:
            tabla = crear_tabla_error(nombre_herramienta, ruta_txt)

        else: 
            tabla = procesador(ruta_txt, ruta_proyecto, lenguaje)

        referencias = obtener_referencias(nombre_herramienta, lenguaje)

        if isinstance(tabla, list): # usamos instace para comprobar si es una lista
            tablas_resultados.extend(tabla) #si es una lista se ñanade los elementos de la lista uno a uno

        else:
            tabla["referencias"] = referencias

            tablas_resultados.append(tabla)

    return datos_proyecto, tablas_resultados

