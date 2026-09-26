# Tercera auditoría adversarial: una sintaxis de escritura

2026-09-26. Ejecuté las sondas desde la raíz de este checkout. Los proyectos y archivos de prueba se crearon con `tempfile.TemporaryDirectory()` y desaparecieron al terminar. No cambié código ni hice commits. «Acepta» indica que la operación nombrada procesó el texto; **no** implica que `oracle test` lo considere de forma única. Las salidas siguientes están recortadas.

## Veredicto

una sola sintaxis de escritura: no, porque `juzgar`, el cargador del proyecto, MCP y LSP admiten texto `.oracle` distinto del impresor; `oracle test` y `formatear` dejan pasar CRLF en disco; y README todavía presenta `.json` como archivo de catálogo/corpus y dice que ambos formatos cargan por igual.

`oracle test` sí detecta muchas variantes de superficie. Los lectores JSON de intercambio siguen siendo otra entrada admitida, aunque los generadores probados no la producen como autoría.

## Comandos ejecutados y salidas recortadas

1. `python3 tools/cli.py tarea ver una-sintaxis`; `cat tareas/20260926-023437-una-sintaxis/AUDITORIA.md tareas/20260926-023437-una-sintaxis/AUDITORIA-2.md`; `git status --short`. Resultado: tarea `20260926-023437-una-sintaxis`, ABIERTA, con el ENCARGO de tercera auditoría a las 11:34:12 UTC. `git status --short` no imprimió nada al comienzo.

2. Localización: `rg -n 'forma.unica|formatear|texto.*impresor|canon|CRLF|BOM|sintaxis 0.8' nucleo tools tests`; `rg -n '^def |^class |EXTENSIONES|suffix' nucleo/{sintaxis,caso,relacion,macro,medida}.py tools/{cli,mcp,lsp}.py`. Resultados decisivos: `tools/formato.py:24` define `canonico`; `tools/sintaxis.py:123,149,175` compara `sin_comentarios(texto) == superficie`; `tools/cli.py:1099` ejecuta `verificar_catalogo` sólo en `cmd_test`; `tools/lsp.py:81` diagnostica; `tools/mcp.py:883` carga texto en memoria. Leí además `tools/formato.py`, los tramos correspondientes de estos archivos y `tests/test_forma_unica_texto.py` con `cat`/`sed`.

3. Sonda Python ejecutada con `nucleo.sintaxis.leer`, `nucleo.caso.leer`, `nucleo.relacion.leer`, `tools.formato.canonico` y `sin_comentarios`, usando `MEDIDA`, `AGRUPADA`, `CASO` y `RELACION` de `tests.test_forma_unica_texto`. Para cada variante ejecuté, en esencia, `lector(texto)` y `sin_comentarios(texto) == canonico(Path('x'+ext), texto, macros=macros_base())`. Salida:

   ```text
   version              LECTOR=OK IGUAL_IMPRESOR=False
   espacios encabezado  LECTOR=OK IGUAL_IMPRESOR=False
   cientifica           LECTOR=OK IGUAL_IMPRESOR=False
   agrupar orden        LECTOR=OK IGUAL_IMPRESOR=False
   donde doble          LECTOR=OK IGUAL_IMPRESOR=True
   variantes comillas   LECTOR=OK IGUAL_IMPRESOR=False
   clave sin ;          LECTOR=OK IGUAL_IMPRESOR=False
   origen orden         LECTOR=OK IGUAL_IMPRESOR=False
   comentario           LECTOR=OK IGUAL_IMPRESOR=True
   blanco               LECTOR=OK IGUAL_IMPRESOR=False
   espacio final        LECTOR=OK IGUAL_IMPRESOR=False
   tab [de indentación] LECTOR=ERROR ... indentación de 4 espacios
   CRLF                 LECTOR=OK IGUAL_IMPRESOR=False
   BOM                  LECTOR=ERROR ... se esperaba encabezado
   sin LF               LECTOR=OK IGUAL_IMPRESOR=False
   ```

   El texto de `donde doble` contenía dos pasos `donde` y el impresor los mantuvo: es una estructura distinta de un único `donde ... y ...`, pero **ambas estructuras están en forma de impresor**. `version` fue `sintaxis 0.8\n` antepuesta; `cientifica` sustituyó `contar(1)` por `contar(1e-3)`; `blanco` agregó una línea inicial; `sin LF` quitó el salto final. La comparación de CRLF aquí usó la cadena original en memoria, antes de lectura de archivo.

4. Otra sonda Python sobre `MEDIDA` con `leer` y `canonico` probó umbral, `requiere`, ámbito, blancos internos, tab final y rechazo léxico. Salida:

   ```text
   umbral sin segun       OK UNICA True
   umbral sin porque      OK UNICA True
   umbral orden inverso   ERROR ... se esperaba fin de línea
   requiere lista         OK UNICA True
   requiere repetido      OK UNICA False
   requiere despues alcance ERROR ... se esperaba fin de medida
   ambito presente        OK UNICA True
   sinonimo MAYUS         ERROR ... se esperaba encabezado
   espacio interior       OK UNICA False
   comentario inline      ERROR ... se esperaba de <relación> <alias>
   linea vacia interna    OK UNICA False
   tab final              OK UNICA False
   ```

   Que `segun`, `porque` y `ambito` sean opcionales no crea por sí solo otra grafía del **mismo árbol**: el impresor conserva su presencia o ausencia. Una lista `requiere pieza, modulo` es canónica; dos líneas consecutivas que agrupa en una no lo son.

5. En la misma clase de sonda, ejecuté `sintaxis.leer(texto, macros=macros_base())` para las grafías anteriores de expresiones y macros. Salida:

   ```text
   mayus             REJECT ... encabezado
   mas(1,2)          REJECT ... escribí a + b
   menos(1,2)        REJECT ... escribí a - b
   por(1,2)          REJECT ... escribí a * b
   col(p)            REJECT ... escribí p en vez de col(p)
   macro argumentos  REJECT ... la invocación de macro se escribe con las cláusulas de su plantilla
   ```

   Leí `nucleo/macros/ninguno.oracle` y ejecuté `leer`/`imprimir` sobre su `defmacro`: la forma de plantilla de la macro es legible y la primera línea impresa sigue siendo `defmacro ninguno(...)`. También probé la macro con línea vacía inicial y sin salto final: ambas se leen y ninguna coincide con el impresor. La macro empaquetada con su comentario completo sí satisface `sin_comentarios(texto) == canonico(...)`.

6. Evidencia de caso: ejecuté `caso.leer` y `caso.imprimir` sobre `CASO` de la prueba y sobre la sustitución `paso: clave(t); t\n            0`. Salida: `mismo árbol True`; la variante `fila {"t": 0}` es legible pero `fila texto canónico False`, mientras la tabla da `tabla texto canónico True`. El escape sigue siendo necesario y lo imprime el propio impresor para filas heterogéneas o nombres no imprimibles como cabecera; aquí sólo se demuestra que también se acepta para una fila homogénea imprimible.

7. Lectores de compatibilidad: en un directorio temporal ejecuté `cargar_fuente_medida(m.json)`, `cargar_fuente_caso(c.json)`, `cargar_fuente_relacion(r.json)` tras volcar los árboles que dieron los tres lectores; ejecuté también `_datos_de_macro(macro.json)` con un `defmacro` leído de `.oracle`, y `cargar_fuente_relacion(r.oracle)` con JSON. Salida:

   ```text
   JSON medida demo.prueba
   JSON caso 001-demo
   JSON relacion evento
   macro JSON defmacro
   relacion oracle REJECT ... una relación se escribe en .relacion
   ```

   Son entradas JSON admitidas en disco, no producción de los generadores de autoría probados. La extensión `.oracle` de una relación JSON sigue rechazada.

8. Entradas públicas: en un proyecto temporal con `catalogos/demo.prueba.oracle` cuyo encabezado era `medida   demo.prueba:`, un `.caso` con `clave(t)` sin `;` y una `.relacion` con `"inicio":`, ejecuté `cargar_fuente_*`, `lsp.diagnosticar(Proyecto(p), ruta, texto)`, `mcp._medida_en_memoria({'texto': texto, 'formato': 'oracle'}, macros_base())`, `sintaxis.verificar_catalogo(p)` y los subprocesos `python3 tools/cli.py juzgar --proyecto <tmp> --con <tmp>/hechos.json` y `python3 tools/cli.py formatear <medida> --proyecto <tmp>`. Salida:

   ```text
   cargar medida demo.prueba; cargar caso 001-demo; cargar relacion evento
   LSP medida diagnósticos []
   LSP caso diagnósticos []
   LSP relación diagnósticos []
   MCP memoria demo.prueba
   verificar desformateados ['catalogos/demo.prueba.oracle', 'corpus/001-demo.caso', 'relaciones/evento.relacion']
   juzgar rc 1: VEREDICTO: 1 de 1 medidas en rojo
   formatear rc 0: .../demo.prueba.oracle: requiere formato
   ```

   El rojo de `juzgar` fue el **resultado de evaluar** `resumen contar(1)` con la evidencia dada; no fue rechazo por forma. LSP para `.relacion` devolvió lista vacía porque esa extensión no pasa por `diagnosticar` (`tools/lsp.py:83-86`); no lo interpreto como validación positiva. Para MCP probé `_validar_evaluacion` y la función de carga de medida en memoria, no el transporte JSON-RPC: `formato: json` dio `ARGUMENTOS_INVALIDOS ... se esperaba oracle`; `formato: oracle` con encabezado de triple espacio dio `OK oracle` y `_medida_en_memoria` la cargó. El esquema `_ESQUEMA_MEDIDA` declara `{'const': 'oracle'}`. Una llamada directa a `_medida_en_memoria` con el árbol JSON y `formato: json` dio `MEDIDA_INVALIDA`; con texto de superficie y `formato: json` dio `demo.prueba`, pero la validación pública anterior rechaza este último par.

9. `oracle test` real: ejecuté `python3 tools/cli.py init <tmp>`, escribí en ese proyecto la medida con triple espacio y la relación `demo_evento.relacion` con `"inicio":`, y ejecuté `python3 tools/cli.py test --rapido --proyecto <tmp>`. Salida: `rc 1`, `SINTAXIS ✗ — 2 archivo(s) fuera de la forma única`, con instrucciones `oracle formatear catalogos/demo.prueba.oracle --escribir` y `oracle formatear relaciones/demo_evento.relacion --escribir`. El primer intento usó el nombre `evento`, que chocó con una relación empaquetada y dio `PROYECTO INVÁLIDO`; lo repetí con `demo_evento` para aislar el invariante.

10. **Borde nuevo, CRLF en disco.** Ejecuté una sonda que guardó cada variante mediante `Path.write_bytes` y llamó `tools.sintaxis.verificar_catalogo`:

    ```text
    canonico      ilegibles 0 desformateados 0
    comentario    ilegibles 0 desformateados 0
    blanco        ilegibles 0 desformateados 1
    espacio final ilegibles 0 desformateados 1
    tab final     ilegibles 0 desformateados 1
    CRLF          ilegibles 0 desformateados 0
    BOM           ilegibles 1 desformateados 0
    sin LF        ilegibles 0 desformateados 1
    ```

    Luego guardé `MEDIDA.replace('\n','\r\n')` en un proyecto creado con `oracle init` y ejecuté `python3 tools/cli.py formatear <archivo> --proyecto <tmp>`, el mismo comando con `--escribir`, y `python3 tools/cli.py test --rapido --proyecto <tmp>`. Salida:

    ```text
    formatear rc 0: ... ya tiene forma única
    formatear --escribir rc 0: ... ya tiene forma única
    test rc 1: SINTAXIS OK · 1 medidas · 0 macros · 0 casos · 0 relaciones
    CRLF conservado True; igual impresor bytes False
    ```

    El rojo final de `test` se debió a falta de casos y aceptación, no a sintaxis. `Path.read_text()` normaliza CRLF antes de que `verificar_catalogo` y `formatear` comparen la cadena; el archivo no cambia. La excepción explícita de comentarios es distinta: una línea completa `# comentario` puede diferir del impresor y seguir en forma única por diseño de `sin_comentarios`.

11. Generadores y conversión: en un proyecto temporal ejecuté `python3 tools/cli.py init <tmp>`, `nueva demo.prueba --proyecto <tmp>`, `caso nuevo demo/001-prueba --proyecto <tmp>` y `biblioteca nueva demo.biblio <tmp>/biblio`. Los cuatro devolvieron `rc 0`: `oracle.json` empieza `{`, la medida `ninguno demo.prueba:` y el caso `caso 001-prueba:`. La biblioteca creó una estructura anidada de paquete con `oracle-biblioteca.toml` (mi sonda inicialmente buscó el TOML directamente bajo `<tmp>/biblio` y devolvió `False`; la salida del comando indicó la ruta anidada). Ejecuté además `python3 -m unittest tests.test_forma_unica_texto tests.test_ensenanza_una_sintaxis tests.test_relaciones_por_revisar -q`: `Ran 26 tests ... OK`, que incluye el generador `relaciones --escribir`. Para `convertir`, ejecuté el CLI sobre `.oracle`, `.json` de medida y `.caso`: `rc 1` y «esperaba una medida .json para convertir a superficie» en los dos primeros formatos de superficie; `.json` dio `rc 0` y `medida demo.prueba:`. No observé producción de JSON de medida por ese comando.

12. Enseñanza: ejecuté `python3 tools/cli.py contexto --compacto | rg -A9 'CON QUÉ SE ESCRIBE'`, `python3 tools/cli.py manual aritmetica | head -13`, `python3 tools/cli.py --help | rg 'convertir|formatear'`, `sed` de README, `docs/03-escribir-una-medida.md`, `docs/mcp-contrato.md`, `ejemplo/sensor-prosa/README.md` y `docs/tutorial-practico.md`; `rg -n -i '(\.oracle.{0,80}\.json|\.json.{0,80}\.oracle|\.caso.{0,80}\.json|\.json.{0,80}\.caso)' README.md docs/*.md ejemplo/*/README.md ESPECIFICACION.md`. Salida recortada:

    ```text
    contexto: accesores: p.x ... · p ... · x ...; aritmética: a + b · a - b · a * b
    manual: ARITMETICA — aritmética infija de expresiones
    help: oracle convertir <archivo> Convierte medidas JSON a superficie
    docs/mcp-contrato.md: {"texto": ..., "formato": "oracle"}
    sensor-prosa/README.md: corpus/prosa/013-vacio-favorable.caso
    docs/tutorial-practico.md: Guardá la medida en `.oracle`, con la forma que produce `oracle formatear`.
    README.md:604: archivos de datos (`.oracle` y `.json`), no como código
    README.md:608: Ambos cargan superficie y JSON por igual.
    ```

    `README.md:375` sí fija superficie para escritura, pero las líneas 602-608 conservan una presentación dual en el tramo «¿Querés escribir una medida?». `docs/03` explica `.json` como intercambio/migración, y `docs/mcp-contrato.md` sólo ofrece `oracle` para texto de medida. `README.md:602` y `ESPECIFICACION.md:1098` mencionan `.json` como almacenamiento del corpus; no los cuento por sí solos como enseñanza de autoría. `docs/03` y sus HTML contienen árboles JSON en la explicación de la forma interna; tampoco los cuento por sí solos.

13. Censo y configuración: ejecuté un `Path.rglob` de `catalogos`, `corpus`, `relaciones`, `perfiles`, `ejemplo` y `nucleo/macros` con `Counter(p.suffix)`: `{'.oracle': 96, '.caso': 321, '.relacion': 23, '.json': 14}`. La lista impresa de 14 JSON contenía `oracle.json`, evidencia, metadatos y partida, no declaraciones JSON de medida/caso/relación. Con `configuracion(Proyecto(p))` probé `oracle.json` ausente, básico, con clave extra y con `ESQUEMA`: los tres primeros dieron `OK`; `ESQUEMA` dio `ProyectoInvalido ... debe declarar esquema`. La configuración JSON queda fuera del invariante textual de `.oracle/.caso/.relacion`.

## Tabla final

| Forma o punto de entrada | Estado | Evidencia ejecutada |
|---|---|---|
| MCP con `formato: json` | Cerrada en la validación pública | `_validar_evaluacion` rechazó `json`; esquema con `const: oracle`; `docs/mcp-contrato.md` sólo enseña `oracle`. |
| MCP con texto Oracle no impreso | **Abierta** | `_medida_en_memoria` aceptó `medida   demo.prueba:`. |
| `convertir` que imprime JSON desde superficie | Cerrada | `.oracle` y `.caso` rc 1; `.json` de medida rc 0, imprime superficie. |
| `contexto` con AST/accesores JSON y aritmética funcional | Cerrada | Salida `p.x`, `p`, `x`, `a + b`, `a - b`, `a * b`. |
| README/guías como invitación a escribir JSON | **Abierta en README** | README:604 y :608 presentan `.oracle`/`.json` y «ambos cargan ... por igual» junto a «¿Querés escribir una medida?»; docs/03 distingue autoría de intercambio. |
| Plantilla sensor-prosa `.json` inexistente | Cerrada | README de la plantilla cita `.caso`. |
| Tutorial práctico con `.oracle` igual que `.json` | Cerrada | Ahora dice «Guardá la medida en `.oracle`, con la forma que produce `oracle formatear`». |
| Invocación de macro por argumentos | Cerrada | `leer` la rechazó con instrucción de usar plantilla; macro empaquetada se lee/imprime. |
| `mas()`, `menos()`, `por()`, `col()` en expresión | Cerrada | Los cuatro `leer` dieron `ErrorSintaxis` correctivo. |
| Relación JSON en `.oracle`; mayúsculas de encabezado | Cerrada | `cargar_fuente_relacion` y `leer` rechazaron las sondas. |
| JSON de medida/caso/relación/macro en disco | Abierta como compatibilidad | Cuatro cargadores aceptaron JSON; el censo no encontró declaraciones JSON propias en los directorios revisados. |
| Umbral sin `segun`/`porque`; `ambito` opcional | Válida, sin segunda grafía del mismo árbol | Lector OK e igualdad con impresor en cada caso. |
| `requiere` repetido; espacios alternativos; notación científica; `sintaxis 0.8` | **Abiertas en lectores; detectadas por el invariante** | `leer` OK, igualdad con impresor False; `test` marcó encabezado alternativo. |
| `agrupar` con `agregado` antes de `clave` | **Abierta en lector; detectada por el invariante** | `leer` OK, impresor invierte al orden canónico. |
| Dos `donde` frente a uno con `y` | Dos estructuras canónicas | Dos `donde` dio igualdad con impresor True; el árbol no es el mismo que un único paso `donde`. |
| Variante entrecomillada en `.relacion` | **Abierta en lector; detectada por el invariante** | `leer` OK, igualdad False; `test` marcó relación. |
| `clave(t)` sin `;`, orden de `origen` en `.caso` | **Abiertas en lector; detectadas por el invariante** | `leer` OK, igualdad False, `verificar_catalogo` señaló el caso. |
| Tabla y `fila {...}` para la misma fila homogénea | **Abierta en lector; detectada por el invariante** | Mismo árbol, sólo la tabla coincidió con `imprimir`. El impresor usa `fila` cuando la tabla pierde datos. |
| Comentario de línea completa | Excepción deliberada | `leer` OK, `sin_comentarios(texto) == impresor`, `verificar_catalogo` no lo marca. |
| Línea blanca, espacios/tab al final, falta de LF final | **Abiertas en lectores; detectadas por el invariante** | Sondas `leer`/`verificar_catalogo`: OK + desformateado. Tab de indentación y BOM se rechazan. |
| **CRLF en archivo** | **Hallazgo nuevo: invariante eludido** | Bytes distintos del impresor; `formatear` y `test` dicen forma única/SINTAXIS OK y dejan CRLF intacto. |
| `juzgar`, LSP y cargadores de proyecto | **Hallazgo nuevo: invariante no aplicado** | `juzgar` evaluó medida no impresa; LSP devolvió `[]` para medida/caso variantes; cargadores aceptaron las tres superficies variantes. |
| Generadores CLI y biblioteca | Cerrada para las formas verificadas | `init`, `nueva`, `caso nuevo` rc 0 y producen sus formatos previstos; 26 tests, incluidos borradores de relaciones, OK. |

**Próxima corrección concreta:** aplicar la comparación con el impresor en las rutas que aceptan texto de autoría fuera de `test`, decidir explícitamente el tratamiento de CRLF a nivel de bytes, y corregir README:604-608. Esta auditoría no modifica esas rutas.
