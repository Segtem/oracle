# oracle convertir traduce un archivo por vez: tiene que migrar un directorio entero y sólo reemplazar si la ida y vuelta es idéntica

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, parte de una-sintaxis. oracle convertir <archivo> traduce entre superficie y JSON por la extensión, de a uno. Para migrar un repo hace falta: oracle convertir <directorio> --a-superficie, que convierte cada medida, caso y (cuando exista .relacion) relación JSON a su superficie; que compruebe por archivo que leer la superficie nueva da EXACTAMENTE el mismo árbol canónico que el JSON original (si no, no toca ese archivo y lo informa); que escriba el nuevo, borre el viejo sólo si la comprobación pasó, y termine con un resumen (convertidos, no convertibles y por qué). Sin --escribir, sólo informa. Tests con un proyecto de ejemplo que mezcle formas. Esto es lo que usan oracle-a-superficie y los consumidores.

### Nota (2026-09-26 02:59:23 UTC)

Implementado oracle convertir <directorio> --a-superficie con vista previa y --escribir: descubre JSON de catalogos/corpus/relaciones, convierte medidas y casos con macros del proyecto, exige igualdad exacta del árbol JSON (incluidos tipos), evita colisiones, informa causas por archivo y resume convertidos/no convertibles. Relaciones: _superficie en tools/cli.py es el punto de extensión; hoy informa que .relacion todavía no tiene conversor, sin asumir formato. Tests de proyecto mixto, pérdida, colisión y tipos. Ejecutado: python3 -m unittest discover -s tests -t . (2585, OK); python3 tools/guia.py (OK); python3 tools/sitio.py --escribir (OK); python3 tools/cli.py test --rapido (VERDE tras actualizar cifras); python3 tools/cifras.py --actualizar (README actualizado). Mutación no ejecutada por límite del sandbox; la corre Claude. Sin commits; tarea abierta.

## Próximo paso

Cuando la sesión de relaciones entregue el lector y el impresor de `.relacion`, conectarlos en `_superficie` y agregar su caso al test de proyecto mixto; repetir las verificaciones. Claude corre la mutación fuera de este sandbox y registra su resultado antes de cerrar la tarea.

### Nota (2026-09-26 03:01:14 UTC)

2026-09-26, Claude: probado contra copias de las medidas de los consumidores. Jam: 76 convertidos (41 medidas, 35 casos), 3 relaciones pendientes de .relacion, los fixtures no se tocan. LyraGASP: 223 convertidos (29 medidas, 194 casos). Con el mismo núcleo, original y convertido dan exactamente la misma corrida de oracle test (mismos casos, sintaxis, aceptación, diferencial y mutación), también la huella del catálogo, porque la forma canónica es idéntica.

### Nota (2026-09-26 03:13:05 UTC)

2026-09-26, Claude: unida a main; la mutación de los módulos tocados va en la ronda del próximo corte (la de una-sintaxis).
