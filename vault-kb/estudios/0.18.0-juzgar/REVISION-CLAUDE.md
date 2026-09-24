# Revisión de Claude — 0.18.0 (`oracle juzgar`)

2026-09-15. Borrador abierto mientras agy implementa; se completa con la revisión del código.

## P0 — confirmado, con una cifra corregida

Medido sobre un proyecto temporal con sólo `{"esquema": "oracle.proyecto/v1", "catalogo_base": true}`:

| selección | medidas |
|---|--:|
| `Motor.desde_proyecto` (`catalogos_a_cargar`) | 57 |
| `catalogo_efectivo` | 37 |

Las **20** de más son todas `ambito: del_origen` (por ejemplo `meta.donde_nunca_agrega_filas`,
`meta.el_diagnostico_no_publica_el_dominio`). El avance decía 18: la dirección del hallazgo es
correcta y la cifra no. Además, dentro del propio Oracle la selección no es uniforme:
`aceptacion`, `censar`, `contexto` y `mcp` usan `catalogo_efectivo`; la carga de `cmd_test`,
`mutar`, `diferencial`, `medida`, `cifras`, `trazar` y `metamorficas` usan `catalogos_a_cargar`.

La fachada `Motor` es la que usan LyraGASP (`tools/juzga_oracle.py`) y Jam (`oracle_shadow.py`).
Corregirla queda fuera de 0.18.0 salvo decisión del dueño; `juzgar` no debe heredar el defecto.

## Pendiente de verificar en la entrega

- **Sombras en el código de salida.** El plan de archivos del avance devuelve 0 sólo si
  `informe.ok`. Así, una medida declarada en sombra en `oracle.json` hace fallar `oracle juzgar`
  mientras `oracle test` la tolera: el mismo proyecto, dos veredictos. `juzgar` tiene que evaluarla,
  marcarla `[EN SOMBRA]` y no contarla para el código, igual que `tools/aceptacion.py`.

## Revisión de la entrega

Verificado: `tests/test_juzgar.py` y 14 de 15 tests de `tests/test_juzgar_revision.py` en verde,
junto con CLI, herramientas y MCP (433 tests, 2 fallas: la de sombra y `docs/manual.html`, que es de
Claude). `juzgar` usa `catalogo_efectivo`: una medida `del_origen` del catálogo base ya no juzga a un
consumidor (`AmbitoTests`). Mismas reglas que el encargo para corregir: sólo lectura y edición.

### R1. Sombras (defecto)

`tests/test_juzgar_revision.py::SombraTests` falla: con `seguimiento.referencias_locales_presentes`
declarada en sombra en `oracle.json` y en rojo, `oracle juzgar` sale 1. El mismo proyecto daría dos
veredictos. Corregir en `tools/juzgar.py`:

- leer `configuracion(proy).sombra` (`nucleo/proyecto.py`), como `tools/aceptacion.py`;
- evaluar igual las medidas en sombra y mostrarlas: en texto, marcar `[EN SOMBRA]` con su `desde` y
  su `porque`; en `--json`, un campo `en_sombra` por medida sin quitar ni renombrar lo existente;
- el código de salida cuenta sólo los rojos que **no** están en sombra; sin rojos fuera de sombra, 0.
- Si todas las aplicables están en sombra y en rojo, el texto no puede decir «verde» a secas: tiene
  que decir que el verde es por sombra.

### R2. Despacho duplicado en `tools/cli.py` (código muerto)

`main()` despacha `juzgar` tres veces. El primer bloque —antes de las ayudas— ya atiende
`juzgar`, `--juzgar` y `proyecto juzgar`, así que los otros dos nunca se ejecutan y cada uno es
un sitio de mutación que no puede morir. Dejar un solo despacho.

### R3. Alias y `verbos_aceptados` sin necesidad

`("oracle", "juzgar"): "juzgar"` es un alias hacia sí mismo, y el cambio de `verbos_aceptados` a
`VERBOS.get(sustantivo, VERBOS_DIRECTOS if sustantivo == "oracle" else ())` convierte un sustantivo
desconocido —antes `KeyError`, un defecto visible— en un conjunto vacío. `VERBOS_DIRECTOS` ya
declara `juzgar`, que es lo que alimenta la ayuda y el manual. Revertir los dos cambios salvo que un
test existente los necesite; si lo necesita, decir cuál en el informe.

### R4. `except Exception` → código 2 (menor)

Un error de programación dentro de la evaluación queda informado como entrada inválida. Acotar a
las excepciones que corresponden a entrada o catálogo inválidos (evidencia a la que le falta un
campo, medida mal declarada, escalares) y dejar que el resto sea un error visible.

### R5. `cmd_juzgar` ignora tokens sueltos

El parser saltea cualquier `juzgar`, `--juzgar` o `proyecto` en cualquier posición, así que
`oracle juzgar --con h.json proyecto` sale bien con un argumento de más. Consumir sólo el
sustantivo y el verbo iniciales.

## Al terminar

Tests de regresión para R1–R5 en `tests/test_juzgar.py` y sección «Correcciones tras la revisión»
en `INFORME-AGY.md`, sin afirmar que pasan.

### R6. Documentación con afirmaciones que el código no sostiene

En la sección nueva de `docs/12-tareas.md`:

- «1 MiB para documentos `TAREA.md`, 10 MiB para adjuntos»: esos topes no existen. Leer los reales
  en `tools/tareas_hechos.py` y `tools/tareas_contexto.py` (hoy 2 MiB de lectura de texto y 20 MiB
  para `adjuntar`) y citar sólo los que el extractor aplica, o no citar números.
- `archivos_confirmados_sin_cambios` «comprueba `en_indice == true`, `ignorado == false`»: la medida
  mira `git_comprobado`, `en_head`, `indice` y `trabajo`. Describir exactamente lo que dice su
  `donde`, copiado del `.oracle`.
- «El JSON queda en el proyecto temporal indicado al final»: no hay nada indicado al final.
  Reescribir la frase para que diga dónde queda el archivo.
