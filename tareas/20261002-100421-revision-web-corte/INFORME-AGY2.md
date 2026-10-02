# Informe de Revisión Web — agy2
**Proyecto:** Oracle (`docs/` y `docs/assets/`)
**Fecha:** 2026-10-02
**Revisor:** agy2
**Contexto de tarea:** `20261002-100421-revision-web-corte`
**Entorno de ejecución:** Linux x86_64, Chromium 153.0.8010.52 (CDP headless), Node.js v24.21.0, Python 3.14.

---

## 1. Alcance y Metodología

Se auditó la totalidad de los 35 documentos HTML bajo `docs/` y sus activos (`docs/assets/`):
- **Navegación, enlaces y anclas:** Rastreo estático y resolución de todas las etiquetas `<a>`, `<link>`, `<img>`, `<script>` e identificadores `#id` en origen `.md` y destino `.html`.
- **Navegador real (Chromium CDP):** Se ejecutó una suite automatizada sin dependencias (`evidencia/navegador_auditoria.js`) conectada por Chrome DevTools Protocol sobre un servidor local, evaluando:
  - Consola y excepciones de JavaScript (`Runtime.exceptionThrown`, `console.error`, `console.warn`).
  - Renderizado responsivo móvil (viewport 375x667 px) y escritorio (1200x800 px).
  - Modos de color (`prefers-color-scheme: light` y `dark`).
  - Movimiento reducido (`prefers-reduced-motion: reduce`).
- **Interactividad:** Simulación de pulsaciones sobre los botones de copiar, opciones de cuestionarios («Predecí», «Elegí»), tablero interactivo naval (144 celdas), cacería de mutantes y persistencia de bitácora en `localStorage`.
- **Coherencia con generadores:** Contraste contra `tools/sitio.py` y `tools/manual.py`.

---

## 2. Defectos Confirmados Prioritarios

### Defecto 1: `display: flex; flex-wrap: nowrap;` en títulos provoca desborde horizontal en móvil y escritorio
- **Severidad:** Alta (rompe el diseño visual y produce scrollbar horizontal).
- **Ubicación exacta:** `docs/assets/sitio.css`, líneas 372–381:
  ```css
  .prosa h1 {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
  }
  .prosa h2 {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
  }
  ```
- **Evidencia reproducible:**
  Al declarar `display: flex; flex-wrap: nowrap;`, cada nodo de texto, etiqueta `<code>`, canvas de sprite y enlace de ancla (`.ancla`) se convierte en un elemento flex colocado en una única línea horizontal indestructible.
  En pantallas de escritorio a 1200 px de ancho, `docs/notas.html` desborda a `scrollWidth: 1235px` debido al título `0.21.0` cuyo enlace `.ancla` queda desplazado a `left: 1205.95px`.
  En móvil a 375 px, `docs/notas.html` desborda a 675 px de ancho:
  - `H2#motordesde_texto-la-última-entrada-que-aceptaba-json-escrito` (scrollWidth: 424 px).
  - `H1#0210--mutante-es-una-relación-con-variantes-y-requiere-puede-pedir-filas-de-una` (scrollWidth: 659 px).
  - `H1#0200--motor-juzga-con-el-mismo-catálogo-y-las-mismas-sombras-que-oracle-test` (scrollWidth: 487 px).
- **Corrección mínima:**
  En `docs/assets/sitio.css`, reemplazar `display: flex; flex-wrap: nowrap;` por comportamiento de bloque normal (los sprites ya cuentan con `display: inline-block; vertical-align: ...` en líneas 350–370):
  ```css
  .prosa h1, .prosa h2 {
    display: block;
  }
  ```
  *(O alternativamente `flex-wrap: wrap; align-items: baseline;`)*.

---

### Defecto 2: Ausencia de `overflow-wrap: anywhere;` en `.prosa code` desborda en móvil (15 páginas)
- **Severidad:** Alta (afecta la legibilidad en pantallas móviles de 375 px).
- **Ubicación exacta:** `docs/assets/sitio.css`, línea 132:
  ```css
  .prosa code { font-size: 0.84em; background: var(--papel-2); padding: 1px 5px; border-radius: 3px; }
  ```
- **Evidencia reproducible:**
  Los nombres de medidas, relaciones y rutas largas (ej.: `meta.ninguna_sombra_envejece_sin_cota`, `meta.toda_opcion_del_vocabulario_declara_que_significa`, `catalogos/naval/naval.tiros_sin_repeticion.oracle`) se escriben sin espacios dentro de etiquetas `<code>`. Al no permitir quiebre de palabra, el ancho del texto excede los 375 px disponibles en móvil:
  - `docs/de-cero.html`: desborda a 451 px por `catalogos/naval/naval.tiros_sin_repeticion.oracle` (width: 429 px).
  - `docs/especificacion.html`: desborda a 486 px por `meta.toda_relacion_del_lenguaje_esta_en_el_manual` (rectRight: 479 px).
  - Total: 15 de las 35 páginas superan el ancho de la pantalla (registrado en `evidencia/desbordes_movil.json`).
  Al inyectar `.prosa code { overflow-wrap: anywhere; }`, las 15 páginas ajustan exactamente a 375 px (0 desborde).
- **Corrección mínima:**
  En `docs/assets/sitio.css`, línea 132:
  ```css
  .prosa code { font-size: 0.84em; background: var(--papel-2); padding: 1px 5px; border-radius: 3px; overflow-wrap: anywhere; }
  ```

---

### Defecto 3: `docs/assets/pixel.js` no actualiza colores en tema oscuro bajo `prefers-reduced-motion`
- **Severidad:** Media (falla de accesibilidad y modo oscuro).
- **Ubicación exacta:** `docs/assets/pixel.js`, líneas 691 y 700–703:
  ```javascript
  690:    pintar(escena.duracion - 1);  // el cuadro final: la página se entiende en reposo
  691:    if (reducido) return;
  ...
  700:    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { pal = paleta(); });
  701:    new MutationObserver(() => { pal = paleta(); })
  702:      .observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  ```
- **Evidencia reproducible:**
  1. Si `reducido` es verdadero (`prefers-reduced-motion: reduce`), la función `montar(canvas)` retorna en la línea 691 antes de registrar los listeners de `matchMedia` y `MutationObserver` (líneas 700–702).
  2. Si el usuario alterna el tema (claro a oscuro), los lienzos de `docs/index.html` y `docs/por-que.html` jamás se enteran y retienen el fondo y trazos claros (`[242, 244, 241, 255]`) sobre una página oscura (`#0E1215`).
  3. Adicionalmente, cuando `reducido` es falso, el listener de la línea 700 únicamente reasigna `pal = paleta()`, pero no ejecuta `pintar(...)`; si la escena no está animándose en ese instante, el lienzo no se redibuja.
  *(A diferencia de `pixel-sitio.js`, que implementa correctamente `canvas._repintar = () => { pal = paleta(); pintar(...); }` y `refrescarTodo()`)*.
- **Corrección mínima:**
  En `docs/assets/pixel.js`, registrar la función de repintado y los listeners antes de evaluar el retorno por animación:
  ```javascript
    canvas._repintar = () => { pal = paleta(); pintar(escena.duracion - 1); };
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => canvas._repintar());
    new MutationObserver(() => canvas._repintar())
      .observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    if (reducido) return;
  ```

---

### Defecto 4: `navigator.clipboard.writeText` arroja `TypeError` síncrono no capturado en contextos no seguros
- **Severidad:** Media (falla de robustez en botones de copiar).
- **Ubicación exacta:** `tools/sitio.py`, líneas 608–611 (replicado en todas las páginas generadas):
  ```javascript
  navigator.clipboard.writeText(pre.querySelector("code").textContent)
    .then(() => { b.textContent = "Copiado"; setTimeout(() => { b.textContent = "Copiar"; }, 1500); })
    .catch(() => { const r = document.createRange(); r.selectNodeContents(pre.querySelector("code")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); });
  ```
- **Evidencia reproducible:**
  La API `navigator.clipboard` solo está disponible en contextos seguros (HTTPS o localhost). Cuando un usuario sirve la documentación por HTTP en red local (ej. `http://192.168.1.X:8000`) o en navegadores antiguos/restringidos, `navigator.clipboard` es `undefined`.
  Al ejecutarse el click, la llamada `navigator.clipboard.writeText(...)` evalúa la propiedad `writeText` sobre `undefined`, arrojando inmediatamente `Uncaught TypeError: Cannot read properties of undefined (reading 'writeText')`. Como la excepción ocurre de forma síncrona antes de generarse la promesa, el bloque `.catch(...)` nunca llega a ejecutarse y el fallback de selección de texto queda inoperativo.
- **Corrección mínima:**
  Proteger el acceso con encadenamiento opcional `navigator.clipboard?.writeText(...)` o comprobación previa:
  ```javascript
  const texto = pre.querySelector("code").textContent;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(texto)
      .then(() => { b.textContent = "Copiado"; setTimeout(() => { b.textContent = "Copiar"; }, 1500); })
      .catch(() => fallback());
  } else {
    fallback();
  }
  ```

---

### Defecto 5: Enlace roto a archivo inexistente `docs/12-tareas.md`
- **Severidad:** Baja/Media (enlace roto a GitHub 404).
- **Ubicación exacta:** `docs/notas/anteriores-a-0.20.md`, línea 245 (y generado en `docs/notas/anteriores-a-0.20.html:245`):
  ```markdown
  - [Contrato y tutorial](../../docs/12-tareas.md).
  ```
  Genera:
  ```html
  <a href="https://github.com/Segtem/oracle/blob/main/docs/12-tareas.md" rel="noopener">Contrato y tutorial</a>
  ```
- **Evidencia reproducible:**
  El archivo `docs/12-tareas.md` fue retirado del repositorio cuando la funcionalidad de tareas se independizó al paquete `trackertast`. En la rama `main` de GitHub, el enlace `https://github.com/Segtem/oracle/blob/main/docs/12-tareas.md` responde error HTTP 404.
- **Corrección mínima:**
  En `docs/notas/anteriores-a-0.20.md`, línea 245, cambiar el destino a la versión histórica archivada o referenciarlo en texto plano:
  ```markdown
  - Contrato y tutorial (`docs/12-tareas.md`, retirado al independizar trackertast).
  ```

---

### Defecto 6: Jerarquía de encabezados `#` en `NOTAS-DE-RELEASE.md` distorsiona el índice y sprites
- **Severidad:** Media (inconsistencia estructural entre HTML y generador).
- **Ubicación exacta:** `NOTAS-DE-RELEASE.md`, líneas 37, 66, 97, 120, etc.:
  ```markdown
  # 0.38.0 — las promesas de OpenSpec, y un generador que busca
  ...
  # 0.37.0 — lo que respalda la fijación, lo que alimenta a las medidas y lo que se cumple
  ```
- **Evidencia reproducible:**
  En `tools/sitio.py`, `Convertidor.bloques` reserva el nivel 1 (`#`) para el título principal de la página, asignándole el sprite de página (`sprite-titulo`) y excluyéndolo del índice lateral `aside.en-esta-pagina` (línea 420: `if nivel in (2, 3): self.indice.append(...)`).
  Como cada versión en `NOTAS-DE-RELEASE.md` usa `#` en vez de `##`:
  1. Cada una de las 23 versiones renderiza un canvas repetido `<canvas class="sprite sprite-titulo" data-sprite="faro_destello">`.
  2. Ninguna versión ingresa al índice lateral `aside.en-esta-pagina` de `docs/notas.html`.
  3. El índice lateral termina poblado exclusivamente por 15 repeticiones de los subtítulos de nivel 2: «Para actualizar», «Verificación», «Cómo se hizo», «Lo demás», perdiendo su utilidad como índice navegable de versiones.
- **Corrección mínima:**
  En `NOTAS-DE-RELEASE.md`, titular las versiones con `##` (nivel 2), manteniendo únicamente `# Notas de release` en la línea 1 como encabezado de nivel 1.

---

## 3. Preferencias de Diseño y Mejoras No Bloqueantes
*(Diferenciadas explícitamente de fallos funcionales)*

1. **Estado activo en barra superior (`aria-current="page"`):**
   Las páginas no generadas `por-que.html` y `manual.html` marcan su enlace activo en el menú superior (`<a href="..." aria-current="page">`). En cambio, en las páginas generadas por `tools/sitio.py`, el enlace `Documentación` de la cabecera carece de `aria-current="page"`.
2. **Metadatos y Canonical en páginas generadas:**
   `docs/index.html`, `docs/por-que.html` y `docs/manual.html` declaran `<link rel="canonical" href="...">` y `<meta name="description" ...>`. La plantilla de `tools/sitio.py` omite ambas etiquetas en las páginas de documentación.
3. **Contraste de lámpara ámbar:**
   En tema claro, el color de texto `--ambar: #A86A00` sobre el fondo `--ambar-suave: #F6E8C8` presenta un contraste de 3.45:1. Para texto pequeño (12 px en `.lampara.ambar`), el estándar WCAG AA sugiere un ratio mínimo de 4.5:1.
4. **Navegación entre decisiones de diseño:**
   Al visualizar una decisión individual (ej.: `docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.html`), la barra lateral no expone un submenú con las demás decisiones (DECISION-002 a 012), obligando a volver al índice de decisiones (`Referencia > Decisiones`).

---

## 4. Verificaciones Contrastadas y Correctas

1. **Integridad de enlaces y anclas internas:**
   Se comprobó la validez de los 178 enlaces en Markdown y más de 300 hipervínculos en HTML: no existe ningún enlace roto ni ancla `#id` faltante entre páginas locales.
2. **Accesibilidad estructural:**
   - Enlace de salto rápido `<a class="saltar" href="#contenido">` presente y funcional con teclado en todas las páginas.
   - Hitos semánticos (`<header>`, `<nav>`, `<main id="contenido">`, `<aside>`) correctamente estructurados.
   - Todas las imágenes `<img>` poseen atributo `alt`.
   - Los lienzos decorativos poseen `aria-hidden="true"`; los lienzos interactivos de la portada cuentan con `role="img"` y descripciones completas en `aria-label`.
3. **Juegos y Guía interactiva (`docs/de-cero.html`):**
   - Ejecución verificada sin errores de consola.
   - Las 10 insignias/logros de `LOGROS` cuentan con caminos reales y alcanzables de adjudicación.
   - El tablero naval evalúa expresiones en tiempo real sobre las 144 celdas sin desfasajes de estado.
   - La cacería de mutantes filtra adecuadamente mutantes vivos y muertos según los casos marcados.
   - Los botones «Copiar» extraen fielmente el contenido del elemento `<code>` sin incorporar el rótulo del propio botón.
4. **Sincronización con el repositorio:**
   `python3 tools/sitio.py` y `python3 -m unittest tests/test_sitio.py tests/test_manual.py` confirmaron que todos los archivos publicados en `docs/*.html` son representaciones idénticas de sus especificaciones fuente.
