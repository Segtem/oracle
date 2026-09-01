# DECISIÓN 008 — El repositorio se abre

**Fecha:** 2026-08-31
**Estado:** tomada

## Qué se decide

`Segtem/oracle` pasa de privado a **público**, con su historia completa —269 commits desde el
2026-07-29— y sin reescribirla.

## Por qué

El repositorio era privado a propósito y la decisión de publicar estaba **diferida**. El
`CLAUDE.md` del entorno afirmaba que esa postergación estaba «registrada con fecha en
`COMPROMISOS.json`». **Ese archivo no existe** —se buscó en `oracle` y en `jam`—. O sea que
durante meses hubo una afirmación sobre un registro, y ninguna forma de leer el registro.

Este documento existe para que eso no se repita: la decisión queda donde se la puede leer, en el
mismo formato que las siete anteriores, y no en la memoria de nadie.

## Qué se publica que antes no

Se auditó la historia entera antes de abrir. **No hay credenciales, claves, `.env` ni tokens en
ningún commit.** Lo que sí queda expuesto:

- **`diferencial/vault.json`** (8 MB, borrado del árbol en `dab72cb`, vivo en la historia):
  **49 títulos de documentos** del vault privado de Jam, con carpeta y fecha. Sólo metadatos, sin
  el texto de los documentos. Los títulos revelan qué features tiene Jam y cuándo se rompieron.
- **`diferencial/geometria.json`**: coordenadas de `oracle_placement` y `oracle_snap`. Números,
  sin nombres.
- **`estudios/*-jam/`**: esquemas de relaciones de Jam —campos y unidades—, en el árbol actual.
- Menciones a **LyraGASP** y **BotOO**, los dos privados.

Se decide que ese costo es aceptable. Es el modelo de datos de un plugin y una lista de títulos,
no material que dé ventaja a nadie.

## Por qué NO se reescribió la historia

Sacar `vault.json` con `git filter-repo` era posible y se descartó por su costo real: reescribir
cambia **todos los SHA**, exige force-push, y **rompe la trazabilidad de los dos subtrees** —Jam y
LyraGASP registran el SHA de upstream en su commit de squash, y ese SHA dejaría de existir—.
Pagar la rotura de los dos consumidores para ocultar 49 nombres de archivo no cierra.

## Por qué NO se creó un repositorio limpio

En este proyecto **la historia es el artefacto**. Los 269 commits documentan qué se midió, qué dio
y por qué se decidió así; los siete `DECISION-*.md` son la parte visible de eso. Un repositorio
limpio publicaría el código y tiraría la evidencia de que cada afirmación se midió —que es
justamente lo que Oracle sostiene que hay que conservar—.

## Consecuencias

- Cualquiera puede leer, clonar y auditar el proyecto, incluidas las rondas de mutación que dieron
  rojo y las decisiones que se revirtieron.
- El estado sigue siendo **`EXPERIMENTAL`**, y el README lo dice de frente. Abrir no es declarar
  que está terminado.
- La licencia ya era MIT y no cambia.

## PyPI: se publicó el mismo día

**Hecho el 2026-08-31**: `0.2.0` está en PyPI como **`oracle-metalenguaje`**, el mismo día que se
abrió el repositorio. `pip install oracle-metalenguaje` funciona.

Se ensayó antes en `test.pypi.org` y se instaló desde ahí en entornos limpios —wheel y sdist— para
comprobar que el paquete sirve y no sólo que la subida anda. Ahí apareció que el sdist no compila
contra TestPyPI solo, porque `pip` busca `setuptools` en ese índice y no está; con
`--extra-index-url https://pypi.org/simple/` funciona, y en PyPI real no ocurre.

Se evaluó `segtem-oracle` (también libre, igual que `segtem` y `oracle-segtem`) y se descartó:
cambiar el nombre obliga a tocar `pyproject.toml` sin ganar nada. `oracle` a secas está ocupado.

**Por qué el mismo día y no más adelante.** El plan anterior era esperar a que alguien externo lo
usara. Ese criterio tiene un costo que conviene nombrar: **en PyPI no se reserva un nombre**, se
toma subiendo una release (PEP 541 prohíbe el squatting), y tener cuenta creada no aparta nada.
Esperar deja el nombre disponible para cualquiera. Subir una release real el primer día lo toma
por uso, que es como PyPI quiere que se tome — no es apartar un nombre con un paquete vacío, es
publicar algo instalable y funcional.

**Lo que hay que saber antes de apretar.** Una versión publicada **no se puede reemplazar**: si
`0.2.0` sale con un error, la única salida es `0.2.1`. Por eso el ensayo va en `test.pypi.org`
primero, y `tools/verificar_instalacion.py` —que construye el wheel y prueba la API en un venv y
un cwd aislados— corre antes de subir, no después.

Queda escrito acá y no en la cabeza de nadie, que es el motivo por el que este documento existe.
