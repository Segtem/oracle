# Informe — claves de unicidad declarables por relación

## Qué hice

Una relación puede **declarar** una clave de unicidad opcional poniendo a la cabeza de su lista de
hechos un nodo `["clave", [<campo>, …]]`:

```json
{ "pieza": [["clave", ["id"]], {"id": "Muro_A", "x": 100}, {"id": "Muro_B", "x": 300}] }
```

La clave se valida **antes de medir** y fail-closed: si dos hechos repiten la clave, la evaluación
levanta `ErrorDeAlgebra` nombrando la relación, la clave responsable y la fila que la viola (y contra
cuál). Un campo de la clave ausente en un hecho, o un valor de clave no escalar, también levanta — no
hay nulos implícitos que dejen la identidad sin comprobar en silencio.

Cambios:

- `nucleo/algebra.py`: `separar_clave()` (extrae y valida el nodo) y `validar_unicidad()` (la
  comprobación fail-closed). `_de` los invoca al leer la relación, antes de cualquier `donde`,
  `agrupar` o `resumen`.
- `nucleo/fixtures.py`: `_validar_evidencia()` acepta y valida el nodo `clave`, y rechaza el duplicado
  en el momento de **leer** el fixture, no de usarlo.
- `ESPECIFICACION.md` §1 y `DECISION-001-RELACIONES-COMO-BOLSAS.md`: documentada la consecuencia.
- `tests/test_algebra.py` y `tests/test_nucleo.py`: 16 tests nuevos que fijan las tres propiedades del
  criterio de éxito.

No toqué `nucleo/medida.py`: la validación vive en el álgebra, que es donde se leen las relaciones, así
que el cambio no llega a `Medida`.

## Qué decidí (y por qué)

- **La clave vive en la evidencia, no en la medida.** La auditoría lo dice con precisión: «la carga de
  unicidad recae en cada sensor». El sensor produce la relación, así que el sensor declara su
  identidad. Si fuera un nodo de la medida, dos medidas sobre la misma relación tendrían que repetirla
  y podrían contradecirse.
- **Nodo a la cabeza de la lista, y no un objeto envoltorio.** `requiere` es el precedente: un nodo
  opcional que no altera la forma canónica de lo que no lo declara. Acá `evidencia[relacion]` sigue
  siendo una lista; sin el nodo es byte a byte la bolsa de siempre y **cero cambios de conducta**.
- **Dos capas de validación, con motivos distintos.** En `_de` se valida al medir (la relación que una
  medida consume no puede traer un duplicado); en `_validar_evidencia` se valida al leer un fixture
  (un fixture con un duplicado bajo clave falla aunque ninguna medida lo mire). Las dos son
  fail-closed, pero la primera es la precondición de medir y la segunda la de cargar.
- **Campo ausente es error, no `None`.** L0 prohíbe los nulos implícitos; una identidad a medias no se
  puede comprobar y devolver `False` la taparía en verde.
- **La clave no deduplica: rechaza.** La multiplicidad intencional sigue expresable (sin nodo, o con
  una clave que distinga los eventos). Deduplicar seguiría siendo, si algún día hace falta, un operador
  explícito con dos usuarios — como dice `DECISION-001`, no una normalización silenciosa.

## Qué NO cubrí (el alcance de este trabajo)

- **Sin casos de corpus.** La tarea autoriza `corpus/algebra/`, pero no pude usarla sin violar los
  límites: `tools/corpus.py` (ajeno) exige que toda relación sea una lista de hechos y rechazaría el
  nodo `clave`; y un caso `verde_correcto` exige una medida nueva, que vive en `catalogos/` (también
  ajeno). La conducta nueva queda fijada por los 16 tests de unidad, no por el mutador de medidas.
- **Sin mutador.** `nucleo/mutacion.py` está prohibido para mí y, además, la clave es una propiedad de
  la relación, no de la medida: el mutador de medidas no la toca. La mutación de código (`mutar_codigo`)
  no forma parte de la verificación de `DOCTRINA.md`; de todos modos los tests nuevos ejercitan cada
  rama del código nuevo (nodo mal formado, campo ausente, valor no escalar, clave compuesta, límite de
  filas).
- **La validación es per-relación y per-lectura.** En la ruta de evaluación sólo se comprueba la clave
  de las relaciones que la medida lee; una relación que ninguna medida mira no se comprueba al evaluar
  (sí al cargar un fixture). Me pareció coherente con `requiere`, que también es una precondición de
  la medida y no un escaneo global de la evidencia.

## Verificación

```
python -m unittest discover -s tests -t . -q     # 424 tests OK
python tools/cifras.py                           # CIFRAS OK
python tools/corpus.py                           # CORPUS OK
python tools/aceptacion.py                       # ACEPTACIÓN ✓
python tools/diferencial.py                      # DIFERENCIAL ✓
python tools/compromisos.py                      # en plazo
python tools/trazar.py                           # las 4 propiedades verdes
python tools/mutar.py                            # 0 sobrevivientes (206/206)
```
