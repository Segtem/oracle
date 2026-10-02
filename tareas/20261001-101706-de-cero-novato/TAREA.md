# de-cero lo sigue alguien que no sabe programar

- ESTADO: CERRADA
- PRIORIDAD: 82
- ETIQUETAS: 

### Nota (2026-10-01 10:17:06 UTC)

Brian: «desde cero tiene que ser capaz de seguirlo alguien que no entiende del tema». Qué: una auditoría de quien no programa (agy2, con citas) y una reescritura de la prosa (agy1): qué instalar y cómo (uv, git, un editor), qué es una terminal y cómo se abre, cómo se crea un archivo y una carpeta, cada término explicado la primera vez, y un «si ves otra cosa» donde haga falta. Sin tocar los bloques de código ni sus salidas.

## Avance

Se reescribió la prosa de `docs/de-cero.md` manteniendo el tono rioplatense, frases cortas y la estructura pedagógica de cada misión, sin modificar bloques de código, atributos ni comentarios de juego (`<!-- juego ... -->`).

### Qué se resolvió de la auditoría:
1. **Sección «Antes de empezar» previa al Paso 1:**
   - Explicación de qué es una terminal/consola y cómo abrirla en Windows (PowerShell/Terminal), macOS (Spotlight) y Linux, junto con el truco del clic derecho para pegar en Windows.
   - Navegación básica entre directorios con `pwd`, `cd` y `cd ..`, indicando dónde se ubica por defecto la terminal al abrirse.
   - Guía de instalación de los requisitos: Python 3.11+ (con advertencia crítica sobre «Add python.exe to PATH» en Windows), `uv` (comandos para macOS/Linux y PowerShell en Windows), `git` (enlace oficial y opciones estándar) y editores de texto plano recomendados (Visual Studio Code o Bloc de Notas, advirtiendo explícitamente no usar Word ni WordPad).
   - Comprobación de instalación mediante `python --version`, `uv --version` y `git --version`.
   - Instrucciones para crear carpetas y archivos con nombres y extensiones exactas: configuración para mostrar extensiones en Windows, selección de Tipo «Todos los archivos (*.*)» en Bloc de Notas para evitar `.txt` involuntarios, e interpretación de rutas con barras `/`.
   - Cómo interpretar los bloques de la guía: comandos para terminal (`paso`), archivos para guardar (`archivo=`), salidas esperadas (`salida`) y diagnósticos («Si ves otra cosa»).
2. **Definición de términos técnicos en su primera aparición (en una sola frase, integrada a la narrativa):**
   - **LLM / modelo de lenguaje:** en la introducción.
   - **Oracle, caso y mutante:** en la introducción y reforzados en los pasos 5 y 6.
   - **Catálogo, catálogo base, JSON y sombra:** en el Paso 1.
   - **Tests:** en el Paso 3.
   - **Filas planas, relación y campo:** en el Paso 4.
   - **Corpus, medida, regla y umbral:** en el Paso 5.
   - **Requisito y cobertura:** en el Paso 8.
   - **Testigos:** en el Paso 8.
   - **Git, commit, HEAD y script:** en el Paso 9.
3. **Secciones «Lo que tenés que ver» y «Si ves otra cosa» ampliadas:**
   - Paso 1: explicación de la salida inicial vacía y solución ante `oracle: command not found` (reinicio de terminal, PATH, reingreso con `cd batalla-naval`).
   - Paso 2: reconocimiento del estado visual inicial (cabecera y paneles oscuros sin tableros normales antes de JS) y solución si el navegador muestra el texto plano (`.html.txt`) o no abre.
   - Paso 3: apertura de herramientas de inspección y pestaña Consola (F12) para diagnosticar archivos faltantes en `js/`.
   - Paso 5: explicación pedagógica del `VEREDICTO: ROJO` por falta de regla en catálogo y del posterior rojo por mutación (regla aún vulnerable).
   - Paso 6: traducción del reporte de mutaciones a lenguaje cotidiano y confirmación del veredicto verde blindado.
   - Paso 7: explicación de la alerta `MEDIDAS SIN CASOS` y guía para guardar los 26 casos faltantes.
   - Paso 8: instrucciones detalladas para mover `hechos_partida.json` desde Descargas a `batalla-naval` (o renombrar `partida_real.json`), desmitificación de la lista `SIN MIRAR` (no son errores, sino transparencia), símbolos de cobertura (`✓`, `◐`, `·`) y diagnóstico si falta el archivo de hechos.
   - Paso 9: diagnóstico si falta Git (`git: command not found`), explicación de `oracle cambios` detectando el umbral aflojado y cómo restaurarlo.
4. **Verificación técnica:**
   - `python3 -m unittest tests.test_guia`: 4 tests en verde en ~14s.
   - `python3 tools/guia.py`: 14 pasos verificados, 0 salidas actualizadas.
   - Comprobación estructural: los 89 bloques de código y los 23 comentarios de juego se mantuvieron 100% idénticos.

### Qué no se resolvió de la auditoría (y por qué):
- Los puntos de la auditoría referidos al contenido interno de los archivos del ejemplo incluidos por referencia (como el `README.md` con fórmulas LaTeX y comandos `xdg-open`, o el shebang de Linux en `verificar_oraculo.py`) no se modificaron directamente en sus archivos fuente de `ejemplo/batalla-naval/` para cumplir estrictamente la regla de no alterar los bloques de código ni los archivos de los ejemplos que son validados por los tests automatizados y el trabajo de otros agentes en paralelo. En su lugar, se explicó su propósito y comandos equivalentes en la prosa de la guía.


### Nota (2026-10-02 00:40:10 UTC)

Revisión del relevo (2026-10-01, Codex): hay 8 tareas abiertas. main está 4 commits por delante de origin/main local y había 37 archivos modificados al empezar. Los pasos manuales, árboles y resaltado figuran CERRADOS; de-cero-novato sigue ABIERTA. Se recuperó el log de Claude bffm8jbo0.output: tools/sitio.py 137-211: 28/28 muertos; 411-411: 4/4 muertos; tools/guia.py 84-172: 64/66 muertos, vivos tools/guia.py:169:80:constante y tools/guia.py:171:45:constante (1 a 2). La tanda acabó con árbol sin cambios; el exit 0 del envoltorio no significa que no haya supervivientes. Evidencia preservada en mutacion-relevo.log dentro de esta tarea. No se repitieron la suite ni oracle test en esta revisión; git diff --check pasó. Falta revisar los supervivientes y ejecutar la validación independiente de la guía nueva desde una carpeta vacía antes del cierre y push.

### Nota (2026-10-02 00:56:42 UTC)

Continuación con ask-agy1 y ask-agy2 de ~/bin, autorizados por Brian. Cada agente trabaja en una copia separada bajo /tmp/oracle-cierre-novato. agy1 confirmó que los supervivientes no son equivalentes: L169 cambia la ubicación del diagnóstico y L171 conserva la primera línea del árbol viejo al reescribirlo. Tests integrados en test_guia.py y test_guia_rapida.py; 20 focalizados OK. Informe guardado como revision-mutantes-agy1.txt. Se corrigió la prosa de docs/de-cero.md: rótulos reales del HTML, árbol como referencia, alcance real del test automático, descripción de Git y recuperación si Oracle no está en PATH antes de crear la carpeta. Comando uv tool update-shell contrastado con uv local y https://docs.astral.sh/uv/concepts/tools/. Mutaciones de sitio y guía lanzadas sobre copias fijas; agy2 sigue la guía HTML desde una carpeta vacía con instalación aislada.

### Nota (2026-10-02 09:45:13 UTC)

Cierre técnico verificado: agy1 resolvió la cobertura de los dos supervivientes; agy2 recorrió las nueve misiones con Oracle 0.38.0 aislado. Dos hallazgos reales corregidos y registrados en script-naval-guia y copiar-forma-unica. Su informe crudo y logs se preservan, con revisión-hallazgos.txt que descarta dos afirmaciones incorrectas al contrastar la página original. Reproducción independiente del HTML corregido: 14 bloques de comandos, 63 escrituras, todas las salidas comparadas y script complementario OK. Verificación final: oracle test código 0, 2256 unitarios OK, 1026/1026 mutantes de medida, VERDE con mutación de código completa omitida. Mutación focalizada: guía 66/66 y sitio final 36/36 muertos, 0 supervivientes/timeouts/errores; ambas rondas parciales (código 2 esperado). Sitio generado al día y git diff --check OK. El primer intento de suite descubrió caché dejada por el test nuevo en el ejemplo; se aisló la importación en temporal, pasaron 4 tests focalizados y luego la suite completa. No se validaron clics del juego ni Windows/macOS ni una persona real; pilotos-externos conserva esa validación humana pendiente.

### Nota (2026-10-02 09:47:38 UTC)

Implementación y evidencia commiteadas en 1d04031. Defectos derivados cerrados: script-naval-guia (a5d23ed) y copiar-forma-unica (465fe01). Cierre de la validación con agentes y reproducción automática desde HTML; no se presenta como prueba con una persona principiante. Todos los cambios de código y documentación ya están verificados; quedan los commits de cierre para publicar en main.

## Próximo paso

Sin pendientes en esta tarea: recorrido con agentes y reproducción del HTML corregido completos. La validación con personas reales continúa en pilotos-externos; Windows/macOS y los clics del juego no se verificaron en esta corrida.
