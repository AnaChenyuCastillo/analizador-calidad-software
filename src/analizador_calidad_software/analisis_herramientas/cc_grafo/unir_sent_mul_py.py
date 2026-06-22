import os
import subprocess
import io
import tokenize
import sys
def unir_sentencias_multilinea_python(myfile) :
    """
    Recibe el contenido completo de un programa Python y devuelve el programa
    uniendo en una sola línea las sentencias multilínea.
    """
    with open(myfile, "r", encoding="utf-8") as f:
            texto = f.read()

    tokens = list(tokenize.generate_tokens(io.StringIO(texto).readline))

    resultado = []
    sentencia = []
    indentacion_actual = ""

    nivel_parentesis = 0
    dentro_sentencia = False

    def normalizar_fragmentos(fragmentos):
        """
        Une fragmentos de una sentencia en una sola línea,
        respetando una separación mínima entre tokens.
        """
        partes = []

        for frag in fragmentos:
            if frag is None:
                continue

            frag = frag.strip()

            if not frag:
                continue

            partes.append(frag)

        if not partes:
            return ""

        linea = " ".join(partes)

        # Limpieza estética básica.
        reemplazos = [
            (" (", "("),
            (" )", ")"),
            (" [", "["),
            (" ]", "]"),
            (" {", "{"),
            (" }", "}"),
            (" ,", ","),
            (" :", ":"),
            (" ;", ";"),
            (" . ", "."),
            (" = ", " = "),
        ]

        for viejo, nuevo in reemplazos:
            linea = linea.replace(viejo, nuevo)

        return linea

    def volcar_sentencia():
        nonlocal sentencia, dentro_sentencia

        if not sentencia:
            return

        indent = sentencia[0][0]
        fragmentos = [x[1] for x in sentencia]
        linea = normalizar_fragmentos(fragmentos)

        if linea:
            resultado.append(indent + linea)

        sentencia = []
        dentro_sentencia = False

    for tok in tokens:
        tok_type = tok.type
        tok_str = tok.string
        start_line = tok.start[0]
        start_col = tok.start[1]
        line_text = tok.line

        if tok_type == tokenize.ENCODING:
            continue

        if tok_type == tokenize.ENDMARKER:
            volcar_sentencia()
            break

        if tok_type == tokenize.INDENT:
            indentacion_actual = tok_str
            continue

        if tok_type == tokenize.DEDENT:
            volcar_sentencia()
            indentacion_actual = ""
            continue

        if tok_type in (tokenize.NL, tokenize.NEWLINE):
            if nivel_parentesis == 0:
                volcar_sentencia()
            continue

        if tok_type == tokenize.COMMENT:
            # Comentario en línea propia.
            if not dentro_sentencia and line_text[:start_col].strip() == "":
                resultado.append(line_text.rstrip())
                continue

            # Comentario al final de una sentencia.
            # Lo conservamos como parte de la sentencia.
            if not dentro_sentencia:
                indentacion = line_text[:start_col]
                sentencia.append((indentacion, tok_str))
                dentro_sentencia = True
            else:
                sentencia.append(("", tok_str))

            continue

        if tok_type in (tokenize.NL,):
            continue

        if tok_str in ("(", "[", "{"):
            nivel_parentesis += 1
        elif tok_str in (")", "]", "}"):
            nivel_parentesis -= 1

        if not dentro_sentencia:
            indentacion = line_text[:start_col]
            sentencia.append((indentacion, tok_str))
            dentro_sentencia = True
        else:
            sentencia.append(("", tok_str))
    resultado="\n".join(resultado) + "\n"
    with open("C:\\tfg\\analizador-calidad-software-main\\pruebas_herramientas\\resultados\\py_multi_tratado.txt", "w", encoding="utf-8") as f:
            f.write(resultado)
    return 

if __name__ == "__main__":
    myfile = sys.argv[1]
    unir_sentencias_multilinea_python(myfile)
