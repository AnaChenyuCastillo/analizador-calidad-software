import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def obtener_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def obtener_ruta_ckjm() -> Path:
    repo_root = obtener_repo_root()
    print(repo_root)
    ruta = repo_root / "herramientas" / "ckjm" / "ckjm.jar"
    

    if not ruta.exists():
        raise RuntimeError(f"No se encontró ckjm.jar en {ruta}")
    
    return ruta

def selecionar_class() -> Path:
    print("Selecionando clase:")
    root = tk.Tk()
    root.withdraw()
    print("Abriendo ventana para seleccionar clase")

    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo .class para analizar con CKJM",
        filetypes=[("Java class files", "*.class")]
    )

    print("Valor de ruta", ruta)

    print("Tipo de ruta", type(ruta))

    if not ruta:
        raise RuntimeError("No se selecionó ningún archivo .class")
    
    return Path(ruta)

def ejecutar_ckjm(ruta_class: Path) -> subprocess.CalledProcessError:
    repo_root = obtener_repo_root()
    ruta_ckjm = obtener_ruta_ckjm()
    print(ruta_ckjm)

    print(ruta_class)

    ruta_class_relativa = ruta_class.relative_to(repo_root)

    resultado = subprocess.run(
        ["java", "-jar", str(ruta_ckjm), str(ruta_class_relativa)],
        capture_output=True,
        text=True,
        cwd=repo_root
    )

    print(resultado)

    return resultado

def interpretar_salida_ckjm(salida: str) -> dict:
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
    texto.append("Resultadode prueba CKJM")
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

def guardar_resultado_txt(contenido: str) -> Path:
    repo_root = obtener_repo_root()
    carpeta_resultados = repo_root / "pruebas_herramientas" / "resultados"
    carpeta_resultados.mkdir(parents=True, exist_ok=True)


    timestap = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_fichero = f"resultado_ckjm_{timestap}.txt"

    with open(carpeta_resultados / nombre_fichero, "w") as fichero:
        fichero.write(contenido)
    ruta_fichero = carpeta_resultados / nombre_fichero

   

    return ruta_fichero



def main() -> None:
    ruta_class = selecionar_class()

    print("clase seleccionada")

    resultado = ejecutar_ckjm(ruta_class)

    print(resultado.returncode)
    print(f"Este es el resultado {resultado.stderr}")

    if resultado.returncode != 0:
        print("Error al ejecutar ckjm:")
        print(resultado.stderr)
        return
    
    metricas = interpretar_salida_ckjm(resultado.stdout)

    contenido = generar_texto_resultado(metricas)

    ruta_resultado = guardar_resultado_txt(contenido)

    print("Prueba completada correctamente.")
    print(f"Archivo generado: {ruta_resultado}")
    print(f"Ruta absoluta: {ruta_resultado.resolve()}")


if __name__ == "__main__":
    main()