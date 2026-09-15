# Revisión de Claude — 0.21.0 (`mutante` con variantes y `requiere` con condición)

2026-09-15. Entrega de agy terminada a las 14:28 (`AVANCE-AGY.md`, `INFORME-AGY.md`).

## Lo que se verificó

- `tests/test_mutante_revision.py`, escrito contra el encargo **antes** de leer la entrega: pasó entero
  sobre ella (junto con los tests de agy, 56).
- El diseño coincide con el encargo: forma canónica de `requiere` con `["filas", …]`, lector de varias
  líneas `requiere`, relaciones con `variantes` y sus reglas, hechos aditivos (`con_condicion`,
  `variante`, `variantes`), `relaciones/mutante.json` con los campos reales de los dos productores,
  `tipo` en los dos productores y en la validación del manifiesto, y las dos medidas en forma plana.
- Ninguna edición fuera de la propiedad del encargo; el único test existente que agy señaló
  (`tests/test_medida.py:150`, sin `con_condicion`) estaba bien señalado.

## Defectos, corregidos por Claude

### R1. La condición recorría el nodo `clave` (traceback en la aceptación)

`Medida.evaluar` iteraba `evidencia.get(relacion)` crudo. Una relación puede traer `["clave", […]]` a la
cabeza (ESPECIFICACION §1), y el caso `059-clave-declarada-en-un-caso` —que ya tenía `mutante` con
`clave(id)`— hacía reventar `tools/aceptacion.py` con `AttributeError: 'list' object has no attribute
'get'`. Ningún test de la entrega ni de la revisión usaba una clave. Corregido con `separar_clave`, como
el resto del álgebra; test `test_la_condicion_recorre_filas_y_no_el_nodo_clave` (también una relación
que sólo trae la clave sale SIN EVIDENCIA).

### R2. Una condición que no da booleano pasaba en silencio

`_es_expresion_booleana` acepta cualquier escalar registrada como condición, y la evaluación filtraba
con la verdad de Python: una escalar que devuelve `1` o `0` decidía `SIN EVIDENCIA` sin que nada lo
dijera. Corregido en la evaluación: `_cumple` levanta `ErrorDeAlgebra` si el resultado no es `bool`.
Test `test_una_condicion_que_no_da_booleano_levanta_al_evaluar`.

### R9. Una validación nueva sobre algo que ya cargaba (subía la MAYOR)

La entrega validaba los **nombres simples** de `requiere` con `NOMBRE_RELACION_RE` y los guardaba con
`strip()`. En 0.6 cualquier texto no vacío cargaba tal cual; rechazar lo que antes cargaba es un cambio
MAYOR según §0, y el plan declara la subida como MENOR. Los nombres simples vuelven a la regla de 0.6;
la expresión de nombre queda sólo para las entradas con condición, que son nuevas. Test
`test_un_nombre_simple_de_requiere_conserva_la_regla_de_06`.

## Tests existentes actualizados (propiedad de Claude)

Todos por columnas o campos que el encargo agrega, ninguno por un cambio de conducta:

- `test_medida`: la fila de `requiere` suma `con_condicion`.
- `test_relacion`: `relacion_declarada` suma `variantes` y `campo_declarado` suma `variante`.
- `test_mutacion`, `test_mutacion_codigo`: las filas de `mutante` suman `tipo`; la reanudación suma dos
  corrupciones nuevas que la validación rechaza (`tipo` distinto y `tipo` faltante).
- `test_vigilar`: las relaciones falsas exponen `todos_los_campos`.
- `test_macro`: una medida escrita entera se justifica también por un `requiere` con condición, que
  ninguna macro expresa (igual que `unir` y `agrupar`).
- `equivalentes.json`: los dos sitios de `nucleo/sintaxis.py` se corrieron de línea (1427→1459,
  1448→1480) con el mismo texto; `docs/manual.html` regenerado por el alcance nuevo de las dos medidas.

## Observaciones sin cambio

- `from .sintaxis import _expr` dentro de `Medida.evaluar`: el núcleo de evaluación importa el impresor
  de la superficie para redactar `sin_evidencia`. Funciona y es perezoso; se deja.
- `Relacion.todos_los_campos` deduplica por nombre, lo que es correcto porque las reglas exigen el mismo
  tipo y unidad para un nombre repetido entre variantes.

## Después del primer push (CI de `5040565` en rojo)

### R10. `tools/mutar.py` salía 1 por un SIN EVIDENCIA

El paso `python tools/mutar.py` de `contratos` falló en 3.11 y 3.13. La ronda de mutación de medidas
sólo produce filas `tipo == "medida"`, y `proceso.codigo_con_mutante_que_lo_mata` —que ahora sí aplica
por relación— sale SIN EVIDENCIA porque pide filas de código. El veredicto es correcto; lo que estaba
mal es que la herramienta lo contara como política incumplida (`informe.ok`). Antes de este corte esa
medida levantaba y figuraba entre las que «NO pudieron juzgar», que no hacían fallar la ronda.
`_politicas_ok` cuenta sólo los rojos; un SIN EVIDENCIA se imprime y no tumba. `tools/mutar_codigo.py`
no tenía el problema: su código de salida no depende de los veredictos del catálogo. Test
`test_un_sin_evidencia_no_hace_fallar_la_ronda_y_un_rojo_si`; `python tools/mutar.py` sale 0.

### Texto de SIN EVIDENCIA

`Veredicto.linea` imprime «<faltante>» vacía; con la frase de la entrega salía
«mutante sin filas con m.tipo == "codigo"» vacía. `sin_evidencia` de una entrada con condición pasa a
ser `mutante con m.tipo == "codigo"`.

### Sobrevivientes de la mutación, cubiertos

- `nucleo/medida.py:267` (`return True` → `None` y → `False`): la condición literal booleana no la
  cargaba ningún test. Test `test_una_condicion_literal_carga_y_se_comporta_como_el_nombre`.
- `nucleo/relacion.py:72` (`frozen=True` → `False` en `Variante`): nadie fijaba la inmutabilidad, como sí
  se fija la de `Campo` y `Relacion`. Test `test_una_variante_es_inmutable`.

Los tres verificados aplicando el mutante a mano sobre una copia: el test nuevo falla con cada uno.
