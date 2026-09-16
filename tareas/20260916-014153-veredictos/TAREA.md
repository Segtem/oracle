# Los fixtures de los consumidores guardan sólo el ok, no el veredicto entero

- ID: 20260916-014153-veredictos
- ESTADO: ABIERTA
- PRIORIDAD: 45
- ETIQUETAS: oracle, metalenguaje, diferencial
- CREADA: 2026-09-16

Desde 0.23.1 un veredicto guardado en un fixture puede ser el mapa `{ok, valor, levanta}`, que
distingue un rojo de un SIN EVIDENCIA y de un error (§6). El emisor del diferencial de Oracle
—`tools/generar_diferencial.py`— ya lo escribe así, pero `nucleo/dominio.generar`, que es por donde
pasan los fixtures de LyraGASP y de Jam, sigue guardando un booleano por medida.

La forma corta es válida a propósito: exigir la larga habría invalidado de golpe los 13 fixtures de
los dos consumidores. Pero mientras sigan en la corta, un cambio que lleve una de sus medidas de
roja a SIN EVIDENCIA no lo ve nadie.

A hacer: que `nucleo/dominio.generar` use `registro_de_veredicto`, medir qué fixtures de los
consumidores cambian de contenido al re-emitirse, y re-emitirlos junto con la tarea
`20260915-155111-consumidores`, que ya los va a tocar para subirlos de 0.17.0.
