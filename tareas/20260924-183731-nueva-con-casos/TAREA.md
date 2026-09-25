# oracle nueva crea la medida sola, sin su caso rojo ni su caso verde, y un agente se saltea los casos

- ESTADO: CERRADA
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

### Nota (2026-09-25 12:12:14 UTC)

2026-09-25, Claude: va. Complementa medida-sin-casos (una medida propia sin casos ya pone rojo oracle test): que oracle nueva cree además el caso rojo y el verde de andamio, marcados como andamio, y que oracle test no dé verde mientras lo sean. Implementa Codex.

### Nota (2026-09-25 12:29:54 UTC)

Implementado: oracle nueva crea casos rojo (falso_verde) y verde (verde_correcto) con evidencia POR_COMPLETAR y marca ANDAMIO; oracle test avisa y da ROJO mientras la marca persista; medida listar no los cuenta como fijacion. Test nuevo fallo antes de implementar. Verificacion: 2553 tests OK, oracle test --rapido VERDE, guia.py y sitio.py OK, cifras.py --actualizar aplicado. Sin commits por .git de solo lectura.

## Próximo paso

Incorporar el diff de este worktree desde un entorno con acceso de escritura a `.git`.
