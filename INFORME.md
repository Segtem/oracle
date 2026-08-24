# Informe

## Qué hice

Implementé la opción (a): las UDF externas de `escalares.py` ya no se importan en el proceso de
Oracle. `escalares_del_proyecto()` valida la ruta como antes, pero registra proxies que hablan por
JSON con un trabajador Python separado.

El trabajador vive en `nucleo/aislamiento/escalares.py`. Carga el módulo externo con entorno mínimo,
sin secretos heredados, y aplica una auditoría fail-closed: lectura sólo del proyecto, Oracle y la
biblioteca estándar; escritura sólo dentro del proyecto; red, procesos, señales externas y `ctypes`
bloqueados. El proceso se lanza en su propio grupo y se cierra al salir del contexto temporal o al
morir los proxies de un registro persistente.

Agregué una regresión hostil en `tests/test_proyecto.py`: una UDF intenta leer un centinela fuera del
proyecto, escribir fuera y lanzar un proceso. Las tres operaciones terminan en `PermissionError`, no
queda archivo externo escrito y no queda PID de proceso creado.

Actualicé la sección "Frontera de confianza" de `ESCRIBIR-UNA-MEDIDA.md` y regeneré las cifras
publicadas que vencieron por el cambio. `estudio/` se generó como artefacto ignorado para que
`tools/cifras.py` pudiera custodiar también `estudio/00-esencia.md`.

## Decisiones

Mantuve `--confiar-escalares` como consentimiento explícito, no como bypass: sin la bandera no se
ejecuta nada externo; con la bandera se ejecuta sólo en el trabajador aislado.

Conservé la semántica transaccional del registro: si el contexto falla, el registro vuelve al estado
anterior; si un `Motor` carga un registro propio correctamente, las UDF quedan disponibles mediante
proxies.

Moví el soporte nuevo a un subpaquete de `nucleo/` para no ampliar los objetivos automáticos de
mutación de código sin tocar `tools/mutar_codigo.py`, que no era un archivo asignado.

## Qué no cubrí

El aislamiento no promete ejecutar UDF que necesiten autoridad fuera del proyecto: esos datos deben
generarse antes y entrar como evidencia.

La frontera bloquea Python hostil común, procesos, red, archivos externos y `ctypes`, pero no declara
soporte para extensiones nativas arbitrarias cargadas por una UDF. El contrato operativo queda en
valores JSON finitos por el canal.

## Verificación

- `python -m unittest discover -s tests -t . -q` -> 409 tests OK.
- `python tools/cifras.py` -> CIFRAS OK.
- `python tools/corpus.py` -> CORPUS OK.
- `python tools/aceptacion.py` -> ACEPTACIÓN ✓.
- `python tools/diferencial.py` -> DIFERENCIAL ✓.
- `python tools/compromisos.py` -> en plazo.
- `python tools/trazar.py` -> 4 propiedades verdes.
- `python tools/mutar.py` -> 206/206 mutantes muertos, 0 sobrevivientes.

No hice commit.
