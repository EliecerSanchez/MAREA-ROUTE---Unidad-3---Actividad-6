"""Genera la presentacion (PDF de diapositivas) de la Actividad 6.

Ejecutar: python docs/presentacion/build_slides.py
Requisito: pip install reportlab
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE = Path(__file__).resolve().parent.parent.parent
UML = BASE / "docs" / "uml"
RESULTS = BASE / "docs" / "results"
OUT = BASE / "docs" / "presentacion" / "Presentacion_Actividad6.pdf"

BENCH = json.loads((RESULTS / "benchmark.json").read_text(encoding="utf-8"))

PAGE_W, PAGE_H = landscape(A4)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


styles = getSampleStyleSheet()


def st(name, **kw):
    return ParagraphStyle(name, **kw)


S = {
    "title": st("pt", fontName="Helvetica-Bold", fontSize=30, leading=34, textColor=colors.HexColor("#0b3d66")),
    "kicker": st("pk", fontName="Helvetica", fontSize=13, leading=16, textColor=colors.HexColor("#596a75")),
    "h2": st("ph2", fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=colors.HexColor("#0b3d66"), spaceAfter=10),
    "body": st("pb", fontSize=13, leading=18, alignment=TA_LEFT, spaceAfter=6),
    "bullet": st("pbu", fontSize=12.5, leading=17, spaceAfter=5),
    "small": st("psm", fontSize=9, leading=12, textColor=colors.grey),
}


def bullets(items):
    from reportlab.platypus import ListFlowable, ListItem

    flow = []
    for it in items:
        if isinstance(it, tuple):
            flow.append(ListItem(Paragraph(f"<b>{esc(it[0])}</b> {esc(it[1])}", S["bullet"])))
        else:
            flow.append(ListItem(Paragraph(esc(it), S["bullet"])))
    return ListFlowable(flow, bulletType="bullet", bulletFontSize=8, leftIndent=16, bulletColor=colors.HexColor("#0b3d66"))


def slide_title(kicker, title):
    return [Paragraph(esc(kicker), S["kicker"]), Spacer(1, 0.1 * cm), Paragraph(esc(title), S["title"]), Spacer(1, 0.5 * cm)]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#7f8c8d"))
    canvas.drawString(1.3 * cm, 0.9 * cm, "MAREA ROUTE - U3 Actividad 6")
    canvas.drawRightString(PAGE_W - 1.3 * cm, 0.9 * cm, f"{doc.page}")
    canvas.restoreState()


def make_table(data):
    t = Table(data, hAlign="LEFT")
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9fb6c9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d66")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=landscape(A4),
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.6 * cm,
        title="Presentacion Actividad 6",
        author="Equipo Arquitectura de Software",
    )
    story = []

    # Slide 1 portada
    story.append(Spacer(1, 2.6 * cm))
    story.append(Paragraph("Arquitectura de Software - U3", S["kicker"]))
    story.append(Paragraph("MAREA ROUTE", st("t0", fontName="Helvetica-Bold", fontSize=48, leading=54, textColor=colors.HexColor("#0b3d66"))))
    story.append(Paragraph("Estrategias de navegacion en la arquitectura de software", S["title"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(esc("Actividad 6 - Navegando mareas  |  Septiembre 2026"), S["kicker"]))
    story.append(Spacer(1, 1.4 * cm))
    story.append(make_table([
        ["Equipo", "Integrantes (3-4)"],
        ["Roles", "Lider / Disenador UML / Programador / Investigador"],
        ["Docente", "(nombre del docente)"],
    ]))
    story.append(PageBreak())

    # Slide 2 problema
    story.extend(slide_title("MARCO DEL PROBLEMA", "Rutas suboptimas cuando el trafico cambia"))
    story.append(bullets([
        ("Problema:", "los mapas calculan la ruta mas corta/rapida sobre un plan estatico de la red."),
        ("Marea de trafico:", "en horas pico la congestion satura calles centrales con apariencia de atajo."),
        ("Comun:", "la ruta de menor distancia no es la mas rapida en minutos reales."),
        ("Pregunta:", "como arquitecturar un navegador para que la estrategia sea intercambiable, reaccione a la congestion y presente el recorrido de forma extensible?"),
    ]))
    story.append(PageBreak())

    # Slide 3 impacto
    story.extend(slide_title("RELEVANCIA", "Impacto en tres dimensiones"))
    story.append(bullets([
        ("Experiencia de usuario:", "menos tiempo de viaje, menos estres, instrucciones claras paso a paso."),
        ("Rendimiento del sistema:", "A* reduce nodos explorados y la latencia del servicio de mapas."),
        ("Eficiencia operativa:", "flotas y entregas ahorran combustible y horas-hombre con replanificacion en vivo."),
        ("Escalabilidad:", "nuevas estrategias de ruteo se agregan sin tocar el nucleo (interfaz RouteStrategy)."),
    ]))
    story.append(PageBreak())

    # Slide 4 arquitectura
    story.extend(slide_title("ARQUITECTURA", "Capas con fachada central y patrones desacoplados"))
    stories_lines = [
        ["Capa", "Rol", "Patrones"],
        ["Presentacion (CLI)", "Demo por consola", "-"],
        ["Aplicacion", "Navigator (fachada) + CommandHistory", "Facade, Observer, Command"],
        ["Logica de ruteo", "RoutePlanner, RouteStrategy, grafo y rutas", "Strategy, Composite, Iterator"],
        ["Infraestructura", "TrafficControlCenter, metricas", "Observer"],
    ]
    story.append(make_table(stories_lines))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(esc("Regla: las dependencias apuntan a interfaces y los patrones se modelan antes en UML."), S["small"]))
    story.append(PageBreak())

    for titulo, archivo, nota in [
        ("Diagrama de componentes", "componentes.png", "Estructura y conectores entre capas."),
        ("Diagrama de clases", "clases.png", "Colaboracion de los cinco patrones."),
        ("Diagrama de secuencia", "secuencia.png", "Solicitud de ruta, notificacion y replanificacion."),
    ]:
        story.extend(slide_title("MODELADO UML", titulo))
        story.append(Image(str(UML / archivo), width=26.4 * cm, height=15.4 * cm))
        story.append(Paragraph(esc(nota), S["small"]))
        story.append(PageBreak())

    # Slide 8 patrones
    story.extend(slide_title("PATRONES DE DISENO", "Cinco patrones para navegar optimamente"))
    patrones = [
        ["Patron", "Aplicacion en MAREA ROUTE"],
        ["Strategy", "RoutePlanner conmuta Dijkstra, A* y modo en vivo (marea)."],
        ["Observer", "TrafficControlCenter notifica a Navigator; activa replanificacion."],
        ["Command", "RerouteCommand / ChangeDestinationCommand con undo en CommandHistory."],
        ["Iterator", "RouteIterator entrega instrucciones paso a paso desacopladas."],
        ["Composite", "PlaceGroup navega grupos de destinos como un unico destino."],
    ]
    story.append(make_table(patrones))
    story.append(PageBreak())

    # Slide 9 prototipo
    story.extend(slide_title("PROTOTIPO", "Python 3 estandar, reproducible y probado"))
    demo = (RESULTS / "demo_salida.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    keep = []
    cap = False
    for ln in demo:
        if "[4]" in ln:
            cap = True
        if cap:
            keep.append(ln)
        if len(keep) > 10:
            break
    story.append(Paragraph("    " + "<br/>    ".join(esc(ln) for ln in keep), st("mono", fontName="Courier", fontSize=8.5, leading=11)))
    story.append(Spacer(1, 0.25 * cm))
    story.append(bullets([
        ("11 pruebas unitarias:", "optimo de Dijkstra, A* == Dijkstra en vivo, Observer, Command, Iterator, Composite."),
        ("Reproduccion:", "python -m navigation.demo | python -m unittest discover -s tests | python -m benchmarks.run_benchmarks"),
    ]))
    story.append(PageBreak())

    # Slide 10 resultados
    story.extend(slide_title("RESULTADOS DEL BENCHMARK", "Metricas: 30 pares OD x 5 estrategias x 2 escenarios"))
    data = [["Estrategia", "km", "min (marea)", "nodos", "ms"]]
    for r in BENCH["con_marea"]:
        data.append([r["strategy"], f"{r['avg_distance_km']:.2f}", f"{r['avg_time_min']:.2f}", f"{r['avg_nodes_expanded']:.1f}", f"{r['avg_exec_ms']:.3f}"])
    story.append(make_table(data))
    story.append(Spacer(1, 0.25 * cm))
    h = BENCH["hallazgos"]
    story.append(bullets([
        (f"Ahorro en vivo vs minima distancia (marea): {h['ahorro_marea_min']} min", "promedio por viaje, con recorridos ligeramente mayores."),
        (f"A* expande {h['reduccion_nodos_astar_pct']}% menos nodos", "para el mismo camino optimo que Dijkstra."),
        (f"Ruta en vivo supera al plan estatico en {h['mejora_vivo_vs_plano_pct']}%", "durante la marea."),
    ]))
    story.append(PageBreak())

    # Slide 11 conclusiones
    story.extend(slide_title("CONCLUSIONES", "Optimizar no es solo acortar distancias"))
    story.append(bullets([
        "La arquitectura por capas + fachada aislaron algoritmos, trafico y presentacion.",
        "Strategy hizo medible la optimizacion: el modo en vivo gana durante la marea.",
        "Observer permitio replanificar sin intervencion del usuario.",
        "Command, Iterator y Composite sumaron usabilidad y extensiones sin tocar el nucleo.",
        "Trabajo futuro: grafos jerarquicos, dato historico/en vivo y API REST de rutas.",
    ]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(esc("Video de demostracion: enlace privado (YouTube) incluido en el informe y el LMS."), S["small"]))
    story.append(PageBreak())

    # Slide 12 reproduccion
    story.append(Spacer(1, 2.0 * cm))
    story.append(Paragraph("Reproduccion y evidencias", S["title"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("    python -m navigation.demo<br/>    python -m unittest discover -s tests<br/>    python -m benchmarks.run_benchmarks", st("mono2", fontName="Courier", fontSize=16, leading=26)))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(esc("Evidencias: diagramas UML en docs/uml/, metricas en docs/results/benchmark.json, informe en docs/informe/."), S["body"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(esc("Gracias."), S["title"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Presentacion generada: {OUT.resolve()}")


if __name__ == "__main__":
    build()