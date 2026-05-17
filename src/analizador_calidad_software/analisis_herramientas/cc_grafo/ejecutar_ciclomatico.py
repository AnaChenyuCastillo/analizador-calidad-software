import subprocess
import sys
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfWriter
from pathlib import Path

from analizador_calidad_software.cli import (
    obtener_repo_root
)
from analizador_calidad_software.analisis_herramientas.cc_grafo.ciclo_java import flujo_grafos_java
from analizador_calidad_software.analisis_herramientas.cc_grafo.ciclo_python import flujo_grafos_python

'''def listar_archivos_por_extension1(directorio, extension):
    """
    Lista todos los archivos con una extensión específica en un directorio (no recursivo).
    
    Args:
        directorio (str): Ruta del directorio.
        extension (str): Extensión de archivo (ej. '.txt', '.jpg').
    
    Returns:
        list: Lista de rutas completas de archivos que coinciden.
    """
    if not os.path.isdir(directorio):
        raise ValueError(f"La ruta '{directorio}' no es un directorio válido.")

    # Normalizamos la extensión para que siempre empiece con '.'
    if not extension.startswith('.'):
        extension = '.' + extension

    archivos = [
        os.path.join(directorio, f)
        for f in os.listdir(directorio)
        if os.path.isfile(os.path.join(directorio, f)) and f.lower().endswith(extension.lower())]
    return archivos'''

def listar_archivos_por_extension(directorio, extension):
    archivos = []  # Lista donde se guardan los archivos encontrados

    # Iterar sobre los elementos del directorio actual
    for elemento in os.listdir(directorio):
        ruta_completa = os.path.join(directorio, elemento)

        # Si es un directorio, llamar recursivamente
        if os.path.isdir(ruta_completa):
            archivos.extend(listar_archivos_por_extension(ruta_completa, extension))
        # Si es un archivo y tiene la extensión deseada, agregarlo a la lista
        elif os.path.isfile(ruta_completa) and ruta_completa.endswith(extension):
            archivos.append(ruta_completa)

    return archivos

def ejectar_ciclomatico(ruta_directorio, lenguaje: str):
    try:
        # Seleccionar carpeta

        if not ruta_directorio:
            print("No se seleccionó ningún directorio.")
        else:
            if lenguaje.lower() == "java":
            # seleccionar archivos *.java
                extension_buscada = ".java"
                lista_archivos = listar_archivos_por_extension(ruta_directorio, extension_buscada)
                print("Carpeta seleccionada:",ruta_directorio)
                print(f"\nArchivos encontrados con extensión '{extension_buscada}':")

                for archivo in lista_archivos:
                    print(f'archivo->{archivo}')
                #lista_archivos = [ruta.replace("/", "//") for ruta in lista_archivos]
                lista_archivos = [ruta.replace("\\", "/") for ruta in lista_archivos]           

                print(f"\nTotal: {len(lista_archivos)} archivo(s) encontrado(s).")
            elif lenguaje.lower() == "python":
                # seleccionar archivos *.py 
                extension_buscada = ".py"
                lista_archivos = listar_archivos_por_extension(ruta_directorio, extension_buscada)
                print("Carpeta seleccionada:",ruta_directorio)
                print(f"\nArchivos encontrados con extensión '{extension_buscada}':")

                for archivo in lista_archivos:
                    print(f'archivo->{archivo}')
                #lista_archivos = [ruta.replace("/", "//") for ruta in lista_archivos]
                lista_archivos = [ruta.replace("\\", "/") for ruta in lista_archivos]           

                print(f"\nTotal: {len(lista_archivos)} archivo(s) encontrado(s).")
    except Exception as e:
        print(f"Error: {e}")

    T_grafos_files=[]
    #llamada a ciclomatico2 con lista de archivos   
    for archivo in lista_archivos:
        
        try:
            # Ejecuta ciclomatico2 
            
            repo_root = obtener_repo_root()
            print(repo_root)
            print(lenguaje)
            ext_pdf=""
            if lenguaje.lower() == "java":
                ext_pdf="_java.pdf"
                ruta = flujo_grafos_java(archivo)
            elif lenguaje.lower() == "python":
                ext_pdf="_py.pdf"
                ruta = flujo_grafos_python(archivo)
            
            if ruta is not None:
                print(f"Datos encontrados: {ruta}")
                T_grafos_files.append(ruta)
            else:
                print("No se encontró ninguna línea que empiece con 'grafo_file:'")
        
            #print("Salida del otro script:",x,result.stdout)
            print("Salida del otro script:")
           

        except subprocess.CalledProcessError as e:
            print("Error al ejecutar el script:", e.stderr)

    #fusionar pdf's
    fusionador = PdfWriter()
    for pdf in T_grafos_files:
        fusionador.append(pdf)
        os.remove(pdf)

    marca_tiempo=datetime.today().strftime("%Y%m%d%H%M%S")
    nombre_arc=(os.path.basename(os.path.normpath(ruta_directorio)))+"_"+marca_tiempo+ext_pdf
    nombre_archivo= repo_root / "src"/ "analizador_calidad_software" / "resultados" / nombre_arc
    fusionador.write(nombre_archivo)
    fusionador.close() 
    print(f'Generados en pdf:{nombre_archivo}') 
   
    
    return nombre_archivo
