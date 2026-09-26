# Decimoquinta auditoría adversarial: una sintaxis

2026-09-26. Apliqué el criterio público de `ESPECIFICACION.md:527-554`: un texto por árbol, exceptuadas las líneas completas cuyo primer carácter no blanco es `#`; el orden de relaciones, columnas y claves de objeto (salvo `origen`) pertenece al árbol; texto histórico sólo es hallazgo si presenta como vigente una forma que hoy se rechaza sin decir que cambió; JSON en `.json` se admite como formato de intercambio. Trabajé en contra, buscando activamente segundas sintaxis, con sondas y entornos temporales en `/tmp`. No cambié código ni realicé commits.

## Productores en `tools/`, `ejemplo/` y `perfiles/`

El hallazgo de AUDITORIA-14 señaló que `tools/sondear_procedencia.py` escribía casos temporales con `json.dumps` en `<id>.json`. Verifiqué el estado actual de este script y barrí todos los scripts del repositorio en busca de productores de medidas, casos, relaciones o macros.

Ejecuté:

```bash
python3 tools/sondear_procedencia.py
python3 - <<'PY'
from tools.sondear_procedencia import escribir_corpus, SONDAS
from nucleo.caso import cargar_casos
r = escribir_corpus(SONDAS['un_caso_observado_no_dice_de_donde_salio'][0])
print([(p.name, p.suffix) for p in sorted(r.rglob('*')) if p.is_file()])
print(len(cargar_casos(r)))
print(next(p for p in sorted(r.rglob('*')) if p.is_file()).read_text(encoding='utf-8')[:90])
PY
```

Salida recortada:

```text
PROCEDENCIA — 2 sondas sobre corpus reales, juzgadas por meta.todo_caso_observado_declara_de_donde_salio
  ✓ un_caso_observado_no_dice_de_donde_salio
  ✓ todos_los_observados_dicen_de_donde_salieron
[('001-corrida-sin-registro.caso', '.caso'), ('002-corrida-con-registro.caso', '.caso'), ('003-escrito-a-mano.caso', '.caso')]
3
caso 001-corrida-sin-registro:
    fecha: "2026-09-07"
    origen:
        repo: "Segtem/oracle"
```

El script ahora produce archivos `.caso` con `imprimir_caso` y son validados por `cargar_casos`.

Inspeccioné mediante AST y análisis léxico todas las operaciones de escritura en `tools/`, `ejemplo/` y `perfiles/`:
- `tools/observar.py`: emite `.caso` mediante `_caso_escrito(caso)` invocando `imprimir(caso)`.
- `tools/medida.py`: emite borradores `.relacion` (`_imprimir_borrador`), andamios `.oracle` (`PLANTILLA`) y andamios `.caso` con marca `# ANDAMIO:`. Conserva la guarda de no pisar un `.json` preexistente.
- `tools/corpus.py`: emite `.caso` en superficie única (`PLANTILLA`).
- `tools/cli.py`: `formatear --escribir` guarda la forma única en `.oracle`, `.caso` y `.relacion`; `convertir` migra JSON histórico a superficie única; `oracle.json` guarda exclusivamente metadatos de configuración del proyecto.
- `tools/verificar_instalacion.py`: genera temporales en `.oracle`, `.caso` y `.relacion` en superficie canónica.
- `nucleo/generador.py`: escribe `.caso` con `imprimir_caso(caso_final)`.
- `ejemplo/caso-observado/convertir.py`: convierte capturas JSON en `.caso` mediante `imprimir(datos)`.
- `ejemplo/sensor-prosa/`, `ejemplo/seguimiento-tareas/`, `ejemplo/primer-valor/` y `ejemplo/batalla-naval/`: producen `hechos.json` (evidencia consumida por `oracle juzgar --con`), formato de intercambio expresamente admitido.
- `perfiles/python/mutacion_codigo.py`: escribe código mutante Python y exclusiones en `equivalentes.json`, no modelos de Oracle.

No se detectó ningún productor activo que genere medidas, casos, relaciones o macros en JSON ni en otra grafía fuera de la superficie canónica.

## Inserción exhaustiva de comentarios en las cuatro superficies

Ejecuté una prueba de inserción exhaustiva sobre 11 archivos reales representativos de todas las variantes estructurales del lenguaje:
- Medidas `.oracle`: `catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle` y `catalogos/meta/meta.toda_medida_de_ausencia_declara_requiere.oracle` (con `requiere ... donde ...`).
- Macros `.oracle`: `nucleo/macros/ninguno.oracle` y `nucleo/macros/peor.oracle`.
- Casos `.caso`: `corpus/simulacion/301-simulador-que-ignora-la-semilla.caso` (tablas y prosa), `corpus/meta/501-las-dos-formas-del-impresor-eligen-bien.caso` (filas heterogéneas con escape `fila {`), `corpus/proceso/008-vault-falso-rojo.caso` (tablas con delimitador pipe `|`), `corpus/proceso/019-ronda-sin-mutantes-declarada-verde.caso` (relación `(vacia)`), `corpus/proceso/059-clave-declarada-en-un-caso.caso` (declaración `clave:`).
- Relaciones `.relacion`: `relaciones/mutante.relacion` y `relaciones/evento.relacion` (con bloque `variantes por tipo:`).

En cada límite de línea (antes de la primera, entre cada línea y después de la última) se insertaron 4 variantes de línea de comentario:
1. `# comentario prueba 15\n` (sin sangría)
2. `    # comentario con cuatro espacios\n` (con sangría)
3. `\t# comentario con tab\n` (con tabulador)
4. `#\n` (comentario vacío)

Para cada variante se comprobó: (1) igualdad estricta del árbol devuelto por `leer`; (2) `sin_comentarios(texto) == imprimir(arbol)`; (3) carga correcta por el cargador correspondiente (`cargar_fuente_medida`, `_datos_de_macro`, `cargar_fuente_caso`, `cargar_fuente_relacion`); (4) preservación exacta byte a byte del archivo tras `cmd_formatear(..., escribir=True)`; (5) ausencia total de diagnósticos en `lsp.diagnosticar`.

Ejecuté el script de prueba en `/tmp/oracle_audit15_comments.py`. Salida recortada:

```text
medida             lines  6 positions  7 probes  28 passes  28 failures 0
medida_requiere    lines 14 positions 15 probes  60 passes  60 failures 0
macro_ninguno      lines  9 positions 10 probes  40 passes  40 failures 0
macro_peor         lines  9 positions 10 probes  40 passes  40 failures 0
caso_simulacion    lines 21 positions 22 probes  88 passes  88 failures 0
caso_fila          lines 22 positions 23 probes  92 passes  92 failures 0
caso_pipe          lines 18 positions 19 probes  76 passes  76 failures 0
caso_vacia         lines 17 positions 18 probes  72 passes  72 failures 0
caso_clave         lines 18 positions 19 probes  76 passes  76 failures 0
relacion_mutante   lines 19 positions 20 probes  80 passes  80 failures 0
relacion_evento    lines  6 positions  7 probes  28 passes  28 failures 0
TOTAL: 680 probes, 680 passes, 0 failures
```

Las 680 sondas pasaron sin fallas. Se confirmó además que el impresor rechaza escribir una línea de prosa que empiece con `#` (`ValueError: «sintoma»: una línea de prosa no puede empezar con #`) cumpliendo la especificación léxica, y que comentarios al final de líneas con código (inline) son rechazados por los lectores de las cuatro superficies con errores de sintaxis (`MedidaMalDeclarada`, `CasoMalDeclarado`, `RelacionMalDeclarada`, `MacroMalDeclarada`).

## Reejecución de variantes y bordes de la forma única

Ejecuté una matriz completa de variantes sobre las cuatro superficies:

```bash
python3 - <<'PY'
# Script de prueba ejecutando matrices léxicas y sintácticas
# evaluando cargar_fuente_*, sin_comentarios == imprimir y lsp.diagnosticar
PY
```

Salidas recortadas por categoría:

1. **Variantes léxicas y de terminación**:
   - `medida/caso/relacion/macro`: base y comentarios (inicio, sangrado, final, sin LF): `cargado: OK`, `igual: True`, `LSP: 0`.
   - `medida/caso/relacion/macro`: CRLF (`\r\n`), sin LF final, línea blanca extra: `cargado: ERR: fuera de la forma única`, `igual: False`, `LSP: 1`.
   - `medida/caso/relacion/macro`: BOM UTF-8 (`\xef\xbb\xbf`): `cargado: ERR`, `igual: False`, `LSP: 1`.
   - Archivos vacíos o con solo comentarios/blancos: rechazados por los cuatro cargadores.

2. **Variantes sintácticas históricas (AUDITORIA-2 a -14)**:
   - `medida triple_espacio`: `MedidaMalDeclarada` (fuera de la forma única), `LSP: 1`.
   - `medida version`: `MedidaMalDeclarada` (fuera de la forma única), `LSP: 1`.
   - `medida cientifica` (`1e-3` en lugar de `0.001`): `MedidaMalDeclarada`, `LSP: 1`.
   - `medida resta_sin_espacios` (`p.x-p.y`): `MedidaMalDeclarada` (`ErrorSintaxis`), `LSP: 1`.
   - `medida parentesis` (`(p.x + p.y)`): `MedidaMalDeclarada` (`ErrorSintaxis`), `LSP: 1`.
   - `medida agrupar_invertido`: `MedidaMalDeclarada` (fuera de la forma única), `LSP: 1`.
   - `medida funcion_mas`, `funcion_col`, `mayuscula`: `ErrorSintaxis`, `MedidaMalDeclarada`, `LSP: 1`.
   - `caso clave_sin_puntoycoma`: `CasoMalDeclarado` (`ErrorSintaxis`), `LSP: 1`.
   - `caso origen_invertido`: `CasoMalDeclarado` (fuera de la forma única), `LSP: 1`.
   - `relacion comillas`: `RelacionMalDeclarada`, `LSP: 1`.
   - `relacion unidad_corchetes`: `RelacionMalDeclarada`, `LSP: 1`.
   - `macro version`: `MacroMalDeclarada` (fuera de la forma única), `LSP: 1`.
   - `macro invocacion_argumentos`: `MacroMalDeclarada` (`ErrorSintaxis`), `LSP: 1`.

3. **Árboles y órdenes**:
   - `dos_donde` vs `donde ... y ...`: producen árboles sintácticos distintos en el pipeline (`["donde", ...], ["donde", ...]` vs `["donde", ["y", ...]]`), y ambos roundtripean idénticos con su respectivo impresor (`a1 == a2` da `False`; `imprimir(a1) == m1` y `imprimir(a2) == m2` dan `True`).
   - `ambito` omitido: genera su propio árbol impreso.
   - Orden de campos en relación, columnas en tabla y relaciones de evidencia: pertenecen al árbol y se preservan.
   - Orden en `origen`: el impresor normaliza al orden canónico fijo, por lo que cualquier variación de orden no coincide con el impresor y es rechazada por `error_forma`.

4. **Comportamiento ante CLI, MCP y LSP**:
   Sobre una medida con espacios adicionales en encabezado (`medida   demo.prueba:`):
   - `python3 tools/sintaxis.py --leer`: informa `fuera de la forma única`, código 1.
   - `python3 tools/cli.py medida revisar`: informa `fuera de la forma única`, código 1.
   - `python3 tools/cli.py medida probar --con '[]'`: informa `fuera de la forma única`, código 1.
   - `python3 tools/medida.py --expandir`: falla cerrado con `MedidaMalDeclarada: fuera de la forma única`, código 1.
   - `python3 tools/cli.py formatear`: responde `requiere formato`, código 0.
   - MCP `_medida_en_memoria`: levanta `ErrorHerramienta MEDIDA_INVALIDA — <texto de medida>: fuera de la forma única`.
   - LSP: 1 diagnóstico («Versión formateada»), 0 lentes de código.

5. **Suite de verificación y catálogo**:
   - `python3 tools/sintaxis.py --verificar`: 63 medidas, 6 macros, 217 casos, 13 relaciones convertidas; ida JSON OK, vuelta texto OK, forma única OK, 24 bloques de documentación verificados.
   - `python3 tools/cli.py test --rapido`: VEREDICTO: VERDE.
   - Aclaración sobre ejecución de tests unitarios: en la corrida de `python3 -m unittest discover -s tests`, 2 de 2647 tests fallaron (`test_cli_integracion.EmpaquetadoCliTests.test_wheel_instalado_trae_datos_y_ejecuta_oracle_test` y `test_enlaces_pypi.EnlacesDePyPI.test_el_wheel_conserva_los_enlaces_del_readme`) debido a la ausencia de `setuptools` en el intérprete global `/usr/local/bin/python3`. Los tests que evalúan la forma única (`test_forma_unica_texto.py`, `test_ensenanza_una_sintaxis.py`, `test_sondear_procedencia.py`, `test_nueva_con_casos.py`) pasaron al 100%.

## Enseñanza, paquete y plantilla

- `python3 tools/cli.py --help`: explicita que `formatear` conserva líneas `#` y presenta los comandos de autoría en superficie.
- `python3 tools/cli.py manual aritmetica`: enseña `a - b` y aclara expresamente que `a-b` queda fuera de la forma única.
- `python3 tools/cli.py contexto --compacto`: lista las medidas y relaciones vigentes en superficie.
- `NOTAS-DE-RELEASE.md` y `docs/notas.html`: contienen la aclaración explícita sobre `t1.turno - 1` desde sintaxis 1.0 (Oracle 0.32.0).
- Empaquetado: ejecuté `UV_CACHE_DIR=/tmp/oracle-audit15-uv-cache uv build --out-dir /tmp/oracle-audit15-dist`. Se construyeron sdist y wheel (`oracle_metalenguaje-0.31.1-py3-none-any.whl`). Inspeccioné el wheel con `zipfile.ZipFile`: no contiene medidas, casos ni relaciones en JSON; únicamente `oracle.json` como archivo de configuración.
- Instalación limpia: en `/tmp/oracle-audit15-venv` instalé el wheel mediante `pip install --no-index --no-deps`. Ejecuté `oracle plantilla sensor-prosa /tmp/oracle-audit15-template` y `oracle test --rapido --proyecto /tmp/oracle-audit15-template`: la plantilla se desplegó en superficie única (1 medida `.oracle`, 15 casos `.caso`, 1 relación `.relacion`) y concluyó en `VEREDICTO: VERDE`. Limpié el directorio `oracle_metalenguaje.egg-info` generado en el worktree por el build de `uv`.

## Tabla final

| Frente / Punto | Estado observado | Evidencia ejecutada |
|---|---|---|
| Productores en `tools/`, `ejemplo/` y `perfiles/` | Conforme; hallazgo 14 cerrado | `tools/sondear_procedencia.py` escribe 3 casos `.caso` válidos; barrido integral AST/léxico confirmó que ningún script produce medidas, casos, relaciones o macros en JSON. |
| Inserción exhaustiva de comentarios en las cuatro superficies | Conforme; regla léxica cumplida universalmente | 680/680 sondas en 11 archivos estructuralmente diversos: mismo árbol, coincidencia con impresor, cargadores OK, `formatear --escribir` conserva intacto, LSP=0. Prosa con `#` rechazada al imprimir; inline `#` rechazado al leer. |
| Variantes léxicas y de borde (CRLF, sin LF, blancos, BOM, vacíos) | Rechazados por los cargadores | Matrices reejecutadas en las 4 superficies: error de forma o de sintaxis; LSP=1 diagnóstico. |
| Variantes sintácticas históricas (AUDITORIA-2 a -14) | Rechazadas por cargadores y herramientas | Triple espacio, versión, científica, resta pegada, paréntesis, agrupar invertido, origen invertido, operadores funcionales, comillas y corchetes rechazados; LSP=1. |
| Árboles y órdenes semánticos (`donde`, `ambito`, claves/columnas) | Árboles canónicos propios bajo el criterio público | `dos_donde` vs `y` generan ASTs distintos; orden de campos y columnas pertenecen al árbol; `origen` de caso exige orden canónico fijo. |
| Herramientas de entrada: CLI, MCP y LSP | Rechazo estricto de textos no canónicos | `sintaxis.py --leer`, `medida revisar`, `medida probar`, `medida --expandir`, `formatear`, `_medida_en_memoria` y `lsp.lentes` rechazan o no activan sobre variantes no formateadas. |
| Verificación del repositorio y catálogo | Conforme | `sintaxis.py --verificar` OK (63 medidas, 6 macros, 217 casos, 13 relaciones); `cli.py test --rapido` VEREDICTO: VERDE. |
| Documentación, manual, contexto y notas históricas | Sin segunda enseñanza vigente | `cli.py --help`, `manual aritmetica`, `contexto --compacto`, `NOTAS-DE-RELEASE.md` y `docs/notas.html` conformes. |
| Wheel y plantilla `sensor-prosa` | Conforme | Build con `uv`, inspección ZipFile sin JSON espurio, instalación en venv limpio y `oracle test --rapido` en verde sobre la plantilla. |

una sola sintaxis de escritura: sí
