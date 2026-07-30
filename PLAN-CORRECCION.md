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
- [ ] Separar en la evidencia `baseline_verde`, `tests_fallaron`, `error_arnes` y `timeout`.
- [x] Derivar `resultado_confiable` de comprobaciones reales o eliminar el campo.
- [ ] Incorporar timeout por mutante y conservar la salida del primer fallo para diagnóstico.

**Criterio de salida:** una suite originalmente roja nunca puede producir “todos los mutantes
murieron” ni un código de salida exitoso.

### P0.3 Comprobar de verdad el caché y los equivalentes

- [x] Hacer que `limpiar_cache` falle si no puede borrar un caché o si éste sigue presente.
- [x] Emitir `bytecode_frio=True` sólo después de verificar el estado, no por construcción declarada.
- [x] Probar fallos de borrado y symlinks sin seguir ni borrar su destino.
- [ ] Probar y definir qué ocurre si un caché reaparece durante la misma corrida.
- [x] Rechazar equivalentes con razón vacía, id inexistente o id vencido.
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

## P1 — estabilizar semántica, diferencial e integración externa

### P1.1 Formalizar el contrato del álgebra

- [ ] Decidir mediante una nota de diseño si una relación es conjunto o bolsa.
- [ ] Si es bolsa, corregir especificación y explicar duplicados; si es conjunto, definir identidad y
  deduplicación determinista.
- [ ] Prohibir `==` y `!=` exactos sobre flotantes también en el umbral final.
- [ ] Validar números finitos y tipos compatibles en agregados y umbrales.
- [ ] Sustituir `GRANDE = 1e12` por una mutación independiente de escala y agregar casos por encima y
  por debajo de ese orden de magnitud.
- [ ] Ampliar la mutación de medidas a fuentes, expresiones, agregados y campos; documentar claramente
  el denominador cubierto.

**Criterio de salida:** duplicados y flotantes tienen una semántica única, probada y documentada;
“aflojar” nunca vuelve un umbral más estricto.

### P1.2 Versionar y dar frescura al diferencial

- [ ] Definir una versión de esquema para fixtures.
- [ ] Guardar huellas SHA-256 del emisor, fuentes de referencia, catálogo y configuración usada.
- [ ] Rechazar o marcar como vencido un fixture cuya huella no coincide.
- [ ] Distinguir en datos y salida “acuerdo global del conjunto” de “veredicto individual”.
- [ ] Añadir una regresión donde dos medidas intercambiadas mantengan el `AND` global, para que el
  límite quede visible o sea corregido.
- [ ] Reemplazar `hash()` por una semilla estable derivada con SHA-256 en Jam.
- [ ] Hacer reproducible byte a byte la regeneración de fixtures.

**Criterio de salida:** cambiar una referencia o un emisor vence el fixture; regenerar dos veces sin
cambios produce el mismo archivo; el informe no llama veredictos individuales a comparaciones globales.

### P1.3 Reparar el camino de autoría y el contrato de proyecto

- [ ] Extraer un lector común de fixtures que entienda formatos versionados `grupos` y `escenarios`.
- [ ] Hacer funcionar `--relaciones`, revisión de una medida, diferencial y mutación contra
  `jam/medidas`.
- [ ] Validar ids con una gramática cerrada y confinar toda ruta creada debajo de `catalogos/` después
  de resolverla.
- [ ] Corregir la presentación de rutas para proyectos externos.
- [ ] Validar estructura de proyecto según la herramienta: catálogo, corpus y/o diferencial requerido,
  en vez de aceptar siempre sólo `catalogos/`.
- [ ] Crear un fixture de integración temporal que pruebe el flujo externo completo en tests.

**Criterio de salida:** todos los comandos documentados funcionan sobre Jam y sobre un proyecto mínimo
creado en un directorio temporal; ningún id puede escribir fuera del proyecto.

### P1.4 Hacer explícita la frontera de confianza de las escalares

- [ ] Mover la carga de `escalares.py` dentro de `main`, después de parsear argumentos; `--help` nunca
  debe ejecutar código del proyecto.
- [ ] Exigir una confirmación o bandera explícita para cargar Python de un proyecto externo no marcado
  como confiable.
- [ ] Documentar que una UDF tiene los mismos permisos que Oracle.
- [ ] Aislar el registro por proyecto y declarar nombre, aridad y unidad verificables.
- [ ] Evaluar un modo aislado para inspección que no ejecute UDF.

**Criterio de salida:** abrir ayuda o inventariar archivos no ejecuta código externo; toda ejecución de
UDF es explícita y está documentada como frontera de confianza.

### Puerta P1

P1 termina sólo cuando:

- Oracle se verifica a sí mismo sin verdes vacíos;
- los tres fixtures de Jam son reproducibles y frescos;
- `--relaciones`, aceptación, diferencial y mutación funcionan sobre Jam;
- la suite contiene integración real de un proyecto externo temporal;
- upstream y `vendor/oracle` están sincronizados.

## P2 — robustez operativa y generalidad demostrada

### P2.1 Aislar la mutación de código

- [ ] Mutar una copia o worktree temporal, no las fuentes activas.
- [ ] Añadir bloqueo de ejecución, restauración atómica y limpieza verificable.
- [ ] Acotar tiempo y salida de cada subproceso.
- [ ] Instalar manejadores de señal sólo durante una ronda, sin reemplazar los del proceso al importar.
- [ ] Reanudar una ronda interrumpida con un manifiesto verificable.

**Criterio de salida:** SIGTERM, timeout, dos invocaciones concurrentes y un fallo de escritura no
alteran el worktree original ni dejan procesos huérfanos.

### P2.2 Separar lo universal de los perfiles particulares

- [ ] Mover CPython, `.pyc` y análisis AST de imports a un perfil Python optativo.
- [ ] Reemplazar la razón literal `tope` por un contrato configurable de terminación.
- [ ] Convertir la heurística `NO ` en una señal no normativa o en estructura declarada.
- [ ] Volver extensible la clasificación de relaciones meta.
- [ ] Añadir límites configurables para productos cartesianos, tamaño de entrada y profundidad.

**Criterio de salida:** el catálogo base no presupone Python, español ni el flujo de Jam; los perfiles
particulares se cargan explícitamente.

### P2.3 Cerrar deuda, empaquetar y probar independencia

- [ ] Triar los mutantes vivos (92 en la última ronda completa; cuatro murieron después en pruebas
  dirigidas): test discriminante o equivalencia individual con razón revisada.
- [ ] Reclasificar los casos `004` y `012` como resueltos sin contarlos como huecos abiertos; definir el
  estado honesto de `011`.
- [ ] Implementar `con` y unión izquierda sólo si existen al menos dos usuarios reales; de lo contrario,
  retirarlos de la especificación activa.
- [ ] Añadir `pyproject.toml`, versión mínima de Python, entry points, licencia elegida y CI.
- [ ] Generar cifras del README durante CI en vez de mantenerlas a mano.
- [ ] Completar la migración o retirar el camino legado `jam.medida`/`jam.catalogo` después de un periodo
  de sombra.
- [ ] Validar el flujo con un segundo proyecto que no pertenezca a Jam ni haya sido diseñado junto con
  Oracle.

**Criterio de salida:** cero mutantes vivos no equivalentes, documentación generada y coherente, CI
reproduce las verificaciones y un consumidor independiente completa autoría, diferencial y mutación.

## Primer bloque de trabajo recomendado

El primer bloque debe ser pequeño y dejar una mejora verificable sin migrar formatos todavía:

1. ~~Añadir regresiones para colisiones de simulación y baseline rojo de mutación.~~ Hecho.
2. ~~Corregir ambos contratos.~~ Hecho.
3. ~~Eliminar `bytecode_frio=True` y `resultado_confiable=True` incondicionales.~~ Hecho.
4. ~~Añadir regresiones para cero medidas, cero mutantes y relación ausente.~~ Hecho.
5. ~~Corregir las invariantes vacías y actualizar las medidas meta.~~ Hecho.
6. ~~Ejecutar suite, corpus, aceptación y mutación de medidas.~~ Hecho.
7. ~~Ejecutar mutación de código en una copia temporal y registrar el nuevo baseline.~~ Hecho: la
   última ronda completa fue 454/546 muertos; después cuatro mutantes meta dirigidos murieron 4/4,
   sin una tercera ronda completa.

No se debe empezar por `con`, por migrar verificadores de Jam ni por reducir en masa los mutantes vivos:
primero hay que asegurar que el instrumento que cuenta esos mutantes no pueda declarar confianza por
construcción.

## Siguiente bloque de trabajo

El P0 todavía no está cerrado. Lo siguiente es completar P0.2 y P0.3, sin saltar aún a P1:

1. modelar por separado `tests_fallaron`, `error_arnes` y `timeout`, conservando salida diagnóstica;
2. imponer un timeout por mutante y demostrar que no se confunde con una muerte válida;
3. probar la reaparición de caché durante una ronda;
4. repetir la mutación completa en copia temporal y cerrar el baseline posterior a las regresiones
   dirigidas.
