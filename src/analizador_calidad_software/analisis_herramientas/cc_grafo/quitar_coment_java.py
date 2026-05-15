#!/usr/bin/env python3
import sys
import re
import os

def remove_java_comments(code: str) -> str:
    """
    Elimina comentarios de código Java, preservando cadenas de texto.
    También limpia líneas vacías sobrantes.
    """
    pattern = re.compile(
        r'(\"(?:\\.|[^"\\])*\"|\'.*?(?<!\\)\'|/\*[\s\S]*?\*/|//[^\n]*)',
        re.MULTILINE
    )

    def replacer(match):
        text = match.group(0)
        if text.startswith("/*") or text.startswith("//"):
            return ""
        return text

    code_no_comments = re.sub(pattern, replacer, code)
    code_clean = re.sub(r'\n\s*\n+', '\n', code_no_comments)
    return code_clean.strip() + "\n"

def wrap_case_blocks(java_code):
    """
    Envuelve el contenido de cada 'case' o 'default' en llaves si no las tiene.
    """
    lines = java_code.splitlines()
    output = []
    inside_case = False
    case_indent = ""
    temp_block = []

    for line in lines:
        stripped = line.strip()

        # Detectar inicio de case o default
        if re.match(r'^(case\s+.+:|default\s*:)', stripped):
            # Si había un bloque previo, cerrarlo
            if inside_case:
                output.extend(wrap_block(temp_block, case_indent))
                temp_block.clear()

            output.append(line)
            inside_case = True
            case_indent = re.match(r'^(\s*)', line).group(1)
            continue

        # Detectar fin de bloque case por otro case/default o cierre de switch
        if inside_case and (re.match(r'^(case\s+.+:|default\s*:)', stripped) or stripped.startswith("}")):
            output.extend(wrap_block(temp_block, case_indent))
            temp_block.clear()
            inside_case = False

        # Acumular líneas dentro del case
        if inside_case:
            temp_block.append(line)
        else:
            output.append(line)

    # Si el archivo termina dentro de un case
    if inside_case:
        output.extend(wrap_block(temp_block, case_indent))

    return "\n".join(output)


def wrap_block(block_lines, indent):
    """
    Envuelve un bloque de líneas en llaves si no las tiene ya.
    """
    # Eliminar líneas vacías iniciales y finales
    while block_lines and not block_lines[0].strip():
        block_lines.pop(0)
    while block_lines and not block_lines[-1].strip():
        block_lines.pop()

    if not block_lines:
        return []

    # Si ya empieza con { y termina con }, no hacer nada
    if block_lines[0].strip().startswith("{") and block_lines[-1].strip().endswith("}"):
        return block_lines

    wrapped = [f"{indent}{{"]
    wrapped.extend(block_lines)
    wrapped.append(f"{indent}}}")
    return wrapped

def format_braces_and_indent(code: str) -> str:
    """
    Coloca cada llave en su propia línea y aplica indentación
    de 4 espacios por nivel de llaves abiertas.
    También asegura espacio antes de ';'.
    """
    # Asegurar que las llaves estén separadas por saltos de línea
    code = re.sub(r'\{', r'\n{\n', code)
    code = re.sub(r'\}', r'\n}\n', code)

    # Quitar líneas vacías múltiples
    code = re.sub(r'\n\s*\n+', '\n', code)

    lines = code.strip().split("\n")
    formatted_lines = []
    indent_level = 0

    for line in lines:
        stripped = line.strip()

        # Ajustar indentación antes de procesar
        if stripped == "}":
            indent_level = max(indent_level - 1, 0)

        # Asegurar espacio antes de ';' (fuera de cadenas)
        stripped = re.sub(r'(?<!\s);', r' ;', stripped)
        # Asegurar espacio antes de '(' (fuera de cadenas) para poder leer plabra claves que tengan pegado el parentesis. ej if(...
        stripped = re.sub(r'(?<!\s)\(', r' (', stripped)

        formatted_lines.append(" " * (indent_level * 4) + stripped)

        if stripped == "{":
            indent_level += 1

    return "\n".join(formatted_lines) + "\n"


def quitar_coment_java1(file_path, work_file):


    origen, destino = file_path, work_file

    if not os.path.isfile(origen):
        print(f"Error: El archivo '{origen}' no existe.")
        sys.exit(1)

    try:
        with open(origen, "r", encoding="utf-8") as f:
            codigo = f.read()
        codigo_sin_comentario = wrap_case_blocks(codigo)
        codigo_sin_comentarios = remove_java_comments(codigo_sin_comentario)
        codigo_formateado = format_braces_and_indent(codigo_sin_comentarios)

        with open(destino, "w", encoding="utf-8") as f:
            f.write(codigo_formateado)

        

    except Exception as e:
        print(f"Error procesando archivos: {e}")
        sys.exit(1)


if __name__ == "__main__":
    quitar_coment_java1()
