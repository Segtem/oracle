# de-cero lo sigue alguien que no sabe programar

- ESTADO: ABIERTA
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

## Próximo paso

Hacer una lectura de validación de la guía con un usuario sin conocimientos de programación para comprobar que pueda seguir el flujo completo desde una máquina limpia sin trabarse en ningún paso.

