# el respaldo real se informa por medida: qué medidas no fija ningún defecto observado

- ESTADO: ABIERTA
- PRIORIDAD: 83
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: la propuesta 2 del estado del arte (ISSTA 2026) pedía «qué defectos reales atrapa cada medida». 0.37.0 sólo trajo la cifra global («respaldo real: N de M muertos»). El cálculo por medida existe en tareas/20260930-153404-las-medidas-se/procedencia.py (medidas_fijadas_solo_con_inventada: Oracle 0/59, LyraGASP 18/29, Jam 42/42) pero no está en la herramienta. Qué: que la mutación de medidas nombre las medidas cuyos muertos no mata ningún caso observado. Ojo: ya existe la medida meta.la_medida_no_se_fija_solo_con_evidencia_fabricada (en sombra con cota en los consumidores); ver si esto la duplica antes de escribir nada.
