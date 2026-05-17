from pathlib import Path
from tkinter import messagebox
from datetime import datetime
import webbrowser

from analizador_calidad_software.cli import (
    seleccionar_proyecto,
    obtener_repo_root
)
from analizador_calidad_software.deteccion.detector_lenguaje import (
    obtener_lenguaje_principal,
    obtener_ranking_lenguajes_proyecto,
    detectar_lenguaje_proyecto
)

from analizador_calidad_software.analisis_herramientas.cc_grafo.ejecutar_ciclomatico import ejectar_ciclomatico

from analizador_calidad_software.analisis_herramientas.herramientas_java.ckjm import ejecutar_analisis_ckjm
from analizador_calidad_software.analisis_herramientas.herramientas_java.cpd import ejecutar_analisis_cpd
from analizador_calidad_software.analisis_herramientas.herramientas_multilenguaje.lizard import ejecutar_analisis_lizard
from analizador_calidad_software.analisis_herramientas.herramientas_python.radon import ejecutar_analisis_radon
from analizador_calidad_software.analisis_herramientas.herramientas_python.pylint import ejecutar_analisis_pylint
from analizador_calidad_software.procesar_resultados.unificar_resultados_herramientas import unificar_resultados_herramientas
from analizador_calidad_software.generar_informe_html.generar_informe_html import generar_contenido_html

def ejecutar_analisis_java(ruta_proyecto: Path, carpeta_resultados) -> None:
    
    print("\n Se ha detectado que es un proyecto Java")
    print("Aqui se llamara mas adelante a los modulos de anailisi de java")
    print("Herramientas pendientes:")
    print("- CKJM")
   
    resultado_ckjm, calses_errores_ckjm = ejecutar_analisis_ckjm(ruta_proyecto, carpeta_resultados)
    #print(resultado_ckjm)
    
    
    print("- CPD")

    resultado_cpd = ejecutar_analisis_cpd(ruta_proyecto, carpeta_resultados)
    #print(resultado_cpd)
    print("- Lizard")

    resultado_lizard = ejecutar_analisis_lizard(ruta_proyecto, carpeta_resultados)

    resultados_herramientas = []

    if resultado_ckjm is not None:
        resultados_herramientas.append({
            "herramienta": "CKJM",
            "ruta_txt": resultado_ckjm
        })

    if resultado_cpd is not None:
        resultados_herramientas.append({
            "herramienta": "CPD",
            "ruta_txt": resultado_cpd
        })

    if resultado_lizard is not None:
        resultados_herramientas.append({
            "herramienta": "LIZARD",
            "ruta_txt": resultado_lizard
        })
    
    return resultados_herramientas, calses_errores_ckjm

def preguntar_modo_pyhton() -> str:
    print("\n Se ha detectado que es un proyecto pyhon")
    print("Seleciona el modo de analisis")
    print("1. Completo")
    print("2. Rapido")
    print("El anlisis completo puede tardar varias horas dado que analiz exahustivamente el programa con pylint")
    print("El analisis rapido tarda menos pero analiza los 30 fichero mas importarnte con pylint")

    while True:
        opcion = input("introduce 1 o 2: ").strip()

        if opcion == "1":
            print("Recuerda que el analisis completo puede tardar varias horas")
            return "Completo"
        
        if opcion == "2":
            print("Recuerda que el anlisi rapido no ejecutará la aplicación de detección de errores pylint")
            return "Rapido"
        
        print("Opcion no valida. Introduce 1 o 2")

def ejecutar_analisis_python(ruta_proyecto: Path, carpeta_resultados) -> None:
    modo = preguntar_modo_pyhton()

    resultados_herramientas = []
    resultado_radon= None
    resultado_lizard = None
    resultado_pylint = None

    print("\n Se ha detectado que es un proyecto pyhon")

    if modo == "Completo":
        print("Ejecutar todas las aplicaciones al completo ")
        print("Herramientas pendientes:")
        print("- Radon -> completa")

        resultado_radon = ejecutar_analisis_radon(ruta_proyecto, carpeta_resultados)

        print("- Lizard -> completa")

        resultado_lizard = ejecutar_analisis_lizard(ruta_proyecto, carpeta_resultados)


        print("- Pylint -> completa")

        resultado_pylint = ejecutar_analisis_pylint(ruta_proyecto, carpeta_resultados)


    else:
        print("Ejecutar las aplicaciones Lizard y Radon completas y pylint parcialmente")
        print("Herramientas pendientes:")
        print("- Radon -> completa")

        resultado_radon = ejecutar_analisis_radon(ruta_proyecto, carpeta_resultados)

        print("- Lizard -> completa")

        resultado_lizard = ejecutar_analisis_lizard(ruta_proyecto, carpeta_resultados)

    if resultado_radon is not None:
        resultados_herramientas.append({
            "herramienta": "RADON",
            "ruta_txt": resultado_radon
        })

    if resultado_lizard is not None:
        resultados_herramientas.append({
            "herramienta": "LIZARD",
            "ruta_txt": resultado_lizard
        })

    if resultado_pylint is not None:
        resultados_herramientas.append({
            "herramienta": "PYLINT",
            "ruta_txt": resultado_pylint
        })

    return resultados_herramientas


def ejecutar_programa() -> int:
    messagebox.showwarning(
        "Alerta",
        "Para poder analizar los proyectos Java es necesario que se detecten archivos .class, es decir que el proyecto esté compilado"
    )
    ruta_proyecto = seleccionar_proyecto()

    #lenguaje = obtener_ranking_lenguajes_proyecto(ruta_proyecto)[0][0]
    print("detectando lengueje")
    lenguaje = detectar_lenguaje_proyecto(ruta_proyecto)
    print(lenguaje)
    lista_lenguajes = obtener_ranking_lenguajes_proyecto(ruta_proyecto)
    contador = 1
    while lenguaje != "python" and lenguaje !="java" and contador < len(lista_lenguajes):
        lenguaje = lista_lenguajes[contador][0]
        contador = contador + 1
        print("lenguaje, contador",lenguaje, contador)

    if lenguaje != "python" and lenguaje !="java":
        print("El lenguaje principal no esta registradp en el sistema, asegurese de que el proyecto es Java o Python")
        return 1
    else:
        repo_root = obtener_repo_root()
        timestap = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        carpeta_resultados = repo_root / "src" / "analizador_calidad_software" / "analisis_herramientas" / "resultados_herramientas" / f"{ruta_proyecto.name}_{timestap}"
        carpeta_resultados.mkdir(parents=True, exist_ok=True)
        ruta_dcc =Path(ejectar_ciclomatico(ruta_proyecto, lenguaje))
        #ruta_dcc = ""

        
        print("\n ======INFORMACION DEL PROYECTO==========")
        print(f"Ruta del proyecto: {ruta_proyecto}")
        print(f"Lengujes principal del proyecto: {lenguaje}")
        print(f"Lista de lenguajes del proyecto: {lista_lenguajes}")

        errores_ckjm =[]

        if lenguaje == "java":
            resultados_herremientas, errores_ckjm = ejecutar_analisis_java(ruta_proyecto, carpeta_resultados)
            
        elif lenguaje == "python":
            resultados_herremientas = ejecutar_analisis_python(ruta_proyecto, carpeta_resultados)
        
        datos_proyecto, tablas_resultados = unificar_resultados_herramientas(ruta_proyecto.name, ruta_proyecto, resultados_herremientas, lenguaje)

        ruta_relativa_dcc = ruta_dcc.relative_to(repo_root)
        print(tablas_resultados)

        contenido_html = generar_contenido_html(datos_proyecto, tablas_resultados, ruta_dcc, errores_ckjm)
        carpeta_resultados_finales = repo_root / "src"/ "analizador_calidad_software" / "resultados"

        print("\n===== DEBUG HTML GENERADO =====")
        print("Longitud HTML:", len(contenido_html))
        print("Contiene clases.Administrador:", "clases.Administrador" in contenido_html)
        print("Contiene Resultados CKJM:", "Resultados CKJM" in contenido_html)
        print("Contiene Resultados CPD:", "Resultados CPD" in contenido_html)
        print("Contiene Resultados Lizard:", "Resultados Lizard" in contenido_html)

        ruta_html = carpeta_resultados_finales / f"Informe_calidad_{ruta_proyecto.name}_{timestap}.html"
        ruta_html.parent.mkdir(parents=True, exist_ok=True)
        ruta_html.write_text(contenido_html, encoding="utf-8")
        webbrowser.open(ruta_html.as_uri())

        print("\nResultados procesados correctamente")
        print(f"Proyecto: {datos_proyecto['nombre_proyecto']}")
        print(f"Número de tablas generadas: {len(tablas_resultados)}")
        print("Informe generado correctamente")
        