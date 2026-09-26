# Sexta auditoría adversarial de la sintaxis de escritura

2026-09-26. Inspeccioné este checkout y ejecuté las sondas indicadas abajo. Los archivos de prueba se crearon en `TemporaryDirectory`; no cambié código ni hice commits. `git status --short` estaba vacío al comenzar.

## Veredicto

**una sola sintaxis de escritura: no, porque el LSP produce un `codeLens` semántico para medidas de superficie que su propio diagnóstico rechaza, y todavía hay instrucciones vigentes que presentan JSON como catálogo de medidas o como destino de un caso nuevo.**

## Hallazgos reproducidos

1. **LSP: `textDocument/codeLens` interpreta una medida fuera de la forma única.** Con `MEDIDA` de `tests.test_forma_unica_texto`, sustituí `medida demo.prueba:` por `medida   demo.prueba:` y, en otra sonda, LF por CRLF. `lsp.diagnosticar(Proyecto(temp), ruta, texto)` devolvió un diagnóstico en ambos casos; `lsp.lentes(...)` devolvió un lente en ambos, con `0 casos · SIN FIJAR · umbral <= 0 segun contrato`. El archivo no carga con `cargar_fuente_medida`. `tools/lsp.py:153-159` llama `leer_con_mapa` y construye `Medida` sin `error_forma`; el servidor despacha ese resultado para `textDocument/codeLens` en `:364-367`. Es aceptación y producción de información semántica por una entrada LSP, aunque el diagnóstico simultáneo avise el defecto.

2. **La receta `caso-observado` quedó corregida en código pero aún enseña un destino JSON.** El bloque ejecutable de `ejemplo/caso-observado/README.md:17-23` indica `.caso`; `:64` afirma «Se guarda como `<id>.json`, sin sobrescribir» al explicar cómo usarla con otra captura. Corrí el conversor con la captura y los metadatos de la receta: creó únicamente `<id>.caso`, `cargar_fuente_caso` devolvió el id y `tools.corpus.verificar` devolvió `[]`. Un destino `<id>.json` salió con código 1: `destino debe llamarse <id>.caso`. La instrucción editorial contradice el comportamiento y enseña una segunda forma para el caso nuevo.

3. **La guía del sensor de prosa aún propone catálogos JSON.** `docs/14-sensor-prosa.md:67` y `docs/14-sensor-prosa.html:47` dicen: «El catálogo puede ser otro directorio de medidas `.oracle` o canónicas JSON». Creé `catalogo/demo.prueba.json` con el árbol de `sintaxis.leer(MEDIDA)` y ejecuté `python3 ejemplo/sensor-prosa/sensor_prosa.py preparar --catalogo <temp>/catalogo --salida <temp>/salida`: código 0, `1 medidas preparadas; sin red`, y generó `lote.json`, `configuracion.json` y `solicitud-001.json`. El JSON de salida es un lote del sensor; el problema es la instrucción de usar JSON **como medida del catálogo**, no el formato de salida.

4. **Una ayuda de `tools/medida.py` da un ejemplo heredado de `.json`.** Su docstring, presentada como «Escribir una medida», muestra `python tools/medida.py <archivo.json> la revisa y la corre contra el corpus` en `:7`. Al ejecutar `python3 tools/medida.py --expandir` salió código 1 y `falta el archivo: --expandir <archivo.json>` (`:942`); `python3 tools/medida.py --expandir catalogos/meta/meta.donde_compone.oracle` salió código 0 y emitió el árbol interno JSON. La salida de expansión es legítima como representación interna; los argumentos de ayuda siguen usando JSON como archivo de medida. No ejecuté una revisión de `<archivo.json>` por esa herramienta y no atribuyo más comportamiento a ese ejemplo.

## Comandos y salidas recortadas

Los bloques `python3 - <<'PY'` ejecutados importaron `MEDIDA`, `AGRUPADA`, `CASO` y `RELACION` de `tests.test_forma_unica_texto`, escribieron cada variante con `Path.write_bytes(texto.encode())`, y llamaron a los lectores, cargadores y LSP. La tabla conserva las salidas relevantes:

```text
forma                         lector   --leer   cargador                         LSP diagnósticos
triple espacio                OK       rc 1     MedidaMalDeclarada: forma única  1
sintaxis 1.0 inicial          OK       rc 1     MedidaMalDeclarada: forma única  1
CRLF                          OK       rc 1     MedidaMalDeclarada: forma única  1
sin LF final                  OK       rc 1     MedidaMalDeclarada: forma única  1
contar(1e-3)                 OK       rc 1     MedidaMalDeclarada: forma única  1
clave(t) sin ; en caso        OK       —        CasoMalDeclarado: forma única    1
variante "inicio"             OK       —        RelacionMalDeclarada: forma     1
```

Para `--leer` corrí `python3 tools/sintaxis.py --leer <temp>/demo.oracle`; cada salida empezó `✗ ... fuera de la forma única`. En la misma sonda `mcp._medida_en_memoria({'texto': variante, 'formato': 'oracle'}, None)` rechazó el triple espacio con `ErrorHerramienta MEDIDA_INVALIDA — ... fuera de la forma única`. `_datos_de_macro` cargó `nucleo/macros/ninguno.oracle` y rechazó versiones CRLF y sin LF final con `MacroMalDeclarada: ... fuera de la forma única`. Así, las dos entradas defectuosas de la quinta auditoría no se reprodujeron en esas variantes.

```text
LSP lentes: MEDIDA canónica 1; triple espacio 1; CRLF 1
LSP diagnosticar: triple espacio 1; CRLF 1
cargar_fuente_medida: triple espacio y CRLF → MedidaMalDeclarada
```

Ejecuté una segunda sonda de lector → impresor → cargador sobre las filas anteriores que seguían abiertas en las auditorías 2–4:

```text
agregado antes de clave: lector OK, igual impresor False, cargador forma única
requiere a / requiere b después de umbral: lector OK, igual False, cargador forma única
ambito sin_declarar explícito: lector OK, igual False, cargador forma única
blanco final, espacio final, tab final: lector OK, igual False, cargador forma única
origen invertido: lector OK, igual False, cargador forma única
fila {"t": 0} para tabla simple: lector OK, igual False, cargador forma única
variante "inicio": lector OK, igual False, cargador forma única
comentario de línea completa: cargador OK
umbral sin segun: igual impresor True, cargador OK
umbral sin porque: igual impresor True, cargador OK
dos donde: igual impresor True, cargador OK
```

Probé `mas(1,2)`, `menos(1,2)` y `por(1,2)` en `resumen`: `ErrorSintaxis`, respectivamente en las columnas 18, 20 y 18. `col(p)` en ese **lugar de agregado** sí se lee y se imprime idéntico como `['resumen','col',['col','p']]`; no prueba que `col(p)` siga aceptado como forma funcional de acceso a campo en una expresión. No lo conté como segundo acceso a columna. Las mayúsculas y BOM ya fueron rechazados en la quinta auditoría; no los repetí aquí.

Ejecuté `json.dumps` de los árboles leídos en archivos `.json` temporales y los cuatro cargadores: `medida.json → list`, `caso.json → dict`, `relacion.json → list`, `macro.json → defmacro`. Es la lectura de intercambio permitida por el encargo; sólo la guía que **recomienda** un catálogo JSON se cuenta como hallazgo. Un recorrido de `catalogos`, `corpus`, `relaciones`, `nucleo/macros`, `perfiles` y `ejemplo` con sus cargadores produjo `96 .oracle`, `321 .caso`, `23 .relacion`, `0 errores`. El censo recorrió extensiones de superficie, no constituye prueba de ausencia de declaraciones JSON en otros árboles.

Además ejecuté:

```text
python3 tools/cli.py diagnostico → distribución 0.31.1, álgebra 1.0, sintaxis 1.0
python3 tools/cli.py contexto --compacto | rg 'a \+ b|mas\(' → aritmética: a + b · a - b · a * b ...
python3 tools/cli.py manual aritmetica | head → ARITMETICA — aritmética infija de expresiones
rg -n 'Se guarda como|canónicas JSON|archivo.json' docs/14-sensor-prosa.html ejemplo/caso-observado/README.md tools/medida.py → las cuatro ubicaciones citadas arriba
rg -n 'sintaxis.*1\.0|sintaxis MAYOR' ESPECIFICACION.md → versión vigente 1.0 y encabezado descrito en pasado
rg -n 'sintaxis.*1\.0' NOTAS-DE-RELEASE.md → sin coincidencias
```

La última búsqueda sólo constata una omisión de crónica de la versión; las notas históricas 0.x no las conté como una instrucción actual de autoría.

## Tabla final

| Forma o entrada | Estado observado | Evidencia |
|---|---|---|
| `tools/sintaxis.py --leer` con espacios, encabezado, CRLF o falta de LF | Cerrada para las sondas | Código 1 y `fuera de la forma única`. |
| Receta `caso-observado` | Código corregido; enseñanza abierta | Genera `.caso`, rechaza `.json`; README:64 aún ordena `<id>.json`. |
| LSP `textDocument/codeLens` con medida no impresa | **Abierta: entrada semántica alternativa** | `lsp.lentes` devuelve lente para triple espacio y CRLF; cargador y diagnóstico rechazan. |
| `docs/14-sensor-prosa` y HTML | **Abierta: catálogo JSON enseñado** | Prosa actual y comando `preparar` sobre medida JSON con rc 0. |
| Ayuda de `tools/medida.py` | **Abierta: ejemplo JSON de medida** | Docstring y mensaje de `--expandir` ejecutado. |
| `requiere` repetido, `agrupar` reordenado, número científico, variante entrecomillada, orden de `origen`, `clave(t)` sin `;`, `fila` redundante, espacios, CRLF | Sólo lector puro; cargadores rechazan | Lector OK; igualdad con impresor falsa y error de forma. |
| Comentarios completos | Excepción deliberada | Cargador OK; la comparación elimina esas líneas. |
| `umbral` sin campos opcionales, dos `donde`, escape `fila` cuando la tabla no representa datos | Estructuras canónicas | Ensayos de opciones y dos `donde` imprimen igual; el escape necesario consta en la quinta auditoría, no lo reejecuté con filas heterogéneas. |
| JSON `.json` de medida, caso, relación y macro | Intercambio admitido | Cuatro cargadores ejecutados; no es hallazgo por sí mismo. |
| MCP con medida no impresa; macro CRLF/sin LF | Cerradas para las sondas | `ErrorHerramienta` y `MacroMalDeclarada`. |
| Notas de sintaxis 1.0 | Omisión editorial | `diagnostico` da 1.0; búsqueda sin coincidencias en notas. |

**una sola sintaxis de escritura: no, porque `codeLens` interpreta medidas que el proyecto no admite y aún se enseña JSON como catálogo de medidas y como destino de un caso nuevo.**
