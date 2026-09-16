# Contrastar la referencia 0.7 con Codex cuando vuelva su cuota

- ESTADO: ABIERTA
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
