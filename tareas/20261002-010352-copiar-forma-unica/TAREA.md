# Copiar archivos desde la web pierde el salto final y rompe la forma única de Oracle

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS:

### Nota (2026-10-02 01:07:23 UTC)

Defecto observado por agy2: tools/sitio.py quitaba el salto final mediante rstrip al incluir archivos; al copiar el primer caso desde HTML, oracle test rechazaba la forma única. Evidencia: ../20261001-101706-de-cero-novato/evidencia-agy2/paso5_oracle_test_rojo.log. Corregido: se conserva read_text completo, el portapapeles usa textContent y la selección alternativa sólo selecciona code, sin el botón. Test nuevo compara todo el texto copiable de los 63 bloques de archivo de la guía con sus fuentes. 29 tests del sitio pasaron; recorrido independiente desde HTML regenerado: 14 bloques de comandos y 63 escrituras, salidas coincidentes y script complementario OK. Nueva mutación parcial del sitio y oracle test en curso.

### Nota (2026-10-02 09:47:08 UTC)

Corrección integrada en 1d04031. Verificación final: 2256 tests OK y oracle test VERDE; ronda parcial final de tools/sitio.py en líneas 137-215 y 409-411: 36/36 muertos, sin supervivientes, timeouts ni errores de arnés (salida 2 por alcance parcial, no fija el módulo completo). Reproducción del HTML: 14 bloques de comandos, 63 escrituras exactas y salidas comparadas. Evidencia en de-cero-novato/mutacion-sitio-final.log y reproduccion-html-final.log.

## Próximo paso

Sin pendiente: copiado corregido en 1d04031 y reproducción del HTML verificada.
