# Auditoría de comandos `oracle …` y opciones en `docs/` vs implementación (`tools/cli.py` y módulos despachados)

Auditoría realizada sobre todos los archivos `.md` de `docs/` (excluyendo `vault-kb/`), cotejando cada comando `oracle …` y herramienta de soporte contra la CLI de Oracle (`tools/cli.py`) y los módulos a los que despacha (`tools/tareas.py`, `tools/tareas_contexto.py`, `tools/tareas_hechos.py`, `tools/tareas_grafo.py`, `tools/medida.py`, `tools/corpus.py`, `pyproject.toml`, entre otros).

---

## 1. Resumen de discrepancias principales

1. **Invocación rota de `oracle medida probar` en múltiples guías:**
   - En `docs/02-de-cero-a-un-rojo.md:30`, `docs/03-escribir-una-medida.md:108`, `docs/07-conectar-a-un-proyecto-propio.md:82`, `docs/13-primer-valor.md:90` y `docs/tutorial-practico.md:86`, las guías documentan la firma `oracle medida probar <medida> <caso>`.
   - Sin embargo, en la implementación de `tools/cli.py:1211-1217`, el comando exige obligatoriamente la opción `--con "<filas>"` con texto de evidencia relacional inline. Si no se pasa `--con`, la CLI falla inmediatamente con código 1 indicando falta de evidencia.
   - Además, la salida ejemplificada en `docs/07-conectar-a-un-proyecto-propio.md:88-91` no coincide con el formato real emitido por `tools/medida.py:531-542`.

2. **Invenciones masivas en `docs/12-tareas.md`:**
   - La guía documenta 8 subcomandos que **no existen** en `tools/tareas.py` ni en `tools/cli.py`: `paso`, `bloquear`, `balance`, `auditoria` (existe como `revisar`), `siguiente`, `retro`, `exportar`, `importar`.
   - Documenta opciones inexistentes en subcomandos reales:
     - `nueva`: documenta `--bloquea` y `--padre`, pero no existen en `tools/tareas.py:681-704`.
     - `listar`: documenta `--estado`, `--prioridad-min`, `--bloqueada`, `--orden` y `--limite`, que no existen en `tools/tareas.py:769-793`.
     - `cerrar`: documenta `[MOTIVO]` posicional y `--forzar`, pero `tools/tareas.py:990-997` sólo acepta `id` y rechaza cualquier argumento posicional extra o flag no reconocido.
     - `buscar`: documenta `--estado`, inexistente en `tools/tareas_contexto.py:666-675`.
     - `hechos`: documenta `--desde`, `--hasta`, `--autor` y `--formato`, inexistentes en `tools/tareas_hechos.py:891-910`.
     - `grafo`: documenta `--formato` y `--salida`, inexistentes en `tools/tareas_grafo.py:19-26`.
   - Omite 7 subcomandos reales implementados en `tools/tareas.py:1546-1588`: `adjuntar`, `etiquetar`, `desetiquetar`, `referencias`, `resumen`, `seguimiento` y `revisar`.

3. **Uso de scripts internos de desarrollo en vez de comandos oficiales:**
   - `docs/03-escribir-una-medida.md:105-106` y `docs/tutorial-practico.md:110-112` recomiendan invocar `python tools/sintaxis.py --imprimir` y `python tools/sintaxis.py --leer`.
   - El comando canónico oficial es `oracle convertir <archivo>` (`tools/cli.py:61` y `tools/cli.py:695-739`). Como explica el comentario en `tools/cli.py:698-701`, invocar `tools/sintaxis.py` es una práctica obsoleta que requería tener el repositorio clonado y no funcionaba con el paquete instalado vía pip.

4. **Sintaxis desactualizada de umbral en ejemplos prácticos:**
   - En `docs/tutorial-practico.md:71` y `docs/tutorial-practico.md:99`, se muestra `umbral <= 0 porque "..."` omitiendo la cláusula obligatoria `segun <fuente>` exigida desde la versión 0.4 del álgebra (`docs/decisiones/DECISION-006-DE-DONDE-SALE-EL-NUMERO.md:8-14` y `nucleo/sintaxis.py`).

5. **Descripción incorrecta del alcance de `oracle escalares`:**
   - En `docs/tutorial-practico.md:780`, se afirma que `oracle escalares` muestra "funciones de dominio, operadores y agregados disponibles".
   - En `tools/cli.py:21`, `tools/cli.py:673-682` y `tools/cli.py:1260`, el comando sólo lista funciones escalares (`nucleo.algebra.ESCALARES` y las registradas en `escalares.py`). Los operadores de tubería y agregados corresponden al manual (`oracle manual operadores`, `tools/cli.py:53`).

---

## 2. Detalle archivo por archivo de `docs/`

### 2.1. `docs/README.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle corpus validar <dir-del-corpus>` | `docs/README.md:121` | `tools/cli.py:12`, `tools/cli.py:519` | Coincide | Subcomando canónico implementado. |
| `oracle medida compilar <dir-o-archivo>` | `docs/README.md:122` | `tools/cli.py:16`, `tools/cli.py:541` | Coincide | Subcomando canónico implementado. |
| `oracle corpus medir <dir-del-corpus>` | `docs/README.md:123`, `:233` | `tools/cli.py:13`, `tools/cli.py:488` | Coincide | Subcomando canónico implementado. |
| `oracle mutar <dir-del-corpus>` / `corpus/` | `docs/README.md:124`, `:170`, `:240` | `tools/cli.py:22`, `tools/cli.py:688` | Coincide | Subcomando canónico implementado. |
| `oracle diferencial <dir-del-corpus>` | `docs/README.md:125` | `tools/cli.py:23`, `tools/cli.py:689` | Coincide | Subcomando canónico implementado. |
| `oracle inicializar mi-proyecto` | `docs/README.md:219` | `tools/cli.py:11`, `tools/cli.py:1257` | Coincide | `inicializar` es alias reconocido de `init`. |
| `oracle medida compilar medidas/` | `docs/README.md:225` | `tools/cli.py:16`, `tools/cli.py:541` | Coincide | Compilación de directorio soportada. |

---

### 2.2. `docs/02-de-cero-a-un-rojo.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle init <directorio>` / `mi-proyecto` | `docs/02-de-cero-a-un-rojo.md:10`, `:44` | `tools/cli.py:11`, `tools/cli.py:557` | Coincide | Comando canónico de inicialización. |
| `oracle medida nueva <grupo/id>` | `docs/02-de-cero-a-un-rojo.md:14`, `:71` | `tools/cli.py:15`, `tools/cli.py:530` | Coincide | Crea plantilla `.oracle`. |
| `oracle medida compilar <ruta>` / `medidas/` | `docs/02-de-cero-a-un-rojo.md:18`, `:106` | `tools/cli.py:16`, `tools/cli.py:541` | Coincide | Compila a `.json`. |
| `oracle caso nuevo <grupo/id>` | `docs/02-de-cero-a-un-rojo.md:22`, `:127` | `tools/cli.py:17`, `tools/cli.py:552` | Coincide | Crea plantilla de caso `.json`. |
| `oracle corpus validar <ruta>` / `corpus/` | `docs/02-de-cero-a-un-rojo.md:26`, `:158` | `tools/cli.py:12`, `tools/cli.py:519` | Coincide | Valida formato y esquema de casos. |
| `oracle medida probar <medida> <caso>` | `docs/02-de-cero-a-un-rojo.md:30`, `:177` | `tools/cli.py:1207-1224` | **Falla / Incompatible** | La CLI **exige obligatoriamente** `--con "<filas>"` (`tools/cli.py:1211`). La sintaxis posicional con un archivo de caso no está soportada por el router y produce error: `falta la evidencia. Se escribe igual que en un caso del corpus: oracle medida probar <archivo> --con ...`. |
| `oracle corpus medir <ruta>` / `corpus/` | `docs/02-de-cero-a-un-rojo.md:34`, `:203` | `tools/cli.py:13`, `tools/cli.py:488` | Coincide | Ejecuta evaluación del corpus. |
| `oracle caso proceso/001-aprobacion-huerfana` | `docs/02-de-cero-a-un-rojo.md:149` | `tools/cli.py:1250` | Coincide (atajo) | Resuelto en el router al contener `/` o coincidir con `ID_CASO_RE`. |

---

### 2.3. `docs/03-escribir-una-medida.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle caso proceso/002-aprobacion-valida` | `docs/03-escribir-una-medida.md:60` | `tools/cli.py:1250` | Coincide (atajo) | Despacha a `cmd_caso_nuevo` por contener `/`. |
| `oracle corpus medir corpus/` | `docs/03-escribir-una-medida.md:85` | `tools/cli.py:13`, `tools/cli.py:488` | Coincide | Evaluación estándar. |
| `oracle caso proceso/0NN-nombre` | `docs/03-escribir-una-medida.md:103` | `tools/cli.py:1250` | Coincide (atajo) | Atajo para nuevo caso. |
| `python tools/sintaxis.py --imprimir <archivo.json>` | `docs/03-escribir-una-medida.md:105` | `tools/cli.py:61`, `tools/cli.py:695-739` | **Obsoleto / Reemplazado** | Invoca un script interno del árbol. El comando canónico oficial de la CLI es `oracle convertir <archivo>` (`tools/cli.py:695`). |
| `python tools/sintaxis.py --leer <archivo.oracle>` | `docs/03-escribir-una-medida.md:106` | `tools/cli.py:61`, `tools/cli.py:695-739` | **Obsoleto / Reemplazado** | Invoca script interno. El comando canónico oficial es `oracle convertir <archivo>`. |
| `oracle medida compilar <ruta>` | `docs/03-escribir-una-medida.md:107` | `tools/cli.py:16`, `tools/cli.py:541` | Coincide | Compila `.oracle` a `.json`. |
| `oracle medida probar <medida> <caso>` | `docs/03-escribir-una-medida.md:108` | `tools/cli.py:1207-1224` | **Falla / Incompatible** | La CLI requiere `--con "<filas>"` y rechaza esta sintaxis posicional. |

---

### 2.4. `docs/05-por-que-la-mutacion.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle mutar corpus/` | `docs/05-por-que-la-mutacion.md:158` | `tools/cli.py:22`, `tools/cli.py:688` | Coincide | Ejecuta mutación sobre el corpus. |

---

### 2.5. `docs/07-conectar-a-un-proyecto-propio.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle init mi-sistema` | `docs/07-conectar-a-un-proyecto-propio.md:13` | `tools/cli.py:11`, `tools/cli.py:557` | Coincide | Inicializa estructura base. |
| `oracle medida nueva inventario/001-sin-stock-negativo` | `docs/07-conectar-a-un-proyecto-propio.md:70` | `tools/cli.py:15`, `tools/cli.py:530` | Coincide | Crea medida en la carpeta del dominio. |
| `oracle medida probar ... ...` | `docs/07-conectar-a-un-proyecto-propio.md:82` | `tools/cli.py:1207-1224` | **Falla / Incompatible** | Invoca `oracle medida probar <medida> <caso.json>` sin flag `--con`. La CLI falla con error y código 1. |
| Salida ejemplificada de `oracle medida probar` | `docs/07-conectar-a-un-proyecto-propio.md:88-91` | `tools/medida.py:531-542` | **Discrepancia de salida** | La guía muestra:<br>`ROJO: se esperaban 0 pero se encontraron 1`<br>`Testigos:`<br>`  {'d': {'nombre': 'Widget A', ...}}`<br>El código real emite:<br>`ROJO   valor 1  (<= 0)`<br>`  testigos (1) — las filas que ofenden, no un resumen:`<br>`    {'sku': 'W-001', ...}`<br>`  alcance: ...` |

---

### 2.6. `docs/12-tareas.md`

Este documento concentra el mayor volumen de discrepancias de toda la documentación:

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle tarea init [ruta] [--sin-readme]` | `docs/12-tareas.md:40`, `:105` | `tools/tareas.py:607-624` vs `tools/cli.py:29` | Coincide en módulo, omitido en ayuda CLI | `tools/tareas.py:620` implementa `--sin-readme`, pero la ayuda general de la CLI en `tools/cli.py:29` sólo lista `oracle tarea init [RUTA]`. |
| `oracle tarea nueva ... --prioridad 80 --sufijo salida-error` | `docs/12-tareas.md:36`, `:106` | `tools/tareas.py:681-704` | Coincide | Argumentos soportados por `cmd_nueva`. |
| `oracle tarea nueva ... --bloquea <id>` | `docs/12-tareas.md:303` | `tools/tareas.py:681-704` | **Inexistente** | `cmd_nueva` no define `--bloquea`. Falla con argumento no reconocido. |
| `oracle tarea nueva ... --padre <id>` | `docs/12-tareas.md:305` | `tools/tareas.py:681-704` | **Inexistente** | `cmd_nueva` no define `--padre`. Falla con argumento no reconocido. |
| `oracle tarea listar` | `docs/12-tareas.md:44`, `:107` | `tools/tareas.py:769-793` | Coincide (básico) | Lista tareas abiertas ordenadas por prioridad. |
| `oracle tarea listar --estado ESTADO` | `docs/12-tareas.md:107` | `tools/tareas.py:774-775`, `:835` | **Inexistente** | No existe `--estado`. El filtrado por estado usa `--cerradas`, `--todas` o una consulta TQL `estado = "..."`. |
| `oracle tarea listar --prioridad-min N` | `docs/12-tareas.md:107` | `tools/tareas.py:769-793` | **Inexistente** | No existe `--prioridad-min`. Se realiza mediante consulta TQL `prioridad >= N`. |
| `oracle tarea listar --bloqueada` | `docs/12-tareas.md:107` | `tools/tareas.py:769-793` | **Inexistente** | No existe flag `--bloqueada`. |
| `oracle tarea listar --texto TEXTO` | `docs/12-tareas.md:107` | `tools/tareas.py:778` | Coincide | Soportado mediante `--texto/-t`. |
| `oracle tarea listar --orden ORDEN` | `docs/12-tareas.md:107` | `tools/tareas.py:781-785` | **Inexistente** | No existe `--orden`. Las opciones reales son `--por-id` e `--invertir`. |
| `oracle tarea listar --limite N` | `docs/12-tareas.md:107` | `tools/tareas.py:769-793` | **Inexistente** | No existe opción `--limite`. |
| `oracle tarea ver salida-error` | `docs/12-tareas.md:48`, `:109` | `tools/tareas.py:937-987` | Coincide | Muestra metadatos y cuerpo. |
| `oracle tarea anotar salida-error "..."` | `docs/12-tareas.md:52`, `:110` | `tools/tareas_contexto.py:236-251` | Coincide | Añade nota a `TAREA.md`. |
| `oracle tarea paso salida-error "..."` | `docs/12-tareas.md:56`, `:111` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando inexistente. La actualización de `## Próximo paso` se hace editando `TAREA.md` directamente. |
| `oracle tarea cerrar salida-error "Motivo..."` | `docs/12-tareas.md:60`, `:112` | `tools/tareas.py:990-997` | **Incompatible** | `cmd_cerrar` sólo acepta el argumento posicional `id` (y `--proyecto`). No acepta un segundo argumento de motivo. Falla con `error: unrecognized arguments`. |
| `oracle tarea cerrar ID --forzar` | `docs/12-tareas.md:112` | `tools/tareas.py:990-997` | **Inexistente** | `cmd_cerrar` no define `--forzar`. |
| `oracle tarea bloquear salida-error "..."` | `docs/12-tareas.md:64`, `:113` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando inexistente. |
| `oracle tarea reabrir salida-error` | `docs/12-tareas.md:68`, `:114` | `tools/tareas.py:1036-1079` | Coincide | Marca tarea como ABIERTA. |
| `oracle tarea buscar "..."` | `docs/12-tareas.md:72`, `:115`, `:648` | `tools/tareas_contexto.py:666-675` | Coincide | Busca texto en tareas y notas. |
| `oracle tarea buscar TEXTO --estado ESTADO` | `docs/12-tareas.md:115` | `tools/tareas_contexto.py:666-675` | **Inexistente** | `cmd_buscar` busca texto plano recursivamente y no admite `--estado`. |
| `oracle tarea balance [--dias N]` | `docs/12-tareas.md:76`, `:119`, `:654` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando completamente inexistente. |
| `oracle tarea auditoria [--corregir]` | `docs/12-tareas.md:80`, `:120` | `tools/tareas.py:1082-1090`, `tools/cli.py:32` | **Inexistente / Nombre incorrecto** | `auditoria` no existe. El subcomando real es `oracle tarea revisar [--json] [--proyecto RUTA]`. La opción `--corregir` no existe. |
| `oracle tarea hechos` | `docs/12-tareas.md:84`, `:118`, `:180`, `:287`, `:506` | `tools/tareas_hechos.py:891-910` | Coincide en base | Emite hechos relacionales JSON. Admite `--git`, `--json`, `--proyecto`. |
| `oracle tarea hechos [--desde] [--hasta] [--autor] [--formato]` | `docs/12-tareas.md:118` | `tools/tareas_hechos.py:891-910` | **Inexistente** | Ninguna de esas 4 opciones existe en el código. La salida siempre es JSON relacional bajo el esquema `oracle.tareas.hechos/v1`. |
| `oracle tarea grafo` | `docs/12-tareas.md:88`, `:121`, `:460`, `:661` | `tools/tareas_grafo.py:19-26` | Coincide en base | Emite DOT a stdout. Admite pipe `\| dot -Tsvg -o grafo.svg` y flag `--json`. |
| `oracle tarea grafo [--formato FORMATO] [--salida ARCHIVO]` | `docs/12-tareas.md:121` | `tools/tareas_grafo.py:24-26` | **Inexistente** | `cmd_grafo` sólo define `--json` y `--proyecto`. No tiene `--formato` ni `--salida`. |
| `oracle tarea siguiente` | `docs/12-tareas.md:92`, `:667` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando inexistente. |
| `oracle tarea retro [--periodo PERIODO]` | `docs/12-tareas.md:96`, `:122`, `:673` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando inexistente. |
| `oracle tarea exportar [RUTA] [--formato FORMATO]` | `docs/12-tareas.md:123` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando inexistente. |
| `oracle tarea importar RUTA [--formato FORMATO]` | `docs/12-tareas.md:124` | `tools/tareas.py:1546-1590`, `tools/cli.py:28-45` | **Inexistente** | Subcomando inexistente. |
| *(Omitidos en la guía)* Comandos reales de `oracle tarea` | No mencionados en `docs/12-tareas.md` | `tools/tareas.py:1560-1585`, `tools/cli.py:28-45` | **Omitidos** | La guía no menciona los subcomandos existentes: `adjuntar`, `revisar`, `etiquetar`, `desetiquetar`, `referencias`, `resumen`, `seguimiento`. |

---

### 2.7. `docs/13-primer-valor.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle init mi-proyecto` | `docs/13-primer-valor.md:17` | `tools/cli.py:11`, `tools/cli.py:557` | Coincide | Inicialización estándar. |
| `oracle proyecto validar` | `docs/13-primer-valor.md:24` | `tools/cli.py:19`, `tools/cli.py:687` | Coincide | Valida consistencia estructural del proyecto. |
| `oracle medida nueva proceso/001-sin-aprobacion-huerfana` | `docs/13-primer-valor.md:33` | `tools/cli.py:15`, `tools/cli.py:530` | Coincide | Creación de medida. |
| `oracle medida compilar medidas/` | `docs/13-primer-valor.md:60` | `tools/cli.py:16`, `tools/cli.py:541` | Coincide | Compilación de medidas. |
| `oracle caso nuevo proceso/001-aprobacion-huerfana` | `docs/13-primer-valor.md:70` | `tools/cli.py:17`, `tools/cli.py:552` | Coincide | Creación de caso. |
| `oracle medida probar ... ...` | `docs/13-primer-valor.md:90` | `tools/cli.py:1207-1224` | **Falla / Incompatible** | Invoca con 2 rutas posicionales sin `--con`. La CLI falla exigiendo evidencia. |
| `oracle corpus medir corpus/` | `docs/13-primer-valor.md:99` | `tools/cli.py:13`, `tools/cli.py:488` | Coincide | Evaluación estándar. |

---

### 2.8. `docs/14-sensor-prosa.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle corpus medir corpus/` | `docs/14-sensor-prosa.md:99` | `tools/cli.py:13`, `tools/cli.py:488` | Coincide | Evaluación estándar. |

---

### 2.9. `docs/mutacion-memoria.md`

- No cita comandos `oracle …`. Documenta el diseño y los experimentos de mutación de código en memoria.

---

### 2.10. `docs/mcp-contrato.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle mcp` | `docs/mcp-contrato.md:19` | `tools/cli.py:25`, `tools/cli.py:690` | Coincide | Servidor MCP por stdin/stdout. |
| `oracle mcp --directorio /ruta/al/proyecto` | `docs/mcp-contrato.md:24` | `tools/cli.py:25`, `tools/mcp.py` | Coincide | Opción `--directorio` soportada. |

---

### 2.11. `docs/tutorial-practico.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle init tutorial` / `[directorio]` | `docs/tutorial-practico.md:18`, `:759` | `tools/cli.py:11`, `tools/cli.py:557` | Coincide | Inicialización estándar. |
| `oracle proyecto validar` | `docs/tutorial-practico.md:26`, `:762` | `tools/cli.py:19`, `tools/cli.py:687` | Coincide | Valida proyecto. |
| `oracle caso nuevo ...` | `docs/tutorial-practico.md:39`, `:121`, `:771` | `tools/cli.py:17`, `tools/cli.py:552` | Coincide | Creación de caso. |
| `oracle corpus validar ...` | `docs/tutorial-practico.md:52`, `:774` | `tools/cli.py:12`, `tools/cli.py:519` | Coincide | Validación de corpus. |
| `oracle medida nueva ...` | `docs/tutorial-practico.md:60`, `:765` | `tools/cli.py:15`, `tools/cli.py:530` | Coincide | Creación de medida. |
| Sintaxis de umbral `umbral <= 0 porque "..."` | `docs/tutorial-practico.md:71`, `:99` | `nucleo/sintaxis.py`, `docs/decisiones/DECISION-006...:11-12` | **Sintaxis desactualizada** | Omite `segun <fuente>`, obligatorio en el álgebra actual. Debe ser `umbral <= 0 segun contrato porque "..."`. |
| `oracle medida compilar ...` | `docs/tutorial-practico.md:80`, `:768` | `tools/cli.py:16`, `tools/cli.py:541` | Coincide | Compilación de medida. |
| `oracle medida probar <medida> <caso>` | `docs/tutorial-practico.md:86`, `:141`, `:777` | `tools/cli.py:1207-1224` | **Falla / Incompatible** | La CLI requiere `--con` con filas de evidencia; rechaza invocación posicional con caso. |
| `python tools/sintaxis.py --imprimir ...` | `docs/tutorial-practico.md:110` | `tools/cli.py:61`, `tools/cli.py:695-739` | **Obsoleto / Reemplazado** | Invoca script interno. Debe usarse `oracle convertir <archivo>`. |
| `python tools/sintaxis.py --leer ...` | `docs/tutorial-practico.md:112` | `tools/cli.py:61`, `tools/cli.py:695-739` | **Obsoleto / Reemplazado** | Invoca script interno. Debe usarse `oracle convertir <archivo>`. |
| `oracle corpus medir ...` | `docs/tutorial-practico.md:157`, `:783` | `tools/cli.py:13`, `tools/cli.py:488` | Coincide | Evaluación estándar. |
| `oracle escalares` | `docs/tutorial-practico.md:780` | `tools/cli.py:21`, `tools/cli.py:673-682`, `tools/cli.py:1260` | **Discrepancia semántica** | La guía dice: "Funciones de dominio, operadores y agregados disponibles". En realidad sólo lista funciones escalares (`nucleo.algebra.ESCALARES` y `escalares.py`). No lista operadores ni agregados de tubería (se ven en `oracle manual operadores`). |
| `oracle biblioteca listar <ruta>` | `docs/tutorial-practico.md:784` | `tools/cli.py:27`, `tools/cli.py:1177` | Coincide | Lista medidas de una biblioteca instalada. |
| `oracle diagnostico` | `docs/tutorial-practico.md:785` | `tools/cli.py:141`, `tools/cli.py:1298` | Coincide (atajo) | Atajo plano para diagnóstico del entorno. |

---

### 2.12. `docs/migracion/de-subtree-a-pypi.md`, `jam.md`, `lyragasp.md`

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle-medida --proyecto medidas --confiar-escalares --escalares` | `docs/migracion/de-subtree-a-pypi.md:89` | `pyproject.toml:53`, `tools/medida.py:886-895` | Coincide | Entry point instalado y opciones válidas. |
| `oracle-corpus` | `de-subtree-a-pypi.md:126`, `jam.md:135`, `lyragasp.md:97` | `pyproject.toml:48`, `tools/corpus.py:main` | Coincide | Entry point instalado. |
| `oracle-aceptacion` | `de-subtree-a-pypi.md:128`, `jam.md:136`, `lyragasp.md:98` | `pyproject.toml:47`, `tools/aceptacion.py:main` | Coincide | Entry point instalado. |
| `oracle-mutar` | `de-subtree-a-pypi.md:130`, `jam.md:137`, `lyragasp.md:99` | `pyproject.toml:54`, `tools/mutar.py:main` | Coincide | Entry point instalado. |
| `oracle-diferencial` | `de-subtree-a-pypi.md:131`, `jam.md:138`, `lyragasp.md:100` | `pyproject.toml:49`, `tools/diferencial.py:main` | Coincide | Entry point instalado. |

---

### 2.13. `docs/decisiones/` (DECISION-001 a DECISION-012)

| Comando / Opción citada | Guía (`archivo:línea`) | Código (`archivo:línea`) | Estado | Detalle |
|---|---|---|---|---|
| `oracle test` | `DECISION-004...:122` | `tools/cli.py:46`, `tools/cli.py:1269` | Coincide | Atajo canónico de `oracle tests` (`cmd_test`). |
| `oracle biblioteca listar` | `DECISION-007...:60` | `tools/cli.py:27`, `tools/cli.py:1177` | Coincide | Inspecciona medidas y alcances de bibliotecas. |
| `oracle bug preparar` | `DECISION-007...:120` | `tools/cli.py` | **No implementado (citado como propuesta futura)** | El texto aclara que es una propuesta de fase 2 aceptada condicionalmente para cuando haya usuarios externos reportando issues. No está en la CLI. |
| `oracle biblioteca` vs `oracle politica` / `oracle pack` | `DECISION-007...:130` | `tools/cli.py:26-27` | Histórico / Discusión | Discusión de diseño; se adoptó finalmente `oracle biblioteca`. |
