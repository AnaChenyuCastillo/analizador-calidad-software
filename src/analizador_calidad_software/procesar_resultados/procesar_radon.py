from pathlib import Path

from analizador_calidad_software.procesar_resultados.referencias_metricas import (
    referencia_radon,
)

def construir_fila(
    elemento_analizado,
    sloc,
    complejidad,
    clasificacion_complejidad,
    observacion_complejidad,
    mi,
    clasificacion_mi,
    observacion_mi,
    volumen
) -> list[str]:
    return [
        elemento_analizado,
        sloc,
        complejidad,
        clasificacion_complejidad,
        observacion_complejidad,
        mi,
        clasificacion_mi,
        observacion_mi,
        volumen
    ]

def obtener_clasificacion(valor, rangos_cualitativos) -> tuple[str, str]:
    try:
        valor_numerico = float(valor)
    except Exception:
        return "No disponible", "No se ha podido interpretar el valor."

    for rango in rangos_cualitativos:
        minimo = rango["min"]
        maximo = rango["max"]

        if maximo is None:
            if valor_numerico >= minimo:
                return rango["etiqueta"], rango["observacion"]

        elif valor_numerico >= minimo and valor_numerico <= maximo:
            return rango["etiqueta"], rango["observacion"]

    return "No clasificado", "No se ha encontrado un rango cualitativo aplicable."


def obtener_ruta_relativa(ruta_archivo, ruta_proyecto: Path) -> str:
    try:
        return str(Path(ruta_archivo).resolve().relative_to(ruta_proyecto.resolve()))
    except Exception:
        return ruta_archivo


def crear_datos_archivo_vacios() -> dict:
    return {
        "SLOC": "",
        "MI": "",
        "VOLUMEN": "",
    }

def procesador_radon(ruta_txt: Path, ruta_proyecto: Path, lenguaje) -> dict:
    contenido = ruta_txt.read_text(encoding="utf-8", errors="replace")
    lineas = contenido.splitlines()

    info_referencia = referencia_radon()

    rangos_complejidad = info_referencia["rangos_cualitativos"]["COMPLEJIDAD"]

    rangos_mi = info_referencia["rangos_cualitativos"]["MI"]

    titulo = "Resultados Radon"

    cabeceras = [
        "Elemento analizado",
        "SLOC",
        "Complejidad ciclomatica",
        "Clasificacion complejidad",
        "Observacion complejidad",
        "MI",
        "Clasificacion MI",
        "Observacion MI",
        "Volumen Halstead",
    ]

    datos_archivos = {}
    filas_complejidad = []

    seccion_actual = ""
    archivo_actual = ""

    for linea in lineas:
        texto = linea.strip()

        if texto == "":
            continue

        if texto.startswith("===") and texto.endswith("==="):
            seccion_actual = texto.replace("=", "").strip().upper()
            archivo_actual = ""
            continue

        if seccion_actual == "RAW":
            if texto.endswith(".py"):
                archivo_actual = obtener_ruta_relativa(texto, ruta_proyecto)

                if archivo_actual not in datos_archivos:
                    datos_archivos[archivo_actual] = crear_datos_archivo_vacios()

            elif texto.startswith("SLOC:") and archivo_actual != "":
                datos_archivos[archivo_actual]["SLOC"] = texto.split(":", 1)[1].strip()

        elif seccion_actual == "MI":
            if " - " in texto:
                archivo, mi = texto.split(" - ", 1)
                archivo = obtener_ruta_relativa(archivo.strip(), ruta_proyecto)
                mi = mi.strip()

                if archivo not in datos_archivos:
                    datos_archivos[archivo] = crear_datos_archivo_vacios()

                datos_archivos[archivo]["MI"] = mi

        elif seccion_actual == "HALSTEAD":
            if texto.endswith(".py"):
                archivo_actual = obtener_ruta_relativa(texto, ruta_proyecto)

                if archivo_actual not in datos_archivos:
                    datos_archivos[archivo_actual] = crear_datos_archivo_vacios()

            elif texto.startswith("VOLUMEN:") and archivo_actual != "":
                datos_archivos[archivo_actual]["VOLUMEN"] = texto.split(":", 1)[1].strip()

        elif seccion_actual == "COMPLEJIDAD":
            if texto.endswith(".py"):
                archivo_actual = obtener_ruta_relativa(texto, ruta_proyecto)

                if archivo_actual not in datos_archivos:
                    datos_archivos[archivo_actual] = crear_datos_archivo_vacios()

            elif " - " in texto and archivo_actual != "":
                nombre_bloque, complejidad = texto.rsplit(" - ", 1)

                elemento_analizado = f"{archivo_actual}::{nombre_bloque.strip()}"
                complejidad = complejidad.strip()

                filas_complejidad.append(
                    {
                        "archivo": archivo_actual,
                        "elemento": elemento_analizado,
                        "COMPLEJIDAD": complejidad,
                    }
                )

    filas = []

    for fila_complejidad in filas_complejidad:
        archivo = fila_complejidad["archivo"]
        elemento_analizado = fila_complejidad["elemento"]
        complejidad = fila_complejidad["COMPLEJIDAD"]

        datos_archivo = datos_archivos.get(
            archivo,
            crear_datos_archivo_vacios(),
        )

        sloc = datos_archivo["SLOC"]
        mi = datos_archivo["MI"]
        volumen = datos_archivo["VOLUMEN"]

        clasificacion_complejidad, observacion_complejidad = obtener_clasificacion(
            complejidad,
            rangos_complejidad,
        )

        clasificacion_mi, observacion_mi = obtener_clasificacion(
            mi,
            rangos_mi,
        )

        fila = construir_fila(
            elemento_analizado,
            sloc,
            complejidad,
            clasificacion_complejidad,
            observacion_complejidad,
            mi,
            clasificacion_mi,
            observacion_mi,
            volumen,
        )

        filas.append(fila)

    tabla = {
        "titulo": titulo,
        "tabla_referencias": info_referencia["tabla_referencias"],
        "observaciones_tabla": info_referencia["observaciones_tabla"],
        "cabeceras": cabeceras,
        "filas": filas,
    }

    return tabla