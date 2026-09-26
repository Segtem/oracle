# Séptima auditoría adversarial: una sintaxis

2026-09-26. Checkout de esta tarea. Revisé las tablas de `AUDITORIA-2.md` a `AUDITORIA-6.md` y ejecuté las sondas que se detallan abajo. Las pruebas que escribieron archivos usaron `TemporaryDirectory`. No cambié código ni hice commits. `git status --short` salió vacío al inicio.

## Hallazgos

1. **Ejemplo de plan de observación que enseña una medida JSON.** `tools/observar.py:32-49` presenta un bloque `json` bajo «El plan» con `"medida": "medidas/catalogos/dominio/dominio.lo_que_falta.json"`. Es una instrucción de autoría vigente en el docstring de una herramienta, no una descripción del árbol interno. Ejecuté `python3 tools/observar.py --help`: el comando existe y salió `usage: observar.py ... {capturar,revalidar}`; la ayuda corta no muestra ese bloque. No ejecuté un plan de observación con esa ruta. La segunda forma está **enseñada en el código**, y su ruta JSON es compatible con la lectura de intercambio que probé abajo.

2. **El verificador de instalación construye declaraciones JSON en proyectos temporales.** `tools/verificar_instalacion.py:395-405` arma un AST de medida y lo escribe como `catalogos/demo.instalado.json` en un perfil externo; `:541-547` escribe una relación AST como `relaciones/item.json` del proyecto del CLI. En `:537-540` el comentario llama a este último «el ejemplo que ve quien instala el paquete». Ejecuté una reproducción aislada de esas dos clases de archivo: `cargar_fuente_medida` devolvió `medida` y `cargar_fuente_relacion` devolvió `evento`. **No ejecuté el verificador de instalación completo ni afirmo haber observado su salida final.** El código inspeccionado sí muestra que un productor empaquetado conserva dos grafías de autoría en carpetas de proyecto. La lectura JSON, por sí sola, está permitida como intercambio; el hallazgo es el productor.

3. **Orden alternativo en `origen:` de un caso que también pasa la regla del impresor.** A partir de un caso impreso, intercambié las líneas `repo` y `commit`. `caso.leer`, `caso.imprimir` y `cargar_fuente_caso` aceptaron la variante: el impresor preservó el orden de inserción y devolvió exactamente la variante. Por lo tanto hay dos textos distintos con el mismo contenido de origen que son canónicos para sus respectivos árboles ordenados. Esto no elude `error_forma` (ambos son iguales a su propia impresión), pero sí contradice la idea más fuerte de una sola ordenación para los campos de origen. No atribuyo equivalencia estricta de AST: los diccionarios conservan el orden.

## Reejecución de los puntos abiertos de las auditorías 2–6

Ejecuté una sonda Python con `MEDIDA`, `AGRUPADA`, `CASO` y `RELACION` de `tests.test_forma_unica_texto`, los lectores e impresores de `nucleo.sintaxis`, `nucleo.caso` y `nucleo.relacion`, los tres `cargar_fuente_*`, `lsp.diagnosticar` y `lsp.lentes`. Cada variante fue escrita en un archivo temporal por `Path.write_bytes(texto.encode())`. Salida recortada:

```text
variante              lector  igual al impresor  cargador                    LSP diag/lens
espacios encabezado   OK      False               MedidaMalDeclarada forma   1/0
sintaxis 1.0 inicial  OK      False               MedidaMalDeclarada forma   1/0
científica 1e-3       OK      False               MedidaMalDeclarada forma   1/0
requiere repetido     OK      False               MedidaMalDeclarada forma   1/0
agregado antes clave  OK      False               MedidaMalDeclarada forma   1/0
CRLF                  OK      False               MedidaMalDeclarada forma   1/0
sin LF final          OK      False               MedidaMalDeclarada forma   1/0
blanco final          OK      False               MedidaMalDeclarada forma   1/0
espacio final         OK      False               MedidaMalDeclarada forma   1/0
caso fila redundante  OK      False               CasoMalDeclarado forma     1/0
relación "inicio"     OK      False               RelacionMalDeclarada forma 1/0
origen invertido      OK      True                OK                          0/0
```

En la sonda, `caso-clave` dio `ErrorSintaxis` porque se quitó el punto y coma de una **tabla**, donde esa grafía no vale. Repetí sobre el escape `fila`:

```text
paso: clave(t) + fila {"t": 0}  → lector OK; igualdad False; impresor produce tabla
paso: clave(t); + fila {"t": 0} → lector OK; igualdad False; impresor produce tabla
```

El cargador de caso ya rechazó arriba el escape redundante. No reejecuté en esta ronda un caso heterogéneo que obligue a `fila`; la sexta auditoría tampoco lo había reejecutado. El impresor del caso base produjo `paso: clave(t); t` y la fila `0`.

La misma sonda ejecutó:

```text
mas(1,2) / menos(1,2) / por(1,2) / col(p) → cuatro ErrorSintaxis correctivos
MEDIDA mayúscula / BOM inicial → ErrorSintaxis
comentario de línea completa → cargar_fuente_medida OK
 dos donde, umbral sin segun, umbral sin porque → igualdad con impresor True; cargador OK
MCP, medida con tres espacios → ErrorHerramienta MEDIDA_INVALIDA: fuera de la forma única
macro empaquetada canónica → _datos_de_macro: defmacro
macro CRLF / sin LF final → MacroMalDeclarada: fuera de la forma única
```

La línea `dos donde` de esa salida indica dos pasos canónicos que el impresor conserva, no dos grafías del mismo árbol. La omisión de cláusulas opcionales de umbral también se conserva. El comentario completo sigue siendo la excepción expresa de `sin_comentarios`.

## Entradas, vistas de editor y materiales

- Ejecuté `python3 tools/sintaxis.py --leer <medida temporal con tres espacios>`: rc 1, `fuera de la forma única`. `--imprimir` sobre ese archivo también dio rc 1 (con traceback del cargador); sobre el JSON equivalente dio rc 0 y comenzó `medida demo.prueba:`. Esas ramas no imprimieron una segunda superficie en estas sondas.
- Ejecuté `lsp.diagnosticar` y `lsp.lentes` sobre medida canónica, con tres espacios y CRLF: respectivamente `0/1`, `1/0`, `1/0`. La corrección de `codeLens` de la sexta auditoría se reprodujo. Para relación entrecomillada y CRLF dio diagnóstico 1 y lente 0. Para caso se usó el texto impreso por `caso.imprimir`; su origen invertido dio 0 diagnósticos.
- Ejecuté `lsp.completar` en un documento **incompleto** con `umbral <= 0 segun `, una vez con encabezado canónico y otra con triple espacio: ambos devolvieron `contrato`, `convencion`, `medicion`, `tanteo`. Es asistencia de escritura sobre texto incompleto, no carga ni evaluación de una medida; por sí sola no demuestra que el proyecto acepte una segunda superficie completa. Conviene decidir si el editor debe ofrecerla sobre un encabezado que ya diagnosticaría. Ejecuté `Servidor.manejar` para `textDocument/hover`: respondió error `-32601`, `método no soportado`; no hay vista hover implementada en esta ruta.
- Ejecuté el conversor de `ejemplo/caso-observado` con la captura y metadatos de su README, primero con destino `<id>.caso` y luego `<id>.json`: `rc 0, exists True` y `rc 1, exists False, destino debe llamarse <id>.caso`. `ejemplo/caso-observado/README.md:64` ahora dice `<id>.caso`.
- Ejecuté `rg -n 'El catálogo puede|Se guarda como|archivo\\.oracle|archivo\\.json|dominio\\.lo_que_falta\\.json|demo\\.instalado\\.json|item\\.json' docs/14-sensor-prosa.html ejemplo/caso-observado/README.md tools/medida.py tools/observar.py tools/verificar_instalacion.py`. La salida confirmó: HTML del sensor sólo dice catálogo `.oracle`; receta dice `<id>.caso`; ayuda y mensaje de `tools/medida.py` dicen `<archivo.oracle>`; y aparecieron los tres sitios nuevos citados en `tools/observar.py` y `tools/verificar_instalacion.py`.
- Ejecuté `rg -n -i '([.]json.{0,90}(medida|caso|relaci|cat[aá]logo|macro)|(?:medida|caso|relaci|cat[aá]logo|macro).{0,90}[.]json|sintaxis [0-9]|mas\\(|menos\\(|por\\(|col\\()' README.md ESPECIFICACION.md NOTAS-DE-RELEASE.md docs ejemplo tools perfiles nucleo/macros --glob '*.md' --glob '*.html' --glob '*.py' | head -160`. Encontró las menciones históricas de sintaxis 0.x en la crónica, las rutas de conversión `.json`, y los sitios nuevos. No tomé menciones de historia, intercambio o evidencia `hechos.json` como instrucciones vigentes de autoría. `ESPECIFICACION.md:1106` dice `.caso` para autoría o `.json` para almacenamiento; esa formulación distingue los usos. Las notas de release siguen sin crónica de sintaxis 1.0 según `rg -n 'sintaxis.*1\\.0' NOTAS-DE-RELEASE.md` de la sexta auditoría; **no repetí esa búsqueda exacta** aquí, así que lo dejo como pendiente editorial anterior, no como resultado nuevo.
- Ejecuté una reproducción de lectura JSON en `catalogos/` y `relaciones/`, y probé el mismo AST de relación guardado como `.oracle`: las dos rutas `.json` cargaron y la `.oracle` dio `RelacionMalDeclarada: una relación se escribe en .relacion`. Esta compatibilidad de intercambio no se cuenta como hallazgo sin un productor o enseñanza.

## Tabla final

| Forma o entrada | Estado en esta ronda | Evidencia ejecutada o inspeccionada |
|---|---|---|
| `codeLens` sobre medida no impresa; `--leer`; receta caso-observado; HTML sensor-prosa; ayuda de medida | Cerradas para las sondas | `1/0` diagnóstico/lente; `--leer` rc 1; conversor sólo `.caso`; búsqueda de los textos corregidos. |
| Encabezado, notación científica, `requiere`, `agrupar`, espacios, CRLF, LF faltante, variante de relación, escape `fila` redundante | Sólo lectores puros; cargadores rechazan | Sonda de lector → impresor → cargador → LSP, arriba. |
| `clave(t)` sin `;` ante `fila` | Sólo lector puro en la sonda | Dos formas leídas, impresor las convirtió en tabla; no son guardables en el caso homogéneo probado. |
| Orden de `origen` de caso | **Dos órdenes guardables** | Lector, impresor y cargador aceptaron el orden invertido, con igualdad textual. |
| Comentarios completos, umbral opcional, dos `donde`, JSON `.json` de intercambio | Permitidos; sin hallazgo por sí mismos | Carga o igualdad del impresor en sondas. |
| `mas/menos/por/col`, mayúsculas, BOM, macro CRLF/sin LF, MCP con forma alterna, relación JSON `.oracle` | Rechazados | Errores ejecutados arriba. |
| LSP completion sobre texto incompleto no canónico | Abierto como comportamiento de editor, no carga de medida | Devuelve los mismos cuatro orígenes de umbral con encabezado de triple espacio. |
| Ejemplo de plan de `tools/observar.py` | **Enseñanza JSON abierta** | Bloque del plan inspeccionado; herramienta `--help` ejecutada. |
| `tools/verificar_instalacion.py` | **Productor JSON abierto** | Dos escrituras explícitas inspeccionadas; reproducción aislada de carga JSON OK. El verificador completo no se ejecutó. |
| Notas de sintaxis 1.0 | Pendiente editorial heredado; no se contó como segunda sintaxis | Sin nueva ejecución específica. |

**una sola sintaxis de escritura: no, porque `tools/observar.py` sigue enseñando una medida `.json` en un plan y `tools/verificar_instalacion.py` construye una medida y una relación JSON en carpetas de proyecto; además, el orden de `origen` admite dos disposiciones guardables.**
