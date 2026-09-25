# Los enlaces de la página de PyPI apuntan a main y se rompen cuando un archivo se mueve

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, distribucion, flaqueza


## Por qué

El README es la descripción de PyPI (`pyproject.toml`, `readme = "README.md"`), y sus enlaces van a
`github.com/Segtem/oracle/blob/main/...`. Cuando en 0.30.0 se movieron las decisiones y los estudios,
la página de PyPI de 0.28.0 y de las versiones anteriores quedó con enlaces 404, y no tiene arreglo:
PyPI no deja editar una descripción publicada.

## Qué hacer

Que cada versión publicada enlace a **su** tag (`blob/v0.30.0/...`), que no se mueve:
`tools/cifras.py` reescribe los enlaces relativos y los de `blob/main` del README a la URL del tag
de `VERSION_DISTRIBUCION`. Con un test y la comprobación del wheel y el sdist en
`verificar_instalacion`.

### Nota (2026-09-24 23:51:29 UTC)

Prueba inicial roja: METADATA del wheel conservaba blob/main y faltaba el backend. Implementado backend que reescribe enlaces blob/tree/main y relativos al tag v0.30.0 en METADATA, actualiza RECORD y conserva README del repo. Verificado: 2442 unit tests OK; test --rapido VERDE; cifras --actualizar; verificar_instalacion WHEEL OK; wheel desde sdist sin enlaces a main; git diff --check OK. Sin ids de equivalentes.json en archivos con líneas movidas.

### Nota (2026-09-24 23:52:33 UTC)

2026-09-24, revisión de Claude: el backend propio (backend_pypi.py + MANIFEST.in en la raíz) reescribe sólo el wheel; el sdist sigue con enlaces a main, y la descripción de PyPI dependería del orden de subida de twine. Además suma dos archivos a la raíz recién limpiada y reescribe METADATA/RECORD después del build. Forma más chica: que tools/cifras.py, que ya regenera bloques del README en cada corte, reescriba los enlaces del README a blob|tree/v<VERSION_DISTRIBUCION>/ (los relativos y los de main). Así el README del repo, el wheel y el sdist dicen lo mismo, sin backend propio. verificar_instalacion comprueba wheel Y sdist.

### Nota (2026-09-24 23:58:22 UTC)

Rehecho según revisión: eliminados backend_pypi.py y MANIFEST.in; setuptools.build_meta restaurado. cifras.py actualiza y custodia enlaces del README y URLs de pyproject.toml para el tag v0.30.0. Test de enlaces adaptado; verificar_instalacion comprueba METADATA del wheel y PKG-INFO del sdist. Verificado: 2443 unit tests OK, test --rapido VERDE, verificar_instalacion WHEEL OK (wheel y sdist), git diff --check OK. Sin commits.

## Próximo paso

En el próximo corte de distribución, actualizar `VERSION_DISTRIBUCION` y ejecutar `python3 tools/cifras.py --actualizar` antes de construir los paquetes.

### Nota (2026-09-25 00:00:59 UTC)

2026-09-24, Claude: límite conocido — un enlace nuevo a un archivo creado después del último tag da 404 en el README de main hasta el corte siguiente, cuando cifras lo lleva al tag nuevo.
