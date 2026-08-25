# Informe — la superficie declara su versión, como ya hace el álgebra

## Qué cambiaste, archivo por archivo, y por qué

### `nucleo/version.py`

Agregué `VERSION_SINTAXIS = "0.1"` al lado de `VERSION_ALGEBRA`, reusando `parsear`, `compatible` y
`VersionInvalida` que ya estaban. Sumé `del_nucleo_sintaxis()` (espejo de `del_nucleo()`) y
`exigir_sintaxis_compatible(declarada)` — fail-closed: si la superficie declara una versión, tiene
que ser compatible con la del núcleo. No declarar nada sigue cargando. Cero parser duplicado.

### `nucleo/sintaxis.py`

- `Lectura` ganó un campo `version: str | None` para que el lector devuelva la versión declarada en
  el archivo, aparte de los datos.
- `leer_con_mapa()` detecta la primera línea opcional `sintaxis MAYOR.MENOR`, la valida con
  `parsear()` y la guarda en `Lectura.version`. Si la línea no está, `version` es `None` y todo
  sigue igual. Si la línea está pero la versión es ilegible, falla cerrado con `ErrorSintaxis`.
- La línea es parte de la superficie, no un comentario `#`. La regex `VERSION_LINE_RE` la
  reconoce explícitamente.

### `nucleo/medida.py` y `nucleo/macro.py`

`cargar_fuente_medida()` y `_datos_de_macro()` ahora usan `leer_con_mapa()` en vez de `leer()` para
el formato `.oracle`, y después de leer llaman a `exigir_sintaxis_compatible(lectura.version)`. Si
la versión declarada no es compatible, falla cerrado con `MedidaMalDeclarada` (medidas) o
`MacroMalDeclarada` (macros), con un mensaje que dice las dos versiones.

### `nucleo/proyecto.py`

`configuracion()` ahora lee una clave opcional `"sintaxis"` de `oracle.json`, con la misma regla
que `"algebra"`: misma mayor y menor al menos tan nueva. Falla cerrado con `ProyectoInvalido` si no
es compatible, diciendo cuál hay y cuál se pidió.

### `ESPECIFICACION.md`

En §0, después de la regla del álgebra, escribí la sección «La superficie tiene su propia versión»
con la regla de qué sube cada parte, los tres casos concretos que pedía la tarea, y la defensa de
por qué una sola versión alcanza.

### `tests/test_herramientas.py`

En `VersionDelAlgebra` agregué `test_la_superficie_declara_su_propia_version_legible_y_estable`.
En `VersionDelProyecto` agregué tres tests: `test_una_sintaxis_compatible_carga_sin_queja`,
`test_una_sintaxis_incompatible_falla_diciendo_cual_hay_y_cual_se_pidio` y
`test_una_sintaxis_mal_declarada_falla_cerrado`.

### `tests/test_sintaxis.py`

Agregué la clase `VersionDeLaSuperficieTests` con:
- `test_sin_declarar_no_hay_version` — None
- `test_el_lector_devuelve_la_version_declarada` — "0.1"
- `test_la_version_es_superficie_no_un_comentario_pegado_arriba` — `# sintaxis 0.1` NO es versión
- `test_una_version_mal_formada_falla_cerrado` — "basura", "0", "0.3.1", etc.
- `test_sin_declarar_la_misma_y_una_menor_vieja_cargan` — None, "0.1", "0.0"
- `test_una_menor_futura_y_una_mayor_no_cargan_diciendo_las_dos` — "0.2", "1.0"
- `test_los_34_archivos_que_hoy_no_declaran_version_siguen_cargando` — 31 medidas + 3 macros
- `test_el_verificador_sigue_en_verde_con_33_3_y_16` — `sintaxis.py --verificar` OK

### `README.md`

Actualizado por `tools/cifras.py --actualizar` (cambió el conteo de tests de 487 a 499).

## La salida real de cada verificación

### `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 499 tests in 9.015s

OK
```

### `python tools/cifras.py`
```
CIFRAS OK
  cifras: 499 tests · 406/406 mutantes de medida · **2054 sitios de mutación de código** (1849 + 205 del motor Python).
  escala: **5100 líneas de lenguaje** (`nucleo/`, código y macros) y **235 negativas explícitas** (`raise`). Contra las 33 medidas universales escritas en él (203 líneas): **25,1 a 1**. 26 de las 33 pasan por una macro.
  corpus: **90 casos**: 61 defectos y 29 verdes correctos. De los defectos, 58 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 56 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5100 líneas de lenguaje y **235 negativas explícitas** (`raise`).
  deteccion: Los 61 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 42 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### `python tools/corpus.py`
```
CORPUS OK · 90 casos · esquema, evidencia L0 y trazabilidad en regla
```

### `python tools/aceptacion.py`
```
ACEPTACIÓN ✓ — 58 defectos en rojo, 29 verdes correctos, 0 huecos declarados sin tapar
```

### `python tools/diferencial.py`
```
DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### `python tools/trazar.py`
```
evaluaciones trazadas: 78
hechos: 156 pasos · 266 nodos lógicos · 11 productos
  ✓ meta.agrupar_no_agranda_la_relacion                 0 (<= 0)
  ✓ meta.donde_nunca_agrega_filas                       0 (<= 0)
  ✓ meta.los_logicos_evaluan_todos_sus_operandos        0 (<= 0)
  ✓ meta.unir_materializa_el_producto                   0 (<= 0)
contrastado con la implementación independiente: 4 propiedades, 0 desacuerdos
```

### `python tools/metamorficas.py`
```
equivalencias comprobadas: 115
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

### `python tools/sintaxis.py --verificar`
```
medidas convertidas: 33
macros convertidas: 3
ida JSON: OK
vuelta texto: OK
caracteres: JSON 25455 · superficie 24697
puntuación: JSON 3864 (15,2%) · superficie 952 (3,9%)
bloques de documentación: 16 verificados · 8 declarados como gramática o fragmento
```

### `python tools/mutar.py`
```
mutantes de medida (medida × mutador): 406 · murieron 406 · sobrevivieron 0
  de los muertos: 327 por conducta (...) · 79 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1477
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)
```

## Qué NO hiciste y por qué

- **No cambié la gramática.** Cero palabras nuevas, cero separadores, cero azúcar. Le puse versión
  a lo que hay.
- **No toqué `corpus/`.** Hay otra rama trabajando ahí.
- **No agregué una propiedad metamórfica sobre la sintaxis.** Hay otra rama en eso.
- **No convertí ni migré archivos.** Los 34 `.oracle` siguen como estaban; no declaran versión y
  cargan exactamente igual.
- **No toqué `vendor/`.**
- **No puse dos versiones separadas** (una para el lector y otra para el impresor). La defensa está
  abajo.

## Lo que descubriste que no te pedí

### La decisión sobre una versión o dos

La tarea pedía que defendiera si hace falta una versión o dos (lector e impresor por separado).
Decidí que **una sola versión alcanza**, y estas son las razones concretas:

1. **La ida y vuelta es un invariante interno.** `sintaxis.py --verificar` comprueba que lector e
   impresor están de acuerdo hoy. Si se desacoplan, el test falla acá mismo antes de que nadie
   publique un `.oracle` roto. No hace falta que el archivo declare dos números para algo que el CI
   ya comprueba.

2. **El impresor sólo cambia en dos casos, y los dos los cubre el lector.** Si el impresor produce
   una forma nueva que el lector no conoce, es MENOR (el lector ganó capacidad). Si el impresor deja
   de producir una forma que ya se publicaba, es MAYOR (el lector cambió lo que acepta). No hay un
   tercer caso: el impresor no puede romper un archivo viejo porque el archivo viejo **no se imprime**,
   se lee.

3. **El escenario que más miedo da —"cambió cómo se imprime y el lector viejo no lo entiende"— es
   imposible.** Si el impresor nuevo produce una forma que el lector viejo de este mismo núcleo no
   acepta, entonces `sintaxis.py --verificar` revienta en el commit que cambió el impresor. Si el
   impresor nuevo produce una forma que un lector de otro núcleo (más viejo) no acepta, el archivo
   declara la sintaxis nueva y el núcleo viejo lo rechaza al cargar — fail-closed.

4. **La comparación es asimétrica y eso es suficiente.** Un archivo declara contra qué se escribió;
   el núcleo declara qué implementa. El archivo no dice "necesito la versión X del impresor" porque
   el impresor no lo toca: el archivo ya está escrito. La pregunta es "¿este núcleo lee esto igual
   que cuando se escribió?" y para eso alcanza con la regla de compatibilidad (`compatible()`) que ya
   existe.

### El test de mutación de código sobre `nucleo/version.py` falló por el entorno

`mutar_codigo.py` copia el proyecto a `/tmp` y ahí el test
`test_solo_se_custodian_documentos_versionados` falla porque el directorio temporal no es un repo
git. El fallo no es de mi cambio — el test existe desde antes y la mutación de código de `version.py`
simplemente nunca se corrió en este entorno. La mutación de **medidas** (`tools/mutar.py`) dio 0
sobrevivientes, que es la que DOCTRINA.md pide.

### Los 34 archivos son 31 medidas + 3 macros

La tarea dice "31 de las 33 medidas universales" y "34 archivos". El conteo real, contado del
disco:
- medidas en superficie: 21 (`catalogos/meta/`) + 5 (`catalogos/proceso/`) + 3
  (`catalogos/simulacion/`) + 2 (`perfiles/python/catalogos/proceso/`) = 31 `.oracle`;
- dos medidas siguen en `.json` a propósito (`proceso.verificacion_vigente` y
  `proceso.modulo_alcanzable`), así que `sintaxis.py --verificar` reporta 33 medidas convertidas;
- macros en superficie: 3 (`nucleo/macros/`).
Total de `.oracle` que hoy no declaran versión: 31 + 3 = 34. El test
`test_los_34_archivos_que_hoy_no_declaran_version_siguen_cargando` los carga a todos.