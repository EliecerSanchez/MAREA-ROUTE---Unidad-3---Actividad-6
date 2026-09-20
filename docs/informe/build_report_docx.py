"""Genera el informe tecnico en formato Word editable (.docx).

Ejecutar: python docs/informe/build_report_docx.py
Requisito: pip install python-docx
"""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

BASE = Path(__file__).resolve().parent.parent.parent
UML = BASE / "docs" / "uml"
RESULTS = BASE / "docs" / "results"
OUT = BASE / "docs" / "informe" / "Informe_Actividad6.docx"

BENCH = json.loads((RESULTS / "benchmark.json").read_text(encoding="utf-8"))
JSON_BENCH = json.dumps(BENCH, ensure_ascii=False, indent=2)

AZUL = RGBColor(0x0B, 0x3D, 0x66)
AZUL2 = RGBColor(0x17, 0x5E, 0x8C)
GRIS = RGBColor(0x59, 0x6A, 0x75)


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def build():
    doc = Document()

    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    for stl, size, color, bold in (
        ("Heading 1", 16, AZUL, True),
        ("Heading 2", 13, AZUL2, True),
        ("Heading 3", 11, AZUL2, False),
        ("Title", 28, AZUL, True),
    ):
        st = doc.styles[stl]
        st.font.name = "Calibri"
        st.font.size = Pt(size)
        st.font.color.rgb = color
        st.font.bold = bold

    def p(text, style=None, size=None, bold=None, italic=None, align=None, color=None, space_after=None):
        par = doc.add_paragraph(style=style)
        run = par.add_run(text)
        if size:
            run.font.size = Pt(size)
        if bold is not None:
            run.font.bold = bold
        if italic is not None:
            run.font.italic = italic
        if color is not None:
            run.font.color.rgb = color
        if align is not None:
            par.alignment = align
        if space_after is not None:
            par.paragraph_format.space_after = Pt(space_after)
        par.paragraph_format.line_spacing = 1.15
        return par

    def bullets(items, style="List Bullet"):
        for it in items:
            if isinstance(it, tuple):
                lead, rest = it
                par = doc.add_paragraph(style=style)
                r1 = par.add_run(lead + " ")
                r1.font.bold = True
                par.add_run(rest)
            else:
                doc.add_paragraph(it, style=style)

    def add_table(headers, rows, widths=None, header_fill="0B3D66"):
        table = doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        for j, h in enumerate(headers):
            cell = table.rows[0].cells[j]
            cell.text = ""
            run = cell.paragraphs[0].add_run(h)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.size = Pt(10)
            shade_cell(cell, header_fill)
        for i, row in enumerate(rows, start=1):
            for j, val in enumerate(row):
                cell = table.rows[i].cells[j]
                cell.text = ""
                run = cell.paragraphs[0].add_run(str(val))
                run.font.size = Pt(10)
        if widths:
            for j, w in enumerate(widths):
                for row in table.rows:
                    row.cells[j].width = Cm(w)
        return table

    def divider():
        p("", size=2, space_after=2)
        p("_" * 90, size=8, color=GRIS, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    def caption(text):
        p(text, size=9, italic=True, color=GRIS, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    # ------------------ PORTADA ------------------
    p("Arquitectura de Software", size=16, bold=True, color=AZUL, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    p("Unidad 3 - Evaluacion y optimizacion de arquitecturas", size=12, color=GRIS, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
    p("MAREA ROUTE", size=34, bold=True, color=AZUL, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p("Estrategias de navegacion en la arquitectura de software", size=17, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    p("Actividad 6 - Navegando mareas", size=13, color=GRIS, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)
    add_table(
        ["Campo", "Valor"],
        [
            ["Curso", "Arquitectura de Software 20262 - N5 GrB"],
            ["Docente", "Edward Alfonso Villamizar Vallejo"],
            ["Equipo", "Omar Vallejo (coordinacion y plan) / David Mape y Eliécer Sanchez (arquitectura y UML) / Daniel Rodriguez (desarrollador) / Volmar Rincon (pruebas de carga y robustez)"],
            ["Fecha", "Septiembre de 2026"],
        ],
        widths=[4.0, 12.4],
    )
    doc.add_page_break()

    # ------------------ INDICE ------------------
    doc.add_heading("Indice", level=1)
    for item in [
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
    ]:
        p(item, size=11, space_after=4)
    p("Nota: para actualizar el indice automatico en Word, Inserte la referencia -> Tabla de contenido.", size=9, italic=True, color=GRIS)
    doc.add_page_break()

    # ------------------ 1. PROBLEMA ------------------
    doc.add_heading("1. Contexto y problema abordado", level=1)
    doc.add_heading("1.1 Problema seleccionado", level=2)
    p("Se selecciono el problema de optimizacion de rutas en sistemas de mapas y navegacion "
      "inteligente. La mayoria de los sistemas de ruteo calculan la ruta mas corta o mas rapida "
      "a partir de un plan estatico de la red vial, pero no consideran la evolucion inmediata de "
      "la congestion, especialmente durante las mareas de trafico (horas pico).")
    p("Como consecuencia, al conductor se le ofrecen trayectorias que en minutos reales son "
      "suboptimas: una calle central con apariencia de atajo puede exigir el triple de tiempo "
      "cuando la congestion la satura. El proyecto se enfoco en la pregunta: como debe "
      "estructurarse la arquitectura de un navegador para que la estrategia de camino sea "
      "seleccionable, el sistema reaccione a los cambios del entorno y el recorrido se presente "
      "al usuario de forma desacoplada y extensible?")
    doc.add_heading("1.2 Relevancia e impacto", level=2)
    p("La navegacion eficiente impacta tres dimensiones. En la experiencia de usuario, una ruta "
      "optima reduce el estres y el tiempo de viaje. En el rendimiento del sistema, algoritmos "
      "dirigidos por heuristica (A*) reducen el numero de nodos explorados y, por lo tanto, la "
      "latencia del servicio. Y en la eficiencia operativa, flotas de entrega y transportadores "
      "ahorran combustible, horas hombre y costo por recorrido cuando la replanificacion se "
      "adapta a la congestion en tiempo real.")
    doc.add_heading("1.3 Objetivos", level=2)
    bullets([
        ("O1.", "Modelar una arquitectura por capas que separe presentacion, aplicacion, logica de ruteo e infraestructura."),
        ("O2.", "Aplicar los patrones Strategy, Observer, Command, Iterator y Composite para lograr extensibilidad y baja cohesion."),
        ("O3.", "Especificar el sistema con diagramas UML de componentes, clases, secuencia y actividad."),
        ("O4.", "Implementar un prototipo funcional y validarlo con metricas objetivas (tiempo, nodos expandidos, ms de ejecucion)."),
    ])
    doc.add_page_break()

    # ------------------ 2. ANALISIS ------------------
    doc.add_heading("2. Analisis y marco de referencia", level=1)
    doc.add_heading("2.1 Estrategias de navegacion en la literatura", level=2)
    p("Los algoritmos clasicos de camino minimo son la base del ruteo. Dijkstra garantiza el "
      "optimo sobre pesos no negativos pero explora de forma radial; A* incorpora una heuristica "
      "admisible que orienta la busqueda y reduce nodos expandidos. BFS ignora los pesos y solo "
      "minimiza saltos, util como linea base para medir la optimizacion. En la bibliografia de "
      "la unidad (Blas et al., 2019) se enfatiza el modelado y verificacion de patrones "
      "arquitectonicos antes de su despliegue; el presente prototipo aplica esa metodologia: los "
      "patrones se modelan primero en UML y luego se validan por ejecucion.")
    doc.add_heading("2.2 Enfoques en sistemas reales", level=2)
    bullets([
        ("Google Maps / Waze:", "combinan grafos viales con datos de trafico en vivo y heuristica A* sobre grafos jerarquicos para baja latencia."),
        ("OSRM / OpenStreetMap:", "usa tecnicas de contraccion de grafos (CH) y pesos por velocidad para servicio masivo de rutas."),
        ("Flotas de mensajeria:", "replanifican sobre pedidos agrupados por zona, equivalente al patron Composite de destinos."),
    ])
    doc.add_heading("2.3 Criterios de diseno", level=2)
    add_table(
        ["Criterio", "Definicion"],
        [
            ["Eficiencia", "Minimizar tiempo real de viaje y nodos explorados por el algoritmo."],
            ["Escalabilidad", "Anadir nuevas estrategias de ruteo sin modificar el nucleo (interfaz RouteStrategy)."],
            ["Adaptabilidad", "Reaccionar a eventos de trafico (mareas) con replanificacion automatica."],
            ["Extensibilidad", "Incluir nuevos tipos de destino (grupos) y nuevos comandos sin alterar el grafo."],
            ["Mantenibilidad", "Capas y patrones bien delimitados permiten evolucion aislada de cada pieza."],
        ],
        widths=[4.0, 12.4],
    )
    doc.add_page_break()

    # ------------------ 3. ARQUITECTURA ------------------
    doc.add_heading("3. Arquitectura propuesta", level=1)
    doc.add_heading("3.1 Estilo arquitectonico", level=2)
    p("La solucion adopta un estilo por capas con una fachada central (Navigator). La capa de "
      "presentacion (CLI) invoca la fachada; la capa de aplicacion orquesta contextos de patrones; "
      "la capa de logica contiene el grafo, los algoritmos y los modelos; la capa de "
      "infraestructura mantiene el sujeto de trafico y el registro de metricas. El flujo de datos "
      "sigue un sentido unico hacia abajo, y las dependencias apuntan a interfaces (RouteStrategy, "
      "Observer, Command).")
    doc.add_heading("3.2 Diagrama de componentes", level=2)
    doc.add_picture(str(UML / "componentes.png"), width=Cm(16.5))
    caption("Diagrama de componentes: dependencias y conectores entre las capas y los patrones.")
    doc.add_heading("3.3 Diagrama de clases", level=2)
    doc.add_picture(str(UML / "clases.png"), width=Cm(16.5))
    caption("Diagrama de clases: colaboracion de los cinco patrones sobre el modelo de dominio.")
    doc.add_heading("3.4 Diagrama de secuencia", level=2)
    doc.add_picture(str(UML / "secuencia.png"), width=Cm(16.5))
    caption("Diagrama de secuencia: solicitud de ruta, notificacion de trafico y replanificacion.")
    doc.add_heading("3.5 Diagrama de actividad", level=2)
    doc.add_picture(str(UML / "actividad.png"), width=Cm(13.5))
    caption("Diagrama de actividad: flujo completo desde la solicitud hasta la navegacion paso a paso.")
    doc.add_page_break()

    # ------------------ 4. PATRONES ------------------
    doc.add_heading("4. Patrones de diseno aplicados", level=1)
    add_table(
        ["Patron", "Necesidad", "Solucion aplicada en MAREA ROUTE"],
        [
            ["Strategy", "Conmutar el algoritmo de ruteo sin cambiar el cliente.", "RoutePlanner (contexto) delega en RouteStrategy; se implementaron Dijkstra-distancia, Dijkstra-tiempo plano, Dijkstra-tiempo en vivo, A* y BFS."],
            ["Observer", "Reaccionar a los cambios del trafico en tiempo real.", "TrafficControlCenter (sujeto) notifica a Navigator y TrafficLogger cuando cambia la congestion de un tramo; Navigator activa la replanificacion."],
            ["Command", "Encapsular acciones del usuario con soporte de deshacer.", "ChangeDestinationCommand y RerouteCommand se apilan en CommandHistory con execute() y undo()."],
            ["Iterator", "Recorrer la ruta paso a paso sin exponer la coleccion.", "RouteIterator entrega objetos RouteStep con la instruccion del tramo y sus metricas parciales."],
            ["Composite", "Tratar un destino unico y un grupo de destinos de forma uniforme.", "PlaceGroup agrupa Places y/o grupos hijos; un grupo de entregas se navega como objetivo unico."],
        ],
        widths=[2.6, 4.6, 9.2],
    )
    doc.add_heading("Justificacion de pertinencia", level=2)
    bullets([
        ("Strategy", "permite comparar algoritmos en el mismo prototipo y cambiar de politica de navegacion en tiempo de ejecucion (eficiencia y extensibilidad)."),
        ("Observer", "sustenta la optimizacion reactiva: el sistema detecta la marea y propone la mejor ruta nueva sin que el usuario pida recalculos."),
        ("Command", "da robustez operativa: un conductor puede deshacer una accion erronea (cambio de destino) y volver a la ruta previa."),
        ("Iterator", "separa la navegacion del cliente: la capa de presentacion consume pasos desacoplados de la estructura interna de la ruta."),
        ("Composite", "habilita flotas y entregas por zonas: un corredor comercial o una zona de despacho se tratan como un solo destino agregado."),
    ])
    doc.add_heading("Correspondencia con el diagrama de clases", level=2)
    p("El diagrama de clases (seccion 3.3) anota cada relacion con su patron: RoutePlanner "
      "compone RouteStrategy (Strategy); TrafficControlCenter mantiene observadores (Observer); "
      "CommandHistory apila Command (Command); Route crea RouteIterator que produce RouteStep "
      "(Iterator); PlaceGroup contiene Place o PlaceGroup (Composite).")
    doc.add_page_break()

    # ------------------ 5. PROTOTIPO ------------------
    doc.add_heading("5. Implementacion del prototipo", level=1)
    doc.add_heading("5.1 Stack y estructura", level=2)
    p("Prototipo en Python 3 (libreria estandar), sin dependencias externas para el nucleo. "
      "El repositorio organiza el paquete navigation/ por responsabilidades (domain, traffic, "
      "routing, commands, iterator, facade, city_map) y separa benchmarks, pruebas y "
      "documentacion UML.")
    add_table(
        ["Archivo", "Responsabilidad"],
        [
            ["navigation/domain.py", "Grafo, Place, PlaceGroup (Composite), RoadSegment y Route."],
            ["navigation/routing.py", "RoutePlanner y las cinco estrategias (Strategy)."],
            ["navigation/traffic.py", "TrafficControlCenter y observadores (TrafficLogger)."],
            ["navigation/commands.py", "Command, ChangeDestinationCommand, RerouteCommand y CommandHistory."],
            ["navigation/iterator.py", "RouteIterator y Modelo RouteStep."],
            ["navigation/facade.py", "Navigator: fachada que integra los patrones y observa el trafico."],
            ["navigation/city_map.py", "Mapa urbano de 16 lugares y generador de mallas aleatorias."],
            ["benchmarks/run_benchmarks.py", "Metricas de 30 pares OD x 5 estrategias x 2 escenarios."],
        ],
        widths=[6.2, 10.2],
    )
    doc.add_heading("5.2 Extraccion de la salida de la demo", level=2)
    demo = (RESULTS / "demo_salida.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    keep = []
    cap = False
    for ln in demo:
        if "[4]" in ln:
            cap = True
        if cap:
            keep.append(ln)
        if len(keep) > 15:
            break
    for ln in keep:
        par = doc.add_paragraph()
        run = par.add_run(ln)
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.0
    p("", size=6, space_after=2)
    p("La salida muestra el valor central del prototipo: la estrategia en vivo elige la ruta "
      "periferica (anillo) y ahorra minutos frente a la ruta de minima distancia, que queda "
      "atrapada en el centro congestionado.")
    doc.add_page_break()

    # ------------------ 6. PRUEBAS ------------------
    doc.add_heading("6. Pruebas y resultados", level=1)
    doc.add_heading("6.1 Pruebas unitarias", level=2)
    p("Se disenaron 11 pruebas unitarias (unittest, Python). Cubren: optimo conocido de "
      "Dijkstra, equivalencia A* = Dijkstra en vivo, ventaja de la ruta en vivo frente a la de "
      "minima distancia bajo marea, notificacion de observadores, activacion de la bandera de "
      "replanificacion, comportamiento de undo en Command, orden del RouteIterator y recorrido "
      "del Composite. Todas pasan en ejecucion.")
    doc.add_heading("6.2 Benchmark", level=2)
    p(f"Se construyo una malla urbana de {BENCH['hallazgos']['nodos_grafo']} nodos con avenidas "
      f"rapidas cada tres lineas y calles locales. Se evaluaron {BENCH['hallazgos']['pares_evaluados']} "
      f"pares origen-destino por estrategia en dos escenarios (sin marea y con marea de trafico).")
    doc.add_heading("Escenario sin marea", level=3)
    add_table(
        ["Estrategia", "km avg", "min avg", "nodos avg", "ms avg", "ms max"],
        [
            [
                r["strategy"],
                f"{r['avg_distance_km']:.2f}",
                f"{r['avg_time_min']:.2f}",
                f"{r['avg_nodes_expanded']:.1f}",
                f"{r['avg_exec_ms']:.3f}",
                f"{r['max_exec_ms']:.3f}",
            ]
            for r in BENCH["sin_marea"]
        ],
        widths=[6.4, 1.9, 1.9, 2.0, 1.8, 2.0],
    )
    doc.add_paragraph()
    doc.add_heading("Escenario con marea", level=3)
    add_table(
        ["Estrategia", "km avg", "min avg", "nodos avg", "ms avg", "ms max"],
        [
            [
                r["strategy"],
                f"{r['avg_distance_km']:.2f}",
                f"{r['avg_time_min']:.2f}",
                f"{r['avg_nodes_expanded']:.1f}",
                f"{r['avg_exec_ms']:.3f}",
                f"{r['max_exec_ms']:.3f}",
            ]
            for r in BENCH["con_marea"]
        ],
        widths=[6.4, 1.9, 1.9, 2.0, 1.8, 2.0],
    )
    doc.add_heading("6.3 Interpretacion", level=2)
    h = BENCH["hallazgos"]
    bullets([
        (f"Ahorro de la ruta en vivo bajo marea: {h['ahorro_marea_min']} min promedio.", "frente a la ruta de minima distancia, con recorridos ligeramente mas largos."),
        (f"Ahorro sin marea: {h['ahorro_sin_marea_min']} min promedio.", "confirmar que la distancia corta no es sinonimo de tiempo corto."),
        (f"Reduccion de nodos expandidos con A*: {h['reduccion_nodos_astar_pct']}%.", "A* obtiene exactamente el mismo camino optimo que Dijkstra, con menor exploracion."),
        (f"Mejora en vivo vs plan estatico bajo marea: {h['mejora_vivo_vs_plano_pct']}%.", "la politica reactiva supera al plan que ignora la congestion."),
    ])
    doc.add_page_break()

    # ------------------ 7. RUBRICA ------------------
    doc.add_heading("7. Validacion frente a la rubrica", level=1)
    add_table(
        ["Criterio", "Como se evidencia"],
        [
            ["Claridad y precision del problema", "Seccion 1: problema delimitado (rutas suboptimas por mareas de trafico) con impacto en UX, rendimiento y operacion."],
            ["Calidad del diseno UML", "Seccion 3: diagramas de componentes, clases, secuencia y actividad con PlantUML y referenciados con sus patrones."],
            ["Aplicacion de patrones de diseno", "Seccion 4: cinco patrones implementados, justificados y anotados sobre el diagrama de clases."],
            ["Calidad del prototipo", "Secciones 5 y 6: prototipo funcional con demo, 11 pruebas unitarias y benchmark reproducible."],
            ["Presentacion y documentacion", "Este informe (PDF), presentacion adjunta y video de demostracion (enlace privado)."],
        ],
        widths=[5.4, 11.0],
    )
    doc.add_page_break()

    # ------------------ 8. CONCLUSIONES ------------------
    doc.add_heading("8. Conclusiones y trabajo futuro", level=1)
    bullets([
        ("Conclusion 1.", "La separacion de estrategias via Strategy convierte el ruteo en una politica intercambiable: el mismo nucleo produce rutas por distancia, tiempo plano, tiempo en vivo o heuristica, lo que facilita comparar costos y cuantificar la optimizacion."),
        ("Conclusion 2.", "El Observer fue decisivo para la optimizacion reactiva: subir la congestion de un tramo detona la replanificacion sin intervencion del usuario, reduciendo el tiempo real del trayecto."),
        ("Conclusion 3.", "A* demostro ser tan optimo como Dijkstra en tiempo bajo marea y reducir cerca de un tercio de los nodos explorados, un beneficio directo de latencia y escalabilidad."),
        ("Conclusion 4.", "Command, Iterator y Composite mejoraron la usabilidad y extensibilidad: undo de acciones, navegacion paso a paso desacoplada y navegacion por grupos de destinos."),
        ("Trabajo futuro.", "Incorporar grafos jerarquicos (contraccion), actualizar congestion con datos historicos y en vivo, integrar persistencia de rutas y exponer el nucleo como servicio REST para evaluar latencia bajo carga."),
    ])
    doc.add_page_break()

    # ------------------ REFERENCIAS ------------------
    doc.add_heading("Referencias", level=1)
    for i, ref in enumerate([
        "Gamma, E., Helm, R., Johnson, R., y Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley.",
        "Teniente Lopez, E., Costal Costa, D., y Sancho Samso, M. R. (2015). Especificacion de sistemas software en UML. Universitat Politecnica de Catalunya. https://elibro.net/es/ereader/tecnologicadeloriente/61407",
        "Blas, M. J., Leone, H. P., y Gonnet, S. M. (2019). Modelado y verificacion de patrones de diseno de arquitectura de software para entornos de computacion en la nube. CONICET. https://ri.conicet.gov.ar/handle/11336/125130",
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L., y Stein, C. (2009). Introduction to Algorithms (3a ed.). MIT Press.",
    ], start=1):
        p(f"[{i}] {ref}", size=10, space_after=6)
    doc.add_page_break()

    # ------------------ ANEXO ------------------
    doc.add_heading("Anexo A: comandos y reproduccion de resultados", level=1)
    for cmd in [
        "python -m navigation.demo",
        "python -m unittest discover -s tests",
        "python -m benchmarks.run_benchmarks",
        "python docs/informe/build_report.py",
        "python docs/presentacion/build_slides.py",
    ]:
        par = doc.add_paragraph()
        run = par.add_run(cmd)
        run.font.name = "Consolas"
        run.font.size = Pt(10)
    p("", size=6)
    p("El archivo docs/results/benchmark.json contiene las metricas detalladas por par "
      "origen-destino y por estrategia; los diagramas UML (PlantUML) residen en docs/uml/ "
      "tanto en formato fuente (.puml) como en PNG listos para el informe.")

    doc.save(str(OUT))
    print(f"Informe Word generado: {OUT.resolve()}")


if __name__ == "__main__":
    build()