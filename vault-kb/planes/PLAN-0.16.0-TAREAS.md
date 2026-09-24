# Roadmap 0.16.0 — tareas y contexto de trabajo en Git

Fecha: 2026-09-11. Base: distribución 0.15.0, álgebra 0.6, sintaxis 0.4.
Estado al 2026-09-13: P0–P4 implementados con agy, revisados y verificados por Codex.
Ver [el encargo](../estudios/0.16.0-tareas/ENCARGO-AGY.md),
[el avance de agy](../estudios/0.16.0-tareas/AVANCE-AGY.md) y
[la sesión de trabajo](../estudios/0.16.0-tareas/SESION-AGY.md).
El [cierre de P0–P1](../estudios/0.16.0-tareas/CIERRE-P0-P1.md) reúne resultados y límites.
P2 está implementado y verificado por agy y Codex; ver [cierre P2](../estudios/0.16.0-tareas/CIERRE-P2.md).
P3 está cerrado; ver [cierre P3](../estudios/0.16.0-tareas/CIERRE-P3.md).
P4 está cerrado; ver [cierre P4 y propuesta de corte](../estudios/0.16.0-tareas/CIERRE-P4.md).
El dueño autorizó el corte el 2026-09-13: distribución **0.16.0**, álgebra **0.6**, sintaxis **0.4**.
La verificación del número aplicado se registra en [el corte](../estudios/2026-09-13-corte-0.16.0/README.md).

## El problema y el recorrido que debe resolver

El dueño junta capturas, videos de YouTube, enlaces, notas e investigaciones en carpetas sueltas.
No tiene una vista general de TODOs, issues y tareas, ni una historia en Git de ese contexto.
Oracle ya conserva planes, decisiones, estudios y relevos, pero esos documentos no constituyen
un listado vigente de pendientes.

La entrega sirve cuando una persona puede crear una tarea, guardar el material al lado,
reencontrarla por una consulta, cerrarla y recuperar tanto el contexto como su historia en Git.
Debe funcionar también desde el paquete instalado en un repositorio consumidor.

## Qué tomamos de tatr y qué adaptamos

Referencias consultadas el 2026-09-11:

- [Formato de carpetas, HUID y TASK.md](https://github.com/tsoding/tatr#the-spec).
- [CLI: init, new, ls, find, ref, summary y graph](https://github.com/tsoding/tatr/blob/main/src/tatr.c).
- [Carga de tareas y tratamiento de entradas omitidas](https://github.com/tsoding/tatr/blob/main/src/task.c).

Conservamos una carpeta por registro, identidad estable, Markdown editable, adjuntos cercanos,
consultas por etiquetas y Git como historia. Implementamos la conducta en Python con la biblioteca
estándar; tatr es referencia de diseño, no una dependencia ni código C para incorporar.

La interfaz sigue el sustantivo y los verbos en español de Oracle. `ls` es alias explícito de
`listar`, declarado y documentado en el registro del CLI. El contenido permanece legible sin Oracle.
El formato propio no se anuncia como compatible con tatr: importar o exportar su formato requiere
un contrato y pruebas posteriores.

```text
proyecto/
  tareas/
    README.md
    20260911-180000-brian/
      TAREA.md
      captura.png
      notas.md
```

Plantilla inicial propuesta:

```markdown
# Investigar un defecto del sensor

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: bug, sensor

Descripción, referencias y apuntes en Markdown libre.
```

Estados iniciales: `ABIERTA` y `CERRADA`. La prioridad mayor aparece primero; los empates se
resuelven por ID en orden estable. Las etiquetas son libres: `bug`, `idea`, `investigacion`,
`kb`, `en-curso`, etc. No se impone un circuito de estados ni tres subsistemas de contenido.
Una nota de KB puede quedar abierta y enlazada sin inventarle una promesa de finalización.

## Entregas y criterios de salida

Cada tramo depende del anterior. El estado se actualiza con archivos y comandos efectivamente
verificados. Los comandos de P1–P3 están disponibles en este checkout; P4 completó el uso propio
y la preparación del corte con las verificaciones registradas.

### P0 — contrato mínimo y ejemplos

Responsable: agy. Completado y revisado; contrato en [docs/12-tareas.md](../../docs/12-tareas.md).

- Documentar el formato, descubrimiento de raíz, identidad, orden, errores y códigos de salida.
- Usar IDs de fecha/hora UTC con sufijo opcional y resolver colisiones sin sobrescribir ni esperar
  indefinidamente; probar dos creaciones en el mismo segundo.
- Dar precedencia a `--proyecto`, luego `ORACLE_PROYECTO`, después búsqueda local ascendente.
  La búsqueda automática se detiene en el límite Git y no salta a un tracker de otro repositorio.
  La raíz explícita contiene `tareas/`. `init` puede iniciar sólo el tracker sin exigir catálogos.
- Mantener el tracker utilizable aunque una medida esté rota: resolver ubicación no debe ejecutar
  escalares ni cargar/evaluar el catálogo.
- Precisar el bloque de metadatos: campos duplicados o estados inválidos son errores; texto parecido
  dentro de la descripción o de un bloque de código no se interpreta como metadato.

Salida: contrato escrito y ejemplos de tarea mínima, investigación con referencias y nota de KB.
Los ejemplos son construidos y no se presentan como observaciones ni casos del corpus.

### P1 — tracker local usable desde Oracle

Responsable: agy. Completado y revisado; recorrido del paquete instalado verificado por Codex.

```bash
oracle tarea init
oracle tarea nueva "Investigar un defecto del sensor" --etiqueta bug
oracle tarea listar
oracle tarea ls --etiqueta bug
oracle tarea ver <id>
oracle tarea cerrar <id>
oracle tarea reabrir <id>
oracle tarea revisar
```

- `nueva` crea carpeta y plantilla, y devuelve ID y ruta. Las lecturas no escriben archivos.
- `listar` muestra abiertas por defecto; permite cerradas, todas, etiqueta, texto y salida JSON.
  Cero coincidencias es éxito; datos ilegibles o argumentos inválidos no se disfrazan de lista vacía.
- `ver` acepta ID completo; los prefijos sólo se aceptan si son inequívocos. `--ruta` permite
  componer con el editor o la shell. JSON es salida derivada, no otra fuente de verdad.
- `cerrar` y `reabrir` cambian sólo el estado, preservando descripción, campos desconocidos y
  adjuntos; repetición del mismo estado es idempotente. Escrituras mediante reemplazo atómico.
- `revisar` denuncia registros mal formados, carpetas candidatas sin `TAREA.md` y omisiones.
  `README.md` y archivos auxiliares documentados no se confunden con tareas rotas.
- Los listados tampoco ocultan registros rotos: diagnóstico con ruta y salida no exitosa.
- Rutas e IDs no permiten escribir fuera del tracker ni seguir enlaces simbólicos hacia otro lugar.
- Ayuda, alias y manual nacen de las declaraciones del CLI; el wheel incluye la herramienta.

Salida: recorrido crear → editar con el editor → listar → ver → cerrar → reabrir en un proyecto
temporal, desde subcarpeta y desde instalación limpia, con tests de los fallos de datos y rutas.
No hay commits automáticos: crear un archivo y versionarlo son operaciones distintas.

### P2 — capturar material y recuperar relaciones

Completado y revisado el 2026-09-12. Agy implementó captura y consultas; Codex implementó seguimiento
en Git y verificó la integración. Ver [encargo P2](../estudios/0.16.0-tareas/ENCARGO-P2-AGY.md)
y [revisión P2](../estudios/0.16.0-tareas/REVISION-P2-CODEX.md).

- Agregar notas, URLs y archivos mediante operaciones simples (`anotar`, `adjuntar`). Una URL
  conserva el texto y timestamp que aporte la persona; no necesita descargar la página o el video.
- Copiar adjuntos explícitos sin sobrescribir nombres existentes ni mover el original.
  Registrar enlaces relativos y preservar nombres Unicode y espacios.
- `buscar` y `referencias`: buscar texto y encontrar menciones entre tareas, notas y código.
  Distinguir mención textual de dependencia declarada.
- `resumen`: cantidades por estado y etiquetas derivadas de archivos válidos.
- Mostrar si los archivos están sin seguimiento o ignorados por Git. El diagnóstico de cobertura
  debe impedir afirmar que el trabajo quedó versionado sólo porque existe en `tareas/`.
- Documentar que un enlace remoto guarda la referencia, no el contenido remoto; definir el manejo
  de archivos grandes antes de incluir videos locales. Sin descarga masiva ni LFS obligatorio.

Salida: una captura, una URL con timestamp y una nota quedan vinculadas a una tarea, se encuentran
por búsqueda y un diagnóstico distingue archivos registrados en Git de archivos todavía locales.

### P3 — hechos de seguimiento que Oracle pueda medir

Completado y revisado el 2026-09-12. Agy implementó `oracle tarea hechos`; Codex escribió políticas
optativas y relaciones en `ejemplo/seguimiento-tareas/`, preparó casos/mutación y verificó el
recorrido instalado. Ver [cierre P3](../estudios/0.16.0-tareas/CIERRE-P3.md),
[encargo P3](../estudios/0.16.0-tareas/ENCARGO-P3-AGY.md) y
[revisión P3](../estudios/0.16.0-tareas/REVISION-P3-CODEX.md).

- Sensor explícito y determinista que emita hechos de tareas, adjuntos y referencias locales.
  El contrato debe distinguir declarado, observado y no comprobado.
- Medidas opcionales del proyecto sobre integridad de referencias y cobertura de seguimiento.
  Se escriben en el lenguaje existente; no se amplía el álgebra para gestionar tareas.
- Cada medida trae alcance, defensa y casos de ambas polaridades; se verifica por mutación.
- No exigir universalmente una verificación técnica para cerrar una idea o una nota. Una política
  para bugs corregidos puede exigir vínculos a evidencia, pero debe declarar qué no comprueba.
- Conectar consultas de contexto después de definir su costo y tamaño; el servidor MCP conserva
  su contrato de sólo lectura.

Salida: un defecto construido de integridad produce testigos y un ejemplo correcto pasa; un
enlace existente no se presenta como prueba de autenticidad ni de que una tarea está bien resuelta.

### P4 — uso propio y preparación del corte

Completado el 2026-09-13. Se registraron tres pendientes reales en `tareas/` y se verificó el
recorrido de uso propio. Agy revisó el tutorial y el código; Codex reprodujo y corrigió los
hallazgos. Las cuatro rondas de código cerraron en 762/762 y la suite general en 1852 tests.
Ver [cierre y evidencia P4](../estudios/0.16.0-tareas/CIERRE-P4.md). El tutorial utiliza material
construido; no hubo capturas ni videos personales disponibles para migrar.

- Registrar los pendientes vigentes de este roadmap como primeras tareas del propio Oracle.
  Enlazar decisiones, estudios y relevos existentes sin copiar su contenido ni reinterpretar
  como pendientes las limitaciones históricas ya cerradas.
- Ejercitar el recorrido con material real del dueño cuando esté disponible; conservar el origen.
  Mientras falte, informar que la prueba fue con ejemplos construidos.
- Completar tutorial breve y manual derivado, verificar wheel desde un cwd ajeno al checkout.
- Ejecutar la secuencia de verificación de `RELEVO-PARA-CODEX.md`, leyendo también las correcciones
  de `RELEVO-2026-09-10.md` y la evidencia del corte 0.15.0. Registrar comandos, resultados y alcance.
- Medir por mutación los tramos de código cambiados que custodien afirmaciones; no editar durante
  las rondas, no contar timeouts como muertos ni bajar umbrales para cerrar.

Salida de 0.16.0: P0–P4 verificados y revisados. Propuesta de distribución 0.16.0 con álgebra 0.6
y sintaxis 0.4, si el cambio final respeta ese límite. La publicación y el cambio de versión se
preparan al terminar la implementación; este roadmap no declara un release realizado.

## Fuera de esta entrega

UI web, tablero Kanban, sincronización con GitHub Issues, importación masiva de carpetas,
descargas de YouTube, búsqueda semántica y un lenguaje nuevo de consultas como TQL.
Se reconsideran cuando un uso concreto muestre que filtros, Markdown y enlaces no alcanzan.

## Seguimiento de la delegación

Codex coordina el roadmap y revisa la entrega. Agy implementa P0–P1 primero, con propiedad de los
archivos de runtime y tests necesarios. El encargo especifica restricciones y entrega esperada.
Su avance debe quedar en `vault-kb/estudios/0.16.0-tareas/AVANCE-AGY.md`; el resultado y comandos de
verificación, en `vault-kb/estudios/0.16.0-tareas/INFORME-AGY.md`. Ambos fueron recibidos y revisados.
Agy participó además en una revisión final de sólo lectura de P0–P1. Esas sesiones finalizaron.
El dueño autorizó continuar P2: la misma conversación se retomó con un encargo nuevo de
implementación, registrado en `ENCARGO-P2-AGY.md` y `AVANCE-P2-AGY.md`.
P2 fue recibido, corregido y verificado. Sus sesiones finalizaron.
P3 se inició por pedido del dueño con `ENCARGO-P3-AGY.md`; la conversación se retomó para
implementar el extractor y luego corregir las reproducciones independientes de Codex.
P3 fue recibido, corregido y verificado. Ambas sesiones finalizaron con código 0; no queda agy
trabajando en segundo plano. P4 también terminó; su cierre registra las sesiones adicionales
de agy, las correcciones, la mutación y la propuesta de versión pendiente de aplicar.
