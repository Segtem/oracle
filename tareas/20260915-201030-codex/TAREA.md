# Contrastar la referencia 0.7 con Codex cuando vuelva su cuota

- ESTADO: CERRADA
- PRIORIDAD: 30
- ETIQUETAS: oracle, diferencial, idea

La referencia del diferencial la escribió Codex (2026-08-24) y la re-derivó agy aislado contra 0.7
(2026-09-15), porque Codex estaba sin cuota hasta el 2026-09-19. Hoy tiene dos autores. En 2026-08-24
lo que encontró problemas de la especificación fue que tres implementaciones independientes se
dividieran entre sí, no una sola.

A hacer después del 19/09: Codex, aislado con la especificación vigente, las DECISION y el contrato
(sin la referencia actual), escribe su propia implementación 0.7; se compara con la de agy sobre los
mundos de `20260915-201030-diferencial` y se clasifican los desacuerdos. Si coinciden, se registra en
`PROCEDENCIA.md`; si no, cada división es una pregunta que la especificación no contesta.

### Nota (2026-09-16 15:00:23 UTC)

2026-09-16: preparado todo lo que no necesita a Codex, en estudios/0.26.0-codex/ (README, CONTRATO, lanzar.sh, contrastar.py). El contraste está probado: 248 comparaciones, 0 desacuerdos contra la propia referencia y 29 contra un candidato que ignora requiere. Falta la entrega: Codex sigue en usage limit con gpt-5.6-luna y gpt-6-astra. Para retomar: estudios/0.26.0-codex/lanzar.sh <dir fuera del repo> y después contrastar.py sobre su evaluador.py.

### Nota (2026-09-16 15:00:59 UTC)

2026-09-16: el dueño eligió esperar a Codex antes que usar agy aislado ahora: es el autor que la tarea pide y un modelo distinto de los dos que ya tocaron la referencia. Se retoma cuando vuelva la cuota (19/09).

### Nota (2026-09-16 15:29:04 UTC)

2026-09-16: el dueño decidió hacer la anti-junta ahora (álgebra 0.8) y que Codex escriba su implementación de cero contra 0.8, no 0.7. Antes de lanzar, CONTRATO.md y README.md del estudio tienen que decir 0.8, y la especificación tiene que estar cortada con la anti-junta.

### Nota (2026-09-16 20:26:16 UTC)

2026-09-16: el estudio (CONTRATO, README, lanzar.sh) apunta al álgebra 0.8, con los rincones de sin que la especificación ahora decide y la referencia no.

### Nota (2026-09-24 10:15:21 UTC)

2026-09-24, Claude: entrega de Codex (gpt-6-sol), aislado, en estudios/0.26.0-codex/entrega-2026-09-24/. Contraste directo: 285 comparaciones, 274 desacuerdos, casi todos por UN hueco de la especificación: dice que la sintaxis 0.6 sumó un nodo opcional ambito pero ninguna forma canónica muestra dónde va; Codex lo espera después de alcance y la referencia lo emite antes. Con un adaptador que sólo reordena ese nodo (adaptado.py) quedan 66 desacuerdos, por clasificar.

### Nota (2026-09-24 10:18:02 UTC)

2026-09-24: ejecuté contraste adaptado (285 comparaciones, 66 desacuerdos) y clasifiqué cada pareja origen+medida en estudios/0.26.0-codex/entrega-2026-09-24/CLASIFICACION.md. Tres causas: 14 defectos del candidato por relación requerida ausente (§2: SIN EVIDENCIA); 49 huecos por aridad de y/o; 3 huecos por min/max de booleanos. Incluido el hueco previo de posición canónica de ambito. Ningún defecto de referencia entre estos 66. Pendientes decisiones del dueño sobre los tres huecos y tratamiento del defecto del candidato.


### Nota (2026-09-24 10:23:59 UTC)

2026-09-24, Claude y Brian: los tres huecos se resuelven con lo que ya hace el núcleo, sin cambiar el lenguaje. (1) ambito va antes de alcance, como lo emite Medida.a_datos. (2) y/o aceptan dos o más operandos: el núcleo evalúa ["y", a, b, c]. (3) min/max aceptan booleanos homogéneos con false < true: el núcleo da 12, 1 y 0 en los casos 015, 024 y 116 de proceso.modulo_alcanzable, igual que el candidato; la que se aparta es la referencia, que los rechaza. Eso no es un hueco (clase 1) sino un defecto de la referencia frente al núcleo (clase 3), y la clasificación lo había puesto mal.

### Nota (2026-09-24 10:27:15 UTC)

2026-09-24, Codex: verifiqué en nucleo/medida.py y nucleo/algebra.py el orden requiere → ambito → alcance, la aridad de y/o (mínimo dos) y min/max de booleanos homogéneos (false < true). Aclaré §2–3 de ESPECIFICACION.md sin tocar versiones ni nucleo/. Test nuevo de referencia rojo antes del cambio y verde después; corregí su rechazo de booleanos. Regeneré diferencial/simulacion.json con tools/generar_diferencial.py --escribir y el emisor confirmó 10 mundos × 8 medidas con acuerdo referencia/Oracle. Contrasté adaptado.py: 285 comparaciones, 63 desacuerdos restantes: 49 por aridad y/o y 14 por requiere ausente; ambos son ahora clase 2 del candidato. Corregí CLASIFICACION.md (los 3 casos de min/max eran clase 3). Suite tests: 2430 OK. Sin commits ni cierre.

## Resultado

Tercer autor, sin ver la referencia: de 285 comparaciones, los desacuerdos se explican por tres
preguntas que la especificación no contestaba —posición de `ambito`, aridad de `y`/`o`, `min`/`max`
sobre booleanos— y un defecto de la referencia (el último). Las tres quedaron escritas en
`ESPECIFICACION.md` con lo que ya hace el núcleo, sin subir versiones, y la referencia se corrigió.
Los 63 desacuerdos que quedan son defectos del candidato (clase 2); la entrega se conserva sin
tocar como evidencia de lo que un tercer autor lee en el texto.

## Próximo paso

Ninguno.
