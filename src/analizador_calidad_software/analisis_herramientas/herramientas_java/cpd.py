from pathlib import Path
import tkinter as tk


from analizador_calidad_software.cli import (
    ejecutar_herramienta, 
    obtener_ruta_herramienta,
    obtener_repo_root, 
    guardar_resultado_txt
    )

def ejecutar_cpd(directorio_proyecto: Path):
    repo_root = obtener_repo_root()
    ruta_pmd = obtener_ruta_herramienta("cpd", "pmd.bat")
    print(ruta_pmd)
    ruta_relativa_pmd = ruta_pmd.relative_to(repo_root)
    print("ruta relativa", ruta_relativa_pmd)

    comando = [
        "cmd",
        "/c",
        str(ruta_relativa_pmd),
        "cpd",
        "--minimum-tokens",
        "30",
        "--dir",
        str(directorio_proyecto),
        "--language",
        "java"
    ]
    
    resultado = ejecutar_herramienta(comando, cwd=repo_root)
    return resultado

def generar_texto_resultado(directorio_proyecto: Path, resultado) -> str:
    lineas = []
    lineas.append("RESULTADO DE PRUEBA - cpd")
    lineas.append("")
    lineas.append(f"Proyecto analizado: {directorio_proyecto.name}")
    lineas.append(f"Ruta del poyecto: {directorio_proyecto}")
    lineas.append("Lenguaje analizado: Java")
    lineas.append("Herramienta: CPD")
    lineas.append("Minimun tokens: 30") #saca por lo menos 30 lineas de codigo duplicadas
    lineas.append("")
    lineas.append(f"Codigo de salida: {resultado.returncode}")
    lineas.append("")
    lineas.append("SALIDA DE CPD:")

    if resultado.stdout.strip():
        lineas.append(resultado.stdout)
    else:
        lineas.append("No se detecto duplicacion o no hubo salida estandar")

    lineas.append("")

    if resultado.stderr.strip():
        lineas.append("ERRORES/ STDERR:")
        lineas.append(resultado.stderr)

    return "\n".join(lineas)


def ejecutar_analisis_cpd(directorio_proyecto, carpeta_resultados) :



    resultado = ejecutar_cpd(directorio_proyecto)

    print("Resultado bruto de subprocess:")
    print(resultado)

    contenido = generar_texto_resultado(directorio_proyecto, resultado)
    ruta_resultado = guardar_resultado_txt(contenido, carpeta_resultados, "cpd")

    print("Prueba competa correctamente")
    print(f"Archivo generado: {ruta_resultado}")

    return ruta_resultado

