# El verificador complementario de batalla naval falla con el nombre de partida que usa la guía

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-02 01:07:23 UTC)

Defecto observado por agy2 al reconstruir la guía: verificar_oraculo.py buscaba partida_real.json pero la guía guarda hechos_partida.json. Evidencia: ../20261001-101706-de-cero-novato/evidencia-agy2/paso9_verificar_oraculo.log. Corregido: el script usa hechos_partida.json cuando no existe partida_real.json; README explica ambos nombres. Nuevo test reproduce la carpeta con el nombre de la guía y ejecuta los juicios reales. Los 3 tests de tests.test_ejemplo_batalla_naval pasaron. La reproducción final desde HTML también ejecutó el script con éxito sin crear partida_real.json (reproduccion-html-final.log en de-cero-novato).

## Próximo paso

Marcar CERRADA y registrar el commit de cierre: corrección y verificaciones completas, integradas con de-cero-novato.
