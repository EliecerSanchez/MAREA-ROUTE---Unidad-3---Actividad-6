# MAREA ROUTE - Unidad 3 / Actividad 6

Estrategias de navegacion en la arquitectura de software: optimizacion de rutas
urbanas frente a las **mareas de trafico** (horas pico) mediante una arquitectura
por capas con patrones de diseno **Strategy, Observer, Command, Iterator y Composite**.

## Problema abordado

Los sistemas de navegacion exponen al usuario a rutas suboptimas cuando la congestion
cambia (hora pico, eventos, accidentes). La ruta *mas corta en distancia* no es la
*mas rapida en tiempo*. El proyecto plantea una arquitectura que:

1. Selecciona en tiempo de ejecucion la estrategia de ruteo mas adecuada (Strategy).
2. Reacciona a los cambios del trafico y recomienda replanificar (Observer).
3. Permite deshacer acciones de navegacion (Command).
4. Recorre la ruta paso a paso sin acoplar al consumidor (Iterator).
5. Agrupa destinos (zonas de entrega) y los navega como un solo objetivo (Composite).

## Estructura del repositorio

```
.
|-- navigation/                 # Paquete principal (arquitectura)
|   |-- domain.py               # Grafo, Place, PlaceGroup (Composite), Route
|   |-- traffic.py              # TrafficControlCenter + Observer
|   |-- routing.py              # RoutePlanner + RouteStrategy (Strategy)
|   |-- commands.py             # Command + CommandHistory
|   |-- iterator.py             # RouteIterator
|   |-- facade.py               # Navigator (Facade + Observer)
|   |-- city_map.py             # Mapas de demostracion
|   `-- demo.py                 # Demo por consola
|-- benchmarks/
|   `-- run_benchmarks.py       # Metricas: 30 pares OD x 5 estrategias x 2 escenarios
|-- tests/
|   `-- test_system.py          # 11 pruebas unitarias
|-- docs/
|   |-- uml/                    # Diagramas PlantUML (.puml + .png)
|   `-- results/                # benchmark.json, demo_salida.txt
|-- README.md
```

## Requisitos

- Python 3.10+ (solo libreria estandar para el codigo).
- Para regenerar el PDF del informe: `pip install reportlab`.

## Ejecucion

```bash
python -m navigation.demo                 # Demo por consola
python -m unittest discover -s tests      # Pruebas unitarias
python -m benchmarks.run_benchmarks       # Benchmark (guarda docs/results/benchmark.json)
python docs/informe/build_report.py       # Genera el informe PDF
python docs/presentacion/build_slides.py  # Genera la presentacion PDF
```

Regeneracion de los diagramas UML (requiere Java y plantuml.jar, p.ej. de
https://github.com/plantuml/plantuml):

```bash
java -jar plantuml.jar -charset UTF-8 docs/uml/*.puml
```

## Resultados clave (benchmark)

- Con marea de trafico, la estrategia en vivo ahorra en promedio **mas de 1 minuto
  por viaje** frente a la ruta de minima distancia (con recorridos ligeramente mas
  largos en km).
- **A\* expande ~30% menos nodos** que Dijkstra para obtener el mismo camino optimo.
- La ruta en vivo mejora **~7%** el tiempo frente al plan estatico durante la marea.

Detalle completo en `docs/results/benchmark.json` y en el informe PDF.