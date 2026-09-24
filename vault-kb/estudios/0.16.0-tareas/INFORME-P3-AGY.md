# Informe agy — Entrega P3 (Oracle 0.16.0: evidencia del tracker propio)

Nota de cierre de Codex (2026-09-12): tras esta entrega se completaron las correcciones de rutas
absolutas con `..`, directorios simbólicos y ayuda general. La verificación final pasó 1679 tests,
52/52 mutantes de las políticas nuevas y el recorrido instalado. Ver [CIERRE-P3.md](CIERRE-P3.md)
para el resultado integrado y sus límites. El resto de este archivo conserva el informe de agy.

Fecha: 2026-09-12  
Responsable: agy  
Rama/Workspace: `/home/workstation/Dev/oracle`  
Base: distribución 0.15.0 (sin cambio de versión en código)  
Destinatario: Codex / Equipo de Oracle  

---

## 1. Resumen ejecutivo

Se completó la implementación y el endurecimiento del tramo **P3** del subsistema de tareas de Oracle según las especificaciones de `vault-kb/estudios/0.16.0-tareas/ENCARGO-P3-AGY.md`, `vault-kb/planes/PLAN-0.16.0-TAREAS.md` y las observaciones de revisión de `vault-kb/estudios/0.16.0-tareas/REVISION-P3-CODEX.md`.

Este tramo implementa el extractor explícito de hechos relacionales (`oracle tarea hechos`), el cual inspecciona el árbol de tareas local y emite un objeto JSON estructurado directamente a `stdout`. Este formato es consumido por el evaluador de políticas de Oracle (`ejemplo/seguimiento-tareas/evaluar.py --con ARCHIVO.json`), desarrollado por Codex y basado en `Medida.evaluar`.

En estricta observancia del modo de operación acordado:
- No se ejecutaron comandos de shell ni corridas de tests desde agy (la ejecución de pruebas y validación en runtime queda delegada a la coordinación de Codex).
- No se modificaron versiones (`nucleo/version.py` permanece en `0.15.0`).
- No se realizaron commits ni operaciones de red.
- Se respetaron los archivos de propiedad exclusiva de Codex (`ejemplo/seguimiento-tareas/`, `tests/test_tareas_p3_revision.py`, `tools/verificar_instalacion.py` y suites previas).

---

## 2. Resoluciones de revisión (`REVISION-P3-CODEX.md`)

A continuación se detalla cómo se abordaron todos los puntos reproducidos y sugerencias de código reportados por Codex:

1. **Definiciones reales de enlace en fixture y parser**:
   - Se corrigió el fixture en `tests/test_tareas_hechos.py` para usar definiciones Markdown reales al inicio de línea (`[clave1]: destino.txt`).
   - El parser `tools/tareas_hechos.py` reconoce definiciones con o sin espacios tras colon (`[clave]:destino` y `[clave]: destino`), registrando la omisión correspondiente (`"definición de enlace por referencia no resuelta: [clave]: ..."`).
2. **Conservación de una fila por aparición**:
   - Se eliminó el colapso por `(ruta, linea, destino)`. Cada enlace inline que aparece en una línea genera una fila independiente en `referencia_seguimiento`.
   - Se utilizan intervalos de caracteres (`spans_cubiertos`) para evitar que autolinks o URLs queden duplicados dentro de la misma aparición de un enlace inline.
3. **Sintaxis multilínea e incompleta**:
   - Enlaces partidos como `[nota](\nausente.txt)` o corchetes que no cierran en la línea ya no desaparecen con `completa=true`. Se detecta la condición y se genera una omisión explícita (`"sintaxis de enlace incompleta o multilínea no admitida"`), marcando `completa=false`.
4. **Esquemas case-insensitive**:
   - URLs con esquemas en mayúsculas (como `HTTPS://...` o autolinks `<HTTPS://...>`) se clasifican correctamente como clase `remota` con estado `no_comprobado`, conservando intacto el texto exacto declarado en `destino_declarado`.
5. **Cierre estricto de bloques cercados**:
   - Se ajustó el reconocedor de cierre de cercas (```` ``` ```` o `~~~`) para exigir exclusivamente espacios opcionales tras la cerca (`^[ \t]{0,3}(`{3,}|~{3,})[ \t]*$`). Una línea como ```` ```no-es-cierre ```` ya no cierra el bloque de código.
6. **Inspección segura de componentes con `..` y symlinks**:
   - Se reemplazó la normalización anticipada por un recorrido componente a componente sobre las partes originales sin llamar a `resolve()`.
   - En rutas como `puente/../parece-local.txt`, si `puente` es un enlace simbólico, la inspección detecta el symlink en ese componente y clasifica la referencia como `no_comprobado`, emitiendo una omisión en `omision_seguimiento`.
   - Si un componente intermedio es un archivo regular seguido de `/..`, se reconoce que no es un directorio válido y se clasifica como `ausente`.
7. **Manejo estricto de errores de E/S y permisos**:
   - Se implementó `_lstat_seguro()`: únicamente `FileNotFoundError` y `NotADirectoryError` indican ausencia física.
   - Cualquier otro `OSError` (como `PermissionError` por `chmod 000` o fallos de E/S) se propaga como `TareaError` y hace que el CLI aborte con código 1, sin emitir JSON parcial ni convertir errores de permisos en falsas ausencias.
8. **Prechequeo acotado de `TAREA.md` centrales**:
   - `_prechequear_documentos_centrales()` inspecciona los documentos `TAREA.md` centrales antes de invocar `auditar_tareas()`. Si algún `TAREA.md` central es un enlace simbólico o supera los 2 MiB, el comando falla con código 1 inmediatamente.
   - Por el contrario, los adjuntos Markdown grandes (> 2 MiB) se omiten en `omision_seguimiento` con `completa=false` sin abortar la ejecución.
9. **Corrección del consumidor de hechos en integración**:
   - Se corrigió la documentación y el informe para aclarar que `oracle tarea hechos` emite a `stdout` y su consumidor es `ejemplo/seguimiento-tareas/evaluar.py --con ARCHIVO.json`.
10. **Literales escapados y límites de gramática**:
    - Se verifica si los corchetes están escapados (`_esta_escapado()`), evitando que `\[texto](destino)` sea interpretado como enlace.
    - Se documentaron formalmente los límites reales de la gramática Markdown soportada.

---

## 3. Inventario de archivos

| Archivo | Estado | Descripción del cambio |
|---|---|---|
| `tools/tareas_hechos.py` | Creado y endurecido | Módulo principal extractor de hechos: `extraer_hechos()` y subcomando `cmd_hechos()`. |
| `tools/tareas.py` | Modificado | Incorporación del verbo `hechos` en `despachar()` con import local diferido y actualización de `ayuda()`. |
| `tools/cli.py` | Modificado | Declaración de `hechos` en la tupla `VERBOS["tarea"]`. |
| `docs/12-tareas.md` | Modificado | Especificación formal de hechos P3, distinciones de centrales/adjuntos, semántica de rutas y consumidor `evaluar.py`. |
| `tests/test_tareas_hechos.py` | Creado y ampliado | Suite con 24 pruebas de comportamiento del CLI sobre proyectos temporales. |
| `vault-kb/estudios/0.16.0-tareas/AVANCE-P3-AGY.md` | Actualizado | Bitácora viva de seguimiento del tramo P3 con resoluciones de revisión completas. |
| `vault-kb/estudios/0.16.0-tareas/INFORME-P3-AGY.md` | Actualizado | Este informe de entrega. |

---

## 4. Detalle de cobertura de la suite `test_tareas_hechos.py`

Se estructuraron **24 tests de comportamiento** divididos en 5 clases de prueba sobre el CLI público:

1. **`TestHechosEsquemaYDeterminismo` (2 tests)**:
   - `test_hechos_esquema_y_cinco_claves_siempre_presentes`: verifica presencia de las 5 claves relacionales y estructura de `lectura_seguimiento`.
   - `test_hechos_determinismo_byte_por_byte`: verifica salida idéntica carácter por carácter entre corridas sucesivas sobre el mismo árbol.
2. **`TestHechosTareasYArchivos` (3 tests)**:
   - `test_hechos_datos_declarados_tarea`: valida extracción de metadatos declarados y hash SHA-256 de `TAREA.md`.
   - `test_hechos_inventario_archivos_y_auxiliares`: valida clasificación de `documento`, `adjunto` y `auxiliar` (`tareas/README.md`).
   - `test_hechos_no_lee_binarios_ni_se_bloquea_en_fifo`: comprueba que binarios sólo inspeccionen `stat` y FIFOs generen omisión sin bloquearse.
3. **`TestHechosReferenciasMarkdown` (11 tests)**:
   - `test_hechos_referencias_locales_presentes_y_rotas`: verifica clasificación `presente` vs `ausente` para adjuntos locales.
   - `test_hechos_multiples_apariciones_en_misma_linea`: comprueba que dos enlaces iguales en la misma línea generen dos filas en `referencia_seguimiento`.
   - `test_hechos_esquemas_mayusculas_y_autolinks`: verifica clasificación de esquemas `http`/`https` case-insensitive preservando texto original.
   - `test_hechos_sintaxis_multilinea_o_incompleta_genera_omision`: verifica que enlaces incompletos o partidos generen omisión con `completa=false`.
   - `test_hechos_corchetes_escapados_no_son_enlaces`: verifica que `\[texto](...)` sea tratado como literal y no como enlace.
   - `test_hechos_cerca_de_codigo_con_texto_no_cierra_bloque`: verifica que ```` ```no-es-cierre ```` no cierre el bloque cercado.
   - `test_hechos_referencia_puente_symlink_con_puntos_causa_omision`: comprueba que `puente/../archivo` a través de symlink dé `no_comprobado` con omisión.
   - `test_hechos_componente_archivo_con_puntos_es_ausente`: comprueba que navegar a través de un archivo regular con `..` dé `ausente`.
   - `test_hechos_referencias_escape_fuera_del_proyecto`: verifica que referencias que escapan de la raíz se marquen como `fuera_del_proyecto`.
   - `test_hechos_nombres_unicode_espacios_y_percent_encoding`: comprueba resolución de adjuntos con caracteres Unicode y percent-encoding.
   - `test_hechos_omisiones_sintaxis_no_soportada_y_esquemas_invalidos`: comprueba reporte de omisión ante `[texto][clave]`, definiciones y esquemas ajenos.
4. **`TestHechosLimitesYErrores` (6 tests)**:
   - `test_hechos_permiso_denegado_falla_con_codigo_1`: comprueba que directorios o archivos sin permisos de lectura aborten con código 1 sin dar falsa ausencia.
   - `test_hechos_tarea_md_central_grande_o_simbolico_falla_codigo_1`: comprueba que un `TAREA.md` central > 2 MiB o symlink aborte con código 1 en prechequeo.
   - `test_hechos_archivo_markdown_adjunto_grande_se_omite`: verifica que adjuntos Markdown > 2 MiB se omitan con `completa=false` sin abortar.
   - `test_hechos_metadata_corrupta_falla_con_codigo_1`: valida aborto con código 1 sin JSON parcial ante tareas corruptas.
   - `test_hechos_ayuda_no_escribe_en_disco`: verifica que `--help` devuelva 0 sin tocar disco.
   - `test_hechos_opcion_desconocida_devuelve_codigo_2`: valida rechazo con código 2 ante opciones desconocidas.
5. **`TestHechosIntegracionGit` (2 tests)**:
   - `test_hechos_git_sin_repositorio`: verifica reporte `sin_repositorio` y `git_comprobado=false` cuando no hay Git.
   - `test_hechos_git_con_repositorio_y_commits`: verifica reporte `comprobado`, hash de `HEAD` y banderas de índice/HEAD cuando Git está presente.

---

## 5. Declaración de límites y estado de entrega

- **Ejecución de pruebas**: En estricto cumplimiento de las directivas de la asignación, agy no ejecutó tests unitarios, comandos shell ni arneses de mutación. La verificación en runtime queda bajo la custodia de Codex.
- **Límites conocidos**:
  - La presencia de referencias locales comprueba la existencia física del archivo referenciado en el momento de la consulta, pero no valida su contenido ni autenticidad.
  - Los estados y prioridades en `tarea_seguimiento` reflejan exclusivamente lo declarado por los metadatos de las tareas, sin constituir verificación del trabajo realizado.
  - La opción `--git` efectúa una consulta de solo lectura sobre el estado del árbol respecto de Git; no garantiza la existencia de copias de seguridad en repositorios remotos.
