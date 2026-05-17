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

def seleccionar_directorio():
    """Abre un cuadro de diálogo para seleccionar un directorio."""
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    carpeta = filedialog.askdirectory(title="Selecciona un directorio")
    return carpeta

def listar_archivos_por_extension(directorio, extension):
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
    return archivos



if __name__ == "__main__":
    try:
        # Seleccionar carpeta
        ruta_directorio = seleccionar_directorio()
        if not ruta_directorio:
            print("No se seleccionó ningún directorio.")
        else:
            
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
            ruta = repo_root / "src" / "analizador_calidad_software" / "analisis_herramientas" / "cc_grafo" / "ciclo_python.py"
            result = subprocess.run(
                [sys.executable, str(ruta) ,archivo],capture_output=True,text=True,check=True)
            datos = None
            for linea in result.stdout.splitlines():
                linea = linea.strip()  # Quitar espacios y saltos de línea
                if linea.lower().startswith("grafo_file:"):
                    # Extraer lo que viene después de "grafo_file:"
                    datos = linea.split(":", 1)[1].strip()
                    break  
            if datos is not None:
                print(f"Datos encontrados: {datos}")
                T_grafos_files.append(datos)
            else:
                print("No se encontró ninguna línea que empiece con 'grafo_file:'")
        
            #print("Salida del otro script:",x,result.stdout)
            print("Salida del otro script:")
            print(result.stdout)

        except subprocess.CalledProcessError as e:
            print("Error al ejecutar el script:", e.stderr)

    #fusionar pdf's
    fusionador = PdfWriter()
    for pdf in T_grafos_files:
        fusionador.append(pdf)
        os.remove(pdf)

    marca_tiempo=datetime.today().strftime("%Y%m%d%H%M%S")
    nombre_arc=(os.path.basename(os.path.normpath(ruta_directorio)))+"_"+marca_tiempo+"_py.pdf"
    nombre_archivo= repo_root / "pruebas_herramientas" / "resultados" / nombre_arc
    fusionador.write(nombre_archivo)
    fusionador.close() 
    print(f'Generados en pdf:{nombre_archivo}') 
   
    

