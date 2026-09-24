# oracle relaciones escribe el esqueleto de las relaciones observadas

- ID: 20260916-035758-declarar
- ESTADO: CERRADA
- PRIORIDAD: 62
- ETIQUETAS: oracle, metalenguaje, herramienta
- CREADA: 2026-09-16

Sale de [`20260915-155111-exigentes`](../20260915-155111-exigentes/TAREA.md) y del estudio
[TRES-MEDIDAS-QUE-TODOS-PONEN-EN-SOMBRA.md](../../vault-kb/estudios/TRES-MEDIDAS-QUE-TODOS-PONEN-EN-SOMBRA.md).

`meta.toda_cantidad_comparada_tiene_unidad_derivable` exige que la relación comparada esté declarada
con la unidad de sus campos. Ninguno de los dos consumidores declara una sola relación —no tienen
carpeta `relaciones/`—, así que la medida no puede dar otra cosa que el total de sus comparaciones:
60 en LyraGASP y 54 en Jam al 2026-09-16, y creciendo con cada medida nueva.

`oracle relaciones` ya lista las relaciones **observadas** en la evidencia, con sus campos. Lo que no
existe es el paso de ahí a `relaciones/*.json`, que hoy se transcribe a mano, relación por relación —
que es literalmente la razón que las dos sombras dan para seguir tapadas.

A hacer: que `oracle relaciones` pueda **escribir** el esqueleto de cada relación observada que el
proyecto todavía no declara (campos con su tipo inferido de la evidencia y la unidad en
`sin_unidad`), sin pisar lo ya declarado y diciendo qué escribió. El trabajo del consumidor pasa a
ser revisar y completar unidades, no transcribir. Medir después cuánto baja la deuda en los dos.
