# Encargo 0.21.0 — una relación `mutante` con variantes y un `requiere` con condición

2026-09-15. Tarea [`20260915-155111-mutante`](../../tareas/20260915-155111-mutante/TAREA.md).
Plan aprobado por el dueño: [vault-kb/planes/PLAN-0.21.0-MUTANTE.md](../../planes/PLAN-0.21.0-MUTANTE.md). Revisa y verifica
Claude.

Leer antes: el plan entero (tiene lo medido y el porqué de cada decisión); `ESPECIFICACION.md` §0
(versiones), la sección de `requiere` y §1 (relaciones); `nucleo/medida.py` (`Medida.de_datos`,
validación de `requiere`, `Medida.evaluar`, `a_datos`, `_requiere_de`, `dependencia_de_medida`);
`nucleo/sintaxis.py` (`_leer_requiere`, la lectura del cuerpo de `medida` y el impresor de
`requiere`); `nucleo/algebra.py` (evaluación de un `donde`, límites); `nucleo/relacion.py` entero;
`nucleo/unidad.py` (derivación de la unidad de un campo); `tools/medida.py` (puntos ciegos por campos
declarados); `nucleo/mutacion.py` (filas de `mutante`); `perfiles/python/mutacion_codigo.py` (filas
de `mutante` y validación del manifiesto); `catalogos/proceso/proceso.test_con_mutante_que_lo_mata.oracle`
y `proceso.codigo_con_mutante_que_lo_mata.oracle`; `nucleo/macros/ninguno-requiere.oracle`.

## Propiedad

Agy: `nucleo/medida.py`, `nucleo/sintaxis.py`, `nucleo/relacion.py`, `nucleo/unidad.py`,
`tools/medida.py`, `nucleo/mutacion.py`, `perfiles/python/mutacion_codigo.py` en lo que pide este
encargo; nuevo `relaciones/mutante.json`; las dos medidas de `catalogos/proceso/` nombradas arriba;
tests nuevos `tests/test_requiere_con_condicion.py` y `tests/test_relacion_variantes.py`; y en
`vault-kb/estudios/0.21.0-mutante/` sus `AVANCE-AGY.md` (primero, con el plan de archivos) e `INFORME-AGY.md`
(al final).

Claude: `corpus/`, `ESPECIFICACION.md`, `README.md`, `NOTAS-DE-RELEASE.md`, `nucleo/version.py`,
`docs/`, `tools/generar_diferencial.py` y lo del diferencial, `tools/mutar.py`, `tools/mutar_codigo.py`,
`.github/`, tests de revisión y **todo test existente**. Si un test existente
contradice el encargo, no editarlo: anotarlo en el informe con el nombre del test y por qué.

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.**
En el informe no afirmar verificaciones que no se corrieron.

## 1. `requiere` con condición — `nucleo/medida.py`

Forma canónica: cada elemento después de `"requiere"` es un nombre de relación (como hoy) **o** una
entrada con condición:

```json
["requiere", "pieza", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]]
```

- `["filas", <relación>, <alias>, <condición>]`: relación y alias con las mismas reglas de nombre que
  una fuente `de`; la condición es una expresión booleana del álgebra, validada con los mismos límites
  y registro que un `donde`, y sólo puede usar ese alias.
- Una relación no puede aparecer dos veces en `requiere`, sea como nombre o con condición.
- **Semántica**, antes de medir, en el mismo lugar donde hoy se corta: `SIN EVIDENCIA` si la relación
  viene vacía **o** si ninguna de sus filas cumple la condición. La condición se evalúa fila por fila
  con el álgebra del `donde`: un campo ausente **levanta `ErrorDeAlgebra`**, igual que en un `donde`
  (no es `False`).
- `sin_evidencia` del veredicto: para un nombre, lo de hoy; para una entrada con condición, un texto
  que nombre la relación y la condición (por ejemplo `mutante sin filas con m.tipo == "codigo"`).
- `a_datos` devuelve la forma canónica recibida; una medida sin condiciones queda **idéntica** a hoy
  (sin el nodo si no hay `requiere`, sin cambios en las entradas de nombre).
- Hechos: las filas de `requiere` y de `dependencia_de_medida` que salen de `requiere` suman la columna
  `con_condicion` (booleano). No quitar ni renombrar columnas existentes.
- La relación de una entrada con condición cuenta como dependencia de la medida igual que un nombre.

## 2. Superficie — `nucleo/sintaxis.py`

- Lector: además de `requiere a, b`, una línea `requiere <relación> <alias> donde <condición>`. Puede
  haber **varias líneas `requiere` seguidas**; se juntan en un solo nodo, en el orden en que aparecen.
  La condición se lee con el lector de expresiones del `donde`.
- Impresor: una línea con todos los nombres (si hay) y una línea por entrada con condición, en el orden
  canónico. Leer lo impreso da la misma forma canónica (ida y vuelta).
- Las posiciones de `ambito` y `alcance` y sus rutas de diagnóstico siguen funcionando con uno o varios
  renglones `requiere`.
- `ninguno-requiere` no cambia.

## 3. Relaciones con variantes — `nucleo/relacion.py`

```json
["relacion", "mutante",
  ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "tipo", "texto", "sin_unidad"], …],
  ["variantes", "tipo",
    ["variante", "medida", ["campo", "detecciones_conductuales", "entero", "sin_unidad"], …],
    ["variante", "codigo", ["campo", "estado", "texto", "sin_unidad"], …]],
  ["alcance", "…"]]
```

- `variantes` es opcional y va entre `campos` y `alcance`: una relación sin él sigue siendo de cuatro
  elementos y su `a_datos` no cambia.
- Reglas, cada una con su `RelacionMalDeclarada` y un mensaje que nombre relación y campo o variante:
  el discriminante es un campo común de tipo `texto`; hay al menos una variante; los valores de
  variante son textos no vacíos y únicos; cada variante declara al menos un campo con la forma de
  `campo` de siempre; un campo de variante no repite un campo común; el mismo nombre en dos variantes
  exige el mismo tipo y la misma unidad; dentro de una variante no se repite un campo.
- `Relacion` expone los campos comunes como hoy (`campos`) y las variantes aparte, más una forma de
  pedir **todos** los campos declarados (comunes y de variantes) para quien sólo necesita buscar uno
  por nombre.
- Hechos: `campo_declarado` suma `variante` (`""` para los comunes, el valor para los de variante), y
  un campo que aparece en dos variantes da una fila por variante; `relacion_declarada` suma `variantes`
  (cantidad, 0 sin variantes). No quitar ni renombrar columnas.

## 4. Quién busca campos — `nucleo/unidad.py`, `tools/medida.py`

- La derivación de unidad de `["campo", alias, nombre]` encuentra también los campos de variante.
- Los puntos ciegos de `tools/medida.py` consideran todos los campos declarados, comunes y de variante.

## 5. `mutante`

- Nuevo `relaciones/mutante.json` con las dos variantes. Comunes: `id`, `apunta_a`, `cambio`, `tipo`.
  Variante `medida`: `detecciones_conductuales`, `rechazos_del_algebra` (enteros). Variante `codigo`:
  los que hoy exige `requeridos` en `perfiles/python/mutacion_codigo.py` fuera de los comunes, con su
  tipo real. Todos `sin_unidad`. Un `alcance` que diga qué no ve la relación.
- `nucleo/mutacion.py`: cada fila de `mutante` suma `"tipo": "medida"`.
- `perfiles/python/mutacion_codigo.py`: cada fila suma `"tipo": "codigo"`; `requeridos` y la validación
  del manifiesto exigen `tipo == "codigo"`. Un manifiesto sin `tipo` se rechaza como inválido.
- Las dos medidas, en forma plana (no la macro), con su prosa actual intacta:
  - `proceso.test_con_mutante_que_lo_mata`: `de mutante m`, `donde m.tipo == "medida"`, después su
    `donde` actual; `requiere mutante m donde m.tipo == "medida"`.
  - `proceso.codigo_con_mutante_que_lo_mata`: `de mutante m`, `donde m.tipo == "codigo"`, después su
    predicado actual; `requiere mutante m donde m.tipo == "codigo"`.
  - Si el `alcance` de alguna dice algo que deja de ser cierto (por ejemplo, qué pasa con `mutante`
    vacía), ajustarlo lo mínimo y anotarlo en el informe.

## Tests

`tests/test_requiere_con_condicion.py`: carga y rechazo de cada forma inválida (alias, relación
repetida, condición mal formada o no booleana, alias ajeno en la condición); SIN EVIDENCIA con relación
vacía, con filas de otro tipo y sin filas que cumplan; mide con al menos una fila que cumple; campo
ausente en la condición levanta; medida sin condición idéntica a hoy (forma canónica y veredicto);
hechos con `con_condicion`; lectura e impresión `.oracle` con una, varias y ninguna línea `requiere`,
con ida y vuelta; `ambito` y `alcance` después de varias líneas `requiere`.

`tests/test_relacion_variantes.py`: cada regla de variantes con su rechazo; `a_datos` de ida y vuelta
con y sin variantes; hechos `campo_declarado` y `relacion_declarada`; derivación de unidad de un campo
de variante; `relaciones/mutante.json` carga.

Sobre `mutante`, sin herramientas: con una evidencia mezclada (una fila de cada tipo) cada medida de
`proceso` mide su fila sin levantar; con filas sólo del otro tipo, cada una sale SIN EVIDENCIA.
