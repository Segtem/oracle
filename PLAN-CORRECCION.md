# Plan de corrección de Oracle

Este plan parte de [`AUDITORIA-2026-07-30.md`](AUDITORIA-2026-07-30.md). Ordena el trabajo por cadena
de confianza: primero impedir verdes falsos; después estabilizar formatos y semántica; recién entonces
ampliar el lenguaje, migrar Jam o preparar una release.

## Reglas para ejecutar el plan

1. **Cada bypass entra primero como regresión roja.** El test o caso debe discriminar contra la versión
   actual antes de implementar el arreglo.
2. **Un fallo del arnés no es un mutante muerto.** Error ambiental, timeout y fallo de tests son estados
   distintos y se informan por separado.
3. **Cero evidencia no significa verde.** Se representa como error de contrato o estado “sin material”,
   nunca como éxito.
4. **No se declaran equivalentes en masa.** Cada equivalente lleva una razón no vacía y revisable.
5. **No se agregan operadores durante P0 y P1.** Primero se vuelve confiable lo que ya existe.
6. **Cada fase termina con Oracle y Jam verificados.** Los fixtures de Jam se regeneran sólo cuando el
   formato y la frescura estén definidos.

## P0 — hacer que “verde” sea confiable

### P0.1 Proteger los hechos reservados de simulación

- [x] Agregar tests que reproduzcan la sobrescritura de `determinista`, `id`, `semilla`, `pasos`,
  `razon`, `escenario` y `corrida`.
- [x] Declarar conjuntos explícitos de campos reservados para `corrida` y `evento`.
- [x] Rechazar colisiones desde `Corrida.resumen` y desde cada evento; no resolverlas sólo cambiando el
  orden de `**`, porque eso escondería un simulador mal contratado.
- [x] Validar `pasos` como entero no negativo, `razon` como texto, ids de corrida únicos y campos L0
  escalares.
- [x] Añadir tests directos para `simulacion.py`, incluida una corrida no determinista real.

**Criterio de salida:** ningún dato controlado por el simulador puede sobrescribir un campo certificado
por el runner; los bypasses de la auditoría levantan `SimuladorMalContratado`.

### P0.2 Exigir una línea base verde antes de mutar código

- [x] Ejecutar los tests una vez sobre las fuentes originales antes de generar mutantes.
- [x] Abortar con un error específico si la línea base está roja; no producir hechos `murio`.
- [x] Cambiar el test que hoy canoniza “si los tests siempre fallan, todos mueren”.
- [x] Separar en la evidencia `baseline_verde`, `tests_fallaron`, `error_arnes` y `timeout`.
- [x] Tratar fallos de importación/descubrimiento como error del arnés y detener la suite en la
  primera discriminación antes de que un camino posterior la convierta en timeout.
- [x] Derivar `resultado_confiable` de comprobaciones reales o eliminar el campo.
- [x] Incorporar timeout por mutante y conservar la salida del primer fallo para diagnóstico.

**Criterio de salida:** una suite originalmente roja nunca puede producir “todos los mutantes
murieron” ni un código de salida exitoso.

### P0.3 Comprobar de verdad el caché y los equivalentes

- [x] Hacer que `limpiar_cache` falle si no puede borrar un caché o si éste sigue presente.
- [x] Emitir `bytecode_frio=True` sólo después de verificar el estado, no por construcción declarada.
- [x] Probar fallos de borrado y symlinks sin seguir ni borrar su destino.
- [x] Probar y definir qué ocurre si un caché reaparece durante la misma corrida.
- [x] Revalidar cada ruta en el punto de borrado para que un enumerador mutado no pueda borrar el
  proyecto ni una ruta exterior.
- [x] Confinar físicamente cada fuente antes de leerla o escribirla y rechazar objetivos symlink.
- [x] Rechazar equivalentes con razón vacía, id inexistente o id vencido.
- [x] Validar formato y unicidad de `equivalentes.json`; un incidente de un equivalente también
  invalida la ronda completa.
- [x] Hacer que una declaración equivalente inválida ponga la ronda en rojo.

**Criterio de salida:** no queda ningún booleano de confianza fijado incondicionalmente y una razón
vacía no puede sacar un mutante del denominador.

### P0.4 Eliminar los verdes vacuos

- [x] Hacer que una relación ausente sea `ErrorDeAlgebra`; una relación presente y vacía debe poder
  representarse explícitamente.
- [x] Adaptar el verificador L0: una lista vacía es una relación válida; una clave ausente sigue siendo
  ausencia.
- [x] Validar al cargar una medida: tubería no vacía, primera fuente, operadores, aridades, resumen,
  umbral y tipos básicos.
- [x] Impedir que un catálogo o informe con cero medidas sea verde.
- [x] Impedir que aceptación con cero casos diga `ACEPTACIÓN ✓`; usar un estado no aplicable o error.
- [x] Impedir que una ronda de código con cero mutantes —incluidos todos equivalentes— salga verde.
- [x] Cambiar `meta.toda_medida_esta_fijada` para exigir `mutantes > 0` y
  `mutantes_vivos == 0`, con una política explícita para medidas heredadas.
- [x] Rechazar hechos mutantes sin `apunta_a` vigente o sin un `murio` booleano, para que una fila
  incompleta no cuente silenciosamente como mutante muerto.
- [x] Rechazar fixtures diferenciales sin medidas, sin escenarios, sin ambas polaridades o con
  `mundos` incoherente.

**Criterio de salida:** cero medidas, cero casos, cero mutantes y una relación mal escrita producen un
rechazo explícito, nunca verde.

### Puerta P0

P0 termina sólo cuando:

- todos los bypasses A-01 a A-04 tienen regresiones que discriminan;
- la suite completa pasa;
- aceptación y mutación de medidas siguen funcionando sobre Oracle;
- una copia temporal ejecuta la mutación de código sin tocar el worktree real;
- el informe ya no contiene afirmaciones de confianza autoproducidas.

**Estado 2026-07-30:** puerta cumplida. La suite pasa, Oracle y Jam conservan sus verificaciones y el
baseline particionado cubrió 616 sitios en copias temporales restauradas byte a byte, sin rondas
inconclusas en el agregado final.

## P1 — estabilizar semántica, diferencial e integración externa

### P1.1 Formalizar el contrato del álgebra

- [x] Decidir mediante una nota de diseño si una relación es conjunto o bolsa.
- [x] Si es bolsa, corregir especificación y explicar duplicados; si es conjunto, definir identidad y
  deduplicación determinista.
- [x] Prohibir `==` y `!=` exactos sobre flotantes también en el umbral final.
- [x] Validar números finitos y tipos compatibles en agregados y umbrales.
- [x] Sustituir `GRANDE = 1e12` por una mutación independiente de escala y agregar casos por encima y
  por debajo de ese orden de magnitud.
- [x] Ampliar la mutación de medidas a fuentes, expresiones, agregados y campos; documentar claramente
  el denominador cubierto.

**Criterio de salida:** duplicados y flotantes tienen una semántica única, probada y documentada;
“aflojar” nunca vuelve un umbral más estricto.

**Estado 2026-07-30:** P1.1 implementado. La especificación 0.3 fija relaciones como bolsas, el
umbral final comparte el contrato seguro de comparación, agregados y umbrales rechazan no finitos y
tipos incompatibles, y `aflojar_umbral` avanza una unidad o un flotante representable sin centinela de
escala. El denominador localizado pasó de 48 a 128 mutantes. Su primera ronda mató 118 y dejó diez
huecos; ocho reducciones de borde y dos casos internos los cerraron sin reducir el denominador, por
lo que Oracle queda en 128/128. Contra Jam, el mismo denominador produce 157 mutantes, 146 muertos y
11 vivos; la regeneración fresca de P1.2 confirmó que pertenecen a la cobertura de sus escenarios y
no a fixtures vencidos. Se mantienen explícitos para el siguiente bloque de integración.

### P1.2 Versionar y dar frescura al diferencial

- [x] Definir una versión de esquema para fixtures.
- [x] Guardar huellas SHA-256 del emisor, fuentes de referencia, catálogo y configuración usada.
- [x] Rechazar o marcar como vencido un fixture cuya huella no coincide.
- [x] Distinguir en datos y salida “acuerdo global del conjunto” de “veredicto individual”.
- [x] Añadir una regresión donde dos medidas intercambiadas mantengan el `AND` global, para que el
  límite quede visible o sea corregido.
- [x] Reemplazar `hash()` por una semilla estable derivada con SHA-256 en Jam.
- [x] Hacer reproducible byte a byte la regeneración de fixtures.

**Criterio de salida:** cambiar una referencia o un emisor vence el fixture; regenerar dos veces sin
cambios produce el mismo archivo; el informe no llama veredictos individuales a comparaciones globales.

**Estado 2026-07-30:** P1.2 implementado. `oracle.diferencial/v1` firma emisor, referencia, catálogo
canónico y configuración; una diferencia vence el fixture antes de evaluarlo. Cada escenario separa
el acuerdo global independiente de la fotografía de veredictos individuales, incluida una regresión
de permutación compensada. Los tres fixtures de Jam se regeneraron dos veces con SHA-256 idénticos;
el cierre reporta 269 acuerdos globales y 1158 veredictos individuales estables. Los 11 mutantes de
medida vivos de Jam permanecen explícitos y no se confundieron con frescura.

### P1.3 Reparar el camino de autoría y el contrato de proyecto

- [x] Extraer un lector común de fixtures que entienda formatos versionados `grupos` y `escenarios`.
- [x] Hacer funcionar `--relaciones`, revisión de una medida, diferencial y mutación contra
  `jam/medidas`.
- [x] Validar ids con una gramática cerrada y confinar toda ruta creada debajo de `catalogos/` después
  de resolverla.
- [x] Corregir la presentación de rutas para proyectos externos.
- [x] Hacer que `tools/estudio.py --proyecto` resuelva escalares externas mediante una confirmación
  explícita de confianza.
- [x] Validar estructura de proyecto según la herramienta: catálogo, corpus y/o diferencial requerido,
  en vez de aceptar siempre sólo `catalogos/`.
- [x] Crear un fixture de integración temporal que pruebe el flujo externo completo en tests.

**Criterio de salida:** todos los comandos documentados funcionan sobre Jam y sobre un proyecto mínimo
creado en un directorio temporal; ningún id puede escribir fuera del proyecto.

**Estado 2026-07-30:** P1.3 implementado. `nucleo/fixtures.py` es el único lector de ambos formatos y
también aplica frescura cuando lo consumen autoría o mutación. Jam completa inventario, revisión,
diferencial y mutación sin caminos especiales; un proyecto temporal recorre además corpus,
aceptación y estudio. Los ids siguen una gramática cerrada, el destino se confina físicamente y un
symlink exterior tiene regresión. Estudio carga UDF externas sólo con `--confiar-escalares`; P1.4
llevó luego ese opt-in y la carga dentro de `main` al resto de las herramientas. Al sincronizar el vendor
apareció la deriva que aún reportaba 80/80 con el mutador antiguo; actualizado, Jam vuelve a mostrar
el denominador real de 157, con 146 muertos y 11 vivos.

### P1.4 Hacer explícita la frontera de confianza de las escalares

- [x] Mover la carga de `escalares.py` dentro de `main`, después de parsear argumentos; `--help` nunca
  debe ejecutar código del proyecto.
- [x] Exigir una confirmación o bandera explícita para cargar Python de un proyecto externo no marcado
  como confiable.
- [x] Documentar que una UDF tiene los mismos permisos que Oracle.
- [x] Aislar el registro por proyecto y declarar nombre, aridad y unidad verificables.
- [x] Evaluar un modo aislado para inspección que no ejecute UDF.

**Criterio de salida:** abrir ayuda o inventariar archivos no ejecuta código externo; toda ejecución de
UDF es explícita y está documentada como frontera de confianza.

**Estado 2026-07-30:** P1.4 implementado. Seis ayudas y los inventarios `--relaciones` y
`--escalares` tienen regresiones que demuestran ausencia de ejecución externa. Las operaciones que
cargan o evalúan un catálogo externo exigen `--confiar-escalares`; el registro se activa en un
contexto y se restaura siempre. Nombre, unidad, aridad y procedencia se validan al declarar, y un
`escalares.py` symlink o una inserción que evita `@escalar` falla cerrado. La integración temporal
usa una UDF real y sólo concede confianza en los cinco comandos que la necesitan.

### Puerta P1

P1 termina sólo cuando:

- Oracle se verifica a sí mismo sin verdes vacíos;
- los tres fixtures de Jam son reproducibles y frescos;
- `--relaciones`, aceptación, diferencial y mutación funcionan sobre Jam;
- la suite contiene integración real de un proyecto externo temporal;
- upstream y `vendor/oracle` están sincronizados.

**Estado de la puerta P1:** cumplida. Oracle pasa 217 tests, aceptación y 128/128 mutantes de medida;
los fixtures reproducibles de Jam conservan 269 acuerdos globales y 1158 veredictos individuales.
El vendor ejecuta el mismo denominador y expone, sin pintarlos de verde, sus 11 mutantes vivos.

## P2 — robustez operativa y generalidad demostrada

### P2.1 Aislar la mutación de código

- [x] Mutar una copia o worktree temporal, no las fuentes activas.
- [x] Añadir bloqueo de ejecución, restauración atómica y limpieza verificable.
- [x] Acotar tiempo y salida de cada subproceso.
- [x] Instalar manejadores de señal sólo durante una ronda, sin reemplazar los del proceso al importar.
- [x] Reanudar una ronda interrumpida con un manifiesto verificable.

**Criterio de salida:** SIGTERM, timeout, dos invocaciones concurrentes y un fallo de escritura no
alteran el worktree original ni dejan procesos huérfanos.

**Estado 2026-07-30:** P2.1 implementado. `correr()` valida los objetivos originales, copia el
proyecto y sólo entrega rutas de la copia al bucle mutante. Las escrituras internas usan
`os.replace`; un bloqueo estable por raíz rechaza una segunda ronda. Cada subproceso abre una sesión,
tiene timeout y captura drenada con límite; SIGTERM termina el grupo y los handlers se restauran al
salir. Un manifiesto atómico firma fuentes, motor y configuración, guarda cada mutante terminado y
reanuda sólo si todo sigue coincidiendo. Regresiones reales cubren SIGTERM sin hijo huérfano, lock
doble, escritura fallida, limpieza temporal, salida excesiva, nietos resistentes y
reanudación/corrupción. Suite: 225.

### P2.2 Separar lo universal de los perfiles particulares

- [x] Mover CPython, `.pyc` y análisis AST de imports a un perfil Python optativo.
- [x] Reemplazar la razón literal `tope` por un contrato configurable de terminación.
- [x] Convertir la heurística `NO ` en una señal no normativa o en estructura declarada.
- [x] Volver extensible la clasificación de relaciones meta.
- [x] Añadir límites configurables para productos cartesianos, tamaño de entrada y profundidad.

**Criterio de salida:** el catálogo base no presupone Python, español ni el flujo de Jam; los perfiles
particulares se cargan explícitamente.

**Estado 2026-07-30:** P2.2 implementado. El AST de imports, las medidas de módulos/CPython y el
mutador de `.py` viven en `perfiles/python`; `oracle.json` es el único mecanismo que añade ese perfil
al catálogo universal. La terminación se clasifica mediante `ContratoTerminacion`, no mediante una
razón literal. Se retiró la medida que convertía el token español `NO ` en requisito normativo y
`ClasificacionMeta` permite ampliar relaciones/prefijos sin mutar globales. `LimitesAlgebra` acota por
evaluación filas de entrada, productos y profundidad, con techos finitos por defecto. Oracle pasa
234 tests, aceptación y 129/129 mutantes de medida.

**Refuerzo 2026-07-30:** el núcleo ya no enumera perfiles conocidos: descubre cualquier
`perfiles/<nombre>/catalogos` físico y sólo `oracle.json` lo activa. Las herramientas seleccionan
medidas juezas por las relaciones declaradas que pueden consumir, no por ids `proceso.*` incorporados
al código. `nucleo/` tiene una regresión que prohíbe imports hacia perfiles y quedó sin ejemplos de
dominios Jam en sus módulos.

### P2.3 Cerrar deuda, empaquetar y probar independencia

- [x] Reemplazar el baseline vencido 503/616 y triar el denominador actual: test discriminante o
  equivalencia individual con razón revisada.
- [x] Reclasificar los casos `004` y `012` como resueltos sin contarlos como huecos abiertos; definir el
  estado honesto de `011`.
- [x] Implementar `con` y unión izquierda sólo si existen al menos dos usuarios reales; de lo contrario,
  retirarlos de la especificación activa.
- [x] Añadir `pyproject.toml`, versión mínima de Python, entry points y CI.
- [ ] Elegir y declarar la licencia (decisión legal del autor, no inferible del repositorio).
- [x] Generar y comprobar las cifras del README durante CI en vez de mantenerlas a mano.
- [x] Confirmar que Oracle no importa ni resuelve caminos legados de un consumidor; el corpus conserva
  procedencia histórica sólo como datos.
- [x] Validar el flujo completo con un proyecto externo sintético, catálogo y UDF propios.
- [ ] Obtener evidencia de un consumidor real que no haya sido diseñado junto con Oracle.

**Criterio de salida:** cero mutantes vivos no equivalentes, documentación generada y coherente, CI
reproduce las verificaciones y un consumidor independiente completa autoría, diferencial y mutación.

**Estado parcial 2026-07-30:** los casos `004` y `012` ya son memoria resuelta y `011` declara una
frontera humana; el corpus informa cero huecos abiertos. Al no existir dos usuarios reales, `con` y
la unión izquierda se retiraron de la especificación y del parser activos, con regresiones de rechazo.
Suite: 319. El alcance actual tiene 1073 sitios; `grafo`, `macro`, `marco`, `dominio`, `simulacion` y
el sensor Python de módulos suman 137/137, `diferencial` aporta 42/42, `proyecto` 79/79 y `medida`
98/98, `fixtures` 128/128, `mutacion` 147/147 y `algebra` 237/237: 868/868 ejecutados sin
equivalencias. La partición de proyecto añadió contratos de selección, configuración, confinamiento
y opt-in de código externo;
también retiró nueve constantes redundantes, incluido el truncado fijo de la huella del módulo. La de
medida fijó validación de la clasificación meta, inmutabilidad de sus cuatro datos públicos, salida
Unicode y derivación de relaciones; además movió su excepción antes del primer uso. La de fixtures
fijó cada nivel del esquema, consistencia de fotos y proyección a mutación, y retiró un default
inobservable. La del mutador de medidas fijó IDs/rutas estructurales, negación y conteo agrupado, y
retiró cuatro sitios redundantes. La de álgebra fijó límites, firmas escalares, ausencia, aridad,
agregados mixtos y bordes inclusivos; retiró cuatro sitios redundantes y convirtió nueve roturas de
inicialización en fallos atribuibles al código. La generalización posterior descubre perfiles sin
registro central, deriva juezas desde sus relaciones y separa los esquemas de corrida de los dos
sensores de mutación. Los 205 sitios vigentes de `perfiles/python/mutacion_codigo.py` cerraron
205/205 sin equivalencias, timeout ni error de arnés: el total queda en 1073/1073. El manifiesto firma
ahora también las fuentes de tests y soporte; cambiar la suite invalida la reanudación. El paquete se
construye desde `pyproject.toml`, declara Python >=3.11 y siete entry points; CI reproduce contratos,
comprueba las cifras derivables y ejecuta las trece particiones mutacionales. Siguen pendientes la
licencia y la evidencia —necesariamente externa— de un consumidor real independiente.

## Primer bloque de trabajo recomendado

El primer bloque debe ser pequeño y dejar una mejora verificable sin migrar formatos todavía:

1. ~~Añadir regresiones para colisiones de simulación y baseline rojo de mutación.~~ Hecho.
2. ~~Corregir ambos contratos.~~ Hecho.
3. ~~Eliminar `bytecode_frio=True` y `resultado_confiable=True` incondicionales.~~ Hecho.
4. ~~Añadir regresiones para cero medidas, cero mutantes y relación ausente.~~ Hecho.
5. ~~Corregir las invariantes vacías y actualizar las medidas meta.~~ Hecho.
6. ~~Ejecutar suite, corpus, aceptación y mutación de medidas.~~ Hecho.
7. ~~Ejecutar mutación de código en una copia temporal y registrar el nuevo baseline.~~ Hecho:
   503/616 muertos y 113 vivos; cero timeout/error de arnés en el agregado final y copias restauradas
   byte a byte.

No se debe empezar por `con`, por migrar verificadores de Jam ni por reducir en masa los mutantes vivos:
primero hay que asegurar que el instrumento que cuenta esos mutantes no pueda declarar confianza por
construcción.

## Bloque de cierre P0

P0 quedó cerrado sin saltar todavía a P1:

1. ~~Modelar por separado `tests_fallaron`, `error_arnes` y `timeout`, conservando salida
   diagnóstica.~~ Hecho.
2. ~~Imponer un timeout por mutante y demostrar que no se confunde con una muerte válida.~~ Hecho.
3. ~~Probar la reaparición de caché durante una ronda.~~ Hecho: una reaparición invalida la ronda
   antes de que la limpieza pueda ocultarla.
4. ~~Repetir la mutación completa en copia temporal y cerrar el baseline posterior a las regresiones
   dirigidas.~~ Hecho: 503/616, con 113 vivos explícitos y ninguna ejecución inconclusa.

El siguiente bloque recomendado es P1.1: formalizar semántica de bolsas/conjuntos, flotantes y
mutación independiente de escala antes de ampliar operadores o migrar formatos de Jam.

## P3 — autonomía de embedding

P2 cerró la independencia semántica: el núcleo ya no conoce Jam, Unreal ni nombres de perfiles o
juezas particulares. P3 separa otra pregunta que el flujo externo desde el checkout no contestaba:
si Oracle puede entrar como biblioteca en un proceso ajeno sin que el consumidor importe internals,
modifique `sys.path` o comparta estado mutable con otro proyecto.

### Hallazgos que abren P3

- El wheel se construye sin dependencias y sus entry points pueden leer un proyecto externo desde un
  entorno aislado.
- El paquete instala nombres de primer nivel demasiado genéricos (`nucleo`, `catalogos`, `perfiles`,
  `tools`) y no publica una fachada estable: `nucleo/__init__.py` está vacío.
- Un consumidor embebido debe coordinar por su cuenta `Proyecto`, catálogos, escalares, límites,
  selección de medidas y evaluación.
- `ESCALARES` sigue siendo un registro global. El contexto de proyecto lo restaura al salir, pero dos
  motores concurrentes no poseen estado independiente.
- Las herramientas resuelven `PROY` desde `sys.argv` al importar, lo que mezcla biblioteca y CLI.
- El wheel incluye catálogos y perfiles, pero no el corpus de autocertificación: instalado sin
  `--proyecto`, `oracle-aceptacion` falla porque falta `corpus/`. Ese comportamiento debe ser una
  decisión, no un accidente de empaquetado.
- El catálogo base se inyecta siempre. Es una política útil, pero un proyecto debe poder declararla u
  omitirla explícitamente para evitar colisiones de relaciones.

### P3.1 Fijar una fachada pública antes de migrar consumidores

- [x] Publicar `oracle_metalenguaje.Motor` como único punto de entrada recomendado para embedding.
- [x] Construir un motor desde una ruta de proyecto sin que el consumidor conozca módulos internos.
- [x] Evaluar evidencia seleccionando medidas por relaciones y devolver el `Informe` vigente.
- [x] Permitir límites por motor y confianza explícita de escalares externas.
- [x] Mantener compatibilidad temporal con los imports internos mientras se fija el contrato.
- [x] Probar la fachada desde un wheel instalado y un directorio de trabajo vacío.

**Criterio de salida:** un consumidor sólo importa `Motor`, entrega hechos y recibe un informe; no
inserta rutas ni importa `nucleo.*`, `catalogos.*`, `perfiles.*` o `tools.*`.

### P3.2 Aislar estado y composición

- [x] Introducir `RegistroEscalares` por instancia y hacer que validación y evaluación reciban ese
  registro explícitamente.
- [x] Demostrar dos motores con UDF homónimas y distintas en el mismo proceso, sin contaminación.
- [x] Volver explícita la inclusión de las políticas base; un proyecto v1 neutral no las recibe si
  omite `catalogo_base`.
- [x] Permitir fuentes de perfiles adicionales sin modificar la instalación de Oracle.
- [x] Eliminar la resolución de `sys.argv` durante el import de herramientas; `main(argv)` construye
  su sesión después de parsear.

**Criterio de salida:** dos proyectos pueden cargarse y evaluarse intercalados o en paralelo sin que
catálogos, perfiles, UDF, límites o argumentos de uno alteren al otro.

### P3.3 Namespace y recursos instalables

- [x] Mover la implementación bajo `oracle_metalenguaje/` o proporcionar una transición verificable
  que elimine los paquetes públicos genéricos.
- [x] Resolver recursos empaquetados con una raíz de paquete, no con la raíz amplia de
  `site-packages`.
- [x] Decidir si el corpus/diferencial de autocertificación se distribuyen o si los comandos instalados
  siempre exigen `--proyecto`; documentar y probar una sola semántica.
- [x] Probar wheel, entry points, recursos, proyecto sintético y dos motores desde fuera del checkout.

**Criterio de salida:** instalar Oracle no agrega paquetes genéricos al entorno, todos los recursos se
resuelven dentro de su distribución y ningún comando depende accidentalmente del checkout fuente.

### Puerta P3

P3 termina sólo cuando:

- Jam puede integrar `Motor` sin conocer la disposición interna de Oracle;
- dos motores con proyectos y UDF diferentes coexisten sin estado compartido;
- el wheel se prueba desde un entorno limpio y fuera del checkout;
- la política de catálogos y perfiles es explícita;
- la suite, aceptación, diferencial y mutación conservan sus resultados;
- no se amplía el lenguaje ni se migra todavía ningún oráculo particular de Jam.

**Estado 2026-07-31:** P3 implementado del lado de Oracle. `oracle_metalenguaje.Motor` construye desde datos, medidas o
una ruta explícita; selecciona por relaciones, conserva límites por instancia y falla cerrado si no
hay juezas aplicables. `RegistroEscalares` viaja por validación y ejecución; dos proyectos con una UDF
homónima se construyen y evalúan concurrentemente sin tocar el registro global. La carga externa
sigue siendo opt-in y una escritura directa al global se rechaza. `oracle.json` acepta
`catalogo_base`; si falta, vale `false`, de modo que la configuración mínima no hereda políticas de
Oracle. Un smoke test construye el
wheel, lo inspecciona, lo instala en un venv limpio y usa sólo la fachada desde un cwd vacío. El wheel
publica exclusivamente `oracle_metalenguaje.*`; el puente `_compat` mantiene el checkout transitorio
sin instalar `nucleo`, `catalogos`, `perfiles` ni `tools` como paquetes de primer nivel. Las raíces externas de
perfiles las aporta el host —el proyecto sólo puede seleccionar nombres— y rechazan symlinks, rutas
ausentes y nombres ambiguos; el smoke del wheel usa una raíz externa real. Ninguna herramienta
resuelve ya proyecto ni argumentos al importarse: sus `main(argv)` crean la sesión después de
parsear, probado bajo un `sys.argv` anfitrión inválido. Una instalación no contiene el corpus ni los
fixtures diferenciales internos y por eso exige un proyecto explícito; la ausencia de fixtures sale
no-verde y sin traceback. El flujo temporal externo conserva la prueba diferencial positiva. La suite
cierra 339 tests, la mutación de medidas 129/129 y las particiones modificadas de `proyecto`, `Motor`
y `_compat` cierran 100/100, 22/22 y 5/5. Queda fuera de P3 sincronizar el vendor de Jam y migrar su
oráculo particular.

### Cierre de independencia de dominio — 2026-07-31

El valor compatible anterior (`catalogo_base: true` cuando faltaba la clave) mantenía una política
implícita: cualquier proyecto externo incorporaba medidas de proceso, meta y simulación de Oracle.
Se eliminó. Ahora un proyecto sin `oracle.json`, o con la clave omitida, carga exclusivamente su
propio catálogo. Las políticas provistas por Oracle y los perfiles son capacidades opt-in; el propio
Oracle declara ambas porque las usa para autocertificarse, y cada consumidor debe tomar la misma
decisión de manera explícita.

La independencia se protege en tres niveles: una regresión construye un proyecto mínimo y comprueba
que no aparecen medidas heredadas; otra inspecciona los artefactos productivos y rechaza nombres de
consumidores o dominios conocidos; y el wheel se prueba desde un proyecto externo y un cwd vacío. El
corpus y los tests pueden conservar procedencia histórica de Jam: son evidencia de generalidad y no
se instalan ni participan del runtime de un host.
