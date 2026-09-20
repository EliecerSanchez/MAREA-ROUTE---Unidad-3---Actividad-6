"""Genera la presentacion en PowerPoint (.pptx) para la Actividad 6.

Ejecutar: python docs/presentacion/build_pptx.py
Requisito: pip install python-pptx
"""

from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

BASE = Path(__file__).resolve().parent.parent.parent
UML = BASE / "docs" / "uml"
RESULTS = BASE / "docs" / "results"
OUT = BASE / "docs" / "presentacion" / "Presentacion_Actividad6.pptx"

BENCH = json.loads((RESULTS / "benchmark.json").read_text(encoding="utf-8"))

NAVY = RGBColor(0x0B, 0x3D, 0x66)
BLUE2 = RGBColor(0x17, 0x5E, 0x8C)
GRAY = RGBColor(0x59, 0x6A, 0x75)
SOFT = RGBColor(0x9F, 0xB6, 0xC9)
DARK = RGBColor(0x21, 0x2C, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

NAMES = ["DIRECTOX1", "DIRECTOX2"]
DOCENTE = "Edward Alfonso Villamizar Vallejo"
EQUIPO = "Omar Vallejo, David Mape, Eliécer Sanchez, Daniel Rodriguez, Volmar Rincon"
ROLES = "Omar: lider; David y Eliécer: arquitectura y UML; Daniel: desarrollador; Volmar: evaluador"


def big_bullets(tf, items, first):
    for item in items:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.line_spacing = 1.15
        p.space_after = Pt(9)
        r0 = p.add_run()
        r0.text = "\u2022  "
        r0.font.size = Pt(15)
        r0.font.color.rgb = NAVY
        r0.font.bold = True
        if isinstance(item, tuple):
            lead, rest = item
            r1 = p.add_run()
            r1.text = lead + " "
            r1.font.size = Pt(15)
            r1.font.bold = True
            r1.font.color.rgb = DARK
            text = rest
        else:
            text = item
        r2 = p.add_run()
        r2.text = text
        r2.font.size = Pt(15)
        r2.font.color.rgb = DARK
    return first


def add_textbox(slide, l, t, w, h):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def kicker_title(slide, kick, title):
    k = add_textbox(slide, 0.62, 0.30, 12.1, 0.45)
    p = k.paragraphs[0]
    run = p.add_run()
    run.text = kick
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = GRAY
    t = add_textbox(slide, 0.62, 0.70, 12.1, 0.9)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.size = Pt(31)
    run.font.bold = True
    run.font.color.rgb = NAVY


def add_table(slide, data, left, top, width, col_widths=None, font=12):
    rows, cols = len(data), len(data[0])
    frame = slide.shapes.add_table(rows, cols, Inches(left), Inches(top), Inches(width), Inches(0.5 * rows))
    table = frame.table
    table.first_row = True
    table.horz_banding = False
    for j in range(cols):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = data[0][j]
        run.font.bold = True
        run.font.size = Pt(font)
        run.font.color.rgb = WHITE
    for i in range(1, rows):
        for j in range(cols):
            cell = table.cell(i, j)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = data[i][j]
            run.font.size = Pt(font)
            run.font.color.rgb = DARK
    if col_widths:
        for j, w in enumerate(col_widths):
            table.columns[j].width = Inches(w)
    return table


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ---------- Slide 1 portada ----------
    s = new_slide(prs)
    spacer = add_textbox(s, 0.6, 1.5, 12.1, 0.5)
    p = spacer.paragraphs[0]
    run = p.add_run()
    run.text = "Arquitectura de Software - U3"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = GRAY

    t = add_textbox(s, 0.6, 2.1, 12.1, 1.4)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = "MAREA ROUTE"
    run.font.size = Pt(60)
    run.font.bold = True
    run.font.color.rgb = NAVY

    t = add_textbox(s, 0.6, 3.5, 12.1, 0.6)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = "Estrategias de navegacion en la arquitectura de software"
    run.font.size = Pt(24)
    run.font.color.rgb = BLUE2

    t = add_textbox(s, 0.6, 4.15, 12.1, 0.5)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = "Actividad 6 - Navegando mareas   |   Septiembre 2026"
    run.font.size = Pt(15)
    run.font.color.rgb = GRAY

    add_table(
        s,
        [
            ["Equipo", EQUIPO],
            ["Roles", ROLES],
            ["Docente", DOCENTE],
        ],
        1.3, 5.3, 10.7, col_widths=[2.6, 8.1], font=13,
    )

    # ---------- Slide 2 problema ----------
    s = new_slide(prs)
    kicker_title(s, "MARCO DEL PROBLEMA", "Rutas suboptimas cuando el trafico cambia")
    big_bullets(
        add_textbox(s, 0.7, 2.0, 12.0, 4.8),
        [
            ("Problema:", "los mapas calculan la ruta mas corta o rapida sobre un plan estatico de la red."),
            ("Marea de trafico:", "en horas pico la congestion satura calles centrales con apariencia de atajo."),
            ("Ocurre que:", "la ruta de menor distancia no es la mas rapida en minutos reales."),
            ("Pregunta:", "como arquitecturar un navegador para que la estrategia sea intercambiable, reaccione a la congestion y presente el recorrido de forma extensible?"),
        ],
        True,
    )

    # ---------- Slide 3 impacto ----------
    s = new_slide(prs)
    kicker_title(s, "RELEVANCIA", "Impacto en tres dimensiones")
    big_bullets(
        add_textbox(s, 0.7, 2.0, 12.0, 4.8),
        [
            ("Experiencia de usuario:", "menos tiempo de viaje, menos estres, instrucciones claras paso a paso."),
            ("Rendimiento del sistema:", "A* reduce nodos explorados y la latencia del servicio de mapas."),
            ("Eficiencia operativa:", "flotas y entregas ahorran combustible y horas-hombre con replanificacion en vivo."),
            ("Escalabilidad:", "nuevas estrategias de ruteo se agregan sin tocar el nucleo (interfaz RouteStrategy)."),
        ],
        True,
    )

    # ---------- Slide 4 arquitectura ----------
    s = new_slide(prs)
    kicker_title(s, "ARQUITECTURA", "Capas con fachada central y patrones desacoplados")
    add_table(
        s,
        [
            ["Capa", "Rol", "Patrones"],
            ["Presentacion (CLI)", "Demo por consola", "-"],
            ["Aplicacion", "Navigator (fachada) + CommandHistory", "Facade, Observer, Command"],
            ["Logica de ruteo", "RoutePlanner, RouteStrategy, grafo y rutas", "Strategy, Composite, Iterator"],
            ["Infraestructura", "TrafficControlCenter, metricas", "Observer"],
        ],
        0.7, 2.1, 12.0, col_widths=[3.2, 5.4, 3.4], font=13,
    )
    note = add_textbox(s, 0.7, 6.0, 12.0, 0.6)
    p = note.paragraphs[0]
    run = p.add_run()
    run.text = "Regla: las dependencias apuntan a interfaces y los patrones se modelan antes en UML."
    run.font.size = Pt(12)
    run.font.italic = True
    run.font.color.rgb = GRAY

    # ---------- Slides 5-8 UML ----------
    for titulo, archivo, nota in [
        ("Diagrama de componentes", "componentes.png", "Estructura y conectores entre capas."),
        ("Diagrama de clases", "clases.png", "Colaboracion de los cinco patrones."),
        ("Diagrama de secuencia", "secuencia.png", "Solicitud de ruta, notificacion y replanificacion."),
        ("Diagrama de actividad", "actividad.png", "Flujo completo: de la solicitud a la navegacion paso a paso."),
    ]:
        s = new_slide(prs)
        kicker_title(s, "MODELADO UML", titulo)
        img = s.shapes.add_picture(str(UML / archivo), Inches(0.7), Inches(1.8), width=Inches(11.9))
        note = add_textbox(s, 0.7, 6.9, 12.0, 0.5)
        p = note.paragraphs[0]
        run = p.add_run()
        run.text = nota
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = GRAY

    # ---------- Slide 9 patrones ----------
    s = new_slide(prs)
    kicker_title(s, "PATRONES DE DISENO", "Cinco patrones para navegar optimamente")
    add_table(
        s,
        [
            ["Patron", "Aplicacion en MAREA ROUTE"],
            ["Strategy", "RoutePlanner conmuta Dijkstra, A* y modo en vivo (marea)."],
            ["Observer", "TrafficControlCenter notifica a Navigator; activa replanificacion."],
            ["Command", "RerouteCommand / ChangeDestinationCommand con undo en CommandHistory."],
            ["Iterator", "RouteIterator entrega instrucciones paso a paso desacopladas."],
            ["Composite", "PlaceGroup navega grupos de destinos como un unico destino."],
        ],
        0.7, 2.1, 12.0, col_widths=[2.6, 9.4], font=14,
    )

    # ---------- Slide 10 prototipo ----------
    s = new_slide(prs)
    kicker_title(s, "PROTOTIPO", "Python 3 estandar, reproducible y probado")
    demo = (RESULTS / "demo_salida.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    keep = []
    cap = False
    for ln in demo:
        if "[4]" in ln:
            cap = True
        if cap:
            keep.append(ln)
        if len(keep) > 9:
            break
    consolas = add_textbox(s, 0.7, 2.0, 12.0, 2.6)
    first = True
    for ln in keep:
        if first:
            p = consolas.paragraphs[0]
            first = False
        else:
            p = consolas.add_paragraph()
        run = p.add_run()
        run.text = ln
        run.font.name = "Consolas"
        run.font.size = Pt(10)
        run.font.color.rgb = DARK
        p.space_after = Pt(1)
    big_bullets(
        add_textbox(s, 0.7, 4.8, 12.0, 2.4),
        [
            ("11 pruebas unitarias:", "optimo de Dijkstra, A* == Dijkstra en vivo, Observer, Command, Iterator y Composite."),
            ("Reproduccion:", "python -m navigation.demo  |  python -m unittest discover -s tests  |  python -m benchmarks.run_benchmarks"),
        ],
        True,
    )

    # ---------- Slide 11 resultados ----------
    s = new_slide(prs)
    kicker_title(s, "RESULTADOS DEL BENCHMARK", "Metricas: 30 pares OD x 5 estrategias x 2 escenarios")
    data = [["Estrategia", "km", "min (marea)", "nodos", "ms"]]
    for r in BENCH["con_marea"]:
        data.append([r["strategy"], f"{r['avg_distance_km']:.2f}", f"{r['avg_time_min']:.2f}", f"{r['avg_nodes_expanded']:.1f}", f"{r['avg_exec_ms']:.3f}"])
    add_table(s, data, 0.7, 2.0, 9.0, col_widths=[3.0, 1.5, 1.5, 1.5, 1.5], font=13)
    h = BENCH["hallazgos"]
    big_bullets(
        add_textbox(s, 10.0, 2.0, 2.9, 4.8),
        [
            (f"Ahorro vivo vs minima (marea):", f"{h['ahorro_marea_min']} min promedio."),
            (f"A* expande {h['reduccion_nodos_astar_pct']}% menos nodos:", "mismo camino optimo que Dijkstra."),
            (f"Vivo supera al plan estatico en {h['mejora_vivo_vs_plano_pct']}%", "durante la marea."),
        ],
        True,
    )

    # ---------- Slide 12 conclusiones ----------
    s = new_slide(prs)
    kicker_title(s, "CONCLUSIONES", "Optimizar no es solo acortar distancias")
    big_bullets(
        add_textbox(s, 0.7, 2.0, 12.0, 4.0),
        [
            "La arquitectura por capas + fachada aislaron algoritmos, trafico y presentacion.",
            "Strategy hizo medible la optimizacion: el modo en vivo gana durante la marea.",
            "Observer permitio replanificar sin intervencion del usuario.",
            "Command, Iterator y Composite sumaron usabilidad y extensiones sin tocar el nucleo.",
            "Trabajo futuro: grafos jerarquicos, dato historico/en vivo y API REST de rutas.",
        ],
        True,
    )
    note = add_textbox(s, 0.7, 6.5, 12.0, 0.6)
    p = note.paragraphs[0]
    run = p.add_run()
    run.text = "Video de demostracion: enlace privado (YouTube) incluido en el informe y el LMS."
    run.font.size = Pt(13)
    run.font.italic = True
    run.font.color.rgb = GRAY

    # ---------- Slide 13 cierre ----------
    s = new_slide(prs)
    t = add_textbox(s, 0.6, 1.8, 12.1, 1.0)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = "Reproduccion y evidencias"
    run.font.size = Pt(30)
    run.font.bold = True
    run.font.color.rgb = NAVY
    t = add_textbox(s, 0.7, 3.1, 12.0, 1.8)
    for i, cmd in enumerate([
        "python -m navigation.demo",
        "python -m unittest discover -s tests",
        "python -m benchmarks.run_benchmarks",
    ]):
        p = t.paragraphs[0] if i == 0 else t.add_paragraph()
        run = p.add_run()
        run.text = cmd
        run.font.name = "Consolas"
        run.font.size = Pt(16)
        run.font.color.rgb = BLUE2
        p.space_after = Pt(8)
    t = add_textbox(s, 0.7, 5.1, 12.0, 0.8)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = "Evidencias: UML en docs/uml/, metricas en docs/results/benchmark.json, informe en docs/informe/."
    run.font.size = Pt(14)
    run.font.color.rgb = DARK
    t = add_textbox(s, 0.6, 6.3, 12.1, 1.0)
    p = t.paragraphs[0]
    run = p.add_run()
    run.text = "Gracias"
    run.font.size = Pt(34)
    run.font.bold = True
    run.font.color.rgb = NAVY

    prs.save(str(OUT))
    print(f"Presentacion PPTX generada: {OUT.resolve()}")


if __name__ == "__main__":
    build()