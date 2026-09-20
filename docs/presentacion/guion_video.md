# Guion del video - Actividad 6 (max. 15 minutos)

> Version oficial en video: **guion_omar_volmar.md** (presentadores Omar -
> lider - y Volmar - evaluador). Este archivo queda como referencia de
> tiempos y mensajes clave.

Enlace del video (no listado): [pegar enlace de YouTube aqui]

| Minuto | Contenido | Elementos en pantalla |
|--------|-----------|-----------------------|
| 00:00-01:00 | Presentacion del equipo, curso, unidad y actividad. | Portada |
| 01:00-02:30 | Descripcion del problema: rutas suboptimas ante las mareas de trafico; la distancia corta no es el tiempo corto. | Problema e impacto |
| 02:30-04:00 | Arquitectura propuesta: capas + fachada Navigator; criterios de diseno (eficiencia, escalabilidad, adaptabilidad). | Diagrama de componentes |
| 04:00-06:30 | Modelos UML: clases (anotando los patrones), secuencia y actividad. | Diagrama de clases/seq/actividad |
| 06:30-09:30 | Patrones de diseno: Strategy, Observer, Command, Iterator, Composite (necesidad -> solucion y resultado). | Tabla de patrones + codigo |
| 09:30-12:30 | Demostracion del prototipo: ejecutar `python -m navigation.demo`; comparativa de estrategias; replanificacion y undo. | Consola + tabla de resultados |
| 12:30-14:30 | Resultados del benchmark: 30 pares OD, ahorro bajo marea, A* con menos nodos; prueba unitarias. | Graficos y metricas |
| 14:30-15:00 | Conclusiones, trabajo futuro y cierre. | Cierre |

Notas de grabacion:
- Grabar en resolucion 1080p, con la consola ampliada y letra legible.
- Subir a YouTube con visibilidad "No listado" y copiar el enlace en el informe y el LMS.
- Alternar diapositivas (Presentacion_Actividad6.pdf) con la demo en vivo.

Mensajes clave:
1. La arquitectura por capas + fachada permite cambiar de estrategia sin reescribir el nucleo.
2. El Observer habilita la replanificacion reactiva frente a las mareas.
3. A* es tan exacto como Dijkstra en tiempo y expande ~30% menos nodos.