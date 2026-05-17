from pathlib import Path
import os
import sys




if __name__ == "__main__":
    os.environ["PYTHONPATH"] = "src"
    sys.path.insert(0, "src")
    from main import ejecutar_programa
    from cli import obtener_repo_root
    repo_root = Path(obtener_repo_root()).resolve()
    #Cuando se inicailiza nos movemos a la carpeta del proyeco y hacemos el enviroment y le indicamos donde tiene que buscar los archivos
    os.chdir(repo_root)
    
    raise SystemExit(ejecutar_programa())