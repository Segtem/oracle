# Cada corte tarda horas porque se muta el módulo entero aunque haya cambiado una línea

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, mutacion


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.7: sólo `nucleo/sintaxis.py` tarda cerca de dos horas por corte, y ya hubo cortes por memoria.

## Qué hacer

Un modo de mutación incremental, que muta sólo los sitios de las líneas cambiadas desde el último
tag, para los cortes. La corrida completa se reserva para `--todo`. Sin bajar el criterio de muerte, y
con el informe diciendo qué se mutó y qué no.

**Quién:** Codex.

## Próximo paso

Diseñar cómo se mapean las líneas cambiadas a los sitios de mutación.
