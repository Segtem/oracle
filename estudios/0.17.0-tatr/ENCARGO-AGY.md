# Encargo 0.17.0 — lo que faltaba de tatr

2026-09-14. El dueño pidió completar lo que quedó pendiente frente a tatr después del corte 0.16.0
y trabajar con agy. Revisa y verifica Claude (Claude Code). Leer antes: `PLAN-0.16.0-TAREAS.md`,
`docs/12-tareas.md`, `tools/tareas.py`, `tools/tareas_contexto.py`, `tools/tareas_hechos.py`,
`tools/tareas_git.py` y el registro de verbos de `tarea` en `tools/cli.py`.

Referencia de diseño: [tatr](https://github.com/tsoding/tatr) — `untag`, `graph`, archivo
`tasks/tags` y `summary`. tatr sigue siendo referencia, no dependencia ni formato compatible.
**TQL sigue fuera de alcance** (`PLAN-0.16.0-TAREAS.md`, «un lenguaje nuevo de consultas como TQL»).

## Propiedad

Agy: `tools/tareas.py`, `tools/tareas_contexto.py`, nuevo `tools/tareas_grafo.py`, la parte de
`tarea` en `tools/cli.py` (verbos, ayuda, despacho), `tools/tareas_hechos.py` y `tools/tareas_git.py`
sólo si hace falta para reconocer el archivo de etiquetas como auxiliar, sección nueva en
`docs/12-tareas.md`, nuevo `tests/test_tareas_tatr.py`, y en `estudios/0.17.0-tatr/` sus propios
`AVANCE-AGY.md` (escribirlo primero, con el plan de archivos) e `INFORME-AGY.md` (al final).

Claude: `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/version.py`,
`tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `estudios/0.16.0-tareas/`,
tests de revisión independientes y todo test existente. **No editar esos archivos ni tests
anteriores.** Si un test anterior contradice este encargo, anotarlo en el informe.

Usar sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO
commits.** Claude ejecuta todo. En el informe no afirmar verificaciones que no se corrieron.

## 1. `listar`: columnas que no se desalinean

Hoy `cmd_listar` usa anchos fijos (`{t.id:<32}`, `{etiq_str:<20}`); un ID con sufijo largo
(`20260914-161202-investigar-un-defecto-del-sensor`) corre la fila. Calcular el ancho de ID,
estado, prioridad y etiquetas a partir de las filas que se van a imprimir; el título queda
último y sin relleno. No dejar espacios al final de la línea. `--json` no cambia.

## 2. Archivo de descripciones de etiquetas: `tareas/etiquetas`

Equivalente de `tasks/tags`. Opcional, UTF-8, sin extensión. Una línea por etiqueta:

```
<etiqueta>[espacios y/o comas]<descripción>
```

- Líneas vacías o sólo con espacios se ignoran. La etiqueta es todo hasta el primer espacio o
  coma; la descripción es el resto sin separadores iniciales ni espacios finales. Descripción
  vacía es válida. Comparar etiquetas igual que `listar --etiqueta` (sin distinguir mayúsculas).
- Redefinir una etiqueta: `revisar` lo informa como problema con `etiquetas:<línea>` y sale 1;
  las demás lecturas usan la última definición y avisan por stderr sin cambiar el código.
- Reconocerlo como archivo auxiliar documentado: no es «archivo no reconocido» en `revisar`,
  y `hechos`/`seguimiento` lo inventarían como `auxiliar`, igual que `README.md`.
- Mismos controles que el resto del tracker: no seguir enlaces simbólicos, tope de lectura
  acotado (reutilizar el de P2 si existe), UTF-8 inválido ⇒ problema con ruta, no traceback.
- `resumen` muestra la descripción junto al conteo de cada etiqueta que la tenga, y agrega la
  cantidad de tareas **sin etiquetas** (tatr `UNTAGGED`). En `--json`, agregar campos sin quitar
  ni renombrar los existentes: descripción por etiqueta (`null` si no hay) y `sin_etiquetas`.
- `init` no crea el archivo. Documentar el formato con un ejemplo en `docs/12-tareas.md`.

## 3. `etiquetar` y `desetiquetar`

```bash
oracle tarea etiquetar    <id>... --etiqueta bug [--etiqueta ui]
oracle tarea desetiquetar <id>... --etiqueta obsoleta
oracle tarea desetiquetar --etiqueta obsoleta [--cerradas | --todas]   # masivo, como tatr untag
```

- `--etiqueta` es obligatorio y repetible; acepta coma como en `nueva`, con la misma validación.
- Con IDs (completos o prefijo inequívoco, como `ver`) actúa sobre esas tareas sin mirar estado.
  `etiquetar` exige al menos un ID. `desetiquetar` sin IDs actúa sobre todas las abiertas;
  `--cerradas` y `--todas` como en `listar` (y son incompatibles con IDs explícitos).
- **Primero se resuelve y valida todo** (IDs, etiquetas, registros rotos ⇒ 1 sin escribir nada).
  Después se escribe cada documento con `guardar_documento_atomico`. Documentar que la operación
  no es transaccional entre documentos: un fallo de E/S a mitad deja escritos los anteriores, y
  el mensaje debe decir cuáles quedaron escritos.
- Cambiar **sólo** la línea `- ETIQUETAS:` del bloque de metadatos, preservando el resto byte a
  byte: descripción, campos desconocidos, fin de línea (LF/CRLF), permisos y adjuntos. Si la
  tarea no tiene línea de etiquetas, `etiquetar` la inserta al final del bloque de metadatos.
  Quitar la última etiqueta deja la línea con el mismo formato que usa `nueva` sin etiquetas.
  Conservar el orden existente; las nuevas se agregan al final, sin duplicar (insensible a
  mayúsculas, se conserva la grafía que ya estaba).
- Idempotente: una tarea que no cambia no se reescribe (mtime intacto). Salida estilo compilador,
  una línea por tarea modificada: `tareas/<id>/TAREA.md:<línea>: etiquetas: a, b → a`, y al final
  `N tarea(s) modificada(s)`. Cero modificaciones es éxito (0). `--json` emite la lista de cambios.
- Reutilizar el parser de P1; no duplicar la lectura del bloque de metadatos.

## 4. `grafo`

```bash
oracle tarea grafo [--json] [--proyecto RUTA] > tareas.dot
```

- Nuevo `tools/tareas_grafo.py`, invocado desde `tareas.despachar` por import local.
- Arista A → B cuando el `TAREA.md` de A contiene el **ID completo** de otra tarea válida B.
  Borde de token: el carácter anterior y el siguiente no pueden ser `[A-Za-z0-9_-]`, para que
  `…-sensor` no coincida dentro de `…-sensor-2`. Sin autoaristas, sin duplicados. Incluye tareas
  abiertas y cerradas. Se leen sólo los `TAREA.md` ya validados por la auditoría.
- Salida por defecto DOT a stdout, determinista (orden por origen y destino):
  `digraph tareas {` · un nodo por tarea que participa en alguna arista, con `label` = título y
  estado, escapando `"` y `\` · las aristas · `}`. **No invocar graphviz ni escribir archivos.**
  Documentar `oracle tarea grafo | dot -Tsvg -o grafo.svg` como uso.
- `--json`: `{"nodos": [{"id","titulo","estado"}], "aristas": [{"origen","destino"}]}`, ordenado.
- Registros rotos ⇒ 1 con diagnóstico, igual que `listar`. Sin aristas ⇒ grafo vacío válido, 0.
- Documentar el límite: una mención textual no es una dependencia declarada, y el grafo no mira
  código ni notas fuera de `TAREA.md` (para eso está `referencias`).

## 5. Documentación en `docs/12-tareas.md`

Contrato de los cuatro puntos anteriores y una sección **«Diferencias con tatr»** breve y exacta:
nombres en español y formato no compatible; propiedades duplicadas son error (tatr toma la última);
TQL fuera de alcance, con `listar --etiqueta/--texto` como filtro disponible; `grafo` emite DOT y
no renderiza; captura, adjuntos, seguimiento en Git y hechos no existen en tatr.
Actualizar la ayuda de `oracle tarea` y la lista de verbos de `tools/cli.py`.

## 6. Tests: `tests/test_tareas_tatr.py`

Por el CLI público y proyectos temporales, igual que los tests P1–P3. Como mínimo:
alineación con IDs largos y cortos sin espacios finales; archivo de etiquetas (formato con coma,
con espacios, vacío, redefinición en `revisar` y en `resumen`, UTF-8 inválido, enlace simbólico,
auxiliar en `revisar` y en `hechos`); `resumen` con descripciones y `sin_etiquetas` en texto y JSON;
`etiquetar`/`desetiquetar` con IDs, prefijo, masivo por estado, IDs con `--todas` ⇒ error, CRLF y
campos desconocidos preservados byte a byte, inserción de línea ausente, idempotencia sin
reescritura, registro roto ⇒ 1 sin escribir ninguna tarea, salida con línea correcta;
`grafo` con borde de token, autoarista, duplicados, cerradas, título con comillas, determinismo
entre dos corridas, `--json`, sin aristas y registro roto. Ayuda de los verbos nuevos sin escrituras.
