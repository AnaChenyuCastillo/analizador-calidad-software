import re
import sys
import os

def remove_comments_from_code(code: str) -> str:
    """
    Elimina comentarios de un código Python:
    - Comentarios de línea que empiezan con #
    - Comentarios multilínea con ''' o 
    """
    #Eliminar comentarios multilínea (triple comillas simples o dobles)
  
    pattern = r"\"\"\"[\s\S]*?\"\"\""
    code= re.sub(pattern, "", code)
    
    pattern = r"'''[\s\S]*?'''"
    code = re.sub(pattern, '', code)

    # Eliminar comentarios de línea (pero no dentro de strings)
    code = re.sub(r'(?m)(?<!["\'])#.*$', '', code)
    
    # Eliminar espacios en dos puntos :
    code = re.sub(r'\s*:', ':', code)

    return code


def process_file(input_path: str, output_path: str):
    """Lee un archivo, elimina comentarios y guarda el resultado."""
    if not os.path.isfile(input_path) :  
        print(f"Error: El archivo '{input_path}' no existe.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()

        cleaned_code = remove_comments_from_code(code)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)

        print(f"Comentarios eliminados. Archivo limpio guardado en: {output_path}")

    except Exception as e:
        print(f"Error procesando el archivo: {e}")


def ejecutar_quitar_comentario(file_path, work_file):

    process_file(file_path, work_file)
