# La especificación puede tener más preguntas sin contestar que las tres que encontró el tercer autor

- ESTADO: CERRADA
- PRIORIDAD: 78
- ETIQUETAS: oracle, especificacion, flaqueza


## Por qué

El tercer autor (tarea `codex`, 2026-09-24) implementó el álgebra 0.8 sólo con `ESPECIFICACION.md` y
encontró tres preguntas que el texto no contestaba: dónde va `ambito`, la aridad de `y`/`o` y
`min`/`max` sobre booleanos. Las encontró por los desacuerdos del diferencial, o sea, sólo en lo que
los mundos y el corpus ejercitan. Lo que ninguno ejercita puede tener más huecos.

## Qué hacer

Leer `ESPECIFICACION.md` como alguien que va a implementarla sin ver el núcleo y listar cada
pregunta que el texto no contesta. Para cada una: el párrafo que la deja abierta, qué hace
`nucleo/` (archivo:línea) y si la referencia (`diferencial/referencia/evaluador.py`) hace lo mismo.
Las que el núcleo y la referencia resuelven igual se escriben en la especificación con lo que ya
hacen; las que resuelven distinto son defectos; las que ninguno resuelve son decisiones de Brian.
Descartar lo que no se pueda sostener con cita.

## Avance

Se realizó la lectura completa de `ESPECIFICACION.md` contrastando el texto con `nucleo/` (`algebra.py`, `medida.py`, `version.py`) y la implementación de referencia (`diferencial/referencia/evaluador.py`, `diferencial/referencia/DECISIONES.md`).
Se generó el relevamiento en `tareas/20260925-014900-huecos-spec/HUECOS.md` identificando y documentando 19 preguntas sin contestar con cita exacta `archivo:línea` en cada afirmación:
- 8 casos de especificación incompleta donde el núcleo y la referencia resuelven igual (lógicos sin cortocircuito, existencia y aridad de `no`, relación ausente en `requiere`, `agrupar` sobre cero filas, prohibición de `resumen` como paso de tubería, prohibición de `sin` como fuente primaria, vocabulario de `ambito`, y cero claves en `agrupar`).
- 11 casos de defectos por discrepancia entre el núcleo y la referencia (desigualdad `!=` en flotantes, formato y valor de `SIN EVIDENCIA`, forma sintáctica de agregados en `agrupar`, semántica de testigos tras pasos posteriores a `donde`, tipeo booleano estricto vs truthiness en predicados, alcance perezoso vs ansioso de validación de claves, numeración de filas en error de clave, subconsultas en `unir`, tratamiento de literales `None`/`null`, validación de orígenes en `segun`, y discrepancias en nombres y cotas de `LimitesAlgebra`).
No se corrió ninguna verificación por shell ni suite de tests.

### Nota (2026-09-25 01:56:48 UTC)

2026-09-24, revisión de Claude: verificadas ejecutando núcleo y referencia con la misma entrada: 2.1 (!= entre flotantes: el núcleo levanta, la referencia da False,1), 2.3 (la forma de agrupar de la tabla de §3 la rechaza el núcleo con MedidaMalDeclarada; la referencia acepta las dos) y 2.5 (donde con un número: el núcleo lo toma como verdadero, la referencia levanta; es la tarea predicado-bool). Propuesta: la sección 1 (8 preguntas) se escribe con lo que núcleo y referencia ya hacen; en 2.1, 2.3, 2.7, 2.8, 2.10 y 2.11 se sigue al núcleo (se corrige la especificación o la referencia); 2.2 es una diferencia de interfaz, no de semántica; 2.4 (qué son los testigos si hay pasos después del último donde), 2.5 (predicado-bool), 2.6 (validar claves de toda la evidencia o sólo de la usada) y 2.9 (un null explícito en un hecho) cambian lo que una medida dice y son decisión de Brian.

### Nota (2026-09-25 02:02:05 UTC)

Se incorporaron en ESPECIFICACION.md los 8 acuerdos de HUECOS §1, contrastados con nucleo/algebra.py y nucleo/medida.py. Se alinearon §2.1, 2.3, 2.7, 2.8, 2.10 y 2.11 con el núcleo mediante texto y cambios en diferencial/referencia/evaluador.py, con 6 tests de regresión en test_evaluador.py; se actualizaron DECISIONES.md y el fixture con tools/generar_diferencial.py --escribir. Verificaciones: 48 tests de la referencia OK; 2453 tests de la suite completa OK; test --rapido VERDE. Quedan reservados a Brian §2.4, 2.5, 2.6 y 2.9; §2.2 es sólo interfaz. No se modificó nucleo/ ni se subieron versiones. No hubo que reapuntar equivalentes.json: no contiene líneas de los archivos modificados.

## Próximo paso

Brian debe decidir la semántica de los puntos 2.4, 2.5, 2.6 y 2.9 de HUECOS.md. Después, armonizar especificación, núcleo y referencia según esas decisiones y verificar el diferencial.

### Nota (2026-09-25 21:42:01 UTC)

2026-09-25: los cuatro puntos que esperaban decisión (2.4 testigos, 2.5 bool estricto, 2.6 claves en toda la evidencia, 2.9 null) son las cuatro decisiones del álgebra 1.0: implementadas en núcleo, especificación y referencia (algebra-10) y publicadas en 0.31.0, con el diferencial en verde en la verificación del corte. Los puntos 1.x quedaron escritos en la especificación en 2465eba.
