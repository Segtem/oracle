# generador: los sobrevivientes de la mutación en el código anterior

- ESTADO: ABIERTA
- PRIORIDAD: 55
- ETIQUETAS: oracle

### Nota (2026-09-29 05:07:26 UTC)

Medido el 2026-09-29: nucleo/generador.py nunca estuvo en la matriz de mutación del CI. En v0.35.0 la ronda completa daba 573 mutantes, 400 vivos; con los tests de caso-generar-no quedan 683 mutantes, 88 vivos, todos en código anterior a esa tarea (resolver_predicado, las ramas de _proponer_candidatos, generar_caso). Matarlos o declarar equivalentes y sumar el módulo a la matriz.

### Nota (2026-09-29 15:28:57 UTC)

Avance 2026-09-29. Con el disco sano, la ronda completa daba 380 vivos de 645 (los 91 de antes eran muertes falsas por disco lleno; ver la-mutacion). Borrado: el caso especial con la evidencia escrita a mano de simulacion.la_traza_no_tiene_huecos (wip de agy, ningún test lo usaba) y siete escalares de un consumidor escritas por nombre en resolver_predicado, con constantes mágicas y sin ningún caso generado que las usara. Código muerto sacado: parejas sobre filas que el donde ya excluye. Tests nuevos para ==/contiene con literales, _campos_de por alias y un literal primero en el sin. Ronda completa ahora: 412 mutantes, 139 vivos. Suite 2182 OK. Falta: los 139.

### Nota (2026-09-29 15:58:57 UTC)

Hecho. nucleo/generador.py: 327/327, ningún vivo, dos equivalentes declarados (el paso de _menor y el satisfacer de la rama de disyunción, que alias_override pisa); 178 s, entra a la matriz de mutación del CI. Camino: 400/573 vivos en v0.35.0 → 380/645 (disco sano) → 139/412 (sin código de un consumidor ni evidencia escrita por nombre) → 10/340 → 0/327. Además de tests: resolver_predicado reescrito por propiedad (tabla de opuestos y espejos, _valor_que_cumple, nextafter para flotantes) con un test que prueba los seis comparadores con enteros, flotantes y extremos; guardas imposibles fuera. Defectos que salieron y quedaron arreglados: cerca con == o != fabricaba un valor que no cumplía; un join entre relaciones distintas no generaba nada (el sufijo tocaba un id que el donde había fijado); un sin dentro de un join dejaba al candidato sin la relación negada (ahora toda relación que la medida lee va declarada, aunque sea vacía). Límite real, dicho en vez de inventado: el verde de un auto-join. Experimento OpenSpec con el corpus borrado: 29 de 32 medidas con casos generados, 16 con todos sus mutantes muertos. oracle test VERDE, 2200 tests.
