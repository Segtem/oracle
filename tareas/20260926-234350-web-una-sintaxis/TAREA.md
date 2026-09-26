# La web cuenta la sintaxis única: portada, guía de escribir, cómo funciona y la batalla naval

- ESTADO: CERRADA
- PRIORIDAD: 1
- ETIQUETAS: 

### Nota (2026-09-26 23:43:50 UTC)

2026-09-26, pedido de Brian: «actualicemos toda la web» después de publicar 0.32.0. Barrido de las 21 páginas: el JSON que aparece es evidencia (hechos*.json, evidencia/*.json) o configuración (oracle.json), y está bien; lo que falta es que la web CUENTE la sintaxis única. Plan: (1) portada: una sección «Una sola forma de escribir» con el diff real de oracle formatear y el error de una forma retirada; (2) 03-escribir-una-medida: la sección de superficie pasa a «Una sola forma de escribir» —forma única, formatear, la regla de comentarios, .relacion con un ejemplo, lo que dejó de leerse— y se borra la línea vieja que decía que la conversión a .relacion no estaba disponible; (3) como-funciona (guía ejecutada): en lo que comprueba oracle test, la forma única, con la salida real de un archivo fuera de forma; (4) de-cero (guía ejecutada y jugable): en la misión 5, un minijuego «¿cuál de estas tres carga?» y el paso oracle formatear, ejecutado; (5) regenerar el sitio, correr las guías como tests y jugar la guía en Chromium por CDP sin errores.

### Nota (2026-09-26 23:54:09 UTC)

2026-09-26, Claude: hecho. (1) Portada: sección «Cada regla se escribe de una sola manera» con la salida real de oracle formatear (diff) y el error de una forma retirada; además el recorte de colocacion.dentro_del_tablero partía el alcance en tres líneas —una grafía que no carga— y ahora va en una con «…». (2) 03-escribir-una-medida: «Una sola forma de escribir» —forma única, formatear, regla de comentarios, aritmética, .relacion con ejemplo, el orden—; se borró la línea vieja que decía que la conversión a .relacion no estaba disponible; la introducción nombra .relacion. (3) como-funciona: pasos ejecutados que rompen la forma única con un espacio (oracle test ROJO por sintaxis: forma única, con el diff) y la arreglan con formatear; la fila «sintaxis» de la tabla de capas dice lo que hoy comprueba. (4) de-cero, misión 5: paso ejecutado oracle formatear . --escribir y minijuego «Una sola forma de escribir» (tres grafías del donde, sólo una carga; verificadas contra el cargador real). (5) docs/README: la fila de 03. Verificado: sitio al día, las siete guías ejecutadas sin diferencias, suite 2699 OK, y la guía jugada en Chromium por CDP (23 piezas, el minijuego nuevo responde, 0 errores de JavaScript), con capturas.
