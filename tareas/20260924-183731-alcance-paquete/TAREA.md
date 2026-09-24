# El tracker y el MCP son subsistemas grandes dentro de un paquete que se presenta como un metalenguaje

- ESTADO: ABIERTA
- PRIORIDAD: 55
- ETIQUETAS: oracle, arquitectura


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.6: `tools/` tiene 16 415 líneas y `nucleo/` 10 848. El tracker (`tareas*.py`) y el MCP (1962
líneas) crecen más rápido que el lenguaje.

## Qué hacer

Decidir si el tracker es parte del producto o un consumidor que vive en el mismo repo, antes de que
la API pública lo fije. Hay que medir qué importa el tracker del núcleo y qué importa el núcleo del
tracker, y ver qué costaría separarlo en un paquete aparte con la misma versión.

**Quién:** agy (la medición de dependencias); Brian decide.

## Próximo paso

La medición.
