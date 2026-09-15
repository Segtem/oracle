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

## La referencia independiente, versiones y diferencial

La referencia del diferencial la re-derivó agy en una conversación y un proyecto nuevos, confinado a un
directorio con la especificación, las dos DECISION, la referencia anterior y un contrato (detalle en
`diferencial/referencia/PROCEDENCIA.md`). Sus 21 tests pasan. Encontró dos puntos que la especificación
no decidía, y en los dos el núcleo estaba mal:

- **R11. Cortocircuito entre filas.** Al corregir R1 la evaluación pasó a `any(…)` sobre un generador:
  si una fila ya cumplía, una fila posterior sin el campo no se evaluaba y no levantaba. El veredicto
  dependía del orden de la bolsa (`DECISION-001`). La entrega de agy evaluaba todas las filas; el
  defecto lo introdujo esta revisión.
- **R12. Cortocircuito entre entradas.** La primera entrada sin evidencia cortaba antes de evaluar las
  condiciones siguientes, así que una relación requerida vacía tapaba el error de otra condición.

El núcleo evalúa ahora todas las condiciones en todas las filas antes de decidir; si nada levanta, nombra
la primera entrada sin evidencia, en orden. §2 lo dice. Tests `ReferenciaIndependienteTests`.

`VERSION_ALGEBRA` 0.6 → 0.7, `VERSION_SINTAXIS` 0.4 → 0.5, `VERSION_DISTRIBUCION` 0.20.0 → 0.21.0;
`oracle.json` de Oracle pide álgebra 0.7 porque su catálogo ya usa `requiere` con condición.
`diferencial/simulacion.json` regenerado: 4 mundos × 3 medidas, referencia y Oracle de acuerdo. Esos
mundos no ejercitan el `requiere` con condición; lo que la referencia aportó fueron las dos decisiones.

## Más sobrevivientes, cubiertos

- `nucleo/medida.py:272–273` (`y`/`o` en la condición): ningún test cargaba una condición lógica. Test
  `test_una_condicion_con_y_u_o_carga_si_sus_operandos_son_booleanos`.
- `nucleo/relacion.py:162` (`and` ↔ `or` al reconocer el nodo `variantes`) y `:165` (`<` → `<=` en la
  cantidad de variantes): ningún test daba un quinto nodo con otra cabeza ni una sola variante. Test
  `test_el_nodo_variantes_se_reconoce_por_su_cabeza_y_admite_una_sola`.

Los cuatro verificados aplicando el mutante a mano sobre una copia, igual que `nucleo/relacion.py:165:37` (`< 3` → `< 4`), que apareció después y mata el mismo test. La ronda de `nucleo/medida.py` se
relanzó sobre el árbol con R11 y R12.

## Rondas completas de `nucleo/relacion.py` y `nucleo/medida.py`

- `relacion.py` (151 mutantes, 11 vivos): además de los cinco ya cubiertos, seis `and` ↔ `or` en la
  validación de cada variante y sus campos —una tupla en vez de lista, un nombre de campo inválido pero
  de texto, un tipo desconocido, una unidad en blanco— que ningún test daba; y dos equivalentes en el
  límite `len(item) >= 2`, redundante con el «al menos un campo» de tres líneas más abajo. En vez de
  declararlos, las dos comprobaciones quedaron en una (`len(item) >= 3`). Test
  `test_formas_mal_armadas_dentro_de_las_variantes`; los seis verificados a mano.
- `medida.py` (primera ronda completa, 15 vivos entre 273 y 289): las ramas de `_es_expresion_booleana`
  —`no`, el primer operando de `y`/`o`, una escalar declarada— no las fijaba ningún test, y
  `_validar_alias_en_expr` repetía guardas que `validar_expr` ya cubre. Se reescribieron las dos, más
  cortas y con la misma conducta, con tests `test_no_en_la_condicion_y_el_primer_operando_de_un_logico`,
  `test_una_escalar_declarada_sirve_de_condicion` y `test_la_condicion_de_requiere_solo_usa_su_alias`.
  La ronda se relanzó sobre el archivo final.
