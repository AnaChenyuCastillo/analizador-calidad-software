from pathlib import Path
from html import escape

def limpiar_html(valor):
    if valor is None:
        return ""
    
    #escape convierte caracteres especial qu epueden interpretarse como parte del html de forma que se interpreten como texto normal en la pagina
    return escape(str(valor)) 

def generar_estilos():
    return """
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
            color: #222;
        }

        h1 {
            color: #1f2937;
        }

        h2 {
            margin-top: 40px;
            color: #1f2937;
            border-bottom: 2px solid #ccc;
            padding-bottom: 6px;
        }

        .bloque-proyecto {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #ddd;
        }

        .referencia {
            background-color: #eef2ff;
            padding: 12px;
            border-left: 4px solid #6366f1;
            margin: 10px 0;
            border-radius: 4px;
        }

        .observacion {
            background-color: #fff7ed;
            padding: 12px;
            border-left: 4px solid #f97316;
            margin: 10px 0 20px 0;
            border-radius: 4px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            margin-bottom: 30px;
            font-size: 14px;
        }

        th {
            background-color: #1f2937;
            color: white;
            text-align: left;
            padding: 10px;
            border: 1px solid #ddd;
        }

        td {
            padding: 8px;
            border: 1px solid #ddd;
            vertical-align: top;
        }

        tr:nth-child(even) {
            background-color: #f9fafb;
        }

        .tabla-vacia {
            padding: 12px;
            background-color: #fee2e2;
            border-left: 4px solid #dc2626;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .botones-superiores {
        position: fixed;
        top: 20px;
        right: 30px;
        display: flex;
        gap: 10px;
        z-index: 1000;
        }

        .boton {
            background-color: #1f2937;
            color: white;
            text-decoration: none;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 14px;
            border: none;
        }

        .boton:hover {
            background-color: #374151;
        }

        .boton-secundario {
            background-color: #4b5563;
        }

        .boton-secundario:hover {
            background-color: #6b7280;
        }
    </style>
    """

def generar_tablas(tabla: dict):
    # primero ponemos en variables los valores que vamos a necesitar
    titulo = limpiar_html(tabla.get("titulo", "Tabla sin titulo"))
    referencia = limpiar_html(tabla.get("tabla_referencias", ""))
    observacion = limpiar_html(tabla.get("observaciones_tabla", ""))

    cabeceras = tabla.get("cabeceras", [])
    filas = tabla.get("filas", [])

    partes = []

    partes.append(f"<h2>{titulo}</h2>")

    if referencia != "":
        partes.append(
            f"<div class='referencia'><strong> Referencia:</strong> {referencia}</div>"
        )

    if observacion != "":
        partes.append(
            f"<div class='observacion'><strong> Observacion:</strong> {observacion}</div>"
        )

    if not cabeceras:
        partes.append("<div class='tabla-vacia'>Esta tabla no tiene cabeceras.</div>")
        return "\n".join(partes)
    
    if not filas:
        partes.append(
            "<div class='tabla-vacia> NO se han encontrado resultados para esta herramienta.</div>"
        )
        return "\n".join(partes)

    partes.append("<table>")
    partes.append("<thead>")
    partes.append("<th>")

    for cabecera in cabeceras:
        partes.append(f"<th>{limpiar_html(cabecera)}</th>")
    partes.append("</th>")

    partes.append("</thead>")

    partes.append("<tbody>")

    for fila in filas:
        partes.append("<tr>")

        for indice, cabecera in enumerate(cabeceras):
            if indice> len(fila):
                valor = fila[indice]
            else:
                valor = ""

            partes.append(f"<td>{limpiar_html(valor)}</td>")

        partes.append("</tr>")

    partes.append("</tbody")
    partes.append("</table>")

    return "\n".join(partes)

def genera_contenido_html(datos_proyecto: dict, tablas_resultados: list[dict], nombre_dcc):
    nombre_proyecto = limpiar_html(datos_proyecto.get("nombre_proyecto", ""))
    ruta_proyecto = limpiar_html(datos_proyecto.get("ruta_proyecto", ""))
    lenguaje = limpiar_html(datos_proyecto.get("lenguaje", ""))

    partes = []

    partes.append("<!DOCTYPE html>")
    partes.append("<html lang='es'>")
    partes.append("<head>")
    partes.append("<meta charset='UTF-8'>")
    partes.append("<title>Informe de calidad de software</title>")
    partes.append(generar_estilos())
    partes.append("</head>")
    partes.append("<body>")

    partes.append("<div class='botones-superiores'>")
    partes.append("<a class='boton' href='informe_calidad.pdf' download>Descargar informe en PDF</a>")
    partes.append(f"<a class='boton boton-secundario' href='{limpiar_html(nombre_dcc)}' target='_blank'>Ver diagramas</a>")
    partes.append("</div>")

    partes.append("<h1>Informe de calidad de software</h1>")

    partes.append("<div class='bloque-proyecto'>")
    partes.append(f"<p><strong>Proyecto:</strong> {nombre_proyecto}</p>")
    partes.append(f"<p><strong>Ruta:</strong> {ruta_proyecto}</p>")
    partes.append(f"<p><strong>Lenguaje:</strong> {lenguaje}</p>")
    partes.append(f"<p><strong>Número de tablas:</strong> {len(tablas_resultados)}</p>")
    partes.append("</div>")

    for tabla in tablas_resultados:
        partes.append(generar_tablas(tabla))

    partes.append("</body>")
    partes.append("</html>")

    return "\n".join(partes)