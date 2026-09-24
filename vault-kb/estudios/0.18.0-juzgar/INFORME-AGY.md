# Informe 0.18.0 — Implementación de `oracle juzgar` (P0, P1, Tests y Documentación)

**Fecha:** 2026-09-15  
**Autor:** AGY (Antigravity)  
**Revisa y verifica:** Claude (Claude Code)  
**Encargo:** `vault-kb/estudios/0.18.0-juzgar/ENCARGO-AGY.md`  
**Plan base:** `vault-kb/planes/PLAN-0.18.0-JUZGAR.md`  
**Avance previo:** `vault-kb/estudios/0.18.0-juzgar/AVANCE-AGY.md`

---

## 1. Declaración de Cumplimiento de Restricciones

- **Herramientas empleadas**: exclusivamente herramientas de lectura y edición de archivos (`view_file`, `write_to_file`, `replace_file_content`, `grep_search`, `list_dir`, `find_by_name`).
- **Restricciones respetadas estrictamente**:
  - NO se ejecutó ningún comando shell (`run_command` no fue invocado).
  - NO se ejecutaron suites de prueba ni herramientas de mutación por parte de AGY (la verificación queda delegada íntegramente a Claude).
  - NO se invocaron subagentes ni herramientas de red.
  - NO se realizaron operaciones de Git ni commits.
  - NO se modificaron archivos fuera de la propiedad asignada a AGY (`README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/version.py`, `ejemplo/seguimiento-tareas/`, `tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `docs/manual.html`, y los tests existentes / de revisión permanecen intactos).

---

## 2. P0: Con qué catálogo juzga hoy un consumidor

Se realizó la auditoría de código requerida en el encargo, citando funciones y líneas precisas:

### 2.1. Selección de medidas en `oracle test` / `tools/aceptacion.py` para proyectos externos
- **Función y llamada**: En `tools/cli.py` (`cmd_test`, línea 877), `oracle test` delega en `aceptacion._ejecutar(proy)`. En `tools/aceptacion.py` (`_ejecutar`, línea 105), el catálogo se obtiene mediante:
  ```python
  catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
  ```
- **Aplicación de ámbito (`ambito`)**: `catalogo_efectivo` (en `nucleo/proyecto.py`, líneas 380–410) carga las fuentes base y del proyecto con `catalogos_a_cargar(proy)` y filtra rigurosamente las entradas:
  ```python
  return catalogo.filtrar(
      lambda entrada: (
          entrada.medida.ambito in ("universal", AMBITO_SIN_DECLARAR)
          or (entrada.medida.ambito == "del_origen"
              and _el_origen_es_el_proyecto(entrada.origen, proy))
      )
  )
  ```
  Donde `_el_origen_es_el_proyecto(origen, proy)` (líneas 373–377) sólo devuelve `True` si `origen == ORIGEN_PROYECTO`, o si `origen == ORIGEN_CATALOGO_BASE and proy.es_el_propio_oracle`.  
  Por tanto, para cualquier proyecto externo (incluso si declara `"catalogo_base": true`), las medidas empaquetadas en el catálogo base que declaran `ambito: del_origen` (18 medidas) son **descartadas y no forman parte del catálogo efectivo**.
- **Aplicación de sombras (`sombra`)**: En `tools/aceptacion.py` (líneas 196–212), las medidas declaradas en la sección `"sombra"` de `oracle.json` son registradas en `en_sombra`. Si una medida ensombrecida no satisface su umbral (`not v.ok`), se marca como `[EN SOMBRA]`, se reporta su antigüedad y motivo, y **no se añade a las fallas de la corrida**, permitiendo que la suite resulte verde (código 0).

### 2.2. Qué usa `Motor.desde_proyecto`
- En `oracle_metalenguaje/motor.py` (`Motor.desde_proyecto`, líneas 135–160):
  ```python
  with escalares_del_proyecto(proy, confiar=confiar_escalares, registro=registro):
      catalogo = cargar_catalogo(
          catalogos_a_cargar(proy, raices_perfiles=raices_perfiles),
          registro=registro,
          limites=limites_propios,
          macros=macros,
      )
  return cls._crear(catalogo.values(), registro, limites_propios, proyecto=raiz)
  ```
- **Divergencias**:
  1. `Motor.desde_proyecto` utiliza directamente `catalogos_a_cargar(proy)`.
  2. **NO llama a `catalogo_efectivo`**: omite por completo el filtro de `ambito`. En un proyecto con `"catalogo_base": true`, `Motor._medidas` retiene indebidamente las 18 medidas de ámbito `del_origen` de Oracle.
  3. **NO procesa sombras**: `Motor` no consulta `configuracion(proy).sombra`. En `Motor.evaluar(evidencia)`, evalúa todas las medidas aplicables y devuelve `Informe(tuple(veredictos))`, cuyo veredicto es estrictamente `ok = all(v.ok for v in self.veredictos)`. Si una medida falla pero está en sombra, `Motor.evaluar` arroja un veredicto rojo (`ok == False`), contradiciendo la aceptación de `oracle test`.

### 2.3. Proyectos mínimos concretos donde divergen

1. **Divergencia por `ambito` (`del_origen` del catálogo base)**:
   - `oracle.json`: `{"esquema": "oracle.proyecto/v1", "catalogo_base": true}`
   - `catalogos/demo/` y `corpus/demo/` configurados.
   - Evidencia:
     ```json
     {
       "verbo_del_cli": [
         {"sustantivo": "proyecto", "verbo": "inventado", "nombrado_en_la_ayuda": false}
       ]
     }
     ```
   - **En `oracle test` / `catalogo_efectivo`**: La medida `meta.todo_verbo_del_cli_esta_en_la_ayuda` es `del_origen` de Oracle. Como el proyecto es externo, queda excluida del catálogo efectivo. No hay medidas aplicables para `verbo_del_cli`.
   - **En `Motor.desde_proyecto`**: La medida permanece en `Motor._medidas`. Al evaluar, se encuentra aplicable, detecta la fila con `nombrado_en_la_ayuda == false`, excede el umbral `<= 0` y emite **ROJO (✗)**, fallando por una política que no tiene jurisdicción sobre el proyecto.

2. **Divergencia por `sombra`**:
   - Medida local `demo.infraccion` (umbral `<= 0` donde `falla == true`).
   - `oracle.json` declara `"sombra": {"demo.infraccion": {"desde": "2026-09-15", "porque": "deuda"}}`.
   - Evidencia: `{"item": [{"falla": true}]}`.
   - **En `oracle test`**: La medida falla pero la sombra suspende el fallo: la corrida pasa (código 0).
   - **En `Motor.desde_proyecto`**: `Motor.evaluar` desconoce la sombra y retorna `informe.ok == False` (**ROJO**, código 1).

### 2.4. Aislamiento para P1
Siguiendo las instrucciones de no alterar todavía `Motor`, la selección correcta se aisló en `tools/juzgar.py` mediante la función `catalogo_para_juzgar(proy, ...)`:
```python
def catalogo_para_juzgar(proy: Proyecto, *, raices_perfiles=(), registro=None,
                         limites=None, macros=None) -> Catalogo:
    if macros is None:
        macros = macros_del_proyecto(proy, raices_perfiles=raices_perfiles)
    return catalogo_efectivo(
        proy,
        raices_perfiles=raices_perfiles,
        registro=registro,
        limites=limites,
        macros=macros,
    )
```
Esta función queda lista para ser compartida por la fachada `Motor` cuando se decida corregirla.

---

## 3. P1: Implementación del Verbo `oracle juzgar`

### 3.1. Módulo `tools/juzgar.py`
Se creó el módulo con las siguientes responsabilidades:
- **Parseo de argumentos**:
  - `--con <ruta>`: obligatorio. Si falta, o no indica ruta, o se repite -> código 2 con diagnóstico a `stderr`.
  - `--medida <id>`: repetible, sin duplicados. Si un ID se repite, no existe en el catálogo efectivo o no es aplicable a la evidencia -> código 2 a `stderr` nombrando el ID.
  - `--json`: salida estructurada sin ruido en `stdout`.
  - `--confiar-escalares`: autorización para `escalares.py`.
  - `--proyecto <ruta>`: resolución estándar.
  - Rechazo de cualquier bandera o argumento desconocido con código 2 a `stderr`.
- **Lectura segura de evidencia**:
  - Comprobación de existencia y tipo de archivo (rechaza rutas ausentes o directorios con código 2).
  - Cota de tamaño explícita: `LIMITE_TAMANO_EVIDENCIA = 50 * 1024 * 1024` (50 MiB). Archivos que excedan el límite son rechazados con código 2 sin cargarse en memoria.
  - Decodificación estricta en UTF-8 (`errors="strict"`). Bytes inválidos devuelven código 2 sin traceback.
  - Parseo JSON estricto (`json.loads`). JSON roto devuelve código 2 sin traceback.
  - Validación estructural: la evidencia debe ser un diccionario cuyas claves sean cadenas no vacías y cuyos valores sean listas de diccionarios (filas). Cualquier otra estructura devuelve código 2 sin traceback.
- **Resolución y auditoría del proyecto**:
  - Resolución vía `resolver(argv)`.
  - Verificación de estructura con `problemas_estructura(proy, ("catalogos",))`. Si falta `catalogos/` o `oracle.json` es inválido -> código 2.
- **Escalares externas**:
  - Si `escalares.py` existe en un proyecto externo y no se pasó `--confiar-escalares`, se rechaza con código 2 y el mensaje idéntico al de `oracle test`:
    `ESCALARES EXTERNAS NO EJECUTADAS — <ruta> es código Python externo; repetí con --confiar-escalares para ejecutarlo`
    sin ejecutar el archivo.
  - Con `--confiar-escalares`, se ejecuta en el contexto revertible de `escalares_del_proyecto`.
- **Aplicabilidad y evaluación**:
  - Si no se pasa `--medida`, se seleccionan todas las `medidas_aplicables(catalogo.values(), evidencia)`. Si ninguna aplica -> código 1 con mensaje `SIN MEDIDAS APLICABLES` y las relaciones de la evidencia a `stderr`.
  - Si se pasa `--medida`, se evalúan sólo las medidas indicadas tras verificar existencia y aplicabilidad.
  - Evaluación ejecutada en el contexto de escalares: `informe = evaluar(medidas_a_evaluar, evidencia)`.
- **Salida**:
  - Por defecto: `informe.texto()` en `stdout`.
  - Con `--json`: `informe.a_json()` en `stdout` y ningún texto adicional.
  - Retorno: código 0 si `informe.ok` es verdadero; código 1 si no.

### 3.2. Integración en `tools/cli.py`
- Se agregó `juzgar` en `VERBOS["proyecto"]`.
- Se agregó `juzgar` en `VERBOS_DIRECTOS`.
- Se registró el alias `("oracle", "juzgar"): "juzgar"` en `ALIAS`.
- Se actualizó `verbos_aceptados` para resolver de forma segura tanto sustantivos estándar como `oracle`.
- Se actualizaron el docstring del módulo `__doc__`, la función `ayuda()` y la función `ayuda_proyecto()`.
- Se incorporó el despacho temprano en `main()` para atender tanto `oracle juzgar` como `oracle proyecto juzgar` antes de la resolución genérica, asegurando que los fallos de proyecto devuelvan código 2.

---

## 4. Tests: `tests/test_juzgar.py`

Se construyó la suite exhaustiva de pruebas unitarias y de integración en `tests/test_juzgar.py`, estructurada en seis clases de prueba:

1. **`TestVeredictosYSalidas`**:
   - `test_verde_con_alcance_enumerado_retorna_cero`: comprueba código 0, marca verde y sección `SIN MIRAR:` con el alcance.
   - `test_rojo_con_testigo_retorna_uno`: comprueba código 1, marca roja y presencia de los testigos en `stdout`.
   - `test_json_parseable_y_sin_ruido_en_stdout`: comprueba que con `--json` la salida estándar sea exclusivamente JSON parseable con `ok: false`, lista de medidas y testigos.
   - `test_paridad_alias_juzgar_y_proyecto_juzgar`: comprueba que `oracle juzgar` y `oracle proyecto juzgar` produzcan idéntico código de salida, `stdout` y `stderr`.
   - `test_evaluacion_sin_medida_aplica_todas_las_pertinentes`: comprueba la selección automática de todas las medidas aplicables cuando no se pasa `--medida`.

2. **`TestEntradaInvalida`**:
   - `test_sin_con_retorna_dos`: falta de `--con` -> código 2.
   - `test_con_sin_ruta_retorna_dos`: `--con` sin argumento o seguido de bandera -> código 2.
   - `test_con_repetido_retorna_dos`: repetición de `--con` -> código 2.
   - `test_archivo_ausente_retorna_dos_y_nombra_ruta`: archivo inexistente -> código 2, diagnóstico nombra la ruta.
   - `test_ruta_directorio_retorna_dos`: ruta que apunta a un directorio -> código 2.
   - `test_evidencia_no_objeto_retorna_dos`: lista JSON en la raíz -> código 2.
   - `test_evidencia_valor_no_lista_retorna_dos`: valor de relación que no es lista -> código 2.
   - `test_evidencia_fila_no_objeto_retorna_dos`: fila de relación que no es diccionario -> código 2.
   - `test_evidencia_json_malformado_retorna_dos`: sintaxis JSON rota -> código 2 sin traceback.
   - `test_evidencia_utf8_invalido_retorna_dos`: bytes no decodificables como UTF-8 -> código 2 sin traceback.
   - `test_evidencia_supera_tope_50mib_retorna_dos`: archivo sparse que excede los 50 MiB -> código 2 indicando el límite.
   - `test_argumento_desconocido_retorna_dos`: bandera no reconocida -> código 2.

3. **`TestAplicabilidadYRestricciones`**:
   - `test_sin_medidas_aplicables_retorna_uno_y_menciona_relaciones`: relaciones sin medidas que las midan -> código 1, «SIN MEDIDAS APLICABLES».
   - `test_medida_inexistente_retorna_dos_y_la_nombra`: ID no existente en el catálogo -> código 2 nombrando el ID.
   - `test_medida_duplicada_retorna_dos`: repetición del mismo ID en `--medida` -> código 2.
   - `test_medida_no_aplicable_a_evidencia_retorna_dos_y_la_nombra`: medida cuyas relaciones no están en la evidencia -> código 2 nombrando la medida y las relaciones requeridas.

4. **`TestEscalaresYProyecto`**:
   - `test_escalares_sin_confianza_retorna_dos_y_no_las_ejecuta`: `escalares.py` presente sin `--confiar-escalares` -> código 2, no escribe archivo testigo, mensaje idéntico a `oracle test`.
   - `test_escalares_con_confianza_autoriza_ejecucion`: con `--confiar-escalares` ejecuta con código 0.
   - `test_proyecto_sin_catalogos_retorna_dos`: directorio sin `catalogos/` -> código 2.
   - `test_proyecto_oracle_json_invalido_retorna_dos`: `oracle.json` corrupto -> código 2.

5. **`TestAyudasYNoMutacion`**:
   - `test_ayuda_no_escribe_archivos`: verifica que invocar `--help` y corridas normales no generen archivos residuales en disco.
   - `test_ayudas_generales_documentan_juzgar`: verifica que `oracle --help` y `oracle proyecto --help` documenten el verbo y sus opciones.

6. **`TestIntegracionTracker`**:
   - `test_hechos_reales_del_tracker_verde_y_luego_rojo`: ciclo completo de integración. Inicializa un tracker con `oracle tarea init`, crea una tarea con adjunto y enlace local, exporta los hechos reales con `oracle tarea hechos`, y los juzga con `oracle juzgar` contra `ejemplo/seguimiento-tareas`:
     1. Con el archivo presente: veredicto VERDE (código 0).
     2. Modificando el enlace hacia un archivo inexistente: veredicto ROJO (código 1) con el nombre del archivo ausente reportado como testigo.

---

## 5. Documentación: `docs/12-tareas.md`

Se actualizó la documentación del tracker en `docs/12-tareas.md`:
1. En la descripción de `oracle tarea hechos` (línea 165), se actualizó la referencia histórica a `evaluar.py` reemplazándola por `oracle juzgar --proyecto ejemplo/seguimiento-tareas --con <hechos.json>`.
2. Se incorporó una nueva subsección completa: `### Juzgar los hechos del tracker con oracle juzgar`, detallando:
   - Sintaxis de invocación para el catálogo completo y para medidas individuales.
   - Especificación rigurosa de cada una de las tres políticas de `ejemplo/seguimiento-tareas`:
     - `seguimiento.referencias_locales_presentes`: qué verifica (presencia física en disco de referencias relativas locales) y qué NO prueba (contenido/legibilidad de adjuntos, URLs externas, anclas).
     - `seguimiento.archivos_confirmados_sin_cambios`: qué verifica (inclusión en `HEAD`/índice sin modificaciones locales de trabajo) y qué NO prueba (sincronización con repositorios remotos, push, ramas divergentes).
     - `seguimiento.lectura_sin_omisiones`: qué verifica (extracción completa sin omisiones por límites de tamaño, symlinks o codificación) y qué NO prueba (calidad o completitud semántica de la planificación humana).
3. En el tutorial del ciclo completo, se actualizó el paso de evaluación de evidencia hacia la invocación de `oracle juzgar`.

---

## 6. Archivos Modificados y Creados

| Archivo | Estado | Responsabilidad |
|---|---|---|
| `vault-kb/estudios/0.18.0-juzgar/AVANCE-AGY.md` | Creado | Respuestas a P0, diagnóstico de divergencias y plan de archivos. |
| `tools/juzgar.py` | Creado | Implementación de `cmd_juzgar`, `catalogo_para_juzgar`, lectura con tope de 50 MiB y UTF-8 estricto, aplicabilidad y códigos 0, 1, 2. |
| `tools/cli.py` | Modificado | Registro de `juzgar` en `VERBOS["proyecto"]`, `VERBOS_DIRECTOS`, `ALIAS`, actualización de ayudas y despacho en `main()`. |
| `docs/12-tareas.md` | Modificado | Sección sobre cómo juzgar hechos del tracker con `oracle juzgar` y detalle de las tres políticas. |
| `tests/test_juzgar.py` | Creado | Suite completa de pruebas unitarias y de integración para `juzgar`. |
| `vault-kb/estudios/0.18.0-juzgar/INFORME-AGY.md` | Creado | Informe final consolidado del tramo 0.18.0. |

Todos los archivos quedan listos para que Claude ejecute la verificación independiente y la suite completa de pruebas.

---

## 7. Correcciones tras la revisión (R1 a R6)

En respuesta al informe de revisión de Claude (`vault-kb/estudios/0.18.0-juzgar/REVISION-CLAUDE.md`), se implementaron las siguientes correcciones en los archivos bajo propiedad de AGY:

### R1. Soporte de medidas ensombrecidas (`tools/juzgar.py`)
- Se incorporó la lectura de sombras desde `configuracion(proy).sombra` (`nucleo/proyecto.py`), alineando el comportamiento con `tools/aceptacion.py`.
- Las medidas en sombra se evalúan normalmente y se reportan:
  - En la salida de texto, la línea del veredicto se marca con `[EN SOMBRA]` junto con su fecha `desde` y su motivo `porque` (`[EN SOMBRA] (desde <fecha>; porque: <motivo>)`), listando los testigos correspondientes en caso de falla.
  - En la salida `--json`, cada elemento de la lista `"medidas"` incluye el campo booleano `"en_sombra"`, preservando intactos todos los campos y nombres preexistentes.
- El cálculo del código de salida no considera fallas en medidas ensombrecidas: si todas las fallas están en sombra, la ejecución retorna código 0 y el campo `"ok"` en la raíz del JSON es `true`.
- Cuando todas las medidas aplicables resultan en rojo pero están en sombra, el reporte de texto no emite «verde» a secas, sino que explicita `VEREDICTO: verde por sombra en X medidas (Y en sombra en rojo). SIN MIRAR:`, manteniendo la enumeración de alcances.

### R2. Despacho unificado sin duplicación en `tools/cli.py`
- Se eliminaron los dos despachos redundantes y muertos de `juzgar` en `tools/cli.py` (líneas bajo `subcomando == "proyecto"` y atajos directos posteriores a la resolución del proyecto).
- Se unificó el despacho anticipado en una única condición en `main()` previa a la resolución genérica, evitando sitios de mutación equivalentes y manteniendo el retorno con código 2 ante proyectos inválidos.

### R3. Reversión de alias y restauración de `verbos_aceptados` (`tools/cli.py`)
- Se eliminó la entrada innecesaria `("oracle", "juzgar"): "juzgar"` de `ALIAS` (los comandos directos ya están declarados en `VERBOS_DIRECTOS`).
- Se restauró la implementación canónica de `verbos_aceptados(sustantivo)` accediendo directamente a `VERBOS[sustantivo]`, recuperando el levantamiento explícito de `KeyError` ante sustantivos desconocidos en lugar de enmascararlos con tuplas vacías.

### R4. Acotamiento de excepciones en evaluación (`tools/juzgar.py`)
- Se reemplazó el bloque genérico `except Exception` por la captura exclusiva de excepciones correspondientes a entradas o catálogos inválidos:
  - `(EscalaresNoConfiables, EscalaresInvalidas)`
  - `ProyectoInvalido`
  - `(MedidaMalDeclarada, ErrorDeAlgebra, KeyError)`
- Cualquier error imprevisto de programación o defecto interno del evaluador se propaga sin atrapar para visibilidad directa del traceback.

### R5. Consumo estricto de sustantivo y verbo iniciales (`tools/juzgar.py`)
- Se modificó `cmd_juzgar` para consumir únicamente el prefijo inicial de comando (`"proyecto"` y/o `"juzgar"`, `"--juzgar"`).
- Se eliminó la omisión indiscriminada de estos tokens dentro del bucle de opciones; ahora cualquier argumento extra o token suelto en posiciones posteriores (como `oracle juzgar --con hechos.json proyecto`) es catalogado como argumento desconocido y rechazado con código 2 a `stderr`.

### R6. Ajustes de fidelidad en la documentación (`docs/12-tareas.md`)
- Se ajustaron los límites citados para la extracción de hechos a los topes reales aplicados por el extractor (`tools/tareas_hechos.py`): límite de 2 MiB para documentos Markdown (`TAREA.md` y adjuntos Markdown), sin afirmar límites inexistentes.
- Se reescribió la descripción de la política `seguimiento.archivos_confirmados_sin_cambios` para reproducir con exactitud su condición formal del `.oracle`:
  `donde a.git_comprobado == false o a.en_head == false o a.indice != " " o a.trabajo != " "` (comprobación Git activa, archivo en `HEAD`, e índice y árbol de trabajo limpios).
- Se clarificó la ubicación física del archivo generado en el tutorial del ciclo completo, indicando que `hechos-tareas.json` queda dentro del directorio temporal `$proyecto_prueba/hechos-tareas.json` y mostrando cómo invocar `oracle juzgar` referenciando esa ruta.

### Pruebas de regresión añadidas (`tests/test_juzgar.py`)
Se agregó la clase `TestRevisionCorrecciones` con pruebas específicas para cada punto:
- `test_r1_medida_en_sombra_en_rojo_sale_cero_con_marca_y_testigo`
- `test_r1_todas_aplicables_en_sombra_en_rojo_dice_verde_por_sombra`
- `test_r1_json_agrega_campo_en_sombra_sin_remover_ni_renombrar`
- `test_r1_rojo_fuera_de_sombra_con_rojo_en_sombra_sale_uno`
- `test_r2_despacho_unico_cli`
- `test_r3_alias_y_verbos_aceptados_revertidos`
- `test_r4_excepciones_acotadas_a_entrada_y_catalogo`
- `test_r5_tokens_sueltos_rechazados_con_codigo_dos`

