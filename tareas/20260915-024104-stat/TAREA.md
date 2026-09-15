# juzgar termina en traceback si falla consultar la evidencia

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle, bug

CI del corte 0.18.0 (corrida push 34921875657) falló en `contratos` 3.11 y 3.13:
`test_errores_de_lectura_de_la_evidencia_salen_dos` simula un `OSError` en `Path.stat`, y en ese
Python `ruta.exists()` llama a `stat` fuera de todo `try`, así que sale traceback. Localmente
(`exists()` no pasa por el `stat` simulado) daba verde.

No es sólo el test: `_leer_evidencia` consulta el archivo con `exists()` e `is_dir()` antes del
`try`, y un `OSError` real al consultarlo (permiso denegado en un directorio intermedio) termina en
traceback en vez de código 2. Queda publicado en v0.18.0.

### Nota (2026-09-15 10:02:46 UTC)

Cerrada con el corte 0.18.1: una sola consulta stat dentro del try, test del directorio, juzgar.py 111/111.
