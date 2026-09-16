# oracle juzgar omite en silencio las medidas cuya relación no vino en la evidencia

- ESTADO: ABIERTA
- PRIORIDAD: 74
- ETIQUETAS: oracle, metalenguaje, juzgar


Encontrado el 2026-09-16 al recorrer la guía de la batalla naval con 0.25.2
([`20260916-160509-guia`](../20260916-160509-guia/TAREA.md)). Con un catálogo de 4 medidas y una
evidencia sin la relación `impacto`, `oracle juzgar` imprime 3 medidas y «VEREDICTO: 1 de 3 medidas
en rojo»; `--json` tampoco nombra la cuarta. Si las 3 estuvieran verdes, sale 0 con un verde que
nunca miró los hundimientos. Con `impacto: []` sí aparece como `⊘ SIN EVIDENCIA`.

«No aplica porque no vino su relación» es exactamente el «no miré» que el lenguaje persigue. A
decidir: listar las medidas del catálogo que no se aplicaron (texto y `--json`) y si una ausente
cuenta como SIN EVIDENCIA para el código de salida. Cambia lo que un consumidor ve → MENOR.
