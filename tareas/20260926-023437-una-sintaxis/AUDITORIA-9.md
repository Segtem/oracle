# Novena auditoría adversarial: una sintaxis

2026-09-26. Trabajé sobre este checkout sin cambiar código ni hacer commits. El criterio de esta ronda es **un texto por árbol**, con el orden de relaciones, columnas y claves de objeto como parte del árbol, salvo `origen`. Los comandos de abajo se ejecutaron; las salidas están recortadas. Las sondas temporales se escribieron en `/tmp`.

## Hallazgo: los comentarios dan dos textos cargables para el mismo árbol

Ejecuté este par en los cargadores de medida, caso y macro. Las bases fueron `MEDIDA` y `CASO` de `tests.test_forma_unica_texto` (normalicé `CASO` con `caso.imprimir(caso.leer(CASO))`) y `nucleo/macros/ninguno.oracle`. Para cada clase escribí `base` y `# otra explicación\n` + `base` en dos archivos temporales, llamé a `cargar_fuente_medida`, `cargar_fuente_caso` o `_datos_de_macro`, y comparé `json.dumps` de los árboles con `ensure_ascii=False`:

```text
medida textos distintos True mismo JSON True cargaron True
caso   textos distintos True mismo JSON True cargaron True
macro  textos distintos True mismo JSON True cargaron True
```

Comando: `PYTHONPATH=. python3 - <<'PY' ... PY` (la sonda creó los pares con `TemporaryDirectory`, `Path.write_text`, los tres cargadores y la comparación indicada). Repetí la carga de `# nota\n` + medida y caso en la matriz de abajo: ambos cargaron, y el LSP devolvió cero diagnósticos; la medida conservó una lente. `nucleo.forma.error_forma` compara `sin_comentarios(texto)` con el impresor; ésa es la causa verificable. La ayuda de `oracle formatear` dice «conserva comentarios». Por tanto **no es una grafía alternativa de cláusulas ni algo oculto**: es una excepción deliberada y enseñada, pero sí contradice literalmente «un texto por árbol» y «texto distinto del impresor que cargue». Si se quiere conservarla, la regla pública precisa ser «un texto por árbol después de quitar líneas de comentario»; si se exige literalidad, hay que retirar la excepción con su costo para archivos comentados.

## Reejecución de los puntos abiertos de auditorías 2 a 8

Preparé `/tmp/audit9_probe.py` con `MEDIDA`, `AGRUPADA`, `CASO` y `RELACION` de `tests.test_forma_unica_texto`, más la macro empaquetada. Por variante ejecuté lector, `imprimir`, cargador de archivo temporal y `lsp.diagnosticar/lentes`. Primer intento: `python3 /tmp/audit9_probe.py` falló con `ModuleNotFoundError: No module named 'tests'` por el `sys.path` del archivo temporal. Lo repetí con `PYTHONPATH=. python3 /tmp/audit9_probe.py`. Salida recortada (LSP = diagnósticos/lentes):

```text
medida base               impreso=True  carga=OK                         LSP=0/1
medida espacios           impreso=False carga=MedidaMalDeclarada forma   LSP=1/0
medida version            impreso=False carga=MedidaMalDeclarada otro    LSP=1/0
medida cientifica         impreso=False carga=MedidaMalDeclarada forma   LSP=1/0
medida agrupar            impreso=False carga=MedidaMalDeclarada forma   LSP=1/0
medida ambito             impreso=False carga=MedidaMalDeclarada forma   LSP=1/0
medida a-b                impreso=False carga=MedidaMalDeclarada forma   LSP=1/0
medida CRLF/sin LF/blanco/espacio final: impreso=False, carga=MedidaMalDeclarada forma, LSP=1/0
caso origen invertido/fila redundante/clave sin ;: impreso=False, carga=CasoMalDeclarado forma, LSP=1/0
relacion comillas         impreso=False carga=RelacionMalDeclarada forma LSP=1/0
macro CRLF/sin LF         impreso=False carga=MacroMalDeclarada forma    LSP=1/0
medida/caso/macro comentario: carga=OK, LSP=0/1, 0/0, 0/0
```

La `version` de esa sonda era `sintaxis 0.8`: falló antes de la comparación de forma por incompatibilidad de versión. La variante `requiere` de la matriz estaba mal colocada (antes del umbral) y dio `ErrorSintaxis`; no la conté. Repetí ambas con sondas corregidas: `sintaxis 1.0\n` + `MEDIDA` dio lector OK, igualdad con impresor falsa y `MedidaMalDeclarada` por forma; `requiere pieza, evento` después del umbral y las dos líneas `requiere pieza` / `requiere evento` dieron **el mismo árbol**, pero sólo la primera imprimió idéntica y cargó; la segunda dio `MedidaMalDeclarada: fuera de la forma única`.

Ejecuté además un heredoc Python con variantes de expresión y árboles JSON guardados en `.json`:

```text
dos donde: lector OK, impreso True
umbral sin porque: lector OK, impreso True
umbral sin segun: lector OK, impreso True
mas/menos/por(1,2): ErrorSintaxis (en posición de resumen)
MEDIDA mayúscula, BOM: ErrorSintaxis
JSON medida list; JSON caso dict; JSON relacion list; JSON macro list
relacion .oracle: RelacionMalDeclarada, una relación se escribe en .relacion
MCP no impresa: ErrorHerramienta, fuera de la forma única
```

`col(p)` dentro de `resumen` sí se leyó e imprimió idéntico como nombre de agregado; **no** es una prueba de que el antiguo acceso funcional a una columna esté admitido en una expresión. La quinta y sexta auditorías distinguen esa posición. La llamada MCP de `formato: json` en mi heredoc no produjo línea (no hubo excepción en esa llamada directa), por lo que no afirmo rechazo en esa API privada; el contrato público restringe el esquema, como constaba en auditorías anteriores.

Repetí el escape necesario de caso con `c['evidencia']={'a':[{'x':1},{'y':2}]}`: `caso.imprimir` produjo dos líneas `fila {…}`, `cargar_fuente_caso` cargó `001-demo` y la ida y vuelta fue idéntica. El escape redundante para una sola fila homogénea fue rechazado en la matriz.

El orden de relaciones, columnas y objetos del caso de la octava auditoría no se cuenta como segunda grafía: por la definición nueva es orden del árbol. Reprobé `origen` invertido y el impresor/cargador lo normalizaron/rechazaron. No encontré en estas sondas otra pareja sin comentarios con mismo JSON y dos cargas válidas.

## Entradas de CLI y editor

Comandos ejecutados y salida recortada:

```bash
python3 tools/sintaxis.py --leer /tmp/oracle-audit9-bad.oracle
# ✗ /tmp/oracle-audit9-bad.oracle: fuera de la forma única
python3 tools/cli.py formatear /tmp/oracle-audit9-bad.oracle
# requiere formato; -medida   demo.prueba: / +medida demo.prueba:
python3 tools/cli.py init /tmp/oracle-audit9-project
# Creó el proyecto y mostró próximos pasos
python3 tools/cli.py test --rapido --proyecto /tmp/oracle-audit9-project
# SINTAXIS ✗ — 1 archivo(s) fuera de la forma única; VEREDICTO: ROJO
python3 tools/cli.py juzgar --proyecto /tmp/oracle-audit9-project --con /tmp/oracle-audit9-hechos.json
# ERROR AL EVALUAR — .../demo.prueba.oracle: fuera de la forma única
```

Antes de estos comandos escribí `/tmp/oracle-audit9-bad.oracle` con `MEDIDA.replace('medida demo', 'medida   demo')`, lo copié a `catalogos/` del proyecto temporal y escribí `{}` en `hechos.json`. Las variantes de la matriz dieron diagnóstico y ninguna lente en LSP. No ejecuté de nuevo `revisar`, `medida probar`, `caso generar`, `mutar`, `censar`, `estudio` ni todas las llamadas MCP/LSP; la conclusión sobre ellas queda limitada a las sondas anteriores, no a una nueva comprobación.

Ejecuté `lsp.completar` sobre un borrador que termina en `umbral <= 0 segun `, una vez con encabezado normal y otra con triple espacio: ambos devolvieron `contrato, convencion, medicion, tanteo`. Es la asistencia a un borrador incompleto que quedó abierta en las rondas 7 y 8; no cargó una medida. El primer intento usó una columna LSP fuera de la línea y dio `IndexError`; corregí la posición con `len(draft.splitlines()[-1])`.

`python3 tools/cli.py convertir /tmp/oracle-audit9-project/catalogos/demo.prueba.oracle` rechazó el archivo con «esperaba una medida .json para convertir a superficie». Guardé el árbol de `MEDIDA` como `/tmp/oracle-audit9-medida.json`: `python3 tools/cli.py convertir /tmp/oracle-audit9-medida.json` y `python3 tools/sintaxis.py --imprimir /tmp/oracle-audit9-medida.json` imprimieron ambos `medida demo.prueba:` y `de pieza p` al comienzo. La lectura JSON aquí sirve a la migración/intercambio.

Ejecuté la receta `ejemplo/caso-observado/convertir.py` con su captura y metadatos reales. Con destino `/tmp/494-la-cota-de-la-sombra-observada-por-el-recorrido.caso` creó un caso que `cargar_fuente_caso` cargó; con el mismo nombre terminado en `.json` respondió «destino debe llamarse <id>.caso». Un intento previo con nombre abreviado `.caso` fue rechazado por la misma regla.

## Enseñanza, salidas y wheel

Ejecuté `python3 tools/cli.py manual aritmetica | head -8`, `rg -n 'a-b|sin espacios' docs/manual.html tools/manual.py | head -8` y `python3 tools/cli.py contexto --compacto | rg -n 'accesores:|aritmética:|mas\(' | head -8`. Salidas: manual y HTML dicen que la resta lleva espacios y que `a-b` queda fuera de la forma única; contexto muestra `p.x`, `p`, `x`, y `a + b · a - b · a * b`. Así se cerró la enseñanza errónea de la octava auditoría.

Ejecuté `python3 tools/cli.py --help`, `python3 tools/cli.py medida help`, `caso help`, `proyecto help`, `biblioteca help`, y `python3 tools/cli.py convertir --help` / `formatear --help` (estos dos últimos imprimieron ayuda general). La ayuda general dice «Convierte medidas JSON a superficie» y «Normaliza la superficie y conserva comentarios»; `medida help` presenta `expandir` como forma canónica de una macro. No vi una instrucción nueva de autoría JSON en esas salidas.

Ejecuté búsquedas `rg -n` de `.json`, `.oracle`, `.caso`, `.relacion`, `a-b` y funciones antiguas en `README.md docs ejemplo tools`, y una búsqueda más estrecha de rutas `catalogos/`, `corpus/`, `relaciones/` o `macros/` terminadas en `.json`. Encontré `docs/03-escribir-una-medida.md:104` (`convertir <medida.json>` como migración), `tools/sintaxis.py:3` (ejemplo de `--imprimir` desde JSON canónico), notas históricas de migración y evidencia JSON; no los conté como autoría nueva. `docs/especificacion.html` declara explícitamente «texto válido ... sin contar las líneas de comentario». La búsqueda no prueba ausencia exhaustiva de prosa equivalente con otras palabras.

Ejecuté `python3 tools/medida.py --expandir`: pidió `<archivo.oracle>`. Ejecuté `rg -n 'sintaxis.*1\.0' NOTAS-DE-RELEASE.md | head -3`: sin salida; persiste la omisión editorial ya señalada, que no enseña otra sintaxis.

Construí el wheel con:

```bash
UV_CACHE_DIR=/tmp/oracle-audit9-uv-cache uv build --no-build-isolation --python /usr/bin/python3 --out-dir /tmp/oracle-audit9-dist
# Successfully built ...oracle_metalenguaje-0.31.1-py3-none-any.whl
```

Inspección con `zipfile.ZipFile`: `plantilla_sensor_prosa/` contiene 15 `.caso`, 1 `.relacion`, 1 `.oracle`; no hay JSON declarativo bajo sus `catalogos/`, `corpus/`, `relaciones/` o `macros/`. Ejecuté `python3 -m venv /tmp/oracle-audit9-venv`, instalé ese wheel con `/tmp/oracle-audit9-venv/bin/pip install --no-deps /tmp/oracle-audit9-dist/*.whl -q`, y desde `/tmp` ejecuté:

```bash
/tmp/oracle-audit9-venv/bin/oracle plantilla sensor-prosa /tmp/oracle-audit9-plantilla-wheel
/tmp/oracle-audit9-venv/bin/oracle test --rapido --proyecto /tmp/oracle-audit9-plantilla-wheel
# CORPUS OK · 15 casos
# SINTAXIS OK · 1 medidas · 0 macros · 15 casos · 1 relaciones
# VEREDICTO: VERDE
```

Un primer `oracle plantilla` corrido desde el checkout copió el árbol fuente y mostró una ruta relativa al catálogo de este repo; repetí desde `/tmp` para forzar los recursos instalados del wheel. Desde allí la instrucción impresa usa `--catalogo catalogos`, y los archivos copiados son 15 `.caso`, 1 `.oracle`, 1 `.relacion`. También leí el README instalado: enseña `.caso` para el caso y `hechos-construidos.json` como evidencia. No ejecuté `tools/verificar_instalacion.py` completo.

## Tabla final

| Forma o punto | Estado en esta ronda | Evidencia ejecutada |
|---|---|---|
| Línea de comentario en medida, caso o macro | **Hallazgo literal: dos textos, mismo JSON, ambos cargan** | Tres pares por cargador; el LSP tampoco los diagnostica. Excepción deliberada de `sin_comentarios`. |
| Orden de relaciones, columnas y claves de objetos | Dos árboles por definición vigente; no es hallazgo | No repetí el experimento de inversión de la octava auditoría; apliqué la decisión de la última nota. |
| Orden de `origen` | Cerrado | Inversión: impresor distinto, cargador y LSP rechazan. |
| Resta `a-b` | Enseñanza corregida; archivo rechazado | Manual CLI/HTML exige espacios; lector la normaliza y cargador la rechaza. |
| Espacios, científica, `agrupar`, `ambito`, CRLF, falta de LF, blanco y espacio final | Sólo lector puro en las sondas | Impresor distinto, cargador rechaza, LSP 1/0. |
| Versión inicial | Rechazada | `sintaxis 1.0` fue leída, no impresa y rechazada por forma; `0.8` falló por incompatibilidad. |
| `requiere` repetido | Sólo lector puro | Dos líneas y una línea dieron mismo árbol; sólo la línea única cargó. |
| Caso con `fila` redundante o `clave` sin `;`; relación entrecomillada | Sólo lector puro | Cargadores rechazan, LSP diagnostica. |
| Caso con `fila` por filas heterogéneas | Canónico | Dos líneas `fila`, carga y vuelta idéntica. |
| Dos `donde`; umbral sin `segun` o `porque` | Árboles propios, grafías impresas | `imprimir(leer(texto)) == texto` para cada variante. |
| `mas/menos/por` en resumen, mayúsculas y BOM | Rechazados | `ErrorSintaxis` en las sondas. `col(p)` en resumen es agregado, no accesor funcional. |
| JSON de medida/caso/relación/macro en `.json` | Intercambio permitido | Cuatro cargadores ejecutados; no hallazgo sin enseñanza de autoría. |
| MCP no impreso; `sintaxis.py --leer`; `test`; `juzgar`; LSP | Rechazados o diagnosticados para la variante ejecutada | Errores de forma, ROJO de test, LSP 1/0. |
| LSP completion sobre borrador con encabezado alternativo | Asistencia, no carga | Cuatro orígenes iguales en ambos borradores incompletos. |
| `convertir`, `--imprimir` desde JSON, receta caso-observado | Sin producción JSON declarativa | Conversores imprimen superficie; receta sólo escribe `.caso`. |
| Manual, contexto, ayuda, docs examinados, wheel y plantilla instalada | Sin segunda grafía enseñada/producida en lo ejecutado | Búsquedas, comandos de ayuda, build, inspección, copia y `test --rapido` verde. |

**una sola sintaxis de escritura: no, porque una línea de comentario adicional produce un texto distinto con exactamente el mismo JSON y los cargadores de medida, caso y macro aceptan ambos; es una excepción deliberada que la especificación y la ayuda deben formular como tal si se conserva.**
