# Octava auditoría adversarial: una sintaxis

2026-09-26. Ejecuté las sondas indicadas desde este checkout. Los proyectos y archivos de prueba se crearon con `TemporaryDirectory` o bajo `/tmp`; no cambié código ni hice commits. `git status --short` estaba vacío antes de escribir este informe.

## Hallazgos nuevos

Comando de reproducción que ejecuté para los dos órdenes de casos (la salida detallada de cada cabecera figura abajo):

```bash
python3 - <<'PY'
from tests.test_forma_unica_texto import CASO
from nucleo import caso
from nucleo.caso import cargar_fuente_caso
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
base = caso.leer(CASO)
for modo in ('relaciones', 'columnas'):
    a = deepcopy(base)
    a['evidencia'] = {'a': [{'x': 1, 'y': 2}], 'b': [{'u': 3}]} if modo == 'relaciones' else {'a': [{'x': 1, 'y': 2}]}
    b = deepcopy(a)
    if modo == 'relaciones':
        b['evidencia'] = dict(reversed(list(b['evidencia'].items())))
    else:
        b['evidencia']['a'][0] = dict(reversed(list(b['evidencia']['a'][0].items())))
    textos = [caso.imprimir(d) for d in (a, b)]
    with TemporaryDirectory() as td:
        for i, t in enumerate(textos):
            p = Path(td) / f'{i}.caso'; p.write_text(t)
            print(modo, i, cargar_fuente_caso(p)['id'], caso.imprimir(caso.leer(t)) == t)
    print(modo, 'textos distintos', textos[0] != textos[1], 'datos iguales', a == b)
PY
```

Salida: `relaciones 0/1 001-demo True`, `relaciones textos distintos True datos iguales True`, `columnas 0/1 001-demo True`, `columnas textos distintos True datos iguales True`.

### 1. Dos órdenes canónicos para las relaciones de evidencia de un caso

Ejecuté esta sonda con `CASO` de `tests.test_forma_unica_texto`, `nucleo.caso.leer/imprimir` y `cargar_fuente_caso`: agregué dos relaciones `a` y `b` al diccionario `evidencia`, imprimí el caso, invertí sólo el orden de inserción, imprimí de nuevo y guardé ambos textos como `.caso` temporales. Salida recortada:

```text
evidencia 0 carga 001-demo idempotente True
evidencia 1 carga 001-demo idempotente True
evidencia textos distintos True datos equivalentes True
cabeceras ['a: x, y', 'b: u'] ['b: u', 'a: x, y']
```

`caso.imprimir` recorre `datos["evidencia"].items()` sin fijar un orden (`nucleo/caso.py:521`). El lector conserva el orden encontrado. Son dos archivos distintos, aceptados por el cargador y devueltos sin cambios por el impresor, para diccionarios que comparan iguales. El arreglo de `origen` no cubre este campo.

### 2. Dos órdenes canónicos para las columnas de una fila

En la misma sonda dejé una relación `a` con una fila `{"x": 1, "y": 2}`; después invertí sólo el orden de inserción de las claves de esa fila. Salida:

```text
campos_fila 0 carga 001-demo idempotente True
campos_fila 1 carga 001-demo idempotente True
campos_fila textos distintos True datos equivalentes True
cabeceras ['a: x, y'] ['a: y, x']
```

`_lineas_relacion` obtiene las columnas de `hechos[0].keys()` (`nucleo/caso.py:171`). Las dos tablas se leen, cargan y se imprimen idénticas a sí mismas; las filas son diccionarios iguales. No afirmo que el orden de filas o de campos de una declaración `.relacion` sea semánticamente irrelevante: esta prueba invirtió sólo claves de un diccionario de evidencia.

Probé también tres posiciones para un objeto JSON anidado con claves `x,y` y `y,x`: valor de `origen.extra`, valor de una celda `v` de tabla y valor de `v` en una fila que obliga al escape `fila {...}`. Para cada posición ejecuté `caso.imprimir`, guardé ambos textos `.caso`, llamé al cargador y repetí `imprimir(leer(texto))`. Salida:

```text
origen_valor different True equal True load roundtrip [True, True]
celda_objeto different True equal True load roundtrip [True, True]
fila_escape different True equal True load roundtrip [True, True]
```

Así, ordenar las relaciones y las columnas de tabla por sí solo no bastaría para el invariante fuerte; los objetos JSON anidados también conservan el orden de entrada al imprimirse.

### 3. El manual activo enseña una grafía que el cargador rechaza

Comandos ejecutados:

```bash
python3 tools/cli.py manual aritmetica | head -12
rg -n 'sin espacios|a-b' tools/manual.py docs/manual.html ESPECIFICACION.md | head
```

Salida recortada:

```text
ARITMETICA — aritmética infija de expresiones
  a - b        resta, también sin espacios (a-b). En expresiones el guion siempre es resta
tools/manual.py:120: ("a - b", "resta, también sin espacios (a-b). "
docs/manual.html:134: <dt>a - b</dt><dd>resta, también sin espacios (a-b).
ESPECIFICACION.md:124: ... aun sin espacios (`t1.turno-1`, `a.x-a.y`).
```

Ejecuté `leer` y `cargar_fuente_medida` sobre `MEDIDA.replace('contar(1)', 'contar(p.x-1)')`, guardada como `.oracle` temporal:

```text
lector OK igual impresor False impreso     resumen contar(p.x - 1)
cargador MedidaMalDeclarada True   # contiene «fuera de la forma única»
```

El manual y su HTML son referencia vigente, así que enseñan una segunda grafía de expresión, aunque el cargador de proyecto la rechace. El párrafo de `ESPECIFICACION.md:124` describe la sintaxis histórica 0.7; lo consigno como contexto editorial, no como otro productor ejecutado.

## Reejecución en contra de los puntos abiertos de AUDITORIA-2 a AUDITORIA-7

Ejecuté una sonda Python con `MEDIDA`, `AGRUPADA`, `CASO` y `RELACION` de `tests.test_forma_unica_texto`: para cada variante llamé al lector, comparé con el impresor, escribí bytes en un archivo temporal, llamé al cargador y a `lsp.diagnosticar/lentes`. `CASO` se normalizó primero con su impresor para probar cambios sobre una base canónica. Salida recortada (`diag/lens` son cantidades):

```text
variante                  lector  igual  cargador                    diag/lens
triple espacio            OK      False  MedidaMalDeclarada forma     1/0
version inicial           OK      False  MedidaMalDeclarada forma     1/0
cientifica                OK      False  MedidaMalDeclarada forma     1/0
requiere repetido         OK      False  MedidaMalDeclarada forma     1/0
agregado antes de clave   OK      False  MedidaMalDeclarada forma     1/0
ambito explicito          OK      False  MedidaMalDeclarada forma     1/0
CRLF                      OK      False  MedidaMalDeclarada forma     1/0
sin LF                    OK      False  MedidaMalDeclarada forma     1/0
blanco final              OK      False  MedidaMalDeclarada forma     1/0
espacio final             OK      False  MedidaMalDeclarada forma     1/0
tab final                 OK      False  MedidaMalDeclarada forma     1/0
origen invertido          OK      False  CasoMalDeclarado forma       1/0
fila redundante           OK      False  CasoMalDeclarado forma       1/0
clave sin punto y coma    OK      False  CasoMalDeclarado forma       1/0
variante comillas         OK      False  RelacionMalDeclarada forma   1/0
```

Así se reproduce el cierre de la inversión de `origen` de AUDITORIA-7. La sonda de `clave` usó el escape `fila`, donde el lector admite tanto `clave(t)` como `clave(t);`; el impresor eligió tabla y el cargador rechazó ambos escapes redundantes. También ejecuté:

```text
comentario completo al principio → cargar_fuente_medida: medida
mas(1,2), menos(1,2), por(1,2), col(p) → ErrorSintaxis cada uno
MEDIDA mayúscula y BOM → ErrorSintaxis cada uno
dos donde, umbral sin segun, umbral sin porque → igual al impresor True cada uno
MCP con encabezado de triple espacio → ErrorHerramienta, «fuera de la forma única»
macro empaquetada canónica → defmacro
macro con CRLF / sin LF final → MacroMalDeclarada, «fuera de la forma única»
```

`dos donde` conserva dos pasos en el árbol; no es el mismo árbol que un solo `donde` con `y`. La ausencia de cláusulas opcionales de umbral también se conserva. El comentario de línea completa sigue siendo la excepción intencional de `sin_comentarios`: hay textos guardables distintos del impresor por esa regla, pero no es una segunda gramática de declaraciones.

Para los otros puntos abiertos de AUDITORIA-2 ejecuté otra sonda Python con los cuatro árboles de esos fixtures, `json.dumps`, los cuatro cargadores y `oracle convertir`: guardé cada árbol en un `.json` temporal, y en un caso cambié `evidencia` a `{'a': [{'x': 1}, {'y': 2}]}` antes de imprimirlo. Salida:

```text
heterogeneo usa fila 2 carga 001-demo ida vuelta True
intercambio medida medida
intercambio caso dict
intercambio relacion relacion
intercambio macro defmacro
relacion .oracle RelacionMalDeclarada una relación se escribe en .relacion
convertir JSON rc 0 primera medida demo.prueba:
```

El escape `fila {...}` es necesario para filas heterogéneas; en ese caso se imprime y carga sin divergencia. La aceptación de `.json` por los cuatro cargadores es el intercambio permitido. `convertir` emitió superficie, y una relación en `.oracle` fue rechazada.

Ejecuté además, en un proyecto temporal inicializado con `python3 tools/cli.py init <tmp>`, una medida de encabezado con triple espacio:

```text
python3 tools/sintaxis.py --leer <tmp>/demo.oracle → rc 1, fuera de la forma única
python3 tools/cli.py formatear <tmp>/demo.oracle → rc 0, requiere formato
python3 tools/cli.py test --rapido --proyecto <tmp> → rc 1, SINTAXIS ✗, fuera de la forma única
python3 tools/cli.py juzgar --con <tmp>/hechos.json --proyecto <tmp> → rc 2, fuera de la forma única
```

Para la receta de `ejemplo/caso-observado` ejecuté `python3 ejemplo/caso-observado/convertir.py observaciones/2026-09-09-aceptacion/evidencia.json ejemplo/caso-observado/metadatos.json <tmp>/494-la-cota-de-la-sombra-observada-por-el-recorrido.{caso,json}` por separado. Salida: `.caso rc 0 existe True`; `.json rc 1 existe False: destino debe llamarse <id>.caso`.

Ejecuté `lsp.completar` sobre texto incompleto que termina en `umbral <= 0 segun `, con encabezado normal y con triple espacio: ambas vistas devolvieron `contrato`, `convencion`, `medicion`, `tanteo`. Sigue la asistencia sobre un borrador incompleto observada en AUDITORIA-7; no demuestra carga de una medida completa. En cambio, la sonda de arriba dio diagnóstico y cero lentes para las medidas completas fuera de forma.

## Materiales, wheel y plantilla instalada

Ejecuté:

```bash
python3 tools/cli.py contexto --compacto | rg -n 'accesores:|aritmética:|mas\('
python3 tools/cli.py --help | rg -n 'convertir|formatear|nueva|plantilla'
python3 tools/medida.py --expandir
rg -n 'demo\.instalado\.json|relaciones/item\.json|dominio\.lo_que_falta\.json|<id>\.json|archivo\.json|canónicas JSON|El catálogo puede' tools ejemplo docs README.md ESPECIFICACION.md --glob '*.py' --glob '*.md' --glob '*.html'
rg -n 'sintaxis.*1\.0' NOTAS-DE-RELEASE.md
```

Salidas recortadas: `contexto` mostró `p.x`, `p`, `x` y `a + b · a - b · a * b`; la ayuda de CLI dice que `convertir` migra JSON a superficie y que `formatear` normaliza; `medida.py` pidió `<archivo.oracle>`. La búsqueda de las rutas antiguas no encontró los ejemplos JSON de `observar.py` ni `verificar_instalacion.py`; el HTML de sensor-prosa mostró catálogo `.oracle`. Las menciones JSON restantes de esa búsqueda fueron intercambio, `oracle.json`, evidencia o metadatos. La búsqueda exacta de sintaxis 1.0 en `NOTAS-DE-RELEASE.md` no devolvió líneas: continúa una omisión de crónica, no una segunda forma ejecutable.

Construí el paquete con el comando pedido. El primer intento, `uv build --no-build-isolation --out-dir /tmp/oracle-audit8-dist`, falló al intentar escribir la caché bajo `/home/workstation`; con `UV_CACHE_DIR=/tmp/oracle-audit8-uv-cache` y `--no-build-isolation` falló por `ModuleNotFoundError: setuptools` en el Python elegido por uv. Un intento de `uv build` aislado con esa caché falló al resolver `setuptools>=68` por DNS. El comando ejecutado que sí construyó el wheel fue:

```bash
UV_CACHE_DIR=/tmp/oracle-audit8-uv-cache uv build --no-build-isolation --python /usr/bin/python3 --out-dir /tmp/oracle-audit8-dist
```

Salida final: `Successfully built ...oracle_metalenguaje-0.31.1-py3-none-any.whl`. Abrí el wheel con `zipfile.ZipFile` y conté `plantilla_sensor_prosa/`: 15 `.caso`, 1 `.relacion`, 1 `.oracle`, 1 `oracle.json`; no apareció un JSON declarativo en `catalogos/`, `corpus/`, `relaciones/` ni `macros/` del wheel. El README empaquetado usa `.caso` para leer el caso y escribe `hechos-construidos.json` como evidencia.

Instalé ese wheel en `/tmp/oracle-audit8-venv` y ejecuté:

```bash
/tmp/oracle-audit8-venv/bin/oracle plantilla sensor-prosa /tmp/oracle-audit8-plantilla
/tmp/oracle-audit8-venv/bin/oracle test --rapido --proyecto /tmp/oracle-audit8-plantilla
```

La copia salió con rc 0. Enumeré los archivos instalados: 15 `.caso`, 1 `.relacion`, 1 `.oracle`, 1 `oracle.json`; las superficies empiezan `caso`, `relacion` y `medida` respectivamente. El `test --rapido` salió rc 0: `CORPUS OK · 15 casos`, `SINTAXIS OK · 1 medidas · 0 macros · 15 casos · 1 relaciones`, `VEREDICTO: VERDE`. Esto verifica la plantilla instalada; no ejecuté `tools/verificar_instalacion.py` completo.

## Tabla final

| Forma o punto | Estado en esta corrida | Evidencia |
|---|---|---|
| Orden de `origen` | Cerrado | Invertir `repo` y `commit`: impresor lo normalizó; cargador y LSP lo rechazaron. |
| Orden de relaciones en `evidencia` | **Hallazgo: dos textos canónicos** | Ambos `.caso` cargaron, se reimprimieron idénticos y sus diccionarios compararon iguales. |
| Orden de columnas de una fila de evidencia | **Hallazgo: dos textos canónicos** | `a: x, y` y `a: y, x` cargaron y se reimprimieron idénticos para filas equivalentes. |
| Orden de claves de objetos anidados en un caso | **Hallazgo: dos textos canónicos** | Origen, celda y fila de escape: dos textos distintos por posición; tres pares cargaron y reimprimieron idénticos. |
| Resta sin espacios `a-b` | **Hallazgo: segunda grafía enseñada** | Manual de CLI y HTML la enseñan; `leer` OK, impresor agrega espacios y cargador rechaza. |
| Version inicial, espacios, científica, `requiere`, `agrupar`, `ambito`, CRLF, LF ausente, blanco, espacio o tab final | Sólo lectores puros | Impresor diferente; cargador rechazó y LSP dio diagnóstico sin lente. |
| `fila` redundante, `clave` sin `;`, variante entrecomillada | Sólo lectores puros | Lector OK; impresor diferente; cargador rechazó. |
| Comentarios, dos `donde`, umbral opcional | Excepción o estructuras propias | Comentario cargó; las otras sondas fueron idénticas a su impresión. |
| Escape `fila` para datos heterogéneos | Canónico cuando hace falta | Dos `fila`, carga e ida y vuelta idéntica. |
| Aritmética funcional, `col`, mayúsculas, BOM; MCP y macro no canónicos | Rechazados | Errores ejecutados arriba. |
| JSON `.json` de medida, caso, relación y macro; `convertir` | Intercambio permitido | Cuatro cargadores aceptaron; `convertir` emitió `medida demo.prueba:`. |
| `tools/sintaxis.py --leer`, `test`, `juzgar`; receta `caso-observado` | Cerrados para las variantes probadas | Rechazos de forma o destino JSON; `.caso` producido. |
| LSP completion sobre borrador no canónico | Asistencia pendiente de decidir | Ofreció las mismas cuatro opciones; el texto estaba incompleto. |
| `observar.py`, `verificar_instalacion.py`, sensor-prosa y ayuda `medida.py` | Cerrados para la enseñanza/producción revisada | Búsquedas, ayuda ejecutada, wheel construido, plantilla copiada y `test --rapido` verde. |
| JSON `.json` de intercambio y `oracle.json` | Permitidos por el encargo | El wheel contiene `oracle.json`; el README de la plantilla genera evidencia JSON. No los conté como declaraciones de autoría. |

**una sola sintaxis de escritura: no, porque casos con órdenes distintos de relaciones, columnas y claves de objetos anidados pasan como canónicos para datos equivalentes, y el manual activo enseña la resta sin espacios que el cargador rechaza.**
