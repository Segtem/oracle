# oracle juzgar duplica la lógica de sombra que Informe tiene desde 0.20.0

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: oracle, simplificacion

`tools/juzgar.py` (paso 8) calcula a mano `rojos_fuera_de_sombra`, `en_sombra` por medida en
`--json`, la marca `[EN SOMBRA]` y el renglón de veredicto. Desde 0.20.0 `Informe(en_sombra=…)` hace
`ok`, la marca, el conteo y `a_json` con `en_sombra`. Dos implementaciones de la misma regla
envejecen distinto.

A hacer: que `juzgar` construya el `Informe` con las sombras del proyecto y conserve sólo lo propio
(`desde` y `porque` en la marca, «verde por sombra» cuando todas las aplicables están en sombra), sin
cambiar su contrato de salida; los tests de `test_juzgar*` lo fijan.
