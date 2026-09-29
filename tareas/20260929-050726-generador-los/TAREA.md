# generador: los sobrevivientes de la mutación en el código anterior

- ESTADO: ABIERTA
- PRIORIDAD: 55
- ETIQUETAS: oracle

### Nota (2026-09-29 05:07:26 UTC)

Medido el 2026-09-29: nucleo/generador.py nunca estuvo en la matriz de mutación del CI. En v0.35.0 la ronda completa daba 573 mutantes, 400 vivos; con los tests de caso-generar-no quedan 683 mutantes, 88 vivos, todos en código anterior a esa tarea (resolver_predicado, las ramas de _proponer_candidatos, generar_caso). Matarlos o declarar equivalentes y sumar el módulo a la matriz.
