# Documentar un camino corto desde un producto nuevo hasta su primera medida observable

- ESTADO: CERRADA
- PRIORIDAD: 65
- ETIQUETAS: oracle, documentacion

## Problema y evidencia

Derivada de 20260919-134424-naval-pm; ver [postmortem](../../estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md).
La tarea naval prometió medidas de reglas del juego, pero terminó con catálogo propio vacío y un caso que declara sintaxis válida. El README abre con init → nueva → test y “ya tiene quién lo juzgue”; la guía GUIA22 explica correctamente sensores y límites, pero su recorrido completo tiene 1.171 líneas y cuatro medidas. No hay evidencia para atribuirle el 60 % de atención ni afirmar que el tracker fuera obligatorio.

## Resultado buscado

Un recorrido breve, ejecutable desde cero, que termine juzgando hechos del producto con una sola medida pertinente. El lector debe distinguir preparar Oracle, fijar una medida con casos y medir una corrida real.

## Alcance y aceptación

- Agregar o enlazar desde la instalación del README una ruta mínima: elegir una regla del producto → extraer hechos → una medida y casos de ambas polaridades → test → juzgar una corrida real.
- Usar un ejemplo reproducible dentro de Oracle; no modificar /home/workstation/Dev/lab/. Registrar origen verificable de los hechos, comando real y su alcance; no presentar node -c como comprobación de HTML/CSS ni de jugabilidad.
- Mostrar un defecto detectable, su corrección y lo que no mira la medida. Diferenciar evidencia guardada de evidencia regenerada tras cambiar producto.
- Aclarar que tracker y tutorial completo son opciones separadas; indicar cuándo basta un assert y cuándo aporta Oracle. No recortar exigencias de las medidas para lograr una pantalla verde.
- Recorrer los comandos en una copia/entorno limpio con versión fijada y guardar sus resultados. No hace falta diseñar un nuevo comando CLI sin demostrar antes que documentación y ejemplo no alcanzan.

## Avance

- 2026-09-21:
  - Se eligió como regla mínima de dominio la colocación dentro del tablero (`0 <= fila < 10` y `0 <= columna < 10`).
  - Se construyó el proyecto de ejemplo reproducible dentro de Oracle en [`ejemplo/primer-valor/`](../../ejemplo/primer-valor):
    - [`colocador.py`](../../ejemplo/primer-valor/colocador.py): lógica de colocación en Python puro sin dependencias; simula defecto (`--defecto`) y extrae hechos L0 estructurados en JSON (`celda_ocupada(barco, fila, columna)`).
    - [`oracle.json`](../../ejemplo/primer-valor/oracle.json): configuración con `catalogo_base: false` para evaluar únicamente las reglas de negocio locales.
    - [`catalogos/colocacion/colocacion.dentro_del_tablero.oracle`](../../ejemplo/primer-valor/catalogos/colocacion/colocacion.dentro_del_tablero.oracle): medida canónica con filtro negativo, umbral con defensa, `requiere` y `alcance` explícito sobre sus puntos ciegos.
    - [`corpus/colocacion/001-desborde-tablero.caso`](../../ejemplo/primer-valor/corpus/colocacion/001-desborde-tablero.caso): caso negativo (`falso_verde`, esperado ROJO) con desborde en fila 10; mata el mutante `aflojar_umbral`.
    - [`corpus/colocacion/002-colocacion-valida.caso`](../../ejemplo/primer-valor/corpus/colocacion/002-colocacion-valida.caso): caso positivo (`verde_correcto`, esperado VERDE) con celdas legales en rango 0..9; mata el mutante `quitar_filtro`.
    - [`ejemplo/primer-valor/README.md`](../../ejemplo/primer-valor/README.md): documentación del ejemplo con comandos y salidas esperadas.
  - Se redactó la guía del recorrido canónico en [`docs/13-primer-valor.md`](../../docs/13-primer-valor.md), cubriendo la ruta mínima:
    - Explicación conceptual paso a paso: regla de producto → sensor de hechos → medida y casos en dos polaridades → `oracle test` → `oracle juzgar` sobre corrida real.
    - Salidas esperadas exactas para defecto detectable (exit 1) y corrección (exit 0), con el `alcance` visible en el veredicto final.
    - Clarificación de evidencia guardada vs. evidencia regenerada, cuándo basta un `assert` y cuándo aporta Oracle, y el carácter optativo e independiente del tracker de tareas.
  - *Nota de verificación*: Los archivos y salidas esperadas fueron elaborados mediante lectura y edición estricta del código fuente y gramática de Oracle; no se afirmaron ni ejecutaron verificaciones en shell durante este turno.

### Nota (2026-09-21 20:47:36 UTC)

Recorrido ejecutado en copia limpia sin .git y venv nuevo, wheel local Oracle 0.27.0, Python 3.14.7; también se ejecutaron literalmente los bloques bash de docs/13-primer-valor.md. Corregido el directorio diferencial/ ausente mediante .gitkeep, sin relajar validaciones. Los dos casos iniciales dejaban seis mutantes vivos: se agregaron fila -1, columna -1, columna 10 y relación vacía. Resultado: seis casos, 20/20 mutantes muertos, oracle test exit 0; producto con defecto exporta cinco celdas y juzgar detecta fila 10 (exit 1); regenerado corregido da verde con alcance (exit 0). Reemplazadas salidas supuestas por capturas reales, commit ficticio de casos construidos por sin-commit y todos los enlaces file locales por rutas relativas. Enlazado recorrido desde instalación del README. Agregado tests/test_primer_valor.py: copia limpia, catálogo, exportación, rojo y regeneración verde. Suite completa en ejecución; sin commits por instrucción y .git de sólo lectura.

### Nota (2026-09-21 20:48:19 UTC)

La primera suite completa ejecutó 2365 tests y encontró sólo el enlace relativo nuevo del README principal: ese archivo se publica en PyPI y test_el_readme_no_tiene_enlaces_relativos exige URL absoluta a GitHub. Se corrigió únicamente ese enlace nuevo, conservando rutas relativas para los antiguos file locales de guía, ejemplo y tarea. Suite completa relanzada.

### Nota (2026-09-21 20:49:12 UTC)

Verificación final: python3 -m unittest discover -s tests -t . -q terminó con exit 0: Ran 2365 tests in 70.712s, OK (incluye test_primer_valor). git diff --check sin problemas y búsqueda global de enlaces file locales sin coincidencias. Recorrido completo aprobado: catálogo verde con 20/20 mutantes muertos, defecto rojo exit 1 y corrección verde exit 0. Sin cambios al motor ni commits. Trabajo de implementación y verificación terminado; queda revisión e integración desde un checkout con escritura en Git.

## Próximo paso

Revisar e integrar el diff verificado desde un checkout con escritura en Git; luego cerrar esta tarea según el protocolo. La ejecución de punta a punta y la suite completa ya están verdes (2365 tests); no quedan correcciones técnicas pendientes de este pedido. En este worktree no crear commits por instrucción del usuario y .git de sólo lectura.
