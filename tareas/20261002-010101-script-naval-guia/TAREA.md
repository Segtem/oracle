# El verificador complementario de batalla naval falla con el nombre de partida que usa la guía

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS:

### Nota (2026-10-02 01:07:23 UTC)

Defecto observado por agy2 al reconstruir la guía: verificar_oraculo.py buscaba partida_real.json pero la guía guarda hechos_partida.json. Evidencia: ../20261001-101706-de-cero-novato/evidencia-agy2/paso9_verificar_oraculo.log. Corregido: el script usa hechos_partida.json cuando no existe partida_real.json; README explica ambos nombres. Nuevo test reproduce la carpeta con el nombre de la guía y ejecuta los juicios reales. Los 3 tests de tests.test_ejemplo_batalla_naval pasaron. La reproducción final desde HTML también ejecutó el script con éxito sin crear partida_real.json (reproduccion-html-final.log en de-cero-novato).

### Nota (2026-10-02 09:46:42 UTC)

Corrección integrada en 1d04031. Verificación final de Oracle: 2256 tests OK y oracle test VERDE; la nueva prueba corre en una copia temporal sin dejar caché dentro del ejemplo. Reproducción desde HTML corregido y script complementario OK. Evidencia centralizada en de-cero-novato.

## Próximo paso

Sin pendiente: corrección integrada en 1d04031 y verificada en el recorrido HTML y la suite completa.
