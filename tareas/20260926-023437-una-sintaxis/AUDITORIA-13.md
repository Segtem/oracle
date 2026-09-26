# Decimotercera auditoría adversarial: una sintaxis

2026-09-26. Tomé como criterio `ESPECIFICACION.md:526-550`: un texto por árbol, exceptuadas **todas** las líneas completas que empiezan con `#` tras la sangría; esas líneas no pertenecen al árbol, se pueden agregar o quitar y `oracle formatear` las conserva. El orden de relaciones, columnas y claves de objetos (salvo `origen`) pertenece al árbol. El JSON en `.json` es intercambio. No tomé el «sí» de AUDITORIA-11 como premisa. Todo lo afirmado abajo procede de los comandos indicados. Las sondas y el wheel quedaron en `/tmp`; no cambié código ni hice commits.

## Hallazgo: comentarios completos en bloques de `.caso`

En `corpus/simulacion/301-simulador-que-ignora-la-semilla.caso` inserté `        # nota` justo después de `    sintoma:`. Ejecuté:

```bash
PYTHONPATH=. python3 - <<'PY'
from pathlib import Path
from nucleo.caso import leer, imprimir
from nucleo.forma import sin_comentarios
a = Path('corpus/simulacion/301-simulador-que-ignora-la-semilla.caso').read_text()
b = a.replace('    sintoma:\n', '    sintoma:\n        # nota\n', 1)
x, y = leer(a), leer(b)
print('arbol_igual', x == y)
print('sintoma_comentado', repr(y['sintoma'][:65]))
print('sin_comentarios_igual', sin_comentarios(b) == a)
print('impreso_igual', imprimir(x) == imprimir(y))
PY
```

Salida recortada: `arbol_igual False`; `sintoma_comentado '# nota\nEl simulador sortea sin usar la semilla: dos ejecuciones i'`; `sin_comentarios_igual True`; `impreso_igual False`. El lector de casos incorporó la línea de comentario a la prosa; `sin_comentarios` la eliminó para comparar. No es sólo una posición rechazada: el lector le da significado de **dato** a una línea que la definición pública excluye del árbol.

Escribí esa variante en `/tmp/oracle-audit13-comment-inside.caso` y ejecuté `python3 tools/cli.py formatear /tmp/oracle-audit13-comment-inside.caso`, `python3 tools/cli.py formatear /tmp/oracle-audit13-comment-inside.caso --escribir`, `cargar_fuente_caso` y `lsp.diagnosticar`. Salidas recortadas:

```text
formatear: requiere formato; el diff añade +        # nota
formatear --escribir: ✗ ... no se pudieron conservar los comentarios
cargar_fuente_caso: CasoMalDeclarado ... fuera de la forma única
LSP: 1 diagnóstico
```

Copié la plantilla empaquetada a `/tmp/oracle-audit13-template`, inserté la misma línea tras `sintoma:` en su caso `015-relacion-vacia.caso` y ejecuté `python3 tools/cli.py test --rapido --proyecto /tmp/oracle-audit13-template` y `python3 tools/cli.py caso listar --proyecto /tmp/oracle-audit13-template`:

```text
SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
VEREDICTO: ROJO (sintaxis: forma única)
✗ .../015-relacion-vacia.caso: fuera de la forma única
```

Para no escoger sólo un sitio, ejecuté una matriz que insertó `# c`, `    # c` y `\t# c` en **cada límite de línea** de una medida, un caso, una relación y una macro reales, y comparó cada carga con el árbol original. Comando: `PYTHONPATH=. python3 - <<'PY' ...` con `cargar_fuente_medida`, `cargar_fuente_caso`, `cargar_fuente_relacion` y `_datos_de_macro`, sobre `meta.agrupar_no_agranda_la_relacion.oracle`, `301-simulador-que-ignora-la-semilla.caso`, `mutante.relacion` y `ninguno.oracle`. Salida:

```text
medida positions 7 probes 21 failures 0
caso positions 22 probes 66 failures 30
relacion positions 20 probes 60 failures 0
macro positions 10 probes 30 failures 0
```

Las 30 fallas de caso corresponden a diez límites, cada uno con las tres sangrías: dentro de `origen`, tras `sintoma:`, entre cabecera y filas de evidencia, entre filas, y tras `leccion:`. Con `# nota` sin sangría, los límites 3, 4, 9, 13-18 y 20 fallaron. Por ejemplo, antes de la primera fila de `origen`: `se esperaba origen con al menos un campo`; antes de la prosa de `sintoma`: `se esperaba prosa`; antes de la primera relación de `evidencia`: `se esperaba al menos una relación de evidencia`. Esta es una contradicción directa de la excepción sin restricción por bloque escrita para `.caso`.

## Reejecución de las formas anteriores

Ejecuté `PYTHONPATH=. python3 /tmp/oracle_audit13_probe.py`. Para cuatro fuentes reales, el script probó lector, impresor, cargador y `lsp.diagnosticar`; `igual` significa `sin_comentarios(texto) == imprimir(leer(texto))`. Selección de la salida, incluyendo todas las clases del borde:

```text
medida/caso/relacion/macro base: igual, OK, LSP=0
medida/caso/relacion/macro comentario_inicio: igual, OK, LSP=0
medida/caso/relacion/macro comentario_sangrado: igual, OK, LSP=0
medida/caso/relacion/macro comentario_final: igual, OK, LSP=0
medida/caso/relacion/macro comentario_sinLF: igual, OK, LSP=0
medida/caso/relacion/macro CRLF: distinto, error de forma, LSP=1
medida/caso/relacion/macro sin_LF: distinto, error de forma, LSP=1
medida/caso/relacion/macro blanco: distinto, error de forma, LSP=1
medida/espacio_final y tab_final: distinto, error de forma, LSP=1
caso, relacion/espacio_final y tab_final: error de lector, LSP=1
medida/caso/relacion/macro BOM: error de lector, LSP=1
medida/caso/relacion inline: error de lector, LSP=1
macro inline: igual, OK, LSP=0 (alteró la primera línea de comentario)
medida/triple_espacio, version: distinto, error de forma, LSP=1
relacion/unidad_corchetes: error de lector, LSP=1
caso/origen_invertido: distinto, error de forma, LSP=1
```

La sonda `macro/espacio_final`, `macro/tab_final` e `macro/inline` de esa matriz alteró la **primera línea de comentario** del archivo base: dio `igual`, carga OK y LSP=0, conforme a la excepción. No la presento como código alternativo.

Ejecuté además `PYTHONPATH=. python3 /tmp/oracle_audit13_legacy.py` con variantes de las auditorías 2 a 12. Salida completa y recortada:

```text
medida agrupar_invertido distinto MedidaMalDeclarada forma
medida requiere_doble distinto MedidaMalDeclarada forma
medida cientifica distinto MedidaMalDeclarada forma
medida resta_sin_espacios distinto MedidaMalDeclarada forma
medida parentesis distinto MedidaMalDeclarada forma
medida ambito_omitido igual OK
medida funcion_mas lector ErrorSintaxis MedidaMalDeclarada otro
medida funcion_col lector ErrorSintaxis MedidaMalDeclarada otro
medida mayuscula lector ErrorSintaxis MedidaMalDeclarada otro
caso clave_sin_puntoycoma lector ErrorSintaxis CasoMalDeclarado otro
caso origen_invertido distinto CasoMalDeclarado forma
relacion comillas distinto RelacionMalDeclarada forma
relacion mayuscula lector RelacionMalDeclarada RelacionMalDeclarada otro
macro version distinto MacroMalDeclarada forma
macro invocacion_argumentos lector ErrorSintaxis MacroMalDeclarada otro
```

Probé dos `donde` y un `donde` con `y` sobre `simulacion.la_traza_no_tiene_huecos.oracle`: los dos textos coincidieron con su impresor y `leer(a) == leer(b)` fue `False`. Probé el escape redundante `fila {...}` contra la tabla de `059-clave-declarada-en-un-caso.caso`: `leer` dio el mismo árbol, pero sólo la tabla coincidió con `imprimir`; la variante `fila` no fue canónica. No repetí una ejecución separada del escape necesario para filas heterogéneas, ya registrada en auditorías anteriores.

## Entradas y materiales

Sobre `/tmp/oracle-audit13-bad.oracle` (tres espacios en el encabezado) ejecuté `python3 tools/sintaxis.py --leer`, `python3 tools/cli.py medida revisar`, `python3 tools/cli.py medida probar --con '[]'`, `python3 tools/medida.py --expandir` y `python3 tools/cli.py formatear`: las primeras cuatro informaron `fuera de la forma única`; `formatear` respondió `requiere formato` y propuso el encabezado del impresor. `_medida_en_memoria({'texto': bad, 'formato': 'oracle'}, None)` respondió `ErrorHerramienta MEDIDA_INVALIDA — ... fuera de la forma única`; LSP dio 1 diagnóstico y 0 lentes. En la plantilla temporal deformé su medida de igual modo: `oracle test --rapido` dio `SINTAXIS ✗ — 1 archivo(s) fuera de la forma única` y ROJO; `contexto` avisó `no se pudo cargar el catálogo`; `medida listar` dio `CATÁLOGO INVÁLIDO`.

Ejecuté `python3 tools/sintaxis.py --verificar`: `63` medidas, `6` macros, `217` casos y `13` relaciones convertidos; `forma única: OK`; `24` bloques de documentación verificados. `python3 tools/cli.py test --rapido` sobre el repo dio `SINTAXIS OK · 63 medidas · 6 macros · 217 casos · 13 relaciones` y `VEREDICTO: VERDE`. Esta última corrida confirma sólo los archivos existentes; no prueba la libertad de insertar comentarios prometida por la especificación.

Ejecuté `python3 tools/cli.py manual aritmetica` y `python3 tools/cli.py contexto --compacto`: mostraron `a - b` con espacios, aritmética infija y accesores `p.x`, `p`, `x`. `rg -n -C 1 't1.turno-1' NOTAS-DE-RELEASE.md docs/notas.html` halló la aclaración explícita de que desde sintaxis 1.0 se escribe `t1.turno - 1`; bajo el criterio histórico del encargo, no es hallazgo. `python3 tools/cli.py --help` dice de `formatear`: «las líneas # no cuentan y se conservan», promesa desmentida por el caso probado.

Construí sdist y wheel con `UV_CACHE_DIR=/tmp/oracle-audit13-uv-cache uv build --python /usr/bin/python3 --no-build-isolation --out-dir /tmp/oracle-audit13-dist`. Inventarié el wheel con `ZipFile`: la plantilla trae 1 `.oracle`, 15 `.caso`, 1 `.relacion` y 1 `oracle.json`, sin declaración JSON adicional. Instalé el wheel en `/tmp/oracle-audit13-venv` con `pip install --no-index --no-deps`, corrí `oracle plantilla sensor-prosa /tmp/oracle-audit13-template` y `oracle test --rapido --proyecto /tmp/oracle-audit13-template`: `SINTAXIS OK · 1 medidas · 0 macros · 15 casos · 1 relaciones`, `VEREDICTO: VERDE`. El build generó `oracle_metalenguaje.egg-info` en el checkout; lo eliminé después. `git status --short` estaba vacío tras esa limpieza.

## Tabla final

| Superficie / punto | Estado observado | Evidencia ejecutada |
|---|---|---|
| `.caso`: `#` dentro de prosa, origen o evidencia | **Hallazgo: contradicción pública; en prosa también cambia el árbol puro** | Inserciones exhaustivas: 30/66 fallas; `sintoma` entra como dato; cargador, `test`, `caso listar` y LSP fallan; `formatear --escribir` no conserva. |
| `.oracle` medida y macro: `#` completo | Conforme en posiciones ensayadas | 21/21 y 30/30 inserciones sin cambio de árbol; cargador OK. |
| `.relacion`: `#` completo, incluida posición final tras `alcance` | **Hallazgo de AUDITORIA-12 cerrado** | 60/60 inserciones sin cambio de árbol; cargador OK; `formatear` «ya tiene forma única»; LSP=0. |
| Espacios, CRLF, LF faltante, BOM, línea blanca, versión inicial, científica, `agrupar`, `requiere`, paréntesis, resta pegada, origen invertido, variante entrecomillada | Rechazo o sólo lectura pura | Dos matrices de lector, impresor, cargador y LSP; variantes no impresas rechazadas. |
| `mas`, `col`, encabezados en mayúscula, macro por argumentos, unidades entre corchetes | Rechazados por lector en las sondas | Matrices anteriores. |
| `ambito` omitido, dos `donde` frente a `y`, tabla frente a `fila` redundante | Árbol canónico propio o normalización rechazada | Comparación ejecutada de árboles y de impresión. |
| CLI de medida, MCP y LSP con medida no impresa; `test`, `contexto`, `medida listar` | Rechazo o diagnóstico | Comandos y llamadas indicados; `formatear` propone la grafía impresa. |
| Manual, contexto, ayuda, nota histórica, verificador, wheel y plantilla instalada | Sin segunda enseñanza/producción en lo ejecutado; **ayuda de `formatear` contradicha** | Comandos, búsqueda, build, inventario, instalación y test indicados. |
| JSON en `.json` | Intercambio permitido; no hallazgo | Inventario del wheel y definición pública; en esta ronda no repetí las cuatro cargas JSON individuales de auditorías previas. |

**una sola sintaxis de escritura: no, porque la excepción pública de líneas completas `#` no se cumple en `.caso`: dentro de `sintoma` el lector las agrega al árbol y el cargador, el formateador y el LSP rechazan el archivo; otras posiciones de `origen` y `evidencia` también fallan.**
