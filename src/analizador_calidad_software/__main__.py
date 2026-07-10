# Autor: Castillo Casado, Ana Chenyu
# 2026

from pathlib import Path
import os
import sys



if __name__ == "__main__":
    os.environ["PYTHONPATH"] = "src"
    sys.path.insert(0, "src")
    
    #from cli import obtener_repo_root
    repo_root = Path(__file__).resolve().parents[2]
    #Cuando se inicailiza nos movemos a la carpeta del proyeco y hacemos el enviroment y le indicamos donde tiene que buscar los archivos
    os.chdir(repo_root)
    
    from main import ejecutar_programa
    raise SystemExit(ejecutar_programa())