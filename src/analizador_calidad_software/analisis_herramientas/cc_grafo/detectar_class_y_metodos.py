#!/usr/bin/env python3
import argparse
import bisect
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ClaseInfo:
    nombre: str
    pos_decl: int
    pos_llave: int
    pos_cierre: int
    profundidad: int



@dataclass
class MetodoInfo:
    nombre: str
    clase: str
    pos_decl: int


PALABRAS_CONTROL = {
    "if", "else", "for", "while", "switch", "catch", "try",
    "do", "synchronized", "return", "new"
}


def enmascarar_strings_y_comentarios(codigo: str) -> str:
    """
    Sustituye strings, chars y comentarios por espacios,
    manteniendo saltos de línea y posiciones.
    """
    res = list(codigo)
    i = 0
    n = len(codigo)

    while i < n:
        if codigo.startswith("//", i):
            j = codigo.find("\n", i + 2)
            if j == -1:
                j = n
            for k in range(i, j):
                res[k] = " "
            i = j
            continue

        if codigo.startswith("/*", i):
            j = codigo.find("*/", i + 2)
            if j == -1:
                j = n - 2
            j += 2

            for k in range(i, j):
                if res[k] != "\n":
                    res[k] = " "

            i = j
            continue

        if codigo[i] in ("'", '"'):
            quote = codigo[i]
            res[i] = " "
            i += 1

            while i < n:
                if codigo[i] == "\\":
                    if codigo[i] != "\n":
                        res[i] = " "
                    if i + 1 < n and codigo[i + 1] != "\n":
                        res[i + 1] = " "
                    i += 2
                    continue

                if codigo[i] == quote:
                    res[i] = " "
                    i += 1
                    break

                if codigo[i] != "\n":
                    res[i] = " "

                i += 1

            continue

        i += 1

    return "".join(res)


def calcular_lineas(codigo: str):
    starts = [0]

    for i, c in enumerate(codigo):
        if c == "\n":
            starts.append(i + 1)

    return starts


def linea_de_posicion(line_starts, pos: int) -> int:
    return bisect.bisect_right(line_starts, pos) - 1


def calcular_llaves(codigo_limpio: str):
    pila = []
    pares = {}
    profundidad_antes = {}
    profundidad = 0

    for i, c in enumerate(codigo_limpio):
        if c == "{":
            profundidad_antes[i] = profundidad
            pila.append(i)
            profundidad += 1

        elif c == "}":
            profundidad -= 1

            if pila:
                apertura = pila.pop()
                pares[apertura] = i

    return pares, profundidad_antes


def encontrar_clases(codigo_limpio: str, pares_llaves, profundidad_antes):
    clases = []

    patron = re.compile(
        r"\b(class|interface|enum|record)\s+([A-Za-z_$][A-Za-z0-9_$]*)\b"
    )

    for m in patron.finditer(codigo_limpio):
        nombre = m.group(2)
        pos_llave = codigo_limpio.find("{", m.end())

        if pos_llave == -1:
            continue

        if pos_llave not in pares_llaves:
            continue

        clases.append(
            ClaseInfo(
                nombre=nombre,
                pos_decl=m.start(),
                pos_llave=pos_llave,
                pos_cierre=pares_llaves[pos_llave],
                profundidad=profundidad_antes.get(pos_llave, 0)
            )
        )

    return clases


def clase_actual(clases, pos: int):
    candidatas = [
        c for c in clases
        if c.pos_llave < pos < c.pos_cierre
    ]

    if not candidatas:
        return None

    return max(candidatas, key=lambda c: c.pos_llave)


def buscar_inicio_de_declaracion(codigo_limpio: str, pos_llave: int) -> int:
    i = pos_llave - 1

    while i >= 0:
        if codigo_limpio[i] in ";{}":
            return i + 1
        i -= 1

    return 0


def encontrar_parentesis_apertura(codigo_limpio: str, pos_cierre: int) -> int:
    profundidad = 0
    i = pos_cierre

    while i >= 0:
        if codigo_limpio[i] == ")":
            profundidad += 1
        elif codigo_limpio[i] == "(":
            profundidad -= 1

            if profundidad == 0:
                return i

        i -= 1

    return -1


def extraer_identificador_antes(codigo_limpio: str, pos: int):
    i = pos - 1

    while i >= 0 and codigo_limpio[i].isspace():
        i -= 1

    fin = i + 1

    while i >= 0 and (codigo_limpio[i].isalnum() or codigo_limpio[i] in "_$"):
        i -= 1

    inicio = i + 1

    if inicio == fin:
        return None, None, None

    return codigo_limpio[inicio:fin], inicio, fin


def palabra_anterior(codigo_limpio: str, pos: int):
    return extraer_identificador_antes(codigo_limpio, pos)[0]


def es_declaracion_metodo(codigo_limpio: str, pos_llave: int, clase: ClaseInfo, profundidad_antes):
    profundidad = profundidad_antes.get(pos_llave)

    if profundidad is None:
        return None

    # Método o constructor directamente dentro de la clase.
    if profundidad != clase.profundidad + 1:
        return None

    inicio = buscar_inicio_de_declaracion(codigo_limpio, pos_llave)
    cabecera = codigo_limpio[inicio:pos_llave].strip()

    if not cabecera:
        return None

    if re.search(r"\b(class|interface|enum|record)\b", cabecera):
        return None

    pos_cierre_parentesis = codigo_limpio.rfind(")", inicio, pos_llave)

    if pos_cierre_parentesis == -1:
        return None

    pos_apertura_parentesis = encontrar_parentesis_apertura(
        codigo_limpio,
        pos_cierre_parentesis
    )

    if pos_apertura_parentesis == -1 or pos_apertura_parentesis < inicio:
        return None

    nombre, inicio_nombre, _ = extraer_identificador_antes(
        codigo_limpio,
        pos_apertura_parentesis
    )

    if not nombre:
        return None

    if nombre in PALABRAS_CONTROL:
        return None

    previa = palabra_anterior(codigo_limpio, inicio_nombre)

    if previa == "new":
        return None

    j = inicio_nombre - 1
    while j >= 0 and codigo_limpio[j].isspace():
        j -= 1

    if j >= 0 and codigo_limpio[j] == ".":
        return None

    # Constructor.
    if nombre == clase.nombre:
        return nombre, inicio_nombre

    antes_nombre = codigo_limpio[inicio:inicio_nombre].strip()

    antes_sin_anotaciones = re.sub(
        r"@\w+(?:\s*\([^)]*\))?\s*",
        "",
        antes_nombre
    ).strip()

    if not antes_sin_anotaciones:
        return None

    return nombre, inicio_nombre

def inicio_de_linea(codigo: str, pos: int) -> int:
    """
    Devuelve la posición del primer carácter de la línea donde está pos.
    """
    while pos > 0 and codigo[pos - 1] != "\n":
        pos -= 1

    return pos

def encontrar_metodos(codigo_limpio: str, clases, profundidad_antes):
    metodos = []

    for pos, c in enumerate(codigo_limpio):
        if c != "{":
            continue

        clase = clase_actual(clases, pos)

        if clase is None:
            continue

        resultado = es_declaracion_metodo(
            codigo_limpio,
            pos,
            clase,
            profundidad_antes
        )

        if resultado:
            nombre, inicio_nombre = resultado

            # La marca se pone en la línea donde aparece el nombre real del método.
            # Esto evita que se inserte en la llave de cierre del método anterior
            # cuando hay anotaciones como @SuppressWarnings.
            inicio_decl = inicio_de_linea(codigo_limpio, inicio_nombre)

            metodos.append(
                MetodoInfo(
                    nombre=nombre,
                    clase=clase.nombre,
                    pos_decl=inicio_decl
                )
            )

    return metodos


def anteponer_marcas(codigo: str) -> str:
    limpio = enmascarar_strings_y_comentarios(codigo)
    line_starts = calcular_lineas(codigo)

    pares_llaves, profundidad_antes = calcular_llaves(limpio)

    clases = encontrar_clases(
        limpio,
        pares_llaves,
        profundidad_antes
    )

    metodos = encontrar_metodos(
        limpio,
        clases,
        profundidad_antes
    )

    marcas_por_linea = {}

    # Marcar clases.
    for clase in clases:
        linea = linea_de_posicion(line_starts, clase.pos_decl)

        marcas_por_linea.setdefault(linea, []).append(
            f"clase {clase.nombre}"
        )

    # Marcar métodos.
    # La numeración se hace por clase y nombre.
    contador_metodos = {}

    for metodo in metodos:
        clave = (metodo.clase, metodo.nombre)
        contador_metodos[clave] = contador_metodos.get(clave, 0) + 1

        num = contador_metodos[clave]

        if num == 1:
            nombre_marcado = f"{metodo.clase}.{metodo.nombre}"
        else:
            nombre_marcado = f"{metodo.clase}.{metodo.nombre}#{num}"

        linea = linea_de_posicion(line_starts, metodo.pos_decl)

        marcas_por_linea.setdefault(linea, []).append(
            f"metodo {nombre_marcado}"
        )

    lineas = codigo.splitlines(keepends=True)
    salida = []

    for i, linea in enumerate(lineas):
        if i in marcas_por_linea:
            prefijo = " ".join(marcas_por_linea[i])
            salida.append(prefijo + " " + linea)
        else:
            salida.append(linea)

    return "".join(salida)


def procesar_fichero(ruta_entrada: Path):
    """
    Lee el fichero Java, lo procesa y sobrescribe el mismo fichero.

    ruta_entrada debe ser un pathlib.Path.
    """
    ruta_entrada = Path(ruta_entrada)

    with ruta_entrada.open("r", encoding="utf-8") as f:
        codigo = f.read()

    resultado = anteponer_marcas(codigo)

    with ruta_entrada.open("w", encoding="utf-8") as f:
        f.write(resultado)

from pathlib import Path


def detect_class_met(fichero: Path):
    """
    Recibe un Path, procesa el fichero Java y sobrescribe el mismo fichero.
    Devuelve el Path procesado.
    """

    fichero = Path(fichero)

    procesar_fichero(fichero)

    return fichero

