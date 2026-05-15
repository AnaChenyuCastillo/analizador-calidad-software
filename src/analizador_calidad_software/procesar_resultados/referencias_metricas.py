from pathlib import Path

def referencia_ckjm() -> dict:
    return {
        "tabla_referencias": (
            "Los ranfos se basan unicamente en bibliografía con respaldo identificado"
            "Cuando no existe un umbral concreto con suficiente resspaldo, se dejará sinespecificar"
        ),
        "observaciones_tabla": (
            "Las metricas de CKJM deben interpretarse según el contexto del proyecto"
            "Los umbrales no son universales y no sustituyen al analísis del proyecto"
        ),
        "rangos": {
            "WMC": {
                "min": None,
                "max": 20,
            },
            "DIT": {
                "min": None,
                "max": None,
            },
            "NOC": {
                "min": None,
                "max": None,
            },
            "CBO": {
                "min": None,
                "max": 9,
            },
            "RFC": {
                "min": None,
                "max": 40,
            },
            "LCOM": {
                "min": None,
                "max": None,
            },
            "CA": {
                "min": None,
                "max": None,
            },
            "NPM": {
                "min": None,
                "max": None,
            },
        }
    }

def obtener_metricas_fuera_de_rango(metricas: dict, rangos: dict) -> str:
    metricas_fuera = []
    
    for metrica, valor in metricas.items():
        if metrica not in rangos:
            continue

        if not str(valor). isdigit():
            continue

        valor_numerico = int(valor)
        rango = rangos[metrica]

        minimo = rango["min"]
        maximo = rango["max"]

        if minimo is not None and valor_numerico < minimo:
            metricas_fuera.append(metrica)
            continue

        if maximo is not None and valor_numerico > maximo:
            metricas_fuera.append(metrica)
            continue

    if not metricas_fuera:
        return "Ninguna"
    
    return ",".join(metricas_fuera)

def referencia_cpd() -> dict:
    return {
        "tabla_referencias" : (
            "CPD no proporciona un rango univarsal de calidad para interpretar la duplicación"
            "El valor configurado corresponde al umbral técnicode detección de duplicación"
        ),
        "observaciones_tabla": (
            "La dupicación debe interpretarse según el tamaño del pryecto, el contexto del código"
            "y la politica de calidad definida. El umbral de tokens es configurable"
        ),
        "rangos": {
            "LINEAS_DUPLICADAS":{
                "min": None,
                "max": None
            },
            "TOKENS": {
                "min": None,
                "max": 100,
                "nota": (
                    "Se usa 100 como umbral técnico de referencia porque PMD CPD lo muestra en sus ejemplos"
                    "de uso y el Maven PMD Plugin lo documenta como valor por defecto de minimunTokens"
                )
            }
        }
    }

def referencia_lizard() -> dict:
    return {
        "tabla_referencias": (
            "Lizard calcula métricas como MLCO, complejidad ciclomatica, tokens, "
            "numero de prarámetros y longitud. Para la interpretación de la complejidad "
            "ciclomatica se opta el umbral académico basado en McCabe/NIST"
        ),
        "observaciones_tabla": (
            "LA complejidad ciclomatica debe interpretarse en contexto. En proyectos grandes "
            "pueden existit funciones con complejidad moderada o alta justificadas por logica "
            "de negocios, estructuras switch o match extensas o flujos dificiles de dividir. Aun así "
            "canto mayor sea el valor, mayor será la dificultad de prueba y mantenimiento"
        ), 
        "rangos": {
            "NLOC": {
                "min": None,
                "max": None
            },
            "CCN": {
                "min": None,
                "max": 50,
                "nota": (
                    "Se usa 50 como limite superior antes de considerar la complejidad muy alta. "
                    "La interpretación se hace por niveles cualitativos"
                )
            },
            "TOKENS": {
                "min": None,
                "max": None
            },
            "PARAM": {
                "min": None,
                "max": None
            },
            "LENGTH": {
                "min": None,
                "max": None
            }
        },
        "rangos_cualitativos": {
            "CCN": rangos_complejidad_ciclomatica()
        }
    }

def rangos_complejidad_ciclomatica():
    return [
        {
            "min": 1,
            "max": 10,
            "etiqueta": "Buena",
            "observacion": "Complejidad baja, normalmente sencilla de probar y mantener."
        },
        {
            "min": 11,
            "max": 20,
            "etiqueta": "Moderada",
            "observacion": "Complejidad moderada; conviene revisar si puede simplificarse."
        },
        {
            "min": 21,
            "max": 50,
            "etiqueta": "Alta",
            "observacion": (
                "Complejidad alta; puede estar justificada en casos concretos, "
                "pero aumenta el esfuerzo de prueba y mantenimiento"
            )
        },
        {
            "min": 51,
            "max": None,
            "etiqueta": "Alta",
            "observacion": (
                "Complejidad muy alta; requiere revision prioritaria por su impacto "
                "en comprensión, prueba, y mantenimiento"
            )
        }
    ]

def referencia_radon() -> dict:
    return {
        "tabla_referencias": (
            "Radon calcula metricas de código Pyton como complejidad ciclomática, "
            "índice de mantenibilidad, metricas raw y métricas de Halsted. En este informe, "
            "se mostrarán las metrcas más relevantes para interpretar la calidad del codigo."
        ),
        "observaciones_tabla": (
            "La complejidad ciclomática y el índice de mantenibilidad se interpretan "
            "mediante rangos cualitativos. SLOC y volumen de Halstead se muestran como "
            "métricas descriptivas para contextualizar el tamaño y el volumen lógico "
            "del código analizado."
        ),
        "rangos": {
            "SLOC": {
                "min": None,
                "max": None
            },
            "CC": {
                "min": None,
                "max": 50
            },
            "MI": {
                "min": 10,
                "max": None,
            },
            "VOLUMEN": {
                "min": None,
                "max": None,
            },
        },
        "rangos_cualitativos": {
            "CC": rangos_complejidad_ciclomatica(),
            "MI":{
                {
                    "min": 20,
                    "max": 100,
                    "etiqueta": "Alta",
                    "observacion": "Mantenibilidad alta."
                },
                {
                    "min": 10,
                    "max": 19,
                    "etiqueta": "Media",
                    "observacion": "Mantenibilidad media; conviene revisar posibles mejoras."
                },
                {
                    "min": 0,
                    "max": 9,
                    "etiqueta": "Baja",
                    "observacion": "Mantenibilidad baja; requiere revisión prioritaria."
                },
            }
        }
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
                "interpretacion": "Impide o dificulta gravemente el análisis."
            },
            "E": {
                "nombre": "Error",
                "severidad": "Grave",
                "interpretacion": "Posible error real en el código."
            },
            "W": {
                "nombre": "Warning",
                "severidad": "Revisión necesaria",
                "interpretacion": "Posible problema, mala práctica o situación peligrosa."
            },
            "R": {
                "nombre": "Refactor",
                "severidad": "Mejora recomendada",
                "interpretacion": "Código mejorable desde el punto de vista del diseño o la mantenibilidad."
            },
            "C": {
                "nombre": "Convention",
                "severidad": "Estilo",
                "interpretacion": "Incumplimiento de convenciones de estilo o formato."
            },
            "I": {
                "nombre": "Information",
                "severidad": "Informativo",
                "interpretacion": "Información adicional del análisis."
            },
        },
        "categorias_detalle": ["F", "E", "W", "R"],
    }