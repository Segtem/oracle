# OpenSpec medido con Oracle: `cli-validate`

**Pregunta.** De los escenarios de una spec real de OpenSpec, ¿cuántos se pueden volver una medida de
Oracle que juzgue a la herramienta, y cuántos son prosa?

**Material.** `openspec/specs/cli-validate/spec.md` de Fission-AI/OpenSpec en `79b6aa9`: 12 requisitos y
**31 escenarios**. La spec dibuja un `#### Scenario: Short name` dentro de un bloque de código, como
ejemplo; el parser de OpenSpec lo ignora (bien) y aquí tampoco cuenta. Se juzgó la CLI publicada,
`@fission-ai/openspec` **1.13.2**.

## Método

1. `sensor.py` arma 17 proyectos OpenSpec chicos en directorios temporales (uno por situación que
   pide la spec), corre `openspec validate` de verdad (30 corridas, ~4 s) y emite hechos: `corrida`,
   `item`, `problema`, `resumen`, `estado`, `pie`, `salida` y `en_disco`. No juzga nada.
2. `catalogos/openspec/` tiene **32 medidas** en superficie, una por cláusula observable. Cada
   `porque` cita el número de escenario que la motiva.
3. `corpus.py` escribe el corpus desde la corrida real: por medida, un caso **observado** (la
   corrida entera; rojo real → `falso_verde`, verde real → `verde_correcto`), uno sin evidencia y las
   violaciones mínimas construidas, una por rama de cada disyunción. `oracle caso generar` aportó
   los casos de las medidas sin `sin`.
4. `oracle test`: **aceptación ✓** (57 defectos en rojo, 31 verdes correctos, 32 sin evidencia) y
   **mutación 651/651**, ningún mutante vivo.

```bash
python3 sensor.py --openspec <bin/openspec> --exportar hechos.json
oracle juzgar --proyecto . --con hechos.json
oracle test --proyecto .
```

## Clasificación

- **medible**: el THEN entero es observable en una corrida (código de salida, JSON, un texto que la
  spec da literal) y se juzga sin interpretar.
- **parcial**: parte es observable y parte es un juicio («explain», «helpful», «targeted», «when
  available»). Se mide lo observable y el resto queda escrito en el `alcance`.
- **prosa**: nada observable por este sensor.

| # | escenario | clase | medidas |
|---|---|---|---|
| 1 | No deltas found in change | parcial | `sin_deltas_nombra_no_deltas_found`, `sin_deltas_advierte_titulos_antes_de_operaciones` |
| 2 | Missing required sections | parcial | `seccion_faltante_nombra_encabezados`, `error_de_estructura_remite_a_agents_md` |
| 3 | Missing requirement descriptive text | parcial | `error_de_estructura_remite_a_agents_md` |
| 4 | Bulleted WHEN/THEN under a Requirement | medible | `vinetas_avisan_con_el_texto_de_la_spec`, `vinetas_muestran_la_plantilla` |
| 5 | Non-English main spec | medible | `sin_palabra_clave_avisa`, `sin_palabra_clave_no_falla` |
| 6 | Non-English change delta | medible | ídem |
| 7 | Strict validation preserves keyword enforcement | medible | `estricto_falla_ante_un_aviso` |
| 8 | Requirement body is missing | medible | `requisito_sin_cuerpo_es_error` |
| 9 | Zod validation error | parcial | `todo_problema_nombra_su_archivo` |
| 10 | Change invalid summary | parcial | `pie_trae_dos_a_tres_pasos`, `cambio_invalido_muestra_el_pie` |
| 11 | MODIFIED omits an existing scenario | medible | `modified_nombra_el_escenario_omitido`, `item_invalido_sale_con_1` |
| 12 | MODIFIED names the new header of a rename | medible | `modified_tras_rename_nombra_s2` |
| 13 | MODIFIED header is not in the main spec | medible | `modified_sin_base_no_reporta_omision` |
| 14 | Interactive validation selection | prosa | — (necesita una terminal de verdad) |
| 15 | Non-interactive environments do not prompt | parcial | `sin_argumentos_no_interactivo_sale_con_1`, `sin_argumentos_lista_las_banderas` |
| 16 | Direct item validation | medible | `item_directo_detecta_su_tipo` |
| 17 | Validate everything | medible | `todo_lo_vivo_se_valida`, `nada_archivado_se_valida`, `item_invalido_sale_con_1` |
| 18 | Scope of bulk validation | medible | `todo_lo_vivo_se_valida`, `nada_archivado_se_valida` |
| 19 | Validate all changes | medible | ídem, más `el_filtro_no_mezcla_tipos` |
| 20 | Validate all specs | medible | ídem |
| 21 | Strict validation | medible | `estricto_falla_ante_un_aviso` |
| 22 | JSON output | medible | `resumen_cuadra` |
| 23 | JSON output schema for bulk validation | medible | `resumen_cuadra`, `todo_item_trae_duracion`, `todo_problema_tiene_nivel_conocido`, `item_invalido_sale_con_1` |
| 24 | Show validation progress | prosa | — (sólo se ve en una terminal) |
| 25 | Concurrency limits for performance | prosa | — (interno, «e.g. 4–8», «responsive») |
| 26 | Direct item validation with automatic type detection | medible | `item_directo_detecta_su_tipo` |
| 27 | Ambiguity between change and spec names | parcial | `nombre_no_resuelto_sale_con_1_sin_validar`, `nombre_ambiguo_no_valida`, `nombre_ambiguo_sugiere_type` |
| 28 | Unknown item name | parcial | `nombre_no_resuelto_sale_con_1_sin_validar`, `nombre_desconocido_sugiere_el_mas_cercano` |
| 29 | Explicit type override | medible | `tipo_explicito_manda` |
| 30 | Disabling prompts via flags or environment | parcial | `sin_argumentos_no_interactivo_sale_con_1`, `sin_argumentos_lista_las_banderas` |
| 31 | Required sections parsed with CRLF line endings | medible | `crlf_se_parsea` |

**Cuenta: 19 medibles, 9 parciales, 3 prosa.** Hay alguna medida en 28 de 31 escenarios (90 %), y
61 % se mide entero. Los 12 requisitos tienen algo medible, y 8 tienen algún escenario medible
entero. De los 3 de prosa, el 14 y el 24 se podrían medir con un sensor que abra una pseudoterminal;
el 25 no, porque pide un comportamiento interno con un adjetivo («responsive»).

## Lo que encontró en OpenSpec 1.13.2

Juicio de la CLI real: **28 medidas verdes y 4 rojas**. Las cuatro son divergencias entre la spec y
la herramienta que la implementa. Ni `openspec validate` (estructural) ni `/opsx:verify` (opinión de
un modelo) pueden verlas, porque ninguno corre la CLI contra su propia spec.

1. **Los problemas no nombran su archivo** (esc. 9). El requisito dice que *todo* error, aviso o info
   SHALL incluir la ruta del archivo fuente. De 16 problemas observados, 11 tienen `path` sin archivo
   (`"file"`, `"requirements[0]"`). Los 5 restantes dicen `cap/spec.md`, relativo al cambio, y no
   `openspec/changes/<id>/specs/cap/spec.md`. Es el hallazgo de fondo.
2. **El aviso de escenarios en viñetas no dice lo que la spec dice** (esc. 4). La spec pide
   «Scenarios must use '#### Scenario:' headers»; la CLI dice «Scenarios must use level-4 headers». La
   plantilla de conversión sí está.
3. **Falta la nota «Spec delta files cannot start with titles before the operation headers»**
   (esc. 1). La spec la pide explícita y entre comillas.
4. **Ningún error de estructura remite a `openspec/AGENTS.md`** (esc. 2 y 3). Probablemente es
   deuda de la spec: OpenSpec 1.x dejó de generar ese archivo. Entonces lo que miente es la spec, y el
   rojo es igual de útil, porque dice cuál de las dos hay que cambiar.

Vistos al leer los hechos y **no medidos** (quedan como candidatos):

- En una misma corrida, `path` usa dos notaciones: `requirements.0.scenarios` en el ERROR y
  `requirements[0].scenarios` en el WARNING.
- Un requisito sin cuerpo da el error «must contain SHALL or MUST»: atribuye la falta de cuerpo a la
  palabra clave. La spec lo acepta como error (esc. 8), pero el escenario 3 pide explicar que falta
  texto narrativo.
- El escenario 10 sugiere `openspec change show <id>`; la CLI sugiere `openspec show <id>` porque
  `change show` quedó deprecado. Aquí la desactualizada es la spec.

## Lo que encontró en Oracle

- **La mutación reventaba** con `TypeError: unhashable type: 'list'` en
  `mutadores/segundo_autor.py::_alias_referidos` ante una medida con `unir`, dos pasos, `contar`,
  `<=` y `requiere`. Ningún catálogo existente tenía esa combinación. Se arregló en la raíz, con un
  test que falla sin el arreglo.
- **`oracle caso generar` no fabrica evidencia para medidas con `sin`**: de 32 medidas cubrió 18.
  Las otras 14 necesitaron casos escritos por `corpus.py`.
- `contiene` alcanzó para todas las cláusulas de texto. No hizo falta expresión regular ni prefijo.

## Qué dice esto del encaje OpenSpec ↔ Oracle

La correspondencia **requisito ↔ medida, escenario ↔ caso del corpus** funciona sin tocar el núcleo,
sobre una spec que no se escribió pensando en Oracle. Nueve de cada diez escenarios tienen una
cláusula que se puede volver falsable. Lo que queda afuera es poco y conocido: interacción de
terminal y adjetivos de calidad («helpful», «targeted», «responsive»). Esa parte sí es terreno de un
modelo, y es la única en la que `/opsx:verify` debería opinar.
