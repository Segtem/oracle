# Avance 0.22.0 — Campos de relaciones y evaluación unificada

Fecha: 2026-09-15
Tarea: `20260915-155654-campos`
Plan: `PLAN-0.22.0-CAMPOS.md`
Encargo: `estudios/0.22.0-campos/ENCARGO-AGY.md`

## 1. Decisiones de diseño y representación interna

1. **Módulo emisor de `campo_leido`**:
   - Se crea `nucleo/campo_leido.py` en lugar de agregar la relación a `nucleo/unidad.py`.
   - Razón: `tests/test_unidad.py` fija explícitamente `assertEqual(RELACIONES_DE_UNIDAD, frozenset({"cantidad_comparada"}))` y la propiedad de tests existentes pertenece a Claude. Ubicar `campo_leido` en su propio módulo mantiene `nucleo/unidad.py` intacto, declara limpiamente `RELACIONES_DE_CAMPO_LEIDO = frozenset({"campo_leido"})`, `AMBITOS_DE_RELACIONES = {"campo_leido": "universal"}` y `CAMPOS_DE_RELACIONES = {"campo_leido": ("medida", "relacion", "campo", "origen", "existe")}`.

2. **Resolución de alias y lecturas no resueltas en `campo_leido`**:
   - Una lectura `["campo", alias, nombre]` busca el alias en las fuentes de la tubería (`de`, `unir`) y en las entradas condicionales de `requiere` (`["filas", relacion, alias, condicion]`).
   - Si el alias no se resuelve, se emite con `relacion: ""`, `origen: "sin_declarar"`, `existe: False`.
   - `["hecho", alias]` y `["col", nombre]` se ignoran por no ser lecturas de campo.

3. **Lector AST en `nucleo/relacion.py`**:
   - `campos_de_relaciones_declarados(raiz=None) -> dict[str, tuple[str, ...]]` inspecciona estáticamente los archivos en `nucleo/` y `tools/` que declaran `RELACIONES_*`.
   - Falla cerrado con `RelacionMalDeclarada` ante:
     * `CAMPOS_DE_RELACIONES` que no sea mapa literal de cadenas a tuplas de cadenas no vacías.
     * Campos repetidos dentro de una tupla.
     * Relaciones declaradas en más de un archivo.
     * Relaciones del lenguaje sin campos declarados.
     * Campos para una relación que no figure en ningún `RELACIONES_*`.

4. **Relaciones de proceso en `relaciones/`**:
   - Se crean `corrida_mutacion.json`, `archivo.json`, `modulo.json`, `alcanzable.json`, `afirmacion.json` y `hallazgo.json` en `relaciones/`.
   - Esquemas alineados con sus emisores en el repositorio y/o las lecturas de sus medidas y casos.

5. **Evaluación unificada y separación de lo que no se pudo juzgar**:
   - Se implementa `evaluar_conjunto(medidas, evidencia, limites=None, en_sombra=frozenset(), registro=None) -> Informe` en `nucleo/medida.py`.
   - Si la evaluación de una medida levanta `ErrorDeAlgebra`, no se interrumpe la corrida; se registra en `Informe.no_juzgaron` como `(id, motivo)`.
   - `Informe.ok` es `False` si `no_juzgaron` no está vacío.
   - `Informe.texto()` y `Informe.a_json()` incluyen las medidas que no pudieron juzgar, manteniéndose retrocompatibles cuando `no_juzgaron` está vacío.

6. **Adaptación de herramientas**:
   - `tools/aceptacion.py`: usa `evaluar_conjunto` tanto para cada caso como para las medidas meta y de sombra; si un caso o una medida no juzgó, es una falla de la corrida con su motivo, sin traceback.
   - `tools/juzgar.py`: usa `evaluar_conjunto`; si alguna medida no pudo juzgar, termina con código 2 y explica el motivo.
   - `tools/mutar.py`: usa `evaluar_conjunto`; `_politicas_ok(informe)` retorna `False` ante medidas que no juzgaron; agrega `campo_leido` a `ARNESES_APARTE["tools/aceptacion.py"]`.
   - `tools/mutar_codigo.py`: usa `evaluar_conjunto`, conserva su salida e independencia de código de salida.

## 2. Plan de archivos

### Archivos a crear
- `estudios/0.22.0-campos/AVANCE-AGY.md` (este archivo)
- `relaciones/corrida_mutacion.json`
- `relaciones/archivo.json`
- `relaciones/modulo.json`
- `relaciones/alcanzable.json`
- `relaciones/afirmacion.json`
- `relaciones/hallazgo.json`
- `nucleo/campo_leido.py`
- `catalogos/meta/meta.toda_medida_lee_campos_que_existen.oracle`
- `tests/test_campos_de_relaciones.py`
- `tests/test_no_juzgaron.py`
- `estudios/0.22.0-campos/INFORME-AGY.md` (al finalizar)

### Archivos a editar
- `nucleo/relacion.py`: agregar `CAMPOS_DE_RELACIONES` y la función `campos_de_relaciones_declarados`.
- `nucleo/marco.py`: agregar `CAMPOS_DE_RELACIONES`.
- `nucleo/medida.py`: agregar `CAMPOS_DE_RELACIONES`, ampliar `Informe` con `no_juzgaron`, implementar `evaluar_conjunto`.
- `nucleo/referente.py`: agregar `CAMPOS_DE_RELACIONES`.
- `nucleo/unidad.py`: agregar `CAMPOS_DE_RELACIONES`.
- `nucleo/diagnostico.py`: agregar `CAMPOS_DE_RELACIONES`.
- `tools/trazar.py`: agregar `CAMPOS_DE_RELACIONES`.
- `tools/metamorficas.py`: agregar `CAMPOS_DE_RELACIONES`.
- `tools/aceptacion.py`: emisión de `campo_leido` en `evidencia_meta`, uso de `evaluar_conjunto`.
- `tools/juzgar.py`: uso de `evaluar_conjunto` y salida 2 ante `no_juzgaron`.
- `tools/mutar.py`: uso de `evaluar_conjunto`, actualización de `_politicas_ok` y `ARNESES_APARTE`.
- `tools/mutar_codigo.py`: uso de `evaluar_conjunto`.
