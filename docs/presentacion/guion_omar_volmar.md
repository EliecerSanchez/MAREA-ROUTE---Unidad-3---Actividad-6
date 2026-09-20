# Guion del video - Presentacion de diapositivas

**Proyecto:** MAREA ROUTE - Actividad 6, Arquitectura de Software (U3)
**Enlace del video (no listado):** [pegar enlace de YouTube aqui]
**Duracion maxima:** 15 minutos
**Presentadores:** Omar Vallejo (lider/coordinacion) y Volmar Rincon (evaluador/pruebas)
**Presentacion:** `docs/presentacion/Presentacion_Actividad6.pptx` (13 diapositivas)

## Reparto por diapositivas

| Diapositiva | Presentador | Tiempo estimado |
|-------------|-------------|-----------------|
| 1 - Portada | Omar | ~0:40 |
| 2 - Problema | Omar | ~0:55 |
| 3 - Relevancia | Omar | ~0:55 |
| 4 - Arquitectura | Omar | ~1:00 |
| 5 - Componentes | Omar | ~0:45 |
| 6 - Clases | Omar | ~0:45 |
| 7 - Secuencia | Volmar | ~0:45 |
| 8 - Actividad | Volmar | ~0:45 |
| 9 - Patrones | Omar | ~2:00 |
| 10 - Prototipo/Demo | Volmar | ~3:00 |
| 11 - Resultados | Volmar | ~1:50 |
| 12 - Conclusiones | Volmar | ~1:20 |
| 13 - Cierre | Omar | ~0:30 |

> Total: ~13 min con 2 min de holgura para cortes. Hablar pausado y claro.

---

## Omar - Lider (portada, problema, relevancia, arquitectura, UML de estructura y patrones)

### Diapositiva 1 - Portada (Omar, 0:00-0:40)
- "Hola, somos el equipo de Arquitectura de Software de la seccion N5 GrB. Hoy presentamos MAREA ROUTE: estrategias de navegacion en la arquitectura de software, actividad 6, navegando mareas."
- "Mi nombre es Omar Vallejo, lider del equipo. Los demas integrantes son David Mape y Eliécer Sanchez en arquitectura y UML, Daniel Rodriguez en el desarrollo, y Volmar Rincon, mi companero de hoy, en pruebas de carga y robustez. El docente a cargo es Edward Alfonso Villamizar Vallejo."
- "En este video explicamos el problema, la arquitectura, los patrones de diseno, el prototipo y los resultados de evaluacion."

### Diapositiva 2 - Problema (Omar, 0:40-1:35)
- "El problema: los sistemas de mapas calculan la ruta mas corta o rapida sobre un plan estatico de la red vial."
- "En horas pico, las 'mareas de trafico' saturan calles centrales que parecen atajos: la ruta de menor distancia no es la mas rapida en minutos reales."
- "Nuestra pregunta de diseno: como arquitecturar un navegador para que la estrategia sea intercambiable, reaccione a la congestion y presente el recorrido de forma extensible?"

### Diapositiva 3 - Relevancia (Omar, 1:35-2:30)
- "La relevancia esta en tres dimensiones: experiencia de usuario (menos tiempo de viaje y menos estres), rendimiento (A* expande menos nodos y reduce latencia), y eficiencia operativa (flotas que ahorran combustible y horas-hombre al replanificar en vivo)."
- "Ademas, el diseno escala: nuevas estrategias se agregan sin tocar el nucleo."

### Diapositiva 4 - Arquitectura (Omar, 2:30-3:30)
- "Proponemos una arquitectura por capas con fachada central, el Navigator: presentacion (CLI), aplicacion (Navigator y CommandHistory), logica de ruteo (RoutePlanner y el grafo) e infraestructura (TrafficControlCenter y metricas)."
- "Regla clave: las dependencias apuntan a interfaces, y los patrones se modelan primero en UML."

### Diapositiva 5 - Componentes (Omar, 3:30-4:15)
- "El diagrama de componentes muestra la estructura: las capas, sus dependencias y los conectores entre modulos. Se aprecia como el Navigator desacopla al cliente de los algoritmos de ruteo."

### Diapositiva 6 - Clases (Omar, 4:15-5:00)
- "El diagrama de clases anota la colaboracion de los cinco patrones: Strategy en RoutePlanner, Observer en TrafficControlCenter, Command en CommandHistory, Iterator en Route y Composite en PlaceGroup."

### Diapositiva 9 - Patrones (Omar, 6:30-8:30)
- "Detailo los cinco patrones implementados y probados."
- "Strategy: RoutePlanner conmuta entre Dijkstra por distancia, por tiempo plano, en vivo y A*, sin cambiar al cliente."
- "Observer: TrafficControlCenter notifica al Navigator cuando sube la congestion y activa la replanificacion automatica."
- "Command: los comandos de reencaminar y cambiar destino se apilan y se pueden deshacer."
- "Iterator: entrega la ruta paso a paso sin exponer la estructura interna."
- "Composite: un grupo de destinos se navega como un unico destino, pensado para entregas. Ahora Volmar continua con el prototipo."

---
## Volmar - Evaluador (UML de comportamiento, prototipo, resultados y conclusiones)

### Diapositiva 7 - Secuencia (Volmar, 5:00-5:45)
- "El diagrama de secuencia muestra el flujo dinamico: el usuario solicita una ruta, y cuando el trafico notifica un cambio de congestion, el Navigator ejecuta la replanificacion. Es la respuesta reactiva del sistema frente a la marea."

### Diapositiva 8 - Actividad (Volmar, 5:45-6:30)
- "El diagrama de actividad resume ese flujo completo: de la solicitud inicial hasta la navegacion paso a paso, incluyendo las decisiones de cambiar de estrategia cuando mejora el tiempo estimado."

### Diapositiva 10 - Prototipo (Volmar, 8:30-11:30) [DEMO EN VIVO]
*Recomendado: captura de pantalla de la consola con el comando `python -m navigation.demo`.*
- "Ejecutamos la demo real sobre un mapa de 16 lugares, aplicando una marea de trafico en el centro."
- "Con la estrategia de minima distancia, saliendo de la universidad al estadio: la ruta es la mas corta en kilometros, pero entra al centro congestionado."
- "Cambiamos a la estrategia en vivo: toma el anillo periferico; es mas larga en kilometros, pero ahorra alrededor de 12 minutos. Esa diferencia es la optimizacion: no acortar distancias, sino tiempos."
- "Mostramos tambien el deshacer de un comando, la navegacion paso a paso y las notificaciones del centro de trafico."
- "Como evaluador respaldo el resultado con 11 pruebas unitarias, todas en verde, que cubren el optimo de Dijkstra, la equivalencia A* igual a Dijkstra en vivo, y Observer, Command, Iterator y Composite."

### Diapositiva 11 - Resultados (Volmar, 11:30-13:20)
- "Evaluamos metricas objetivas con un benchmark: 30 pares origen-destino, 5 estrategias y 2 escenarios, sobre una malla urbana de 144 nodos."
- "Bajo marea, la ruta en vivo ahorra [X] minutos promedio frente a la minima distancia."
- "A* reduce los nodos expandidos un [Y]% y obtiene exactamente el mismo camino optimo que Dijkstra: beneficio de latencia sin sacrificar optimalidad."
- "Y la ruta en vivo supera al plan estatico en un [Z]% durante la marea: la arquitectura reactiva se justifica numericamente."
> Rellenar [X], [Y], [Z] con los hallazgos de `docs/results/benchmark.json` antes de grabar.

### Diapositiva 12 - Conclusiones (Volmar, 13:20-14:40)
- "Conclusion 1: la arquitectura por capas con fachada aislo algoritmos, trafico y presentacion."
- "Conclusion 2: Strategy hizo medible la optimizacion, y Observer permitio replanificar sin el usuario."
- "Conclusion 3: Command, Iterator y Composite sumaron usabilidad y extensiones sin tocar el nucleo."
- "Conclusion 4 (evaluador): las pruebas y el benchmark validan la robustez del prototipo; el camino optimo por tiempo y la menor expansion de nodos estan verificados."
- "Trabajo futuro: grafos jerarquicos, datos historicos y en vivo, y exponer el nucleo como servicio REST."

### Diapositiva 13 - Cierre (Volmar, 14:40-15:00 / Omar cierra)
- "Reproduccion: python -m navigation.demo, python -m unittest discover -s tests y python -m benchmarks.run_benchmarks. Evidencias en docs/uml, docs/results y el informe PDF."
- **Omar:** "El enlace privado del video y el informe estan cargados en el LMS. Muchas gracias."

---

## Notas de grabacion

1. **Formato:** 1080p, iluminacion frontal, microfono (o audifonos) y sin ruido de fondo.
2. **Encuadre:** Omar presenta en camara hasta la diapositiva 6; Volmar toma cámara desde la 7. Los diagramas UML y la demo se muestran en pantalla compartida.
3. **Traslapes:** respetar el cambio de presentador en la diapositiva 9 ("le paso a Volmar") y en el cierre ("cierra Omar").
4. **Cronometrar:** cada bloque tiene su tiempo; si se excede, recortar la explicacion de los diagramas de secuencia y actividad.
5. **Metrics:** rellenar [X], [Y], [Z] de la diapositiva 11 antes de grabar.
6. **Publicacion:** subir a YouTube como "No listado" y pegar el enlace en el informe y el LMS.