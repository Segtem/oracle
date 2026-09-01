# 0.2.0 — el primer release público

Primer release etiquetado de Oracle, y el primero con el repositorio abierto. **81 commits** desde
que se fijó `0.1.0`.

`0.1.0` no se etiqueta: ese número ya viaja adentro de los subtrees de dos consumidores, así que
volver a usarlo haría que el mismo nombre signifique dos cosas distintas —justo el problema que
las tres versiones separadas existen para evitar—.

```
VERSION_DISTRIBUCION   0.1.0 → 0.2.0     el paquete que se instala
VERSION_ALGEBRA        0.4   → 0.5       lo que una medida SIGNIFICA
VERSION_SINTAXIS       0.1               cómo se ESCRIBE (sin cambios)
```

## Cinco niveles de representación

El lenguaje dejó de hablar sólo de evidencia y medidas. Ahora nombra los cinco niveles
(`DECISION-005`):

| | |
|---|---|
| **L−2** | identidad y frescura del referente: si lo que se midió sigue siendo lo mismo |
| **L−1** | declaración del sensor: unidades y alcance de lo que produce |
| **L0** | las filas de evidencia |
| **L1** | las medidas |
| **L2** | medidas sobre medidas |

L−1 y L−2 se cerraron con `nucleo/unidad.py`, `nucleo/referente.py` y `nucleo/fixtures.py`, los
tres con mutación sin sobrevivientes.

## La superficie infija

Una medida se escribe y se lee en un formato legible, y el catálogo lo carga **tal cual**: no hay
paso de traducción. El JSON sigue siendo válido y los dos conviven.

```
ninguno meta.ningun_umbral_de_igualdad:
    de medida m
    donde m.comparador == "=="
    umbral <= 0 segun contrato porque "…"
    alcance "…"
```

## El umbral declara de dónde sale su número

`segun` es obligatorio y cerrado: `medicion`, `contrato`, `convencion` o `tanteo`. Un umbral sin
procedencia era un número puesto a ojo con cara de dato (`DECISION-006`).

## Editor: un servidor LSP para Emacs y VS Code

El mismo servidor, sin dependencias de npm ni de pip.

- **Diagnósticos**: error de sintaxis, medida mal declarada, y `SIN FIJAR` sobre las medidas que
  ninguna evidencia pone a prueba.
- **Completado** con la **unidad** del campo — `flotante · cm`, que es lo que ningún otro editor
  muestra.
- **CodeLens**: arriba de cada medida, qué la pone a prueba y con qué umbral.

`oracle-lsp` es ahora un entry point del paquete, así que el editor lo encuentra sin que exista
ningún checkout. Los clientes lo buscan en `ORACLE_LSP` → `oracle-lsp` en el `PATH` → el checkout.

## `unir` con índice: el techo del millón deja de ser el techo

`unir` materializaba el producto cartesiano y recién después filtraba, así que dos relaciones de
2.000 filas pedían 4.000.000 de pares y chocaban contra el límite. Cuando el `donde` que sigue
compara por igualdad dos campos, esa igualdad es una clave: se indexa un lado y se recorre el
otro. **20.000 filas en 0,005 s** sobre los datos que el camino ingenuo rechaza.

El plan ingenuo no se borró: `forzar_plan_unir()` elige cuál corre, y los tests exigen que los dos
den el mismo resultado. Una optimización que reemplaza a lo que optimiza se queda sin nada contra
qué compararse.

## La CLI

`oracle init`, `oracle nueva`, `oracle caso`, `oracle test`, `oracle revisar`, `oracle relaciones`,
`oracle escalares`, `oracle expandir`, `oracle medida probar --con` y `--vigilar`. La CLI entró al
arnés de mutación: **317/317 mutantes muertos**.

## Aislamiento de escalares

`escalares.py` de un proyecto se ejecuta en un **proceso aislado**: una función hostil no puede
leer fuera del proyecto, escribir fuera, abrir red ni lanzar procesos. Sigue exigiendo
`--confiar-escalares`.

## Correcciones que vale la pena nombrar

- **Un subrayado de ancho cero no se ve.** El servidor mandaba el rango del error apuntando al
  final de la línea; el editor lo recortaba y quedaba vacío. Se arregló en el servidor, que es
  donde lo arregla también para Emacs.
- **«Está ejercitada» estaba escrito tres veces** —en el LSP, en `--listar` y como medida—, y las
  tres copias en Python compartían el mismo punto ciego: no miraban los fixtures diferenciales.
  Ahora las herramientas se lo preguntan a `meta.toda_medida_esta_ejercitada`, que es donde el
  reclamo está escrito.

## Decisiones registradas en este ciclo

- `DECISION-004` — dos medidas quedan sostenidas por evidencia generada
- `DECISION-005` — cinco niveles de representación
- `DECISION-006` — de dónde sale el número
- `DECISION-007` — bibliotecas de políticas
- `DECISION-008` — el repositorio se abre

## Límites conocidos

**El servidor LSP necesita un proyecto.** `oracle-lsp` sale con código 1 si no resuelve uno
—`oracle.json` en el directorio de trabajo, o `--proyecto` explícito—. Los editores lo arrancan
sin argumentos y le pasan la carpeta abierta: con una carpeta de proyecto abierta funciona, con un
`.oracle` suelto el servidor se apaga y no hay diagnósticos, dejando sólo una línea en el registro.
Se descubrió verificando el wheel antes de publicar. Lo correcto es que el servidor siga dando
diagnósticos de sintaxis —que no necesitan proyecto— y degrade sólo lo que sí lo necesita; eso
cambia el contrato del servidor y va en la próxima versión, no en un arreglo apurado.

**`tools/medida.py` tiene 114 mutantes vivos.** Es la superficie de la CLI y la deuda es anterior
a esta versión. Ésta es además la primera ronda COMPLETA de ese módulo: las anteriores se cortaban
cerca de los 120 sitios sin decirlo, así que la cifra vieja de «115 sitios · 67 vivos» subestimaba
el tamaño real, que son 264 sitios.

## Estado

Sigue siendo **`EXPERIMENTAL`**. Abrir el repositorio no es declarar que está terminado: la
reflexión sobre el catálogo sigue fijada en Python, que es justo lo que un metalenguaje no
debería necesitar. El camino está en `PLAN-LENGUAJE.md`.

## Instalación

```bash
pip install git+https://github.com/Segtem/oracle.git
# o, sin red, desde el archivo adjunto a este release:
pip install oracle_metalenguaje-0.2.0-py3-none-any.whl

oracle init mi-proyecto
```

Python ≥ 3.11. **Sin dependencias** — se instala offline, desde el archivo.
