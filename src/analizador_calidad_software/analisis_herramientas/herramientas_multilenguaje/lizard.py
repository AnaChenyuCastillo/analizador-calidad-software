import sys
from pathlib import Path


from analizador_calidad_software.cli import (
    ejecutar_herramienta, 
    obtener_repo_root,
    guardar_resultado_txt
    )

def ejecutar_lizard(directorio_proyecto: Path):
    repo_root = obtener_repo_root()
    comando = [
        sys.executable,
        "-m",
        "lizard",
        str(directorio_proyecto)
    ]

    print("Comando ejecutado:")
    print(comando)

    resultado = ejecutar_herramienta(comando)

    return resultado

def generar_texto_resultado(directorio_proyeto: Path, resultado) -> str:
    lineas = []
    lineas.append("RESULTADO DE LA PRUEBA DE - LIZARD")
    lineas.append("")
    lineas.append(f"Proyecto analizado: {directorio_proyeto.name}")
    lineas.append(f"Ruta del proyecto: {directorio_proyeto}")
    lineas.append("Herramienta: Lizard")
    lineas.append("Métrica principal: Coplejidad cicloatica")
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



def ejecutar_analisis_lizard(directorio_proyecto, carpeta_resultados) -> None:
    
    print(f"Proyecto seleccionado: {directorio_proyecto}")

    resultado = ejecutar_lizard(directorio_proyecto)

    print("RETURN CODE: ", resultado.returncode)
    print("STDOUT")
    print(resultado.stdout)
    print("STDERR")
    print(resultado.stderr)

    contenido = generar_texto_resultado(directorio_proyecto, resultado)
    ruta_resultado = guardar_resultado_txt(contenido, carpeta_resultados, "lizard")
    
    print("Prueba competa correctamente")
    print(f"Archivo generado: {ruta_resultado}")

    return ruta_resultado

