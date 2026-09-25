# NOTAS-DE-RELEASE.md tiene más de 3000 líneas en un solo archivo

- ESTADO: CERRADA
- PRIORIDAD: 40
- ETIQUETAS: oracle, documentacion


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.9.

## Qué hacer

Un índice arriba, con una línea por versión, y las versiones anteriores a 0.20 en
`docs/notas/` (o partidas por versión mayor), sin romper enlaces entrantes: el README, la web y los
releases de GitHub enlazan `NOTAS-DE-RELEASE.md`.

**Quién:** agy.

## Próximo paso

Después del corte 0.30.0, para no pisar sus notas.

### Nota (2026-09-25 12:12:14 UTC)

2026-09-25, Claude: después del corte 0.31.0, para no pisar sus notas.

### Nota (2026-09-25 21:56:27 UTC)

2026-09-25, Claude: hecho. NOTAS-DE-RELEASE.md arranca con un índice (una fila por versión: número con ancla y título) que genera cifras.py leyendo los títulos del propio archivo, así que no se escribe a mano y oracle test lo vigila como a las demás cifras. Las notas de 0.2.0 a 0.19.0 pasaron a docs/notas/anteriores-a-0.20.md (con sus 19 enlaces relativos reescritos y comprobados) y el sitio las publica como página propia. El archivo principal bajó de 3248 a ~1030 líneas. Nadie enlazaba secciones viejas por ancla (se buscó en README, docs, especificación y pyproject), y los enlaces al archivo entero siguen valiendo. Un test comprueba que cada ancla del índice existe en la página generada.
