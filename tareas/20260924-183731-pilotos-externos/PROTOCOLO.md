# Protocolo de validación externa: camino al primer rojo real en Oracle

- **Tarea de origen**: [20260924-183731-pilotos-externos/TAREA.md:1-24](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L1-L24)
- **Responsables definidos**: agy (redacción del protocolo); Brian (convocatoria y coordinación de participantes) según [TAREA.md:20](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L20).
- **Alcance**: 2 a 3 pilotos externos independientes sobre dominios ajenos a juegos, con registro no guiado donde cada traba se convierte en una tarea según [TAREA.md:15-18](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L15-L18).

---

## 1. Fundamento y diagnóstico: qué salió mal y qué ya existe

### 1.1 El problema de partida (la auditoría)

La auditoría técnica de Oracle determinó que la madurez de producto está rezagada respecto a la ingeniería interna:
1. **Consumo endogámico y evidencia sintética**: Todos los proyectos que consumen Oracle hoy (Jam, LyraGASP, commander) pertenecen al autor de la herramienta ([AUDITORIA.md:40](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L40)). Jam tiene 16 medidas y LyraGASP 17 que sólo dependen de evidencia construida ([AUDITORIA.md:41-42](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L41-L42)).
2. **Fracaso del único antecedente externo**: El único ensayo externo registrado fue el desarrollo de una batalla naval por parte del agente `agy`, que culminó con una pantalla verde sin medir ninguna regla del juego ([AUDITORIA.md:44-45](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L44-L45); [POSTMORTEM-BATALLA-NAVAL-AGY.md:7](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L7)).
3. **Costo de entrada y dispersión**: Se detectaron cinco caminos de inicio superpuestos en la documentación (`docs/02-de-cero-a-un-rojo.md`, `docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`, `docs/tutorial-practico.md` y `docs/de-cero.html`), un README de 868 líneas y 23 comandos en el CLI ([AUDITORIA.md:51-53](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L51-L53)).

### 1.2 Qué falló exactamente en el postmortem de agy

El postmortem formal de la batalla naval documentó los mecanismos específicos de la falla:
1. **Ausencia de sensor y de medidas de dominio**: En el código entregado con Oracle no existió ninguna medición de las reglas del juego ([POSTMORTEM-BATALLA-NAVAL-AGY.md:61](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L61)). `catalogos/` y `diferencial/` quedaron completamente vacíos ([POSTMORTEM-BATALLA-NAVAL-AGY.md:86](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L86)).
2. **Confusión entre verificación del corpus y certificación de producto**: Se redactó un único caso (`001-flota-completa.caso`) que evaluaba la medida heredada `proceso.sintaxis_valida_tras_edicion_masiva` con tres booleanos estáticos `true` ([POSTMORTEM-BATALLA-NAVAL-AGY.md:86-88](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L86-L88)). `oracle test --rapido` arrojaba verde exit 0 incluso si se destruía la sintaxis del código ejecutable `game.js` ([POSTMORTEM-BATALLA-NAVAL-AGY.md:7](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L7); [POSTMORTEM-BATALLA-NAVAL-AGY.md:95](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L95)).
3. **Atrapamiento en el ritual de proceso**: El participante desvió su atención hacia el tracker documental (`oracle init`, `oracle tarea init`, `oracle tarea nueva`, `oracle tarea anotar`) en vez de medir el producto ([POSTMORTEM-BATALLA-NAVAL-AGY.md:110-120](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L110-L120); [POSTMORTEM-BATALLA-NAVAL-AGY.md:133-134](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L133-L134)).
4. **Causa raíz comprobada**: La desconexión en la cadena `regla de negocio → sensor → hechos observables L0 → medida aplicada → oracle juzgar` ([POSTMORTEM-BATALLA-NAVAL-AGY.md:140-141](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L140-L141)).
5. **Pérdida de trazabilidad por falta de logs**: La investigación histórica quedó bloqueada al no conservarse transcripts completos ni llamadas de la sesión previa ([POSTMORTEM-BATALLA-NAVAL-AGY.md:3](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L3); [POSTMORTEM-BATALLA-NAVAL-AGY.md:104-106](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L104-L106)).

### 1.3 Qué soluciones ya fueron construidas en el repositorio

Para mitigar lo ocurrido en el postmortem, el repositorio ya cuenta con dos componentes normativos:
1. **La ruta canónica de primer valor** ([docs/13-primer-valor.md:1-306](../../docs/13-primer-valor.md#L1-L306)):
   - Establece los 5 pasos directos: regla concreta → hechos L0 estructurados → medida y 2 casos en corpus → `oracle test` → `oracle juzgar` sobre corrida real ([docs/13-primer-valor.md:30-36](../../docs/13-primer-valor.md#L30-L36)).
   - Aclara que el sensor emite datos puros sin juicios de valor en JSON ([docs/13-primer-valor.md:49-65](../../docs/13-primer-valor.md#L49-L65)).
   - Enseña a aislar el proyecto con `"catalogo_base": false` en `oracle.json` para no heredar políticas de proceso universales ([docs/13-primer-valor.md:73-82](../../docs/13-primer-valor.md#L73-L82)).
   - Enseña a redactar la medida buscando lo que ofende (`donde ...`), con `umbral <= 0`, `requiere` y declaración obligatoria de `alcance` ([docs/13-primer-valor.md:88-103](../../docs/13-primer-valor.md#L88-L103)).
   - Fija la medida con 2 casos de polaridad opuesta: negativo (`falso_verde` esperado ROJO) y positivo (`verde_correcto` esperado VERDE) ([docs/13-primer-valor.md:109-173](../../docs/13-primer-valor.md#L109-L173)).
   - Documenta la salida de `oracle juzgar` ante defecto (exit 1 con testigo infractor) y ante corrección (exit 0 con veredicto verde y reporte de puntos ciegos bajo `SIN MIRAR`) ([docs/13-primer-valor.md:247-282](../../docs/13-primer-valor.md#L247-L282)).
   - Separa conceptualmente evidencia guardada (corpus estático) de evidencia viva regenerada ([docs/13-primer-valor.md:288-292](../../docs/13-primer-valor.md#L288-L292)), y explicita que el tracker es optativo ([docs/13-primer-valor.md:28-29](../../docs/13-primer-valor.md#L28-L29); [docs/13-primer-valor.md:301-304](../../docs/13-primer-valor.md#L301-L304)).
2. **Clarificación del alcance en `oracle test`**:
   - Se modificó la salida del proyecto vacío para reportar `SIN MEDICIÓN` en lugar de `VERDE` ([20260919-135054-test-alcance/TAREA.md:24-29](../../tareas/20260919-135054-test-alcance/TAREA.md#L24-L29); [docs/02-de-cero-a-un-rojo.md:58-59](../../docs/02-de-cero-a-un-rojo.md#L58-L59)).
   - El resumen final de `oracle test` declara expresamente que valida medidas contra casos guardados y que no reejecuta comandos de origen ni el código del producto ([docs/13-primer-valor.md:224-225](../../docs/13-primer-valor.md#L224-L225)).

---

## 2. Participantes del piloto (A quién)

1. **Responsable de reclutamiento**: Brian convoca a los participantes según la asignación de roles en [TAREA.md:20](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L20).
2. **Cantidad**: Exactamente 2 o 3 pilotos independientes ([TAREA.md:18](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L18); [AUDITORIA.md:45-46](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L45-L46)).
3. **Perfil exigido**:
   - Desarrolladores o agentes autónomos ajenos a la autoría de Oracle ([TAREA.md:1](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L1); [AUDITORIA.md:45-46](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L45-L46)).
   - Capacidad comprobada de programar en su entorno habitual (Python, TypeScript, Go o bash).
   - No deben tener conocimiento previo del árbol de fuentes ni de la arquitectura interna de `nucleo/` o `tools/` de Oracle.
4. **Criterios de exclusión**:
   - El autor de Oracle ([AUDITORIA.md:40](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L40)).
   - Colaboradores directos que hayan diseñado el metalenguaje o revisado tareas de arquitectura.

---

## 3. Dominio de la prueba (En qué dominio)

Mandato obligatorio: **al menos uno de los pilotos (y preferentemente todos) debe ser sobre un dominio que NO sea de juegos** ([TAREA.md:15](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L15); [AUDITORIA.md:46](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L46)).

Se definen 3 dominios no recreativos para cubrir los 2 o 3 pilotos requeridos:

| Piloto | Dominio del producto | Ejemplo de regla de negocio observable | Ejemplo de relación L0 del sensor |
|---|---|---|---|
| **Piloto 1** | **Facturación / Procesador de ventas** (CLI o script de datos) | *Consistencia de cobro*: Ningún item facturado puede tener subtotal negativo ni superar el total de la orden. | `linea_factura(orden_id, item_id, precio_unitario, cantidad, subtotal)` |
| **Piloto 2** | **Servicio de Usuarios / Autenticación** (Backend API / servicio web) | *Política de menores y roles*: Ningún usuario menor de 18 años puede tener asignado un rol administrativo (`rol == "admin"`). | `usuario_registrado(id, edad, rol, email_confirmado)` |
| **Piloto 3** | **Despliegue / Configuración de Infraestructura** (DevOps / Pipeline) | *Hardening de red*: Ningún contenedor expuesto a internet pública puede correr como root (`usuario == "root"`) ni tener el puerto SSH (`22`) abierto. | `puerto_servicio(servicio, ambiente, usuario, puerto)` |

*Requisito estructural*: El producto debe contar con una vía ejecutable donde se pueda inducir un defecto real o intencional, emitiendo un archivo de hechos JSON observable ([docs/13-primer-valor.md:51-63](../../docs/13-primer-valor.md#L51-L63)).

---

## 4. Material e insumos provistos (Qué se le da)

Para evitar la confusión y la dispersión detectada en [AUDITORIA.md:51-53](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L51-L53) y [POSTMORTEM-BATALLA-NAVAL-AGY.md:135-138](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L135-L138), el material provisto se circunscribe a un paquete estrictamente delimitado:

### 4.1 Qué SÍ se entrega

1. **Entorno listo o instrucción única de instalación**:
   - Comando estándar: `uv tool install oracle-metalenguaje` o en venv dedicado con `pip` ([README.md:53-67](../../README.md#L53-L67)).
2. **Enlace exclusivo a la documentación canónica**:
   - Se provee únicamente el enlace a [docs/13-primer-valor.md](../../docs/13-primer-valor.md) (referenciado en [README.md:80](../../README.md#L80)).
3. **Consigna de la tarea**:
   - Enunciado claro: *"Tenés este producto en funcionamiento. Tu objetivo es formular una regla de negocio en Oracle que detecte una corrida con un defecto en dicho producto, logrando un fallo rojo real mediante `oracle juzgar` sobre la corrida defectuosa, y un veredicto verde tras corregirlo"*.
4. **El código del producto objetivo**:
   - El código fuente ejecutable del producto del dominio correspondiente (facturación, auth o infraestructura).

### 4.2 Qué NO se entrega ni se sugiere

1. **NO entregar la guía completa de 1.171 líneas**: Evitar saturar al participante con tutoriales extensos que desvíen la atención ([POSTMORTEM-BATALLA-NAVAL-AGY.md:137-138](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L137-L138)).
2. **NO mencionar ni exigir el tracker documental**: No sugerir `oracle tarea init`, `oracle tarea nueva` ni redacción de bitácoras, dado que el tracker es optativo y no forma parte del motor de medición ([docs/13-primer-valor.md:28-29](../../docs/13-primer-valor.md#L28-L29); [docs/13-primer-valor.md:301-304](../../docs/13-primer-valor.md#L301-L304); [POSTMORTEM-BATALLA-NAVAL-AGY.md:133-136](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L133-L136)).
3. **NO escribir el sensor ni la medida por el participante**: El participante debe descubrir cómo extraer la evidencia estructurada en JSON y cómo redactar la regla ([docs/13-primer-valor.md:49-65](../../docs/13-primer-valor.md#L49-L65); [POSTMORTEM-BATALLA-NAVAL-AGY.md:140-141](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L140-L141)).

---

## 5. Variables y observaciones que se registran (Qué se mide)

El objetivo central es medir el tiempo hasta la primera medida roja real, dónde se trabó el participante y qué entendió mal ([TAREA.md:16-17](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L16-L17); [AUDITORIA.md:46](../../tareas/20260924-174258-auditoria/AUDITORIA.md#L46)).

### 5.1 Definición estricta de "Primera medida roja real"

Para evitar validar falsos verdes o rojos no pertinentes:
- **NO califica como rojo real**:
  - Un error de sintaxis al invocar Oracle (`SINTAXIS ERROR`).
  - Un fallo de mutación en `oracle test` por falta de casos ([POSTMORTEM-BATALLA-NAVAL-AGY.md:94](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L94)).
  - La visualización de `ROJO` en `oracle test` sobre un caso estático de polaridad negativa (`falso_verde`), ya que eso es sólo consistencia del corpus ([docs/13-primer-valor.md:138-139](../../docs/13-primer-valor.md#L138-L139); [docs/13-primer-valor.md:200](../../docs/13-primer-valor.md#L200)).
- **SÍ califica como rojo real**:
  - La ejecución de `oracle juzgar --proyecto <dir> --con <hechos.json>` sobre un archivo de hechos extraído de una corrida con defecto real del producto, donde Oracle rechaza la corrida con código de salida `1` (`exit 1`) y reporta explícitamente el testigo infractor que violó la regla ([docs/13-primer-valor.md:247-260](../../docs/13-primer-valor.md#L247-L260); [ejemplo/primer-valor/README.md:98-106](../../ejemplo/primer-valor/README.md#L98-L106)).

### 5.2 Marcas temporales (Timestamps)

Se registran los siguientes hitos temporales precisos:
- $T_0$: Entrega de la consigna y habilitación del participante.
- $T_{\text{doc}}$: Momento en que el participante finaliza la lectura inicial de la documentación provista.
- $T_{\text{sensor}}$: Momento en que el participante logra generar el primer archivo JSON de hechos L0 desde el producto ([docs/13-primer-valor.md:51-63](../../docs/13-primer-valor.md#L51-L63)).
- $T_{\text{medida}}$: Momento en que se crea el archivo `.oracle` en el catálogo ([docs/13-primer-valor.md:84-97](../../docs/13-primer-valor.md#L84-L97)).
- $T_{\text{corpus}}$: Momento en que `oracle test` da verde aprobando sintaxis, casos y mutación del catálogo ([docs/13-primer-valor.md:189-227](../../docs/13-primer-valor.md#L189-L227)).
- $T_{\text{rojo}}$: Momento en que `oracle juzgar` ejecuta exitosamente sobre los hechos del producto defectuoso y devuelve el primer rojo real con testigos ([docs/13-primer-valor.md:247-260](../../docs/13-primer-valor.md#L247-L260)).
- $T_{\text{verde}}$ (opcional pero deseable): Momento en que se corrige el producto, se regenera la evidencia y `oracle juzgar` devuelve verde reportando `SIN MIRAR` ([docs/13-primer-valor.md:267-282](../../docs/13-primer-valor.md#L267-L282)).

**Métrica principal**: $\Delta T_{\text{rojo}} = T_{\text{rojo}} - T_0$.

### 5.3 Dónde se trabó (Categorización de fricciones)

El observador debe clasificar cada interrupción o detención prolongada (> 3 minutos) en una de las siguientes categorías:
1. **Fricción de entorno/instalación**: Inconvenientes con `uv`, `pip`, PEP 668 o PATH ([README.md:57-67](../../README.md#L57-L67)).
2. **Fricción de inicialización/proyecto**: Errores al configurar `oracle.json`, herencia involuntaria de medidas con `catalogo_base: true` ([docs/13-primer-valor.md:76-82](../../docs/13-primer-valor.md#L76-L82)), o carpetas requeridas (`diferencial/`, `corpus/`, `catalogos/`).
3. **Fricción de sensor L0**: Dificultad para concebir o implementar la exportación de hechos del producto a JSON puro ([docs/13-primer-valor.md:47-65](../../docs/13-primer-valor.md#L47-L65)).
4. **Fricción de sintaxis en la medida**: Errores al redactar palabras clave (`de`, `donde`, `umbral <= ... segun contrato porque "..."`, `requiere`, `alcance`, `ambito`) ([docs/13-primer-valor.md:88-103](../../docs/13-primer-valor.md#L88-L103)).
5. **Fricción en mutación / corpus**: Bloqueo en `oracle test` debido a mutantes sobrevivientes (`aflojar_umbral`, `quitar_filtro`, etc.) o dificultad para redactar casos en formato `.caso` con ambas polaridades ([docs/13-primer-valor.md:138-177](../../docs/13-primer-valor.md#L138-L177); [POSTMORTEM-BATALLA-NAVAL-AGY.md:94-96](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L94-L96)).
6. **Fricción en invocación de juicio**: Intentar usar `oracle test` para juzgar el producto en lugar de `oracle juzgar --con <archivo>` ([docs/13-primer-valor.md:27-28](../../docs/13-primer-valor.md#L27-L28); [docs/13-primer-valor.md:247-248](../../docs/13-primer-valor.md#L247-L248)).

### 5.4 Qué entendió mal (Registro de confusiones conceptuales)

El observador debe registrar si el participante manifiesta o incurre en alguna de las confusiones semánticas conocidas:
- **Confusión A (Test vs Certificación)**: Creer que ver verde en `oracle test` implica que el código del producto ya funciona o fue ejecutado ([docs/13-primer-valor.md:27-28](../../docs/13-primer-valor.md#L27-L28); [POSTMORTEM-BATALLA-NAVAL-AGY.md:7-8](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L7-L8)).
- **Confusión B (Tracker vs Medición)**: Asumir que debe inicializar tareas documentales (`oracle tarea`) o seguir un workflow de commits para poder medir ([docs/13-primer-valor.md:28-29](../../docs/13-primer-valor.md#L28-L29); [POSTMORTEM-BATALLA-NAVAL-AGY.md:133-136](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L133-L136)).
- **Confusión C (Polaridad invertida de la medida)**: Intentar filtrar lo que está bien en lugar de lo que ofende ([docs/13-primer-valor.md:86-87](../../docs/13-primer-valor.md#L86-L87)).
- **Confusión D (Caja negra vs Inspección interna)**: Creer que Oracle tiene que leer el código fuente o variables de memoria de la aplicación sin un sensor de hechos JSON ([docs/13-primer-valor.md:47-49](../../docs/13-primer-valor.md#L47-L49)).
- **Confusión E (Evidencia viva vs Guardada)**: Asumir que al modificar el código del producto, los archivos `.caso` en `corpus/` se actualizan solos, o no comprender por qué debe regenerarse el JSON con el sensor antes de invocar `oracle juzgar` ([docs/13-primer-valor.md:288-292](../../docs/13-primer-valor.md#L288-L292)).

---

## 6. Procedimiento de observación sin guiar (Cómo se registra sin guiarlo)

Mandato de [TAREA.md:16-17](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L16-L17): *"cómo se registra sin guiarlo"*.

### 6.1 Principio estricto de no-intervención

1. **Silencio del observador**: El observador no debe guiar, corregir errores tipográficos, anticipar advertencias de Oracle ni responder preguntas operativas sobre sintaxis o comandos.
2. **Respuesta a preguntas del participante**: Si el participante pregunta *"¿Cómo se hace X en Oracle?"* o *"¿Por qué falla este comando?"*, la única respuesta estandarizada permitida es: *"Tenés a disposición la documentación en docs/13-primer-valor.md y los mensajes de salida del comando en la terminal"*.
3. **Criterio de tiempo límite (Timeout)**:
   - Se establece un límite máximo de **90 minutos** por sesión.
   - Si a los 90 minutos no se alcanzó el rojo real, la sesión concluye registrando el estado alcanzado y las causas del bloqueo.

### 6.2 Captura exhaustiva de evidencia (Trazabilidad garantizada)

Para impedir la imposibilidad de reconstrucción documentada en [POSTMORTEM-BATALLA-NAVAL-AGY.md:3](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L3) y [POSTMORTEM-BATALLA-NAVAL-AGY.md:104-106](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L104-L106):
1. **Grabación íntegra de terminal**:
   - En humanos: Toda la sesión de terminal se ejecuta bajo `script -t` o `asciinema rec` con volcado a archivo de registro con timestamp.
   - En agentes LLM: Se almacena íntegramente el archivo de transcript `.jsonl` con cada prompt, llamada de herramienta, salida de shell o edición de archivo sin truncamiento.
2. **Bitácora paralela del observador**:
   - Una plantilla de observación estructurada (ver §6.3) completada en vivo anotando marcas horarias y conducta observable.
3. **Preservación del workspace final**:
   - Al terminar (sea con éxito o por timeout), se congela una copia completa de la carpeta del proyecto del participante (`oracle.json`, `catalogos/`, `corpus/`, hechos exportados, scripts modificados y logs de ejecución).

### 6.3 Plantilla de registro de sesión

```markdown
# Registro de Piloto: [Identificador Piloto / Fecha]

- Participante: [Humano / Agente - Código anónimo]
- Dominio: [Facturación / Auth / DevOps]
- T0 (Inicio de sesión): [HH:MM:SS]
- T_doc (Fin lectura 13-primer-valor): [HH:MM:SS]
- T_sensor (Primer JSON exportado): [HH:MM:SS]
- T_medida (Archivo .oracle escrito): [HH:MM:SS]
- T_corpus (oracle test verde): [HH:MM:SS]
- T_rojo (oracle juzgar exit 1 con testigo): [HH:MM:SS]
- T_verde (oracle juzgar exit 0 tras corrección): [HH:MM:SS]

## Cronología de eventos notables
- [HH:MM:SS] Acción / Comando ejecutado / Salida observada
- [HH:MM:SS] Traba detectada: [categoría §5.3] - [detalle literal]
- [HH:MM:SS] Confusión conceptual manifestada: [confusión §5.4]

## Archivos resultantes
- Ubicación de grabación/transcript: [ruta]
- Copia del workspace del participante: [ruta]
```

---

## 7. Derivación y gestión de hallazgos: Cada traba es una tarea

Mandato expreso: **"Cada traba es una tarea"** ([TAREA.md:18](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L18)).

1. **Procedimiento de apertura**:
   - Al concluir el piloto y analizar la grabación/transcript, cada punto donde el participante se detuvo por error de herramienta, mensaje opaco, error de documentación o mutación confusa da lugar inmediatamente a una tarea nueva en Oracle mediante el comando estándar:
     `oracle tarea nueva "<título descriptivo de la traba>" --sufijo <corto>` ([AGENTS.md:12](../../AGENTS.md#L12)).
2. **Contenido exigido en cada tarea derivada**:
   - Evidencia literal del mensaje de error o comando donde se produjo el bloqueo.
   - Enlace o referencia a la grabación/transcript con marca temporal.
   - Diagnóstico de por qué ocurrió la fricción (distinguiendo problema de CLI, de documentación, de compilador o de ergonomía de sintaxis).
   - Próximo paso concreto para destrabar el problema en el producto ([AGENTS.md:13-15](../../AGENTS.md#L13-L15)).
3. **Criterio de cierre de la tarea matriz**:
   - La tarea matriz [20260924-183731-pilotos-externos](../../tareas/20260924-183731-pilotos-externos/TAREA.md) sólo podrá darse por CERRADA cuando se hayan completado los 2 o 3 pilotos con sus bitácoras archivadas y todas las trabas registradas como tareas individuales ([TAREA.md:18](../../tareas/20260924-183731-pilotos-externos/TAREA.md#L18)).
