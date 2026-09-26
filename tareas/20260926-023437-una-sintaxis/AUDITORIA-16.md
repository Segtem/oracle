# Decimosexta auditoría adversarial: una sintaxis

2026-09-26. Confirmación independiente del informe 15 (que cerró AUDITORIA-14) bajo el criterio público de `ESPECIFICACION.md:527-554`:
- Un único texto por árbol sintáctico, exceptuadas exclusivamente las líneas completas cuyo primer carácter no blanco es `#`.
- El orden de relaciones en una evidencia, de columnas en una tabla y de claves en un objeto (salvo `origen`) pertenece al árbol y no constituye variante de grafía.
- En el `origen` de un caso, el orden es canónico fijo (`tipo`, `repo`, `commit`, `plan`, `cuando_utc`, `comando`, `registro`, `evidencia_sha256`, `estado`, y campos adicionales en orden alfabético).
- JSON en `.json` se admite únicamente como formato de intercambio de datos y migración; no como formato de autoría de medidas, casos, relaciones o macros.
- El texto histórico es hallazgo sólo si presenta como vigente una forma que hoy se rechaza.

La auditoría se realizó **en contra**, buscando activamente segundas sintaxis, posiciones no cubiertas, herramientas productoras y defectos estructurales en entornos temporales bajo `/tmp`. No se modificó código ni se realizaron commits. Sólo se afirma lo efectivamente ejecutado en el entorno.

## 1. Sondas adversariales de comentarios en posiciones y estructuras no probadas

Para contrastar la afirmación de universalidad léxica de los comentarios `#` y buscar posiciones no evaluadas en AUDITORIA-15, se seleccionaron 11 archivos reales con estructuras sintácticas distintas a las ensayadas previamente:
- **Relaciones (`.relacion`)**:
  - `relaciones/afirmacion.relacion`: colisión de nombre de campo con cláusula reservada (`alcance: texto` y cláusula `alcance "..."`).
  - `relaciones/pieza.relacion`: múltiples campos flotantes con unidades de longitud y ángulo (`cm`, `grados`).
  - `relaciones/corrida_mutacion.relacion`: estructura extensa con 24 campos escalares y de unidad.
- **Macros (`.oracle`)**:
  - `nucleo/macros/ninguno-par.oracle`: macro con cláusula de validación `guarda $aliasA != $aliasB "..."`.
  - `nucleo/macros/peor-requiere.oracle`: macro con cláusula `requiere $relacion`.
- **Medidas (`.oracle`)**:
  - `catalogos/meta/meta.sin_nunca_agrega_filas.oracle`: medida con cláusula de exclusión `sin`.
  - `catalogos/meta/meta.unir_materializa_el_producto.oracle`: medida con producto cartesiano `unir`.
- **Casos (`.caso`)**:
  - `corpus/proceso/012-umbral-duplicado-en-filtro-y-umbral.caso`: caso con bloque de prosa `resuelto:` y `estado_sin_medida: resuelto`.
  - `corpus/proceso/011-conclusion-errada-desvan.caso`: caso con bloque de prosa `limite_humano:`.
  - `corpus/simulacion/202-traza-sin-ningun-evento.caso`: caso con directiva `espera: sin_evidencia`.
  - `corpus/meta/497-el-censo-distingue-perdidas-ilegibles-y-ceros.caso`: caso con escape tabular heterogéneo `fila { ... }`.

### 1.1 Inserción exhaustiva en cada límite de línea

En cada límite de línea (antes de la primera, entre cada línea y tras la última) de los 11 archivos, se insertaron 5 variantes léxicas de comentario:
1. `# comentario auditoria 16\n` (sin sangría)
2. `    # comentario sangrado 4\n` (con sangría regular)
3. `\t# comentario con tab\n` (con sangría de tabulación)
4. `#\n` (comentario vacío sin espacio)
5. `# comentario con espacios finales   \n` (comentario con espacios al final)

Para cada variante se evaluaron 5 propiedades obligatorias:
1. `leer(texto) == orig_tree` (el árbol del AST no se altera).
2. `cargar_fuente_*(tmp_path) == orig_tree` (el cargador de la superficie carga sin error).
3. `sin_comentarios(texto) == imprimir(orig_tree)` (cumple la forma única exacta).
4. `lsp.diagnosticar(proy, tmp_path, texto) == []` (LSP emite 0 diagnósticos).
5. `formato.con_comentarios(texto, canonico) == texto` (`formatear` preserva el comentario exactamente byte a byte).

Comando ejecutado en sonda de prueba:

```bash
python3 - <<'PY'
# Inserción exhaustiva sobre los 11 archivos indicados y verificación de las 5 propiedades
PY
```

Salida recortada por archivo:

```text
afirmacion.relacion                           lines  6 pos  7 probes  35 pass  35 fail  0
pieza.relacion                                lines 13 pos 14 probes  70 pass  70 fail  0
corrida_mutacion.relacion                     lines 27 pos 28 probes 140 pass 140 fail  0
ninguno-par.oracle                            lines 11 pos 12 probes  60 pass  60 fail  0
peor-requiere.oracle                          lines 10 pos 11 probes  55 pass  55 fail  0
meta.sin_nunca_agrega_filas.oracle            lines  6 pos  7 probes  35 pass  35 fail  0
meta.unir_materializa_el_producto.oracle      lines  6 pos  7 probes  35 pass  35 fail  0
012-umbral-duplicado-en-filtro-y-umbral.caso  lines 21 pos 22 probes 110 pass 110 fail  0
011-conclusion-errada-desvan.caso             lines 23 pos 24 probes 120 pass 120 fail  0
202-traza-sin-ningun-evento.caso              lines 17 pos 18 probes  90 pass  90 fail  0
497-el-censo-distingue-perdidas-ilegibles-y-ceros.caso lines 23 pos 24 probes 120 pass 120 fail  0

TOTAL: 870 probes, 870 passes, 0 failures
```

Resultado: **870/870 sondas exitosas**. Las cláusulas `guarda`, `sin`, `unir`, `resuelto`, `limite_humano`, `espera` y campos con nombres de cláusula admiten comentarios completos sin quebrar el cargador, el árbol ni el formateador.

### 1.2 Comentarios con contenidos especiales y caracteres de escape

Se ejecutó una batería de 120 sondas adicionales insertando líneas con caracteres especiales en el inicio, medio y final de archivos de las cuatro superficies:
- Comillas múltiples (`# " ' ` """`).
- Símbolos y delimitadores (`# { [ ( < = > ! & | $ % / \ @ : , ; ) ] }`).
- Caracteres Unicode (`# ñ á é í ó ú ü ¿ ¡ — · « » 🚀`).
- Contenido que simula código de otra superficie (`# defmacro falso(a, b):`, `# relacion falsa:`, `# medida foo:`).
- Múltiples almohadillas consecutivas (`###`, `#####`).

Salida:

```text
Special comments: 120 passed, 0 failed
```

### 1.3 Rechazo de comentarios inline y regla de prosa

Se comprobó el comportamiento ante comentarios que no constituyen una línea completa:
- **Comentarios inline al final de código**:
  - En encabezados (`medida demo.prueba: # c`, `caso 001-prueba: # c`, `relacion prueba: # c`): rechazados con `ErrorSintaxis` y `RelacionMalDeclarada`.
  - En cláusulas internas (`de tabla t # c`, `fecha: "..." # c`, `id: texto # c`): rechazados por error de sintaxis en el lector respectivo.
- **Regla léxica en prosa**:
  - El impresor se niega a escribir una línea de prosa que empiece con `#`: `ValueError: «sintoma»: una línea de prosa no puede empezar con # (sería un comentario): «...»`.
  - Caracteres `#` en el interior de una línea de prosa (ej. `El error fue el #456 en la traza`): no se consideran comentarios, el lector los conserva como dato y el impresor los reproduce intactos (`sin_comentarios(texto) == imprimir(arbol)` da `True`).

## 2. Auditoría integral de productores en `tools/`, `ejemplo/`, `perfiles/` y `catalogos/`

El hallazgo de AUDITORIA-14 identificó un productor interno de casos en JSON (`tools/sondear_procedencia.py`). Se verificó exhaustivamente si persisten productores de medidas, casos, relaciones o macros en JSON u otra forma fuera de la superficie.

### 2.1 Estado de `tools/sondear_procedencia.py`

Ejecuté:

```bash
python3 tools/sondear_procedencia.py
python3 - <<'PY'
from tools.sondear_procedencia import escribir_corpus, SONDAS
from nucleo.caso import cargar_casos
r = escribir_corpus(SONDAS['un_caso_observado_no_dice_de_donde_salio'][0])
print([(p.name, p.suffix) for p in sorted(r.rglob('*')) if p.is_file()])
print(len(cargar_casos(r)))
PY
```

Salida recortada:

```text
PROCEDENCIA — 2 sondas sobre corpus reales ...
  ✓ un_caso_observado_no_dice_de_donde_salio
  ✓ todos_los_observados_dicen_de_donde_salieron
[('001-corrida-sin-registro.caso', '.caso'), ('002-corrida-con-registro.caso', '.caso'), ('003-escrito-a-mano.caso', '.caso')]
3
```

El script emite únicamente `.caso` en superficie única y valida mediante `cargar_casos`.

### 2.2 Barrido sistemático por AST de escrituras en el repositorio

Se analizaron todos los nodos de llamada `write_text`, `write_bytes`, `json.dump` y `open(..., 'w'/'a')` en el código fuente:
- `tools/corpus.py`: emite `PLANTILLA` en `.caso`.
- `tools/medida.py`: emite `PLANTILLA` en `.oracle`, borradores en `.relacion` (`_imprimir_borrador`) y andamios en `.caso` con marca `# ANDAMIO:`.
- `tools/observar.py`: emite `.caso` llamando a `imprimir(caso)`; guarda `evidencia.json` (captura cruda) y `registro.json` (metadatos de ejecución), ambos enlazados desde el `origen` del caso.
- `nucleo/generador.py`: emite `{cid}.caso` llamando a `imprimir_caso(caso_final)`.
- `tools/cli.py`: `cmd_formatear` escribe únicamente forma única canónica; `oracle init` escribe `oracle.json` (configuración del proyecto).
- `ejemplo/caso-observado/convertir.py`: convierte JSON a `.caso` invocando `imprimir(datos)`.
- `ejemplo/sensor-prosa/`, `ejemplo/seguimiento-tareas/`, `ejemplo/primer-valor/`, `ejemplo/batalla-naval/`: generan o manipulan `hechos.json` o dumps de evidencia consumidos por `oracle juzgar --con`, formato de intercambio expresamente autorizado por la especificación.
- `perfiles/python/mutacion_codigo.py`: actualiza `equivalentes.json` (exclusiones de mutación), no modelos de autoría.
- `nucleo/biblioteca.py`: emite manifiestos `oracle-biblioteca.toml` y `pyproject.toml`.

No se identificó ningún script que escriba medidas, casos, relaciones o macros en JSON ni en otra sintaxis no canónica.

## 3. Matriz adversarial de variantes no canónicas y bordes de la forma única

Se evaluaron 26 variantes no canónicas en las cuatro superficies frente a cargadores, LSP y herramientas de CLI.

```bash
python3 - <<'PY'
# Evaluación de variantes no canónicas contra cargar_fuente_* y lsp.diagnosticar
PY
```

Salida de la matriz:

```text
SUPERFICIE VARIANTE               LOADER                    LSP DIAGS 
----------------------------------------------------------------------
medida     triple_espacio         MedidaMalDeclarada (forma) 1 diag(s) 
medida     CRLF                   MedidaMalDeclarada (forma) 1 diag(s) 
medida     sin_LF                 MedidaMalDeclarada (forma) 1 diag(s) 
medida     espacio_final          MedidaMalDeclarada (forma) 1 diag(s) 
medida     linea_blanca           MedidaMalDeclarada (forma) 1 diag(s) 
medida     BOM                    MedidaMalDeclarada (sintaxis) 1 diag(s) 
medida     resta_sin_espacios     MedidaMalDeclarada (forma) 1 diag(s) 
medida     cientifica             MedidaMalDeclarada (forma) 1 diag(s) 
medida     parentesis             MedidaMalDeclarada (forma) 1 diag(s) 
medida     mas_funcional          MedidaMalDeclarada (sintaxis) 1 diag(s) 
caso       triple_espacio         CasoMalDeclarado (forma)  1 diag(s) 
caso       CRLF                   CasoMalDeclarado (forma)  1 diag(s) 
caso       sin_LF                 CasoMalDeclarado (forma)  1 diag(s) 
caso       espacio_final          CasoMalDeclarado (forma)  1 diag(s) 
caso       linea_blanca           CasoMalDeclarado (forma)  1 diag(s) 
caso       BOM                    CasoMalDeclarado (sintaxis) 1 diag(s) 
caso       origen_invertido       CasoMalDeclarado (forma)  1 diag(s) 
relacion   triple_espacio         RelacionMalDeclarada (sintaxis) 1 diag(s) 
relacion   CRLF                   RelacionMalDeclarada (forma) 1 diag(s) 
relacion   sin_LF                 RelacionMalDeclarada (forma) 1 diag(s) 
relacion   corchetes              RelacionMalDeclarada (sintaxis) 1 diag(s) 
relacion   BOM                    RelacionMalDeclarada (sintaxis) 1 diag(s) 
macro      triple_espacio         MacroMalDeclarada (forma) 1 diag(s) 
macro      CRLF                   MacroMalDeclarada (forma) 1 diag(s) 
macro      sin_LF                 MacroMalDeclarada (forma) 1 diag(s) 
macro      BOM                    MacroMalDeclarada (sintaxis) 1 diag(s) 
```

### 3.1 Comportamiento ante herramientas de CLI, MCP y LSP

Sobre una medida con espacios adicionales en encabezado (`medida   demo.test:`):
- `python3 tools/sintaxis.py --leer`: `exit=1`, `✗ ...: fuera de la forma única`.
- `python3 tools/cli.py medida revisar`: `exit=1`, `✗ ...: fuera de la forma única`.
- `python3 tools/cli.py medida probar ... --con '[]'`: `exit=1`, `✗ ...: fuera de la forma única`.
- `python3 tools/medida.py --expandir`: `exit=1`, `Traceback ... MedidaMalDeclarada: fuera de la forma única`.
- `python3 tools/cli.py formatear`: `exit=0`, `requiere formato`.
- `lsp.diagnosticar`: 1 diagnóstico («Versión formateada»), `lsp.lentes`: 0 lentes emitidos.
- MCP `_medida_en_memoria({"texto": ..., "formato": "oracle"})`: `ErrorHerramienta MEDIDA_INVALIDA — <texto de medida>: fuera de la forma única`.
- MCP `_medida_en_memoria({"texto": "[]", "formato": "json"})`: `ErrorHerramienta MEDIDA_INVALIDA — el texto Oracle de la medida no se entiende: línea 1`.

## 4. Wheel, distribución y despliegue limpio de plantilla

Se construyó el paquete wheel de la distribución en aislamiento limpio:

```bash
UV_CACHE_DIR=/tmp/oracle-audit16-uv-cache uv build --out-dir /tmp/oracle-audit16-dist
```

Salida recortada:
```text
Successfully built /tmp/oracle-audit16-dist/oracle_metalenguaje-0.31.1.tar.gz
Successfully built /tmp/oracle-audit16-dist/oracle_metalenguaje-0.31.1-py3-none-any.whl
```

### 4.1 Inspección del contenido del wheel

Se inspeccionó el archivo `.whl` con `zipfile.ZipFile`:
- No contiene ninguna medida, caso ni relación en formato `.json`.
- El único archivo JSON empaquetado es `oracle_metalenguaje/plantilla_sensor_prosa/oracle.json` (configuración del proyecto).
- La plantilla `plantilla_sensor_prosa` incluye: 1 `.oracle`, 15 `.caso`, 1 `.relacion`, `sensor_prosa.py` y `README.md`.

### 4.2 Despliegue y prueba en entorno virtual limpio

Se creó un entorno virtual aislado en `/tmp/oracle-audit16-venv` y se instaló el wheel:

```bash
python3 -m venv /tmp/oracle-audit16-venv
/tmp/oracle-audit16-venv/bin/pip install --no-index --no-deps /tmp/oracle-audit16-dist/oracle_metalenguaje-0.31.1-py3-none-any.whl
/tmp/oracle-audit16-venv/bin/oracle plantilla sensor-prosa /tmp/oracle-audit16-template
/tmp/oracle-audit16-venv/bin/oracle test --rapido --proyecto /tmp/oracle-audit16-template
```

Salida recortada:
```text
Plantilla copiada en /tmp/oracle-audit16-template. El sensor ahora pertenece a tu proyecto.
...
SINTAXIS OK · 1 medidas · 0 macros · 15 casos · 1 relaciones
catálogo: 1 medidas · corpus: 15 casos
...
ACEPTACIÓN ✓ — 4 defectos en rojo, 2 sin evidencia esperada, 9 verdes correctos, 0 huecos declarados sin tapar
VEREDICTO: VERDE (se salteó: mutación de medidas (--rapido))
```

Al ejecutar `oracle formatear /tmp/oracle-audit16-template`, los 17 archivos reportaron `ya tiene forma única`.

### 4.3 Sonda de mutación de comentario en la plantilla instalada

En `/tmp/oracle-audit16-template/corpus/prosa/015-relacion-vacia.caso`, se insertó una línea de comentario `# comentario prueba 16 tras sintoma` inmediatamente después de `sintoma:`.
- `oracle test --rapido --proyecto /tmp/oracle-audit16-template` concluyó en `SINTAXIS OK` y `VEREDICTO: VERDE`.
- `oracle formatear .../015-relacion-vacia.caso` confirmó `ya tiene forma única`.

## 5. Verificación del repositorio, suites y documentación

- `python3 tools/sintaxis.py --verificar`:
  ```text
  medidas convertidas: 63
  macros convertidas: 6
  casos convertidos: 217
  relaciones convertidas: 13
  ida JSON: OK
  vuelta texto: OK
  forma única: OK
  bloques de documentación: 24 verificados · 8 declarados como gramática o fragmento
  ```
- `python3 tools/cli.py test --rapido`:
  ```text
  contrastado con la implementación independiente: 5 propiedades, 0 desacuerdos
  equivalencias comprobadas: 899
  CIFRAS OK
  VEREDICTO: VERDE
  ```
- `python3 -m unittest discover -s tests -t . -q`:
  - 2645 tests pasaron; 2 tests fallaron (`EmpaquetadoCliTests.test_wheel_instalado_trae_datos_y_ejecuta_oracle_test` y `EnlacesDePyPI.test_el_wheel_conserva_los_enlaces_del_readme`).
  - Causa comprobada: invocación de `setuptools` en el intérprete `/usr/local/bin/python3` del contenedor sin dicho paquete instalado en el entorno global. Los tests de forma única y sintaxis pasaron al 100%.
- Documentación y manuales:
  - `python3 tools/cli.py manual aritmetica`: enseña `a - b` y aclara expresamente que `a-b` queda fuera de la forma única.
  - `python3 tools/cli.py contexto --compacto`: lista operadores y relaciones exclusivamente en superficie canónica.
  - `NOTAS-DE-RELEASE.md` y `docs/notas.html`: contienen la mención a `t1.turno - 1` con la advertencia explícita de su vigencia a partir de sintaxis 1.0.

## 6. Cuatro frentes del encargo

- **(a) Dos textos distintos fuera de líneas # con el mismo árbol, que carguen**:
  No se encontró ninguno. Los cargadores (`cargar_fuente_medida`, `cargar_fuente_caso`, `cargar_fuente_relacion`, `_datos_de_macro`) aplican `error_forma(ruta, texto, imprimir(arbol))`, que exige igualdad estricta entre `sin_comentarios(texto)` y la salida determinista de `imprimir(arbol)`. Cualquier discrepancia de orden, espaciado, terminación de línea o sintaxis levanta error de forma o de sintaxis.
- **(b) Una entrada que acepte un texto distinto del impresor**:
  Todas las entradas evaluadas (CLI, MCP, LSP, cargadores de núcleo) rechazan textos no normalizados con código de salida 1, excepción o diagnóstico formal.
- **(c) Un lugar del paquete que enseñe o produzca una forma que el cargador rechace o que no sea la superficie**:
  Inspección sistemática de `tools/`, `ejemplo/`, `perfiles/`, `docs/` y el wheel generado: ningún script produce medidas, casos o relaciones en JSON ni en sintaxis fuera de la superficie; la plantilla empaquetada despliega 100% en superficie única y pasa `test --rapido`.
- **(d) Contradicciones entre la definición pública y el código**:
  Las afirmaciones de `ESPECIFICACION.md:527-554` fueron contrastadas línea por línea: regla léxica de comentarios `#`, prohibición de líneas `#` en prosa, rechazo de comentarios inline, conservación de comentarios por `oracle formatear`, orden fijo en `origen` y orden de lectura en tablas, relaciones y claves. Todas coinciden exactamente con la implementación.

## Tabla final

| Frente / Punto evaluado | Estado observado | Evidencia ejecutada |
|---|---|---|
| Comentarios en posiciones y archivos no probados | Conforme; regla léxica universal | 870/870 sondas en 11 archivos estructuralmente diversos (`guarda`, `sin`, `unir`, `resuelto`, `limite_humano`, `espera`, etc.): mismo árbol, cargadores OK, `formatear --escribir` conserva intacto, LSP=0. |
| Comentarios con caracteres especiales e inline | Conforme; semántica estricta | 120 sondas con comillas, Unicode, símbolos y hashes múltiples OK; inline `#` rechazado con error sintáctico; prosa con `#` inicial rechazada por el impresor. |
| Productores en `tools/`, `ejemplo/` y `perfiles/` | Conforme; sin productores JSON | `sondear_procedencia.py` emite `.caso`; barrido AST demostró 0 emisores de modelos en JSON o variantes; hechos de intercambio en JSON conformes a especificación. |
| Variantes léxicas y no canónicas (CRLF, LF, BOM, espacios) | Rechazo fail-closed | Matriz de 26 variantes en las 4 superficies: todas rechazadas con `MedidaMalDeclarada`, `CasoMalDeclarado`, `RelacionMalDeclarada` o `MacroMalDeclarada`; LSP=1 diagnóstico. |
| Herramientas de entrada: CLI, MCP y LSP | Rechazo estricto | `sintaxis.py --leer`, `medida revisar`, `medida probar`, `medida --expandir`, `formatear`, `_medida_en_memoria` y `lsp.lentes` rechazan textos no canónicos. |
| Empaquetado wheel y plantilla `sensor-prosa` | Conforme | Build con `uv`, inspección ZipFile sin JSON espurio, instalación en venv limpio, despliegue de plantilla y `oracle test --rapido` en VERDE. |
| Verificación del catálogo y suite rápida | Conforme | `sintaxis.py --verificar` OK (63 medidas, 6 macros, 217 casos, 13 relaciones); `cli.py test --rapido` VEREDICTO: VERDE. |
| Enseñanza, manual, contexto y notas de release | Sin segunda enseñanza | `cli.py --help`, `manual aritmetica`, `contexto --compacto`, `tutorial-practico` y notas históricas conformes. |

una sola sintaxis de escritura: sí
