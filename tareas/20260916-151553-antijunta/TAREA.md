# El álgebra no puede decir que ninguna fila de otra relación corresponde a esta

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, metalenguaje, algebra

Medido el 2026-09-16 al cerrar `20260915-010452-commits`: la regla «toda tarea cerrada tiene su
commit de cierre» no se pudo escribir uniendo `tarea_seguimiento` con `commit_seguimiento`. El álgebra
tiene `unir` (producto) y `donde`, pero no puede decir que **ninguna** fila de otra relación
corresponde a esta: le falta la anti-junta. Hubo que hacer que el tracker contara
(`commits_de_cierre`) y que la medida comparara contra cero.

No es un caso aislado. Al 2026-09-16, cinco medidas dependen de un conteo que calcula un sensor en
Python sólo por esto:

| campo contado por el sensor | medida |
|---|---|
| `commits_de_cierre` | `seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` |
| `mutantes` | `meta.toda_medida_esta_fijada` |
| `casos_que_la_evaluan` | `meta.toda_medida_esta_ejercitada` |
| `detecciones_conductuales`, `rechazos_del_algebra` | `proceso.test_con_mutante_que_lo_mata` |

Cada uno es lógica fuera del lenguaje: no la ve el diferencial, no la mide la mutación de medidas y
el catálogo no puede decir qué cuenta.

A decidir con el dueño: la forma (un operador de tubería `sin <relación> <alias> donde <cond>`, que
deja las filas de la izquierda para las que ninguna de la derecha cumple la condición, parece lo que
encaja con `unir` y `donde`), y el momento —es álgebra 0.8, y cambia contra qué versión escribe Codex
su implementación independiente (`20260915-201030-codex`)—.
