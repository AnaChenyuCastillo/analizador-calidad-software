from pathlib import Path

from analizador_calidad_software.procesar_resultados.referencias_metricas import (
    obtener_metricas_fuera_de_rango,
    referencia_ckjm
)

def construir_fila(
        clase, 
        wmc, 
        dit, 
        noc, 
        cbo, 
        rfc, 
        lcom, 
        ca, 
        npm, 
        metricas_fuera_de_rango
        ) -> list[str]:
    return [
        clase,
        wmc,
        dit,
        noc,
        cbo,
        rfc,
        lcom,
        ca,
        npm,
        metricas_fuera_de_rango
    ]



def procesar_ckjm(ruta_txt: Path, ruta_proyecto: Path, lenguaje) -> dict:
    contenido = ruta_txt.read_text(encoding="utf-8", errors="replace")
    lineas = contenido.splitlines()

    info_referencia = referencia_ckjm()
    rangos = info_referencia["rangos"]
    titulo = "Resultados CKJM"

    cabeceras = [
        "Elemente analizado",
        "WMC",
        "DIT",
        "NOC",
        "CBO",
        "RFC",
        "LCOM",
        "CA",
        "NPM",
        "Metricas fuera de rango"
    ]

    filas = []

    clase_actual = ""
    wmc = ""
    dit = ""
    noc = ""
    cbo = ""
    rfc = ""
    lcom = ""
    ca = ""
    npm = ""

    for linea in lineas:
        texto = linea.strip()

        if texto.startswith("Clase analizada"):
            if clase_actual != "":
                metricas_clase = {
                    "WMC": wmc,
                    "DIT": dit,
                    "NOC": noc,
                    "CBO": cbo,
                    "RFC": rfc,
                    "LCOM": lcom,
                    "CA": ca,
                    "NPM": npm,
                }
                metricas_fuera_de_rango = obtener_metricas_fuera_de_rango(
                    metricas= metricas_clase,
                    rangos= rangos
                )
                fila = construir_fila(
                        clase=clase_actual,
                        wmc=wmc,
                        dit=dit,
                        noc=noc,
                        cbo=cbo,
                        rfc=rfc,
                        lcom=lcom,
                        ca=ca,
                        npm=npm,
                        metricas_fuera_de_rango=metricas_fuera_de_rango,
                    )
                filas.append(fila)
            clase_actual = texto.split(":", 1)[1].strip()

            wmc = ""
            dit = ""
            noc = ""
            cbo = ""
            rfc = ""
            lcom = ""
            ca = ""
            npm = ""

        elif texto.startswith("WMC -"):
            wmc = texto.split(":", 1)[1].strip()

        elif texto.startswith("DIT -"):
            dit = texto.split(":", 1)[1].strip()

        elif texto.startswith("NOC -"):
            noc = texto.split(":", 1)[1].strip()

        elif texto.startswith("CBO -"):
            cbo = texto.split(":", 1)[1].strip()

        elif texto.startswith("RFC -"):
            rfc = texto.split(":", 1)[1].strip()

        elif texto.startswith("LCOM -"):
            lcom = texto.split(":", 1)[1].strip()

        elif texto.startswith("CA -"):
            ca = texto.split(":", 1)[1].strip()

        elif texto.startswith("NPM -"):
            npm = texto.split(":", 1)[1].strip()

    if clase_actual != "":
        metricas_clase = {
            "WMC": wmc,
            "DIT": dit,
            "NOC": noc,
            "CBO": cbo,
            "RFC": rfc,
            "LCOM": lcom,
            "CA": ca,
            "NPM": npm,
        }

        metricas_fuera_de_rango = obtener_metricas_fuera_de_rango(
            metricas=metricas_clase,
            rangos=rangos,
        )

        fila = construir_fila(
            clase=clase_actual,
            wmc=wmc,
            dit=dit,
            noc=noc,
            cbo=cbo,
            rfc=rfc,
            lcom=lcom,
            ca=ca,
            npm=npm,
            metricas_fuera_de_rango=metricas_fuera_de_rango,
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