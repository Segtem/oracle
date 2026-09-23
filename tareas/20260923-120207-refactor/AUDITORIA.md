# Auditoría de lo que sobra

Fecha: 2026-09-23. Tarea: `20260923-120207-refactor`, sólo punto 1.

**Nueve hallazgos comprobados de duplicación; 126 líneas netas potencialmente
borrables. No se modificó código productivo, el lenguaje ni el contrato MCP.**
No se hicieron commits ni se cerró la tarea.

Se empezó por `tools/mcp.py`: lectura de declaraciones, carga, huellas,
estabilidad, evaluación y traducción de errores. Además se compararon por AST
los cuerpos de funciones de todos los `.py` de `nucleo/` y `tools/` (ignorando
docstrings y nombres de función). Las dos familias adicionales encontradas se
revisaron con sus dependencias. Esto no certifica ausencia de otras redundancias.

## Evidencia y criterio de conteo

Desde la raíz:

```sh
python3 -B tareas/20260923-120207-refactor/verificar_auditoria.py
```

El script sólo lee y analiza fuentes; no importa módulos productivos ni escribe
archivos. Falla si los bloques citados dejan de ser iguales. Para M1–M5 también
construye las declaraciones en memoria y compara su JSON completo **por bytes**,
sin ordenar claves. Resultado observado: nueve comprobaciones OK; SHA256 del JSON
de las cinco herramientas:
`ba56e283a38179e3fdcfe9391bd3096fb96e33f6149edfdcdf8d8442db0ddbac`.

Los números son líneas físicas de los bloques indicados, inclusivas, menos las
líneas de sustitución. No se cuentan dos veces subbloques anidados. Para cada
constante o función nueva se presupuestan dos líneas separadoras. Se conservan
los comentarios explicativos de M6. Los números describen una extracción
concreta posible, no una reducción ya implementada ni una garantía de equivalencia
de un refactor futuro.

Orden: MCP primero, por ahorro neto descendente; después núcleo, priorizando
menor riesgo antes que una línea adicional de ahorro.

## Hallazgos en tools/mcp.py

### M1. Especificación de medida repetida — 32 líneas netas; riesgo bajo

- **Archivo:línea:** `tools/mcp.py:150–173` y `tools/mcp.py:261–296`.
- **Qué sobra:** dos diccionarios `oneOf` idénticos para elegir medida por id o
  por texto/formato; la segunda copia ocupa más por su disposición en líneas.
- **Evidencia:** M1 del script compara ambos AST completos; M1–M5 verifica además
  que reutilizar una definición conserva los bytes de todas las declaraciones.
- **Borrado:** reemplazar 60 líneas por una definición de 24, dos referencias y
  dos separadoras: `60 − (24 + 2 + 2) = 32`.
- **Riesgo:** evitar compartir identidad mutable entre herramientas; usar copias
  profundas. Mantener `oneOf`, claves, orden y cierre de propiedades tal como están.

### M2. Anotaciones idénticas en cinco herramientas — 17 líneas netas; riesgo bajo

- **Archivo:línea:** `tools/mcp.py:51–56`, `139–144`, `248–253`, `513–518`, `664–669`.
- **Qué sobra:** cinco copias del mismo conjunto de cuatro indicadores MCP.
- **Evidencia:** M2 compara los cinco AST; comparación conjunta por bytes M1–M5.
- **Borrado:** `30 − (6 de definición + 5 referencias + 2 separadoras) = 17`.
- **Riesgo:** copiar el diccionario para conservar independencia. No eliminar
  indicadores del protocolo: lo redundante es su escritura en Python.

### M3. Esquema de umbral triplicado — 17 líneas netas; riesgo bajo

- **Archivo:línea:** `tools/mcp.py:112–122`, `204–214`, `588–598`.
- **Qué sobra:** la misma declaración cerrada de `operador`, `valor`, `segun` y
  `porque` en catálogo, evaluación y juicio.
- **Evidencia:** M3 compara los tres AST; comparación conjunta por bytes M1–M5.
- **Borrado:** `33 − (11 de definición + 3 referencias + 2 separadoras) = 17`.
- **Riesgo:** conservar el tipo unión de `valor`, los campos requeridos y las
  copias independientes. Esto no unifica los valores de umbral de las respuestas.

### M4. Definición de evidencia triplicada — 15 líneas netas; riesgo bajo

- **Archivo:línea:** `tools/mcp.py:176–184`, `331–341`, `536–544`.
- **Qué sobra:** tres bloques `$defs` iguales que describen evidencia como objeto
  de arrays de objetos.
- **Evidencia:** M4 compara AST completos del bloque `$defs`, no sólo sus hojas;
  comparación conjunta por bytes M1–M5.
- **Borrado:** `29 − (9 de definición + 3 referencias + 2 separadoras) = 15`.
- **Riesgo:** mantener la definición dentro de cada `inputSchema`; trasladarla a
  otra ubicación JSON cambiaría la resolución de `$ref`. Compartir sólo la fuente
  Python, copiando la estructura en cada ubicación original.

### M5. Esquema de sombra duplicado — 12 líneas netas; riesgo bajo

- **Archivo:línea:** `tools/mcp.py:215–230` y `599–614`.
- **Qué sobra:** dos declaraciones idénticas de sombra nula u objeto con cuatro
  campos obligatorios.
- **Evidencia:** M5 compara ambos AST; comparación conjunta por bytes M1–M5.
- **Borrado:** `32 − (16 de definición + 2 referencias + 2 separadoras) = 12`.
- **Riesgo:** conservar nulabilidad de sombra y de cota, y copiar profundamente.

**Subtotal M1–M5: 92 líneas netas**, descontando además una línea compartida para
importar `deepcopy`. Las copias profundas conservan independencia de objetos.
El JSON queda igual: **ahorro de tokens del anuncio MCP demostrado: cero**.
La mejora aquí es mantener una sola definición de cada estructura.

### M6. Traducción de escalares no autorizadas cuadruplicada — 11 líneas netas; riesgo bajo a medio

- **Archivo:línea:** `tools/mcp.py:1236–1247`, `1515–1520`, `1589–1595`, `1748–1754`.
- **Qué sobra:** cuatro handlers con exactamente el mismo cálculo de archivo,
  código, mensaje y encadenamiento de excepción.
- **Evidencia:** M6 compara los cuatro `ExceptHandler` completos por AST.
  Los comentarios y el formato explican sus diferentes tamaños físicos.
- **Borrado:** 32 líneas originales frente a 8 para los cuatro handlers que
  delegan, 6 para un auxiliar que recibe `e` y lanza el mismo error, 5 para
  conservar el comentario de `partition` y 2 separadoras: `32 − 21 = 11`.
- **Riesgo:** mantener `raise ... from e`, `partition` y el orden de captura.
  Aparecería un marco adicional en el traceback. No agrupar los demás handlers:
  sus políticas ante errores generales difieren.

### M7. Carga protegida de catálogo repetida — 6 líneas netas; riesgo bajo a medio

- **Archivo:línea:** `tools/mcp.py:1481–1486`, `1545–1550`, `1682–1687`.
- **Qué sobra:** el mismo `try` de carga, propagación de `ProyectoInvalido` y
  traducción del resto mediante `_error_catalogo` en tres operaciones.
- **Evidencia:** M7 exige igualdad AST de los tres `Try` completos, incluidos
  argumentos de carga y orden de excepciones.
- **Borrado:** 18 líneas frente a un auxiliar de 7 que devuelve el catálogo,
  3 llamadas y 2 separadoras: `18 − 12 = 6`.
- **Riesgo:** mantener la carga en su posición actual dentro del contexto de
  escalares y recibir las macros ya calculadas. No ampliar la extracción al
  `try` de `tools/mcp.py:1188`: también abarca la carga de macros y no es idéntico.

## Hallazgos en nucleo/

### N1. Formateador de vocabulario duplicado — 8 líneas netas; riesgo bajo

- **Archivo:línea:** `nucleo/caso.py:82–90`; copia existente en
  `nucleo/vocabulario.py:18–26`.
- **Qué sobra:** implementación local de `opciones`; sólo utiliza `sorted` y su
  argumento, con el mismo cuerpo que el formateador compartido.
- **Evidencia:** N1 compara cuerpos AST excluyendo docstrings. Para localizar
  consumidores: `rg -n '\bopciones\b' nucleo/caso.py nucleo/vocabulario.py
  nucleo/medida.py nucleo/sintaxis.py tests/test_vocabulario.py tests/test_sintaxis.py`.
  `caso.py:419,425,431` usa el nombre local; no es código muerto.
- **Borrado:** 9 líneas de función reemplazadas por una importación de
  `.vocabulario`: 8 netas. Conservar `caso.opciones` como nombre importado.
- **Riesgo:** cambia la identidad y la anotación introspectable de la función
  (`dict` frente a `dict[str, str]`); no cambia el texto que produce. El módulo
  compartido no importa `caso`, por lo que esta dependencia no crea un ciclo.

### N2. Auxiliares de indentación copiados — 9 líneas netas; riesgo medio

- **Archivo:línea:** `nucleo/caso.py:97–108`; originales equivalentes en
  `nucleo/sintaxis.py:129–132` y `488–493`.
- **Qué sobra:** implementaciones duplicadas de `_fallar` y `_indentada`.
- **Evidencia:** N2 compara las funciones completas, incluidos argumentos y
  valores por defecto; comprueba el mismo `IND` y que `caso` ya importa la clase
  `ErrorSintaxis` de `sintaxis`. Usos reproducibles:
  `rg -n '\b(_fallar|_indentada)\b' nucleo/caso.py nucleo/sintaxis.py`.
- **Borrado:** 4 + 6 líneas de funciones, sustituidas por una importación de
  ambos nombres desde `.sintaxis`: 9 netas. No se cuentan las líneas vacías
  existentes ni se propone borrar `IND`, que tiene otros usos.
- **Riesgo:** dependencia de auxiliares privados y cambio del módulo de globals
  al ejecutarlos; hay que revisar consumidores que parcheen `caso._fallar` o
  `caso.IND`. Igualdad de implementación actual demostrada, compatibilidad frente
  a monkeypatching externo no demostrada. Prioridad posterior a N1.

## Descartes y límites

- No se declara código muerto por falta de llamadas internas: hay funciones
  públicas, entradas de CLI y consumidores externos. Tampoco se considera
  sobrante una abstracción sólo porque tenga un único uso.
- No se equiparan `_entradas_de_huella` y `_rutas_de_evaluacion`: reúnen fuentes
  diferentes. Tampoco se equiparan enteros `_estado_estable` y
  `_evaluacion_estable`: difieren en el valor cedido y en las huellas invocadas.
- `_desafiar` descarta el detalle de `observar` (`_detalle`, `_d`), pero eliminar
  su formato de excepción puede cambiar efectos de `str(e)`; no se incluye
  como borrado probado.
- `estudios/MCP-CONTRATO.md` contiene una copia **generada** de las herramientas;
  `tools/mcp_contrato.py:9–15` y su `--check` le dan una función verificable.
  No se cuenta el documento como duplicación borrable.
- No se ejecutó mutación ni se afirma que exista una rama irrelevante por tener
  un mutante vivo. No se inventó evidencia de supervivencia. Todos los hallazgos
  aceptados son duplicaciones demostradas por el script.
- La comprobación ejecutada es la evidencia de auditoría, no la suite de un
  refactor. El punto 2 sigue pendiente: suite y mutación del módulo antes y
  después de cualquier cambio autorizado. Esta auditoría no cambia el lenguaje
  ni propone quitar validaciones o campos de las herramientas.
