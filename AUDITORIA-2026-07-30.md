# Auditoría técnica de Oracle — 2026-07-30

## Dictamen

Oracle es un **prototipo sólido, pero todavía no un oráculo confiable ni genérico de punta a
punta**. El álgebra está razonablemente separada de Jam; el catálogo, las herramientas y la evidencia
conservan supuestos de ese origen y existen caminos concretos para obtener un verde vacío,
autodeclarado o vencido.

| Pregunta | Dictamen |
|---|---|
| ¿Está completo? | No. Hay contratos incompletos, 31 mutantes de código vivos declarados y caminos principales rotos. |
| ¿Está abstraído de Jam? | El álgebra, bastante. El producto completo y su validación, todavía no. |
| ¿Funciona de forma genérica? | El núcleo puede reutilizarse sobre hechos planos, pero sólo fue probado dentro del ecosistema Jam/Python/LLM. |
| ¿Hay Goodhart hardcodeado? | Sí: hay afirmaciones de confianza fijadas a `True`, invariantes vacías y mutaciones dependientes de una escala elegida a mano. |
| ¿Hay una puerta trasera? | No se encontró evidencia de una puerta trasera maliciosa. Sí hay ejecución automática de código de proyectos y riesgos de integridad. |

Esta auditoría no invalida lo que Oracle ya consiguió. Distingue tres cosas que el informe anterior
mezclaba: que el código corra, que el diseño sea reusable y que un verde sea evidencia suficiente.

## Seguimiento posterior a la auditoría

Los hallazgos describen el commit auditado y se conservan como línea base. El worktree posterior
completó P0:

| Hallazgo | Estado posterior |
|---|---|
| A-01, campos certificados de simulación | Corregido en el worktree: colisiones rechazadas y 18 tests directos nuevos. |
| A-02, mutación sin línea base | Corregido en el worktree: una baseline roja levanta `LineaBaseFallida` antes de tocar fuentes. |
| A-03, confianza hardcodeada | Corregido para P0: caché comprobado antes y después, estados estructurados, timeout configurable, diagnóstico y equivalentes validados. Se eliminaron los veredictos de confianza autoproducidos y el estado de bytecode que no aplicaba a la mutación en memoria. La mutación automática sobre una copia en vez de fuentes activas sigue en P2. |
| A-04, verdes vacuos | Corregido en el worktree: ausencia, cero medidas/casos/mutantes y fixtures incompletos fallan de forma explícita. |

Después de P0 la suite tenía 190 tests verdes. Oracle conservaba 19 defectos en rojo, 12
verdes correctos, 3 huecos declarados y 48/48 mutantes de medida muertos; contra Jam conservaba 269
comparaciones diferenciales sin desacuerdo y 80/80 mutantes de medida muertos. La aceptación de Jam,
que no tiene corpus propio, ahora termina como `NO APLICABLE — SIN CASOS` con código distinto de cero.
El generador de estudio funciona sobre Oracle, pero `tools/estudio.py --proyecto .../jam/medidas`
todavía falla al validar `volumen` porque no registra las escalares del proyecto; resolverlo sin
ocultar la ejecución de UDF externas permanece en P1.

P1.1 reemplazó aquella cifra de mutación de medidas: el denominador ahora localiza sitios en fuentes,
expresiones, agregados y campos, además de los cuatro cambios gruesos originales. Sobre Oracle son
128 mutantes: la primera ronda mató 118 y expuso 10 vivos explícitos. Ocho reducciones al borde del
umbral y dos contraejemplos internos los cerraron sin debilitar el denominador; la ronda actual queda
en 128/128. El corpus tiene ahora 42 casos y aceptación conserva 27 defectos en rojo, 12 verdes
correctos y 3 huecos declarados. Contra Jam son 157 mutantes, 146 muertos y 11 vivos, mientras el
diferencial conserva 269 veredictos sin desacuerdo. La suite subió a 202 tests.

P1.2 cerró la frescura del diferencial con el esquema `oracle.diferencial/v1`: los fixtures llevan
SHA-256 del emisor, fuentes de referencia, catálogo canónico y configuración. El lector recalcula las
cuatro huellas y rechaza el fixture vencido. El acuerdo global con la referencia y los veredictos
individuales históricos son datos y salidas distintas; una regresión demuestra que intercambiar dos
medidas ya no se oculta detrás del mismo `AND`. Los emisores de Jam usan semilla SHA-256, Git con
fechas fijas y JSON canónico; dos regeneraciones consecutivas dieron archivos idénticos byte a byte.
Jam verifica 269 acuerdos globales y 1158 veredictos individuales; la suite de Oracle tiene 206 tests.

P1.3 cerró A-07 y el contrato operativo de proyectos. Un lector común valida y normaliza fixtures
`grupos` y `escenarios`; `--relaciones`, revisión y mutación consumen ese lector y la mutación exige
también frescura. Los ids de autoría usan una gramática cerrada y el destino se comprueba físicamente
debajo de `catalogos/`, incluida una regresión contra symlinks exteriores. Cada herramienta valida
las carpetas que usa. `estudio.py` usa el corpus externo y sólo ejecuta sus escalares con
`--confiar-escalares`. Una integración temporal recorre los siete comandos externos; la suite tiene
ahora 212 tests. Contra Jam, inventario y revisión funcionan, el diferencial conserva 269/1158 y la
mutación informa honestamente 146/157 con 11 vivos. La primera ejecución del vendor todavía dio el
verde obsoleto 80/80; sincronizar núcleo, herramientas y catálogo base eliminó esa divergencia.

P1.4 cerró la ejecución automática descrita en A-06. Todas las cargas externas ocurren dentro de
`main` y requieren `--confiar-escalares`; ayuda e inventarios tienen pruebas de ausencia de efectos
laterales. El registro queda aislado por proyecto y se restaura incluso ante error. El decorador fija
nombre, unidad, aridad y procedencia verificables, y no se siguen symlinks para encontrar el archivo.
La suite subió a 217 tests; la integración externa usa una UDF real para demostrar tanto el rechazo
sin confianza como el flujo explícitamente autorizado.

La mutación de código se repitió de forma particionada sobre copias temporales frescas, nunca sobre
este worktree. Los cambios descubiertos durante las rondas obligaron a repetir íntegramente cada
partición afectada. El baseline final cubre 616 sitios: 503 muertos reales y 113 vivos, sin timeout ni
error de arnés. Cada copia terminó con los 11 archivos de `nucleo/*.py` idénticos byte a byte a su
snapshot inicial y sin `__pycache__` local. Ninguno de estos cambios está incluido en el hash auditado
de la sección siguiente.

| Archivo | Muertos | Total | Vivos |
|---|---:|---:|---:|
| `algebra.py` | 183 | 186 | 3 |
| `dominio.py` | 11 | 18 | 7 |
| `grafo.py` | 0 | 4 | 4 |
| `macro.py` | 18 | 21 | 3 |
| `marco.py` | 24 | 43 | 19 |
| `medida.py` | 69 | 80 | 11 |
| `mutacion.py` | 47 | 50 | 3 |
| `mutacion_codigo.py` | 94 | 140 | 46 |
| `proyecto.py` | 18 | 34 | 16 |
| `simulacion.py` | 39 | 40 | 1 |
| **Total** | **503** | **616** | **113** |

Al repetir la ronda durante P0 apareció un riesgo nuevo en la propia instrumentación: mutar el
predicado que enumera `__pycache__` hizo que la limpieza interpretara casi todas las rutas como caché
y borrara una copia temporal completa. El worktree real no estuvo expuesto. El punto de borrado ahora
revalida, de forma independiente, el nombre exacto y el confinamiento físico de cada ruta; dos
regresiones demuestran que ni un enumerador corrompido ni una ruta exterior reciben autoridad de
borrado. El incidente quedó registrado como caso `018` y refuerza que el aislamiento definitivo de
P2 no es una mejora cosmética.

La misma repetición encontró un segundo caso operativo: mutar el comparador que reconoce
`--proyecto` podía quitar también `--hechos` y `--timeout`, lanzar recursivamente otra ronda completa
y agotar el límite de 60 segundos. El estado nuevo lo clasificó como inconcluso, no como muerte. Una
regresión directa fija el parser y el runner se detiene en la primera discriminación; al repetir los
34 sitios de `proyecto.py`, ese mutante terminó como `tests_fallaron` y no quedó ningún timeout ni
error de arnés.

Una revisión cruzada posterior reprodujo otros cuatro bypasses antes del cierre: un objetivo symlink
podía llevar la escritura fuera de la raíz; un error de importación creado como `_FailedTest` salía
con el mismo código que una discriminación; un timeout de un equivalente desaparecía del cálculo de
la CLI; y una ronda con cero mutantes devolvía éxito. Los cuatro tienen regresiones y fallan cerrado.
También se prohibieron códigos de señal como supuestos fallos de tests y se validan formato,
unicidad y razones de `equivalentes.json` antes de convertirlo en mapa. El caso vacuo quedó registrado
como `019`.

## Estado auditado y alcance

- Repositorio: `/home/workstation/Dev/oracle`.
- Commit auditado: `2bddacb4731aacc08c71d052528893fd16a1fab4` (`main`).
- Proyecto de contraste: `/home/workstation/Dev/jam/medidas`.
- Copia vendorizada de Jam: split `5278ebf2f70906e8fe05b94668461ddfde3a2d3d`.
- El núcleo y las herramientas compartidas entre upstream y vendor eran iguales; Jam estaba un commit
  documental por detrás.
- Se revisaron código, catálogo, corpus, tests, historia Git, emisores diferenciales de Jam y la
  integración real `--proyecto`.
- No se volvió a ejecutar la ronda completa de `tools/mutar_codigo.py`: escribe temporalmente sobre
  fuentes reales. El número 31/242 se tomó del estado declarado por Oracle y por el relevo actual de
  Jam; el código que produce esa medición sí fue auditado.
- Jam tenía modificaciones locales ajenas a `vendor/oracle/` y `medidas/`. Las comprobaciones de la
  auditoría no editaron fuentes de Oracle ni archivos de Jam; este documento y el plan son los únicos
  cambios derivados de la revisión.

## Verificaciones ejecutadas

| Verificación | Resultado observado |
|---|---|
| `python -m unittest discover -s tests -t . -v` | 112 tests, todos verdes |
| `python tools/corpus.py --resumen` | 29 casos; esquema aceptado |
| `python tools/aceptacion.py` | 15 defectos rojos, 11 verdes correctos, 3 huecos declarados |
| `python tools/mutar.py` | 44/44 mutantes de medida muertos |
| `python tools/diferencial.py` en Oracle | falla: Oracle no contiene fixtures diferenciales |
| diferencial contra `jam/medidas` | 269 comparaciones globales, 0 desacuerdos |
| mutación de medidas contra `jam/medidas` | 80/80 mutantes muertos |
| aceptación contra `jam/medidas` | verde vacuo: 0 casos, 0 rojos, 0 verdes |
| `tools/medida.py --relaciones --proyecto .../jam/medidas` | falla con `KeyError: 'grupos'` |

Los resultados verdes prueban que los caminos ejercitados funcionan con el material actual. No
cierran los hallazgos siguientes.

## Hallazgos críticos

### A-01 — Un simulador puede falsificar los hechos certificados por Oracle

**Severidad:** crítica para la integridad del modo simulación.

`nucleo/simulacion.py` calcula `id`, `escenario`, `semilla`, `pasos`, `razon` y `determinista`, pero
después expande `**a.resumen`. El resumen controlado por el simulador puede sobrescribir todos esos
campos. Del mismo modo, un evento puede sobrescribir el campo `corrida` que le asigna el runner.

Se reprodujo con dos ejecuciones diferentes. El simulador devolvió
`resumen={"determinista": True, "id": "falso"}` y un evento con `corrida="inyectada"`; la evidencia
final afirmó exactamente esos valores. Esto permite eludir las medidas de reproducibilidad,
presupuesto y continuidad de traza.

**Evidencia:** `nucleo/simulacion.py`, construcción de `corridas` y `eventos`, líneas 104–110. No hay
tests directos del módulo en la suite actual.

### A-02 — La mutación de código puede dar verde si la suite original ya está roja

**Severidad:** crítica para la afirmación de que los tests fijan el código.

El mutador no ejecuta una línea base sobre el código original. Para cada mutante interpreta cualquier
código de salida distinto de cero como “mutante muerto”. Un `ImportError`, un fallo ambiental o una
suite que falla siempre puede matar todos los mutantes y producir el mensaje “Todos los mutantes
murieron”.

El comportamiento está fijado por el test
`test_si_los_tests_siempre_fallan_TODOS_mueren`; por lo tanto, no es sólo una posibilidad teórica.

**Evidencia:** `nucleo/mutacion_codigo.py`, líneas 216–242;
`tests/test_mutacion_codigo.py`, líneas 132–136; `tools/mutar_codigo.py`, líneas 60–80.

### A-03 — `bytecode_frio` y `resultado_confiable` están hardcodeados

**Severidad:** crítica como caso directo de Goodhart autorreferencial.

`limpiar_cache` usa `shutil.rmtree(..., ignore_errors=True)`, incrementa el contador aunque el borrado
falle y no comprueba que el caché haya desaparecido. Aun así, la evidencia emite incondicionalmente:

```python
"bytecode_frio": True,
"resultado_confiable": True,
```

Se reprodujo con un `__pycache__` enlazado: la función reportó un borrado y el directorio seguía
existiendo. La medida `proceso.arnes_con_bytecode_frio` confía en el booleano producido por el mismo
sensor; `resultado_confiable` no es juzgado por ninguna medida.

**Evidencia:** `nucleo/mutacion_codigo.py`, líneas 207–213 y 263–268.

### A-04 — La ausencia y el cero tienden a convertirse en verde

**Severidad:** alta, transversal al álgebra y las herramientas.

Una fuente usa `evidencia.get(relacion, [])`. Una relación ausente o mal escrita es indistinguible de
una relación presente sin filas. Con la forma predominante `contar <= 0`, el resultado es verde.

También se comprobaron estas invariantes vacías:

- `evaluar([], {})` produce un informe verde por `all([])`;
- una tubería `['desde']` carga y termina con cero filas;
- una medida con cero mutantes aplicables satisface `meta.toda_medida_esta_fijada`, porque sólo se
  comprueba que haya cero mutantes vivos;
- la aceptación de Jam devuelve éxito con cero casos;
- un fixture diferencial existente con cero medidas y cero escenarios no es rechazado por esquema o
  cardinalidad.

**Evidencia:** `nucleo/algebra.py`, líneas 146–147; `nucleo/medida.py`, líneas 164–176;
`catalogos/meta/meta.toda_medida_esta_fijada.json`; `tools/aceptacion.py`, líneas 38–105;
`tools/diferencial.py`, líneas 43–66.

## Hallazgos altos

### A-05 — El diferencial es replay de una foto, no verificación independiente actual

Los fixtures guardan `referencia_ok`, pero no la fecha, el commit o hash de la referencia, el hash del
emisor ni el hash del catálogo. `tools/diferencial.py` relee el JSON; no ejecuta ni comprueba la
implementación de referencia actual. Un verificador manual puede cambiar y el fixture viejo seguir
verde.

En el formato `Dominio`, la comparación además es global: compara el `AND` de todas las medidas contra
un booleano. Dos medidas intercambiadas, una medida demasiado amplia o dos errores que se compensan
pueden mantener el acuerdo global. El cierre de Jam tampoco gatea diferencial y mutación de Oracle.

El emisor geométrico de Jam usa `hash((defecto, i))` como semilla. El hash de strings está salado por
proceso, por lo que regenerar el mismo fixture puede producir mundos distintos sin cambios de código.

**Evidencia:** `nucleo/dominio.py`, líneas 106–131; `tools/diferencial.py`, líneas 43–66;
`/home/workstation/Dev/jam/tools/emitir_diferencial.py`, línea 61.

### A-06 — Apuntar a un proyecto ejecuta código de ese proyecto

`registrar_escalares` importa y ejecuta automáticamente `<proyecto>/escalares.py` mediante
`exec_module`. El proyecto también puede elegirse implícitamente por el directorio actual si contiene
`catalogos/`. Cinco herramientas hacen la carga antes de entrar a su `main`, incluso para operaciones
que sólo pretenden inspeccionar o mostrar ayuda.

Es una extensión UDF intencional, no una puerta trasera. Sin embargo, equivale a ejecución de código
arbitrario con los privilegios del usuario y la frontera de confianza no está advertida ni es opt-in.
El `escalares.py` actual de Jam sólo registra funciones matemáticas; no se encontró un payload.

**Evidencia:** `nucleo/proyecto.py`, líneas 73–86 y 93–115; carga temprana en `aceptacion.py`,
`diferencial.py`, `medida.py`, `mutar.py` y `mutar_codigo.py`.

### A-07 — El camino de autoría no funciona contra el primer proyecto real

`tools/medida.py` sólo entiende fixtures antiguos con la clave `grupos`; los tres fixtures actuales de
Jam usan `escenarios`. Por eso el comando recomendado `--relaciones` falla con `KeyError`.

`--nueva` tiene otro problema: sólo exige que el id contenga un punto y usa el id crudo para construir
una ruta. Un id absoluto o con `../` puede crear un JSON fuera de `catalogos`. Para un proyecto externo,
el intento posterior de mostrar la ruta relativa a Oracle también puede fallar después de escribir.

**Evidencia:** `tools/medida.py`, líneas 52–63 y 102–115.

### A-08 — Hay bypasses y contradicciones en la semántica del álgebra

- La especificación define una relación como conjunto; la implementación conserva duplicados. La
  semántica real es de bolsas y afecta conteos, sumas, promedios, productos y testigos.
- La igualdad exacta de flotantes se prohíbe dentro de expresiones, pero el umbral final usa `_cmp`
  directamente. Una medida puede declarar `umbral == 0.3` y obtener un falso rojo silencioso por
  redondeo.
- `aflojar_umbral` usa `GRANDE = 1e12`. Para un límite `<= 1e15`, la supuesta relajación cambia el
  umbral a `<= 1e12` y lo vuelve más estricto, matando artificialmente el mutante.
- La validación de una medida al cargarla es superficial: estructura, aridades y tipos se descubren al
  evaluar, a veces sólo si existe una fila que alcance la expresión.

**Evidencia:** `ESPECIFICACION.md`, sección 1; `nucleo/algebra.py`, líneas 146–147;
`nucleo/medida.py`, líneas 95–129; `nucleo/mutacion.py`, líneas 30–46.

## Riesgos medios y operativos

- Los equivalentes de mutación se excluyen por presencia del id aunque su razón sea una cadena vacía.
  No existe actualmente `equivalentes.json`, por lo que no hay exclusiones ocultas activas.
- El mutador escribe sobre fuentes reales sin bloqueo ni escritura atómica. Dos instancias concurrentes,
  `SIGKILL`, OOM o pérdida de energía pueden dejar código mutado. Instala manejadores globales de señal
  al importar el módulo y no aplica timeout ni límite de salida al subproceso de tests.
- `unir` materializa el producto cartesiano completo. No hay límites de tamaño, profundidad de
  expresiones o tiempo de simulación impuesto por Oracle; el `tope` sólo se pasa al simulador.
- Las relaciones de nivel meta están fijadas en código a `medida`, `caso` y `medida_en_uso`.
- El catálogo llamado universal contiene convenciones de CPython (`.pyc`), análisis de imports Python,
  la palabra española `tope` y la heurística textual `NO ` para reconocer un alcance.
- `como_hechos` deriva el dominio del prefijo del id y sólo observa la primera fuente de una unión.

## Completitud y generalidad

### Lo que sí quedó abstraído

- `nucleo/` no importa Jam, Unreal ni BotOO.
- Los dominios geometría, vault y relevo viven en `jam/medidas`.
- Proyecto, catálogo y escalares pueden resolverse mediante `--proyecto`, `ORACLE_PROYECTO` o el
  directorio actual.
- La misma representación evaluó hechos de geometría, documentos y repositorios Git.
- El proyecto no tiene dependencias de terceros y los 112 tests actuales pasan.

### Lo que todavía impide llamarlo genérico

- Jam es el único consumidor real y todos los dominios de prueba nacieron en el mismo proyecto, con el
  mismo autor y durante la misma sesión.
- Oracle nació como generalización conceptual del `Medida`/`Umbral`/`Veredicto` creado primero dentro
  de Jam. De los 29 casos del corpus, 18 declaran origen Jam y 11 Oracle.
- Jam conserva dos caminos declarativos: `jam.medida`/`jam.catalogo` y Oracle JSON. Sus tests dinámicos
  de geometría prueban el camino legado, no el núcleo Oracle.
- Los verificadores manuales de vault y relevo siguen siendo los productivos; quedan otros oráculos de
  Jam por reexpresar.
- `con` y el modo izquierdo de `unir` siguen sin implementar.
- El repositorio no declara versión mínima de Python, paquete instalable, CI, licencia ni release.
- Cola y laberinto se usaron durante el desarrollo, pero ya no permanecen como pruebas de regresión.
- No existe todavía un segundo proyecto independiente que pruebe el flujo completo de autoría,
  diferencial, corpus, mutación y entrega.

## Deriva documental observada

- El README habla en distintos lugares de 19 y 29 casos, 53, 81 y 112 tests, y resultados de
  diferenciales ya movidos a Jam.
- El docstring del álgebra todavía dice tres operadores aunque hay cinco implementados.
- `tools/medida.py --escalares` afirma que `agrupar` no tiene usuario.
- Dos de los tres “huecos sin tapar” (`004` y `012`) se describen en sus propios casos como resueltos
  por construcción; el informe sigue contándolos como huecos abiertos.
- Jam manda ejecutar `vendor/oracle/tools/estudio.py`, pero su subtree está un commit atrás y no contiene
  ese archivo.

## Revisión de puerta trasera

No se encontró evidencia de una puerta trasera activa en el árbol o el historial inspeccionado:

- no hay red, telemetría, descarga o persistencia;
- no hay `shell=True`, `eval`, pickle, marshal o YAML inseguro;
- no hay hooks Git activos, submódulos o symlinks versionados;
- no se encontraron claves, tokens o contraseñas;
- los subprocess se invocan con listas, no mediante un shell;
- no hay dependencias externas ni ejecutables privilegiados;
- el núcleo vendorizado en Jam coincide con upstream: no aparece una modificación oculta durante la
  extracción.

La ausencia de una backdoor detectable no vuelve segura la ejecución sobre proyectos no confiables:
`escalares.py` sigue siendo código Python ejecutado deliberadamente.

## Conclusión

Oracle ya demuestra una idea reusable: representar medidas como datos, exigir defensa y alcance, y
producir testigos con un álgebra común. Todavía no demuestra que sus propios verdes sean siempre
fail-closed. Antes de ampliar el lenguaje o reemplazar verificadores de Jam hay que corregir la cadena
de confianza: integridad del sensor, línea base de mutación, invariantes no vacías, frescura del
diferencial y frontera de ejecución de proyectos.

El orden de trabajo y sus criterios de salida están en [`PLAN-CORRECCION.md`](PLAN-CORRECCION.md).
