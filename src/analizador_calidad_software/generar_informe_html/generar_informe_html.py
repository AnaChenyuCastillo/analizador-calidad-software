from html import escape


def limpiar_html(valor):
    if valor is None:
        return ""

    # escape convierte caracteres especiales que pueden interpretarse como parte del HTML,
    # de forma que se interpreten como texto normal en la página.
    return escape(str(valor))


def generar_estilos():
    return """
    <style>
        html {
            scroll-behavior: smooth;
        }

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

        h3 {
            margin-top: 25px;
            color: #374151;
        }

        h4 {
            margin-top: 20px;
            color: #374151;
        }

        .bloque-proyecto {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #ddd;
        }

        .bloque-tabla {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 35px;
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

        .aviso {
            background-color: #fef2f2;
            padding: 15px;
            border-left: 4px solid #dc2626;
            margin: 20px 0 30px 0;
            border-radius: 4px;
        }

        .aviso ul {
            margin-top: 10px;
            margin-bottom: 0;
        }

        .contenedor-tabla {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 25px;
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

        .tabla-referencias th {
            background-color: #4338ca;
        }

        .tabla-rangos th {
            background-color: #065f46;
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
            cursor: pointer;
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

        .indice {
            background-color: white;
            padding: 15px 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
            margin-bottom: 30px;
        }

        .indice a {
            display: inline-block;
            margin: 6px 10px 6px 0;
            color: #1f2937;
            text-decoration: none;
            font-weight: bold;
        }

        .indice a:hover {
            text-decoration: underline;
        }

        .volver-arriba {
            display: inline-block;
            margin-top: 5px;
            margin-bottom: 15px;
            font-size: 13px;
            color: #374151;
            text-decoration: none;
        }

        .volver-arriba:hover {
            text-decoration: underline;
        }

        .cabecera-impresion {
            display: none;
        }

        @media print {
            @page {
                size: A4 landscape;
                margin: 10mm;
            }

            body {
                margin: 0;
                background-color: white;
                color: black;
            }

            .botones-superiores,
            .indice,
            .volver-arriba {
                display: none;
            }

            .bloque-proyecto {
                page-break-after: always;
                border: none;
            }

            .bloque-tabla {
                page-break-before: always;
                border: none;
                padding: 0;
                margin: 0;
            }

            .referencia,
            .observacion,
            .tabla-referencias,
            .tabla-rangos {
                page-break-inside: avoid;
            }

            .tabla-referencias,
            .tabla-rangos {
                page-break-after: always;
            }

            table {
                width: 100%;
                font-size: 8px;
                page-break-inside: auto;
            }

            thead {
                display: table-header-group;
            }

            tbody {
                display: table-row-group;
            }

            tr {
                page-break-inside: avoid;
                page-break-after: auto;
            }

            th {
                background-color: #1f2937 !important;
                color: white !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }

            td {
                padding: 4px;
            }

            h1, h2, h3, h4 {
                page-break-after: avoid;
            }

            .cabecera-impresion {
                display: table-row;
            }

            .cabecera-impresion th {
                background-color: #111827 !important;
                color: white !important;
                font-size: 10px;
                text-align: left;
            }
        }
    </style>
    """


def formatear_valor_referencia(valor):
    if valor is None:
        return "Sin especificar"

    if valor == "":
        return "Sin especificar"

    return str(valor)


def generar_tabla_referencias_metricas(referencias: dict) -> str:
    referencias_metricas = referencias.get("referencias_metricas", {})

    if not referencias_metricas:
        return ""

    metricas = list(referencias_metricas.keys())

    partes = []

    partes.append("<h3>Referencias de métricas</h3>")
    partes.append("<div class='contenedor-tabla'>")
    partes.append("<table class='tabla-referencias'>")

    partes.append("<thead>")
    partes.append("<tr>")
    partes.append("<th></th>")

    for metrica in metricas:
        partes.append(f"<th>{limpiar_html(metrica)}</th>")

    partes.append("</tr>")
    partes.append("</thead>")

    partes.append("<tbody>")

    filas_referencias = [
        ("Nombre", "nombre"),
        ("Qué mide", "mide"),
        ("Mínimo", "min"),
        ("Máximo", "max"),
    ]

    for titulo_fila, clave in filas_referencias:
        partes.append("<tr>")
        partes.append(f"<td><strong>{limpiar_html(titulo_fila)}</strong></td>")

        for metrica in metricas:
            valor = referencias_metricas[metrica].get(clave, "")
            partes.append(
                f"<td>{limpiar_html(formatear_valor_referencia(valor))}</td>"
            )

        partes.append("</tr>")

    partes.append("</tbody>")
    partes.append("</table>")
    partes.append("</div>")

    return "\n".join(partes)


def generar_tabla_rangos_cualitativos(referencias: dict) -> str:
    rangos_cualitativos = referencias.get("rangos_cualitativos", {})

    if not rangos_cualitativos:
        return ""

    partes = []

    partes.append("<h3>Rangos cualitativos</h3>")

    for metrica, rangos in rangos_cualitativos.items():
        partes.append(f"<h4>{limpiar_html(metrica)}</h4>")
        partes.append("<div class='contenedor-tabla'>")
        partes.append("<table class='tabla-rangos'>")

        partes.append("<thead>")
        partes.append("<tr>")
        partes.append("<th>Mínimo</th>")
        partes.append("<th>Máximo</th>")
        partes.append("<th>Clasificación</th>")
        partes.append("<th>Observación</th>")
        partes.append("</tr>")
        partes.append("</thead>")

        partes.append("<tbody>")

        for rango in rangos:
            minimo = formatear_valor_referencia(rango.get("min"))
            maximo = formatear_valor_referencia(rango.get("max"))
            etiqueta = rango.get("etiqueta", "")
            observacion = rango.get("observacion", "")

            partes.append("<tr>")
            partes.append(f"<td>{limpiar_html(minimo)}</td>")
            partes.append(f"<td>{limpiar_html(maximo)}</td>")
            partes.append(f"<td>{limpiar_html(etiqueta)}</td>")
            partes.append(f"<td>{limpiar_html(observacion)}</td>")
            partes.append("</tr>")

        partes.append("</tbody>")
        partes.append("</table>")
        partes.append("</div>")

    return "\n".join(partes)


def generar_referencias(tabla: dict) -> str:
    referencias = tabla.get("referencias", {})

    if not referencias:
        return ""

    referencia_general = limpiar_html(referencias.get("tabla_referencias", ""))
    observacion_general = limpiar_html(referencias.get("observaciones_tabla", ""))

    partes = []

    if referencia_general != "":
        partes.append(
            f"<div class='referencia'><strong>Referencia:</strong> {referencia_general}</div>"
        )

    if observacion_general != "":
        partes.append(
            f"<div class='observacion'><strong>Observación:</strong> {observacion_general}</div>"
        )

    tabla_referencias_metricas = generar_tabla_referencias_metricas(referencias)

    if tabla_referencias_metricas != "":
        partes.append(tabla_referencias_metricas)

    tabla_rangos = generar_tabla_rangos_cualitativos(referencias)

    if tabla_rangos != "":
        partes.append(tabla_rangos)

    return "\n".join(partes)


def generar_tablas(tabla: dict, indice_tabla: int):
    titulo = limpiar_html(tabla.get("titulo", "Tabla sin título"))

    cabeceras = tabla.get("cabeceras", [])
    filas = tabla.get("filas", [])

    id_tabla = f"tabla-{indice_tabla}"

    partes = []

    partes.append(f"<section class='bloque-tabla' id='{id_tabla}'>")
    partes.append(f"<h2>{titulo}</h2>")
    partes.append("<a class='volver-arriba' href='#inicio'>Volver arriba</a>")

    referencias_html = generar_referencias(tabla)

    if referencias_html != "":
        partes.append(referencias_html)

    partes.append("<h3>Resultados</h3>")

    if not cabeceras:
        partes.append("<div class='tabla-vacia'>Esta tabla no tiene cabeceras.</div>")
        partes.append("</section>")
        return "\n".join(partes)

    if not filas:
        partes.append(
            "<div class='tabla-vacia'>No se han encontrado resultados para esta herramienta.</div>"
        )
        partes.append("</section>")
        return "\n".join(partes)

    partes.append("<div class='contenedor-tabla'>")
    partes.append("<table>")
    partes.append("<thead>")

    partes.append("<tr class='cabecera-impresion'>")
    partes.append(f"<th colspan='{len(cabeceras)}'>{titulo}</th>")
    partes.append("</tr>")

    partes.append("<tr>")

    for cabecera in cabeceras:
        partes.append(f"<th>{limpiar_html(cabecera)}</th>")

    partes.append("</tr>")
    partes.append("</thead>")

    partes.append("<tbody>")

    for fila in filas:
        partes.append("<tr>")

        for indice, cabecera in enumerate(cabeceras):
            if indice < len(fila):
                valor = fila[indice]
            else:
                valor = ""

            partes.append(f"<td>{limpiar_html(valor)}</td>")

        partes.append("</tr>")

    partes.append("</tbody>")
    partes.append("</table>")
    partes.append("</div>")
    partes.append("</section>")

    return "\n".join(partes)


def generar_aviso_errores_ckjm(errores_ckjm: list) -> str:
    if not errores_ckjm:
        return ""

    partes = []

    partes.append("<div class='aviso'>")
    partes.append("<h2>Aviso del análisis CKJM</h2>")
    partes.append(
        f"<p>Se han producido errores en el análisis CKJM en "
        f"{len(errores_ckjm)} clase(s). Por ello, las métricas CKJM pueden no estar completas "
        f"y conviene revisar la compilación o compatibilidad de esas clases.</p>"
    )

    partes.append("<ul>")

    for clase in errores_ckjm:
        partes.append(f"<li>{limpiar_html(clase)}</li>")

    partes.append("</ul>")
    partes.append("</div>")

    return "\n".join(partes)


def generar_indice_tablas(tablas_resultados: list[dict]) -> str:
    if not tablas_resultados:
        return ""

    partes = []

    partes.append("<div class='indice'>")
    partes.append("<h2>Índice de resultados</h2>")

    for indice, tabla in enumerate(tablas_resultados, start=1):
        titulo = limpiar_html(tabla.get("titulo", f"Tabla {indice}"))
        partes.append(f"<a href='#tabla-{indice}'>{titulo}</a>")

    partes.append("</div>")

    return "\n".join(partes)


def generar_contenido_html(
    datos_proyecto: dict,
    tablas_resultados: list[dict],
    nombre_dcc,
    errores_ckjm=None,
):
    if errores_ckjm is None:
        errores_ckjm = []

    nombre_proyecto = limpiar_html(datos_proyecto.get("nombre_proyecto", ""))
    ruta_proyecto = limpiar_html(datos_proyecto.get("ruta_proyecto", ""))
    lenguaje = limpiar_html(datos_proyecto.get("lenguaje", ""))

    partes = []

    partes.append("<!DOCTYPE html>")
    partes.append("<html lang='es'>")
    partes.append("<head>")
    partes.append("<meta charset='UTF-8'>")
    partes.append(f"<title>Informe de calidad de software {nombre_proyecto}</title>")
    partes.append(generar_estilos())
    partes.append("</head>")
    partes.append("<body id='inicio'>")

    partes.append("<div class='botones-superiores'>")
    partes.append("<a class='boton boton-secundario' href='#inicio'>Inicio</a>")
    partes.append("<button class='boton' onclick='window.print()'>Generar PDF</button>")

    if nombre_dcc:
        partes.append(
            f"<a class='boton boton-secundario' href='{limpiar_html(nombre_dcc)}' target='_blank'>Ver diagramas</a>"
        )

    partes.append("</div>")

    partes.append("<h1>Informe de calidad de software</h1>")

    partes.append("<div class='bloque-proyecto'>")
    partes.append(f"<p><strong>Proyecto:</strong> {nombre_proyecto}</p>")
    partes.append(f"<p><strong>Ruta:</strong> {ruta_proyecto}</p>")
    partes.append(f"<p><strong>Lenguaje:</strong> {lenguaje}</p>")
    partes.append(f"<p><strong>Número de tablas:</strong> {len(tablas_resultados)}</p>")
    partes.append("</div>")

    aviso_ckjm = generar_aviso_errores_ckjm(errores_ckjm)

    if aviso_ckjm != "":
        partes.append(aviso_ckjm)

    partes.append(generar_indice_tablas(tablas_resultados))

    for indice, tabla in enumerate(tablas_resultados, start=1):
        partes.append(generar_tablas(tabla, indice))

    partes.append("</body>")
    partes.append("</html>")

    return "\n".join(partes)