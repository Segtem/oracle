# Décima auditoría adversarial: una sintaxis de escritura

2026-09-26. Leí el encargo y las auditorías anteriores. Trabajé en este checkout; las sondas, el wheel y el proyecto instalado quedaron en `/tmp`. No cambié código ni hice commits. Apliqué la definición vigente de `ESPECIFICACION.md:538-550`: comparé el texto después de quitar líneas completas `#`, y traté el orden de relaciones, columnas y claves (salvo `origen`) como parte del árbol.

## Hallazgo: una nota de release todavía enseña la resta sin espacios

`NOTAS-DE-RELEASE.md:155-156`, bajo el corte histórico 0.30.0, dice «también sin espacios: `t1.turno-1`». La página publicada `docs/notas.html:67` repite la instrucción. Es una crónica de una versión anterior, no el manual vigente; aun así está disponible como ejemplo de escritura sin advertir en ese punto que dejó de ser cargable en 1.0. El manual actual sí dice que `a - b` lleva espacios.

Ejecuté una medida con `donde p.turno-1 > 0` y la misma con `donde p.turno - 1 > 0`, usando `MEDIDA` de `tests.test_forma_unica_texto`, `nucleo.sintaxis.leer/imprimir` y `cargar_fuente_medida` sobre archivos `.oracle` temporales:

```text
p.turno-1   lector OK; impresor: donde p.turno - 1 > 0; mismo árbol True
            cargador MedidaMalDeclarada: fuera de la forma única
p.turno - 1 lector OK; impresor idéntico; mismo árbol True; cargador OK
```

Comandos de localización ejecutados:

```bash
rg -n -F 't1.turno-1' NOTAS-DE-RELEASE.md docs/notas docs | head -12
rg -n -F 'también sin espacios' NOTAS-DE-RELEASE.md docs/notas docs | head -12
python3 tools/cli.py manual aritmetica | head -9
```

Las búsquedas dieron `NOTAS-DE-RELEASE.md:155` y `docs/notas.html:67`. El manual respondió: «resta, con un espacio a cada lado: el impresor la escribe así y `a-b` queda fuera de la forma única». El hallazgo es editorial y está acotado a la crónica histórica; no encontré un productor vigente de archivos con esa grafía.

## Reejecución de formas abiertas en auditorías 2–9

Ejecuté `PYTHONPATH=. python3 /tmp/audit10_probe.py`. El script creó archivos temporales, llamó para cada variante al lector, al impresor, al cargador y a `lsp.diagnosticar`. Usó `MEDIDA`, `AGRUPADA`, `CASO`, `RELACION` del test de forma única y `nucleo/macros/ninguno.oracle`. La salida recortada fue:

```text
medida/base            igual                  carga OK                       LSP=0
medida/espacios        distinto               MedidaMalDeclarada forma       LSP=1
medida/version         distinto               MedidaMalDeclarada forma       LSP=1
medida/cientifica      distinto               MedidaMalDeclarada forma       LSP=1
medida/agrupar         distinto               MedidaMalDeclarada forma       LSP=1
medida/requiere        distinto               MedidaMalDeclarada forma       LSP=1
medida/ambito          distinto               MedidaMalDeclarada forma       LSP=1
medida/a-b             lector:ErrorSintaxis   MedidaMalDeclarada otro        LSP=1
medida/CRLF            distinto               MedidaMalDeclarada forma       LSP=1
medida/sinLF           distinto               MedidaMalDeclarada forma       LSP=1
medida/blanco          distinto               MedidaMalDeclarada forma       LSP=1
medida/espaciofinal    distinto               MedidaMalDeclarada forma       LSP=1
medida/comentario      igual                  carga OK                       LSP=0
medida/mayuscula       lector:ErrorSintaxis   MedidaMalDeclarada otro        LSP=1
medida/BOM             lector:ErrorSintaxis   MedidaMalDeclarada otro        LSP=1
medida/funcion         lector:ErrorSintaxis   MedidaMalDeclarada otro        LSP=1
caso/base              igual                  carga OK                       LSP=0
caso/origen            distinto               CasoMalDeclarado forma         LSP=1
relacion/comillas      distinto               RelacionMalDeclarada forma     LSP=1
macro/CRLF             distinto               MacroMalDeclarada forma        LSP=1
macro/sinLF            distinto               MacroMalDeclarada forma        LSP=1
macro/comentario       igual                  carga OK                       LSP=0
```

Corregí aparte una variante de `fila` mal construida en la matriz: sustituí la tabla canónica `paso: clave(t); t` / `0` por `paso: clave(t);` / `fila {"t": 0}`. `caso.leer` dio el mismo JSON, el impresor devolvió la tabla y `cargar_fuente_caso` rechazó la fila redundante por forma. `clave(t) t` sin `;` dio `ErrorSintaxis`. La inversión de `repo` y `commit` en `origen` dio impresor distinto y rechazo del cargador. Para un caso con dos relaciones, invertí el orden: ambos textos impresos cargaron como `001-demo`; lo mismo ocurre con cambios de orden de columnas y claves de objeto en la ida y vuelta. Los órdenes son parte del árbol según la definición vigente, así que no los cuento como segundas grafías.

Probé además `donde p.x > 0` seguido de `donde p.x < 10`, un umbral sin `porque`, y una línea completa `# nota`: el lector aceptó los tres; los dos primeros se imprimieron idénticos y cargaron, y el comentario fue quitado por `sin_comentarios` y cargó. Un comentario al final de `alcance "a" # nota` dio `ErrorSintaxis`, de acuerdo con la especificación. La forma funcional `mas(1,2)`, mayúsculas y BOM dieron `ErrorSintaxis`. Estas sondas no establecen que *todas* las combinaciones de campos sean canónicas; cubren las variantes indicadas.

## Entradas y materiales

Ejecuté las siguientes entradas sobre una medida con triple espacio en el encabezado:

```bash
python3 tools/sintaxis.py --leer /tmp/oracle-audit10-bad.oracle
python3 tools/cli.py formatear /tmp/oracle-audit10-bad.oracle
python3 tools/cli.py init /tmp/oracle-audit10-project
python3 tools/cli.py test --rapido --proyecto /tmp/oracle-audit10-project
python3 tools/cli.py juzgar --proyecto /tmp/oracle-audit10-project --con /tmp/oracle-audit10-hechos.json
```

Copié la medida mala a `catalogos/` y escribí `{}` en los hechos. Salidas recortadas: `--leer` imprimió «fuera de la forma única»; `formatear` mostró `-medida   demo.prueba:` / `+medida demo.prueba:`; `test` dio `SINTAXIS ✗` y `VEREDICTO: ROJO`; `juzgar` dio `ERROR AL EVALUAR` por forma única. En llamada directa, `mcp._medida_en_memoria({'texto': malo, 'formato': 'oracle'}, None)` dio `ErrorHerramienta MEDIDA_INVALIDA — fuera de la forma única`; el LSP dio un diagnóstico y cero lentes. No ensayé todos los comandos de `medida`, `caso`, `biblioteca`, `mutar` o `estudio` en esta ronda.

Ejecuté una sonda de los cuatro cargadores con árboles JSON guardados como `.json`: medida `list`, caso `dict`, relación `list`, macro `list`. Esto confirma el intercambio admitido; no es hallazgo. `oracle convertir /tmp/oracle-audit10-bad.oracle` respondió «esperaba una medida .json para convertir a superficie».

Ejecuté `python3 tools/cli.py contexto --compacto`, `manual aritmetica`, `tools/medida.py --expandir`, `tools/cli.py --help` y búsquedas `rg` de `.json`, `a-b`, formas funcionales y rutas declarativas en `README.md`, `ESPECIFICACION.md`, notas, `docs/`, `ejemplo/`, `tools/`, `perfiles/` y `nucleo/macros/`. `contexto` mostró `p.x`, `p`, `x` y `a + b · a - b · a * b`; `--expandir` pidió `<archivo.oracle>`; la ayuda general describió `convertir` como JSON a superficie y `formatear` como normalización que conserva comentarios. `docs/manual.html` y `docs/especificacion.html` reflejan la regla actual. Las coincidencias de JSON declarativo revisadas correspondían a migración, configuración, evidencia o historia; la búsqueda no prueba ausencia exhaustiva de otros textos.

Recorrí también `python3 tools/cli.py <comando> --help` para `nueva`, `caso`, `relaciones`, `medida`, `proyecto`, `biblioteca`, `plantilla`, `contexto`, `manual`, `convertir`, `formatear`, `test`, `juzgar`, `mutar`, `censar` y `estudio`. Salida recortada: `nueva`/`medida` ofrecieron plantilla de medida, `caso` plantilla de corpus, `biblioteca` esqueleto de biblioteca, `juzgar` pidió `<hechos.json>`, y `censar` describió `--hechos` como relación en JSON. `mutar` y `estudio` devolvieron código 1 con «Ejecutá `oracle --help`»; `convertir` y `formatear` mostraron la ayuda general. No interpreté JSON de hechos como autoría declarativa.

Construí el paquete con `UV_CACHE_DIR=/tmp/oracle-audit10-uv-cache uv build --no-build-isolation --python /usr/bin/python3 --out-dir /tmp/oracle-audit10-dist`: terminó con wheel y sdist 0.31.1. Inspeccioné el wheel con `zipfile`: la plantilla lleva 1 `.oracle`, 15 `.caso`, 1 `.relacion` y cero JSON declarativos en sus carpetas. Creé un venv temporal, instalé el wheel, y desde `/tmp` ejecuté `oracle plantilla sensor-prosa /tmp/oracle-audit10-plantilla-wheel` y `oracle test --rapido --proyecto /tmp/oracle-audit10-plantilla-wheel`; la plantilla indicó `--catalogo catalogos`, el árbol copiado tiene esas extensiones y el test terminó `VEREDICTO: VERDE`. No ejecuté el sensor externo.

## Tabla final

| Forma o punto | Estado | Evidencia ejecutada |
|---|---|---|
| Resta sin espacios en `NOTAS-DE-RELEASE.md` y `docs/notas.html` | **Hallazgo editorial histórico** | La nota enseña `t1.turno-1`; `p.turno-1` se lee pero el cargador lo rechaza; con espacios carga. |
| Espacios, versión inicial, notación científica, `agrupar`, `requiere`, `ambito`, CRLF, LF faltante, blanco, espacio final | Sólo lector puro | Impresor distinto; cargadores y LSP rechazaron/diagnosticaron. |
| Mayúsculas, BOM, función `mas`, resta `1-2`, comentario al final de código | Rechazadas por lector en las posiciones ensayadas | `ErrorSintaxis`; manual activo exige espacios para la resta. |
| `fila` redundante, `origen` invertido, relación entrecomillada, macro CRLF/sin LF | Rechazadas en archivo | Diferencia con impresor y error de cargador; `clave(t) t` falló ya en lector. |
| Líneas completas `#` | Excepción pública, no hallazgo | Medida, caso y macro cargaron; comentario final en línea de código falló. |
| Orden de relaciones, columnas y claves de objeto | Parte del árbol, no hallazgo | Dos órdenes impresos; relación invertida cargó en ambos órdenes. |
| Dos `donde`, umbral sin `porque`, escape `fila` cuando es impreso | Formas canónicas de árboles distintos o estructura necesaria | Sondas de lector, impresor y cargador indicadas. |
| MCP, LSP, `--leer`, `test`, `juzgar` | Rechazan o diagnostican el encabezado alternativo | Errores y salidas arriba; LSP 1 diagnóstico / 0 lentes. |
| JSON `.json` | Intercambio admitido | Cuatro cargadores devolvieron árboles; `convertir` exige JSON como origen. |
| Manual, contexto, ayudas, wheel y plantilla | Sin otra forma vigente en lo ejecutado | Comandos, búsquedas, build, instalación y test verde arriba. |

**una sola sintaxis de escritura: no, porque la nota de release 0.30.0 y su HTML todavía enseñan `t1.turno-1` como escritura sin espacios, y un `.oracle` equivalente es rechazado por el cargador actual.**
