# Con catalogo_base: false, un caso que no se pone como declara se descarta en silencio y oracle test sale VERDE

- ESTADO: CERRADA
- PRIORIDAD: 95
- ETIQUETAS: oracle, flaqueza

### Nota (2026-09-25 21:04:00 UTC)

2026-09-25: encontrado armando la página «Cómo funciona». La aceptación delegaba el juicio de cada caso a meta.el_caso_se_pone_como_debe, que sólo existe con el catálogo base; la batalla naval de la guía y los demás ejemplos tienen catalogo_base: false. Medido: invertir la etiqueta de naval/005 dejaba oracle test en VERDE con 32 de 33 casos contados. Arreglo: el caso que no se pone como debe es una falla de la aceptación, siempre (criterio 4), y se imprime FALLA con lo esperado. Nadie pone esa meta en sombra (LyraGASP, Jam, Oracle), así que los consumidores no cambian. De paso: juzgar aceptaba sólo objetos como filas y rechazaba la cabecera ["clave", …] de ESPECIFICACION §1; y el resumen de juzgar contaba un SIN EVIDENCIA entre «las medidas en rojo».
