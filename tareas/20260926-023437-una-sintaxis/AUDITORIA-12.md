# Duodécima auditoría adversarial de una sintaxis

2026-09-26. Confirmación independiente del informe 11, sin tomar su veredicto como premisa. Apliqué la definición de `ESPECIFICACION.md` §§0 y versión de la superficie: un texto por árbol salvo líneas completas de comentario; el orden de relaciones, columnas y claves (excepto `origen`) forma parte del árbol. JSON en `.json` es intercambio admitido. Usé archivos de prueba en `/tmp`; no cambié código ni hice commits.

## Hallazgo: la excepción pública de comentarios no funciona en relaciones

La especificación dice que la regla de forma única **aplica también a `.relacion`** (`ESPECIFICACION.md:529-530`), y luego que una línea que empieza con `#`, después de la sangría, «no es parte del árbol ni de la forma única: se puede agregar o sacar» (`:538-542`). `nucleo.forma.sin_comentarios` efectivamente la elimina para comparar. Sin embargo, `nucleo.relacion.leer` sólo omite líneas vacías y exige `relacion <nombre>:` como primera línea; tampoco salta comentarios en el cuerpo. `oracle formatear` llama ese mismo lector antes de poder conservar comentarios.

Ejecuté una sonda con el texto real de `relaciones/pieza.relacion`, insertando `# nota` al comienzo, antes de `id` y después de `alcance`, cada uno en un `.relacion` temporal. Para cada archivo llamé `cargar_fuente_relacion` y `python3 tools/cli.py formatear <archivo>`:

```text
inicio   cargador: RelacionMalDeclarada: se esperaba `relacion <nombre>:`
         formatear: rc 1, ✗ ... se esperaba `relacion <nombre>:`
sangrado cargador: RelacionMalDeclarada: línea 2: campo o cláusula de relación inválida: # nota
         formatear: rc 1, ✗ ... campo o cláusula de relación inválida: # nota
final    cargador: RelacionMalDeclarada: línea 14: `alcance` debe estar al final
         formatear: rc 1, ✗ ... `alcance` debe estar al final
```

`lsp.diagnosticar(Proyecto(Path.cwd()), ruta_relacion, '# nota\n' + texto_base)` devolvió **1 diagnóstico**. Esto contradice una excepción pública de la única forma, aunque no constituye una segunda grafía aceptada. La observación adicional es que el formateador no puede corregir ni conservar ese comentario en una relación. La undécima auditoría probó comentarios en medida, caso y macro, pero no en relación.

## Reejecución de grafías de las auditorías 2 a 11

Ejecuté `PYTHONPATH=. python3 /tmp/audit12_matrix.py`. El script construyó medidas, casos, relaciones y macros temporales; para cada variante llamó lector, impresor y cargador correspondiente. `igual` compara el texto sin comentarios con el impresor. Salida recortada, conservando todas las clases ensayadas:

```text
medida   base                    igual                  OK
medida   CRLF                    distinto               MedidaMalDeclarada forma
medida   sin-LF                  distinto               MedidaMalDeclarada forma
medida   comentario              igual                  OK
medida   blanco                  distinto               MedidaMalDeclarada forma
medida   espacio-final           distinto               MedidaMalDeclarada forma
medida   BOM                     lector:ErrorSintaxis   MedidaMalDeclarada otro
caso     base                    igual                  OK
caso     CRLF                    distinto               CasoMalDeclarado forma
caso     sin-LF                  distinto               CasoMalDeclarado forma
caso     comentario              igual                  OK
caso     blanco                  distinto               CasoMalDeclarado forma
caso     espacio-final           lector:ErrorSintaxis   CasoMalDeclarado otro
relacion base                    igual                  OK
relacion CRLF                    distinto               RelacionMalDeclarada forma
relacion sin-LF                  distinto               RelacionMalDeclarada forma
relacion comentario              lector:RelacionMalDeclarada RelacionMalDeclarada otro
relacion blanco                  distinto               RelacionMalDeclarada forma
macro    base                    igual                  OK
macro    CRLF                    distinto               MacroMalDeclarada forma
macro    sin-LF                  distinto               MacroMalDeclarada forma
macro    comentario              igual                  OK
medida   triple-espacio          distinto               MedidaMalDeclarada forma
medida   version                 distinto               MedidaMalDeclarada forma
medida   cientifica              distinto               MedidaMalDeclarada forma
medida   resta-sin-espacios      distinto               MedidaMalDeclarada forma
medida   resta-con-espacios      igual                  OK
medida   parentesis              distinto               MedidaMalDeclarada forma
medida   ambito-omitido          igual                  OK
medida   dos-donde               igual                  OK
medida   dos-donde-vs-y          igual                  OK
medida   mayuscula               lector:ErrorSintaxis   MedidaMalDeclarada otro
medida   mas / menos / por / col  lector:ErrorSintaxis   MedidaMalDeclarada otro
medida   inline-comentario       lector:ErrorSintaxis   MedidaMalDeclarada otro
caso     origen-invertido        distinto               CasoMalDeclarado forma
relacion mayuscula               lector:RelacionMalDeclarada RelacionMalDeclarada otro
relacion campo-invertido         igual                  OK
macro    invocacion-argumentos   lector:ErrorSintaxis   MacroMalDeclarada otro
```

La primera ejecución de la matriz se detuvo en una aserción del macro base porque el impresor omite sus comentarios completos. Corregí sólo el script temporal para comparar contra `sin_comentarios(macro)` y obtuve la salida de arriba. En otra sonda, `macro/espacio-final` dio `igual` y carga OK porque agregué el espacio **a su primera línea de comentario**, que está excluida por la definición; no lo interpreté como variante de código.

Ejecuté además sondas separadas para los pares que se habían discutido como dos grafías o dos árboles:

```text
requiere una línea / dos líneas: mismo-arbol=True; canonicos=True/False;
    la variante doble: MedidaMalDeclarada fuera de la forma única
agrupar clave/agregado / agregado/clave: mismo-arbol=True; canonicos=True/False;
    la variante invertida: MedidaMalDeclarada fuera de la forma única
dos donde / un donde con y: mismo-arbol=False; canonicos=True/True
relación con id/ox / ox/id: mismo-arbol=False; canonico=True
caso con tabla / fila {...} redundante: mismo-arbol=True; canonico alternativo=False;
    CasoMalDeclarado fuera de la forma única
variante medida: / "medida": en .relacion: mismo-arbol=True;
    canonico alternativo=False; RelacionMalDeclarada fuera de la forma única
```

La tabla y `fila {...}` se probaron sobre `corpus/simulacion/301-simulador-que-ignora-la-semilla.caso`. La variante entrecomillada de relación se probó sobre `relaciones/mutante.relacion`. La matriz también cubrió `origen` invertido, versión inicial, notación científica, espacios, CRLF, LF ausente, BOM, comentarios al final de código y operaciones funcionales.

Después ejecuté las sondas de `clave(id)` sin `;` y `fila` heterogénea. En `corpus/proceso/059-clave-declarada-en-un-caso.caso`, sustituí la tabla `mutante: clave(id); id, ...` por `mutante: clave(id)` y dos `fila {...}` con los mismos campos y orden. `leer` devolvió el mismo árbol; `imprimir` difirió; `cargar_fuente_caso` respondió `fuera de la forma única`. Si se quita el `;` conservando la cabecera tabular, el lector respondió `se esperaba ';' antes de campos`. En `corpus/meta/497-el-censo-distingue-perdidas-ilegibles-y-ceros.caso`, el escape `fila` para filas heterogéneas sí fue canónico: `imprimir(leer(texto)) == texto` y el cargador respondió OK.

## Entradas, intercambio y materiales

En archivos temporales con `medida   demo.unica:` ejecuté `tools/sintaxis.py --leer`, `oracle medida revisar`, `oracle medida probar --con '[]'`, `tools/medida.py --expandir` y `oracle formatear`; también llamé MCP y LSP. Salida recortada:

```text
--leer: rc 1, ✗ ... fuera de la forma única
medida revisar: rc 1, ✗ ... fuera de la forma única
medida probar: rc 1, ✗ ... fuera de la forma única
--expandir: rc 1, Traceback (most recent call last); la excepción fue de carga
formatear: rc 0, ... requiere formato
LSP: 1 diagnóstico, 0 lentes
MCP _medida_en_memoria: ErrorHerramienta MEDIDA_INVALIDA — ... fuera de la forma única
```

Para las entradas de proyecto, copié la plantilla instalada a `/tmp/oracle-audit12-proj-pmkvutfp` y cambié sólo el encabezado de su medida a `medida   prosa.alcance_sin_afirmacion_adversa:`. Ejecuté estos comandos, con las salidas recortadas:

```text
python3 tools/cli.py test --rapido --proyecto <copia>
    rc 1, SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
python3 tools/cli.py juzgar --proyecto <copia> --con /tmp/oracle-audit12-hechos.json
    rc 2, ERROR AL EVALUAR — ... fuera de la forma única
python3 tools/cli.py contexto --proyecto <copia>
    rc 0, ⚠ no se pudo cargar el catálogo — MedidaMalDeclarada: ... fuera de la forma única
python3 tools/cli.py medida listar --proyecto <copia>
    rc 1, CATÁLOGO INVÁLIDO — ... fuera de la forma única
```

El archivo de evidencia temporal contenía `{"afirmacion_prosa": []}`. En otra copia de la plantilla agregué una línea en blanco antes del encabezado de un caso y ejecuté `oracle caso listar --proyecto <copia>` y `oracle test --rapido --proyecto <copia>`: ambos salieron 1 e informaron `fuera de la forma única`. `oracle nueva prosa.audit12` y `oracle caso prosa/999-audit12` en una copia temporal crearon `.oracle` y `.caso` respectivamente. Son andamios con marcadores por completar; el segundo hizo que `relaciones --escribir` fallara al inventariar evidencia. Repetí `relaciones --escribir` en una copia intacta de `ejemplo/sensor-prosa`: rc 0, «No se escribió ningún borrador: no hay relaciones observadas sin declarar». No lo presento como prueba de la grafía de un borrador producido.

Escribí árboles leídos de fuentes reales como cuatro archivos temporales `.json` y llamé los cargadores de medida, caso, relación y macro: los cuatro devolvieron el árbol original. Un árbol de relación escrito en `.oracle` produjo `RelacionMalDeclarada: una relación se escribe en .relacion`. Esto confirma la excepción de intercambio; no lo conté como segunda sintaxis de escritura.

Comprobé la aclaración histórica con `rg -n -C 1 't1.turno-1' NOTAS-DE-RELEASE.md docs/notas.html`: ambos textos aún contienen `t1.turno-1`, y `NOTAS-DE-RELEASE.md:157-159` / `docs/notas.html:67` dicen explícitamente que desde sintaxis 1.0 se escribe `t1.turno - 1`. Ejecuté `python3 tools/cli.py manual aritmetica`: exige espacios en `a - b`. `python3 tools/cli.py contexto --compacto` mostró `p.x`, `p`, `x` y aritmética infija. `python3 tools/sintaxis.py --verificar` informó `forma única: OK` y `bloques de documentación: 24 verificados · 8 declarados como gramática o fragmento`.

`python3 tools/cli.py --help` anuncia para `formatear`: «las líneas # no cuentan y se conservan». La ayuda no limita esa promesa a medida, caso o macro, y `formatear` acepta `.relacion`. `python3 tools/cli.py manual casos` mostró la distinción entre tabla y escape `fila {…}`.

Empaquetado: `UV_CACHE_DIR=/tmp/oracle-audit12-uv-cache uv build --out-dir /tmp/oracle-audit12-dist` falló al no poder consultar PyPI por DNS. `uv build --offline` falló por caché vacía. `uv build --no-build-isolation` sin `--python` no encontró setuptools en el intérprete elegido por uv. Ejecuté finalmente `UV_CACHE_DIR=/tmp/oracle-audit12-uv-cache uv build --python /usr/bin/python3 --no-build-isolation --out-dir /tmp/oracle-audit12-dist`: generó sdist y wheel 0.31.1. Eliminé el directorio `oracle_metalenguaje.egg-info` generado por ese build en el checkout.

Inspeccioné el wheel con `ZipFile`: en `plantilla_sensor_prosa/` hay 1 `.oracle`, 15 `.caso`, 1 `.relacion` y sólo el manifiesto `oracle.json`. Instalé el wheel en `/tmp/oracle-audit12-venv` con `pip install --no-index --no-deps`, ejecuté `oracle plantilla sensor-prosa /tmp/oracle-audit12-template` y luego `oracle test --rapido --proyecto /tmp/oracle-audit12-template`: `SINTAXIS OK · 1 medidas · 0 macros · 15 casos · 1 relaciones`; `VEREDICTO: VERDE`.

`python3 tools/cli.py test --rapido` sobre el repositorio informó `SINTAXIS OK · 63 medidas · 6 macros · 217 casos · 13 relaciones`, pero `VEREDICTO: ROJO (falló: cifras)` por `cifras vencidas en README.md`. No actualicé cifras: queda fuera del encargo y no afecta el hallazgo de comentarios.

## Tabla final

| Forma o punto | Estado en esta corrida | Evidencia ejecutada |
|---|---|---|
| Línea `#` completa en `.relacion` | **Hallazgo: contradicción entre especificación y código** | Tres posiciones rechazadas por cargador y `formatear`; LSP diagnostica. |
| Comentarios en medida, caso y macro | Excepción aplicada | Matriz: mismo texto sin comentarios, carga OK. |
| Espacios, versión, números, `requiere`, `agrupar`, resta sin espacios, paréntesis, CRLF, LF faltante, origen invertido, `fila` redundante, rama entrecomillada | Sólo lector puro o rechazo directo | Árbol igual cuando corresponde, impresor distinto y cargador rechaza. |
| Mayúsculas, BOM, `mas/menos/por/col`, comentario en línea de código, macro por argumentos | Rechazados | Matriz: error de lector y de cargador. |
| `ambito` opcional, dos `donde` frente a `y`, orden de campos | Canónicos o árboles distintos | Igualdad del impresor y comparación de árboles ejecutadas. |
| CLI, MCP y LSP sobre triple espacio; proyecto con medida o caso no impresos | Rechazan o diagnostican | `--leer`, `revisar`, `probar`, `expandir`, `test`, `juzgar`, `contexto`, `medida listar` y `caso listar` ejecutados; códigos y mensajes arriba. `formatear` propone la forma impresa. |
| JSON en `.json` | Intercambio admitido | Cuatro cargadores devolvieron los árboles originales. |
| Manual, contexto, nota histórica, documentación comprobada | Sin segunda enseñanza en las sondas | Comandos y salidas indicados; aclaración de la resta vigente. |
| Wheel y plantilla instalada | Superficie | Inventario del wheel y `test` verde de la plantilla. |
| `test --rapido` del repo | Sintaxis verde, corrida roja por cifras | Salidas exactas indicadas; no corregí README. |

**una sola sintaxis de escritura: no, porque la definición pública permite agregar líneas completas `#` también a relaciones `.relacion`, pero el cargador, el formateador y el LSP las rechazan.**
