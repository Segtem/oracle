# oracle test se cae con un traceback cuando una medida da error en un caso del corpus

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, mutacion, guia


Encontrado el 2026-09-16 al recorrer la guía de la batalla naval con 0.25.2
([`20260916-160509-guia`](../20260916-160509-guia/TAREA.md)): la guía pide cambiar `b.y_fin` por
`b.y_final` para ver `meta.toda_medida_lee_campos_que_existen` en rojo. La aceptación lo informa
bien, pero después `oracle test` termina con un traceback de `ErrorDeAlgebra` salido de
`nucleo/mutacion.correr`: evalúa la medida original contra cada caso sin proteger la llamada.

Arreglo: si la medida original no puede evaluar un caso, ese caso no fija nada y se saltea (la
aceptación ya lo informa). Un test en `tests/test_mutacion.py` lo fija.
