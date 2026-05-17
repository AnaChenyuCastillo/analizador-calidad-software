from pathlib import Path

from analizador_calidad_software.procesar_resultados.referencias_metricas import (
    obtener_metricas_fuera_de_rango,
    referencia_cpd
)

def construir_fila(
    elemento_analizado,
    lineas_duplicadas,
    tokens,
    metricas_fuera_de_rango
) -> list[str]:
    return [
        elemento_analizado,
        lineas_duplicadas,
        tokens,
        metricas_fuera_de_rango
    ]

def procesar_cpd(ruta_txt: Path, ruta_proyecto: Path, lenguaje) -> dict:
    contenido = ruta_txt.read_text(encoding="utf-8", errors="replace")
    lineas = contenido.splitlines()

    info_referencia = referencia_cpd()
    rangos = info_referencia["referencias_metricas"]

    titulo = "Resultados CPD"

    cabeceras = [
        "Elemento analizado",
        "Lineas duplicadas",
        "Tokens",
        "Metricas fuera de rango"
    ]

    filas = []

    lineas_duplicadas = ""
    tokens = ""
    archivos_bloque = []

    for linea in lineas:
        texto = linea.strip()

        if texto.startswith("Found a ") and " duplication in the following files:" in texto:
            if archivos_bloque:
                elemnento_analizado = " <-> ".join(archivos_bloque)

                metricas_bloque = {
                    "LINEAS_DUPLICADAS": lineas_duplicadas,
                    "TOKENS": tokens,
                }

                metricas_fuera_de_rango = obtener_metricas_fuera_de_rango(metricas_bloque, rangos)

                fila = construir_fila(
                    elemnento_analizado,
                    lineas_duplicadas,
                    tokens,
                    metricas_fuera_de_rango
                )

                filas.append(fila)

            partes = texto.split()

            lineas_duplicadas = ""
            tokens = ""
            archivos_bloque = []

            if len(partes) >= 6:
                lineas_duplicadas = partes[2]
                tokens = partes[4].replace("(", "").replace(")", "")
        
        elif texto.startswith("Starting at line ") and " of " in texto:
            ruta_archivo = texto.split(" of ", 1)[1].strip()

            try:
                ruta_relativa = str(
                    Path(ruta_archivo).resolve().relative_to(ruta_proyecto.resolve())
                )
            except Exception:
                ruta_relativa = ruta_archivo

            archivos_bloque.append(ruta_relativa)

    if archivos_bloque:
        elemnento_analizado = " <-> ".join(archivos_bloque)

        metricas_bloque = {
            "LINEAS_DUPLICADAS": lineas_duplicadas,
            "TOKENS": tokens
        }

        metricas_fuera_de_rango = obtener_metricas_fuera_de_rango(metricas_bloque, rangos)

        fila = construir_fila(
            elemnento_analizado,
            lineas_duplicadas,
            tokens,
            metricas_fuera_de_rango
        )

        filas.append(fila)

    tabla = {
        "titulo": titulo,
        "tabla_referencias": info_referencia["tabla_referencias"],
        "observaciones_tabla": info_referencia["observaciones_tabla"],
        "cabeceras": cabeceras,
        "filas": filas
    }

    return tabla