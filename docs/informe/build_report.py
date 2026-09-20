"""Genera el informe tecnico (PDF) de la Actividad 6.

Ejecutar: python docs/informe/build_report.py
Requisito: pip install reportlab
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE = Path(__file__).resolve().parent.parent.parent
UML = BASE / "docs" / "uml"
RESULTS = BASE / "docs" / "results"
OUT = BASE / "docs" / "informe" / "Informe_Actividad6.pdf"

BENCH = json.loads((RESULTS / "benchmark.json").read_text(encoding="utf-8"))


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("·", "-")
    )


styles = getSampleStyleSheet()


def st(name, **kw):
    return ParagraphStyle(name, **kw)


S = {
    "title": st("S-title", fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#0b3d66")),
    "subtitle": st("S-subtitle", fontSize=13, leading=17, alignment=TA_CENTER),
    "h1": st("S-h1", fontName="Helvetica-Bold", fontSize=15, leading=19, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#0b3d66")),
    "h2": st("S-h2", fontName="Helvetica-Bold", fontSize=12, leading=15, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#175e8c")),
    "body": st("S-body", fontSize=10, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=6),
    "bullet": st("S-bullet", fontSize=10, leading=14, spaceAfter=3),
    "caption": st("S-caption", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.grey),
}


def p(text, style="body", bold_prefix=None):
    txt = esc(text)
    if bold_prefix:
        txt = f"<b>{esc(bold_prefix)}</b> " + txt
    return Paragraph(txt, S[style])


def bullets(items):
    flow = []
    for it in items:
        if isinstance(it, tuple):
            flow.append(ListItem(p(it[1], "bullet", bold_prefix=it[0]), leftIndent=6))
        else:
            flow.append(ListItem(p(it, "bullet"), leftIndent=6))
    return ListFlowable(flow, bulletType="bullet", bulletFontSize=6, leftIndent=14, bulletColor=colors.HexColor("#0b3d66"))


def make_table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9fb6c9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d66")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


def loading_bar_chart(categories, series):
    drawing = Drawing(430, 180)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 35
    chart.width = 330
    chart.height = 125
    chart.data = series
    chart.strokeColor = colors.black
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(max(s) for s in series) * 1.25
    chart.categoryAxis.categoryNames = categories
    chart.categoryAxis.labels.angle = 35
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.dx = 10
    chart.categoryAxis.labels.dy = -2
    chart.valueAxis.labelTextFormat = "%2.1f"
    chart.valueAxis.labels.fontSize = 7
    chart.bars[0].fillColor = colors.HexColor("#8fc1e3")
    chart.bars[1].fillColor = colors.HexColor("#e36a4d")
    drawing.add(chart)
    return drawing


def numbered_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawCentredString(A4[0] / 2.0, 1.1 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def header_footer(canvas, doc):
    numbered_page(canvas, doc)
    if doc.page > 1:
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#7f8c8d"))
        canvas.drawString(2 * cm, A4[1] - 1.4 * cm, "MAREA ROUTE - Estrategias de navegacion en la arquitectura de software")
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.4 * cm, "U3 - Actividad 6")
        canvas.restoreState()


def strat_from(name):
    return name


def build():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm,
        title="Informe Actividad 6 - Estrategias de navegacion",
        author="Equipo Arquitectura de Software",
    )
    story = []

    # ---------------- PORTADA ----------------
    story.append(Spacer(1, 3.2 * cm))
    story.append(Paragraph("Arquitectura de Software", S["title"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Unidad 3 - Evaluacion y optimizacion de arquitecturas", S["subtitle"]))
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph("MAREA ROUTE", st("w1", fontSize=30, leading=34, alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=colors.HexColor("#0b3d66"))))
    story.append(Paragraph("Estrategias de navegacion en la arquitectura de software", st("w2", fontSize=16, leading=20, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Actividad 6 - Navegando mareas", st("w3", fontSize=13, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#596a75"))))
    story.append(Spacer(1, 2.4 * cm))
    equipo = [
        ["Curso", "Arquitectura de Software 20262 - N5 GrB"],
        ["Docente", "Edward Alfonso Villamizar Vallejo"],
        ["Equipo", "Omar Vallejo (coordinacion y plan) / David Mape y Eliécer Sanchez (arquitectura y UML) / Daniel Rodriguez (desarrollador) / Volmar Rincon (pruebas de carga y robustez)"],
        ["Fecha", "Septiembre de 2026"],
    ]
    story.append(make_table(equipo, col_widths=[3.2 * cm, 12.6 * cm], header=False))
    story.append(PageBreak())

    # ---------------- INDICE ----------------
    story.append(Paragraph("Indice", S["h1"]))
    indice = [
        "1. Contexto y problema abordado",
        "2. Analisis y marco de referencia",
        "3. Arquitectura propuesta (modelos UML)",
        "4. Patrones de diseno aplicados",
        "5. Implementacion del prototipo",
        "6. Pruebas y resultados",
        "7. Validacion frente a la rubrica",
        "8. Conclusiones y trabajo futuro",
        "Referencias",
        "Anexo A: comandos y reproduccion de resultados",
    ]
    story.append(bullets(indice))
    story.append(PageBreak())

    # ---------------- 1. PROBLEMA ----------------
    story.append(Paragraph("1. Contexto y problema abordado", S["h1"]))
    story.append(Paragraph("1.1 Problema seleccionado", S["h2"]))
    story.append(p(
        "Se selecciono el problema de <b>optimizacion de rutas en sistemas de mapas y navegacion"
        " intelligente</b>. La mayoria de los sistemas de ruteo calculan la ruta mas corta o mas"
        " rapida a partir de un plan estatico de la red vial, pero no consideran la evolucion "
        "inmediata de la congestion, especialmente durante las <b>mareas de trafico</b> (horas pico).",
    ))
    story.append(p(
        "Como consecuencia, al conductor se le ofrecen trayectorias que en minutos reales son "
        "suboptimas: una calle central con apariencia de atajo puede exigir el triple de tiempo "
        "cuando la congestion la satura. El proyecto se enfoco en la pregunta: como debe "
        "estructurarse la arquitectura de un navegador para que la estrategia de camino sea "
        "seleccionable, el sistema reaccione a los cambios del entorno y el recorrido se presente "
        "al usuario de forma desacoplada y extensible?",
    ))
    story.append(Paragraph("1.2 Relevancia e impacto", S["h2"]))
    story.append(p(
        "La navegacion eficiente impacta tres dimensiones. En la <b>experiencia de usuario</b>, "
        "una ruta optima reduce el estres y el tiempo de viaje. En el <b>rendimiento del sistema</b>, "
        "algoritmos dirigidos por heuristica (A*) reducen el numero de nodos explorados y, por lo "
        "tanto, la latencia del servicio. Y en la <b>eficiencia operativa</b>, flotas de entrega "
        "y transportadores ahorran combustible, horas hombre y costo por recorrido cuando la "
        "replanificacion se adapta a la congestion en tiempo real.",
    ))
    story.append(Paragraph("1.3 Objetivos", S["h2"]))
    story.append(bullets([
        ("O1", "Modelar una arquitectura por capas que separe presentacion, aplicacion, logica de ruteo e infraestructura."),
        ("O2", "Aplicar los patrones Strategy, Observer, Command, Iterator y Composite para lograr extensibilidad y baja cohesion."),
        ("O3", "Especificar el sistema con diagramas UML de componentes, clases, secuencia y actividad."),
        ("O4", "Implementar un prototipo funcional y validarlo con metricas objetivas (tiempo, nodos expandidos, ms de ejecucion)."),
    ]))
    story.append(PageBreak())

    # ---------------- 2. ANALISIS ----------------
    story.append(Paragraph("2. Analisis y marco de referencia", S["h1"]))
    story.append(Paragraph("2.1 Estrategias de navegacion en la literatura", S["h2"]))
    story.append(p(
        "Los algoritmos clasicos de camino minimo son la base del ruteo. <b>Dijkstra</b> garantiza "
        "el optimo sobre pesos no negativos pero explora de forma radial; <b>A*</b> incorpora una "
        "heuristica admisible que orienta la busqueda y reduce nodos expandidos. <b>BFS</b> ignora "
        "los pesos y solo minimiza saltos, util como linea base para medir la optimizacion. En la "
        "bibliografia de la unidad (Blas et al., 2019) se enfatiza el modelado y verificacion de "
        "patrones arquitectonicos antes de su despliegue; el presente prototipo aplica esa "
        "metodologia: los patrones se modelan primero en UML y luego se validan por ejecucion.",
    ))
    story.append(Paragraph("2.2 Enfoques en sistemas reales", S["h2"]))
    story.append(bullets([
        ("Google Maps / Waze:", "combinan grafos viales con datos de trafico en vivo y heuristica A* sobre grafos jerarquicos para baja latencia."),
        ("OSRM / OpenStreetMap:", "usa tecnicas de contraccion de grafos (CH) y pesos por velocidad para servicio masivo de rutas."),
        ("Flotas de mensajeria:", "replanifican sobre pedidos agrupados por zona, equivalente al patron Composite de destinos."),
    ]))
    story.append(Paragraph("2.3 Criterios de diseno", S["h2"]))
    story.append(make_table(
        [
            ["Criterio", "Definicion"],
            ["Eficiencia", "Minimizar tiempo real de viaje y nodos explorados por el algoritmo."],
            ["Escalabilidad", "Anadir nuevas estrategias de ruteo sin modificar el nucleo (interfaz RouteStrategy)."],
            ["Adaptabilidad", "Reaccionar a eventos de trafico (mareas) con replanificacion automatica."],
            ["Extensibilidad", "Incluir nuevos tipos de destino (grupos) y nuevos comandos sin alterar el grafo."],
            ["Mantenibilidad", "Capas y patrones bien delimitados permiten evolucion aislada de cada pieza."],
        ],
    ))
    story.append(PageBreak())

    # ---------------- 3. ARQUITECTURA ----------------
    story.append(Paragraph("3. Arquitectura propuesta", S["h1"]))
    story.append(Paragraph("3.1 Estilo arquitectonico", S["h2"]))
    story.append(p(
        "La solucion adopta un estilo <b>por capas</b> con una fachada central (<i>Navigator</i>). "
        "La capa de presentacion (CLI) invoca la fachada; la capa de aplicacion orquesta contextos "
        "de patrones; la capa de logica contiene el grafo, los algoritmos y los modelos; la capa "
        "de infraestructura mantiene el sujeto de trafico y el registro de metricas. El flujo de "
        "datos sigue un sentido unico hacia abajo, y las dependencias apuntan a interfaces "
        "(RouteStrategy, Observer, Command).",
    ))
    story.append(Paragraph("3.2 Diagrama de componentes", S["h2"]))
    story.append(Image(str(UML / "componentes.png"), width=17 * cm, height=11.2 * cm))
    story.append(p("Diagrama de componentes: dependencias y conectores entre las capas y los patrones.", "caption"))
    story.append(Paragraph("3.3 Diagrama de clases", S["h2"]))
    story.append(Image(str(UML / "clases.png"), width=17 * cm, height=11.2 * cm))
    story.append(p("Diagrama de clases: colaboracion de los cinco patrones sobre el modelo de dominio.", "caption"))
    story.append(Paragraph("3.4 Diagrama de secuencia", S["h2"]))
    story.append(Image(str(UML / "secuencia.png"), width=17 * cm, height=10.5 * cm))
    story.append(p("Diagrama de secuencia: solicitud de ruta, notificacion de trafico y replanificacion.", "caption"))
    story.append(Paragraph("3.5 Diagrama de actividad", S["h2"]))
    story.append(Image(str(UML / "actividad.png"), width=14 * cm, height=11.5 * cm))
    story.append(p("Diagrama de actividad: flujo completo desde la solicitud hasta la navegacion paso a paso.", "caption"))
    story.append(PageBreak())

    # ---------------- 4. PATRONES ----------------
    story.append(Paragraph("4. Patrones de diseno aplicados", S["h1"]))
    patrones = [
        ["Patron", "Necesidad", "Solucion aplicada en MAREA ROUTE"],
        [
            "Strategy",
            "Conmutar el algoritmo de ruteo sin cambiar el cliente.",
            "RoutePlanner (contexto) delega en RouteStrategy; se implementaron Dijkstra-distancia, Dijkstra-tiempo plano, Dijkstra-tiempo en vivo, A* y BFS.",
        ],
        [
            "Observer",
            "Reaccionar a los cambios del trafico en tiempo real.",
            "TrafficControlCenter (sujeto) notifica a Navigator y TrafficLogger cuando cambia la congestion de un tramo; Navigator activa la replanificacion.",
        ],
        [
            "Command",
            "Encapsular acciones del usuario con soporte de deshacer.",
            "ChangeDestinationCommand y RerouteCommand se apilan en CommandHistory con execute() y undo().",
        ],
        [
            "Iterator",
            "Recorrer la ruta paso a paso sin exponer la coleccion.",
            "RouteIterator entrega objetos RouteStep con la instruccion del tramo y sus metricas parciales.",
        ],
        [
            "Composite",
            "Tratar un destino unico y un grupo de destinos de forma uniforme.",
            "PlaceGroup agrupa Places y/o grupos hijos; un grupo de entregas se navega como objetivo unico.",
        ],
    ]
    story.append(make_table(patrones, col_widths=[2.2 * cm, 4.3 * cm, 9.3 * cm]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Justificacion de pertinencia", S["h2"]))
    story.append(bullets([
        ("Strategy", "permite comparar algoritmos en el mismo prototipo y cambiar de politica de navegacion en tiempo de ejecucion (eficiencia y extensibilidad)."),
        ("Observer", "sustenta la optimizacion reactiva: el sistema detecta la marea y propone la mejor ruta nueva sin que el usuario pida recalculos."),
        ("Command", "da robustez operativa: un conductor puede deshacer una accion erronea (cambio de destino) y volver a la ruta previa."),
        ("Iterator", "separa la navegacion del cliente: la capa de presentacion consume pasos desacoplados de la estructura interna de la ruta."),
        ("Composite", "habilita flotas y entregas por zonas: un corredor comercial o una zona de despacho se tratan como un solo destino agregado."),
    ]))
    story.append(Paragraph("Correspondencia con el diagrama de clases", S["h2"]))
    story.append(p(
        "El diagrama de clases (seccion 3.3) anota cada relacion con su patron: RoutePlanner "
        "compone RouteStrategy (Strategy); TrafficControlCenter mantiene observadores (Observer); "
        "CommandHistory apila Command (Command); Route crea RouteIterator que produce RouteStep "
        "(Iterator); PlaceGroup contiene Place o PlaceGroup (Composite).",
    ))
    story.append(PageBreak())

    # ---------------- 5. PROTOTIPO ----------------
    story.append(Paragraph("5. Implementacion del prototipo", S["h1"]))
    story.append(Paragraph("5.1 Stack y estructura", S["h2"]))
    story.append(p(
        "Prototipo en <b>Python 3 (libreria estandar)</b>, sin dependencias externas para el "
        "nucleo. El repositorio organiza el paquete navigation/ por responsabilidades (domain, "
        "traffic, routing, commands, iterator, facade, city_map) y separa benchmarks, pruebas y "
        "documentacion UML.",
    ))
    story.append(make_table([
        ["Archivo", "Responsabilidad"],
        ["navigation/domain.py", "Grafo, Place, PlaceGroup (Composite), RoadSegment y Route."],
        ["navigation/routing.py", "RoutePlanner y las cinco estrategias (Strategy)."],
        ["navigation/traffic.py", "TrafficControlCenter y observadores (TrafficLogger)."],
        ["navigation/commands.py", "Command, ChangeDestinationCommand, RerouteCommand y CommandHistory."],
        ["navigation/iterator.py", "RouteIterator y Modelo RouteStep."],
        ["navigation/facade.py", "Navigator: fachada que integra los patrones y observa el trafico."],
        ["navigation/city_map.py", "Mapa urbano de 16 lugares y generador de mallas aleatorias."],
        ["benchmarks/run_benchmarks.py", "Metricas de 30 pares OD x 5 estrategias x 2 escenarios."],
    ]))
    story.append(Paragraph("5.2 Extraccion de la salida de la demo", S["h2"]))
    demo = (RESULTS / "demo_salida.txt").read_text(encoding="utf-8", errors="replace")
    lines = demo.splitlines()
    keep = []
    capture = False
    for ln in lines:
        if "[4]" in ln:
            capture = True
        if capture:
            keep.append(ln)
        if len(keep) > 16:
            break
    story.append(make_table(
        [["Salida de consola - comparacion de estrategias (UNAB -> Estadio)"]],
        col_widths=[16.6 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("    " + "<br/>    ".join(esc(ln) for ln in keep), st("mono", fontName="Courier", fontSize=7.5, leading=9.5)))
    story.append(Spacer(1, 0.2 * cm))
    story.append(p(
        "La salida muestra el valor central del prototipo: la estrategia en vivo elige la "
        "ruta periferica (anillo) y ahorra minutos frente a la ruta de minima distancia, que "
        "queda atrapada en el centro congestionado.",
    ))
    story.append(PageBreak())

    # ---------------- 6. PRUEBAS ----------------
    story.append(Paragraph("6. Pruebas y resultados", S["h1"]))
    story.append(Paragraph("6.1 Pruebas unitarias", S["h2"]))
    story.append(p(
        "Se disenaron 11 pruebas unitarias (unittest, Python). Cubren: optimo conocido de "
        "Dijkstra, equivalencia A* = Dijkstra en vivo, ventaja de la ruta en vivo frente a la "
        "de minima distancia bajo marea, notificacion de observadores, activacion de la bandera "
        "de replanificacion, comportamiento de undo en Command, orden del RouteIterator y "
        "recorrido del Composite. Todas pasan en ejecucion.",
    ))
    story.append(Paragraph("6.2 Benchmark", S["h2"]))
    story.append(p(
        f"Se construyo una malla urbana de {BENCH['hallazgos']['nodos_grafo']} nodos con avenidas "
        f"rapidas cada tres lineas y calles locales. Se evaluaron 30 pares origen-destino por "
        f"estrategia en dos escenarios (sin marea y con marea de trafico).",
    ))
    for scenario, label in (("sin_marea", "Escenario: sin marea"), ("con_marea", "Escenario: con marea")):
        story.append(Paragraph(f"{label}", S["h2"]))
        data = [["Estrategia", "km avg", "min avg", "nodos avg", "ms avg", "ms max"]]
        for r in BENCH[scenario]:
            data.append([
                r["strategy"],
                f"{r['avg_distance_km']:.2f}",
                f"{r['avg_time_min']:.2f}",
                f"{r['avg_nodes_expanded']:.1f}",
                f"{r['avg_exec_ms']:.3f}",
                f"{r['max_exec_ms']:.3f}",
            ])
        story.append(make_table(data))
        story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("6.3 Graficos comparativos", S["h2"]))
    cats = list(BENCH["sin_marea"][i]["strategy"] for i in range(5))
    time_sin = [BENCH["sin_marea"][i]["avg_time_min"] for i in range(5)]
    time_con = [BENCH["con_marea"][i]["avg_time_min"] for i in range(5)]
    nodes_sin = [BENCH["sin_marea"][i]["avg_nodes_expanded"] for i in range(5)]
    nodes_con = [BENCH["con_marea"][i]["avg_nodes_expanded"] for i in range(5)]
    story.append(p("Figura 5 - Tiempo promedio de ruta por estrategia y escenario.", "caption"))
    story.append(loading_bar_chart(
        cats,
        [time_sin, time_con],
    ))
    story.append(p("Azul: sin marea | Rojo: con marea (minutos).", "caption"))
    story.append(Spacer(1, 0.2 * cm))
    story.append(p("Figura 6 - Nodos expandidos promedio por estrategia y escenario.", "caption"))
    story.append(loading_bar_chart(
        cats,
        [nodes_sin, nodes_con],
    ))
    story.append(p("Azul: sin marea | Rojo: con marea (nodos).", "caption"))
    story.append(Paragraph("6.4 Interpretacion", S["h2"]))
    h = BENCH["hallazgos"]
    story.append(bullets([
        (f"Ahorro de la ruta en vivo bajo marea: {h['ahorro_marea_min']} min promedio", "frente a la ruta de minima distancia, con recorridos ligeramente mas largos."),
        (f"Ahorro sin marea: {h['ahorro_sin_marea_min']} min promedio", "configirma que la distancia corta no es sinonimo de tiempo corto."),
        (f"Reduccion de nodos expandidos con A*: {h['reduccion_nodos_astar_pct']}%", "A* obtiene exactamente el mismo camino optimo que Dijkstra, con menor exploracion."),
        (f"Mejora en vivo vs plan estatico bajo marea: {h['mejora_vivo_vs_plano_pct']}%", "la politica reactiva supera al plan que ignora la congestion."),
    ]))
    story.append(PageBreak())

    # ---------------- 7. RUBRICA ----------------
    story.append(Paragraph("7. Validacion frente a la rubrica", S["h1"]))
    story.append(make_table([
        ["Criterio", "Como se evidencia"],
        ["Claridad y precision del problema", "Seccion 1: problema delimitado (rutas suboptimas por mareas de trafico) con impacto en UX, rendimiento y operacion."],
        ["Calidad del diseno UML", "Seccion 3: diagramas de componentes, clases, secuencia y actividad generados con PlantUML y referenciados con sus patrones."],
        ["Aplicacion de patrones de diseno", "Seccion 4: cinco patrones implementados, justificados y anotados sobre el diagrama de clases."],
        ["Calidad del prototipo", "Secciones 5 y 6: prototipo funcional con demo, 11 pruebas unitarias y benchmark reproducible."],
        ["Presentacion y documentacion", "Este informe (PDF), presentacion adjunta y video de demostracion (enlace privado)."],
    ]))
    story.append(PageBreak())

    # ---------------- 8. CONCLUSIONES ----------------
    story.append(Paragraph("8. Conclusiones y trabajo futuro", S["h1"]))
    story.append(bullets([
        ("Conclusion 1", "La separacion de estrategias via Strategy convierte el ruteo en una politica intercambiable: el mismo nucleo produce rutas por distancia, tiempo plano, tiempo en vivo o heuristica, lo que facilita comparar costos y cuantificar la optimizacion."),
        ("Conclusion 2", "El Observer fue decisivo para la optimizacion reactiva: subir la congestion de un tramo detona la replanificacion sin intervencion del usuario, reduciendo el tiempo real del trayecto."),
        ("Conclusion 3", "A* demostro ser tan optimo como Dijkstra en tiempo bajo marea y reducir cerca de un tercio de los nodos explorados, un beneficio directo de latencia y escalabilidad."),
        ("Conclusion 4", "Command, Iterator y Composite mejoraron la usabilidad y extensibilidad: undo de acciones, navegacion paso a paso desacoplada y navegacion por grupos de destinos."),
        ("Trabajo futuro", "Incorporar grafos jerarquicos (contraccion), actualizar congestion con datos historicos y en vivo, integrar persistencia de rutas y expone el nucleo como servicio REST para evaluar latencia bajo carga."),
    ]))
    story.append(PageBreak())

    # ---------------- REFERENCIAS ----------------
    story.append(Paragraph("Referencias", S["h1"]))
    refs = [
        "Gamma, E., Helm, R., Johnson, R., y Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley.",
        "Teniente Lopez, E., Costal Costa, D., y Sancho Samso, M. R. (2015). Especificacion de sistemas software en UML. Universitat Politecnica de Catalunya. https://elibro.net/es/ereader/tecnologicadeloriente/61407",
        "Blas, M. J., Leone, H. P., y Gonnet, S. M. (2019). Modelado y verificacion de patrones de diseno de arquitectura de software para entornos de computacion en la nube. CONICET. https://ri.conicet.gov.ar/handle/11336/125130",
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L., y Stein, C. (2009). Introduction to Algorithms (3a ed.). MIT Press. [Dijkstra, A* y estructuras para caminos minimos]",
    ]
    for i, ref in enumerate(refs, 1):
        story.append(Paragraph(f"[{i}] {esc(ref)}", st("ref", fontSize=9, leading=13, spaceAfter=6, alignment=TA_JUSTIFY)))
    story.append(PageBreak())

    # ---------------- ANEXO ----------------
    story.append(Paragraph("Anexo A: comandos y reproduccion de resultados", S["h1"]))
    story.append(Paragraph("    python -m navigation.demo<br/>    python -m unittest discover -s tests<br/>    python -m benchmarks.run_benchmarks", st("mono2", fontName="Courier", fontSize=9, leading=14)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(p(
        "El archivo docs/results/benchmark.json contiene las metricas detalladas por par "
        "origen-destino y por estrategia; los diagramas UML (PlantUML) residen en docs/uml/ "
        "tanto en formato fuente (.puml) como en PNG listos para el informe.",
    ))

    doc.build(story, onFirstPage=numbered_page, onLaterPages=header_footer)
    print(f"Informe generado: {OUT.resolve()}")


if __name__ == "__main__":
    build()