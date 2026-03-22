import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def obtener_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def obtener_ruta_pmd() -> Path:
    repo_root = obtener_repo_root()
    print(repo_root)
    ruta = repo_root / "herramientas" / "cpd" / "bin" / "pmd.bat"
    

    if not ruta.exists():
        raise RuntimeError(f"No se encontró ckjm.jar en {ruta}")
    
    return ruta

def selecionar_directorio_java() -> Path:
    root = tk.Tk()
    root.withdraw()

    ruta = filedialog.askdirectory(
        title="Selecciona la carpeta raiz del proyecto java que quieres analizar"
    )

    if not ruta:
        raise RuntimeError("NO se seleccionó ninguan carpeta")
        
    return Path(ruta)

def ejecutar_cpd(directorio_proyecto: Path):
    repo_root = obtener_repo_root()
    ruta_pmd = obtener_ruta_pmd()
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
    print(comando)

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

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

def guardar_resultado_txt(contenido: str, nombre_proyecto: str) -> Path:
    repo_root = obtener_repo_root()
    carpeta_resultados =  repo_root / "pruebas_herramientas" / "resultados"
    carpeta_resultados.mkdir(parents=True, exist_ok=True)

    timestap = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ruta_fichero = carpeta_resultados / f"reultado_cpd_{nombre_proyecto}_{timestap}.txt"

    with open(ruta_fichero, "w", encoding="utf-8") as f:
        f.write(contenido)

    return ruta_fichero

def main() -> None:
    directorio_proyecto = selecionar_directorio_java()
    print(f"Proyecto selecionado: {directorio_proyecto}")

    resultado = ejecutar_cpd(directorio_proyecto)

    print("Resultado bruto de subprocess:")
    print(resultado)

    contenido = generar_texto_resultado(directorio_proyecto, resultado)
    ruta_resultado = guardar_resultado_txt(contenido, directorio_proyecto.name)

    print("Prueba competa correctamente")
    print(f"Archivo generado: {ruta_resultado}")

if __name__ == "__main__":
    main()