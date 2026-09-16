# Avance 0.25.0 — Filtro de sitios y declaración de ronda parcial

**Fecha**: 2026-09-16  
**Tarea**: `tareas/20260915-201030-sitios`  
**Encargo**: `estudios/0.25.0-sitios/ENCARGO-AGY.md`  

---

## 1. Análisis del problema y requerimientos

`tools/mutar_codigo.py --objetivo` sólo permitía acotar a archivos completos. En revisiones o refactorizaciones pequeñas, esto obligaba a esperar la mutación íntegra del archivo (~1 hora por archivo grande) o a mutar manualmente sobre una copia sin registro de ronda.

El encargo exige permitir mutar únicamente una selección de sitios mediante:
1. `--lineas a-b` (rango inclusivo de líneas sobre el objetivo).
2. `--sitio <id>` (identificador canónico `archivo:linea:columna:operador`).
Ambos deben ser repetibles y combinables entre sí y con `--objetivo`. Si el filtro no selecciona ningún sitio en los objetivos, debe fallar con un error explícito (código 2, no ronda vacía en verde).

La segunda mitad crítica del encargo es garantizar que una ronda parcial **no pueda confundirse con una ronda completa**:
- `corrida_mutacion` debe declarar `parcial: bool` y `total_sitios: int` (para que la evidencia se defienda sola y revele el denominador original).
- `relaciones/corrida_mutacion.json` y `CAMPOS_DE_RELACIONES` del emisor deben actualizarse.
- El informe en terminal debe anunciarlo en su **primera línea** y en el **resumen final**.
- El catálogo de proceso no debe aceptar una ronda parcial como completa: `proceso.ronda_mutacion_concluyente` debe clasificar una ronda con `parcial == true` como no concluyente.
- Nuevos casos en `corpus/proceso/` con ambas polaridades.
- Batería de tests unitarios en `tests/test_mutacion_codigo.py`.

---

## 2. Decisiones de diseño y arquitectura

### A. Filtro de sitios en `tools/mutar_codigo.py`
- Se incorporan a `argumentos()`:
  - `--lineas`: repetible (`action="append"`). Formato `inicio-fin` (ej. `10-25`), validando que sean enteros positivos con `inicio <= fin`. También se acepta una línea única `n` interpretada como `n-n`.
  - `--sitio`: repetible (`action="append"`). ID canónico del sitio.
- **Semántica de combinación**:
  - Un sitio `s` es seleccionado si coincide con **cualquiera** de los criterios activos (unión): su línea cae en alguno de los rangos de `--lineas` O su ID coincide con alguno de los `--sitio`.
  - Si no se especifica ni `--lineas` ni `--sitio`, se seleccionan todos los sitios de los objetivos (ronda completa, `parcial = False`).
  - Si se especifican filtros y el número total de sitios seleccionados es 0, se levanta `ValueError` ("el filtro de sitios no seleccionó ningún sitio en los objetivos"), saliendo con código 2 sin ejecutar tests ni reportar un falso verde.

### B. Modificaciones en `perfiles/python/mutacion_codigo.py` (cuidado con la auto-mutación)
- Este módulo es parte de la suite de auto-mutación de Oracle (227 mutantes). Por ende, el código añadido debe ser mínimo, conciso y directo para no generar ramas redundantes o difíciles de matar.
- Parámetro en `_correr_en_raiz` y `correr`: `filtro_sitios: Callable[[Sitio], bool] | None = None`.
- `total_sitios`: cuenta todos los sitios encontrados en los objetivos antes de filtrar.
- `es_parcial = filtro_sitios is not None`.
- Si `filtro_sitios` está activo, se filtran las listas de sitios por objetivo; si ningún sitio pasa el filtro, se levanta `ValueError`.
- En el diccionario emitido `corrida_mutacion[0]`:
  - `"parcial": es_parcial`
  - `"total_sitios": total_sitios`
- En `_identidad_ronda`: se incorpora `"parcial": parcial` para evitar que un manifiesto parcial sea reanudado como completo o viceversa.
- Declaración de `CAMPOS_DE_RELACIONES = {"corrida_mutacion": (...)}` en el emisor.

### C. Esquema `relaciones/corrida_mutacion.json`
- Se añaden los campos `parcial` (tipo `booleano`, unidad `sin_unidad`) y `total_sitios` (tipo `entero`, unidad `sin_unidad`) a la lista de campos de la relación `corrida_mutacion`.

### D. Salida del informe en pantalla en `tools/mutar_codigo.py`
- **Primera línea**: Si la ronda es parcial, imprime inmediatamente un encabezado destacado:
  `*** RONDA PARCIAL DE MUTACIÓN (filtro activo) ***`
- **Resumen**: Imprime:
  `*** RESUMEN: RONDA PARCIAL (X de Y sitios del objetivo) ***`
- **Cierre**: En lugar de afirmar "Todos los mutantes murieron: los tests fijan el código del núcleo.", si la ronda fue parcial aclara:
  `Todos los mutantes probados murieron, pero la ronda fue PARCIAL: se probaron X de Y sitios. Esto NO demuestra que los tests fijen el módulo completo.`

### E. Medidas del catálogo en `catalogos/proceso/`
- **`proceso.ronda_mutacion_concluyente.oracle`**:
  - En su cláusula `donde`: se añade `c.parcial == true o ...`.
  - Una ronda parcial no concluye la verificación del módulo; por tanto, `proceso.ronda_mutacion_concluyente` detecta la fila parcial y evalúa a > 0 (violación del umbral `<= 0`).
  - Se actualizan `porque` y `alcance`.
- **`proceso.codigo_con_mutante_que_lo_mata.oracle`**:
  - Decisión analizada: `mutante` no posee campo `parcial` y `relaciones/mutante.json` es ajeno a la propiedad de Agy. Además, acoplar `codigo_con_mutante_que_lo_mata` a `corrida_mutacion` vía `requiere` rompería los casos existentes del corpus que prueban la detección de mutantes de código de forma aislada (sin tabla `corrida_mutacion`).
  - El propio contrato y `alcance` de `codigo_con_mutante_que_lo_mata` declara explícitamente:
    *«Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío.»*
  - Por tanto, la responsabilidad de rechazar una ronda parcial reside arquitectónicamente en `proceso.ronda_mutacion_concluyente`, preservando la modularidad y evitando romper casos preexistentes.

### F. Casos del corpus en `corpus/proceso/`
- Actualización de los 4 casos existentes que evalúan `proceso.ronda_mutacion_concluyente` (`016`, `017`, `019`, `108`) agregando el campo `parcial: false`.
- Nuevos casos:
  - `111-ronda-mutacion-parcial-no-es-concluyente.caso`: polaridad `falso_verde` (la ronda fue parcial, por lo que `proceso.ronda_mutacion_concluyente` debe dar rojo).
  - `112-ronda-mutacion-completa-concluyente.caso`: polaridad `verde_correcto` (ronda con `parcial: false` y sin incidentes, evalúa verde).

---

## 3. Plan de archivos

| Archivo | Acción | Propiedad |
|---|---|---|
| `relaciones/corrida_mutacion.json` | Modificar: agregar `parcial` y `total_sitios` | Agy |
| `perfiles/python/mutacion_codigo.py` | Modificar: `CAMPOS_DE_RELACIONES`, soporte de `filtro_sitios`, `parcial`, `total_sitios` | Agy |
| `tools/mutar_codigo.py` | Modificar: CLI flags `--lineas`, `--sitio`, validación, informe en primera línea y resumen | Agy |
| `catalogos/proceso/proceso.ronda_mutacion_concluyente.oracle` | Modificar: incorporar `c.parcial == true` en `donde`, actualizar `porque` y `alcance` | Agy |
| `corpus/proceso/016-timeout-contado-como-mutante-muerto.caso` | Modificar: agregar `parcial: false` a `corrida_mutacion` | Agy |
| `corpus/proceso/017-error-de-arnes-contado-como-mutante-muerto.caso` | Modificar: agregar `parcial: false` a `corrida_mutacion` | Agy |
| `corpus/proceso/019-ronda-sin-mutantes-declarada-verde.caso` | Modificar: agregar `parcial: false` a `corrida_mutacion` | Agy |
| `corpus/proceso/108-ronda-mutacion-concluyente.caso` | Modificar: agregar `parcial: false` a `corrida_mutacion` | Agy |
| `corpus/proceso/111-ronda-mutacion-parcial-no-es-concluyente.caso` | Crear: caso falso verde de ronda parcial | Agy |
| `corpus/proceso/112-ronda-mutacion-completa-concluyente.caso` | Crear: caso verde de ronda completa | Agy |
| `tests/test_mutacion_codigo.py` | Modificar: clase `FiltroSitiosTests` al final del archivo | Agy |
| `estudios/0.25.0-sitios/INFORME-AGY.md` | Crear: informe final con decisiones, rationale y notas | Agy |
