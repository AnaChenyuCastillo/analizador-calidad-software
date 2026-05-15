from pathlib import Path
import os
import sys
from main import ejecutar_programa
from cli import obtener_repo_root



if __name__ == "__main__":
    repo_root = Path(obtener_repo_root()).resolve()
    #Cuando se inicailiza nos movemos a la carpeta del proyeco y hacemos el enviroment y le indicamos donde tiene que buscar los archivos
    os.chdir(repo_root)
    src_path = repo_root / "src"
    os.environ["PYTHONPATH"] = str(src_path)
    sys.path.insert(0, str(src_path))
    
    raise SystemExit(ejecutar_programa())