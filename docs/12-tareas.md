# 12 · Tareas y contexto de trabajo en Git

Contrato, especificación y guía de uso del tracker local de tareas de Oracle.

## 1. El modelo

Oracle organiza tareas y pendientes como carpetas dentro de `tareas/` en la raíz del proyecto.
Cada tarea es un directorio autónomo con un archivo central `TAREA.md` y cualquier adjunto local asociado (capturas, notas, esquemas, volcados de evidencia).

El formato privilegia la legibilidad y la edición manual:
- Una persona puede editar `TAREA.md` con su editor favorito o copiar archivos al directorio de la tarea.
- La herramienta CLI lee y escribe el archivo preservando el cuerpo, campos adicionales y formato.
- Git conserva la historia de los archivos que agregás y confirmás con commits. Crear una tarea
  no la agrega automáticamente a Git: revisá las reglas de ignore y usá `git add tareas/` y
  `git commit` cuando quieras registrar el contenido.
- La herramienta es independiente del catálogo: no requiere catálogos ni evalúa escalares para operar.

```text
mi-proyecto/
  tareas/
    README.md
    20260911-180000-investigar-sensor/
      TAREA.md
      captura.png
      notas.md
    20260911-181500-kb-timeout-arnes/
      TAREA.md
```

## 2. Descubrimiento de la raíz del tracker

El tracker determina la raíz de trabajo aplicando el siguiente orden de precedencia estricto:

1. **Bandera explícita**: `--proyecto <ruta>` en la línea de comandos.
2. **Variable de entorno**: `$ORACLE_PROYECTO`.
3. **Búsqueda local ascendente**: desde el directorio de trabajo actual (`cwd`), inspecciona cada directorio ascendiendo hacia la raíz del sistema de archivos buscando la presencia de un subdirectorio `tareas/`.
   - **Límite Git**: la búsqueda automática se detiene inmediatamente si encuentra un límite de repositorio Git (`.git`) y no continúa hacia directorios superiores, evitando saltar accidentalmente al tracker de un repositorio padre o contenedor.
   - Si no se encuentra `tareas/` antes o al alcanzar el límite Git, la resolución falla informando que no hay tracker inicializado.

El comando `oracle tarea init [ruta] [--sin-readme]` inicializa el tracker creando el directorio `tareas/` (y opcionalmente `tareas/README.md`, salvo que se especifique `--sin-readme`) en la ruta indicada o en el directorio actual. No exige la presencia de `catalogos/` ni `oracle.json`.

## 3. Identidad de tareas y resolución de colisiones

Cada tarea posee un identificador único basado en tiempo universal coordinado (UTC):

- **Formato canónico**: `YYYYMMDD-HHMMSS[-sufijo]`
  - Ejemplo sin sufijo: `20260911-183000`
  - Ejemplo con sufijo: `20260911-183000-defecto-sensor`
- **De dónde sale el sufijo**: el de `--sufijo`, tal cual, saneado. Sin `--sufijo` se deriva del
  título y se corta en **16 caracteres**, en un límite de palabra: el ID entero es el prefijo de cada
  commit de esa tarea, y con 40 caracteres el prefijo se comía el renglón. `--sufijo ""` deja el ID
  sin sufijo, que es una elección distinta de no pasar nada.
- **Sufijo opcional**: si se proporciona (o se deriva del título/argumento), se normaliza a minúsculas ASCII y guiones, sin caracteres especiales ni secuencias `..` o separadores de ruta.
- **Resolución determinista de colisiones**: si se crean dos o más tareas dentro del mismo segundo en el mismo proyecto (mismo timestamp y sufijo), el sistema agrega un desambiguador numérico secuencial (`-1`, `-2`, etc.) sin sobrescribir directorios existentes ni bloquear la ejecución en bucles de espera:
  - `20260911-183000-sensor`
  - `20260911-183000-sensor-1`
  - `20260911-183000-sensor-2`

### Seguridad y confinamiento de rutas

- Los IDs y prefijos no admiten `..`, `/` ni `\`. Las rutas de proyecto sí pueden ser
  absolutas o relativas y contener espacios.
- La ruta resuelta de una tarea debe pertenecer estrictamente al árbol de `tareas/` del proyecto.
- No se siguen enlaces simbólicos que apunten fuera del directorio `tareas/`. Cualquier intento de escape se rechaza con código de error 1.

Los títulos, etiquetas y nombres de adjuntos no admiten saltos de línea, incluidos separadores Unicode.

## 4. Anatomía y especificación de `TAREA.md`

Un archivo `TAREA.md` se compone de tres partes ordenadas:

1. **Título (H1)**: la primera línea no vacía del documento debe ser un encabezado Markdown de nivel 1 (`# Título de la tarea`).
2. **Bloque de metadatos**: situado inmediatamente después del título (permitiendo líneas en blanco intermedias), consiste en una lista contigua de elementos Markdown con la forma `- CLAVE: VALOR`.
   - `ESTADO`: obligatorio, toma exclusivamente los valores `ABIERTA` o `CERRADA`.
   - `PRIORIDAD`: obligatorio, un número entero (ej. `50`, `100`, `0`). A mayor número, mayor prioridad en los listados. El valor por defecto al crear es `50`.
   - `ETIQUETAS`: lista de etiquetas separadas por comas (ej. `bug, sensor, urgente`).
   - **Campos adicionales**: se admiten campos personalizados (ej. `- ASIGNADO: brian`) y se preservan intactos en operaciones de actualización.
   - **Validación estricta**: campos duplicados dentro del bloque de metadatos o estados desconocidos constituyen un error que invalida la tarea.
3. **Cuerpo libre**: todo el texto posterior al bloque de metadatos, separado por al menos una línea en blanco.
   - El cuerpo admite cualquier contenido Markdown: secciones, listas, tablas, enlaces relativos y bloques de código.
   - **Aislamiento**: líneas dentro del cuerpo libre o dentro de bloques de código cercados (```` ``` ````) que se asemejen a metadatos (como `- ESTADO: ABIERTA`) se interpretan como texto plano y no alteran la cabecera.

### Preservación en escrituras

Los comandos de modificación de estado (`cerrar`, `reabrir`):
- Modifican únicamente la línea `- ESTADO: ...` del bloque de metadatos.
- Preservan intactos el título, los demás campos de metadatos (incluyendo orden y campos desconocidos) y todo el cuerpo libre.
- La escritura se realiza mediante reemplazo atómico (escribiendo a un archivo temporal contiguo y reemplazando con `os.replace`), evitando archivos a medio escribir ante interrupciones.
- La operación es idempotente: cerrar una tarea ya cerrada o reabrir una ya abierta no produce cambios y sale con código 0.

## 5. Comandos del CLI (`oracle tarea`)

| Comando | Argumentos / Opciones | Descripción |
|---|---|---|
| `oracle tarea init` | `[ruta] [--sin-readme]` | Inicializa `tareas/` y opcionalmente `tareas/README.md`. |
| `oracle tarea nueva` | `<titulo> [--etiqueta/-e <etiqueta>]... [--prioridad <n>] [--sufijo <sufijo>] [--json]` | Crea una nueva tarea y devuelve su ID y ruta. |
| `oracle tarea listar` / `ls` | `[consulta] [--cerradas] [--todas] [--etiqueta/-e <e>] [--texto/-t <s>] [--por-id] [--invertir] [--explicar] [--json]` | Lista tareas abiertas (o cerradas/todas). Admite expresiones TQL, orden por ID descendente e inversión. |
| `oracle tarea ver` | `<id> [--ruta] [--json]` | Muestra detalles de la tarea. Admite prefijos inequívocos. Con `--ruta` imprime solo la ruta al archivo. |
| `oracle tarea cerrar` | `<id>` | Cambia el estado a `CERRADA` de forma atómica y preserva el resto. |
| `oracle tarea reabrir` | `<id>` | Cambia el estado a `ABIERTA` de forma atómica y preserva el resto. |
| `oracle tarea revisar` | `[--json]` | Audita la integridad del directorio tareas/: detecta carpetas sin `TAREA.md`, metadatos inválidos y omisiones. |
| `oracle tarea anotar` | `<id> [texto] [--url <url>] [--marca <marca>] [--json]` | Agrega una nota, enlace web o marca al cuerpo de la tarea sin descargar contenido remoto. |
| `oracle tarea adjuntar` | `<id> <archivo> [--permitir-grande] [--json]` | Copia un archivo regular al directorio de la tarea y lo vincula en `TAREA.md`. |
| `oracle tarea buscar` | `<texto> [--json]` | Búsqueda literal en documentos y notas de texto del tracker (omite binarios y archivos > 2 MiB). |
| `oracle tarea referencias` | `[id] [--json]` | Busca menciones textuales del ID canónico en tareas y código fuente. Sin ID, deduce la tarea desde el directorio actual. |
| `oracle tarea resumen` | `[--json]` | Reporta cantidades agregadas por estado y etiquetas a partir de registros válidos. |
| `oracle tarea seguimiento` | `[opciones]` | Diagnóstico de seguimiento y cobertura de tareas y adjuntos en Git. |
| `oracle tarea hechos` | `[--git] [--json]` | Emite evidencia relacional de tareas, inventario, referencias y omisiones en JSON. |
| `oracle tarea etiquetar` | `<id>... --etiqueta <e> [--json]` | Agrega una o más etiquetas a tareas existentes de forma atómica. |
| `oracle tarea desetiquetar` | `[<id>...] --etiqueta <e> [--consulta <tql>] [--cerradas] [--todas] [--json]` | Quita una o más etiquetas de tareas de forma atómica (por ID o por consulta TQL masiva). |
| `oracle tarea grafo` | `[--json]` | Emite el grafo de referencias entre tareas en formato DOT o JSON. |

Todos los subcomandos aceptan `--proyecto <ruta>` para operar sobre un directorio explícito.

### Reglas de captura y contexto (P2)

- **`anotar`**:
  - Exige al menos un texto explicativo o una `--url`.
  - La `--url` debe ser absoluta con esquema `http` o `https`, sin espacios ni caracteres de control. Se preserva exactamente como fue introducida (incluyendo parámetros de consulta como `?t=01m30s`).
  - La opción `--marca` (por ejemplo `01:32` o `Capítulo 2`) representa una posición aportada por la persona y exige especificar `--url`.
  - La nota se añade al cuerpo de `TAREA.md` con timestamp UTC de captura, preservando todos los bytes anteriores, sangrías, espacios significativos y permisos del documento mediante reemplazo atómico. No realiza descargas remotas ni consultas de red.
- **`adjuntar`**:
  - Copia un archivo regular local al directorio de la tarea; conserva intacto el archivo de origen.
  - Preserva nombres con espacios y caracteres Unicode. En `TAREA.md` se genera un enlace Markdown relativo con destino URL escapado (`%20`, `%28`, `%29`, `%23`) y etiqueta visible protegida (escapando barras invertidas antes que corchetes). Rechaza nombres con saltos de línea o caracteres de control.
  - Rechaza enlaces simbólicos de origen, directorios, archivos especiales (FIFOs, dispositivos), destinos ya existentes (incluyendo enlaces rotos), el nombre reservado `TAREA.md` o rutas que escapen de la carpeta de la tarea.
  - Límite por defecto: 20 MiB acumulados durante la copia por bloques. Archivos mayores requieren pasar la bandera `--permitir-grande` explícita, sin imponer Git LFS.
  - Copia por bloques con creación exclusiva, sin sobrescribir destinos. El registro en `TAREA.md`
    usa reemplazo atómico; la copia y ese registro son dos operaciones. Ante un fallo detectado
    se intenta retirar únicamente la copia creada. Una interrupción del proceso puede dejar un
    adjunto sin registrar; no es una transacción entre dos archivos. Si falla la limpieza, el
    diagnóstico conserva la causa original, el error de limpieza y la ruta de la copia residual.
- **`buscar`**:
  - Búsqueda literal case-insensitive en documentos y notas/adjuntos de texto bajo `tareas/`, recorriendo de forma recursiva subdirectorios internos de las tareas (sin seguir enlaces ni repositorios anidados).
  - Admite `.md`, `.txt`, `.rst`, `.json`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`, `.log`,
    `.ini`, `.cfg`, `.conf`, `.sh`, `.bash`, `.py`, `.oracle`, `.js`, `.ts`, `.html`, `.htm`,
    `.css`, `.xml`, `.sql`, `.c`, `.h`, `.cpp`, `.hpp`, `.rs`, `.go` y `.java`, además de
    archivos sin extensión, si decodifican en UTF-8 sin bytes nulos.
  - Omite enlaces simbólicos, archivos especiales (FIFOs), archivos mayores a 2 MiB y archivos binarios reconocidos (`.png`, `.jpg`, `.pdf`, `.zip`, etc.) o con bytes nulos. Tanto en `--json` como en la salida humana se detallan los archivos `omitidos` con su motivo.
  - Cero coincidencias devuelve éxito (código 0). Registros rotos, carpetas corruptas en `tareas/` o fallos operacionales de lectura devuelven código 1; no se disfrazan de búsqueda vacía.
- **`referencias`**:
  - Audita el tracker (fallando con código 1 ante tareas corruptas), resuelve el ID inequívoco y busca menciones de ese ID canónico exacto en las tareas y en el código fuente bajo la raíz del proyecto.
  - Si se omite el argumento `[id]`, determina la tarea automáticamente verificando si el directorio de trabajo actual (`cwd`) se encuentra dentro de la carpeta de una tarea o de cualquiera de sus subdirectorios (ej. `tareas/20260915-100000-a/notas`). Si se invoca fuera del directorio de una tarea sin especificar ID, emite un error a `stderr` y finaliza con código 2 sin volcar trazas.
  - Utiliza límites de palabra/identificador (`(?<![a-zA-Z0-9_-])ID(?![a-zA-Z0-9_-])`) para no atribuir menciones de tareas derivadas (como `ID-1` o `copia-ID`) al ID original.
  - Excluye automáticamente directorios de control y compilación: `.git`, `.hg`, `.svn`, `.venv`, `venv`, `node_modules`, `__pycache__`, `build` y `dist`, sin seguir enlaces simbólicos ni entrar en repositorios anidados.
  - Informa archivos omitidos en consola y formato JSON. Las menciones textuales son referencias de contexto, no dependencias declaradas.
- **`resumen`**:
  - Audita el directorio `tareas/` y calcula el total de tareas, cantidades por estado (`ABIERTA`, `CERRADA`) y censo por etiquetas.
  - Conserva las mayúsculas y minúsculas exactas de las etiquetas, deduplicando sólo identidades idénticas por tarea. Las etiquetas se presentan en orden alfabético estable.
  - No escribe cachés en disco. Si existen carpetas corruptas o metadatos inválidos, la operación falla con código 1. En un tracker vacío devuelve total 0 con código 0.
- **`seguimiento`**:
  - Acepta `--json` y `--proyecto`. Consulta los archivos bajo `tareas/`, incluidos auxiliares,
    adjuntos y archivos borrados aún presentes en el índice o en `HEAD`.
  - Distingue `sin_seguimiento`, `ignorado`, `con_cambios` y `sin_cambios`. Informa por separado
    `existe`, `en_indice` y `en_head`: agregar un archivo al índice no significa haberlo confirmado.
    Que una ruta figure en `HEAD` tampoco implica que su contenido actual esté confirmado;
    los indicadores `indice`, `trabajo` y `codigos_git` muestran cambios pendientes.
  - Las rutas de archivos son relativas al proyecto, incluso si éste ocupa una subcarpeta del
    repositorio. `head` identifica el commit observado o es `null` si no hay commits.
  - Sin repositorio devuelve código 0 con `repositorio: null` y la lista `sin_repositorio`.
    Git ausente o un fallo al consultarlo devuelve código 1: cobertura no comprobada.
  - No ejecuta `git add`, commit ni operaciones de red, ni modifica el índice. No recorre
    enlaces de directorio o subrepositorios; informa esas omisiones.

Las consultas de texto omiten archivos cuyo nombre empieza con punto y registran esa omisión.
Son observaciones de archivos locales durante la consulta; no bloquean editores ni otros procesos.
El seguimiento en Git no comprueba que haya un backup remoto o que los enlaces sigan disponibles.

### Evidencia relacional del tracker (P3)

El comando `oracle tarea hechos [--git] [--json] [--proyecto RUTA]` emite un objeto JSON relacional estructurado directamente a `stdout`, concebido para ser consumido por el evaluador de políticas de Oracle (`oracle juzgar --proyecto ejemplo/seguimiento-tareas --con <hechos.json>`), basado en `evaluar` y el catálogo efectivo.

La salida no se escribe en el tracker ni en disco; se redirige típicamente mediante tuberías o redirección shell hacia un archivo fuera del árbol de tareas (`oracle tarea hechos > /tmp/hechos.json`).

El JSON relacional contiene siempre cinco relaciones clave sin envoltorios adicionales:

1. **`lectura_seguimiento`** (exactamente una fila):
   - `esquema`: `"oracle.tareas.hechos/v1"`.
   - `completa`: booleano (`true` si no hubo omisiones en la lectura del tracker; `false` si se omitieron archivos o enlaces por tamaño, symlinks, codificación o rutas no seguras).
   - `git`: `"no_solicitado"` (sin bandera `--git`), `"sin_repositorio"` (si el proyecto no pertenece a un repositorio Git) o `"comprobado"` (si se auditó el repositorio con éxito).
   - `head`: identificador del commit `HEAD` o cadena vacía `""` si no hay commits o no se solicitó Git.

2. **`tarea_seguimiento`** (una fila por tarea válida registrada en el tracker, ordenada por `id`):
   - `id`: identificador canónico de la tarea.
   - `titulo`: título declarado en el primer encabezado de `TAREA.md`.
   - `estado_declarado`: estado textual en metadatos (`ABIERTA` o `CERRADA`).
   - `prioridad_declarada`: prioridad numérica entera.
   - `ruta`: ruta relativa POSIX al archivo `TAREA.md` desde la raíz del proyecto.
   - `sha256_documento`: hash SHA-256 en minúsculas de los bytes de `TAREA.md`.

3. **`archivo_seguimiento`** (inventario recursivo de archivos bajo `tareas/`, ordenado por `ruta`):
   - `tarea_id`: identificador de la tarea para documentos y adjuntos; cadena vacía `""` para archivos auxiliares (`README.md`, `.gitignore`).
   - `ruta`: ruta relativa POSIX desde la raíz del proyecto.
   - `clase`: `"documento"` (para `TAREA.md`), `"adjunto"` (para archivos dentro de carpetas de tareas) o `"auxiliar"` (para archivos documentados en la raíz de `tareas/`).
   - `tipo`: `"regular"`, `"enlace"`, `"especial"` (FIFOs, sockets, dispositivos) o `"ausente"` (archivos borrados del disco que aún constan en el índice o `HEAD` de Git).
   - `tamano_bytes`: tamaño en bytes (0 para archivos especiales o ausentes).
   - `existe`: booleano de presencia física en disco.
   - `git_comprobado`: booleano (`false` sin `--git` o sin repo; `true` si Git auditó la ruta).
   - `en_indice`, `en_head`, `ignorado`: booleanos del estado en Git.
   - `indice`, `trabajo`: caracteres de estado de Git (equivalentes a `git status --porcelain`).

4. **`referencia_seguimiento`** (una fila por cada aparición de enlace o mención de recurso en Markdown, ordenada por `origen`, `linea`, `destino_declarado`):
   - `tarea_id`: identificador de la tarea asociada o `""`.
   - `origen`: ruta relativa POSIX del archivo Markdown donde aparece la referencia.
   - `linea`: número de línea (1-indexed).
   - `destino_declarado`: texto exacto del destino tal como fue escrito en el documento.
   - `clase`:
     - `"local"`: rutas relativas a archivos o recursos locales.
     - `"remota"`: URLs absolutas con esquema `http` o `https` (insensible a mayúsculas/minúsculas).
     - `"ancla"`: referencias a fragmentos internos (`#seccion`).
     - `"no_admitida"`: esquemas no reconocidos (`mailto:`, `ftp:`, `file:`) o rutas de red (`//host`).
   - `estado`:
     - `"presente"`: el archivo local existe en disco dentro del proyecto.
     - `"ausente"`: el archivo local de destino no existe en la ruta referenciada o navega a través de archivos no directorios con `..`.
     - `"fuera_del_proyecto"`: la referencia apunta fuera de los límites del proyecto.
     - `"no_comprobado"`: referencias remotas, anclas, esquemas no admitidos o rutas locales donde cualquier componente (incluso previo a `..`) es un enlace simbólico.

5. **`omision_seguimiento`** (inventario de elementos o sintaxis que no pudieron procesarse, ordenado por `ruta`, `linea`, `motivo`):
   - `ruta`: ruta relativa POSIX del archivo afectado o del documento donde ocurrió la omisión.
   - `linea`: número de línea (1-indexed) o `0` cuando la omisión afecta a la totalidad del archivo.
   - `motivo`: descripción clara de la causa (ej. adjunto Markdown > 2 MiB, enlace simbólico, bytes nulos, enlaces por referencia no resueltos, sintaxis incompleta o multilínea).

**Garantías de límites, seguridad y gramática**:
- **Distinción entre centrales y adjuntos**: un documento central `TAREA.md` que supere los 2 MiB o sea un enlace simbólico invalida la integridad del tracker y hace fallar la ejecución con código 1. Por el contrario, un adjunto Markdown grande (> 2 MiB) se omite de forma controlada (`omision_seguimiento`, `completa=false`) sin abortar.
- **Seguridad en componentes de rutas**: la inspección de referencias locales analiza cada componente original sin normalizar prematuramente con `resolve()`. Rutas como `puente/../archivo.txt` donde `puente` es un symlink detectan el enlace simbólico y se clasifican como `no_comprobado` con omisión. Componentes regulares seguidos de `/..` se reconocen como no directorios (`ausente`).
- **Manejo estricto de errores de E/S**: sólo `FileNotFoundError` o `NotADirectoryError` acreditan ausencia. Permisos denegados (`PermissionError`) o errores operacionales abortan con código 1 sin emitir JSON parcial ni disfrazar fallos como archivos ausentes.
- **Alcance de la gramática Markdown**: no se afirma soporte de CommonMark completo. Se extraen enlaces inline `[texto](destino)`, `![alt](destino)`, destinos entre ángulos `<destino>`, autolinks `<http...>` y líneas `- URL: ...`. Se excluyen literales escapados `\[texto](...)`, código cercado y código inline. Cierres de bloques cercados exigen exclusivamente espacios tras la cerca. Sintaxis multilínea no resuelta (`[texto](\ndestino)`) genera omisión explícita.
- Los títulos de enlaces entre comillas simples o dobles se consumen como texto. Si la sintaxis no permite localizar su final, se omite el resto de esa línea y se declara la omisión.
- Los destinos locales con NUL codificado se declaran `no_admitida` y `no_comprobado`, con omisión. Un sufijo `/` o `/.` exige un directorio. Las barras obtenidas al decodificar `%5C` pertenecen al nombre del archivo y no se reinterpretan como escapes Markdown.
- Un backtick escapado fuera de código es literal; dentro de código la barra no anula el cierre. Las rachas de apertura y cierre deben tener igual longitud. Se sigue esta distinción de [CommonMark](https://spec.commonmark.org/0.31.2/#backslash-escapes), dentro de la gramática parcial descrita arriba.
- La salida JSON es compacta, conserva un orden fijo de campos y listas ordenadas, y escapa los caracteres no ASCII. Así conserva incluso nombres Unix que no se pueden decodificar como UTF-8 y produce los mismos bytes ante el mismo árbol.

6. **`commit_seguimiento`** (una fila por commit alcanzable desde `HEAD`, del más nuevo al más
   viejo; **vacía sin `--git`** o sin repositorio):
   - `sha`: el sha-1 completo del commit.
   - `asunto`: la primera línea del mensaje, tal cual.
   - `nombra_tarea`: booleano; `true` si el asunto tiene la forma `<ID>: resumen`.
   - `tarea_nombrada`: el ID nombrado, o `""`.
   - `tarea_existe`: booleano; si ese ID está hoy en `tareas/`.
   - `estado_de_la_tarea`: `ABIERTA`, `CERRADA` o `""` si no existe.
   - `es_cierre`: booleano; `true` sólo si el resumen es exactamente `done`. Un asunto que sigue con
     cualquier otra cosa —una firma pegada, por ejemplo— no es el commit de cierre que la convención
     pide, y que se vea es el punto de medirlo.

   No ve el cuerpo del mensaje, ni el autor, ni la fecha, ni los archivos tocados, y **no** comprueba
   que el trabajo del commit tenga que ver con la tarea que nombra: eso no lo puede saber ninguna
   medida.

### Juzgar los hechos del tracker con `oracle juzgar`

La evidencia emitida por `oracle tarea hechos` puede juzgarse directamente mediante el comando `oracle juzgar` (o su forma canónica `oracle proyecto juzgar`), pasando como proyecto el catálogo de políticas de seguimiento provisto en `ejemplo/seguimiento-tareas`:

```bash
oracle tarea hechos --git > hechos.json
oracle juzgar --proyecto ejemplo/seguimiento-tareas --con hechos.json
```

El evaluador carga el catálogo efectivo del proyecto, verifica que las relaciones requeridas estén presentes en la evidencia y emite un informe estructurado (`Informe.texto()` o `Informe.a_json()` con `--json`). Si todas las medidas aplicables resultan verdes, el comando finaliza con código 0; si alguna resulta roja o no hay medidas aplicables, finaliza con código 1.

#### Políticas de seguimiento del tracker

El catálogo de ejemplo en `ejemplo/seguimiento-tareas` define seis políticas de auditoría:

1. **`seguimiento.referencias_locales_presentes`**:
   - **Qué comprueba**: que ninguna referencia local reconocida apunte a un archivo ausente (`donde r.clase == "local" y r.estado != "presente"`). Exige que cada enlace local relativo (`[captura](captura.png)`) dentro de un documento `TAREA.md` apunte a un archivo físico existente en el árbol de la tarea.
   - **Qué NO prueba**: no prueba que el contenido del adjunto sea correcto ni legible (ej. una imagen corrupta pasa como presente), ni audita enlaces remotos (URLs HTTP/HTTPS), anclas internas o destinos fuera de la tarea.

2. **`seguimiento.archivos_confirmados_sin_cambios`**:
   - **Qué comprueba**: que ningún archivo del tracker incumpla `donde a.git_comprobado == false o a.en_head == false o a.indice != " " o a.trabajo != " "`. Es decir, exige que la consulta Git haya sido efectuada (`git_comprobado == true`), que el archivo esté presente en el commit de `HEAD` (`en_head == true`), y que no tenga modificaciones pendientes en el índice (`indice == " "`) ni en el árbol de trabajo (`trabajo == " "`).
   - **Qué NO prueba**: no comprueba repositorios remotos (`git push`), copias de respaldo, autenticidad, confidencialidad ni calidad del contenido. Requiere consulta Git activa; sin filas o sin comprobación Git falla.

3. **`seguimiento.lectura_sin_omisiones`**:
   - **Qué comprueba**: que la extracción de hechos haya sido íntegra (`donde l.completa == false`). Exige que no se hayan producido omisiones por archivos Markdown que superen el límite de 2 MiB, enlaces simbólicos externos, bytes nulos o codificación no UTF-8.
   - **Qué NO prueba**: no prueba que el extractor sea correcto ni amplía su alcance a texto no Markdown, URLs remotas o anclas.

4. **`seguimiento.ningun_commit_nombra_una_tarea_inexistente`**:
   - **Qué comprueba**: que todo commit cuyo asunto empieza con un ID nombre una tarea que existe
     (`donde c.nombra_tarea == true y c.tarea_existe == false`). El ID es la única forma de ir del
     cambio a su razón; si no resuelve, el mensaje afirma algo que nadie puede comprobar.
   - **Qué NO prueba**: no comprueba que el trabajo del commit tenga que ver con esa tarea, ni dice
     nada de los commits que no nombran ninguna: la convención es posterior a la historia del
     proyecto y hacerla obligatoria hacia atrás pondría en rojo todo lo anterior.

5. **`seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre`**:
   - **Qué comprueba**: que ninguna tarea `CERRADA` se haya quedado sin su `<ID>: done`
     (se expresa con anti-junta `sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true`). Cerrar editando el
     documento y no commitear el cierre deja el estado sin punto en el árbol.
   - **Qué NO prueba**: no comprueba que el cierre fuera correcto ni que el trabajo estuviera hecho.
     Una tarea cerrada antes de que la convención existiera cuenta igual, que es deuda declarada y
     no un falso rojo: se tapa con una sombra con `cota`, como hace el propio Oracle.

6. **`seguimiento.ningun_cierre_deja_la_tarea_abierta`**:
   - **Qué comprueba**: que ningún commit que dice `done` apunte a una tarea que hoy sigue abierta
     (`donde c.es_cierre == true y c.tarea_existe == true y c.estado_de_la_tarea != "CERRADA"`). O el
     cierre no se guardó, o alguien la reabrió sin decirlo en un commit.
   - **Qué NO prueba**: el tracker no guarda historia de estados, así que una tarea cerrada y
     reabierta a propósito aparece acá y hay que declararla.

Para restringir la evaluación a una política específica:

```bash
oracle juzgar --proyecto ejemplo/seguimiento-tareas --con hechos.json --medida seguimiento.referencias_locales_presentes
```

### Lenguaje de consultas de tareas (TQL)

El comando `oracle tarea listar` admite una expresión posicional de consulta en lenguaje TQL (Task Query Language) con vocabulario en español para filtrar tareas de forma expresiva:

```bash
oracle tarea listar ":bug y prioridad mayor 50"
oracle tarea listar "no :ui o [:backend y prioridad desde 70]"
```

#### Vocabulario y operadores

1. **Etiquetas**: `:etiqueta` evalúa si la tarea posee la etiqueta indicada. La comparación es insensible a mayúsculas y minúsculas (`:bug` coincide con `bug` y con `Bug`).
2. **Palabras clave primarias**:
   - `cualquiera`: coincide con cualquier tarea (siempre verdadero). Una consulta vacía equivale a `cualquiera`.
   - `etiquetada`: verdadero si la tarea posee al menos una etiqueta declarada.
   - `prioridad`: evalúa al valor entero de prioridad de la tarea.
3. **Identificador exacto**: un ID canónico de tarea (`YYYYMMDD-HHMMSS[-slug]`) coincide únicamente con la tarea que posea ese identificador.
4. **Constantes enteras**: enteros con signo opcional (`50`, `+10`, `-5`).
5. **Comparadores de enteros**:
   - `menor`: estrictamente menor.
   - `hasta`: menor o igual.
   - `mayor`: estrictamente mayor.
   - `desde`: mayor o igual.
   - `igual`: igualdad de enteros.
   - `distinto`: desigualdad de enteros.
   - No hay formas simbólicas (`<`, `>`…): en la shell `<` y `>` redirigen, que es por lo que tatr
     tampoco las usa. `prioridad < 50` es un error de código 2.
6. **Operadores lógicos**:
   - `no <primaria>`: negación booleana de la expresión primaria siguiente.
   - `<izq> y <der>`: conjunción lógica (ambas condiciones deben ser verdaderas).
   - `<izq> o <der>`: disyunción lógica (al menos una condición verdadera).
7. **Agrupamiento**: corchetes `[ consulta ]` para delimitar subexpresiones y alterar la precedencia asociativa.

#### Precedencia de operadores

De mayor a menor precedencia:
1. Primarias: `:etiqueta`, `cualquiera`, `etiquetada`, `prioridad`, enteros, IDs, `[ ... ]` y `no <primaria>`.
2. Comparaciones relacionales: `menor`, `hasta`, `mayor`, `desde`, `igual`, `distinto`.
3. Conjunción: `y` (asociativa por izquierda).
4. Disyunción: `o` (asociativa por izquierda).

#### Sistema de tipos estático en compilación

TQL valida estáticamente los tipos en tiempo de compilación antes de evaluar cualquier tarea en disco:
- Existen dos tipos semánticos: `booleano` y `entero`.
- La raíz de toda consulta ejecutable debe ser estrictamente de tipo `booleano`. Expresiones como `prioridad`, `50` o enteros solos son rechazadas en compilación con código 2.
- Los operadores relacionales exigen operandos enteros a ambos lados y producen un resultado booleano.
- Los conectores lógicos (`o`, `y`, `no`) exigen operandos booleanos y producen un booleano.
- Si una expresión contiene tipos incompatibles (por ejemplo `:bug y prioridad`), la compilación falla informando el desajuste de tipos con código 2.

#### Diagnóstico visual de errores (código 2)

Ante un error léxico, sintáctico o de tipos, el compilador emite un mensaje de error en 3 líneas a `stderr` y finaliza con código 2:
```text
:bug y menor 5
       ^
ERROR: se esperaba una expresión entera antes de «menor»
```
El puntero `^` se alinea exactamente con la columna del token conflictivo (contando caracteres Unicode, no bytes).

#### Explicación de consultas (`--explicar`)

La opción `--explicar` en `oracle tarea listar` compila la consulta, imprime en `stdout` la secuencia de tokens y la representación textual del árbol sintáctico compilado, y finaliza exitosamente con código 0:
```bash
oracle tarea listar ":bug y prioridad mayor 50" --explicar
```
No requiere la existencia del directorio `tareas/` ni la presencia de un tracker, ni lista tareas.

### Alineación dinámica en listados

El comando `oracle tarea listar` (o su alias `ls`) calcula dinámicamente el ancho de cada columna en función del contenido real de las tareas a mostrar:
- Las columnas de identificador, estado, prioridad y etiquetas se ajustan para que las tareas con sufijos largos o múltiples etiquetas no desfasen las líneas ni queden desalineadas.
- La última columna visible de cada línea no agrega espacios en blanco sobrantes al final (`trailing whitespace`).
- Si una tarea carece de etiquetas, la columna correspondiente se muestra vacía respetando el espaciado entre columnas.

### Catálogo de etiquetas (`tareas/etiquetas`)

El tracker admite un catálogo opcional de etiquetas y sus descripciones ubicado directamente en `tareas/etiquetas`.

- **Formato por línea**: `<etiqueta>[espacios o comas]<descripción>`
  - Ejemplo con espacio: `bug Defectos detectados en ejecución`
  - Ejemplo con comas: `sensor, Mediciones y telemetría de hardware`
  - La descripción es opcional (puede estar vacía). Cada línea no vacía define una etiqueta (no hay líneas de comentario; una línea que empiece con `#` define una etiqueta `#algo`).
- **Codificación y límites**: debe ser texto codificado estrictamente en UTF-8 y no superar los 2 MiB.
- **Enlaces simbólicos**: no se admiten. Si `tareas/etiquetas` es un symlink, `oracle tarea revisar` falla con código 1; `oracle tarea resumen` emite un aviso por `stderr`, finaliza con código 0 y omite las descripciones.
- **Tratamiento de redefiniciones**:
  - En `oracle tarea revisar`: una etiqueta redefinida en múltiples líneas se considera un defecto de integridad y aborta con código 1 emitiendo el mensaje `etiquetas:<línea>: etiqueta «...» redefinida`.
  - En `oracle tarea resumen`: ante redefiniciones sucesivas, la última definición prevalece para documentar la etiqueta y la ejecución finaliza con código 0, emitiendo una advertencia a `stderr` (`AVISO: etiquetas:<línea>: etiqueta «...» redefinida (usando última definición)`).
- **Integración con resumen**: `oracle tarea resumen` incorpora las descripciones en su reporte legible y en su salida estructurada `--json` (campo `descripciones`), reportando además el recuento de tareas `sin_etiquetas`.

### Operaciones de etiquetado (`etiquetar` y `desetiquetar`)

Los comandos `etiquetar` y `desetiquetar` permiten gestionar etiquetas sobre tareas existentes sin edición manual:

- **Sintaxis**:
  - `oracle tarea etiquetar <id>... --etiqueta <etiq>... [--json] [--proyecto RUTA]`
  - `oracle tarea desetiquetar [<id>...] --etiqueta <etiq>... [--consulta <tql>] [--cerradas] [--todas] [--json] [--proyecto RUTA]`
- **Validación previa estricta**: antes de aplicar cualquier modificación en disco, se audita el árbol completo del tracker (`auditar_tareas`). Si se detecta alguna tarea corrupta, malformada o fuera de confinamiento, la operación se interrumpe inmediatamente con código 1 sin alterar ningún archivo.
- **Selección masiva y exclusión**: `desetiquetar` permite seleccionar tareas por estado (`--cerradas` para todas las tareas cerradas, o `--todas` para el universo completo de tareas abiertas y cerradas) o mediante una consulta TQL con `--consulta <tql>`. Es incompatible especificar IDs explícitos junto con banderas de estado masivo (`--cerradas`, `--todas`) o con `--consulta` (falla con código 2).
- **Desetiquetado por consulta TQL**: con `--consulta <tql>`, el predicado se compila previamente. Si la consulta contiene errores sintácticos o de tipos, el proceso finaliza con código 2 sin modificar ningún archivo. Solo se quitan las etiquetas indicadas de aquellas tareas que satisfagan la expresión y respeten el filtro de estado (por defecto, tareas abiertas).
- **Preservación y atomicidad**:
  - La actualización se realiza mediante reemplazo atómico (`os.replace` tras escritura en archivo temporal contiguo).
  - Se preservan byte a byte las terminaciones de línea originales (`\r\n` o `\n`), los campos desconocidos o personalizados y todo el cuerpo Markdown posterior a los metadatos.
  - Si el documento carecía de la línea `- ETIQUETAS:`, se inserta automáticamente al final del bloque de metadatos. Si se retiran todas las etiquetas, se preserva la clave vacía como `- ETIQUETAS: ` (con espacio final, idéntica a la plantilla de creación de `nueva`).
- **Idempotencia**: si las etiquetas indicadas ya estaban presentes (al etiquetar) o ausentes (al desetiquetar), el archivo no se reescribe innecesariamente en disco.
- **Salida estilo compilador**: cada modificación se reporta por `stdout` en formato estándar `ruta:línea: mensaje` (o un objeto estructurado si se especifica `--json`), facilitando su uso desde scripts, editores y herramientas de integración.

### Grafo de referencias entre tareas (`grafo`)

El comando `oracle tarea grafo [--json] [--proyecto RUTA]` construye el grafo dirigido de referencias existentes entre las tareas del tracker:

- **Construcción y detección**:
  - Analiza el texto de todas las tareas (abiertas y cerradas).
  - Una tarea A referencia a una tarea B si el ID canónico de B aparece en el contenido de A (fuera de su propio directorio).
  - **Frontera de tokens**: la detección utiliza expresiones regulares con delimitación estricta de palabra (`(?<![A-Za-z0-9_-])ID(?![A-Za-z0-9_-])`), evitando que un identificador corto coincida falsamente con prefijos de identificadores derivados (por ejemplo, `...-sensor` no empareja con `...-sensor-2`).
- **Topología del grafo**:
  - Se descartan auto-aristas (una tarea que menciona su propio ID en su cuerpo) y aristas duplicadas.
  - El grafo contiene únicamente nodos con grado mayor a cero (tareas que referencian o son referenciadas). Si no existen referencias entre tareas, se emite un grafo vacío válido.
  - El orden de nodos y aristas en la salida es determinista (alfabético por ID).
- **Formatos de salida**:
  - Formato DOT (por defecto): especificación estándar para Graphviz apta para su consumo directo por tuberías:
    ```bash
    oracle tarea grafo | dot -Tsvg -o grafo.svg
    ```
    Los títulos de tareas se escapan adecuadamente (barras invertidas y comillas dobles).
  - Formato JSON (`--json`): emite un diccionario con las listas `nodos` (con `id`, `titulo` y `estado`) y `aristas` (con `origen` y `destino`).
- **Diagnóstico y errores**: si el tracker contiene tareas corruptas o no decodificables, la operación emite diagnóstico a `stderr` y finaliza con código 1 sin generar grafo.

### Tutorial del ciclo completo (P1 + P2 + P3)

Con Oracle instalado y Git disponible, este recorrido crea un proyecto temporal y un registro
de texto construido. Conservá el ID que devuelve `nueva`: lo reutilizan los pasos siguientes.
El subshell mantiene el directorio de tu terminal y deja el proyecto temporal disponible para inspección.

```bash
(
proyecto_prueba="$(mktemp -d)"
cd "$proyecto_prueba"
oracle tarea init --proyecto .

# 1. Crear una tarea y conservar su ID real
id_tarea="$(oracle tarea nueva "Desincronización de eventos en sensor" \
  --etiqueta bug --etiqueta sensor --sufijo sinc --json --proyecto . \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')"

# 2. Guardar una URL construida con una marca; no se descarga el video
oracle tarea anotar "$id_tarea" "Ejemplo de nota sobre monotonic clock" \
  --url "https://youtube.com/watch?v=ejemplo&t=150s" \
  --marca "02:30" --proyecto .

# 3. Crear un registro construido y adjuntarlo
printf 'Registro construido para practicar adjuntos.\n' > registro-ejemplo.txt
oracle tarea adjuntar "$id_tarea" registro-ejemplo.txt --proyecto .

# 4. Buscar términos en todas las tareas y notas del tracker
oracle tarea buscar "monotonic clock" --proyecto .

# 5. Crear una mención externa y reencontrarla por el ID
printf 'Investigación relacionada: %s\n' "$id_tarea" > referencias.md
oracle tarea referencias "$id_tarea" --proyecto .

# 6. Ver el resumen global de estados y etiquetas
oracle tarea resumen --proyecto .

# 7. Diagnosticar Git: este proyecto temporal todavía no tiene repositorio
oracle tarea seguimiento --proyecto .

# 8. Extraer hechos; el JSON declara sin_repositorio
oracle tarea hechos --git --proyecto . > hechos-tareas.json

# 9. Cerrar la tarea al finalizar
oracle tarea cerrar "$id_tarea" --proyecto .
oracle tarea listar --cerradas --proyecto .
printf 'Proyecto de práctica: %s\n' "$proyecto_prueba"
)
```

Para usar una captura real, reemplazá `registro-ejemplo.txt` por un archivo existente.
El archivo JSON queda dentro del directorio temporal del proyecto de práctica (`$proyecto_prueba/hechos-tareas.json`); juzgalo con:
```bash
oracle juzgar --proyecto ejemplo/seguimiento-tareas --con "$proyecto_prueba/hechos-tareas.json"
```
La política de archivos confirmados fallará hasta que haya un repositorio con esos archivos
confirmados en HEAD y sin cambios pendientes. El tutorial no hace commits.

Las opciones `--cerradas` y `--todas` de `listar` son incompatibles, al igual que `--ruta` y
`--json` de `ver`; combinarlas devuelve código 1.

La auditoría admite `README.md`, `README`, `.gitignore` y `etiquetas` como archivos auxiliares
directamente en `tareas/`. Otros archivos sueltos en esa raíz se diagnostican como anomalías. Guardá las
capturas, notas y demás adjuntos dentro de la carpeta de su tarea.

### Orden en los listados

Por defecto, las tareas se listan ordenadas según:
1. `PRIORIDAD` en orden descendente (mayor número primero).
2. `ID` en orden ascendente (desempate cronológico y alfabético estable).

Modificadores de orden:
- `--por-id`: descarta el ordenamiento por prioridad y ordena exclusivamente por `ID` en orden descendente (las tareas más recientes primero).
- `--invertir`: invierte el orden del listado final resultante (por defecto: menor prioridad primero, desempate ID descendente; combinado con `--por-id`: ID en orden ascendente).

### Reglas de diagnóstico y códigos de salida

- **Código 0 (éxito)**:
  - Operación completada satisfactoriamente.
  - En `listar`: cuando no hay tareas que coincidan con los filtros (cero resultados es un listado vacío exitoso).
  - En `listar --explicar`: muestra la consulta TQL compilada y finaliza con éxito sin consultar el tracker.
  - En consultas de ayuda (`--help` / `-h`): muestra la documentación sin realizar escrituras ni inicializaciones.
- **Código 1 (error de dominio u operacional)**:
  - Tarea no encontrada o ID de prefijo ambiguo.
  - Registro roto, corrupto o con codificación inválida (no UTF-8) en `listar`, `ver`, `cerrar`, `reabrir` o `revisar`: no se ocultan errores como si fueran listas vacías; se emite diagnóstico con la ruta del archivo defectuoso.
  - Intento de escape del directorio `tareas/`, enlaces simbólicos inseguros o rutas fuera de confinamiento.
  - Errores del sistema de archivos al acceder o modificar documentos.
- **Código 2 (error de sintaxis en CLI / argumentos o consulta inválida)**:
  - Banderas u opciones no reconocidas (por ejemplo `oracle tarea listar --inventada`).
  - Argumentos requeridos ausentes o valores de opciones faltantes detectados por el analizador de argumentos (`argparse`).
  - Expresión de consulta TQL sintáctica o semánticamente inválida en `listar` o `desetiquetar --consulta`.
  - Invocación de `referencias` sin ID fuera del directorio de una tarea.
  - Combinación incompatible de argumentos (como pasar IDs explícitos junto con `--consulta` en `desetiquetar`).

---

## 6. Ejemplos construidos de referencia

Los siguientes ejemplos son construidos con propósitos de especificación y contrato.

### Ejemplo 1: Tarea mínima

Ubicación: `tareas/20260911-190000-actualizar-documentacion/TAREA.md`

```markdown
# Actualizar documentación de inicio rápido

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: docs

Revisar que el paso de instalación coincida con la versión 0.15.0.
```

### Ejemplo 2: Investigación técnica con referencias

Ubicación: `tareas/20260911-191000-investigar-sensor/TAREA.md`
Archivos adjuntos en la misma carpeta: `captura-error.png`, `fragmento.log`

```markdown
# Investigar desincronización de eventos en el sensor de procesos

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: bug, sensor, investigacion
- IMPACTO: alto

## Síntoma observado

Al procesar trazas concurrentes en el arnés, algunos eventos de inicio
se registran con timestamp posterior al evento de fin.

Ver captura del analizador: ![Captura de error](captura-error.png)

## Referencias y evidencia local

- Registro de ejecución: [fragmento.log](fragmento.log)
- Archivo de configuración: `oracle.json`
- Sospecha: temporizador monotonic vs clock_gettime en Python 3.11.
```

### Ejemplo 3: Nota de base de conocimiento (KB)

Ubicación: `tareas/20260911-192000-kb-aislamiento-de-tests/TAREA.md`

```markdown
# KB: Por qué `test_herramientas` requiere aislar la generación de bytecode

- ESTADO: ABIERTA
- PRIORIDAD: 20
- ETIQUETAS: kb, arquitectura, tests
- TIPO: nota-permanente

## Contexto

Cuando se ejecutan tests que mutan o reescriben archivos en el árbol, la
escritura de archivos `.pyc` en `__pycache__` puede dejar artefactos residuales
no versionados o competir entre procesos concurrentes.

Para evitar contaminar el árbol de trabajo y aislar las ejecuciones:
1. Usar siempre `python3 -B` para evitar escribir archivos de bytecode.
2. Las pruebas de integración que ejecutan subprocesos deben pasar `PYTHONDONTWRITEBYTECODE=1`.
3. Si existen cachés previas en disco, deben limpiarse antes de correr mutaciones.

Esta nota permanece abierta para referencia continua del equipo.
```

---

## 7. Diferencias con tatr

- **Nombres en español**: CLI, verbos y metadatos usan identificadores en español (`nueva`, `listar`, `ESTADO`, `PRIORIDAD`, `ETIQUETAS`).
- **Nombres de archivo y campos incompatibles**: tatr usa `TASK.md`, `STATUS` (`OPEN`/`CLOSED`), `PRIORITY` y `TAGS`; Oracle usa `TAREA.md`, `ESTADO` (`ABIERTA`/`CERRADA`), `PRIORIDAD` y `ETIQUETAS`.
- **Separación de etiquetas**: tatr separa etiquetas por comas y espacios; Oracle sólo por comas, por lo que `hola mundo` es una única etiqueta en `TAREA.md` y no se puede describir en `tareas/etiquetas`, donde el primer espacio separa la etiqueta de su descripción.
- **Propiedades duplicadas**: en tatr gana la última; en Oracle una propiedad duplicada o un estado no reconocido invalida la tarea.
- **Lenguaje de consultas TQL**: TQL deja de ser una diferencia de alcance y pasa a ser una diferencia de vocabulario y rigor semántico. Oracle implementa un lenguaje de consultas nativo con vocabulario en español, etiquetas insensibles a mayúsculas/minúsculas y verificación estática de tipos en tiempo de compilación (rechazando raíces enteras o tipos incompatibles con código 2 antes de consultar el disco):

| Concepto / Operación | tatr (inglés) | Oracle (español) |
|---|---|---|
| Disyunción lógica | `or` | `o` |
| Conjunción lógica | `and` | `y` |
| Negación booleana | `not` | `no` |
| Agrupamiento | `[ ... ]` | `[ ... ]` |
| Menor estricto | `lt` | `menor` |
| Menor o igual | `le` | `hasta` |
| Mayor estricto | `gt` | `mayor` |
| Mayor o igual | `ge` | `desde` |
| Igualdad de enteros | `eq` | `igual` |
| Desigualdad de enteros | `ne` | `distinto` |
| Todas las tareas | `any` | `cualquiera` |
| Tarea con etiquetas | `tagged` | `etiquetada` |
| Prioridad | `priority` | `prioridad` |
| Etiqueta | `:tag` (sensible a mayúsculas) | `:etiqueta` (insensible a mayúsculas) |
| Listado por ID desc. | `tatr ls -id` | `oracle tarea listar --por-id` |
| Invertir orden final | `tatr ls -a` | `oracle tarea listar --invertir` |
| Explicar consulta | `tatr ls -debug` (tokens y opcodes) | `oracle tarea listar --explicar` (tokens y árbol compilado) |
- **Grafo**: `tatr graph` escribe `graph.dot` y llama a `neato` para generar `graph.svg`; `oracle tarea grafo` sólo emite DOT por `stdout`, sin escribir archivos ni invocar Graphviz (`oracle tarea grafo | dot -Tsvg -o grafo.svg`).
- **Captura, adjuntos, Git y hechos relacionales**: Oracle incluye captura con marcas temporales (`anotar`), vinculación de archivos (`adjuntar`), diagnóstico Git (`seguimiento`) y evidencia relacional (`hechos`), ausentes en tatr.
