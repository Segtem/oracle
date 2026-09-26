# Quinta auditoría adversarial de la sintaxis de escritura

2026-09-26. Ejecutada en este checkout, con archivos de prueba en directorios temporales. No cambié código ni hice commits. La nota de la tarea menciona `AUDITORIA-4.md`, pero `cat tareas/20260926-023437-una-sintaxis/AUDITORIA-4.md` devolvió `No such file or directory` y `rg --files tareas | rg 'AUDITORIA(-4)?\.md$|AUDITORIA-4'` no lo encontró. Por eso repetí los puntos abiertos documentados en `AUDITORIA-2.md` y `AUDITORIA-3.md`, y los que la nota atribuye a la cuarta; no atribuyo filas no visibles a ese informe ausente.

## Hallazgos

1. **Una utilidad pública sigue aceptando grafías no impresas.** `python3 tools/sintaxis.py --leer <archivo.oracle>` usa `leer_con_mapa` directamente y emite JSON sin exigir `error_forma`. En mis pruebas devolvió código 0 y un árbol `["medida",...]` para `medida   demo.prueba:`, para un encabezado `sintaxis 1.0`, para CRLF y para un archivo sin LF final. `oracle formatear` pidió formato para la primera variante, y los cargadores la rechazaron. No es un cargador de proyecto ni una recomendación de escribir JSON, pero sí es una entrada del paquete que acepta como medida un texto de superficie que el impresor no escribe. Su docstring además presenta `--leer medida.oracle` como operación de la utilidad.

2. **Un ejemplo del repositorio enseña y produce casos JSON de autoría.** `ejemplo/caso-observado/README.md:19-23,35,69` manda generar `<id>.json` en `corpus/`, leerlo como caso y repetir la receta para otra captura. `ejemplo/caso-observado/convertir.py` exige el sufijo `.json` y escribe `json.dumps(datos, ...)`. Lo ejecuté con la captura y metadatos que indica el README: creó `corpus/494-la-cota-de-la-sombra-observada-por-el-recorrido.json`, `cargar_fuente_caso` devolvió ese id y `tools.corpus.verificar` devolvió `[]`. Esto contradice la distinción declarada entre JSON de intercambio y superficie de autoría. Los metadatos también se escriben en JSON, como parte del caso que termina en el corpus.

3. **La especificación promete más de lo que hacen todas las entradas.** `ESPECIFICACION.md:56-68,530-570` dice que desde 1.0 cualquier otra grafía no carga y que Oracle no produce JSON de medidas, casos o relaciones. Las dos ejecuciones anteriores refutan esa formulación sin necesidad de contar como hallazgo los `.json` aceptados para intercambio. `NOTAS-DE-RELEASE.md` aún abre con 0.31.1 y declara sintaxis 0.7 en sus tres cortes más recientes; no encontré allí una sección de sintaxis 1.0 (`rg -n 'sintaxis.*1\.0' NOTAS-DE-RELEASE.md` no dio coincidencias). Esto es una omisión editorial de esta versión, no por sí solo otra grafía enseñada. Sus menciones a `mas(...)` están en la crónica de 0.30.0, con el tiempo pasado explícito.

## Comandos ejecutados y salidas recortadas

Los bloques Python son extractos fieles de las sondas ejecutadas; `MEDIDA`, `AGRUPADA`, `CASO` y `RELACION` vienen de `tests.test_forma_unica_texto`. Cada ruta escrita por las sondas fue temporal.

### Variantes de las auditorías anteriores

Ejecuté `leer`/`imprimir`, el cargador del tipo de archivo y `tools.lsp.diagnosticar` para variantes de esos cuatro textos:

```python
from tests.test_forma_unica_texto import MEDIDA, AGRUPADA, CASO, RELACION
# Para cada variante: lector(texto); sin_comentarios(texto) == impresor(datos);
# Path(temp).write_bytes(texto.encode()); cargar_fuente_*(Path(temp));
# diagnosticar(Proyecto(raiz), Path(temp), texto)
```

```text
forma                         lector  igual impresor  cargador                         LSP
sintaxis 1.0 inicial         OK      False           MedidaMalDeclarada: forma única   1
triple espacio en encabezado OK      False           MedidaMalDeclarada: forma única   1
contar(1e-3)                 OK      False           MedidaMalDeclarada: forma única   1
agregado antes de clave      OK      False           MedidaMalDeclarada: forma única   1
requiere en dos líneas       OK      False           MedidaMalDeclarada: forma única   1
origen en otro orden         OK      False           CasoMalDeclarado: forma única     1
clave(t) sin ;              OK      False           CasoMalDeclarado: forma única     1
variante "inicio"           OK      False           RelacionMalDeclarada: forma única 1
```

`forma única` resume `fuera de la forma única` de cada excepción; `1` es la cantidad de diagnósticos, no una evaluación positiva. Con `cargar_fuente_medida` y `diagnosticar` repetí además:

```text
CRLF: rechazo por forma, LSP 1
sin LF final: rechazo por forma, LSP 1
línea blanca inicial: rechazo por forma, LSP 1
espacio final: rechazo por forma, LSP 1
comentario de línea completa: OK, LSP 0
BOM: rechazo por sintaxis, LSP 1
```

Para macro, leí `nucleo/macros/ninguno.oracle`: `_datos_de_macro` dio `OK`, LSP 0; al quitar el LF final, dio `MacroMalDeclarada: fuera de la forma única`, LSP 1. Para MCP ejecuté `_medida_en_memoria({'texto': texto, 'formato': 'oracle'}, macros_base())`: la medida canónica dio `OK`; triple espacio y CRLF dieron `ErrorHerramienta: fuera de la forma única`.

Ejecuté otras sustituciones con `nucleo.sintaxis.leer` e `imprimir`:

```text
mas(1,2)   ErrorSintaxis: escribí a + b
menos(1,2) ErrorSintaxis: escribí a - b
por(1,2)   ErrorSintaxis: escribí a * b
col(p)     ErrorSintaxis: escribí p en vez de col(p)
MEDIDA ... ErrorSintaxis: se esperaba encabezado
umbral ... porque "r" segun contrato: ErrorSintaxis: se esperaba fin de línea
umbral sin segun: igual al impresor True
umbral sin porque: igual al impresor True
requiere pieza, modulo: igual al impresor True
ambito sin_declarar: igual al impresor False (el impresor lo omite)
dos donde: igual al impresor True; impresor conserva dos pasos
```

En el caso de prueba, `caso.leer(CASO)` y `caso.leer(caso.imprimir(caso.leer(CASO)))` dieron el mismo árbol; el `fila {"t": 0}` original **no** era igual al impresor, que produjo `paso: clave(t); t` seguido de la fila `0`. Por tanto el escape aún es legible para una tabla simple, pero el cargador rechaza esa grafía. La variante `fila {...}` sigue siendo salida necesaria del impresor para filas heterogéneas; esa coexistencia depende de los datos, no mostró dos textos guardables del mismo árbol. `relacion.imprimir(relacion.leer(RELACION)) == RELACION` dio `True`.

### Entradas públicas y generadores

Creé un proyecto temporal con `python3 tools/cli.py init <tmp>`, escribí `MEDIDA` con triple espacio en `catalogos/demo.prueba.oracle` y evidencia `{}` en `hechos.json`. Ejecuté:

```text
python3 tools/cli.py test --rapido --proyecto <tmp>
  rc 1; SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
python3 tools/cli.py juzgar --proyecto <tmp> --con <tmp>/hechos.json
  rc 2; ERROR AL EVALUAR — ...demo.prueba.oracle: fuera de la forma única
python3 tools/cli.py medida probar <archivo> --con <hechos> --proyecto <tmp>
  rc 1; ...fuera de la forma única
python3 tools/cli.py revisar <archivo> --con <hechos> --proyecto <tmp>
  rc 1; ...fuera de la forma única
python3 tools/cli.py expandir <archivo> --proyecto <tmp>
  rc 1; MedidaMalDeclarada: ...fuera de la forma única
python3 tools/cli.py contexto --compacto --proyecto <tmp>
  rc 0; ⚠ no se pudo cargar el catálogo — MedidaMalDeclarada: ...fuera de la forma única
python3 tools/cli.py caso generar demo.prueba --proyecto <tmp>
  rc 1; MedidaMalDeclarada: ...fuera de la forma única
python3 tools/cli.py censar --proyecto <tmp>
  rc 0; NO SE PUDO CENSAR — MedidaMalDeclarada: ...fuera de la forma única
python3 tools/cli.py formatear <archivo> --proyecto <tmp>
  rc 0; ...requiere formato
```

`censar` devuelve 0 aunque informa que no pudo censar; no conté eso como aceptación de la medida. Una primera corrida de `juzgar` en un proyecto que también contenía los andamios de `nueva` dio error de sintaxis por `SEGUN` de ese andamio; repetí en un proyecto limpio para aislar la prueba anterior. También ejecuté `mutar --rapido` vía `tools/cli.py`: respondió `subcomando desconocido: mutar`, de modo que no atribuyo a ese comando ningún resultado de forma única.

Volqué con `json.dumps` los árboles leídos de `MEDIDA`, `CASO` y `RELACION` a tres archivos `.json` temporales y ejecuté respectivamente `cargar_fuente_medida`, `cargar_fuente_caso` y `cargar_fuente_relacion`: `medida JSON OK list`, `caso JSON OK dict`, `relacion JSON OK list`. Volqué además una macro empaquetada a `ninguno.json`: `_datos_de_macro` devolvió `defmacro`. `cargar_fuente_relacion` sobre el mismo árbol JSON guardado como `.oracle` dio `RelacionMalDeclarada: una relación se escribe en .relacion`. Ejecuté también `sintaxis.leer` sobre una invocación de `ninguno` con las líneas `relacion`, `alias`, `predicado`, `porque`, `segun`: dio `ErrorSintaxis: la invocación de macro se escribe con las cláusulas de su plantilla`.

Ejecuté `init`, `nueva demo.prueba`, `caso nuevo demo/001-prueba` y `biblioteca nueva demo.biblio <tmp>/biblioteca`: los cuatro dieron rc 0; entre los archivos generados observé `oracle.json`, `.oracle` y `.caso`. No observé JSON de medida/caso por esos cuatro generadores. `python3 tools/cli.py diagnostico` informó `distribucion: 0.31.1`, `algebra: 1.0`, `sintaxis: 1.0`. `python3 tools/cli.py contexto --compacto` mostró `p.x`, `p`, `x` y `a + b · a - b · a * b`; `python3 tools/cli.py manual aritmetica` encabezó `ARITMETICA — aritmética infija de expresiones`.

Ejecuté `python3 tools/cli.py plantilla sensor-prosa <tmp>/sensor`: rc 0; el censo de archivos generados fue `15 .caso`, `1 .oracle`, `1 .relacion`, `1 .json` y otros recursos; el `.json` no estaba dentro de `catalogos`, `corpus` ni `relaciones`. Ejecuté `python3 -m unittest tests.test_relaciones_por_revisar -q`: `Ran 17 tests ... OK`, incluida la prueba de `relaciones --escribir`; esto verifica esa ruta por el test, no equivale a observar manualmente cada borrador. Para `convertir`, creé un proyecto temporal válido con una medida JSON y otra `.oracle`: `python3 tools/cli.py convertir <m.json> --proyecto <tmp>` dio rc 0 y empezó con `medida demo.prueba:`; el mismo comando con `<m.oracle>` dio rc 1 y `esperaba una medida .json para convertir a superficie`. Un primer intento sin `oracle init` devolvió `PROYECTO INVÁLIDO`; lo repetí con proyecto válido para aislar la conducta de conversión.

### Dos vías que siguen abiertas

Con un `.oracle` temporal de triple espacio ejecuté:

```text
python3 tools/sintaxis.py --leer <tmp>/m.oracle
  rc 0; ["medida","demo.prueba",["desde",["de","pieza","p"]],...]
python3 tools/cli.py formatear <tmp>/m.oracle
  .../m.oracle: requiere formato
```

Repetí `--leer` con `sintaxis 1.0` inicial, CRLF y sin LF final: los tres dieron rc 0 y salida que empieza `["medida"`; con BOM dio rc 1 y `se esperaba encabezado`. La inspección ejecutada con `sed -n '280,310p' tools/sintaxis.py` mostró que esta rama llama `leer_con_mapa`, comprueba sólo compatibilidad de versión e imprime `json.dumps(datos)`.

Ejecuté exactamente la receta de `ejemplo/caso-observado/README.md` con destino temporal:

```text
mkdir <tmp>/corpus
python3 ejemplo/caso-observado/convertir.py \
  observaciones/2026-09-09-aceptacion/evidencia.json \
  ejemplo/caso-observado/metadatos.json \
  <tmp>/corpus/494-la-cota-de-la-sombra-observada-por-el-recorrido.json
  rc 0
find <tmp> -type f -printf '%P\n'
  corpus/494-la-cota-de-la-sombra-observada-por-el-recorrido.json
cargar_fuente_caso(<archivo>)['id']
  494-la-cota-de-la-sombra-observada-por-el-recorrido
tools.corpus.verificar(<tmp>/corpus)[0]
  []
```

### Revisión de enseñanza

Ejecuté `rg -n 'sintaxis [0-9]|\.oracle.*\.json|\.json.*\.oracle|mas\(|menos\(|por\(|col\(' README.md ESPECIFICACION.md NOTAS-DE-RELEASE.md docs ejemplo perfiles nucleo/macros tools`, `rg -n 'caso.*\.json|\.json.*caso' ejemplo README.md docs ESPECIFICACION.md --glob '*.md'`, `sed` de `README.md:595-615`, `docs/03-escribir-una-medida.md:95-115`, `ESPECIFICACION.md:50-70,530-575`, `NOTAS-DE-RELEASE.md:1-160`, `ejemplo/caso-observado/README.md` y `tools/sintaxis.py:265-325`. Salidas decisivas:

```text
README: corpus en .caso; oracle nueva crea .oracle; JSON para intercambio y migración.
docs/03: Escribí medidas en .oracle, casos en .caso y relaciones en .relacion.
ESPECIFICACION: el texto válido es exactamente el que escribe el impresor;
  no los enseña ni los produce [JSON de medidas, casos o relaciones].
ejemplo/caso-observado/README: destino .../corpus/<id>.json; Se guarda como <id>.json.
tools/sintaxis.py: uso: python tools/sintaxis.py --leer <medida.oracle>
NOTAS-DE-RELEASE: VERSION_SINTAXIS 0.7 → 0.7 en los cortes 0.31.1 y 0.31.0.
```

No inferí que una mención histórica de JSON o de `mas()` sea una instrucción vigente de autoría. Tampoco conté los archivos `.json` leídos por los cargadores como defecto por sí mismos: el encargo los permite expresamente para intercambio. Las búsquedas fueron sobre los árboles y documentos enumerados, no una prueba de ausencia en un wheel instalado.

## Tabla final

| Forma o entrada | Estado en esta corrida | Evidencia |
|---|---|---|
| Encabezado de versión, espacios, científica, orden de `agrupar`, `requiere` repetido, `ambito sin_declarar` | Compatibilidad del lector puro; rechazadas al cargar | `leer` OK e igualdad falsa; cargadores y LSP rechazaron/diagnosticaron las variantes medidas arriba. |
| Orden de `origen`, `clave(t)` sin `;`, variante entrecomillada, escape `fila` para tabla simple | Compatibilidad del lector puro; rechazadas al cargar | Sondas de caso/relación e impresores; cargadores dieron `fuera de la forma única`. |
| CRLF, LF final ausente, blanco, espacio final; BOM | Cerradas en cargadores | Rechazos de cargador y diagnóstico LSP; BOM falló ya en el lector. |
| Comentario de línea completa | Excepción documentada | Cargador OK, LSP 0; `sin_comentarios` lo elimina de la comparación. |
| Dos `donde` frente a uno con `y`; `umbral` con campos opcionales | Estructuras canónicas distintas | El impresor conservó dos `donde` y las opciones de umbral ensayadas. |
| `mas`, `menos`, `por`, `col`, mayúsculas, orden inverso de umbral | Cerradas | Seis rechazos del lector con mensajes citados. |
| Invocación de macro por argumentos; relación JSON en `.oracle` | Cerradas | `ErrorSintaxis` con instrucción de plantilla; `RelacionMalDeclarada` con extensión `.relacion`. |
| MCP, LSP, `test`, `juzgar`, `medida probar`, `revisar`, `expandir`, `contexto`, `caso generar`, `censar` | Cerradas para las variantes ensayadas | Errores de forma o diagnósticos; `censar` informó error aunque rc 0. |
| `tools/sintaxis.py --leer` | **Abierta: entrada no canónica** | rc 0 y árbol JSON para triple espacio, versión inicial, CRLF y falta de LF. |
| `ejemplo/caso-observado` | **Abierta: autoría JSON enseñada y producida** | Receta ejecutada: caso `.json` en `corpus/` que carga y verifica. |
| JSON `.json` leído por cargadores | Permitido como intercambio | No se contó como hallazgo sin instrucción de autoría. |
| `convertir`, plantilla sensor-prosa, borradores de relaciones | Cerradas para lo ejecutado | `convertir` emitió superficie desde JSON; plantilla generó declaraciones de superficie; 17 pruebas de borradores OK. |
| Notas de release de sintaxis 1.0 | Omisión editorial | `diagnostico` da 1.0; notas todavía enumeran 0.7 y no contienen sección 1.0. |

**Veredicto: una sola sintaxis de escritura: no, porque la receta `caso-observado` enseña y produce un caso JSON de corpus y `tools/sintaxis.py --leer` acepta medidas `.oracle` distintas de las del impresor.**
