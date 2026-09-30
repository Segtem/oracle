# cobertura con veredicto: qué requisitos se cumplen hoy, no sólo cuáles tienen medida

- ESTADO: CERRADA
- PRIORIDAD: 65
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué: oracle cobertura dice si un requisito tiene medidas, no si pasan; un requisito medido por una medida roja o en sombra sale igual de ✓. Kiro vende exactamente la pregunta «¿tu código cumple tu spec?», pero sin declarar puntos ciegos. Cruzar requisitos con el último juicio (oracle juzgar) da la respuesta con su sin_medir al lado.

### Nota (2026-09-30 17:45:05 UTC)

Hecho: oracle cobertura --con <hechos.json> juzga la evidencia (con sombras y cotas, vía juzgar_evidencia) y da por requisito: ✓ se cumple, ◐ se cumple en lo medido (con SIN MEDIR al lado), ✗ no se cumple (incluye falla en sombra), ? sin juicio (sin evidencia, no aplicada, no juzgó). Sale 1 sólo con un rojo no perdonado, una medida que no juzgó o una inexistente. Sobre la evidencia real de LyraGASP (observaciones/2026-09-07-dataset): 1 no se cumple (ml_deformer.dataset_entrenable, falta ground truth) y 9 sin juicio. Mutación cobertura.py 57/57, líneas nuevas de cli.py 15/15.
