# Auditoría: dónde puede quedar todavía un falso verde en el núcleo

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, auditoria, flaqueza


## Qué hacer

Brian (2026-09-24): «sin puntos flojos». El álgebra 1.0 (tarea `algebra-10`) cierra cuatro falsos
verdes: predicados no booleanos, `null`, claves no validadas y testigos. Buscar los que quedan, en
`nucleo/` (álgebra, medida, proyecto, sintaxis, caso, relación) y en `tools/juzgar.py` y
`tools/aceptacion.py`: todo camino en que una medida, un caso o un proyecto puedan salir VERDE sin
haber medido lo que dicen medir. Por ejemplo: una excepción capturada que se vuelve verde, un valor
por omisión que pasa por medición, una relación vacía sin `requiere`, una comparación que coacciona
tipos. Cada hallazgo con archivo:línea, la entrada concreta que lo dispara y si ya lo cubre un test o
una medida meta. Descartar lo que no se pueda sostener con cita. En `HALLAZGOS.md`.

## Avance

Se completó la auditoría del núcleo y herramientas (`nucleo/` y `tools/`) y se volcaron 8 hallazgos respaldados con cita `archivo:línea`, entrada concreta que los dispara y estado de cobertura en `HALLAZGOS.md`:
1. `nucleo/medida.py:482-484`: `requiere` simple evalúa la verdad de la lista cruda sin llamar a `separar_clave`, por lo que una relación con solo cabecera `["clave", ...]` y 0 filas no activa `faltante` y da verde `<=` 0 en vez de `SIN EVIDENCIA`.
2. `nucleo/algebra.py:1063-1069`: `_unir_donde_indexado` admite tanto `int` como `str` vía `_clave_indexable`, silenciando el `ErrorDeAlgebra` que el camino ingenuo levanta por incompatibilidad de tipos escalares (`nucleo/algebra.py:372-374`), produciendo 0 filas y verde.
3. `nucleo/medida.py:705-707` y `tools/juzgar.py:340-348`: `Informe.perdona` no revisa `sin_evidencia`, perdonando como deuda de código una ausencia total de evidencia cuando la medida en sombra tiene cota >= 0.
4. `nucleo/macros/ninguno.oracle:4-12`, `peor.oracle:4-12`, `ninguno-par.oracle:4-14`: macros base de la biblioteca estándar emitidas sin cláusula `requiere`, dando verde con relación vacía.
5. `nucleo/algebra.py:591-592`: `_agregar` retorna `0` predeterminado para `max`, `min` y `promedio` ante listas vacías.
6. `tools/juzgar.py:159-170, 348`: medidas propias del proyecto no aplicadas por falta de relaciones en la evidencia no invalidan `Informe.ok` ni impiden que `juzgar` salga con código 0 (verde global).
7. `nucleo/marco.py:287-289`: `hechos_de_casos` fuerza `dio = esperado` si la medida no existe en el catálogo, dando falso verde en L2 para `meta.el_caso_se_pone_como_debe`.
8. `nucleo/algebra.py:793, 875-876`: `donde` y `sin` evalúan veracidad booleana de Python sin forzar tipo estricto `bool`.

## Próximo paso

Priorizar los hallazgos para su remediación, comenzando por el parche de `separar_clave` en `nucleo/medida.py:482-484` y la validación de coherencia de tipo en `_unir_donde_indexado` (`nucleo/algebra.py:1063-1069`), escribiendo los tests unitarios correspondientes para cada caso.

### Nota (2026-09-25 02:48:12 UTC)

2026-09-25, Claude, verificado ejecutando el núcleo: CONFIRMADOS dos falsos verdes. (1) requiere con una relación que trae sólo la cabecera ["clave", ["id"]] y ningún hecho no sale SIN EVIDENCIA: con umbral <= 0 da VERDE (ok=True, valor 0). (2) unir … donde con == entre un número y un texto: el camino indexado no encuentra la pareja y da VERDE en silencio, cuando el mismo == en un donde suelto es ErrorDeAlgebra por tipos incompatibles. El 8 ya está en algebra-10. El 7 es deliberado y está documentado en nucleo/marco.py (de la falta se ocupa otra medida). 3 (la sombra perdona un sin_evidencia), 4 (las macros base sin requiere), 5 (agregados sobre cero filas dan 0, que dice la especificación) y 6 (medidas no aplicadas que no invalidan el veredicto) son preguntas de diseño, no defectos comprobados: van a Brian con recomendación.
