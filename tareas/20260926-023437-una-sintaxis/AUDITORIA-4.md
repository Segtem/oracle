# Cuarta auditoría adversarial: una sintaxis de escritura

2026-09-26. Ejecuté las sondas desde este checkout. Los proyectos de prueba fueron temporales. No cambié código ni hice commits. Distingo el **lector** (`leer`), que todavía reconoce grafías históricas, del **cargador de autoría** (`cargar_fuente_*`), que exige el texto del impresor, con la excepción deliberada de comentarios de línea completa. JSON en archivos `.json` es intercambio por decisión del encargo.

## Veredicto

**una sola sintaxis de escritura: no, porque `ESPECIFICACION.md` aún enseña que un autor puede anteponer `sintaxis MAYOR.MENOR` a un `.oracle` y que éste carga; el cargador actual lo rechaza como fuera de la forma única.** La página empaquetada `docs/especificacion.html` reproduce esa indicación. La misma sección enseña que un `.oracle` viejo no se toca y que varias líneas `requiere` siguen cargando, lo que ya no describe la entrada de autoría actual.

No encontré en las rutas de entrada probadas una superficie no impresa que cargue como medida, caso, relación o macro de proyecto. Este alcance no equivale a una prueba exhaustiva de todos los textos posibles.

## Comandos ejecutados y salidas recortadas

1. `python3 tools/cli.py tarea ver una-sintaxis`; `cat tareas/20260926-023437-una-sintaxis/AUDITORIA-2.md`; `cat tareas/20260926-023437-una-sintaxis/AUDITORIA-3.md`; `git status --short`. La tarea es `20260926-023437-una-sintaxis`, ABIERTA; la nota de 11:59:39 UTC encarga esta cuarta ronda. El estado Git inicial no mostró cambios. Leí las filas abiertas de ambas tablas y sus sondas precedentes.

2. `rg -n 'forma.unica|forma_unica|sin_comentarios|verificar_catalogo|cargar_fuente|def diagnosticar|def _medida_en_memoria' nucleo tools`; `sed` de `nucleo/forma.py`, cargadores en `nucleo/{medida,caso,relacion,macro}.py`, `tools/{mcp,lsp,cli,formato}.py` y `tests/test_forma_unica_texto.py`. Encontré `leer_texto(..., newline="")` para preservar CRLF, `error_forma` en los cuatro cargadores de superficie y en MCP/LSP. `sin_comentarios` quita sólo líneas enteras cuyo primer carácter no blanco es `#`.

3. Escribí `/tmp/audit4_probe.py` y lo ejecuté con `PYTHONPATH=. python3 /tmp/audit4_probe.py`. Usó las constantes `MEDIDA`, `AGRUPADA`, `CASO`, `RELACION` de `tests.test_forma_unica_texto`, creó archivos con `write_bytes` y comparó lector, cargador, `lsp.diagnosticar` y `_medida_en_memoria`. Salida recortada (en la sonda, `ValueError: diagnostic 1` representa un diagnóstico devuelto por LSP):

   ```text
   version             parser=OK loader=MedidaMalDeclarada: ... fuera de la forma única LSP=diagnostic 1 MCP=MEDIDA_INVALIDA
   header spaces       parser=OK loader=MedidaMalDeclarada: ... fuera de la forma única LSP=diagnostic 1 MCP=MEDIDA_INVALIDA
   scientific          parser=OK loader=MedidaMalDeclarada: ... fuera de la forma única LSP=diagnostic 1 MCP=MEDIDA_INVALIDA
   agrupar order       parser=OK loader=MedidaMalDeclarada: ... fuera de la forma única LSP=diagnostic 1 MCP=MEDIDA_INVALIDA
   requiere repeat     parser=OK loader=MedidaMalDeclarada: ... fuera de la forma única LSP=diagnostic 1 MCP=MEDIDA_INVALIDA
   blank/trailing space/trailing tab/CRLF/CR only/no LF: parser=OK; loader=... fuera de la forma única; LSP=diagnostic 1; MCP=MEDIDA_INVALIDA
   BOM                 parser=ErrorSintaxis; loader=MedidaMalDeclarada; LSP=diagnostic 1; MCP=MEDIDA_INVALIDA
   comment             parser=OK loader=OK LSP=OK MCP=OK
   case key no semicolon / case origin order / case homogeneous row: parser=OK; loader=CasoMalDeclarado: ... fuera de la forma única; LSP=diagnostic 1
   relation quotes / relation CRLF: parser=OK; loader=RelacionMalDeclarada: ... fuera de la forma única; LSP=diagnostic 1
   macro canonical     loader=OK
   macro CRLF/no LF/blank: loader=MacroMalDeclarada: ... fuera de la forma única
   ```

   La fila `case homogeneous row` usó `fila {"t": 0}`: el lector la entiende, pero el impresor elige tabla para esa evidencia. Para filas heterogéneas el impresor sí produce `fila {...}`; no afirmo que el escape deba desaparecer. La línea de comentario es una excepción admitida explícitamente por el invariante, no una grafía alternativa de una cláusula.

4. Ejecuté una sonda Python con `sintaxis.leer` e `imprimir` sobre omisiones de `segun`, `porque`, `ambito` presente/ausente y dos pasos `donde`. Salida:

   ```text
   umbral sin segun reader OK same printer True
   umbral sin porque reader OK same printer True
   ambito ausente reader OK same printer True
   ambito presente reader OK same printer True
   donde doble reader OK same printer True
   ```

   Son estructuras que el impresor conserva. También repetí `MEDIDA` con encabezado en mayúsculas y las expresiones `mas(1, 2)`, `menos(1, 2)`, `por(1, 2)` y `col(p)`: `leer` dio `ErrorSintaxis` en las cinco; las cuatro últimas dicen respectivamente `escribí a + b`, `a - b`, `a * b`, `p en vez de col(p)`.

5. En otro directorio temporal volqué árboles leídos a `.json` y ejecuté los cuatro cargadores. Salida:

   ```text
   medida.json loaded True
   caso.json loaded True
   relacion.json loaded True
   macro.json loaded defmacro
   rel.oracle RelacionMalDeclarada: una relación se escribe en .relacion
   ```

   Esta compatibilidad JSON está excluida del hallazgo por el encargo. No probé un proyecto que escribiera esos JSON a mano.

6. Escribí `/tmp/audit4_routes.py`, ejecutado con `PYTHONPATH=. python3 /tmp/audit4_routes.py`. Inicializó un proyecto temporal y puso a la vez `medida   demo.prueba:`, `clave(t)` sin `;` y `"inicio":` en archivos de autoría. Extractos:

   ```text
   revisar rc 2 PROYECTO INVÁLIDO — ...demo_evento.relacion: fuera de la forma única
   probar rc 1 ✗ ...demo.prueba.oracle: fuera de la forma única
   expandir rc 1 ... MedidaMalDeclarada: ...demo.prueba.oracle: fuera de la forma única
   caso generar rc 1 ... MedidaMalDeclarada: ...demo.prueba.oracle: fuera de la forma única
   contexto rc 0 # CONTEXTO PARA ESCRIBIR UNA MEDIDA ...
   juzgar rc 2 PROYECTO INVÁLIDO — ...demo_evento.relacion: fuera de la forma única
   test rc 1 SINTAXIS ✗ — 3 archivo(s) fuera de la forma única
   censar rc 0 ... NO SE PUDO CENSAR — MedidaMalDeclarada: ... fuera de la forma única
   estudio rc 1 ... MedidaMalDeclarada: ...demo.prueba.oracle: fuera de la forma única
   ```

   Repetí el script mostrando el final de las trazas de `expandir`, `caso generar` y `estudio` para comprobar que era rechazo por forma. `revisar` y `juzgar` se detuvieron primero en la relación, por lo que esas dos líneas **no** prueban por sí solas su comportamiento frente a la medida; la prueba separada siguiente sí comprueba `juzgar`. `censar` terminó con código 0 y un aviso de que no pudo censar: tampoco aceptó la medida. `contexto` devolvió 0, pero la comprobación separada siguiente mostró su advertencia expresa.

7. En un proyecto temporal que sólo tenía `sintaxis 0.8` antepuesto a `MEDIDA`, ejecuté `python3 tools/mutar.py --proyecto <tmp> --hechos` y `python3 tools/cli.py contexto --compacto`, `formatear`, `test --rapido`, `juzgar --con hechos.json`, todos con `--proyecto <tmp>`. Salida recortada:

   ```text
   mutar rc 1 MedidaMalDeclarada: ... fuera de la forma única
   contexto rc 0 ## LAS MEDIDAS QUE YA EXISTEN — NO SE PUDIERON LEER; ⚠ ... MedidaMalDeclarada: ... fuera de la forma única
   formatear rc 0 ... requiere formato
   test rc 1 SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
   juzgar rc 2 ERROR AL EVALUAR — ... fuera de la forma única
   ```

   La línea de versión es el caso que la especificación todavía enseña y el cargador rechaza. El `rc 0` de `formatear` informa que requiere normalización; no afirma carga exitosa como proyecto.

8. En otra sonda temporal guardé `MEDIDA` con CRLF y ejecuté `test --rapido`, `formatear` y `formatear --escribir`. Salida:

   ```text
   test rc 1 SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
   formatear rc 0 ... requiere formato
   formatear --escribir rc 0 ... escrito
   bytes LF True
   ```

   Así se cerró el bypass CRLF observado en la tercera auditoría.

9. Ejecuté un recorrido Python de archivos `.oracle`, `.caso` y `.relacion` bajo `catalogos`, `corpus`, `relaciones`, `perfiles`, `ejemplo` y `nucleo/macros`, llamando al cargador correspondiente (a `_datos_de_macro` para `defmacro`). Salida: `archivos 440 cargados {'medida': 90, 'caso': 321, 'relacion': 23, 'macro': 6} errores 0`. Este censo incluye ejemplos empaquetados, plantilla sensor-prosa y perfil Python. No infiero por ello que todos los comandos de ejemplo se hayan ejecutado.

10. Ejecuté `oracle biblioteca nueva demo.lib <tmp>/lib` y `oracle plantilla sensor-prosa <tmp>/sensor` en un temporal: ambos `rc 0`. Enumeré sus superficies: el sensor creó `.relacion`, `.oracle` y `.caso`; en `catalogos`, `corpus`, `relaciones` y `macros` de ambos destinos no apareció ningún `.json`. `oracle biblioteca verificar ejemplo/biblioteca-guia` dio `BIBLIOTECA INVÁLIDA — falta oracle-biblioteca.toml`; ese ejemplo no es una biblioteca verificable, y esa salida no prueba aceptación ni rechazo de una medida. El cargador de medida fue probado directamente en el punto 3.

11. Revisé enseñanza con `rg -n -i '(\.oracle.{0,80}\.json|\.json.{0,80}\.oracle|\.caso.{0,80}\.json|\.json.{0,80}\.caso|escrib.{0,50}json|json.{0,50}escrib)' README.md docs ejemplo nucleo/macros perfiles`, `sed -n '515,565p' ESPECIFICACION.md`, `rg -n 'sintaxis MAYOR|sintaxis 0\.8|ambos por igual|se guardan como JSON|viejo se|formato de autoría|forma única' docs/*.md README.md ESPECIFICACION.md`, `python3 tools/cli.py manual | rg -n -i 'json|sintaxis mayor|sintaxis 0\.8|dos formatos|escrib|fila \{'`, `python3 tools/cli.py contexto --compacto | rg -n -i 'json|mas\(|menos\(|por\(|sintaxis|escrib'` y `sed -n '595,615p' README.md`. Salidas decisivas:

   ```text
   ESPECIFICACION.md:523-524: ... la superficie es cómo se escribe y el JSON es cómo se guarda, cargándose ambos por igual.
   ESPECIFICACION.md:525-526: ... un archivo .oracle o .caso viejo se lee; el impresor no lo toca.
   ESPECIFICACION.md:559-562: Un .oracle puede declarar ... sintaxis MAYOR.MENOR. Es opcional ... y es parte de la superficie ... falla cerrado [si incompatible].
   docs/especificacion.html:106: Un .oracle puede declarar ... sintaxis MAYOR.MENOR ... es parte de la superficie.
   README.md:608: El JSON se conserva como formato de intercambio y migración.
   manual: tabla; fila {…} para datos heterogéneos; JSON descrito como intercambio en la meta.
   ```

   El texto de `ESPECIFICACION.md:559-562` es una instrucción positiva para escribir una grafía que la entrada de autoría rechaza. Las frases de `:525-526`, `:538-542` (varias líneas `requiere`) y `:549-552` (archivo viejo) refuerzan una expectativa de carga que la forma única actual contradice. `docs/tutorial-practico.md:23` dice que medidas y casos «se guardan como JSON»; leída junto con su frase inmediata «la superficie es cómo se escribe» no la conté como instrucción de escribir JSON. `docs/tutorial-practico.html:260` y `docs/especificacion.html:260` aún hablan de carga dual; bajo la exclusión explícita de `.json` de intercambio, tampoco los conté como hallazgo independiente. `oracle manual` y `oracle contexto` no mostraron otra grafía de autoría en las búsquedas ejecutadas.

## Tabla final: filas abiertas de las auditorías 2 y 3

| Forma o ruta | Estado en cuarta auditoría | Evidencia ejecutada |
|---|---|---|
| `fila {...}` de caso, incluida fila homogénea | Lector aún la acepta; proyecto rechaza la grafía no impresa. Escape canónico para heterogeneidad | Punto 3; manual, punto 11. |
| JSON de medida, caso, relación y macro en `.json` | Admitido como intercambio; excluido como hallazgo | Punto 5. |
| Umbral sin `segun` o `porque`; `ambito` presente o ausente | Formas canónicas distintas, conservadas por impresor | Punto 4. |
| `requiere` en varias líneas | Lector acepta; proyecto, MCP y LSP rechazan grafía no impresa | Punto 3. La especificación todavía afirma compatibilidad de carga. |
| `agrupar` con `agregado` antes de `clave` | Lector acepta; proyecto, MCP y LSP rechazan | Punto 3. |
| Dos `donde` frente a uno con `y` | Dos estructuras canónicas; el impresor conserva dos pasos | Punto 4. |
| Variante entrecomillada de relación | Lector acepta; proyecto y LSP rechazan | Puntos 3 y 6. |
| `sintaxis 0.8` antepuesto a medida | Lector acepta; proyecto, `juzgar`, `test`, `mutar`, MCP y LSP rechazan. **Enseñanza abierta** | Puntos 3, 7 y 11. |
| `clave(t)` sin `;` y orden de `origen` | Lector acepta; cargador y LSP rechazan | Punto 3. |
| Notación científica y espacios alternativos | Lector acepta; cargador, MCP y LSP rechazan | Punto 3. |
| Comentario de línea completa | Excepción deliberada admitida | Punto 3. |
| Líneas blancas, espacios/tab finales, CRLF, CR solo, falta de LF final | Lector acepta; cargador, MCP y LSP rechazan. CRLF también falla `test` y se corrige con `formatear --escribir` | Puntos 3 y 8. |
| BOM, mayúsculas de encabezado y `mas/menos/por/col` | Rechazados por lector | Puntos 3 y 4. |
| Texto no impreso en `juzgar`, MCP, LSP y cargadores | Hallazgo de tercera auditoría cerrado en sondas ejecutadas | Puntos 3, 6 y 7. |
| `convertir`/`expandir` y JSON canónico impreso | `expandir` de texto no impreso rechaza; JSON de `expandir` es árbol interno para inspección. No repetí la sonda de `convertir` en esta ronda | Punto 6 y lectura de `tools/medida.py:expandir_archivo`, `tools/cli.py:cmd_convertir`. |
| README dual de autoría | Cerrado en el fragmento antes abierto | Punto 11. |
| Especificación que enseña línea de versión y carga de grafías viejas | **Hallazgo de enseñanza abierto** | Punto 11, contrastado con puntos 3 y 7. |
| `medida probar/revisar/expandir`, `caso generar`, `contexto`, `mutar`, `censar`, `biblioteca`, `estudio` | No aceptaron la medida no impresa en las rutas que la cargaron; `contexto` avisó falla, `censar` avisó sin censar. Biblioteca verificable no probada | Puntos 6, 7 y 10. |
| Perfiles y ejemplos empaquetados | 440 superficies recorrieron sus cargadores sin error; generadores probados emitieron superficie | Puntos 9 y 10. |

**Corrección sugerida:** actualizar la sección de versión de `ESPECIFICACION.md` y regenerar `docs/especificacion.html` para distinguir lectura histórica de autoría cargable hoy; decidir si la línea de versión debe imprimirse (y entonces ser canónica) o presentarse sólo como entrada heredada que requiere `oracle formatear`. En esta auditoría no cambié esos archivos.
