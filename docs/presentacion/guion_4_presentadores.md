# Guion del video - 4 presentadores (max. 15 min)

**Proyecto:** MAREA ROUTE - Actividad 6, Arquitectura de Software (U3)
**Enlace del video (no listado):** [pegar enlace de YouTube aqui]
**Presentacion:** `docs/presentacion/Presentacion_Actividad6.pptx` (13 diapositivas)

## Reparto

| Rol | Presentador | Diapositivas | Tiempo estimado |
|-----|-------------|--------------|-----------------|
| P1 - Moderador | Integrante 1 | 1-3 | ~2.5 min |
| P2 - Arquitecto | Integrante 2 | 4-8 | ~4.0 min |
| P3 - Desarrollador | Integrante 3 | 9-10 | ~4.0 min |
| P4 - Evaluador | Integrante 4 | 11-13 | ~3.5 min |

> Total: ~14 min (margen de 1 min para cortes y errores).
> Hablar claro y pausado; cada guion incluye ideas y frases sugeridas en comillas (adaptar con su propio estilo).

---

## P1 - MODERADOR (diapositivas 1-3, ~2.5 min)

### Diapositiva 1 - Portada (0:00-0:40)
*Encuadre: camara principal, P1 en cuadro, presentacion en pantalla.*

- "Hola, somos el equipo de Arquitectura de Software. Presentamos MAREA ROUTE: estrategias de navegacion en la arquitectura de software."
- "Actividad 6 - Navegando mareas, con nuestro lider [nombre], el disenador UML [nombre], el programador [nombre] y el investigador [nombre]."
- "En este video mostramos el problema, la arquitectura, los patrones de diseno, el prototipo y los resultados."

### Diapositiva 2 - Problema (0:40-1:35)
- "El problema: los sistemas de mapas calculan la ruta mas corta o mas rapida sobre un plan estatico de la red vial."
- "En las horas pico, las 'mareas de trafico' saturan calles que parecen atajos: la ruta de menor distancia no es la mas rapida en minutos reales."
- "Nuestra pregunta de diseno: como arquitecturar un navegador para que la estrategia sea intercambiable, reaccione a la congestion y presente el recorrido de forma extensible?" *(cambiar turno)*

### Diapositiva 3 - Impacto (1:35-2:30)
- "La relevancia esta en tres dimensiones: experiencia de usuario, porque menos tiempo y menos estres; rendimiento, porque A* expande menos nodos y reduce latencia; y eficiencia operativa, porque las flotas ahorran combustible y horas-hombre al replanificar en vivo."
- "Ademas, el diseno escala: nuevas estrategias se agregan sin tocar el nucleo."
- "Ahora, [P2] presenta la arquitectura propuesta."

---

## P2 - ARQUITECTO (diapositivas 4-8, ~4.0 min)

### Diapositiva 4 - Arquitectura (2:30-3:30)
*Pantalla compartida con la tabla de capas.*

- "Proponemos una arquitectura por capas con una fachada central, el Navigator."
- "Capas: presentacion (CLI), aplicacion (Navigator y CommandHistory), logica de ruteo (RoutePlanner, Strategy y el grafo) e infraestructura (TrafficControlCenter y metricas)."
- "Regla clave: las dependencias apuntan a interfaces, y los patrones se modelan primero en UML antes de implementarlos."

### Diapositivas 5-8 - Modelado UML (3:30-6:30)
*Mostrar cada diagrama en pantalla explicando brevemente (unos 45 s cada uno).*

- **Componentes (5):** "Este diagrama muestra la estructura: las capas, las dependencias y los conectores entre modulos; se ve como el Navigator desacopla al cliente de los algoritmos."
- **Clases (6):** "El de clases anota la colaboracion de los cinco patrones: Strategy en RoutePlanner, Observer en TrafficControlCenter, Command en CommandHistory, Iterator en Route y Composite en PlaceGroup."
- **Secuencia (7):** "El de secuencia muestra el flujo: el usuario pide una ruta, mientras el trafico notifica un cambio de congestion y el Navigator replanifica."
- **Actividad (8):** "Y el de actividad resume el flujo completo: de la solicitud hasta la navegacion paso a paso."
- "Estos diagramas residen en docs/uml y se regeneran con PlantUML. Le paso con [P3], que implemento el prototipo."

---

## P3 - DESARROLLADOR (diapositivas 9-10, ~4.0 min)

### Diapositiva 9 - Patrones de diseno (6:30-8:30)
- "Cinco patrones aplicados (no solo dibujados, implementados y probados)."
- "Strategy: RoutePlanner conmuta entre Dijkstra por distancia, por tiempo plano, tiempo en vivo y A*, sin cambiar al cliente."
- "Observer: TrafficControlCenter es el sujeto; cuando sube la congestion, notifica al Navigator y a un registro, y se activa la replanificacion automatica."
- "Command: RerouteCommand y ChangeDestinationCommand se apilan y se pueden deshacer con undo."
- "Iterator: RouteIterator entrega la ruta paso a paso, sin exponer la estructura interna."
- "Composite: PlaceGroup trata un grupo de destinos como un unico destino, pensado para entregas y flotas."

### Diapositiva 10 - Prototipo (8:30-10:30)
***DEMO EN VIVO** (recomendado: grabar pantalla de la consola).*
*Comando: `python -m navigation.demo`*

- "Ejecutamos la demo real. Vemos el mapa con 16 lugares y aplicamos una marea de trafico en el centro."
- "Primera estrategia: minima distancia. Salida de la universidad al estadio; la ruta es la mas corta en kilometros, pero entra al centro congestionado." *(señalar en consola la linea de la ruta mas corta)*
- "Ahora cambiamos a la estrategia en vivo: la ruta toma el anillo periferico; es mas larga en kilometros pero ahorra alrededor de doce minutos." *(señalar la diferencia de tiempo)*
- "Mostramos tambien el deshacer de un comando, la navegacion paso a paso y las notificaciones del trafico."
- "Ademas: 11 pruebas unitarias que cubren el optimo de Dijkstra, la equivalencia A* igual a Dijkstra en vivo, y el comportamiento de Observer, Command, Iterator y Composite. Todas pasan."

---

## P4 - EVALUADOR (diapositivas 11-13, ~3.5 min)

### Diapositiva 11 - Resultados del benchmark (10:30-12:20)
- "Evaluamos metricas objetivas con un benchmark: 30 pares origen-destino, 5 estrategias y 2 escenarios, sobre una malla urbana de 144 nodos."
- "Bajo marea, la ruta en vivo ahorra [X] minutos promedio frente a la minima distancia."
- "A* reduce los nodos expandidos un [Y]% mientras obtiene exactamente el mismo camino optimo que Dijkstra."
- "Y la ruta en vivo supera al plan estatico un [Z]% cuando hay marea: la arquitectura reactiva vale la pena." *(los valores X, Y, Z se reemplazan por los hallazgos del benchmark.json)*

### Diapositiva 12 - Conclusiones (12:20-13:40)
- "Conclusion 1: la arquitectura por capas con fachada aislo algoritmos, trafico y presentacion."
- "Conclusion 2: Strategy hizo medible la optimizacion y Observer permitio replanificar sin el usuario."
- "Conclusion 3: Command, Iterator y Composite sumaron usabilidad y extensiones sin tocar el nucleo."
- "Trabajo futuro: grafos jerarquicos con contraccion, fusion de datos historicos y en vivo, y exponer el nucleo como API REST."

### Diapositiva 13 - Cierre (13:40-14:??)
- "Reproduccion: tres comandos - demo, pruebas unitarias y benchmark. Evidencias en docs/uml, docs/results/benchmark.json y el informe PDF."
- "El enlace privado del video y el informe estan en el LMS."
- "Gracias por su atencion; respondemos preguntas en los comentarios."

---

## Notas de grabacion

1. **Escenario:** grabar en 1080p, iluminacion frontal y audio con microfono (o audifonos). Evitar ruido de fondo.
2. **Encuadre:** P1 y P2 frente a camara; para UML y la demo usar captura de pantalla compartida a pantalla completa.
3. **Traspasos:** respetar los cambios de presentador al final de cada bloque; ensayar una pasada completa.
4. **Tiempos:** cronometrar; si se pasa de 15 min, recortar las explicaciones de los diagramas de secuencia y actividad.
5. **Subir a YouTube** con visibilidad "No listado"; pegar el enlace en el informe (seccion de entregables) y en el LMS.
6. **Voz en off opcional:** si algun integrante no aparece, puede narrar desde fuera de cuadro sobre la captura.