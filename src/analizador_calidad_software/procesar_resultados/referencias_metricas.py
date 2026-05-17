from pathlib import Path

def referencia_ckjm() -> dict:
    return {
        "tabla_referencias": (
            "Los rangos se basan únicamente en bibliografía con respaldo identificado. "
            "Cuando no existe un umbral concreto con suficiente respaldo, se deja sin especificar."
        ),
        "observaciones_tabla": (
            "Las métricas de CKJM deben interpretarse según el contexto del proyecto. "
            "Los umbrales no son universales y no sustituyen al análisis del proyecto."
        ),
        "referencias_metricas": {
            "WMC": {
                "nombre": "Métodos ponderados por clase",
                "mide": "Cantidad y complejidad de los métodos definidos en una clase.",
                "min": None,
                "max": 20,
            },
            "DIT": {
                "nombre": "Profundidad del árbol de herencia",
                "mide": "Nivel de profundidad de una clase dentro de la jerarquía de herencia.",
                "min": None,
                "max": None,
            },
            "NOC": {
                "nombre": "Número de clases hijas",
                "mide": "Cantidad de subclases directas que heredan de la clase analizada.",
                "min": None,
                "max": None,
            },
            "CBO": {
                "nombre": "Acoplamiento entre clases",
                "mide": "Número de clases con las que la clase analizada está acoplada.",
                "min": None,
                "max": 9,
            },
            "RFC": {
                "nombre": "Respuesta de una clase",
                "mide": "Cantidad de métodos que pueden ejecutarse como respuesta a un mensaje recibido por la clase.",
                "min": None,
                "max": 40,
            },
            "LCOM": {
                "nombre": "Falta de cohesión entre métodos",
                "mide": "Grado en que los métodos de una clase no comparten atributos o responsabilidades comunes.",
                "min": None,
                "max": None,
            },
            "CA": {
                "nombre": "Acoplamiento aferente",
                "mide": "Número de clases externas que dependen de la clase analizada.",
                "min": None,
                "max": None,
            },
            "NPM": {
                "nombre": "Número de métodos públicos",
                "mide": "Cantidad de métodos públicos definidos en la clase.",
                "min": None,
                "max": None,
            },
        },
    }


def referencia_cpd() -> dict:
    return {
        "tabla_referencias": (
            "CPD no proporciona un rango universal de calidad para interpretar la duplicación. "
            "El valor configurado corresponde al umbral técnico de detección de duplicación."
        ),
        "observaciones_tabla": (
            "La duplicación debe interpretarse según el tamaño del proyecto, el contexto del código "
            "y la política de calidad definida. El umbral de tokens es configurable."
        ),
        "referencias_metricas": {
            "LINEAS_DUPLICADAS": {
                "nombre": "Líneas duplicadas",
                "mide": "Cantidad de líneas incluidas en un bloque de código duplicado.",
                "min": None,
                "max": None,
            },
            "TOKENS": {
                "nombre": "Tokens duplicados",
                "mide": "Cantidad de unidades léxicas detectadas como duplicadas entre fragmentos de código.",
                "min": None,
                "max": 100,
            },
        },
    }


def referencia_lizard(lenguaje: str = "") -> dict:
    lenguaje = lenguaje.lower().strip()

    referencias_metricas = {
        "NLOC": {
            "nombre": "Líneas de código sin comentarios",
            "mide": "Cantidad de líneas efectivas de código dentro del elemento analizado.",
            "min": None,
            "max": None,
        },
        "TOKENS": {
            "nombre": "Tokens",
            "mide": "Cantidad de unidades léxicas presentes en el elemento analizado.",
            "min": None,
            "max": None,
        },
        "PARAM": {
            "nombre": "Número de parámetros",
            "mide": "Cantidad de parámetros recibidos por una función o método.",
            "min": None,
            "max": None,
        },
        "LENGTH": {
            "nombre": "Longitud",
            "mide": "Número de líneas que ocupa la función o método analizado.",
            "min": None,
            "max": None,
        },
    }

    rangos_cualitativos = {}

    if lenguaje != "python":
        referencias_metricas["CCN"] = {
            "nombre": "Complejidad ciclomática",
            "mide": "Número de caminos independientes del flujo de control del elemento analizado.",
            "min": 1,
            "max": 10,
        }

        rangos_cualitativos["CCN"] = rangos_complejidad_ciclomatica()

    return {
        "tabla_referencias": (
            "Lizard calcula métricas estructurales como NLOC, tokens, número de parámetros "
            "y longitud. En proyectos Java también se incluye la complejidad ciclomática. "
            "En proyectos Python, la complejidad ciclomática se muestra mediante Radon para evitar duplicidad."
        ),
        "observaciones_tabla": (
            "Las métricas de Lizard deben interpretarse en contexto. En proyectos grandes pueden existir "
            "funciones extensas justificadas por lógica de negocio, estructuras condicionales amplias o flujos "
            "difíciles de dividir. Aun así, valores elevados pueden indicar mayor dificultad de prueba y mantenimiento."
        ),
        "referencias_metricas": referencias_metricas,
        "rangos_cualitativos": rangos_cualitativos,
    }


def referencia_radon() -> dict:
    return {
        "tabla_referencias": (
            "Radon calcula métricas de código Python como complejidad ciclomática, "
            "índice de mantenibilidad, métricas básicas de tamaño y métricas de Halstead. "
            "En este informe se muestran las métricas más relevantes para interpretar la calidad del código."
        ),
        "observaciones_tabla": (
            "La complejidad ciclomática y el índice de mantenibilidad se interpretan mediante rangos cualitativos. "
            "SLOC y las métricas de Halstead se muestran como métricas descriptivas para contextualizar el tamaño, "
            "el volumen lógico, la dificultad y el esfuerzo estimado del código analizado."
        ),
        "referencias_metricas": {
            "SLOC": {
                "nombre": "Líneas de código fuente",
                "mide": "Cantidad de líneas de código fuente sin contar líneas en blanco ni comentarios.",
                "min": None,
                "max": None,
            },
            "CC": {
                "nombre": "Complejidad ciclomática",
                "mide": "Número de caminos independientes existentes en el flujo de control del código.",
                "min": 1,
                "max": 10,
            },
            "MI": {
                "nombre": "Índice de mantenibilidad",
                "mide": "Indicador numérico que estima la facilidad de mantenimiento del código.",
                "min": 20,
                "max": 100,
            },
            "VOLUMEN": {
                "nombre": "Volumen de Halstead",
                "mide": "Tamaño lógico del código calculado a partir de operadores y operandos.",
                "min": None,
                "max": None,
            },
            "DIFICULTAD": {
                "nombre": "Dificultad de Halstead",
                "mide": "Estimación de la dificultad de comprensión o implementación del código.",
                "min": None,
                "max": None,
            },
            "ESFUERZO": {
                "nombre": "Esfuerzo de Halstead",
                "mide": "Estimación del esfuerzo necesario para comprender o desarrollar el código.",
                "min": None,
                "max": None,
            },
            "BUGS": {
                "nombre": "Errores estimados de Halstead",
                "mide": "Estimación teórica del número de defectos potenciales asociados al volumen lógico del código.",
                "min": None,
                "max": None,
            },
        },
        "rangos_cualitativos": {
            "CC": rangos_complejidad_ciclomatica(),
            "MI": [
                {
                    "min": 20,
                    "max": 100,
                    "etiqueta": "Alta",
                    "observacion": "Mantenibilidad alta.",
                },
                {
                    "min": 10,
                    "max": 19,
                    "etiqueta": "Media",
                    "observacion": "Mantenibilidad media; conviene revisar posibles mejoras.",
                },
                {
                    "min": 0,
                    "max": 9,
                    "etiqueta": "Baja",
                    "observacion": "Mantenibilidad baja; requiere revisión prioritaria.",
                },
            ],
        },
    }


def referencia_pylint() -> dict:
    return {
        "tabla_referencias": (
            "Pylint realiza análisis estático de código Python y clasifica los mensajes "
            "detectados en categorías como fatal, error, warning, refactor, convention e information."
        ),
        "observaciones_tabla": (
            "Los resultados de Pylint deben interpretarse como incidencias estáticas detectadas "
            "por la herramienta. La puntuación global indica conformidad con sus reglas, pero no "
            "garantiza por sí sola la calidad completa del software."
        ),
        "categorias": {
            "F": {
                "nombre": "Fatal",
                "severidad": "Muy grave",
                "interpretacion": "Impide o dificulta gravemente el análisis.",
            },
            "E": {
                "nombre": "Error",
                "severidad": "Grave",
                "interpretacion": "Posible error real en el código.",
            },
            "W": {
                "nombre": "Warning",
                "severidad": "Revisión necesaria",
                "interpretacion": "Posible problema, mala práctica o situación peligrosa.",
            },
            "R": {
                "nombre": "Refactor",
                "severidad": "Mejora recomendada",
                "interpretacion": "Código mejorable desde el punto de vista del diseño o la mantenibilidad.",
            },
            "C": {
                "nombre": "Convention",
                "severidad": "Estilo",
                "interpretacion": "Incumplimiento de convenciones de estilo o formato.",
            },
            "I": {
                "nombre": "Information",
                "severidad": "Informativo",
                "interpretacion": "Información adicional del análisis.",
            },
        },
        "categorias_detalle": ["F", "E", "W", "R"],
    }


def rangos_complejidad_ciclomatica():
    return [
        {
            "min": 1,
            "max": 10,
            "etiqueta": "Buena",
            "observacion": "Complejidad baja, normalmente sencilla de probar y mantener.",
        },
        {
            "min": 11,
            "max": 20,
            "etiqueta": "Moderada",
            "observacion": "Complejidad moderada; conviene revisar si puede simplificarse.",
        },
        {
            "min": 21,
            "max": 50,
            "etiqueta": "Alta",
            "observacion": (
                "Complejidad alta; puede estar justificada en casos concretos, "
                "pero aumenta el esfuerzo de prueba y mantenimiento."
            ),
        },
        {
            "min": 51,
            "max": None,
            "etiqueta": "Muy alta",
            "observacion": (
                "Complejidad muy alta; requiere revisión prioritaria por su impacto "
                "en comprensión, prueba y mantenimiento."
            ),
        },
    ]


def obtener_metricas_fuera_de_rango(metricas: dict, referencias_metricas: dict) -> str:
    metricas_fuera = []

    for metrica, valor in metricas.items():
        if metrica not in referencias_metricas:
            continue

        try:
            valor_numerico = float(valor)
        except Exception:
            continue

        referencia = referencias_metricas[metrica]

        minimo = referencia.get("min")
        maximo = referencia.get("max")

        if minimo is not None and valor_numerico < minimo:
            metricas_fuera.append(metrica)
            continue

        if maximo is not None and valor_numerico > maximo:
            metricas_fuera.append(metrica)
            continue

    if not metricas_fuera:
        return "Ninguna"

    return ", ".join(metricas_fuera)