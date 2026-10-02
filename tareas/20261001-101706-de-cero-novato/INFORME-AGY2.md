# Informe de Validación Independiente: Guía «De Cero a Novato» (Oracle Metalenguaje)

**Agente evaluador:** `agy2`
**Fecha de evaluación:** 2026-10-01
**Documento evaluado:** `guia-publicada/de-cero.html` (copia estática publicada)
**Proyecto reconstruido en:** `/tmp/oracle-cierre-novato/agy2/recorrido/batalla-naval`
**Directorio de evidencias:** `/tmp/oracle-cierre-novato/agy2/evidencia/`

---

## 1. Resumen Ejecutivo y Estado Final

Se realizó la validación independiente, exhaustiva y ciega de la guía oficial publicada `de-cero.html`, recorriendo de principio a fin las nueve misiones del tutorial para reconstruir el juego táctico de Batalla Naval con auditoría formal.

- **Estado final del proyecto:** **VERDE** (`VEREDICTO: VERDE (todas las verificaciones aplicables en regla)`).
  - 11 medidas activas en `catalogos/naval/`.
  - 33 casos de prueba en `corpus/naval/`.
  - 209 mutantes evaluados y 100% extinguidos (0 supervivientes).
  - 6 requisitos funcionales con cobertura auditada en `requisitos/`.
  - Juicio sobre partida real (`hechos_partida.json`) con 11/11 medidas en verde.
  - Auditoría diferencial de Git ante relajación de umbrales probada con éxito (`oracle cambios`).
- **Comportamiento general del marco:** Excelente coherencia conceptual, herramientas rápidas y didáctica progresiva sobresaliente.
- **Hallazgos críticos / bloqueos para novatos:**
  1. **Bloqueo generalizado de forma única (salto de línea final):** Todos los bloques HTML `<pre class="archivo">` del sitio carecen del salto de línea final (`\n`). Al copiar y pegar en editores planos que no fuerzan salto final (como Bloc de Notas o VS Code por defecto), `oracle test` falla inmediatamente en el Paso 5 con `VEREDICTO: ROJO (sintaxis: forma única)`, impidiendo ver la salida esperada (`falló: aceptación`).
  2. **Inconsistencia de nombres en script complementario:** En el Paso 9, el script `verificar_oraculo.py` busca `partida_real.json`, pero en el Paso 8 la guía instruyó guardar el archivo como `hechos_partida.json`. Ejecutar el script provoca un `FileNotFoundError` inmediato.
  3. **Rutas intermedias no creadas:** En el Paso 5, la guía asume la existencia de `corpus/naval/` y `catalogos/naval/`, que no son creadas por `oracle init`. A diferencia de `css/`, `js/` y `requisitos/`, en el Paso 5 no hay instrucción explícita de `mkdir`.
  4. **Diferencias de salida en Paso 1 y Paso 5:** Hay discrepancias textuales entre lo que la versión instalada (`oracle 0.38.0`) emite y lo impreso en los recuadros «Lo que tenés que ver».

---

## 2. Alcance y Límites de la Validación

Es imperativo explicitar la naturaleza de esta auditoría para no distorsionar las conclusiones:
1. **Entorno de ejecución:** Linux x86_64, shell Bash, Python 3.14.7, `uv` 0.12.17.
2. **Entorno aislado de herramientas:** `oracle-metalenguaje` se instaló en un entorno completamente aislado dentro del workspace mediante:
   ```bash
   export UV_TOOL_DIR="/tmp/oracle-cierre-novato/agy2/uv-isolated/tools"
   export UV_TOOL_BIN_DIR="/tmp/oracle-cierre-novato/agy2/uv-isolated/bin"
   export UV_CACHE_DIR="/tmp/oracle-cierre-novato/agy2/uv-isolated/cache"
   export PATH="/tmp/oracle-cierre-novato/agy2/uv-isolated/bin:$PATH"
   ```
   No se modificó la variable global `HOME` ni se tocaron dependencias globales del sistema.
3. **Validación visual del juego web:**
   - **Límite:** El entorno de evaluación es una máquina Linux sin servidor gráfico ni pantalla conectada (headless).
   - **Alcance:** No se pudo abrir una ventana física de navegador para ver el renderizado visual de `index.html` ni jugar interactivamente con el ratón.
   - **Verificación alternativa:** Se inspeccionó estáticamente la estructura completa de `index.html`, la hoja de estilos `css/style.css` y los scripts `js/audio.js`, `js/trace.js`, `js/engine.js` y `js/ui.js`. Todos los archivos enlazados coinciden en rutas y referencias de identificadores DOM.
4. **Diferencia entre simulación por IA y principiante humano:**
   - Una inteligencia artificial posee capacidad reflexiva para interpretar volcados de depuración (como `salto de línea final` o `mkdir -p`), diagnosticar la causa raíz y aplicar un formateo o corrección de emergencia para seguir el flujo.
   - Una persona novata real siguiendo la guía en Windows con Bloc de Notas o VS Code se habría quedado totalmente bloqueada en el Paso 5 ante el error de sintaxis inesperado, ya que el recuadro «Lo que tenés que ver» le prometía un fallo de aceptación y no de sintaxis canónica.

---

## 3. Versión Instalada y Configuración

Comando ejecutado:
```bash
uv tool install oracle-metalenguaje
```
Salida obtenida (evidencia en `evidencia/paso0_uv_install.log`):
```text
Resolved 1 package in 456ms
Prepared 1 package in 214ms
Installed 1 package in 6ms
 + oracle-metalenguaje==0.38.0
Installed 9 executables: oracle, oracle-aceptacion, oracle-corpus, oracle-diferencial, oracle-estudio, oracle-lsp, oracle-medida, oracle-mutar, oracle-mutar-codigo
```
Versión reportada:
```text
oracle 0.38.0
  álgebra:  1.0   (qué SIGNIFICA una medida)
  sintaxis: 1.1   (cómo se ESCRIBE)
```

---

## 4. Recorrido Paso a Paso por las Nueve Misiones

### Antes de empezar
- **Texto evaluado:** Explicación de terminal, instalación de Python 3.11+, `uv`, `git` y editores de texto plano.
- **Observaciones:** Excelente claridad pedagógica explicando extensiones ocultas de Windows y advirtiendo contra procesadores de texto enriquecido (Word/WordPad).

### Paso 1 · Preparar la carpeta
- **Comandos ejecutados:**
  ```bash
  oracle init batalla-naval
  cd batalla-naval
  oracle test
  ```
- **Archivo editado:** `oracle.json` (desactivación de `catalogo_base: false`).
- **Evidencia guardada:** `evidencia/paso1_oracle_init.log`, `evidencia/paso1_oracle_test.log`.
- **Discrepancias detectadas:**
  - *Diferencia en salida de `oracle init`:* La guía muestra:
    > `Proyecto Oracle inicializado en batalla-naval:`
    La salida real emite la ruta canónica absoluta:
    > `Proyecto Oracle inicializado en /tmp/oracle-cierre-novato/agy2/recorrido/batalla-naval:`
  - *Agrupación de comandos vs salida:* El bloque para copiar contiene 4 líneas (`uv tool install ...`, `oracle init ...`, `cd batalla-naval`, `oracle test`), pero el bloque de salida esperada solo muestra el resultado de `oracle init` y `oracle test`, omitiendo la salida de instalación de `uv`.

### Paso 2 · El tablero
- **Archivos creados:**
  - `index.html` (9.534 caracteres, raíz de `batalla-naval`).
  - `css/style.css` (19.230 caracteres, dentro de `batalla-naval/css/`).
- **Instrucción de carpetas:** Explícita y correcta: «creá una subcarpeta llamada css».
- **Evaluación:** Todo en orden.

### Paso 3 · El juego
- **Archivos creados:**
  - `js/audio.js`
  - `js/trace.js`
  - `js/engine.js`
  - `js/ui.js`
- **Instrucción de carpetas:** Explícita y correcta: «creá una carpeta nueva llamada js».
- **Estructura de árbol verificada:** Coincidencia exacta con el árbol de directorios publicado en la guía.

### Paso 4 · Que el juego cuente lo que pasó
- **Naturaleza:** Conceptual / formativa.
- **Acciones:** Explicación de la traza de auditoría, las relaciones (`celda_barco`, `tiro`, `partida`) y el botón «⚖ Auditoría & Traza Oracle».
- **Evaluación:** Didáctica impecable, sin comandos a ejecutar.

### Paso 5 · La primera regla, empezando por el caso rojo
- **Archivos creados:**
  - `corpus/naval/005-barco-fila-desbordada.caso`
  - `catalogos/naval/naval.barcos_dentro_del_tablero.oracle`
- **Comandos ejecutados:**
  ```bash
  oracle test
  oracle formatear . --escribir
  oracle test
  ```
- **Evidencia guardada:**
  - `evidencia/paso5_oracle_test_rojo.log` (bloqueo por sintaxis)
  - `evidencia/paso5_oracle_formatear.log`
  - `evidencia/paso5_oracle_test_aceptacion_rojo.log` (salida real tras formatear)
  - `evidencia/paso5_oracle_test_mutacion.log`
- **Hallazgos críticos y discrepancias:**
  1. **Falta de carpeta previa:** `oracle init` crea `corpus/` y `catalogos/`, pero no las subcarpetas `naval/`. La guía dice: *«Adentro de corpus/naval/, creá un archivo nuevo...»* sin advertir que `naval/` debe ser creada primero.
  2. **Bloqueo por falta de salto de línea:** El bloque HTML del caso no incluye salto de línea al final. Al ejecutar el primer `oracle test`, el veredicto fue:
     ```text
     SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
       · corpus/naval/005-barco-fila-desbordada.caso
         @@ salto de línea final @@
         - sin salto final
         + con salto final
     VEREDICTO: ROJO (sintaxis: forma única)
     ```
     La guía decía que debía verse:
     ```text
     VEREDICTO: ROJO (falló: aceptación)
     ```
  3. **Discrepancia de salida en aceptación roja:** Cuando el archivo tiene su salto de línea, la salida de `oracle 0.38.0` difiere en varias líneas respecto a la salida publicada (ver sección 5).
  4. **Diferencia en `oracle formatear`:** La guía prometía que la regla `ya tiene forma única`. En la realidad, como el bloque HTML carecía de `\n`, `oracle formatear` indicó `requiere formato` y procedió a reescribirlo.
  5. **Segunda corrida de `oracle test`:** Coincidencia perfecta al 100% con los 18 mutantes (10 muertos, 8 vivos) y veredicto `ROJO (falló: mutación)`.

### Paso 6 · Un caso rojo no alcanza: la mutación
- **Archivos creados:**
  - `corpus/naval/006-barco-en-borde.caso`
  - `corpus/naval/026-barco-columna-desbordada.caso`
  - `corpus/naval/027-barco-fila-negativa.caso`
  - `corpus/naval/028-barco-columna-negativa.caso`
- **Comandos ejecutados:**
  ```bash
  oracle test
  oracle test
  ```
- **Evidencia guardada:** `evidencia/paso6_oracle_test_1.log`, `evidencia/paso6_oracle_test_2.log`.
- **Resultados:**
  - Primera corrida: 14 mutantes muertos, 4 supervivientes (`ROJO (falló: mutación)`). Coincidencia exacta con la guía.
  - Segunda corrida: 18 mutantes muertos, 0 supervivientes (`VEREDICTO: VERDE (todas las verificaciones aplicables en regla)`). Coincidencia exacta con la guía.

### Paso 7 · Diez reglas más, y la trampa de los pocos casos
- **Archivos creados:**
  - 10 archivos `.oracle` en `catalogos/naval/`.
  - 2 archivos `.caso` iniciales (`001`, `002`) en `corpus/naval/`.
  - 26 archivos `.caso` complementarios en `corpus/naval/`.
- **Comandos ejecutados:**
  ```bash
  oracle test
  oracle test
  ```
- **Evidencia guardada:** `evidencia/paso7_oracle_test_1.log`, `evidencia/paso7_oracle_test_2.log`.
- **Resultados:**
  - Primera corrida: Se detiene con `MEDIDAS SIN CASOS ✗ — 9 medida(s) propias sin ejercitar` y veredicto `ROJO (falló: medidas sin casos, mutación)`. Coincidencia carácter por carácter con la guía.
  - Segunda corrida: Con los 33 casos cargados, 209 mutantes evaluados, 209 muertos, 0 vivos. Veredicto: `VERDE (todas las verificaciones aplicables en regla)`. Coincidencia carácter por carácter con la guía.

### Paso 8 · Juzgar una partida de verdad
- **Archivos creados:**
  - `hechos_partida.json` (32.708 caracteres, obtenido directamente del bloque visible desplegable).
  - 6 archivos en `requisitos/`: `naval.flota.requisito`, `naval.disparos.requisito`, `naval.turnos.requisito`, `naval.impactos.requisito`, `naval.final.requisito`, `naval.barcos_rectos.requisito`.
  - `sin-tiros.json` (5.261 caracteres).
- **Comandos ejecutados:**
  ```bash
  oracle juzgar --con hechos_partida.json
  oracle cobertura
  oracle cobertura --con hechos_partida.json
  oracle juzgar --con sin-tiros.json
  ```
- **Evidencia guardada:** `evidencia/paso8_oracle_juzgar.log`, `evidencia/paso8_oracle_cobertura.log`, `evidencia/paso8_oracle_juzgar_sin_tiros.log`.
- **Resultados:**
  - `oracle juzgar --con hechos_partida.json`: 11 medidas en verde. Coincidencia idéntica.
  - `oracle cobertura`: El bloque de salida en la guía muestra la concatenación de la ejecución sin `--con` y con `--con`. La salida real concatenada coincide al 100%.
  - `oracle juzgar --con sin-tiros.json`: 4 medidas cumplidas y 7 sin aplicar por falta de la relación `tiro`. Coincidencia idéntica.

### Paso 9 · Qué le falta a este juego
- **Acciones y comandos ejecutados:**
  ```bash
  git init
  git add .
  git commit -m base
  # Edición de catalogos/naval/naval.tiros_sin_repeticion.oracle (umbral <= 1)
  oracle cambios
  # Restauración de catalogos/naval/naval.tiros_sin_repeticion.oracle (umbral <= 0)
  oracle cambios
  ```
- **Archivos complementarios creados:**
  - `README.md`
  - `verificar_oraculo.py`
- **Prueba adicional:**
  - Activación de `catalogo_base: true` en `oracle.json` y corrida de `oracle test`.
  - Intento de ejecución de `python3 verificar_oraculo.py`.
- **Evidencia guardada:**
  - `evidencia/paso9_git_init.log`
  - `evidencia/paso9_oracle_cambios_1.log`
  - `evidencia/paso9_oracle_cambios_2.log`
  - `evidencia/paso9_oracle_test_catalogo_base_true.log`
  - `evidencia/paso9_verificar_oraculo.log`
- **Resultados:**
  - `oracle cambios` con umbral relajado detectó la anomalía: `✗ umbral aflojado sin nueva defensa naval.tiros_sin_repeticion <= 0 → <= 1 (el porque no cambió)`.
  - `oracle cambios` restaurado emitió `cambios desde HEAD: nada se aflojó · 0 errores · 0 avisos`. Coincidencia exacta.
  - Al activar `catalogo_base: true`, Oracle evaluó el proyecto con sus propias metamanchas (`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` y `meta.toda_cantidad_comparada_tiene_unidad_derivable`), tal como anticipó el texto explicativo.
  - `verificar_oraculo.py` falló por discrepancia de nombre de archivo (`partida_real.json` no encontrado).

---

## 5. Bloqueos Reproducibles y Discrepancias Críticas

### Hallazgo 1: Falta de salto de línea final en bloques `<pre class="archivo">` del HTML (Bloqueo Severo)
- **Cita del texto visible (Paso 5):**
  > *«Adentro de corpus/naval/, creá un archivo nuevo, pegá el contenido de este bloque y guardalo con el nombre exacto 005-barco-fila-desbordada.caso: [...] Volvé a la ventana de la terminal [...], escribí oracle test y presioná Enter. Lo que tenés que ver: [...] VEREDICTO: ROJO (falló: aceptación).»*
- **Comportamiento real observado:**
  Al copiar fielmente el texto contenido en el bloque visible de la página, el archivo se guarda sin `\n` terminal. Al ejecutar `oracle test`, Oracle aborta en la fase de validación de sintaxis canónica:
  ```text
  SINTAXIS ✗ — 1 archivo(s) fuera de la forma única
    · corpus/naval/005-barco-fila-desbordada.caso
      @@ salto de línea final @@
      - sin salto final
      + con salto final
      oracle formatear corpus/naval/005-barco-fila-desbordada.caso --escribir

  VEREDICTO: ROJO (sintaxis: forma única)
  ```
- **Impacto en una persona novata:** Bloqueo total. El principiante no ve el fallo de aceptación esperado, cree que escribió mal el código y se desorienta.
- **Acción realizada para continuar:** Se aplicó `oracle formatear corpus/naval/005-barco-fila-desbordada.caso --escribir` para añadir el salto de línea reglamentario.
- **Recomendación:** El generador de HTML debe preservar el salto de línea `\n` antes de la etiqueta de cierre `</code></pre>`, o la guía debe instruir el uso preventivo de `oracle formatear . --escribir`.

### Hallazgo 2: Discrepancia fatal en `verificar_oraculo.py` (`partida_real.json` vs `hechos_partida.json`)
- **Cita del texto visible (Paso 8 vs Paso 9):**
  - Paso 8: *«Guardá este archivo como hechos_partida.json...»*
  - Paso 9: *«El ejemplo también incluye una explicación y un script [...] para probar infracciones deliberadas. Copialos para tener la carpeta completa adentro de batalla-naval: un archivo de texto explicativo en formato Markdown (README.md) y el script de Python (verificar_oraculo.py).»*
- **Código en `verificar_oraculo.py` (líneas 87-88):**
  ```python
  ruta_real = BASE_DIR / "partida_real.json"
  evidencia_real = json.loads(ruta_real.read_text(encoding="utf-8"))
  ```
- **Comportamiento real:**
  Al ejecutar `python3 verificar_oraculo.py` en la carpeta `batalla-naval`, el script lanza:
  ```text
  FileNotFoundError: [Errno 2] No such file or directory: '.../batalla-naval/partida_real.json'
  ```
- **Impacto:** Si el usuario decide probar el script automatizado provisto en los archivos complementarios, falla de inmediato.
- **Acción realizada para verificar:** Se copió temporalmente `hechos_partida.json` como `partida_real.json` y se constató que con ese nombre el script corre y pasa todas las pruebas de falsabilidad al 100%.

### Hallazgo 3: Subcarpetas `corpus/naval` y `catalogos/naval` no creadas previamente
- **Cita del texto visible (Paso 5):**
  > *«Adentro de corpus/naval/, creá un archivo nuevo, pegá el contenido de este bloque y guardalo con el nombre exacto 005-barco-fila-desbordada.caso»*
  > *«Creá un archivo nuevo adentro de catalogos/naval/, pegale este código y guardalo con el nombre exacto naval.barcos_dentro_del_tablero.oracle»*
- **Comportamiento real:**
  `oracle init batalla-naval` genera `catalogos/` y `corpus/`, pero no crea el subdominio `naval/`. En el Paso 2 se explicó `mkdir css`, en el Paso 3 `mkdir js`, y en el Paso 8 `mkdir requisitos`, pero en el Paso 5 se omite la instrucción `mkdir -p corpus/naval catalogos/naval`.
- **Impacto:** En entornos gráficos o editores simples, intentar guardar en una carpeta no existente arroja error de ruta no encontrada.

### Hallazgo 4: Diferencia textual en la salida de aceptación roja (Paso 5)
- **Salida publicada en la guía:**
  ```text
  CORPUS: 1 casos guardados para verificar
    ✓ naval/005-barco-fila-desbordada (1 hechos, 1 aserciones)
  SINTAXIS: salteado (sin medidas todavía)
  ACEPTACIÓN: falló
    ✗ naval/005-barco-fila-desbordada
        el caso referencia 'naval.barcos_dentro_del_tablero' pero esa medida no existe en los catálogos
  ```
- **Salida real emitida por `oracle 0.38.0`:**
  ```text
  CORPUS OK · 1 casos · esquema, evidencia L0 y trazabilidad en regla
  SINTAXIS OK · 0 medidas · 0 macros · 1 casos · 0 relaciones
  catálogo: 0 medidas · corpus: 1 casos
  defectos que se pusieron rojos: 0 · verdes correctos: 0 · sin evidencia esperada: 0 · huecos declarados: 0
  nivel meta — el marco medido con sus propias medidas:
  ACEPTACIÓN ✗ — 1 problema(s)
    · 005-barco-fila-desbordada: reclama la medida «naval.barcos_dentro_del_tablero» y no está en el catálogo
  ```
- **Impacto:** Si bien el veredicto final es `ROJO (falló: aceptación)`, la redacción intermedia ha evolucionado en `oracle 0.38.0` y no coincide con el texto estático de la guía.

---

## 6. Conocimiento Deducido y Supuestos de la Guía

1. **Configuración de Git:** El Paso 9 asume que `git config` ya tiene definidos `user.name` y `user.email`. Aunque incluye un párrafo de advertencia (*«Si Git pide nombre y correo...»*), un usuario novato que pegue el bloque `git init && git add . && git commit -m base` de un tirón verá fallar el commit sin entender qué ocurrió si su entorno está limpio.
2. **Dependencia estricta de Git para `oracle cambios`:** Si no se crea el commit en Git, `oracle cambios` falla con `✗ «HEAD» no es un commit de git`.
3. **Descarga vs guardado manual:** En el Paso 8, la guía sugiere descargar `hechos_partida.json` desde el navegador y moverlo desde `Descargas/` a `batalla-naval/`. El proceso de mover archivos entre carpetas del sistema operativo suele ser un punto de fricción común para principiantes. El bloque desplegable alternativo mitiga esto, pero sufre de la discrepancia de nombre con `verificar_oraculo.py`.

---

## 7. Inventario de Evidencias Técnicas

Todos los registros de comandos y salidas reales se encuentran resguardados en `/tmp/oracle-cierre-novato/agy2/evidencia/`:

| Archivo de Log | Comando / Paso Asociado | Propósito / Hallazgo |
|---|---|---|
| `paso0_uv_install.log` | `uv tool install oracle-metalenguaje` | Instalación aislada de `oracle 0.38.0` en `uv-isolated/`. |
| `paso1_oracle_init.log` | `oracle init batalla-naval` | Inicialización de carpetas base; muestra ruta absoluta. |
| `paso1_oracle_test.log` | `oracle test` (Paso 1) | Veredicto: `SIN MEDICIÓN (advertencia: proyecto vacío)`. |
| `paso5_oracle_test_rojo.log` | `oracle test` (Paso 5 - inicial) | **Evidencia del bloqueo:** falla en `SINTAXIS (forma única)` por falta de `\n`. |
| `paso5_oracle_formatear.log` | `oracle formatear . --escribir` | Corrección automática de forma canónica mediante la herramienta. |
| `paso5_oracle_test_aceptacion_rojo.log` | `oracle test` (Paso 5 - formateado) | Veredicto esperado `ROJO (falló: aceptación)`. |
| `paso5_oracle_test_mutacion.log` | `oracle test` (Paso 5 - con regla) | Veredicto `ROJO (falló: mutación)` con 18 mutantes (10 muertos, 8 vivos). |
| `paso6_oracle_test_1.log` | `oracle test` (Paso 6 - caso 006) | 14 muertos, 4 supervivientes. |
| `paso6_oracle_test_2.log` | `oracle test` (Paso 6 - casos 026-028) | Primer `VEREDICTO: VERDE` completo de la regla 1. |
| `paso7_oracle_test_1.log` | `oracle test` (Paso 7 - 10 reglas, 2 casos) | Detección de `MEDIDAS SIN CASOS ✗ (9 medidas)`. |
| `paso7_oracle_test_2.log` | `oracle test` (Paso 7 - 26 casos extra) | Blindaje total: 11 reglas, 33 casos, 209 mutantes extinguidos. `VERDE`. |
| `paso8_oracle_juzgar.log` | `oracle juzgar --con hechos_partida.json` | 11 medidas cumplidas sobre la partida real. |
| `paso8_oracle_cobertura.log` | `oracle cobertura [--con ...]` | Matriz de cobertura de los 6 requisitos funcionales. |
| `paso8_oracle_juzgar_sin_tiros.log` | `oracle juzgar --con sin-tiros.json` | Rechazo a juzgar a ciegas: 7 medidas omitidas por falta de hechos. |
| `paso9_git_init.log` | `git init`, `add`, `commit` | Inicialización del repositorio de control de versiones. |
| `paso9_oracle_cambios_1.log` | `oracle cambios` (umbral relajado) | Detección de regresión por umbral `<= 1`. |
| `paso9_oracle_cambios_2.log` | `oracle cambios` (umbral restaurado) | Verificación de restauración: `0 errores · 0 avisos`. |
| `paso9_oracle_test_catalogo_base_true.log` | `oracle test` (`catalogo_base: true`) | Activación de reglas internas de Oracle sobre el catálogo. |
| `paso9_verificar_oraculo.log` | `python3 verificar_oraculo.py` | **Evidencia de error:** `FileNotFoundError: partida_real.json`. |

---

## 8. Conclusiones y Recomendaciones de Cierre

1. **La herramienta y el método funcionan:** La arquitectura de Oracle demuestra un rigor excepcional. La detección de mutantes, la exigencia de casos rojos y verdes y el análisis de cobertura funcionan con precisión quirúrgica.
2. **Ajustes indispensables en la guía web:**
   - **Salto de línea final en HTML:** Añadir explícitamente `\n` al final del contenido en los bloques `<pre class="archivo">` para que el copiado directo respete la forma canónica de Oracle.
   - **Unificar nombres de partida:** En el Paso 8 o en `verificar_oraculo.py` / `README.md`, utilizar consistentemente el mismo nombre (`hechos_partida.json` o `partida_real.json`).
   - **Comando explícito `mkdir`:** Indicar `mkdir -p corpus/naval catalogos/naval` al inicio del Paso 5, manteniendo la coherencia con los pasos 2, 3 y 8.
   - **Actualizar captura de salida de Paso 5:** Reflejar el formato vigente de `oracle test` para que los aprendices no duden al comparar sus pantallas.
