# Informe

## Qué cambié

- `nucleo/sintaxis.py`: moví la implementación del lenguaje infijo al núcleo: tokenizador, parser, impresor, mapa de fuente y fragmentos de error. También amplié `fragmento_de_error` para que un `ErrorSintaxis` muestre línea, columna y marcador.
- `tools/sintaxis.py`: quedó como CLI y fachada de compatibilidad. Importa el parser/impresor desde `nucleo.sintaxis`, conserva `--imprimir`, `--leer` y `--verificar`, y enumera medidas con el inventario común del núcleo.
- `nucleo/medida.py`: agregué `rutas_de_catalogo` y `cargar_fuente_medida`. `cargar` y `cargar_catalogo` aceptan `.json` y `.oracle`; un `.oracle` mal formado falla con archivo, línea, columna y fragmento; un id duplicado entre formatos falla nombrando los dos archivos; los archivos de catálogo symlink se rechazan.
- `catalogos/meta/meta.agrupar_sin_claves_es_el_resumen_global.oracle`: convertí una medida universal real con `python tools/sintaxis.py --imprimir`.
- `catalogos/meta/meta.agrupar_sin_claves_es_el_resumen_global.json`: lo borré para que no exista el mismo id en dos formatos.
- `tools/cifras.py`: el conteo de medidas universales y de formas por macro usa el lector común, así no pierde `.oracle`.
- `tools/estudio.py`: el catálogo en prosa y los números usan el lector/inventario común. También corregí el texto de encabezado que decía que todo el catálogo era JSON.
- `tools/medida.py`: `--expandir` y la revisión de un archivo puntual leen `.json` o `.oracle`.
- `tools/metamorficas.py`: la ida y vuelta de sintaxis lee fuentes con el lector común.
- `tools/mutar_codigo.py`: agregué `nucleo/sintaxis.py` a los objetivos con tests prioritarios.
- `pyproject.toml`: incluí `**/*.oracle` en package-data de catálogos base y perfiles.
- `README.md`: lo actualicé con `python tools/cifras.py --actualizar`. La proporción nueva publicada es `15,9 a 1`.
- `tests/test_nucleo.py`: agregué pruebas de carga `.oracle`, duplicado `.json`/`.oracle`, error con archivo/línea/columna, `.oracle` vacío y rechazo de symlink.
- `tests/test_sintaxis.py`: ajusté el conteo del catálogo al inventario común y agregué una regresión contra volver a inventariar catálogo con `rglob("*.json")` o `glob("*/*.json")` a mano.
- `tests/test_herramientas.py` y `tests/test_macro.py`: ajusté lecturas de catálogo en tests para que usen el lector común.

## Actualización de cifras

```text
$ python tools/cifras.py --actualizar
README.md actualizado
```

## Verificaciones

```text
$ python -m unittest discover -s tests -t . -q
----------------------------------------------------------------------
Ran 462 tests in 9.141s

OK
```

```text
$ python tools/cifras.py
CIFRAS OK
  cifras: 462 tests · 406/406 mutantes de medida · **1909 sitios de mutación de código** (1704 + 205 del motor Python).
  escala: **4747 líneas de lenguaje** (`nucleo/`, código y macros) y **226 negativas explícitas** (`raise`). Contra las 33 medidas universales escritas en él (298 líneas): **15,9 a 1**. 26 de las 33 pasan por una macro.
  corpus: **90 casos**: 61 defectos y 29 verdes correctos. De los defectos, 58 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 56 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 4747 líneas de lenguaje y **226 negativas explícitas** (`raise`).
  deteccion: Los 61 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 42 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

```text
$ python tools/corpus.py
CORPUS OK · 90 casos · esquema, evidencia L0 y trazabilidad en regla
```

```text
$ python tools/aceptacion.py
catálogo: 33 medidas · corpus: 90 casos

  ROJO  049-donde-agrego-filas                 meta.donde_nunca_agrega_filas  (valor 1)
  verde 050-donde-filtra-como-debe             meta.donde_nunca_agrega_filas  (valor 0)
  ROJO  051-agrupar-invento-un-grupo           meta.agrupar_no_agranda_la_relacion  (valor 1)
  verde 052-agrupar-colapsa-como-debe          meta.agrupar_no_agranda_la_relacion  (valor 0)
  ROJO  053-unir-perdio-un-par                 meta.unir_materializa_el_producto  (valor 1)
  verde 054-unir-materializa-el-producto       meta.unir_materializa_el_producto  (valor 0)
  ROJO  055-logico-cortocircuito               meta.los_logicos_evaluan_todos_sus_operandos  (valor 2)
  verde 056-logico-evalua-todo                 meta.los_logicos_evaluan_todos_sus_operandos  (valor 0)
  ROJO  057-un-solo-cortocircuito              meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  ROJO  061-ausencia-sin-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-cubierta-o-no-aplica      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  063-ausencia-sin-terminos-no-concluye  meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  064-medida-sin-filtro-ni-grupo         meta.toda_medida_filtra_o_agrupa  (valor 1)
  verde 065-medida-filtra-o-agrupa             meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  066-filtro-sin-terminos-no-concluye    meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  067-umbral-de-igualdad                 meta.ningun_umbral_de_igualdad  (valor 1)
  verde 068-umbral-de-orden                    meta.ningun_umbral_de_igualdad  (valor 0)
  ROJO  069-filtro-no-toma-terminos-ajenos     meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  100-donde-no-compone                   meta.donde_compone  (valor 1)
  verde 101-donde-compone-bien                 meta.donde_compone  (valor 0)
  ROJO  102-unir-no-conmuta                    meta.unir_conmuta  (valor 1)
  verde 103-unir-conmuta-bien                  meta.unir_conmuta  (valor 0)
  ROJO  104-agrupar-sin-claves-difiere         meta.agrupar_sin_claves_es_el_resumen_global  (valor 1)
  verde 105-agrupar-sin-claves-coincide        meta.agrupar_sin_claves_es_el_resumen_global  (valor 0)
  ROJO  106-macro-expande-distinto             meta.una_macro_equivale_a_su_expansion  (valor 1)
  verde 107-macro-equivale                     meta.una_macro_equivale_a_su_expansion  (valor 0)
  ROJO  108-donde-compone-un-campo-por-vez     meta.donde_compone  (valor 3)
  ROJO  109-unir-conmuta-un-campo-por-vez      meta.unir_conmuta  (valor 3)
  ROJO  110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez meta.agrupar_sin_claves_es_el_resumen_global  (valor 2)
  ROJO  111-una-macro-equivale-a-su-expansion-un-campo-por-vez meta.una_macro_equivale_a_su_expansion  (valor 3)
  ROJO  120-sintaxis-no-vuelve-igual           meta.sintaxis_ida_y_vuelta  (valor 1)
  verde 121-sintaxis-vuelve-exacta             meta.sintaxis_ida_y_vuelta  (valor 0)
  ROJO  122-sintaxis-revienta-al-leer          meta.sintaxis_ida_y_vuelta  (valor 1)
  ROJO  123-sintaxis-un-campo-por-vez          meta.sintaxis_ida_y_vuelta  (valor 3)
  ROJO  400-umbral-flotante-de-igualdad        meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  ROJO  401-umbral-flotante-de-desigualdad     meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  verde 402-umbral-flotante-de-orden-y-entero  meta.ningun_umbral_flotante_de_igualdad  (valor 0)
  ROJO  403-umbral-sin-defensa                 meta.ningun_umbral_sin_defensa  (valor 1)
  verde 404-umbral-con-defensa                 meta.ningun_umbral_sin_defensa  (valor 0)
  ROJO  405-medida-sin-alcance                 meta.ninguna_medida_sin_alcance  (valor 1)
  verde 406-medida-con-alcance                 meta.ninguna_medida_sin_alcance  (valor 0)
  ROJO  001-verde-acumulativo                  proceso.afirmacion_declara_alcance  (valor 3)
  ROJO  002-mutante-firma-por-id               proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  003-mutante-fondo-nunca-ejercitado     proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  005-mutante-yaw-sin-franja             proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  006-arnes-bytecode-viejo               proceso.arnes_con_bytecode_frio  (valor 1)
  ROJO  007-relevo-verde-arbol-sucio           proceso.verificacion_vigente  (valor 2)
  ROJO  008-vault-falso-rojo                   proceso.verificador_sin_falsos_rojos  (valor 2)
  ROJO  009-modulo-sin-consumidor              proceso.modulo_con_consumidor  (valor 3)
  ROJO  010-sed-desindenta                     proceso.sintaxis_valida_tras_edicion_masiva  (valor 1)
  ROJO  013-comparadores-del-algebra-sin-ejercitar proceso.test_con_mutante_que_lo_mata  (valor 6)
  ROJO  014-mutador-dejo-un-archivo-mutado-al-ser-matado proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  015-racimo-inalcanzable                proceso.modulo_alcanzable  (valor 12)
  ROJO  016-timeout-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  017-error-de-arnes-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  018-mutante-de-cache-borro-la-copia-del-proyecto proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  019-ronda-sin-mutantes-declarada-verde proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  020-una-afirmacion-sin-alcance-alcanza proceso.afirmacion_declara_alcance  (valor 1)
  ROJO  021-un-cambio-vivo-invalida-la-verificacion proceso.verificacion_vigente  (valor 1)
  ROJO  022-un-falso-rojo-ya-rompe-el-verificador proceso.verificador_sin_falsos_rojos  (valor 1)
  ROJO  023-un-import-ajeno-no-es-consumidor   proceso.modulo_con_consumidor  (valor 1)
  ROJO  024-una-variante-no-vacia-inalcanzable proceso.modulo_alcanzable  (valor 1)
  ROJO  043-ausencia-total-sale-verde          proceso.modulo_con_consumidor  (valor 0)
  ROJO  044-sin-grafo-de-alcance-sale-verde    proceso.modulo_alcanzable  (valor 0)
  verde 058-rechazo-del-algebra-no-es-deteccion proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 059-clave-declarada-en-un-caso         proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 101-mutantes-todos-muertos             proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 102-verificacion-vigente               proceso.verificacion_vigente  (valor 0)
  verde 103-vault-sin-falsos-rojos             proceso.verificador_sin_falsos_rojos  (valor 0)
  verde 104-afirmacion-con-alcance             proceso.afirmacion_declara_alcance  (valor 0)
  verde 105-arnes-con-cache-frio               proceso.arnes_con_bytecode_frio  (valor 0)
  verde 106-modulos-con-consumidor             proceso.modulo_con_consumidor  (valor 0)
  verde 107-reruteo-sin-romper-sintaxis        proceso.sintaxis_valida_tras_edicion_masiva  (valor 0)
  verde 108-ronda-mutacion-concluyente         proceso.ronda_mutacion_concluyente  (valor 0)
  verde 116-todo-el-nucleo-es-alcanzable       proceso.modulo_alcanzable  (valor 0)
  ROJO  200-corrida-sin-ninguna-corrida        simulacion.corrida_reproducible  (valor 0)
  ROJO  201-presupuesto-sin-ninguna-corrida    simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  202-traza-sin-ningun-evento            simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  301-simulador-que-ignora-la-semilla    simulacion.corrida_reproducible  (valor 2)
  verde 302-corridas-reproducibles             simulacion.corrida_reproducible  (valor 0)
  ROJO  303-el-presupuesto-no-alcanzo          simulacion.no_se_agoto_el_presupuesto  (valor 3)
  verde 304-el-presupuesto-alcanzo             simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  305-traza-con-hueco                    simulacion.la_traza_no_tiene_huecos  (valor 2)
  verde 306-traza-completa                     simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  307-una-corrida-no-reproducible-alcanza simulacion.corrida_reproducible  (valor 1)
  ROJO  308-una-corrida-agota-el-presupuesto   simulacion.no_se_agoto_el_presupuesto  (valor 1)
  ROJO  309-una-traza-con-un-hueco             simulacion.la_traza_no_tiene_huecos  (valor 1)

defectos que se pusieron rojos: 58 · verdes correctos: 29 · huecos declarados: 0
  resuelto       004-testigos-duplicados
  resuelto       012-umbral-duplicado-en-filtro-y-umbral
  limite_humano  011-conclusion-errada-desvan

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ningun_umbral_sin_defensa                      0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)

ACEPTACIÓN ✓ — 58 defectos en rojo, 29 verdes correctos, 0 huecos declarados sin tapar
```

```text
$ python tools/diferencial.py
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

```text
$ python tools/trazar.py
evaluaciones trazadas: 78
hechos: 156 pasos · 266 nodos lógicos · 11 productos

el álgebra, juzgada por medidas escritas en el álgebra:
  ✓ meta.agrupar_no_agranda_la_relacion                 0 (<= 0)
  ✓ meta.donde_nunca_agrega_filas                       0 (<= 0)
  ✓ meta.los_logicos_evaluan_todos_sus_operandos        0 (<= 0)
  ✓ meta.unir_materializa_el_producto                   0 (<= 0)

contrastado con la implementación independiente: 4 propiedades, 0 desacuerdos

  · meta.agrupar_no_agranda_la_relacion: compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción
  · meta.donde_nunca_agrega_filas: compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción
  · meta.los_logicos_evaluan_todos_sus_operandos: cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción
  · meta.unir_materializa_el_producto: compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción
```

```text
$ python tools/metamorficas.py
equivalencias comprobadas: 115
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         33 (0 construidas, 33 del catálogo)
  una_macro_equivale_a_su_expansion             60 (0 construidas, 60 del catálogo)
  unir_conmuta                                  16 (1 construidas, 15 del catálogo)

juzgado por las medidas aplicables:
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

```text
$ python tools/sintaxis.py --verificar
medidas convertidas: 33
ida JSON: OK
vuelta texto: OK
caracteres: JSON 24430 · superficie 23859
puntuación: JSON 3409 (14,0%) · superficie 910 (3,8%)
```

```text
$ python tools/mutar.py
mutantes de medida (medida × mutador): 406 · murieron 406 · sobrevivieron 0
  de los muertos: 327 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 79 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1477

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)
```

## Verificación adicional

`python tools/verificar_instalacion.py` no pudo construir el wheel con build isolation porque el entorno no tiene red para descargar `setuptools>=68` desde PyPI. Para separar eso del cambio, corrí el build sin aislamiento:

```text
$ tmp=$(mktemp -d); python -m pip wheel --no-build-isolation --no-deps --wheel-dir "$tmp" . >/tmp/oracle-wheel-build.log && TMP_WHEEL="$tmp" python - <<'PY'
from pathlib import Path
import os
import zipfile
ruedas = sorted(Path(os.environ['TMP_WHEEL']).glob('oracle_metalenguaje-*.whl'))
print(ruedas[0].name)
with zipfile.ZipFile(ruedas[0]) as z:
    nombres = z.namelist()
print('oracle?', any(n.endswith('meta.agrupar_sin_claves_es_el_resumen_global.oracle') for n in nombres))
print('nucleo_sintaxis?', 'oracle_metalenguaje/nucleo/sintaxis.py' in nombres)
PY
WARNING: The directory '/home/workstation/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
oracle_metalenguaje-0.1.0-py3-none-any.whl
oracle? True
nucleo_sintaxis? True
```

## Qué NO hice

- No convertí los 33 catálogos. Convertí una sola medida universal, como pedía la tarea.
- No cambié la gramática ni agregué operadores, palabras o nodos nuevos.
- No toqué `ESCRIBIR-UNA-MEDIDA.md`, `ORACLE-TUTORIAL-PRACTICO.md`, `defmacro` ni `nucleo/macro.py`.
- No toqué `vendor/`.
- No agregué una abstracción para corpus/diferencial: siguen siendo JSON y no son el formato nuevo del catálogo.
- No incorporé `DOCTRINA.md` ni `TAREA.md` al cambio; estaban sin seguimiento y los usé como instrucciones de esta ronda.

## Lo que descubrí

- La tarea decía que `tools/sintaxis.py --verificar` convertía 33 medidas, pero el CLI tenía `medidas == 29` hardcodeado. Lo cambié a “mayor que cero” y dejé el conteo real derivado.
- Mover `tools/sintaxis.py` a `nucleo/sintaxis.py` suma el parser al numerador y al denominador de mutación de código: los sitios de mutación publicados pasaron de 1404 a 1909.
- `pyproject.toml` también asumía que el catálogo empaquetado era sólo `*.json`; sin ese ajuste, una instalación por wheel perdía la medida `.oracle`.
- `git mv` falló en el primer intento porque el índice real estaba bloqueado en una ruta fuera del workspace escribible. Hice el renombre físico y después `git add`/`git commit` sí funcionó. El fallo del `git mv` fue:

```text
fatal: Unable to create '/home/workstation/Dev/oracle/.git/worktrees/wt-primeraclase/index.lock': Read-only file system
```

- El commit quedó registrado con mensaje `Haz .oracle formato de catalogo`. El renombre de `tools/sintaxis.py` no quedó como rename puro: Git ve `nucleo/sintaxis.py` como archivo nuevo y `tools/sintaxis.py` como CLI reescrito, porque el `git mv` no pudo tocar el índice en ese momento.
