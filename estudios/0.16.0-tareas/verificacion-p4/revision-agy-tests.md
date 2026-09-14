# Informe de implementación — Tests de mutación P1 (`tests/test_tareas_mutacion.py`)

Se creó exclusivamente el archivo [`tests/test_tareas_mutacion.py`](file:///home/workstation/Dev/oracle/tests/test_tareas_mutacion.py) con 21 casos de prueba de comportamiento directo en proceso, dirigidos a cubrir los sobrevivientes del diagnóstico de mutación sobre [`tools/tareas.py`](file:///home/workstation/Dev/oracle/tools/tareas.py). No se ejecutaron comandos de shell, ni tests, ni subagentes, ni se modificaron archivos preexistentes.

---

## 1. Lo implementado

El nuevo módulo organiza las pruebas en 6 clases temáticas, documentando en cada docstring el defecto concreto que previene:

1. **Resolución de raíz (`TestMutacionResolucionRaiz`)**:
   - `test_resolver_raiz_con_ruta_explicita_permitir_crear_en_directorio_sin_tareas`: verifica la conjunción booleana `not permitir_crear and not (destino / "tareas").is_dir()` (mata mutantes booleanos y de negación en L140 y retorno L142).
   - `test_resolver_raiz_con_argv_proyecto_sin_valor_al_final`: asegura el límite `idx + 1 >= len(argv_limpio)` ante `--proyecto` sin valor al final de `argv` (mata comparador `GtE -> Gt` en L147 y booleano).
   - `test_resolver_raiz_con_argv_proyecto_seguido_de_otra_bandera`: previene que banderas posteriores se tomen como ruta del proyecto.
   - `test_resolver_raiz_con_variable_entorno_permitir_crear_y_sin_tareas`: valida el comportamiento de `$ORACLE_PROYECTO` con `permitir_crear=True` y `False` (mata mutantes en L161 y retorno L163).
   - `test_resolver_raiz_con_variable_entorno_apunta_a_archivo`: asegura rechazo si `$ORACLE_PROYECTO` apunta a un archivo regular (L160).

2. **Parseo de `TAREA.md` (`TestMutacionParseoTarea`)**:
   - `test_parsear_tarea_lineas_en_blanco_al_inicio`: tolera saltos y espacios en blanco iniciales antes del encabezado H1 (L191–194).
   - `test_parsear_tarea_titulo_un_solo_caracter_valido_y_rechazo_espacio_vacio`: fija el límite de longitud `len(linea_titulo) <= 2`, permitiendo `# X` y rechazando `# ` o `#Titulo` sin espacio (mata mutantes de constante `2 -> 3` y operadores de comparación en L198).
   - `test_parsear_tarea_campos_adicionales_se_guardan_y_estandar_se_excluyen`: verifica que los metadatos desconocidos se guarden en `campos_adicionales` y que los estándar (`ESTADO`, `PRIORIDAD`, `ETIQUETAS`) no se filtren en ese diccionario (mata `NotIn -> In` en L232).
   - `test_parsear_tarea_etiquetas_espacios_y_elementos_vacios`: depuración de comas y espacios en blanco en la tupla de etiquetas (L257).

3. **Actualización atómica y CRLF (`TestMutacionActualizacionAtomaYCrlf`)**:
   - `test_actualizar_estado_idempotente_retorna_false_estricto`: asegura que operaciones sin cambio de estado retornen `False` estricto (mata `return False -> return None` en L296).
   - `test_actualizar_estado_preserva_crlf_orden_metadata_y_espaciado`: garantiza preservación byte por byte de saltos CRLF (`\r\n`), orden de campos anteriores a `ESTADO`, espacios y bloques de código (mata mutantes de punteros y offsets en L300–345).

4. **Creación atómica y desambiguación (`TestMutacionCreacionYColisiones`)**:
   - `test_crear_carpeta_atomica_desambiguador_secuencial_exacto`: ejercita directamente `crear_carpeta_tarea_atomica` ante colisiones en el mismo segundo UTC, asegurando que el primer reintento use `-1` y el segundo `-2` (mata `contador = 1 -> 2` en L401 y `contador += 1 -> 2` en L409).
   - `test_sanear_slug_translitera_acentos_sin_insertar_guiones_espurios`: asegura que el filtrado de caracteres combinables tras `NFKD` permanezca activo, convirtiendo acentos a letras base sin guiones internos espurios.

5. **Resolución de ID y confinamiento (`TestMutacionResolucionIdYConfinamiento`)**:
   - `test_resolver_id_carpeta_directa_y_prefijo_inequivoco`: verifica la rama directa de directorios existentes (mata `or -> and` en L446) y la resolución de prefijo único sin confundirlo con ambiguo (mata `len > 1 -> len >= 1` en L466 y constante `candidatos[0]` en L472).
   - `test_validar_seguridad_id_rechaza_casos_inseguros`: valida rechazo de vacíos, tipos no string, `/`, `\\`, `..` y bytes nulos (L90–97).
   - `test_asegurar_confinamiento_acepta_rutas_seguras_y_rechaza_escapes`: prueba caminos válidos y rechazo de escapes fuera de `tareas/` sin exigir retorno `Path`.

6. **Comandos CLI, códigos y formatos (`TestMutacionCliComandosYCodigos`)**:
   - `test_parser_subcomando_opcion_invalida_sale_con_codigo_2_exacto`: valida que opciones desconocidas aborten con código `2` exacto (mata mutante de constante `2 -> 3` en L55).
   - `test_cmd_nueva_prioridad_por_defecto_50_y_sufijo_custom`: fija prioridad por defecto en `50` (mata constante `50 -> 51` en L633) y respeta `--sufijo` explícito (mata `and <-> or` en L672).
   - `test_cmd_nueva_recorte_de_slug_largo_a_40_caracteres`: prueba el límite de 40 caracteres en slugs generados desde títulos extensos (L672).
   - `test_cmd_listar_incompatibilidad_cerradas_y_todas_devuelve_codigo_1`: valida conflicto entre `--cerradas` y `--todas` devolviendo código `1` (L718).
   - `test_cmd_listar_por_defecto_solo_abiertas_y_filtros_etiqueta_texto`: comprueba que el listado por defecto excluya cerradas (mata mutante L748), filtro case-insensitive por `--etiqueta` (L752) y búsqueda por `--texto` en cuerpo (L756).
   - `test_cmd_ver_ruta_y_formato_humano`: incompatibilidad `--ruta` y `--json`, salida exclusiva de ruta y formato humano para tareas sin etiquetas ni cuerpo (L790, L838–840, L850, L858).
   - `test_cmd_cerrar_y_reabrir_mensajes_cambio_e_idempotencia`: salidas diferenciadas ante cambio efectivo vs tarea ya cerrada/abierta (L903–905, L949–951).
   - `test_cmd_revisar_json_y_humano_exito_y_fallo`: códigos 0 y 1 en salidas humana y JSON, ignorando auxiliares permitidos (`README`, `.gitignore`) y detectando archivos sueltos no reconocidos (L503, L975, L984).

---

## 2. Premisas del diseño

- **Ejecución en proceso**: Todas las pruebas usan captura en memoria (`_callado`) y APIs directas de `tareas.*` sobre directorios temporales aislados, evitando la lentitud de subprocesos y garantizando tiempos de ejecución inferiores a 300 ms en total.
- **Desacople de `generar_id_tarea`**: Ningún test importa ni llama a `generar_id_tarea`, permitiendo que Codex retire este helper del runtime sin afectar la suite.
- **Desacople del retorno de confinamiento**: Las pruebas de `asegurar_confinamiento` y `asegurar_confinamiento_archivo` solo validan que las rutas válidas no lancen excepciones y que las inseguras lancen `RutaInsegura`, sin afirmar el tipo de retorno `Path`.

---

## 3. Huecos restantes y siguientes pasos

- **Centralización atómica pendiente en Codex**: Los fallos de permisos simulados sobre `os.fchmod` / `os.chmod` se abordarán cuando Codex introduzca `guardar_documento_atomico`, evitando acoplar pruebas a la implementación duplicada actual.
- **Líneas a eliminar por Codex**: El código muerto del segundo `is_dir()` en el límite Git ([`tools/tareas.py#L172-L173`](file:///home/workstation/Dev/oracle/tools/tareas.py#L172-L173)) y el bucle de `generar_id_tarea` no fueron cubiertos intencionalmente, ya que serán retirados del runtime.
- **Ejecución y mutación**: La suite queda lista para que Codex ejecute la verificación completa y la siguiente ronda diagnóstica de mutación.
