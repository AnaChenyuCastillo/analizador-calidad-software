import re
import sys
import os
from pathlib import Path

def detect_class_met(entrada: str):
   
    archivo_entrada = str(entrada) 

    archivo_salida = str(entrada) + "cop"
    
   
    """
    Procesa un archivo Java para detectar clases, métodos y constructores.
    Antepone 'class <nombre>' o 'metodo <nombre>' según corresponda.
    Mantiene la indentación original.
    """
    # Detecta clases
    patron_clase = re.compile(r'^(\s*)(?:public\s+|private\s+|protected\s+)?class\s+(\w+)')

    # Detecta métodos con tipo de retorno
    patron_metodo = re.compile(
    r'^(\s*)(?!else\s+if\s*\()'                 # (1) Espacios iniciales y NEGACIÓN de "else if" con espacios variables
    r'(?:public\s+|private\s+|protected\s+)?'    # (2) Modificador de acceso opcional
    r'(?:static\s+)?'                            # (3) 'static' opcional
    r'[\w\<\>\[\]]+'                             # (4) Tipo de retorno
    r'\s+'                                       # (5) Espacio obligatorio
    r'(\w+)'                                     # (6) Nombre del método
    r'\s*\([^)]*\)'                              # (7) Lista de parámetros
    r'\s*'                                       # (8) Espacios opcionales
    r'(?:throws\s+\w+(?:\s*,\s*\w+)*)?'          # (9) Cláusula throws opcional
    r'\s*\{?',                                   # (10) Llave de apertura opcional
    re.IGNORECASE                                # Ignorar mayúsculas/minúsculas
    )


     

    # Detecta constructores (nombre igual al de la clase, sin tipo de retorno)
    patron_constructor = re.compile(
        r'^(\s*)(?:public\s+|private\s+|protected\s+)?([A-Z]\w*)\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{?'
    )

    nombre_clase_actual = None

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f_in , open(archivo_salida, 'w', encoding='utf-8') as f_out:

            for linea in f_in:
                # Detectar clase
                match_clase = patron_clase.match(linea)
                if match_clase:
                    indent, nombre = match_clase.groups()
                    nombre_clase_actual = nombre
                    nueva_linea = f"{indent}class {nombre} {linea.lstrip()}"
                    f_out.write(nueva_linea)
                    continue

                # Detectar constructor (solo si coincide con la clase actual)
                match_constructor = patron_constructor.match(linea)
                if match_constructor:
                    indent, nombre = match_constructor.groups()
                    if nombre_clase_actual == nombre:
                        nueva_linea = f"{indent}metodo {nombre} {linea.lstrip()}"
                        f_out.write(nueva_linea)
                        continue

                # Detectar método normal
                match_metodo = patron_metodo.match(linea)
                if match_metodo:
                    indent, nombre = match_metodo.groups()
                    nueva_linea = f"{indent}metodo {nombre} {linea.lstrip()}"
                    f_out.write(nueva_linea)
                    continue

                # Si no es clase, método o constructor, escribir igual
                f_out.write(linea)
        


    except FileNotFoundError:
        print(f"Error: Detect class.No se encontró el archivo {archivo_entrada}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    f_out.close()
    f_in.close()
    
    os.remove(archivo_entrada)
    os.rename(archivo_salida,entrada)
    


if __name__ == "__main__":
    # Ejemplo de uso: python script.py entrada.java salida.txt
    if len(sys.argv) != 2:
        print("Uso: python script.py <archivo_entrada.java> <archivo_salida.txt>")
        sys.exit(1)

    archivo_entrada = Path(sys.argv[1]+"cop")
    archivo_salida =  Path(sys.argv[1])
    
    detect_class_met(str(archivo_entrada))
