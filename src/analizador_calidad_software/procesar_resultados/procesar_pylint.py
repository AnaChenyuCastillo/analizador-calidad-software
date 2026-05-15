from pathlib import Path
import re

from analizador_calidad_software.procesar_resultados.referencias_metricas import (
    referencia_pylint,
)


def construir_fila_resumen(
    categoria,
    severidad,
    numero_incidencias,
    interpretacion,
) -> list[str]:
    return [
        categoria,
        severidad,
        numero_incidencias,
        interpretacion,
    ]


def construir_fila_detalle(
    archivo,
    linea,
    columna,
    categoria,
    codigo,
    simbolo,
    mensaje,
    severidad,
    interpretacion,
) -> list[str]:
    return [
        archivo,
        linea,
        columna,
        categoria,
        codigo,
        simbolo,
        mensaje,
        severidad,
        interpretacion,
    ]


def obtener_ruta_relativa(ruta_archivo, ruta_proyecto: Path) -> str:
    try:
        return str(Path(ruta_archivo).resolve().relative_to(ruta_proyecto.resolve()))
    except Exception:
        return ruta_archivo


def extraer_puntuacion_pylint(texto: str) -> str:
    patron = r"rated at\s+(-?\d+(?:\.\d+)?)/10"

    coincidencia = re.search(patron, texto)

    if coincidencia is None:
        return ""

    return coincidencia.group(1) + "/10"


def procesar_linea_pylint(texto: str):
    patron = r"^(.*?):(\d+):(\d+):\s*([A-Z]\d{4}):\s*(.*?)\s*\(([^()]*)\)\s*$"

    coincidencia = re.match(patron, texto)

    if coincidencia is None:
        return None

    archivo = coincidencia.group(1).strip()
    linea = coincidencia.group(2).strip()
    columna = coincidencia.group(3).strip()
    codigo = coincidencia.group(4).strip()
    mensaje = coincidencia.group(5).strip()
    simbolo = coincidencia.group(6).strip()

    return archivo, linea, columna, codigo, mensaje, simbolo


def procesar_pylint(ruta_txt: Path, ruta_proyecto: Path, lenguaje: str = "") -> list[dict]:
    contenido = ruta_txt.read_text(encoding="utf-8", errors="replace")
    lineas = contenido.splitlines()

    info_referencia = referencia_pylint()
    categorias = info_referencia["categorias"]
    categorias_detalle = info_referencia["categorias_detalle"]

    puntuacion = extraer_puntuacion_pylint(contenido)

    contador_categorias = {}

    for codigo_categoria in categorias:
        contador_categorias[codigo_categoria] = 0

    filas_detalle = []

    for linea_txt in lineas:
        texto = linea_txt.strip()

        if texto == "":
            continue

        resultado = procesar_linea_pylint(texto)

        if resultado is None:
            continue

        archivo, linea, columna, codigo, mensaje, simbolo = resultado

        tipo_categoria = codigo[0]

        if tipo_categoria not in categorias:
            continue

        contador_categorias[tipo_categoria] = contador_categorias[tipo_categoria] + 1

        if tipo_categoria not in categorias_detalle:
            continue

        informacion_categoria = categorias[tipo_categoria]

        archivo = obtener_ruta_relativa(archivo, ruta_proyecto)
        categoria = informacion_categoria["nombre"]
        severidad = informacion_categoria["severidad"]
        interpretacion = informacion_categoria["interpretacion"]

        fila = construir_fila_detalle(
            archivo,
            linea,
            columna,
            categoria,
            codigo,
            simbolo,
            mensaje,
            severidad,
            interpretacion,
        )

        filas_detalle.append(fila)

    filas_resumen = []

    for codigo_categoria, informacion_categoria in categorias.items():
        fila_resumen = construir_fila_resumen(
            informacion_categoria["nombre"],
            informacion_categoria["severidad"],
            contador_categorias[codigo_categoria],
            informacion_categoria["interpretacion"],
        )

        filas_resumen.append(fila_resumen)

    observacion_resumen = info_referencia["observaciones_tabla"]

    if puntuacion != "":
        observacion_resumen = (
            f"Puntuación Pylint: {puntuacion}. "
            + observacion_resumen
        )

    tabla_resumen = {
        "titulo": "Resumen Pylint",
        "tabla_referencias": info_referencia["tabla_referencias"],
        "observaciones_tabla": observacion_resumen,
        "cabeceras": [
            "Categoria",
            "Severidad",
            "Numero de incidencias",
            "Interpretacion",
        ],
        "filas": filas_resumen,
    }

    tabla_detalle = {
        "titulo": "Incidencias relevantes Pylint",
        "tabla_referencias": (
            "Esta tabla muestra únicamente las incidencias de Pylint clasificadas como "
            "Fatal, Error, Warning o Refactor."
        ),
        "observaciones_tabla": (
            "No se muestran los mensajes de convención ni los informativos para centrar "
            "el informe en errores, advertencias y mejoras relevantes."
        ),
        "cabeceras": [
            "Archivo",
            "Linea",
            "Columna",
            "Categoria",
            "Codigo",
            "Simbolo",
            "Mensaje",
            "Severidad",
            "Interpretacion",
        ],
        "filas": filas_detalle,
    }

    return [
        tabla_resumen,
        tabla_detalle,
    ]