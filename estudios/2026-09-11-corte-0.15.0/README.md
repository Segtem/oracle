# Verificación del corte 0.15.0 — 2026-09-11

El dueño autorizó versión, commit, push, tag y release. PyPI queda a su cargo.
La implementación parte de `22cc9ba`; este corte cambia la versión de distribución, sus tres
expectativas literales en los tests de MCP y la documentación. Álgebra sigue en 0.6 y sintaxis en 0.4.

La primera suite falló porque tres tests de MCP todavía esperaban 0.14.0. El registro se conserva
en `intento-version-anterior-en-tests/`. Se actualizaron los tres valores sin cambiar las
comparaciones y se repitió la secuencia completa del relevo, desde el primer paso.

`resultados.json` conserva comandos, códigos y duraciones de la secuencia final. Sus once pasos
salieron 0: 1536 tests, corpus 203, aceptación 115 defectos y 81 verdes correctos sin huecos,
959/959 mutantes de medidas, cifras, manual, rueda, sondas, traza y aceptación de Jam 28/3.
El manual se regeneró sin cambios. Jam se verificó con el código de este árbol; no se editó su
repositorio. LyraGASP no se tocó.

Las rondas completas de mutación de código del cambio de implementación están conservadas en
los estudios del 2026-09-10: metamórficas 242/242, CLI 509/509 y álgebra 390/390, sin
sobrevivientes, timeouts ni errores de arnés. El cambio de versión no altera esos tramos.

Se construyeron el paquete fuente y el wheel con:

```bash
uv build --no-build-isolation --offline --no-cache --python /usr/bin/python3 --out-dir dist
```

La construcción del wheel desde el paquete fuente terminó correctamente. Se comprobaron nombre
y versión en ambos metadatos y el contenido de `nucleo/version.py` dentro del wheel.
`artefactos.json` conserva sus tamaños y SHA-256. Esta verificación es local; el resultado de
GitHub Actions se consulta después del push y no se presume a partir de estas salidas.
