# Auditoría de exactitud y claridad: sección `t-enfoques`

Se auditó la sección `t-enfoques` (`docs/index.html`, líneas 67-133) y sus estilos asociados (`docs/assets/portada.css`, líneas 177-224), contrastando sus afirmaciones con `README.md`, `docs/como-funciona.md` y `docs/openspec.md`. Se identificaron los siguientes defectos concretos:

### 1. Escalera de superioridad y sesgo de «verde total»
* **Citas:**
  * `docs/index.html` (L. 70): `<h2 id="t-enfoques">De pedir código a pedir evidencia.</h2>`
  * `docs/assets/portada.css` (L. 177-183):
    * `.enfoque { --ruta: var(--gris); ... background: var(--papel-2); }`
    * `.enfoque-sdd { --ruta: var(--ambar); }`
    * `.enfoque-oracle { --ruta: var(--verde); background: var(--papel); border-color: var(--verde); box-shadow: 4px 4px 0 var(--verde-suave); }`
* **Defecto:** El título plantea una progresión evolutiva («De X a Y») que jerarquiza los enfoques como etapas hacia una meta superior, contradiciendo la premisa de que representan focos distintos y combinables (L. 73). Visualmente, la secuencia cromática (gris → acento → ámbar de advertencia → verde destacado con relieve y fondo diferenciado) posiciona a Oracle como el desenlace ganador («verde total»), en abierta tensión con la filosofía del proyecto: `README.md` (L. 311) advierte que *«un verificador que dice “TODO VERDE” enseña a confiar en él más de lo que merece»*.

### 2. Falsa dicotomía y asimetría de categorías
* **Citas:**
  * `docs/index.html` (L. 70): `De pedir código a pedir evidencia.`
  * `docs/index.html` (L. 108): Paso 1: `<strong>Producto</strong><span>creado con IA</span>`.
* **Defecto:**
  * Reduce SDLC y SDD a la categoría de «pedir código», ignorando que SDD formaliza requisitos y escenarios (`docs/openspec.md`, L. 3) y que SDLC incluye diseño y verificación formal.
  * Coloca a «Oracle development» como un enfoque metodológico en el mismo plano que SDLC y SDD. En rigor, Oracle es una capa ortogonal de medición de invariantes que se ejecuta *dentro* de ellos (`docs/openspec.md`, L. 60-77 muestra a Oracle integrándose en la verificación de SDD).
  * Los pasos de Oracle (Producto → Sensor → Hechos → Oracle → Veredicto) describen la tubería de observación y juicio de un artefacto ya existente, no un ciclo de desarrollo de software comparable a los otros tres.

### 3. Confusión entre lo real y lo construido
* **Cita:** `docs/index.html` (L. 105): `<span>La mutación comprueba si los casos detectan que se debilitan.</span>`
* **Defecto:** Presenta la mutación como prueba suficiente de la validez de las reglas. Omite la distinción fundamental documentada en `docs/como-funciona.md` (L. 573-576): la mutación sobre casos sintéticos prueba sensibilidad mecánica frente a lo imaginado, pero no veracidad ante el mundo. La confianza real exige casos con `procedencia: observada`: *«Un catálogo con mutación 100 % y respaldo real cero todavía no vio el mundo»*.

### 4. Omisión del alcance en el paso del veredicto
* **Cita:** `docs/index.html` (L. 108): `<strong>Veredicto</strong><span>valor + testigos</span>`
* **Defecto:** Según `README.md` (L. 143: *«El veredicto no es el producto — el punto ciego lo es»*) y `docs/como-funciona.md` (L. 234-235: *«Un verde nunca termina ahí: siempre enumera lo que no se miró»*), el veredicto es inseparable de su *alcance*. Sintetizar el paso 5 únicamente como «valor + testigos» desdibuja el principio central de confianza acotada.
