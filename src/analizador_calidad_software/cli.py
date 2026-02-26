import sys
import subprocess
import shutil
from pathlib import Path


def asegurar_cloc_instalado() -> None:
    #Comprueba si la aplicacón cloc está disponible en el sistema.
    #Si no lo está, intetará instalarlo automáticamente

    #Primero comprobamos si la aplicación Cloc esta instalada y para ello utlizamos el comando hutil.which que retorna la ruta del ejecutable
    if shutil.which("cloc") is not None:
        return


    print("La aplicación Cloc no está instalada. Intentando instalarlo automáticamente...")

    #A continuación se iintetará instalar la aplicación cloc

    try: 
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "cloc"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        #
        print("La instalación ha fallado")
        if e.stderr:
            print(e.stderr.strip())

    #Volcemos a comprobar si la aplicación cloc está instalada
    if shutil.which("cloc") is not None:
        print("La aplicación cloc ya está disponible")
        return
    
    #Si la comprobación falla es que la instalación ha fallado, entonces mandamos un mensaje 
    #de que la aplicación no se ha podido instalar y que para continuar tiene que instalarla
    raise RuntimeError(
        "No se pudo instalar 'cloc' automáticamente. "
        "Instálalo manualmente (por ejemplo con Chocolatey o Scoop) "
        "o añade 'cloc' al PATH."
    )


def main() -> int:
    # 1) Validación: comprobar que el usuario ha pasado una ruta
    if len(sys.argv) < 2:
        print("Uso: python -m analizador_calidad_software.cli <ruta_proyecto>")
        return 1

    # 2) Convertir el argumento a una ruta y validar que existe
    ruta = Path(sys.argv[1])

    if not ruta.exists():
        print("Error: la ruta indicada no existe.")
        return 1
    
    asegurar_cloc_instalado()

    if ruta.is_dir():
        print(f"Analizando directorio: {ruta.resolve()}")
    elif ruta.is_file():
        print(f"Analizando fichero: {ruta.resolve()}")
    else:
        print("Error: la ruta indicada no es válida.")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
