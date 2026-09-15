# Encargo 0.22.0 — toda medida lee campos que existen, y un campo ausente se informa igual

2026-09-15. Tarea [`20260915-155654-campos`](../../tareas/20260915-155654-campos/TAREA.md). Plan aprobado
por el dueño: [PLAN-0.22.0-CAMPOS.md](../../PLAN-0.22.0-CAMPOS.md). Revisa y verifica Claude.

Leer antes: el plan entero; `ESPECIFICACION.md` §1.1 (relaciones del lenguaje) y §1.3 (relaciones
declaradas); `nucleo/medida.py` (`RELACIONES_DE_CATALOGO`, `AMBITOS_DE_RELACIONES`,
`relaciones_del_lenguaje_declaradas`, `_extraer_relaciones_de_arbol`, `como_hechos`, `evaluar`,
`Informe`, `medidas_aplicables`); `nucleo/relacion.py` (`ambitos_de_relaciones_declarados`,
`_ambitos_del_arbol`, `hechos_de_relaciones`, `Relacion.todos_los_campos`); `nucleo/unidad.py`
(`hechos_de_unidades`, que es el modelo más cercano de `campo_leido`); los demás emisores con
`RELACIONES_*` y `AMBITOS_DE_RELACIONES` (`nucleo/marco.py`, `nucleo/referente.py`,
`nucleo/diagnostico.py`, `tools/trazar.py`, `tools/metamorficas.py`); `tools/medida.py`
(`relaciones_por_alias`); `nucleo/proyecto.py` (`relaciones_del_proyecto`); `tools/aceptacion.py`
(evaluación de cada caso y de las medidas meta, y la evidencia meta); `tools/juzgar.py`; `tools/mutar.py`
(`_politicas_ok`, «NO pudieron juzgar»); `tools/mutar_codigo.py` (el mismo aviso); los emisores de
`corrida_mutacion` (`perfiles/python/mutacion_codigo.py`), `archivo` (`tools/observar.py`), `modulo` y
`alcanzable` (`perfiles/python/marco.py`); y las medidas que leen `afirmacion` y `hallazgo`
(`catalogos/proceso/proceso.afirmacion_declara_alcance.oracle`,
`proceso.verificador_sin_falsos_rojos.oracle`).

## Propiedad

Agy: los emisores nombrados arriba sólo para agregarles `CAMPOS_DE_RELACIONES`; el lector de esos
literales en `nucleo/relacion.py`; nuevo emisor de `campo_leido` (en `nucleo/unidad.py` junto a
`hechos_de_unidades`, o un módulo nuevo en `nucleo/` si queda más claro: decidirlo y documentarlo);
`nucleo/medida.py` (evaluación que separa lo que no se pudo juzgar, `Informe.no_juzgaron`);
`tools/aceptacion.py`, `tools/juzgar.py`, `tools/mutar.py` y `tools/mutar_codigo.py` en lo que pide este
encargo; nuevas declaraciones en `relaciones/`; nueva medida
`catalogos/meta/meta.toda_medida_lee_campos_que_existen.oracle`; tests nuevos
`tests/test_campos_de_relaciones.py` y `tests/test_no_juzgaron.py`; y en `estudios/0.22.0-campos/` sus
`AVANCE-AGY.md` (primero, con el plan de archivos) e `INFORME-AGY.md` (al final).

Claude: `corpus/`, `ESPECIFICACION.md`, `README.md`, `NOTAS-DE-RELEASE.md`, `nucleo/version.py`, `docs/`,
`equivalentes.json`, `.github/`, tests de revisión y **todo test existente**. Si un test existente
contradice el encargo, no editarlo: anotarlo en el informe con el nombre del test y por qué.

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.**
En el informe no afirmar verificaciones que no se corrieron.

## 1. Los campos de lo que emite el núcleo

- En cada archivo que declara `RELACIONES_*` para relaciones del lenguaje, un mapa literal
  `CAMPOS_DE_RELACIONES = {"<relación>": ("<campo>", …), …}` con los campos de cada fila que emite.
- `campos_de_relaciones_declarados(raiz=None) -> dict[str, tuple[str, ...]]` en `nucleo/relacion.py`,
  que lo lee **sin importar** los módulos (AST, como `ambitos_de_relaciones_declarados`) y falla cerrado
  con `RelacionMalDeclarada` ante: un literal que no es un mapa de textos a tuplas de textos, un campo
  repetido, una relación declarada dos veces entre archivos, una relación del lenguaje sin campos, o
  campos para una relación que no está en ningún `RELACIONES_*`.
- Test por emisor: las filas emitidas traen **exactamente** los campos declarados (ni uno más ni uno
  menos), al menos para las relaciones que se pueden emitir en un test sin herramientas externas.

## 2. Las relaciones de proceso que lee el catálogo

Declarar en `relaciones/` (raíz del repo) `corrida_mutacion`, `archivo`, `modulo`, `alcanzable`,
`afirmacion` y `hallazgo`, con la forma de siempre (`campo` con tipo y unidad, `alcance`). Los campos
salen de lo que emite cada productor; para `afirmacion` y `hallazgo`, que no emite nadie en Oracle, de lo
que leen sus medidas, y el `alcance` lo dice. Unidades: `sin_unidad` salvo que el campo sea una magnitud
con unidad clara en su emisor.

## 3. `campo_leido`

Una relación del lenguaje nueva, con sus `RELACIONES_*`, `AMBITOS_DE_RELACIONES` (`universal`) y
`CAMPOS_DE_RELACIONES`. Una fila por cada lectura `["campo", alias, nombre]` en la forma canónica de cada
medida del catálogo:

- `medida`, `relacion` (resuelta por las fuentes y por las entradas `["filas", relación, alias, …]` de
  `requiere`; una lectura cuyo alias no se resuelve **no** se emite como `existe: true`: decidir si se
  emite con `relacion: ""` y documentarlo), `campo`;
- `origen`: `"declarada"` si la relación está en las relaciones del proyecto (campos comunes y de
  variante), `"lenguaje"` si está en `campos_de_relaciones_declarados()`, `"sin_declarar"` si no;
- `existe`: si el campo está entre los conocidos de la relación; `false` para `sin_declarar`.

`["hecho", alias]` y `["col", nombre]` no son lecturas de campo. Se emite donde `tools/aceptacion.py` arma
la evidencia meta (junto a `hechos_de_unidades`) y en cualquier otro lugar que emita hoy
`cantidad_comparada` para medidas meta.

## 4. `meta.toda_medida_lee_campos_que_existen`

En `catalogos/meta/`, superficie `.oracle`, forma `ninguno` sobre `campo_leido` con
`donde c.origen != "sin_declarar" y c.existe == false`, `umbral <= 0 segun contrato`, `ambito universal`,
con `porque` y `alcance` en español que digan qué ve y qué no (no ve relaciones sin declarar, ni si la
variante leída es la que la medida filtra).

## 5. Una sola forma de evaluar que separa lo que no se pudo juzgar

- `nucleo/medida.py`: una función (nombre a elección, documentado) que evalúa un iterable de medidas
  sobre una evidencia y devuelve un `Informe`; una medida cuya evaluación levanta `ErrorDeAlgebra` va a
  `Informe.no_juzgaron` como `(id, motivo)` en vez de cortar. El resto de las medidas se evalúa igual.
  `evaluar` existente no cambia de conducta.
- `Informe` suma `no_juzgaron: tuple = ()`. `ok` es falso si hay alguna; `texto()` las lista aparte, con su
  motivo, sin mezclarlas con rojos ni con SIN EVIDENCIA; `a_json()` suma `no_juzgaron` como lista de
  `{"id", "motivo"}`. Con `no_juzgaron` vacío, `texto()` y `a_json()` no cambian salvo la clave nueva.
- `tools/aceptacion.py`: las medidas meta y la evaluación de cada caso usan la función; un caso o una
  medida que no juzgó es una falla de la corrida con su motivo, nunca un traceback.
- `tools/juzgar.py`: la usa; si alguna medida no juzgó, sale 2 como hoy, con el motivo.
- `tools/mutar.py` y `tools/mutar_codigo.py`: la usan en lugar de su `try` propio y conservan el aviso
  «NO pudieron juzgar»; `mutar.py` cuenta una que no juzgó como política incumplida (`_politicas_ok`);
  `mutar_codigo.py` sigue sin depender de los veredictos del catálogo para su código de salida.
- `tools/observar.py` y `Motor.evaluar` **no** cambian.

## Tests

`tests/test_campos_de_relaciones.py`: el lector y cada rechazo; que las 25 relaciones del lenguaje y
`campo_leido` tengan campos; emisores contra sus campos declarados; `campo_leido` con lecturas de relación
declarada (común y de variante), del lenguaje y sin declarar, con campo existente y no existente,
lecturas dentro de la condición de `requiere`, `hecho` y `col` ignorados; la medida meta en verde sobre el
catálogo de Oracle y en rojo con una medida que lee un campo inexistente de `mutante`.

`tests/test_no_juzgaron.py`: la función con una medida que levanta y otra que no; `Informe.ok`, `texto()`
y `a_json()` con y sin `no_juzgaron`; `aceptacion` sin traceback ante un caso cuya evidencia no trae un
campo; `juzgar` sale 2; `_politicas_ok` de `mutar.py` falso con una que no juzgó.
