# Copiar archivos desde la web pierde el salto final y rompe la forma única de Oracle

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-02 01:07:23 UTC)

Defecto observado por agy2: tools/sitio.py quitaba el salto final mediante rstrip al incluir archivos; al copiar el primer caso desde HTML, oracle test rechazaba la forma única. Evidencia: ../20261001-101706-de-cero-novato/evidencia-agy2/paso5_oracle_test_rojo.log. Corregido: se conserva read_text completo, el portapapeles usa textContent y la selección alternativa sólo selecciona code, sin el botón. Test nuevo compara todo el texto copiable de los 63 bloques de archivo de la guía con sus fuentes. 29 tests del sitio pasaron; recorrido independiente desde HTML regenerado: 14 bloques de comandos y 63 escrituras, salidas coincidentes y script complementario OK. Nueva mutación parcial del sitio y oracle test en curso.

## Próximo paso

Marcar CERRADA y registrar el commit de cierre: corrección y verificaciones completas, integradas con de-cero-novato.
