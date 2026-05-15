from pathlib import Path

from analizador_calidad_software.procesar_resultados.referencias_metricas import (
    obtener_metricas_fuera_de_rango,
    referencia_lizard
)

def construir_fila (
    mostrar_ccn,
    elemento_analizado,
    nloc,
    ccn,
    tokens,
    parametros,
    longitud,
    clasificacion_ccn,
    observacion_ccn,
    metricas_fuera_de_rango
) -> list[str]:
    if mostrar_ccn:
        return [
            elemento_analizado,
            nloc,
            ccn,
            tokens,
            parametros,
            longitud,
            clasificacion_ccn,
            observacion_ccn,
            metricas_fuera_de_rango
        ] 
    else:
        return [
            elemento_analizado,
            nloc,
            tokens,
            parametros,
            longitud,
        ]

def obtener_clasificacion_ccn(ccn, rangos_cualitativos) -> tuple[str, str]:
    if not str(ccn).isdigit():
        return "No disponible", "No se ha podido interpretar en valor de CCN"
    
    valor_ccn = int(ccn)

    for rango in rangos_cualitativos:
        minimo = rango["min"]
        maximo = rango["max"]

        if maximo is None:
            if valor_ccn >= minimo:
                return rango["etiqueta"], rango["observacion"]
            
        elif valor_ccn >= minimo and valor_ccn <= maximo:
            return rango["etiqueta"], rango["observacion"]
    
    return "No clasificado", "No se ha encontrado rango cualitativo aplicable"

def obtener_ruta_relativa_lizard(elemento_analizado, ruta_proyecto: Path) -> str:
    if "@" not in elemento_analizado:
        return elemento_analizado
    
    nombre_funcion, resto = elemento_analizado.split("@", 1)
    if ":" in resto:
        ruta_archivo, numero_linea = resto.split(":", 1)
    else:
        ruta_archivo = resto
        numero_linea = ""

    try:
        ruta_relativa = str(
            Path(ruta_archivo).resolve().relative_to(ruta_proyecto.resolve())
        )
    except:
        ruta_relativa = ruta_archivo

    if numero_linea != "":
        return f"{nombre_funcion}@{ruta_relativa}:{numero_linea}"
    
    return f"{nombre_funcion}@{ruta_relativa}"

def es_fila_metricas_lizard(texto: str) -> bool:
    partes = texto.split()

    if len(partes) < 6:
        return False
    
    return (
        partes[0].isdigit()
        and partes[1].isdigit()
        and partes[2].isdigit()
        and partes[3].isdigit()
        and partes[4].isdigit()
    )

def procesar_lizard(ruta_txt: Path, ruta_proyecto: Path, lenguaje) -> dict:
    contenido = ruta_txt.read_text(encoding="utf-8", errors="replace")
    lineas = contenido.splitlines()

    info_referencia = referencia_lizard()
    rangos = info_referencia["rangos"]

    mostrar_ccn = lenguaje.lower() == "java"

    titulo = "Resultados Lizard"

    if mostrar_ccn:
        rangos_cualitativos_ccn = info_referencia["rangos_cualitativos"]["CCN"]

        cabeceras = [
            "Elemento analizado",
            "NLOC",
            "CCN",
            "Tokens",
            "Parametros",
            "longitud",
            "Clasificacion CCN",
            "Observacion CCN",
            "Metricas fuera de rango"
        ]
    else:
        cabeceras = [
            "Elemento analizado",
            "NLOC",
            "Tokens",
            "Parametros",
            "longitud"
        ]

    filas = []

    for linea in lineas:
        texto = linea.strip()

        if not es_fila_metricas_lizard(texto):
            continue

        partes = texto.split(None, 5)

        nloc = partes[0]
        ccn = partes[1]
        tokens = partes[2]
        parametos = partes[3]
        longitud = partes[4]
        elemento_analizado = partes[5]

        elemento_analizado = obtener_ruta_relativa_lizard(elemento_analizado, ruta_proyecto)
        clasificacion_ccn = ""
        observacion_ccn = ""
        metricas_fuera_de_rango = ""

        if mostrar_ccn:

            clasificacion_ccn, observacion_ccn = obtener_clasificacion_ccn(ccn, rangos_cualitativos_ccn)

            metricas_funcion = {
                "NLOC": nloc,
                "CCN": ccn,
                "TOKENS": tokens,
                "PARAM": parametos,
                "LENGTH": longitud
            }

            metricas_fuera_de_rango = obtener_metricas_fuera_de_rango(metricas_funcion, rangos)

        fila = construir_fila(
            mostrar_ccn,
            elemento_analizado,
            nloc,
            ccn,
            tokens,
            parametos,
            longitud,
            clasificacion_ccn,
            observacion_ccn,
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