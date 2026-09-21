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
  - En proyectos con `oracle test`: exportación de los veredictos de medidas emitidos por la suite de aceptación.
  - En proyectos que juzgan evidencia del dominio: los veredictos emitidos por `oracle juzgar --json` (campo `medidas` con su `id` y `ok`).
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
    unir de tarea_seguimiento t
    donde cm.tarea_id == t.id y t.estado_declarado == "CERRADA"
    sin de aceptacion_medida am donde am.medida == cm.medida y am.ok == true
    resumen contar(1)
    umbral <= 0 segun contrato porque "toda tarea cerrada cuyo criterio de cierre nombre medidas exige que esas medidas existan en el catálogo y estén verdes en la última aceptación"
    ambito del_origen
    alcance "cruza las medidas declaradas en CIERRA CON de tareas CERRADAS con la relación aceptacion_medida de la evidencia. NO evalúa código ni reejecuta medidas directamente; juzga sobre los veredictos provistos. Una tarea sin CIERRA CON no emite filas y cumple por vacuidad"
```

### 5. Plan de implementación por pasos

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


## Próximo paso

Implementar en `tools/tareas.py` el soporte del campo de metadatos `- CIERRA CON:` en `parsear_tarea`, agregando el atributo `cierra_con: tuple[str, ...]` al dataclass `Tarea`, validando los identificadores de medidas y preservando el campo de forma atómica en modificaciones del documento.

### Nota (2026-09-21 20:43:24 UTC)

2026-09-21, revisión de Claude del diseño de agy: la dirección es buena (el tracker sólo declara tarea_cierre_medida; el veredicto viene de la aceptación; la política usa sin). Dos correcciones antes de implementar: (1) la superficie de la medida está mal — es 'unir tarea_seguimiento t' y 'sin aceptacion_medida am donde …', sin 'de'; (2) falta el paso 0: hoy NADIE emite aceptacion_medida. oracle test no exporta sus veredictos como hechos; oracle juzgar --json sí trae id y ok por medida. Hay que decidir el emisor (por ejemplo 'oracle test --hechos-aceptacion <ruta>') antes que el parser.
