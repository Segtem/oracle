# medida nueva desde un escenario WHEN/THEN

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle

### Nota (2026-09-29 00:08:47 UTC)

Hecho. oracle medida nueva <id> --escenario "WHEN … THEN …" | --escenario-de <spec.md> "<nombre>" [--requisito <id>]. tools/escenario.py lee GIVEN/WHEN/THEN/AND y DADO/CUANDO/ENTONCES/Y (en mayúsculas y separadas por espacio, para no confundir WHEN/THEN/AND dentro de una frase), en viñetas de OpenSpec o en una línea, y saca un escenario por nombre de un spec.md salteando bloques de código. La medida nace con el escenario como comentarios # (no cuentan para la forma única); los casos rojo y verde traen título y síntoma derivados; --requisito suma la medida al medido_por. Todo se valida antes de escribir el primer archivo. Mutación: escenario 20/20, medida 332/332, cli 760/760 (más aceptacion 89/89, formato 9/9, mutar 51/51 de las tareas anteriores). oracle test VERDE, 2168 tests. No genera la tubería: el escenario dice qué ofende en prosa y la relación la conoce quien escribe el sensor.
