# Plan de avance - Hito 0.21.0 (mutante y variantes)

**Tarea**: `tareas/20260915-155111-mutante`  
**Plan base**: `PLAN-0.21.0-MUTANTE.md`  
**Encargo**: `estudios/0.21.0-mutante/ENCARGO-AGY.md`  

---

## 1. Archivos a crear y editar

### Archivos a editar (propiedad de AGY):
1. `nucleo/relacion.py`:
   - Soporte para relaciones con variantes (`variantes`, `discriminante`, dataclass `Variante`).
   - Validación estructural y semántica de variantes (discriminante campo común texto, unicidad de variantes y campos, tipos/unidades consistentes entre variantes, no solapamiento con campos comunes).
   - Generación de hechos `relacion_declarada` (columna `variantes`) y `campo_declarado` (columna `variante` vacía para comunes, valor de variante para específicos).
   - Propiedad o método auxiliar `todos_los_campos` para consultas de catálogo/unidades/puntos ciegos.
2. `nucleo/medida.py`:
   - Soporte para entradas con condición en `requiere`: `["filas", relacion, alias, condicion]`.
   - Validación sintáctica y semántica de `requiere` (alias y relación válidos, no repetidas, alias consistente en expresiones `campo`/`hecho`, condición booleana).
   - Evaluación en `Medida.evaluar`: filtrado por filas que cumplan la condición usando `evaluar_expr` contra el entorno `{alias: hecho}`, emisión de veredicto `sin_evidencia` (`"{relacion} sin filas con {_expr(condicion)}"`) si la relación no existe o no tiene filas que cumplan la condición; propagación sin tragar de errores de evaluación/álgebra (`ErrorDeAlgebra`).
   - Hechos generados: columna `con_condicion` (`bool`) en la relación `requiere` y en `_dependencias_de_medida`.
3. `nucleo/sintaxis.py`:
   - Lector de medidas: soporte para múltiples líneas consecutivas `requiere ` y para la sintaxis condicional `requiere <relacion> <alias> donde <condicion>`.
   - Impresor de medidas: serialización canónica de `requiere` emitiendo primero la línea de nombres simples si existen, y luego una línea por cada requerimiento con condición.
   - Preservación de los índices de diagnóstico de `ambito` y `alcance`.
   - Ajuste de `_tipos_en_plantilla` si corresponde para reconocer `requiere` estructurado.
4. `nucleo/unidad.py`:
   - Extensión de `_unidades_de_campo` para buscar tanto en campos comunes como en campos de variantes (`rel.todos_los_campos`).
5. `tools/medida.py`:
   - Extensión de `_puntos_ciegos` para verificar campos no referenciados usando todos los campos declarados (comunes y de variantes).
6. `nucleo/mutacion.py`:
   - Agregar `"tipo": "medida"` a los hechos generados para mutantes de medida.
7. `perfiles/python/mutacion_codigo.py`:
   - Agregar `"tipo": "codigo"` a los hechos generados para mutantes de código.
   - En `_cargar_reanudacion`, requerir `"tipo"` y validar que sea `"codigo"` para rechazar manifiestos sin tipo.
8. `catalogos/proceso/proceso.test_con_mutante_que_lo_mata.oracle`:
   - Reescribir en sintaxis plana con `m.tipo == "medida"` y `requiere mutante m donde m.tipo == "medida"`.
9. `catalogos/proceso/proceso.codigo_con_mutante_que_lo_mata.oracle`:
   - Reescribir en sintaxis plana con `m.tipo == "codigo"` y `requiere mutante m donde m.tipo == "codigo"`.

### Archivos a crear (propiedad de AGY):
1. `relaciones/mutante.json`:
   - Declaración de la relación `mutante` con campos comunes (`id`, `apunta_a`, `cambio`, `tipo`) y variantes `medida` y `codigo`.
2. `tests/test_requiere_con_condicion.py`:
   - Pruebas unitarias para `requiere` con condición: parseo de sintaxis, canonicalización de AST, validaciones de errores de algebra/sintaxis, evaluación sin evidencia y con evidencia, propagación de errores de algebra, hechos generados con columna `con_condicion`.
3. `tests/test_relacion_variantes.py`:
   - Pruebas unitarias para relaciones con variantes: lectura desde JSON/datos, validaciones de errores (discriminante inválido, no común, no texto, variantes vacías, solapamiento de nombres, tipos discordantes), hechos generados (`relacion_declarada` y `campo_declarado`), resolución de unidades y puntos ciegos.
4. `estudios/0.21.0-mutante/INFORME-AGY.md`:
   - Informe final de la entrega.

---

## 2. Decisiones de diseño y representación de datos

### A. Representación canónica de `requiere`
- Forma canónica en AST:
  `["requiere", *entradas]`
  donde cada entrada puede ser:
  - Una cadena: `"nombre_relacion"` (requiere incondicional simple).
  - Una tupla/lista: `["filas", "nombre_relacion", "alias", condicion_ast]` (requiere condicional).
- En hechos:
  - Relación `requiere`: filas `{"medida": id, "indice": i, "relacion": r, "con_condicion": bool}`.
  - Relación `_dependencias_de_medida`: filas `{"medida": id, "relacion": r, "fuente": bool, "con_condicion": bool}`.
  
### B. Representación canónica de variantes en `relacion`
- En datos canónicos (JSON/AST):
  `["relacion", nombre, ["campos", ...], ["variantes", discriminante, ["variante", valor, ["campo", ...], ...], ...], ["alcance", ...]]`
  Si no hay variantes, se omite el nodo `variantes` (4 elementos: `relacion`, `nombre`, `campos`, `alcance`).
- En hechos:
  - `relacion_declarada`: incluye `variantes: int` (cantidad de variantes declaradas, 0 si no tiene).
  - `campo_declarado`: incluye `variante: str` (`""` para campos comunes, el nombre de la variante para campos de variante).

### C. Manejo de tipos y puntos ciegos
- `rel.todos_los_campos` expone un mapeo o lista unificada de todos los campos (comunes y de variantes).
- `_unidades_de_campo` y `_puntos_ciegos` usan esta vista para no omitir campos de variantes.
