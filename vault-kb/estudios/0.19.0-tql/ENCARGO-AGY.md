# Encargo 0.19.0 — consultas de tareas en español

2026-09-15. El dueño eligió seguir con la tarea
[`20260915-023750-tql`](../../tareas/20260915-023750-tql/TAREA.md), con vocabulario **en español**.
Plan: [vault-kb/planes/PLAN-0.19.0-TQL.md](../../planes/PLAN-0.19.0-TQL.md). Revisa y verifica Claude.

Leer antes: el plan, `docs/12-tareas.md`, `tools/tareas.py` (`cmd_listar`, `cmd_desetiquetar`,
`cmd_init`, `resolver_id_o_prefijo`, `ID_COMPLETO_RE`), `tools/tareas_contexto.py`
(`cmd_referencias`), `tools/cli.py` (ayuda y verbos de `tarea`) y, como referencia de diseño,
[`src/query.c` de tatr](https://github.com/tsoding/tatr/blob/main/src/query.c).

## Propiedad

Agy: nuevo `tools/tareas_consulta.py`; `tools/tareas.py` y `tools/tareas_contexto.py` en lo que pide
este encargo; la ayuda de `tarea` en `tools/cli.py`; nuevo `tests/test_tareas_consulta.py`; la sección
nueva y la actualización de «Diferencias con tatr» en `docs/12-tareas.md`; y en `vault-kb/estudios/0.19.0-tql/`
sus `AVANCE-AGY.md` (primero, con el plan de archivos) e `INFORME-AGY.md` (al final).

Claude: `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/`, `ejemplo/`,
`tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `docs/manual.html`, tests de
revisión y todo test existente. Si un test existente contradice el encargo, anotarlo en el informe.

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.**
En el informe no afirmar verificaciones que no se corrieron.

## 1. El lenguaje — `tools/tareas_consulta.py`

Módulo puro: recibe texto y tareas ya parseadas (`tareas.Tarea`), no lee archivos ni conoce argv.

**Tokens.** `[` y `]` son tokens de un carácter; el resto se separa por blancos y corchetes. Cada
token conserva su posición (columna en caracteres, no bytes) para los diagnósticos.

**Gramática.**

```
consulta    ::= o
o           ::= y *('o' y)
y           ::= comparacion *('y' comparacion)
comparacion ::= primaria *(comparador primaria)
comparador  ::= 'menor' | 'hasta' | 'mayor' | 'desde' | 'igual' | 'distinto'
primaria    ::= ':' etiqueta | '[' consulta ']' | 'no' primaria
              | 'cualquiera' | 'etiquetada' | 'prioridad' | entero | id
```

- `:etiqueta`: verdadero si la tarea tiene esa etiqueta, **sin distinguir mayúsculas** (igual que
  `listar --etiqueta`). `:` solo es error.
- `cualquiera`: siempre verdadero. `etiquetada`: la tarea tiene al menos una etiqueta.
- `prioridad`: entero. `entero`: con signo opcional, dígitos ASCII.
- `id`: un token que cumple `tareas.ID_COMPLETO_RE`; verdadero si es **exactamente** el ID de la
  tarea (no prefijo).
- `menor` `<`, `hasta` `<=`, `mayor` `>`, `desde` `>=`, `igual` `==`, `distinto` `!=`, sólo entre
  enteros; asociativas a izquierda como en tatr.
- `no` se aplica a una primaria: `no :a y :b` es `(no :a) y :b`.
- Una consulta vacía (sólo blancos) equivale a `cualquiera`.

**Tipos al compilar.** Cada nodo tiene tipo booleano o entero, conocido sin mirar tareas. Un
comparador con un operando booleano, `y`/`o`/`no` con un entero, o una consulta cuyo resultado final
es entero (`prioridad` sola) son **errores de compilación**, no de evaluación. Es la diferencia
declarada con tatr.

**Errores.** Una excepción propia (p. ej. `ConsultaInvalida`) con mensaje y columna. Presentación
como en tatr: la consulta en una línea, en la siguiente un `^` bajo el token, y el mensaje en español.
Casos mínimos: primaria esperada al final, token inesperado (nombrarlo), `]` faltante, `[` sin
cerrar, `:` vacío, operador infijo inesperado después de una consulta completa (nombrarlo), tipo
incorrecto (decir cuál se esperaba y cuál llegó).

**API mínima.** `compilar(texto) -> Consulta` (lanza `ConsultaInvalida`), `Consulta.evaluar(tarea)
-> bool`, y una forma de explicarla: tokens y la forma compilada, determinista, para `--explicar`.
La representación interna (árbol o pila como tatr) es decisión del implementador: documentarla.

## 2. `listar`

```bash
oracle tarea listar [consulta...] [--cerradas|--todas] [--etiqueta E] [--texto T]
                    [--por-id] [--invertir] [--explicar] [--json]
```

- Las palabras posicionales se unen con un espacio y forman la consulta. Sin consulta, `cualquiera`.
- La consulta se aplica **además** de `--etiqueta`, `--texto` y el filtro de estado (conjunción).
- Consulta inválida: el diagnóstico por stderr y **código 2**, sin leer el tracker si puede evitarse.
- `--explicar`: imprime los tokens y la forma compilada y sale 0 **sin listar ni exigir tracker**.
- Orden: por defecto el actual (prioridad descendente, empate por ID). `--por-id`: por ID
  **descendente**, las más nuevas primero, como `tatr ls -id`. `--invertir`: invierte el orden final
  como `tatr ls -a`, combinable con `--por-id`.
- `--json` no cambia de forma.

## 3. `desetiquetar --consulta`

```bash
oracle tarea desetiquetar --etiqueta E --consulta ":scope y no :ui" [--cerradas|--todas]
```

- Selecciona entre las tareas del estado elegido (abiertas por defecto) las que cumplen la consulta.
- `--consulta` con IDs explícitos es error de uso (código 2), como `--todas` con IDs hoy.
- Consulta inválida: código 2 **sin escribir nada**.
- Todo lo demás —validación previa, escritura atómica, salida `ruta:línea`, idempotencia— igual que hoy.

## 4. `referencias` sin argumento

Si se omite el ID y el directorio actual está **dentro** de la carpeta de una tarea válida
(`tareas/<id>/` o un subdirectorio suyo, resolviendo la raíz como el resto de los verbos), usar esa
tarea. Fuera de una tarea, sin ID: código 2 con un mensaje que diga que falta el ID o hay que pararse
en la carpeta de una tarea. Con ID explícito, igual que hoy.

## 5. `init --sin-readme`

Crea `tareas/` sin `README.md`. El resto de `init` igual. Un tracker sin README sigue siendo válido
para `revisar`.

## Tests: `tests/test_tareas_consulta.py`

Del lenguaje, sin CLI: cada primaria; precedencia `y` sobre `o`; `no` sobre una primaria; corchetes;
comparadores en sus bordes (igual, uno menos, uno más) y negativos; encadenados a izquierda; ID exacto
contra prefijo; etiqueta con mayúsculas distintas; consulta vacía; cada error con su columna,
incluidos los de tipo, y columnas con caracteres no ASCII antes del error. Por CLI y trackers
temporales: `listar` con consulta, combinada con `--etiqueta`/`--texto`/estado; `--explicar` sin
tracker; `--por-id`, `--invertir` y los dos juntos; consulta inválida → 2 sin traceback;
`desetiquetar --consulta` en abiertas, `--todas`, con IDs → 2, inválida → 2 sin escrituras;
`referencias` desde la carpeta de la tarea, desde un subdirectorio, fuera → 2; `init --sin-readme` y
`revisar` OK sobre ese tracker; ayuda de los verbos sin escrituras.

## Documentación

En `docs/12-tareas.md`: la gramática, el vocabulario, ejemplos, errores y códigos, y las banderas
nuevas. En «Diferencias con tatr»: TQL deja de ser una diferencia de alcance y pasa a ser una de
vocabulario, con la tabla de equivalencias; los tipos se verifican al compilar; las etiquetas no
distinguen mayúsculas.
