# oracle nueva crea la medida sola, sin su caso rojo ni su caso verde, y un agente se saltea los casos

- ESTADO: ABIERTA
- PRIORIDAD: 82
- ETIQUETAS: oracle, cli, ergonomia


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.3: un agente se saltea el caso cuando la medida y los casos son pasos separados. Es lo que pasó
en la batalla naval: medidas sin casos y un verde que no medía nada.

## Qué hacer

`oracle nueva <dominio.nombre>` crea también un caso rojo y uno verde de andamio, con la evidencia
por completar y marcada como tal, y `oracle test` avisa, sin dar verde, mientras sigan siendo
andamio. Tests que fallen hoy.

**Quién:** Codex.

## Próximo paso

Implementar.
