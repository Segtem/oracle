# Informe agy — Entrega P2 (Oracle 0.16.0: captura y consultas de contexto)

Nota de Codex: entrega de agy revisada posteriormente; el resultado verificado y las correcciones finales figuran en `CIERRE-P2.md`. Este informe conserva la autoría de la implementación inicial.

Fecha: 2026-09-12  
Responsable: agy  
Rama/Workspace: `/home/workstation/Dev/oracle`  
Base: distribución 0.15.0 (sin cambio de versión en código)  
Destinatario: Codex / Equipo de Oracle  

---

## 1. Resumen ejecutivo

Se completó la implementación y el endurecimiento del tramo **P2** del subsistema de tareas de Oracle según las especificaciones de `vault-kb/estudios/0.16.0-tareas/ENCARGO-P2-AGY.md`, `vault-kb/planes/PLAN-0.16.0-TAREAS.md` y las observaciones de `vault-kb/estudios/0.16.0-tareas/REVISION-P2-CODEX.md`.

Este tramo dota al tracker de tareas de capacidades para capturar contexto (apuntes, URLs técnicas con marcas temporales y adjuntos locales de cualquier tipo) y recuperar información operativa mediante consultas especializadas (búsqueda literal en tareas y notas, rastreo de referencias cruzadas en el código fuente del proyecto y resúmenes estadísticos agregados).

En estricta observancia del modo de operación acordado:
- No se ejecutaron comandos de shell ni corridas de tests desde agy (la ejecución y validación de pruebas queda reservada a la coordinación de Codex).
- No se modificaron versiones (`nucleo/version.py` permanece en `0.15.0`).
- No se realizaron commits ni operaciones de red.
- Se respetaron los archivos de propiedad exclusiva de Codex (`tools/tareas_git.py`, `tests/test_tareas_git.py`, `tests/test_tareas_p2_revision.py`, `tools/verificar_instalacion.py` y suites previas P0/P1).

---

## 2. Conducta implementada y arquitectura

La lógica de contexto se estructuró en el módulo `tools/tareas_contexto.py`, reutilizando las funciones de resolución, confinamiento y auditoría de `tools/tareas.py` para reutilizar el contrato de P0 y P1.

### 2.1. `oracle tarea anotar`
- **Contrato y validación**:
  - Exige la presencia de texto explicativo o de una `--url`.
  - Preserva **exactamente** la sangría y los espacios significativos del texto sin aplicar `strip()`.
  - Si se pasa `--url`, se valida de forma estricta que sea absoluta con esquema `http` o `https`, y que no contenga espacios ni caracteres de control (`validar_url_estricta`).
  - La URL se conserva idéntica a la provista, preservando parámetros de consulta sensibles como `?t=01m30s` o anclas sin re-escapar ni normalizar.
  - La opción `--marca` (posición aportada por el usuario, ej. `01:32`) exige la presencia obligatoria de `--url` y conserva su texto exacto.
- **Preservación y atomismo**:
  - Se añade una entrada de nota al cuerpo libre de `TAREA.md` con timestamp UTC de captura (`YYYY-MM-DD HH:MM:SS UTC`).
  - Se preservan todos los bytes existentes del documento (encabezados, sangrías, viñetas, comentarios, cuerpo y estilo CRLF/LF).
  - Se conservan los permisos POSIX del archivo (`st_mode & 0o777`).
  - La creación y escritura del archivo temporal contiguo captura de forma segura cualquier `OSError` en la frontera pública, evitando tracebacks no controlados y saliendo con código 1. Reemplazo atómico con `os.replace`. No realiza descargas remotas ni llamadas de red.

### 2.2. `oracle tarea adjuntar`
- **Contrato y seguridad de archivos**:
  - Acepta exclusivamente archivos regulares existentes.
  - Rechaza enlaces simbólicos de origen, directorios o archivos especiales (dispositivos, FIFOs, sockets).
  - Conserva intacto el archivo original en su ubicación fuente.
  - Preserva nombres con espacios y caracteres Unicode al guardarlos en la carpeta de la tarea (`tareas/<id>/<nombre>`).
  - Rechaza explícitamente nombres con saltos de línea (`\n`, `\r`) o caracteres de control ASCII (`< 32`) antes de iniciar cualquier copia, evitando corromper enlaces Markdown.
  - Rechaza colisiones si el archivo de destino ya existe en la carpeta (incluyendo enlaces rotos).
  - Rechaza cualquier intento de sobreescribir el documento central `TAREA.md` (insensible a mayúsculas/minúsculas).
- **Control de volumen acumulado**:
  - Límite predeterminado de 20 MiB por archivo. El tamaño se fiscaliza tanto en la inspección inicial como **acumulativamente bloque a bloque** durante la copia (en bloques de 64 KiB). Si el archivo fuente crece durante la copia superando los 20 MiB sin `--permitir-grande`, se cancela inmediatamente la operación, se revierte la copia parcial y se sale con código 1.
- **Copia segura y enlace relativo**:
  - Copia por bloques con creación exclusiva (`os.O_CREAT | os.O_EXCL`).
  - Genera y registra en `TAREA.md` un enlace relativo Markdown con la URL de destino debidamente escapada (`%20` para espacios, `%28`/`%29` para paréntesis, `%23` para numerales) y la etiqueta visible protegida escapando barras invertidas (`\\`) **antes** que corchetes (`\[`, `\]`).
  - **Reversión ante fallo detectado**: se intenta eliminar únicamente la copia creada. La copia y el registro no son una transacción entre archivos: una interrupción del proceso puede dejar un adjunto sin registrar.
  - Salida JSON: emite objeto con `id`, `ruta` (ruta absoluta al adjunto) y `documento` (ruta absoluta a `TAREA.md`).

### 2.3. `oracle tarea buscar`
- **Contrato de búsqueda literal y seguridad**:
  - Búsqueda literal e insensible a mayúsculas/minúsculas dentro de `tareas/`.
  - Recorre de manera recursiva la carpeta de cada tarea, encontrando notas en subdirectorios internos sin seguir enlaces simbólicos ni descender en repositorios anidados.
  - Comprueba que cada archivo sea un archivo regular (`stat.S_ISREG`) antes de abrirlo, y abre con banderas `O_RDONLY | O_NONBLOCK` para prevenir que FIFOs o dispositivos especiales bloqueen la ejecución del proceso. Los archivos especiales se omiten con motivo descriptivo.
  - Clasificación unificada de archivos de texto acotada (`leer_archivo_texto_si_aplica`) con lectura de `LIMITE_BUSQUEDA_BYTES + 1` (2 MiB).
  - Aplica la lista `EXTENSIONES_TEXTO_ADMITIDAS` (incorporando `.oracle` explícitamente y soportando archivos de texto sin extensión que decodifiquen UTF-8 sin bytes nulos).
  - Omite enlaces simbólicos y archivos binarios reconocidos por extensión o presencia de bytes nulos.
  - Informa los archivos omitidos con su motivo tanto en `--json` como en la salida humana por consola (incluso cuando hay cero coincidencias encontradas).
  - Fallos operacionales reales de lectura o acceso emiten diagnóstico y devuelven código 1; no se transforman en omisiones exitosas ni se enmascaran como búsquedas vacías.
  - Cero coincidencias con tracker válido devuelve código 0. Si existen tareas rotas o registros corruptos en `tareas/`, la operación falla con código 1.

### 2.4. `oracle tarea referencias`
- **Rastreo de menciones sin ambigüedad**:
  - Audita previamente `tareas/` mediante `auditar_tareas`, fallando con código 1 ante cualquier registro corrupto antes de proceder.
  - Resuelve el ID canónico de la tarea.
  - Busca menciones del ID exacto en tareas, notas y código fuente bajo la raíz del proyecto.
  - Utiliza límites estrictos de palabra/identificador (`(?<![a-zA-Z0-9_-])ID(?![a-zA-Z0-9_-])`) para no atribuir menciones de tareas derivadas (como `ID-1` o `copia-ID`) a la tarea base.
  - Excluye directorios ignorados: `.git`, `.hg`, `.svn`, `.venv`, `venv`, `node_modules`, `__pycache__`, `build`, `dist`.
  - No atraviesa enlaces simbólicos ni desciende en repositorios Git anidados.
  - Utiliza manejador `onerror` en `os.walk` para detectar y reportar fallos de E/S con código 1 en lugar de silenciarlos.
  - Salida JSON y humana: incluye `id`, `tipo: "mencion_textual"`, `coincidencias` y lista de `omitidos` con su motivo.
  - Claridad de contrato: las menciones encontradas representan contexto histórico, no dependencias formales declaradas ni arcos dirigidos de grafos.

### 2.5. `oracle tarea resumen`
- **Agregación y censo**:
  - Audita el tracker y computa el total de tareas, cantidades por estado (`ABIERTA`, `CERRADA`) y desglose por etiquetas.
  - Conserva exactamente las mayúsculas y minúsculas de las etiquetas originales (alineado con `oracle tarea listar --etiqueta`, que filtra por coincidencia exacta).
  - Deduplica únicamente identidades de etiquetas repetidas dentro de la misma tarea.
  - Ordena las etiquetas alfabéticamente de forma determinista.
  - No genera cachés en disco. Falla con código 1 si hay tareas corruptas. En un tracker vacío devuelve total 0 con código 0.

### 2.6. Integración del verbo `seguimiento`
- En `tools/tareas.py`, la función `despachar` incluye el caso `verbo == "seguimiento"`, delegando mediante import local diferido a `tools.tareas_git.cmd_seguimiento(argv, args)` provisto por Codex.
- Se registró el verbo en `VERBOS["tarea"]` en `tools/cli.py` y se actualizó la ayuda general del CLI.

---

## 3. Resoluciones de revisión (`REVISION-P2-CODEX.md`)

A continuación se detalla cómo se abordaron todos los puntos reproducidos y sugerencias de código reportados por Codex:

1. **Bloqueo en FIFOs y archivos especiales en `buscar`**:
   - Se implementó en `leer_archivo_texto_si_aplica` la verificación previa `stat.S_ISREG(st.st_mode)` y apertura con `os.O_NONBLOCK`. Un FIFO nombrado no bloquea el arnés: se registra inmediatamente en `omitidos` como `"archivo especial (FIFO/dispositivo/socket)"`. Los fallos operacionales de lectura devuelven error con código 1.
2. **`referencias` ante `TAREA.md` corrupto**:
   - Se incorporó la invocación a `auditar_tareas(raiz_tareas)` al inicio de `cmd_referencias`. Si hay registros corruptos, devuelve código 1 inmediatamente, idéntico a `buscar` y `resumen`.
3. **Preservación de sangría y espacios en `anotar`**:
   - Se eliminó el `strip()` del texto de la nota y de la `--marca`. Se preservan indentaciones de código y espacios intencionales, validando únicamente que el texto no esté compuesto puramente de espacios en blanco si se provee.
4. **Corrección en suite de tests de agy**:
   - Se importó `shutil` en `tests/test_tareas_contexto.py`.
   - Se corrigió `test_opciones_desconocidas_devuelven_codigo_2` aportando los argumentos posicionales requeridos por cada subcomando, de modo que `argparse` evalúe efectivamente el rechazo a opciones desconocidas con código 2 y no por falta de posicionales obligatorios.
5. **Lectura unificada y acotada con `EXTENSIONES_TEXTO_ADMITIDAS`**:
   - `_es_archivo_de_texto` fue reemplazada por `leer_archivo_texto_si_aplica`, que realiza una única lectura acotada de `LIMITE_BUSQUEDA_BYTES + 1` (2 MiB), verifica bytes nulos, UTF-8 y extensiones admitidas (incluyendo `.oracle` y archivos sin extensión).
6. **Búsqueda recursiva en subcarpetas de la tarea**:
   - `cmd_buscar` ahora recorre recursivamente todos los subdirectorios bajo cada carpeta de tarea, omitiendo symlinks y repositorios anidados con reporte explícito.
7. **Reporte de omisiones en salida humana**:
   - Tanto `buscar` como `referencias` muestran el bloque `Archivos omitidos:` en texto plano cuando existen omisiones, incluso ante cero coincidencias.
8. **Manejo de errores en `os.walk` en `referencias`**:
   - Se definió la función `on_walk_error` pasada al parámetro `onerror` de `os.walk`, reportando diagnósticos y devolviendo código 1 ante fallos de recorrido.
9. **Frontera pública para `OSError` en creación de temporales en `anotar`**:
   - Se encapsuló la llamada a `NamedTemporaryFile` dentro del bloque `try...except OSError` reportando diagnóstico claro con código 1 sin propagar tracebacks.
10. **Control de tamaño acumulado durante copia de adjuntos**:
    - `cmd_adjuntar` fiscaliza el total acumulado en cada iteración del bucle de copia de 64 KiB. Si el archivo fuente crece durante la copia superando 20 MiB sin `--permitir-grande`, se aborta inmediatamente, se elimina el archivo parcial en destino y se retorna 1.
11. **Escape seguro y rechazo de saltos de línea en adjuntos**:
    - En la generación del enlace Markdown, se escapan las barras invertidas (`\\`) antes de los corchetes (`\[`, `\]`). Además, se rechazan explícitamente nombres de archivo que contengan saltos de línea (`\n`, `\r`) o caracteres de control ASCII.
12. **Conservación de mayúsculas/minúsculas en etiquetas de `resumen`**:
    - Se eliminó la conversión a minúsculas en `cmd_resumen`. Se preserva la caja original y se deduplican etiquetas idénticas por tarea, garantizando total coherencia con el filtro exacto de `listar --etiqueta`.

---

## 4. Inventario de archivos asignados a agy

| Archivo | Estado | Descripción del cambio |
|---|---|---|
| `tools/tareas_contexto.py` | Creado y endurecido | Módulo principal de contexto P2: `cmd_anotar`, `cmd_adjuntar`, `cmd_buscar`, `cmd_referencias` y `cmd_resumen`. |
| `tools/tareas.py` | Modificado | Incorporación de los 5 verbos P2 y delegación diferida de `seguimiento` en `despachar()` y `ayuda()`. |
| `tools/cli.py` | Modificado | Declaración de `anotar`, `adjuntar`, `buscar`, `referencias`, `resumen` y `seguimiento` en `VERBOS["tarea"]` y en la ayuda del sustantivo. |
| `docs/12-tareas.md` | Modificado | Especificación técnica formal de los comandos P2, reglas de URLs, copias y omisiones, y tutorial práctico paso a paso. |
| `tests/test_tareas_contexto.py` | Creado y ampliado | Suite con 28 pruebas de comportamiento que cubren los nuevos comandos vía CLI público en temporales. |
| `vault-kb/estudios/0.16.0-tareas/AVANCE-P2-AGY.md` | Modificado | Bitácora viva de seguimiento de P2 actualizada con la confirmación de recepción y checklist completo. |
| `vault-kb/estudios/0.16.0-tareas/INFORME-P2-AGY.md` | Actualizado | Este informe de entrega. |

---

## 5. Detalle de cobertura de la suite `test_tareas_contexto.py`

Se estructuraron **28 tests de comportamiento** distribuidos en 6 clases de caso de prueba sobre el CLI público en proyectos temporales:

1. **`TestAnotar` (6 tests)**:
   - `test_anotar_agrega_texto_y_preserva_cuerpo_y_permisos`: verificación de fecha UTC, preservación del cuerpo H1 y conservación de modo POSIX 0640.
   - `test_anotar_preserva_sangria_y_espacios_significativos`: conservación intacta de indentación de código sin aplicar `strip()`.
   - `test_anotar_con_url_y_marca_exactas`: conservación de query string `?t=42s`, marca `01:32` y estructura JSON.
   - `test_anotar_rechaza_sin_texto_ni_url`: falla con código 1 si no se provee texto ni URL.
   - `test_anotar_marca_sin_url_se_rechaza`: rechazo con código 1 de marca temporal huérfana sin URL.
   - `test_anotar_url_invalida_o_con_espacios_se_rechaza`: rechazo de esquemas no http/https, URLs relativas y saltos de línea.
2. **`TestAdjuntar` (8 tests)**:
   - `test_adjuntar_copia_exacta_y_preserva_original`: verificación de bytes idénticos, original intacto y enlace relativo en `TAREA.md`.
   - `test_adjuntar_con_espacios_y_caracteres_unicode`: nombres complejos con acentos, corchetes, paréntesis y numerales, con URL escapada en Markdown.
   - `test_adjuntar_escapa_barras_invertidas_antes_que_corchetes`: verificación de orden de escape en la etiqueta visible Markdown.
   - `test_adjuntar_rechaza_nombre_con_saltos_de_linea`: rechazo explícito de nombres de archivo con `\n` antes de copiar.
   - `test_adjuntar_rechaza_enlace_simbolico_de_origen`: prohibición estricta de adjuntar symlinks.
   - `test_adjuntar_rechaza_colision_con_archivo_existente`: rechazo de sobreescritura si el destino ya existe en la carpeta.
   - `test_adjuntar_rechaza_nombre_tarea_md`: protección del nombre reservado `TAREA.md`.
   - `test_adjuntar_limite_20mib_sin_bandera_y_permite_con_ella`: falla ante archivos > 20 MiB y aprobación explícita con `--permitir-grande`.
3. **`TestBuscar` (5 tests)**:
   - `test_buscar_encuentra_coincidencias_en_subcarpetas_de_la_tarea`: localización recursiva en notas y documentos dentro de subdirectorios.
   - `test_buscar_omite_fifo_sin_bloquearse`: verificación de que un FIFO no bloquea el proceso y se reporta en omitidos.
   - `test_buscar_omite_binarios_con_diagnostico_en_json`: exclusión de archivos binarios (`.png`) reportada en `omitidos`.
   - `test_buscar_humano_muestra_omitidos_con_cero_coincidencias`: presentación de archivos omitidos en consola humana incluso sin coincidencias.
   - `test_buscar_falla_si_hay_registros_invalidos`: código 1 ante carpetas o documentos corruptos en el tracker.
4. **`TestReferencias` (4 tests)**:
   - `test_referencias_encuentra_menciones_en_codigo_del_proyecto`: detección de ID en código fuente dentro del proyecto.
   - `test_referencias_falla_si_hay_registros_invalidos`: auditoría previa falla con código 1 si el tracker está corrupto.
   - `test_referencias_no_confunde_id_con_sufijos`: límites estrictos de regex impiden confundir `ID` con `ID-1`.
   - `test_referencias_ignora_directorios_excluidos`: exclusión estricta de `.git` y otros directorios del sistema.
5. **`TestResumen` (3 tests)**:
   - `test_resumen_calcula_totales_estados_y_conserva_mayusculas_de_etiquetas`: cómputo exacto conservando mayúsculas/minúsculas y deduplicando por tarea.
   - `test_resumen_vacio_devuelve_cero`: total 0 con código 0 en tracker sin tareas.
   - `test_resumen_falla_si_hay_registros_invalidos`: código 1 si hay registros mal formados.
6. **`TestComportamientoGlobalP2` (2 tests)**:
   - `test_ayudas_de_cada_verbo_no_escriben`: `--help` en los 5 verbos devuelve 0 sin crear `tareas/` ni tocar disco.
   - `test_opciones_desconocidas_devuelven_codigo_2`: banderas no reconocidas devuelven código 2 de `argparse` al aportar posicionales requeridos.

---

## 6. Declaración de límites y estado de ejecución

- **Ejecución de pruebas**: En cumplimiento de las directivas del encargo, agy no ejecutó tests unitarios, comandos shell ni arneses de mutación. La verificación en runtime y ejecución de la suite completa queda delegada a la coordinación de Codex.
- **Límites conocidos**:
  - Las referencias encontradas por `referencias` son puramente textuales y orientativas; no constituyen un grafo de dependencias formales ni validan la completitud del trabajo.
  - La operación `adjuntar` copia los archivos localmente en el directorio de la tarea; no interactúa con servidores remotos ni repositorios externos.
  - El diagnóstico de control de versiones y estado del índice corresponde al comando `seguimiento` (`tools/tareas_git.py`), desarrollado por Codex.
