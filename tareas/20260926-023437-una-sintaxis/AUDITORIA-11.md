# Undécima auditoría adversarial: una sintaxis de escritura

2026-09-26. Leí el encargo de la undécima auditoría y las auditorías anteriores (AUDITORIA-2 a -10). Trabajé en este worktree (`/work`) sin modificar código ni hacer commits. Apliqué la definición pública vigente de `ESPECIFICACION.md:538-550`: forma única = un texto por árbol sin contar líneas de comentario completas; el orden de relaciones, columnas y claves (salvo `origen`) es parte del árbol. Apliqué además el criterio fijado para textos históricos: una mención histórica sólo es hallazgo si presenta como vigente una forma hoy rechazada sin aclarar que cambió. Las sondas temporales, el wheel y el entorno virtual se construyeron en `/tmp`.

## 1. Verificación del hallazgo de AUDITORIA-10

En AUDITORIA-10 se señaló que `NOTAS-DE-RELEASE.md:155` y `docs/notas.html:67` (corte 0.30.0) enseñaban la resta sin espacios (`t1.turno-1`). En este checkout verifiqué que ambos archivos contienen ahora la aclaración explícita en línea:
`*Desde sintaxis 1.0 (Oracle 0.32.0) el guion se lee igual, pero se escribe t1.turno - 1: el cargador sólo acepta el texto del impresor.*`

Ejecuté búsquedas de comprobación y la prueba comparativa con el cargador:

```bash
grep -n -C 2 "t1.turno-1" NOTAS-DE-RELEASE.md docs/notas.html
python3 tools/cli.py manual aritmetica
```

Salida recortada:
```text
NOTAS-DE-RELEASE.md:155:- **Dentro de una expresión el guion es siempre resta**, también sin espacios: `t1.turno-1` es
NOTAS-DE-RELEASE.md:157:  de macro con guion (`ninguno-requiere`) siguen valiendo en los encabezados. *Desde sintaxis 1.0
NOTAS-DE-RELEASE.md:158:  (Oracle 0.32.0) el guion se lee igual, pero se escribe `t1.turno - 1`: el cargador sólo acepta el
NOTAS-DE-RELEASE.md:159:  texto del impresor.*
docs/notas.html:67: ... <em>Desde sintaxis 1.0 (Oracle 0.32.0) el guion se lee igual, pero se escribe <code>t1.turno - 1</code>: el cargador sólo acepta el texto del impresor.</em> ...
```

Al evaluar en archivo `.oracle`:
```text
p.turno-1   lector OK; impresor: donde p.turno - 1 > 0; sin_comentarios == impresor: False
            cargador MedidaMalDeclarada: fuera de la forma única; LSP: 1 diagnóstico
p.turno - 1 lector OK; impresor idéntico; sin_comentarios == impresor: True; cargador OK; LSP: 0 diagnósticos
```

Bajo el criterio del encargo («Texto histórico es hallazgo SÓLO si presenta como vigente una forma que hoy se rechaza sin decir que cambió»), el punto quedó subsanado y deja de ser hallazgo.

## 2. Reejecución adversarial de los puntos abiertos (AUDITORIA-2 a -10)

Ejecuté una matriz completa de sondas con `PYTHONPATH=. python3 /tmp/audit11_probe.py`. Para cada variante se ejercitó el lector, el impresor, el cargador correspondiente (`cargar_fuente_medida`, `cargar_fuente_caso`, `cargar_fuente_relacion`, `_datos_de_macro`) y `lsp.diagnosticar`.

Salida del script:

```text
medida/base            igual                  carga OK                       LSP=0
medida/espacios        distinto               MedidaMalDeclarada forma       LSP=1
medida/version         distinto               MedidaMalDeclarada otro        LSP=1
medida/cientifica      distinto               MedidaMalDeclarada forma       LSP=1
medida/agrupar         distinto               MedidaMalDeclarada forma       LSP=1
medida/requiere        distinto               MedidaMalDeclarada forma       LSP=1
medida/ambito          distinto               MedidaMalDeclarada forma       LSP=1
medida/a-b             distinto               MedidaMalDeclarada forma       LSP=1
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

Comprobaciones adicionales sobre casos, relaciones y expresiones:
- **`fila` redundante:** en un caso con columnas homogéneas, escribir `fila {"t": 0}` en lugar de tabla devuelve `CasoMalDeclarado: fuera de la forma única` porque el impresor emite la cabecera tabular.
- **`origen` con campos extra desordenados:** en un caso con campos adicionales en `origen` (`zeta: 1` antes de `alpha: 2`), el cargador rechazó el archivo con `CasoMalDeclarado: fuera de la forma única` debido al orden alfabético exigido para campos no prefijados (`ORDEN_ORIGEN`).
- **Comentarios al final de línea con código:** `alcance "a" # nota` falló en el lector con `ErrorSintaxis: se esperaba expresión; llegó '#'`.
- **Paréntesis redundantes:** `donde (p.x > 0)` y `donde (true y false) y true` son despojados de paréntesis por el impresor; `sin_comentarios(actual) != impresor` y el cargador los rechaza.
- **Dos `donde` vs `y`:** `donde p.x > 0` seguido de `donde p.x < 10` produce dos pasos `['donde', ...]` en la tubería; `donde p.x > 0 y p.x < 10` produce un solo paso con operador `['y', ...]`. Son árboles distintos y cada uno se imprime idéntico a sí mismo.

## 3. Entradas, generadores y herramientas CLI

Probé las herramientas de entrada sobre archivos válidos y sobre archivos deliberadamente desformateados (triple espacio, CRLF o claves invertidas):

```bash
python3 tools/sintaxis.py --leer /tmp/oracle-audit11-bad.oracle
python3 tools/cli.py medida revisar /tmp/oracle-audit11-bad.oracle
python3 tools/cli.py medida probar /tmp/oracle-audit11-bad.oracle --con '[]'
python3 tools/medida.py --expandir /tmp/oracle-audit11-bad.oracle
python3 tools/cli.py formatear /tmp/oracle-audit11-bad.oracle
python3 tools/cli.py caso listar --proyecto /tmp/oracle-audit11-proj-bad
```

Salidas recortadas:
- `tools/sintaxis.py --leer`: salida 1, `✗ ... fuera de la forma única`.
- `tools/cli.py medida revisar`: salida 1, `✗ ... fuera de la forma única`.
- `tools/cli.py medida probar`: salida 1, `✗ ... fuera de la forma única`.
- `tools/medida.py --expandir`: salida 1, `MedidaMalDeclarada: ... fuera de la forma única`.
- `tools/cli.py formatear`: salida 0, emitió diff unificado y con `--escribir` normalizó al texto del impresor.
- `tools/cli.py caso listar`: con un caso con `origen` desordenado en el corpus, falló con código 1 y `✗ ... fuera de la forma única`.
- `mcp._medida_en_memoria`: rechazó el texto alternativo con `ErrorHerramienta: fuera de la forma única`. Rechazó `formato: json` exigiendo encabezado `.oracle`.
- `lsp.diagnosticar`: produjo 1 diagnóstico con la versión formateada y 0 lentes de código ante el texto fuera de forma.
- `tools/cli.py test --rapido`: sobre el repositorio actual dio `SINTAXIS OK · 63 medidas · 6 macros · 217 casos · 13 relaciones` y `VEREDICTO: VERDE`.
- `tools/sintaxis.py --verificar`: sobre el catálogo del repositorio dio 0 ilegibles y 0 desformateados.

## 4. Empaquetado, wheel, plantilla e instalación limpia

Construí e instalé la distribución en un entorno aislado:

```bash
UV_CACHE_DIR=/tmp/oracle-audit11-uv-cache uv build --out-dir /tmp/oracle-audit11-dist
python3 -m venv /tmp/oracle-audit11-venv
/tmp/oracle-audit11-venv/bin/pip install /tmp/oracle-audit11-dist/oracle_metalenguaje-0.31.1-py3-none-any.whl
/tmp/oracle-audit11-venv/bin/oracle plantilla sensor-prosa /tmp/oracle-audit11-plantilla-installed
/tmp/oracle-audit11-venv/bin/oracle test --rapido --proyecto /tmp/oracle-audit11-plantilla-installed
```

Salidas recortadas:
- `uv build`: construyó exitosamente `oracle_metalenguaje-0.31.1.tar.gz` y `oracle_metalenguaje-0.31.1-py3-none-any.whl`.
- Inspección de archivos empaquetados en el wheel: 1 `.oracle`, 15 `.caso`, 1 `.relacion` y 1 manifest `oracle.json` dentro de `plantilla_sensor_prosa/`. Cero archivos JSON declarativos para medidas o casos.
- `pip install`: instalación exitosa de `oracle-metalenguaje-0.31.1`.
- `oracle plantilla sensor-prosa`: copió 15 casos `.caso`, 1 medida `.oracle` y 1 relación `.relacion`.
- `oracle test --rapido`: ejecutado desde `/tmp` sobre el proyecto generado por la plantilla instalada:
  `CORPUS OK · 15 casos`
  `SINTAXIS OK · 1 medidas · 0 macros · 15 casos · 1 relaciones`
  `ACEPTACIÓN ✓ — 4 defectos en rojo, 2 sin evidencia esperada, 9 verdes correctos`
  `VEREDICTO: VERDE`

## 5. Auditoría de textos, ayudas, contratos y ejemplos

- **Ejemplos en documentación (`docs/` y Markdown):** ejecuté un extractor automático sobre todos los bloques de código de medidas, casos y relaciones en `docs/`, `README.md` y `ESPECIFICACION.md`. Todos los ejemplos ejecutables coinciden estrictamente con su versión impresa por el núcleo (`sin_comentarios(original) == impresor`).
- **Ayuda del CLI y `manual`:** ejecuté `python3 tools/cli.py --help` y `manual <tema>` para todos los temas (`aritmetica`, `casos`, `macros`, etc.). No enseñan formas funcionales obsoletas; `manual aritmetica` explica explícitamente la obligatoriedad de espacios en `a - b`.
- **`contexto --compacto`:** enseña únicamente operadores infijos `a + b · a - b · a * b` y accesores `p.x · p · x`. No incluye accesores funcionales obsoletos (`col(p)`, `mas(a, b)`).
- **Proyectos en `ejemplo/`:** los 6 subproyectos con estructura completa (`batalla-naval`, `como-funciona`, `primer-valor`, `recetas`, `seguimiento-tareas`, `sensor-prosa`) pasaron `oracle test --rapido` con `SINTAXIS OK` y `VEREDICTO: VERDE`. (`biblioteca-guia` es sólo un proyecto pedagógico que no declara `diferencial/`).

## Tabla final

| Forma o punto | Estado | Evidencia ejecutada |
|---|---|---|
| Aclaración de `t1.turno-1` en notas de release y web | **Cerrado sin hallazgo** | `NOTAS-DE-RELEASE.md:157` y `docs/notas.html:67` incluyen la aclaración explícita sobre sintaxis 1.0 (0.32.0); el cargador rechaza `p.turno-1` y acepta `p.turno - 1`. |
| Espacios, versión inicial, notación científica, `agrupar`, `requiere`, `ambito`, CRLF, sin LF final, blanco intermedio, espacio al final | Rechazadas por el cargador | `sin_comentarios(actual) != impresor`; `MedidaMalDeclarada / CasoMalDeclarado / RelacionMalDeclarada / MacroMalDeclarada: fuera de la forma única`; LSP=1. |
| Mayúsculas, BOM UTF-8, funciones aritméticas (`mas`, `menos`, `por`), accesor `col(p)`, comentario al final de línea de código | Rechazadas en el lector | `ErrorSintaxis` con mensaje correctivo («escribí a + b», «escribí p en vez de col(p)»). |
| `fila` redundante cuando cabe en tabla, `origen` desordenado o campos extra no alfabéticos | Rechazadas por el cargador | Diferencia con la salida de `imprimir`; error de forma única con diff y sugerencia de `formatear --escribir`. |
| Líneas completas `#` | Excepción pública admitida | Medida, caso y macro cargaron idéntico; LSP=0 diagnósticos. |
| Orden de relaciones, columnas y claves de objeto en evidencia | Parte del árbol (definición pública) | Ambos órdenes son canónicos de dos árboles con distinta secuencia de lectura. |
| Encadenamiento de múltiples `donde` vs operador `y` | Árboles distintos | Producen ASTs diferentes en la tubería; cada uno se conserva e imprime canónicamente. |
| Puntos de entrada (`--leer`, `revisar`, `probar`, `expandir`, `formatear`, `test`, `juzgar`, `caso listar`, MCP, LSP) | Comprobación uniforme | Todas las entradas rechazan o diagnostican textos fuera de la forma única. |
| JSON `.json` en catálogos | Intercambio admitido | Permitido únicamente en archivos con extensión `.json`; rechazado en `.oracle`. |
| Distribución empaquetada (wheel y sdist) y `oracle plantilla` | Superficie pura y verde | `uv build`, instalación en venv limpio de `/tmp`, `oracle plantilla` y `oracle test` verde. |

**una sola sintaxis de escritura: sí**
