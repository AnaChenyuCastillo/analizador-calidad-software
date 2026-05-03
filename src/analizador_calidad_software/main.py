from pathlib import Path
from tkinter import messagebox

from analizador_calidad_software.cli import seleccionar_proyecto
from analizador_calidad_software.deteccion.detector_lenguaje import (
    obtener_lenguaje_principal,
    obtener_ranking_lenguajes_proyecto,
    detectar_lenguaje_proyecto
)

from analizador_calidad_software.analisis_herramientas.herramientas_java.ckjm import ejecutar_analisis_ckjm

def ejecutar_analisis_java(ruta_proyecto: Path) -> None:
    print("\n Se ha detectado que es un proyecto Java")
    print("Aqui se llamara mas adelante a los modulos de anailisi de java")
    print("Herramientas pendientes:")
    print("- CKJM")
   
    resultado_ckjm = ejecutar_analisis_ckjm(ruta_proyecto)
    print(resultado_ckjm)
    
    
    print("- CPD")
    print("- Lizard")

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
            print("Recuerda que el anlisi rapido solo analiza con pylint los 30 ficheros principales")
            return "Rapido"
        
        print("Opcion no valida. Introduce 1 o 2")

def ejecutar_analisis_python(ruta_proyecto: Path) -> None:
    modo = preguntar_modo_pyhton()

    print("\n Se ha detectado que es un proyecto pyhon")

    if modo == "Completo":
        print("Ejecutar todas las aplicaciones al completo ")
        print("Herramientas pendientes:")
        print("- Radon -> completa")
        print("- Lizard -> completa")
        print("- Pylint -> completa")


    else:
        print("Ejecutar las aplicaciones Lizard y Radon completas y pylint parcialmente")
        print("Herramientas pendientes:")
        print("- Radon -> completa")
        print("- Lizard -> completa")
        print("- Pylint -> parcial")


def ejecutar_programa() -> int:
    messagebox.showwarning(
        "Alerta",
        "Para poder analizar los proyectos Java es necesario que se detecten archivos .class, es decir que el proyecto esté compilado"
    )
    ruta_proyecto = seleccionar_proyecto()

    #lenguaje = obtener_ranking_lenguajes_proyecto(ruta_proyecto)[0][0]
    lenguaje = detectar_lenguaje_proyecto(ruta_proyecto)
    lista_lenguajes = obtener_ranking_lenguajes_proyecto(ruta_proyecto)
    
    print("\n ======INFORMACION DEL PROYECTO==========")
    print(f"Ruta del proyecto: {ruta_proyecto}")
    print(f"Lengujes principal del proyecto: {lenguaje}")
    print(f"Lista de lenguajes del proyecto: {lista_lenguajes}")

    if lenguaje == "java":
        ejecutar_analisis_java(ruta_proyecto)
        return 0
    elif lenguaje == "python":
        ejecutar_analisis_python(ruta_proyecto)
        return 0
    else:
        print("El lenguaje principal no esta registradp en el sistema, asegurese de que el proyecto es Java o Python")
        return 1