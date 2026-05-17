import subprocess
from pathlib import Path

from analizador_calidad_software.cli import (
    ejecutar_herramienta, 
    obtener_ruta_herramienta,
    obtener_repo_root
    )

def ejecutar_ckjm(proyecto: Path, clase: Path) -> tuple[subprocess.CalledProcessError, Path]:
    repo_root = obtener_repo_root()
    ruta_ckjm = obtener_ruta_herramienta("ckjm", "ckjm.jar")
    print(ruta_ckjm)

    print(proyecto)
    

    '''resultado = subprocess.run(
        ["java", "-jar", str(ruta_ckjm), str(ruta_class_relativa)],
        capture_output=True,
        text=True,
        cwd=repo_root
    )'''

    ruta_relativa =clase.relative_to(proyecto)

    print(ruta_relativa)
    print("Existe ruta relativa", ruta_relativa.exists())
    resultado = ejecutar_herramienta(["java", "-jar", str(ruta_ckjm), str(ruta_relativa)], proyecto)

    print(resultado)

    return resultado, ruta_relativa

def interpretar_salida_ckjm(salida: str, nombre_proyecto: str) -> dict:
    linea = salida.strip()

    print(f"Esta es la salida {salida}")
    print("Esta es la linea", linea)

    if not linea:
        raise RuntimeError("CKJM no devolvió ninguna salida.")

    partes = linea.split()
    print("Estas son las partes",partes)

    if len(partes) != 9:
        raise RuntimeError(f"La salida de ckjm no tiene el formato esperado: \n {salida}")
    
    salida_metodo = {
        "Nombre" : nombre_proyecto,
        "Clase" : partes[0],
        "WMC": partes[1],
        "DIT": partes[2],
        "NOC": partes[3],
        "CBO": partes[4],
        "RFC": partes[5],
        "LCOM": partes[6],
        "CA": partes[7],
        "NPM": partes[8],
    }

    print("esta es la salida del metodo", salida_metodo)
    
    return salida_metodo

def generar_texto_resultado(metricas: dict) -> str:
    print("Las métrocas son:", metricas)
    texto = []
    texto.append("")
    texto.append(f"Clase analizada: {metricas['Clase']}")
    texto.append("")
    texto.append(f"WMC - Metodos ponderados por clase: {metricas['WMC']}")
    texto.append(f"DIT - Profundidad del arbol de herencia: {metricas['DIT']}")
    texto.append(f"NOC - Numero de clases hijas : {metricas['NOC']}")
    texto.append(f"CBO - Acoplamiento entre clases: {metricas['CBO']}")
    texto.append(f"RFC - COnjunto de respuesta de la clase: {metricas['RFC']}")
    texto.append(f"LCOM - Falta de cohesion en metodos: {metricas['LCOM']}")
    texto.append(f"CA - Acoplamiento aferente: {metricas['CA']}")
    texto.append(f"NPM - Numero de metodos publicos: {metricas['NPM']}")


    return "\n".join(texto)

def guardar_resultado_txt(contenido: str, carpeta_resultados) -> Path:
    

    
    nombre_fichero = f"resultado_ckjm.txt"

    print(carpeta_resultados / nombre_fichero)
    

    with open(carpeta_resultados / nombre_fichero, "w", encoding="utf-8") as fichero:
        fichero.write(contenido)

    ruta_fichero = carpeta_resultados / nombre_fichero
    print("El fichero esta creado:", ruta_fichero.exists(), ruta_fichero)

   

    return ruta_fichero


def buscar_clases_compiladas(ruta_proyecto: Path) -> list[Path]:
    clases = []

    for ruta in ruta_proyecto.rglob("*.class"):
        if ruta.is_file():
            clases.append(ruta)

    return clases



def ejecutar_analisis_ckjm(ruta_proyecto: Path, carpeta_resultados) -> None:
    clases = buscar_clases_compiladas(ruta_proyecto)

    if not clases:
        raise RuntimeError(
            "No se han encontrado archivos .class en el proyecto seleccionado."
        )

    bloques = []
    bloques.append("RESULTADO COMPLETO DE CKJM")
    bloques.append(f"Proyecto analizado: {ruta_proyecto.name}")
    bloques.append(f"Ruta del proyecto: {ruta_proyecto}")
    bloques.append(f"Número de clases analizadas: {len(clases)}")
    bloques.append("")
    clases_errores = []

    for ruta_class in clases:
        resultado, ruta_relativa = ejecutar_ckjm(ruta_proyecto, ruta_class)


        proyecto = ruta_relativa
        print(resultado)
        if resultado.stdout.strip()!= "":
            bloque_salida = interpretar_salida_ckjm(resultado.stdout, proyecto.name)

            bloque = generar_texto_resultado(bloque_salida)

            bloques.append(bloque)
        else: 
            clases_errores.append(str(ruta_relativa))

    contenido_final = "\n".join(bloques)
    ruta_txt = guardar_resultado_txt(contenido_final, carpeta_resultados)

    return ruta_txt, clases_errores