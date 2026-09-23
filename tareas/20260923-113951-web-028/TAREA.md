# La web no muestra nada de lo que Oracle ganó desde 0.26

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, web, documentacion


## El hueco

La página publicada (`docs/index.html`, GitHub Pages) se regenera en cifras en cada corte, pero su
contenido se quedó atrás. Nada de lo que entró desde 0.26 está explicado ahí:

- **el álgebra dice «ninguna»** (`sin`, 0.26);
- **una sombra perdona hasta su cota**, y `juzgar` nombra lo que no se aplicó (0.27);
- **el MCP**, con sus cinco herramientas de sólo lectura y el porqué (0.27);
- **retomar es leer una tarea**: el tracker como relevo, la búsqueda por sufijo y `CIERRA CON` (0.28);
- **`oracle test` dice lo que no midió** (`SIN MEDICIÓN`, 0.28);
- **el camino corto a la primera medida real** (`docs/13-primer-valor.md`);
- **Jev**: un modelo como sensor de la prosa, con lo medido (10/10 controles, 15/15 con un juez
  ciego, centavos) y sus límites; y cómo lo usa alguien desde PyPI cuando cierre
  [`jev-pypi`](../20260923-113127-jev-pypi/TAREA.md).

## Qué hacer

1. Un apartado por tema, corto, con un ejemplo que se pueda copiar y su salida real. Nada de
   promesas: cada cifra sale de una corrida que se pueda repetir.
2. **Un apartado propio para Jev**, que explique la división que hace que valga: el sensor produce
   hechos, la medida juzga; Oracle no llama a ningún modelo; la calibración medida y la zona del
   medio que va a revisión humana.
3. Que la página no dependa de este repo desordenado: se escribe después de
   [`repo-limpio`](../20260923-113951-repo-limpio/TAREA.md) si esa tarea cambia rutas, para no enlazar lo que se va a mover.
4. Comprobar enlaces y cifras con lo que ya existe (`tools/cifras.py`, el test que compara la página
   con el manual).

## Próximo paso

Inventario: qué dice hoy la página, qué falta, y un índice propuesto para revisión de Brian.
