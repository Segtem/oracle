# oracle convertir traduce un archivo por vez: tiene que migrar un directorio entero y sólo reemplazar si la ida y vuelta es idéntica

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, parte de una-sintaxis. oracle convertir <archivo> traduce entre superficie y JSON por la extensión, de a uno. Para migrar un repo hace falta: oracle convertir <directorio> --a-superficie, que convierte cada medida, caso y (cuando exista .relacion) relación JSON a su superficie; que compruebe por archivo que leer la superficie nueva da EXACTAMENTE el mismo árbol canónico que el JSON original (si no, no toca ese archivo y lo informa); que escriba el nuevo, borre el viejo sólo si la comprobación pasó, y termine con un resumen (convertidos, no convertibles y por qué). Sin --escribir, sólo informa. Tests con un proyecto de ejemplo que mezcle formas. Esto es lo que usan oracle-a-superficie y los consumidores.
