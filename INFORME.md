# Informe

## Qué cambié

- `README.md`: agregué una sección de instalación arriba del documento con `uv tool install .` como
  camino principal, `uvx --from . oracle --help` para probar sin instalar y `python -m pip install
  -e .` como alternativa. Reemplacé ejemplos que empujaban `python <oracle>/tools/...` por el comando
  instalado `oracle`. Actualicé la cifra publicada de la suite de 597 a 598 tests con
  `tools/cifras.py --actualizar`.
- `ESCRIBIR-UNA-MEDIDA.md`: agregué la misma instalación antes del primer flujo de autoría y pasé el
  recorrido práctico a `oracle caso`, `oracle relaciones`, `oracle escalares`, `oracle nueva`,
  `oracle revisar`, `oracle expandir` y `oracle test`.
- `pyproject.toml`: agregué `oracle_metalenguaje.nucleo.aislamiento` y su `package-dir`. El wheel no
  estaba incluyendo ese subpaquete; se notaba al instalar sin `PYTHONPATH` del checkout.
- `tools/cli.py`: `oracle test` ahora carga el catálogo dentro de `escalares_del_proyecto(...)` cuando
  se pasó `--confiar-escalares`. Sin esto, un consumidor con UDF en `medidas/escalares.py` podía
  fallar como `CATÁLOGO INVÁLIDO` antes de llegar a aceptación/diferencial/mutación.
- `tests/test_cli.py`: agregué una regresión que construye el wheel desde una copia temporal, revisa
  que estén empaquetados `tools/cli.py`, macros `.oracle`, catálogo base, perfil `python` y
  `nucleo/aislamiento`, instala el wheel en un venv limpio, corre `oracle init`, `oracle test` vacío
  y después `oracle test --rapido` con una medida que usa la macro estándar `ninguno`. También fijé
  que `oracle test --confiar-escalares` cargue una medida con UDF antes de fallar por falta de casos.
- `tools/verificar_instalacion.py`: lo endurecí para limpiar `PYTHONPATH` y `ORACLE_PROYECTO`,
  construir el wheel sin depender de red, validar datos empaquetados, instalar en venv limpio,
  ejecutar los 8 entry points, correr `oracle init`/`oracle test` desde un cwd vacío y probar una
  medida con macro estándar. También dejé errores con stdout/stderr del subproceso.
- `INFORME.md`: este informe.

## Instalación y empaquetado

La prueba completa de wheel + instalación limpia + `oracle test` sobre proyecto recién inicializado
dio:

```text
WARNING: The directory '/home/workstation/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
Processing ./.
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Building wheels for collected packages: oracle-metalenguaje
  Building wheel for oracle-metalenguaje (pyproject.toml): started
  Building wheel for oracle-metalenguaje (pyproject.toml): finished with status 'done'
  Created wheel for oracle-metalenguaje: filename=oracle_metalenguaje-0.1.0-py3-none-any.whl size=204573 sha256=6c9bcdc1a3b236ba9508bc3ad3c56436dded09cc1f034065cde0c34e9e9532f9
  Stored in directory: /tmp/pip-ephem-wheel-cache-5i6ys4bs/wheels/b6/d4/15/2e95767d1963811f036c605db67e33a88842ea49307e59d7f0
Successfully built oracle-metalenguaje
Resolved 1 package in 0.76ms
Prepared 1 package in 6ms
Installed 1 package in 0.87ms
 + oracle-metalenguaje==0.1.0 (from file:///tmp/oracle-uv-final-2/dist/oracle_metalenguaje-0.1.0-py3-none-any.whl)
Installed 8 executables: oracle, oracle-aceptacion, oracle-corpus, oracle-diferencial, oracle-estudio, oracle-medida, oracle-mutar, oracle-mutar-codigo
/tmp/oracle-uv-final-2/bin/oracle
Proyecto Oracle inicializado en /tmp/oracle-uv-final-2/proyecto:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
CORPUS OK · 0 casos · esquema y evidencia L0 en regla
SINTAXIS: salteado (sin medidas ni casos todavía)
ACEPTACIÓN: salteado (sin medidas ni casos todavía)
DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)
MUTACIÓN: salteada (sin medidas todavía)

VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)
WHEEL OK · namespace, datos, 8 entry points, oracle test y dos motores aislados fuera del checkout
```

`uvx` sin instalación persistente funciona desde el wheel local:

```text
Installed 1 package in 0.90ms
Oracle — metalenguaje para medir evidencia, alcance y mutación.

Uso:
  oracle init [ruta]                      Inicializa un proyecto nuevo
  oracle nueva <dominio.nombre>          Crea una medida con plantilla lista para editar
  oracle caso <grupo/id>                 Crea un caso de prueba en el corpus
  oracle revisar <archivo>               Revisa y evalúa una medida suelta
  oracle test [--rapido]                 Ejecuta la secuencia completa de verificación
  oracle relaciones                      Muestra las relaciones y campos observados
  oracle escalares                       Muestra las funciones escalares y operadores
  oracle expandir <archivo>              Muestra la forma canónica de una macro
  oracle --help                          Muestra esta ayuda

Banderas comunes:
  --proyecto <ruta>      Ruta al proyecto (por defecto: directorio actual o $ORACLE_PROYECTO)
  --confiar-escalares    Autoriza la ejecución de funciones en `escalares.py`
  --rapido               En `oracle test`, saltea la mutación de medidas
```

El comando literal `uv tool install .` y `uvx --from . oracle --help` no se pudieron completar con
cache frío en esta sesión porque `uv` quiso resolver `setuptools>=68` en build isolation y no hay DNS.
No es una falla del paquete instalado: el wheel local corrió, y el source install corrió sólo con
`--no-build-isolation` más `PYTHONPATH` apuntando al `setuptools` local. Salida de
`uvx --from . oracle --help`:

```text
   Building oracle-metalenguaje @ file:///tmp/claude-1000/-home-workstation-Dev-oracle/a8cb83db-d0a6-4ce5-8455-a73c15ecb341/scratchpad/wt-uv
  × Failed to build `oracle-metalenguaje @
  │ file:///tmp/claude-1000/-home-workstation-Dev-oracle/a8cb83db-d0a6-4ce5-8455-a73c15ecb341/scratchpad/wt-uv`
  ├─▶ Failed to resolve requirements from `build-system.requires`
  ├─▶ No solution found when resolving: `setuptools>=68`
  ├─▶ Request failed after 3 retries in 6.7s
  ├─▶ Failed to fetch: `https://pypi.org/simple/setuptools/`
  ├─▶ error sending request for url (https://pypi.org/simple/setuptools/)
  ├─▶ client error (Connect)
  ├─▶ dns error
  ╰─▶ failed to lookup address information: Temporary failure in name
      resolution
rc=1
```

Salida de `uv tool install --no-build-isolation .` con `PYTHONPATH` al `setuptools` local:

```text
Resolved 1 package in 0.63ms
   Building oracle-metalenguaje @ file:///tmp/claude-1000/-home-workstation-Dev-oracle/a8cb83db-d0a6-4ce5-8455-a73c15ecb341/scratchpad/wt-uv
      Built oracle-metalenguaje @ file:///tmp/claude-1000/-home-workstation-Dev-oracle/a8cb83db-d0a6-4ce5-8455-a73c15ecb341/scratchpad/wt-uv
Prepared 1 package in 231ms
Installed 1 package in 0.93ms
 + oracle-metalenguaje==0.1.0 (from file:///tmp/claude-1000/-home-workstation-Dev-oracle/a8cb83db-d0a6-4ce5-8455-a73c15ecb341/scratchpad/wt-uv)
Installed 8 executables: oracle, oracle-aceptacion, oracle-corpus, oracle-diferencial, oracle-estudio, oracle-medida, oracle-mutar, oracle-mutar-codigo
/tmp/oracle-uv-source-pypath-2/bin/oracle
Proyecto Oracle inicializado en /tmp/oracle-uv-source-pypath-2/proyecto:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
CORPUS OK · 0 casos · esquema y evidencia L0 en regla
SINTAXIS: salteado (sin medidas ni casos todavía)
ACEPTACIÓN: salteado (sin medidas ni casos todavía)
DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)
MUTACIÓN: salteada (sin medidas todavía)

VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)
```

No agregué `uv.lock`. El proyecto no tiene dependencias de runtime (`dependencies = []`) y la
instalación de la herramienta no gana reproducibilidad con un lock que sólo congelaría ausencia de
dependencias. El problema observado con `uv` no lo arregla un lock de runtime: es la resolución del
backend de build aislado (`setuptools>=68`), que ya está declarado en `[build-system]` y queda cubierto
por la prueba de wheel.

## Consumidores

No escribí en `~/Dev/jam` ni en `~/Dev/games/unreal/LyraGASP`. Antes y después de correr, los cambios
que muestra `git status` eran trabajo preexistente del usuario.

### Jam

Cadena larga de sólo lectura:

```text
$ python vendor/oracle/tools/corpus.py --proyecto medidas
CORPUS OK · 23 casos · esquema, evidencia L0 y trazabilidad en regla
rc=0

$ python vendor/oracle/tools/aceptacion.py --proyecto medidas --confiar-escalares
ACEPTACIÓN ✓ — 20 defectos en rojo, 3 verdes correctos, 0 huecos declarados sin tapar
rc=0

$ python vendor/oracle/tools/diferencial.py --proyecto medidas --confiar-escalares
DIFERENCIAL ✗ — 1 desacuerdo(s)
  · vault.json: fixture vencido: cambió referencia (fd9fca096aa8… → 9a79cad14237…)
rc=1

$ python vendor/oracle/tools/mutar.py --proyecto medidas --confiar-escalares
MUTACIÓN NO CONFIABLE — fixtures diferenciales inválidos o vencidos:
  · vault.json: fixture vencido: cambió referencia (fd9fca096aa8… → 9a79cad14237…)
rc=1
```

`oracle test` instalado:

```text
VEREDICTO: ROJO (falló: diferencial, mutación)
rc=1
```

El veredicto coincide: rojo por `medidas/diferencial/vault.json` vencido. `oracle test` no regenera
fixtures diferenciales; si cambia el catálogo o la referencia de Jam, hay que correr primero su
emisor propio.

Reemplazo propuesto en `AGENTS.md`:

```diff
-python vendor/oracle/tools/diferencial.py --proyecto medidas --confiar-escalares
-python vendor/oracle/tools/mutar.py       --proyecto medidas --confiar-escalares
+oracle test --proyecto medidas --confiar-escalares
 python vendor/oracle/tools/estudio.py     --proyecto medidas --confiar-escalares
```

`estudio.py` no está cubierto por `oracle test` y escribe salida, así que no lo corrí. Si la intención
también es eliminar la ruta vendorizada para estudio, la línea equivalente es:

```diff
-python vendor/oracle/tools/estudio.py     --proyecto medidas --confiar-escalares
+oracle-estudio --proyecto medidas --confiar-escalares
```

Reemplazo propuesto en la tabla de `RELEVO.md`:

```diff
-| oracle sobre Jam | `python vendor/oracle/tools/diferencial.py --proyecto medidas --confiar-escalares` | ... |
-| » mutación de medidas | `python vendor/oracle/tools/mutar.py --proyecto medidas --confiar-escalares` | ... |
+| oracle sobre Jam | `oracle test --proyecto medidas --confiar-escalares` | veredicto integrado |
```

### LyraGASP

Cadena larga de sólo lectura:

```text
$ python vendor/oracle/tools/corpus.py --proyecto medidas
CORPUS OK · 23 casos · esquema, evidencia L0 y trazabilidad en regla
rc=0

$ python vendor/oracle/tools/aceptacion.py --proyecto medidas --confiar-escalares
ACEPTACIÓN ✓ — 11 defectos en rojo, 12 verdes correctos, 0 huecos declarados sin tapar
rc=0

$ python vendor/oracle/tools/diferencial.py --proyecto medidas --confiar-escalares
DIFERENCIAL ✓ — 580 acuerdos globales con referencias independientes · 1740 veredictos individuales estables
rc=0

$ python vendor/oracle/tools/mutar.py --proyecto medidas --confiar-escalares
mutantes de medida (medida × mutador): 111 · murieron 111 · sobrevivieron 0
rc=0
```

`oracle test` instalado:

```text
VEREDICTO: VERDE (completo: todas las verificaciones en regla, 0 mutantes sobrevivientes)
rc=0
```

El veredicto coincide: verde. `oracle test` además corre sintaxis y diferencial; `docs/ORACLE.md`
todavía no listaba diferencial aunque `medidas/diferencial/` tiene fixtures.

Reemplazo propuesto en `docs/ORACLE.md`:

```diff
-python vendor/oracle/tools/corpus.py     --proyecto medidas
-python vendor/oracle/tools/aceptacion.py --proyecto medidas --confiar-escalares
-python vendor/oracle/tools/mutar.py      --proyecto medidas --confiar-escalares
+oracle test --proyecto medidas --confiar-escalares
```

Cuando cambien catálogos o referencias en LyraGASP, los emisores propios de fixtures diferenciales
tienen que correrse antes de `oracle test`; el comando integrado sólo consume fixtures existentes.

## Verificaciones

### `python -m unittest discover -s tests -t . -q`

```text
----------------------------------------------------------------------
Ran 598 tests in 12.706s

OK
```

### `python tools/cifras.py`

```text
CIFRAS OK
  cifras: 598 tests · 547/547 mutantes de medida · **2394 sitios de mutación de código** (2189 + 205 del motor Python).
  escala: **5674 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,2 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5674 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### `python tools/corpus.py`

```text
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### `python tools/aceptacion.py`

```text
catálogo: 37 medidas · corpus: 104 casos

  ROJO  049-donde-agrego-filas                 meta.donde_nunca_agrega_filas  (valor 1)
  verde 050-donde-filtra-como-debe             meta.donde_nunca_agrega_filas  (valor 0)
  ROJO  051-agrupar-invento-un-grupo           meta.agrupar_no_agranda_la_relacion  (valor 1)
  verde 052-agrupar-colapsa-como-debe          meta.agrupar_no_agranda_la_relacion  (valor 0)
  ROJO  053-unir-perdio-un-par                 meta.unir_materializa_el_producto  (valor 1)
  verde 054-unir-materializa-el-producto       meta.unir_materializa_el_producto  (valor 0)
  ROJO  055-logico-cortocircuito               meta.los_logicos_evaluan_todos_sus_operandos  (valor 2)
  verde 056-logico-evalua-todo                 meta.los_logicos_evaluan_todos_sus_operandos  (valor 0)
  ROJO  057-un-solo-cortocircuito              meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  ROJO  061-ausencia-sin-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-cubierta-o-no-aplica      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  063-ausencia-sin-terminos-no-concluye  meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  064-medida-sin-filtro-ni-grupo         meta.toda_medida_filtra_o_agrupa  (valor 1)
  verde 065-medida-filtra-o-agrupa             meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  066-filtro-sin-terminos-no-concluye    meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  067-umbral-de-igualdad                 meta.ningun_umbral_de_igualdad  (valor 1)
  verde 068-umbral-de-orden                    meta.ningun_umbral_de_igualdad  (valor 0)
  ROJO  069-filtro-no-toma-terminos-ajenos     meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  100-donde-no-compone                   meta.donde_compone  (valor 1)
  verde 101-donde-compone-bien                 meta.donde_compone  (valor 0)
  ROJO  102-unir-no-conmuta                    meta.unir_conmuta  (valor 1)
  verde 103-unir-conmuta-bien                  meta.unir_conmuta  (valor 0)
  ROJO  104-agrupar-sin-claves-difiere         meta.agrupar_sin_claves_es_el_resumen_global  (valor 1)
  verde 105-agrupar-sin-claves-coincide        meta.agrupar_sin_claves_es_el_resumen_global  (valor 0)
  ROJO  106-macro-expande-distinto             meta.una_macro_equivale_a_su_expansion  (valor 1)
  verde 107-macro-equivale                     meta.una_macro_equivale_a_su_expansion  (valor 0)
  ROJO  108-donde-compone-un-campo-por-vez     meta.donde_compone  (valor 3)
  ROJO  109-unir-conmuta-un-campo-por-vez      meta.unir_conmuta  (valor 3)
  ROJO  110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez meta.agrupar_sin_claves_es_el_resumen_global  (valor 2)
  ROJO  111-una-macro-equivale-a-su-expansion-un-campo-por-vez meta.una_macro_equivale_a_su_expansion  (valor 3)
  ROJO  120-sintaxis-no-vuelve-igual           meta.sintaxis_ida_y_vuelta  (valor 1)
  verde 121-sintaxis-vuelve-exacta             meta.sintaxis_ida_y_vuelta  (valor 0)
  ROJO  122-sintaxis-revienta-al-leer          meta.sintaxis_ida_y_vuelta  (valor 1)
  ROJO  123-sintaxis-un-campo-por-vez          meta.sintaxis_ida_y_vuelta  (valor 3)
  ROJO  124-sintaxis-cubre-algebra-no-vuelve-igual meta.sintaxis_cubre_algebra  (valor 1)
  verde 125-sintaxis-cubre-algebra-vuelve-exacta meta.sintaxis_cubre_algebra  (valor 0)
  ROJO  126-sintaxis-cubre-algebra-un-campo-por-vez meta.sintaxis_cubre_algebra  (valor 4)
  ROJO  127-sintaxis-casos-no-vuelve-igual     meta.sintaxis_casos_ida_y_vuelta  (valor 1)
  verde 128-sintaxis-casos-vuelve-exacta       meta.sintaxis_casos_ida_y_vuelta  (valor 0)
  ROJO  129-sintaxis-casos-generados-no-vuelve-igual meta.sintaxis_casos_cubre_casos  (valor 1)
  verde 130-sintaxis-casos-generados-vuelve-exacta meta.sintaxis_casos_cubre_casos  (valor 0)
  ROJO  131-sintaxis-casos-un-campo-por-vez    meta.sintaxis_casos_ida_y_vuelta  (valor 4)
  ROJO  132-sintaxis-casos-generados-un-campo-por-vez meta.sintaxis_casos_cubre_casos  (valor 4)
  ROJO  400-umbral-flotante-de-igualdad        meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  ROJO  401-umbral-flotante-de-desigualdad     meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  verde 402-umbral-flotante-de-orden-y-entero  meta.ningun_umbral_flotante_de_igualdad  (valor 0)
  ROJO  403-umbral-sin-defensa                 meta.ningun_umbral_sin_defensa  (valor 1)
  verde 404-umbral-con-defensa                 meta.ningun_umbral_sin_defensa  (valor 0)
  ROJO  405-medida-sin-alcance                 meta.ninguna_medida_sin_alcance  (valor 1)
  verde 406-medida-con-alcance                 meta.ninguna_medida_sin_alcance  (valor 0)
  ROJO  001-verde-acumulativo                  proceso.afirmacion_declara_alcance  (valor 3)
  ROJO  002-mutante-firma-por-id               proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  003-mutante-fondo-nunca-ejercitado     proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  005-mutante-yaw-sin-franja             proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  006-arnes-bytecode-viejo               proceso.arnes_con_bytecode_frio  (valor 1)
  ROJO  007-relevo-verde-arbol-sucio           proceso.verificacion_vigente  (valor 2)
  ROJO  008-vault-falso-rojo                   proceso.verificador_sin_falsos_rojos  (valor 2)
  ROJO  009-modulo-sin-consumidor              proceso.modulo_con_consumidor  (valor 3)
  ROJO  010-sed-desindenta                     proceso.sintaxis_valida_tras_edicion_masiva  (valor 1)
  ROJO  013-comparadores-del-algebra-sin-ejercitar proceso.test_con_mutante_que_lo_mata  (valor 6)
  ROJO  014-mutador-dejo-un-archivo-mutado-al-ser-matado proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  015-racimo-inalcanzable                proceso.modulo_alcanzable  (valor 12)
  ROJO  016-timeout-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  017-error-de-arnes-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  018-mutante-de-cache-borro-la-copia-del-proyecto proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  019-ronda-sin-mutantes-declarada-verde proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  020-una-afirmacion-sin-alcance-alcanza proceso.afirmacion_declara_alcance  (valor 1)
  ROJO  021-un-cambio-vivo-invalida-la-verificacion proceso.verificacion_vigente  (valor 1)
  ROJO  022-un-falso-rojo-ya-rompe-el-verificador proceso.verificador_sin_falsos_rojos  (valor 1)
  ROJO  023-un-import-ajeno-no-es-consumidor   proceso.modulo_con_consumidor  (valor 1)
  ROJO  024-una-variante-no-vacia-inalcanzable proceso.modulo_alcanzable  (valor 1)
  ROJO  025-mutante-de-codigo-sobreviviente    proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  027-ronda-de-codigo-sin-mutantes-no-concluye proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  ROJO  043-ausencia-total-sale-verde          proceso.modulo_con_consumidor  (valor 0)
  ROJO  044-sin-grafo-de-alcance-sale-verde    proceso.modulo_alcanzable  (valor 0)
  verde 058-rechazo-del-algebra-no-es-deteccion proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 059-clave-declarada-en-un-caso         proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 101-mutantes-todos-muertos             proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 102-verificacion-vigente               proceso.verificacion_vigente  (valor 0)
  verde 103-vault-sin-falsos-rojos             proceso.verificador_sin_falsos_rojos  (valor 0)
  verde 104-afirmacion-con-alcance             proceso.afirmacion_declara_alcance  (valor 0)
  verde 105-arnes-con-cache-frio               proceso.arnes_con_bytecode_frio  (valor 0)
  verde 106-modulos-con-consumidor             proceso.modulo_con_consumidor  (valor 0)
  verde 107-reruteo-sin-romper-sintaxis        proceso.sintaxis_valida_tras_edicion_masiva  (valor 0)
  verde 108-ronda-mutacion-concluyente         proceso.ronda_mutacion_concluyente  (valor 0)
  verde 109-mutantes-de-codigo-todos-muertos   proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  verde 110-mutante-de-codigo-equivalente-declarado-verde proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  verde 116-todo-el-nucleo-es-alcanzable       proceso.modulo_alcanzable  (valor 0)
  ROJO  200-corrida-sin-ninguna-corrida        simulacion.corrida_reproducible  (valor 0)
  ROJO  201-presupuesto-sin-ninguna-corrida    simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  202-traza-sin-ningun-evento            simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  301-simulador-que-ignora-la-semilla    simulacion.corrida_reproducible  (valor 2)
  verde 302-corridas-reproducibles             simulacion.corrida_reproducible  (valor 0)
  ROJO  303-el-presupuesto-no-alcanzo          simulacion.no_se_agoto_el_presupuesto  (valor 3)
  verde 304-el-presupuesto-alcanzo             simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  305-traza-con-hueco                    simulacion.la_traza_no_tiene_huecos  (valor 2)
  verde 306-traza-completa                     simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  307-una-corrida-no-reproducible-alcanza simulacion.corrida_reproducible  (valor 1)
  ROJO  308-una-corrida-agota-el-presupuesto   simulacion.no_se_agoto_el_presupuesto  (valor 1)
  ROJO  309-una-traza-con-un-hueco             simulacion.la_traza_no_tiene_huecos  (valor 1)

defectos que se pusieron rojos: 67 · verdes correctos: 34 · huecos declarados: 0
  resuelto       004-testigos-duplicados
  resuelto       012-umbral-duplicado-en-filtro-y-umbral
  limite_humano  011-conclusion-errada-desvan

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ningun_umbral_sin_defensa                      0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)

ACEPTACIÓN ✓ — 67 defectos en rojo, 34 verdes correctos, 0 huecos declarados sin tapar
```

### `python tools/diferencial.py`

```text
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### `python tools/trazar.py`

```text
evaluaciones trazadas: 92
hechos: 182 pasos · 339 nodos lógicos · 11 productos

el álgebra, juzgada por medidas escritas en el álgebra:
  ✓ meta.agrupar_no_agranda_la_relacion                 0 (<= 0)
  ✓ meta.donde_nunca_agrega_filas                       0 (<= 0)
  ✓ meta.los_logicos_evaluan_todos_sus_operandos        0 (<= 0)
  ✓ meta.unir_materializa_el_producto                   0 (<= 0)

contrastado con la implementación independiente: 4 propiedades, 0 desacuerdos

  · meta.agrupar_no_agranda_la_relacion: compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción
  · meta.donde_nunca_agrega_filas: compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción
  · meta.los_logicos_evaluan_todos_sus_operandos: cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción
  · meta.unir_materializa_el_producto: compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción
```

### `python tools/metamorficas.py`

```text
equivalencias comprobadas: 331
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_casos_cubre_casos                     5 (5 construidas, 0 del catálogo)
  sintaxis_casos_ida_y_vuelta                  104 (0 construidas, 104 del catálogo)
  sintaxis_cubre_algebra                        94 (94 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         37 (0 construidas, 37 del catálogo)
  una_macro_equivale_a_su_expansion             69 (0 construidas, 69 del catálogo)
  unir_conmuta                                  16 (1 construidas, 15 del catálogo)

juzgado por las medidas aplicables:
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_casos_cubre_casos                     0 (<= 0)
  ✓ meta.sintaxis_casos_ida_y_vuelta                    0 (<= 0)
  ✓ meta.sintaxis_cubre_algebra                         0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

### `python tools/sintaxis.py --verificar`

```text
medidas convertidas: 37
macros convertidas: 3
casos convertidos: 104
ida JSON: OK
vuelta texto: OK
caracteres: JSON 142369 · superficie 139406
puntuación: JSON 25487 (17,9%) · superficie 10489 (7,5%)
bloques de documentación: 21 verificados · 8 declarados como gramática o fragmento
```

### `python tools/mutar.py`

```text
mutantes de medida (medida × mutador): 547 · murieron 547 · sobrevivieron 0
  de los muertos: 422 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 125 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1924

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.codigo_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'estado'], 'pasaron'] en `2.2.1.1`
```

## Qué no hice

- No toqué `nucleo/`, `corpus/`, `catalogos/` ni `vendor/`.
- No agregué dependencias.
- No agregué `uv.lock`, por el argumento escrito arriba.
- No escribí en Jam ni en LyraGASP. Sólo corrí comandos de lectura y con `PYTHONDONTWRITEBYTECODE=1`.
- No corrí `python vendor/oracle/tools/estudio.py` en Jam porque genera salida y la tarea prohibía
  escribir en consumidores.
- No regeneré fixtures diferenciales de Jam: `vault.json` está vencido y eso pertenece al consumidor.

## Lo que apareció de más

- El paquete tenía otro agujero además de las macros: faltaba `oracle_metalenguaje.nucleo.aislamiento`
  en `pyproject.toml`. El verificador anterior no lo detectaba si el checkout estaba en `PYTHONPATH`.
- `oracle test` no registraba `escalares.py` antes de cargar el catálogo. Jam lo expuso con
  `colocacion.bounds` y la escalar `volumen`.
- `uv tool install .` no es completamente “sin resolver” en un cache frío: aunque Oracle no tenga
  dependencias de runtime, el build aislado necesita resolver `setuptools>=68`. Con red cerrada eso
  falla antes de entrar al paquete.
