# Una tarea no puede declarar con qué medidas se cierra, así que cerrarla no se comprueba

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, tracker, metalenguaje


## Qué pasó

2026-09-19, en LyraGASP: Codex explicó bien que el tracker (`tareas/`) es la cola de trabajo y que
`medidas/` son los contratos, y que una tarea como «dedos deformados» sólo se cierra cuando su
hallazgo tiene una medida que pasa la aceptación. Es la regla del `CLAUDE.md` de LyraGASP («todo
hallazgo que se pueda medir se escribe como medida antes de darlo por cerrado»). Pero hoy ese
vínculo es **prosa**: nada impide cerrar la tarea con la medida inexistente o en rojo.

## Qué hacer

1. Una forma de declarar, en la tarea, las medidas que la cierran (por ejemplo una línea
   `- CIERRA CON: recarga.montage_en_slot_cuerpo_entero, dedos.flexion_digital`), leída por el
   parser del tracker y emitida por `oracle tarea hechos` como relación (`tarea_cierre_medida`:
   tarea, medida).
2. Una política en `ejemplo/seguimiento-tareas` (y para copiar en los consumidores): **ninguna tarea
   cerrada cuyo criterio de cierre nombre una medida que no existe en el catálogo o que no está
   verde en la última aceptación**. Decidir de dónde sale el «está verde»: el tracker no evalúa
   medidas, así que la evidencia tiene que venir de juntar `tarea hechos` con los hechos de la
   aceptación del proyecto, y eso se diseña antes de escribirlo.
3. Una tarea sin `CIERRA CON` sigue siendo válida: no todo trabajo es medible (documentación,
   decisiones). La política sólo mira las que lo declaran.

## Diseño: integración de hechos del tracker con la aceptación

### 1. Principio de separación e independencia

El tracker (`oracle tarea`) **no evalúa medidas ni accede al catálogo**:
- Preserva su naturaleza liviana, offline y sin dependencias del motor de medidas.
- `oracle tarea hechos` sólo audita el árbol de `tareas/` y emite la declaración estructural:
  la nueva relación **`tarea_cierre_medida`** (`tarea_id: texto`, `medida: texto`).
- El estado de veredicto («está verde», «dio rojo», o no existe) proviene del subsistema de evaluación
  del proyecto (`oracle test`, `tools/aceptacion.py` o `oracle juzgar`).

### 2. Contrato de hechos de aceptación (`aceptacion_medida`)

La evidencia de la última aceptación se reifica como la relación **`aceptacion_medida`**:
- **`medida`** (`texto`, `sin_unidad`): identificador canónico de la medida (ej. `dedos.flexion_digital`).
- **`ok`** (`booleano`, `sin_unidad`): `true` si la medida está en el catálogo y pasó la aceptación; `false` si dio rojo.
- **De dónde sale**:
  - Emisor elegido: `oracle juzgar --json` sobre la evidencia actual del dominio y el catálogo del proyecto. El flujo consumidor convierte `medidas` (`id`, `ok`) a `aceptacion_medida` (`medida`, `ok`).
  - `oracle test` comprueba el corpus (incluidos rojos esperados); su éxito no acredita que las medidas estén verdes sobre el dominio. No se agregará `oracle test --hechos-aceptacion`.
  - Se conserva el `ok` individual, incluso si una sombra perdona un rojo. `no_aplicadas` no aporta filas. Sólo se convierte una salida JSON válida de una ejecución terminada con código 0 o 1; cualquier error aborta el flujo, sin reutilizar evidencia anterior.
  - Si una medida no existe en el catálogo o no fue evaluada, no figura con `ok: true` en `aceptacion_medida`.

### 3. Composición de la evidencia para `oracle juzgar`

Para juzgar las políticas de `seguimiento-tareas`, la evidencia es un único objeto JSON relacional:
`{ "relacion": [filas] }`.
- **Composición**: se unen las relaciones emitidas por `oracle tarea hechos` y las emitidas por la aceptación:
  `evidencia_total = {**hechos_tracker, **hechos_aceptacion}`.
- **En el flujo de trabajo / CI**:
  ```bash
  oracle tarea hechos --git > /tmp/hechos-tracker.json
  # la corrida de aceptación del proyecto emite /tmp/hechos-aceptacion.json
  python3 -c 'import json, sys; d={}; [d.update(json.load(open(f))) for f in sys.argv[1:]]; print(json.dumps(d))' \
      /tmp/hechos-tracker.json /tmp/hechos-aceptacion.json > /tmp/hechos-combinados.json
  oracle juzgar --proyecto ejemplo/seguimiento-tareas --con /tmp/hechos-combinados.json
  ```
- **Compatibilidad fail-closed y aplicabilidad**:
  - Si un proyecto sólo corre `oracle tarea hechos` sin entregar `aceptacion_medida`, la política no aplica (aparece en `NO SE APLICARON`), preservando compatibilidad hacia atrás.
  - Si la relación `aceptacion_medida` se entrega (incluso vacía `[]`), la política aplica y exige que toda tarea cerrada que declare medidas las tenga presentes con `ok == true`.

### 4. Formulación de la política (`seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre`)

Se implementará en `ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre.oracle`:
```oracle
medida seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre:
    de tarea_cierre_medida cm
    unir tarea_seguimiento t
    donde cm.tarea_id == t.id y t.estado_declarado == "CERRADA"
    sin aceptacion_medida am donde am.medida == cm.medida y am.ok == true
    resumen contar(1)
    umbral <= 0 segun contrato porque "toda tarea cerrada cuyo criterio de cierre nombre medidas exige que esas medidas existan en el catálogo y estén verdes en la última aceptación"
    ambito del_origen
    alcance "cruza las medidas declaradas en CIERRA CON de tareas CERRADAS con la relación aceptacion_medida de la evidencia. NO evalúa código ni reejecuta medidas directamente; juzga sobre los veredictos provistos. Una tarea sin CIERRA CON no emite filas y cumple por vacuidad"
```

### 5. Plan de implementación por pasos

0. **Paso 0 (Emisor decidido)**: convertir la salida actual de `oracle juzgar --json` en el flujo consumidor, según el contrato de la sección 2.
1. **Paso 1 (Parser)**: en `tools/tareas.py`, parsear `- CIERRA CON: ...` en `parsear_tarea` guardando la tupla de medidas saneadas en `Tarea.cierra_con`, preservando el campo en operaciones atómicas (`actualizar_estado_tarea`, `etiquetar`).
2. **Paso 2 (Hechos del tracker)**: en `tools/tareas_hechos.py`, emitir la relación `tarea_cierre_medida` (siempre presente en la salida de `oracle tarea hechos`).
3. **Paso 3 (Declaraciones L−1)**: crear `ejemplo/seguimiento-tareas/relaciones/tarea_cierre_medida.json` y `aceptacion_medida.json`.
4. **Paso 4 (Política)**: escribir `ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre.oracle`.
5. **Paso 5 (Corpus y fijación)**: agregar casos en `ejemplo/seguimiento-tareas/corpus/` cubriendo tareas abiertas con medidas, tareas cerradas sin medidas, tareas cerradas con medidas verdes, y tareas cerradas con medidas rojas o inexistentes.


## Avance

- Se leyó la especificación del tracker (`docs/12-tareas.md`), el código del parser y tracker (`tools/tareas.py`), extractor de hechos (`tools/tareas_hechos.py`), evaluador de juzgamiento (`tools/juzgar.py`), arnés de aceptación (`tools/aceptacion.py`), álgebra relacional (`nucleo/algebra.py`) y políticas de ejemplo (`ejemplo/seguimiento-tareas/`).
- Se completó el diseño detallado de cómo se juntan los hechos del tracker con los de la aceptación:
  - Se definió el contrato de la relación `tarea_cierre_medida` (del tracker) y de `aceptacion_medida` (de la aceptación).
  - Se resolvió el mecanismo de composición de evidencia como unión de relaciones para `oracle juzgar`, preservando la independencia estricta del tracker frente a la evaluación de medidas.
  - Se formuló la política de seguimiento en el álgebra de Oracle con anti-junta `sin`.
  - Se definió el plan ordenado en 5 pasos para la implementación.
- Conforme a la instrucción, no se ejecutó shell ni se afirmaron verificaciones dinámicas no corridas en este turno.


### Nota (2026-09-21 20:43:24 UTC)

2026-09-21, revisión de Claude del diseño de agy: la dirección es buena (el tracker sólo declara tarea_cierre_medida; el veredicto viene de la aceptación; la política usa sin). Dos correcciones antes de implementar: (1) la superficie de la medida está mal — es 'unir tarea_seguimiento t' y 'sin aceptacion_medida am donde …', sin 'de'; (2) falta el paso 0: hoy NADIE emite aceptacion_medida. oracle test no exporta sus veredictos como hechos; oracle juzgar --json sí trae id y ok por medida. Hay que decidir el emisor (por ejemplo 'oracle test --hechos-aceptacion <ruta>') antes que el parser.

### Nota (2026-09-21 21:29:34 UTC)

Decisión del paso 0 (antes del parser): el emisor elegido es oracle juzgar --json sobre evidencia actual del dominio y catálogo del proyecto. El flujo consumidor transforma medidas[].id/ok en aceptacion_medida[].medida/ok; conserva el ok individual (un rojo perdonado por sombra NO es verde), omite no_aplicadas y sólo publica evidencia si juzgar termina con 0 o 1 y entrega JSON válido. Errores de ejecución abortan el flujo sin reutilizar una corrida anterior. oracle test valida expectativas del corpus, incluidos rojos esperados, y no se usará como prueba de dominio verde. La implementación de este turno cubre el próximo paso del parser; la composición queda para la integración posterior. Se corrige también la superficie del diseño: unir tarea_seguimiento t y sin aceptacion_medida am, sin de.

### Nota (2026-09-21 21:32:22 UTC)

Implementado el paso 1: parsear_tarea reconoce CIERRA CON en el bloque de metadatos; Tarea.cierra_con es una tupla opcional y a_dict la publica como lista. Valida la gramática ASCII de medidas sin importar el motor, recorta espacios y deduplica conservando orden; rechaza identificadores inválidos, elementos vacíos entre comas y campos duplicados. Ausente o vacío conserva compatibilidad. Estado y etiquetas preservan los bytes del criterio mediante las escrituras atómicas existentes. Documentado en docs/12-tareas.md. Agregados 7 tests en tests/test_tareas_cierre_medidas.py: opcionalidad/JSON, saneamiento, errores, aislamiento del cuerpo, orden de metadatos, preservación LF/CRLF y permisos, y fallo de reemplazo sin modificar el original. Verificación: 11 tests específicos (incluidos test_tareas_atomicas) OK; nueva corrida de los 7 tests tras acotar IGNORECASE al nombre del campo OK; suite solicitada python3 -B -m unittest discover -s tests -t . -q: 2386 tests en 81.556 s, OK. git diff --check OK. Sin commits. La tarea sigue ABIERTA: resta emitir relaciones y aplicar la política; el parser no bloquea cierres por veredictos.


### Nota (2026-09-22 11:06:07 UTC)

Completados los pasos 2–5. tools/tareas_hechos.py emite siempre tarea_cierre_medida, incluso [], ordenada por tarea y conservando el orden saneado de sus criterios. Agregadas las declaraciones tarea_cierre_medida/aceptacion_medida, la política seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre con unir/sin y 7 casos construidos (33 casos totales). El flujo consumidor ejecutable ejemplo/seguimiento-tareas/cierre_medidas.py corre juzgar --json sobre evidencia actual del dominio, conserva el ok individual incluso ante sombra, omite no_aplicadas, exige códigos 0/1 con informe válido y combina sólo evidencia de esta ejecución en un temporal privado. Ante errores aborta sin publicar ni reutilizar evidencia anterior. El tracker sigue independiente y el cierre no se bloquea en el comando: la política se exige en revisión/CI.

Pruebas agregadas en tests/test_cierre_medidas_integracion.py: contrato determinista y saneado, relación ausente versus vacía, flujo CLI real verde/rojo/sombra/no evaluada/inexistente/abierta/sin criterios, errores tras una corrida verde, formatos inválidos y fallos operacionales. Actualizadas las expectativas del contrato en test_tareas_hechos y test_tareas_p3_revision. Documentados contrato y flujo en docs/12-tareas.md y README del ejemplo; regeneradas las cifras del README raíz con tools/cifras.py --actualizar.

Verificación final: 38 tests específicos y 24 de revisión OK; python3 -B -m unittest discover -s tests -t . -q: 2393 tests en 83.027 s, OK, evidencia [suite completa](verificacion/suite-completa.log). python3 -B tools/cli.py test: VERDE, incluye otra corrida de 2393 unitarios y 1010/1010 mutantes de medida muertos, evidencia [oracle test](verificacion/oracle-test.log); es el nivel normal, sin --todo ni mutación de código. python3 -B tools/cli.py test --proyecto ejemplo/seguimiento-tareas: VERDE, 33 casos y 109/109 mutantes muertos, evidencia [ejemplo](verificacion/ejemplo-test.log). git diff --check OK. Las dos expectativas antiguas detectadas en la primera suite y las cifras desactualizadas detectadas en la primera verificación general quedaron corregidas y verificadas en estas corridas finales. Sin commits; cambios ajenos preservados. Implementación terminada; permanece ABIERTA para revisión y cierre con commit por Claude.

## Próximo paso

Claude: revisar el diff y los logs de verificación de esta tarea; la implementación de los pasos 1–5 está terminada y la suite completa quedó verde. Marcar la tarea CERRADA y realizar el commit de cierre `20260919-171824-cierre-medidas: done`, seleccionando sólo los cambios de esta tarea y preservando los cambios ajenos. Codex no creó commits porque `.git` es de sólo lectura.
