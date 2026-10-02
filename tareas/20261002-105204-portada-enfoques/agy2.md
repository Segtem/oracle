# Informe de Revisión Estática: Sección `t-enfoques`

## 1. Alcance y límite metodológico
- **Objetivo**: Auditoría estática exclusiva de la nueva comparación `t-enfoques` en [docs/index.html](../../docs/index.html) y su CSS final en [docs/assets/portada.css](../../docs/assets/portada.css).
- **Límite metodológico explícito**: Revisión estrictamente estática sobre el código fuente. Conforme a las instrucciones, no se utilizó navegador web, no se capturaron pantallas ni se ejecutaron suites de prueba, mutación o instalación de paquetes.

## 2. Veredicto general
**Estado: Sin bloqueos.** La sección se encuentra lista y correctamente construida. Cumple con los estándares de accesibilidad, semántica HTML5, coherencia conceptual, integración con el sistema de diseño (temas claro/oscuro) y responsividad en dispositivos móviles.

---

## 3. Evaluación por dimensiones

### Coherencia del diagrama
- **Progresión de fases**: Cada enfoque (*Vibe coding*, *SDLC*, *Spec-driven development* y *Oracle development*) modela de manera clara su flujo mediante listas ordenadas (`<ol>`), complementadas por bucles de iteración (`.vuelta-enfoque`) y textos de criterio.
- **Integración de Oracle**: En *Oracle development*, el bloque superior `.entrada-reglas` articula la alimentación del catálogo (reglas y mutación) hacia el sensor/medición, reflejando fielmente la arquitectura del proyecto (*producto → sensor → hechos → oracle → veredicto*).
- **Conectores direccionales**: Las flechas poligonales mediante `clip-path` y color dinámico `var(--ruta)` guían adecuadamente la secuencia tanto horizontal como verticalmente.

### IDs y SVG `<use>`
- **Unicidad de IDs**: Los identificadores (`t-enfoques`, `enfoques-fuente`, `enfoque-*-titulo`, y los IDs de `<symbol>`) son únicos en el documento.
- **Resolución de símbolos**: Todos los elementos `<use href="#...">` resuelven a símbolos existentes en `<defs>`.
- **Hallazgo menor (no bloqueante)**: El símbolo `#enfoque-tilde` (tilde verde) está definido en `<defs>`, pero ningún elemento hace referencia a él; se trata de código huérfano inocuo.

### HTML semántico
- **Jerarquía estructural**: Uso correcto de `<section aria-labelledby="t-enfoques">` con título de segundo nivel `<h2>`, integrando artículos `<article>` etiquetados individualmente con `<h3>`.
- **Uso de `<figure>` y `<figcaption>`**: La comparación completa está contenida en `<figure>`, asociada correctamente a su fuente/atribución en `<figcaption id="enfoques-fuente">`.
- **Estructuración secuencial**: El uso de `<ol>` y `<li>` para los pasos de cada flujo es semánticamente adecuado.

### Texto alternativo y accesibilidad
- **Iconografía puramente decorativa**: Todos los SVGs de pasos y definiciones contienen `aria-hidden="true"` y `focusable="false"`. El contenido accesible recae en el texto contiguo (`<strong>` y `<span>`).
- **Glifos y flechas aislados**: Símbolos Unicode (`↶`, `↓`, `→`) están marcados con `aria-hidden="true"`, evitando anuncios confusos en lectores de pantalla.
- **Navegabilidad asistiva**: Las etiquetas `aria-labelledby` en cada `<article>` aseguran un nombre accesible al navegar por regiones o puntos de referencia.

### Temas por variables
- **Tokens centralizados**: No hay colores fijos en la nueva sección de CSS. Se emplean tokens del sistema: `--papel`, `--papel-2`, `--tinta`, `--tinta-2`, `--linea`, `--gris`, `--acento`, `--ambar`, `--verde` y `--verde-suave`.
- **Modo oscuro**: Todas las variables poseen su correspondiente definición adaptada para tema oscuro en `@media (prefers-color-scheme: dark)` y `:root[data-theme="dark"]`.
- **Contraste**: Los contrastes cromáticos de texto, bordes y tarjetas superan las pautas WCAG AA en ambos modos.

### Puntos de quiebre móvil
- **Escritorio (> 1000px)**: Cuadrícula de 2 columnas (210px cabecera + recorrido) con pasos distribuidos horizontalmente.
- **Intermedio (601px a 1000px)**: La tarjeta pasa a 1 columna completa, concediendo el ancho total a los pasos para evitar compresión excesiva.
- **Móvil (≤ 600px)**: Transición fluida a flujo vertical (`grid-auto-flow: row`). Los iconos se alinean a la izquierda en cuadrícula de dos filas (`grid-row: 1 / 3`) y las flechas giran 90° (`transform: rotate(90deg)`), ubicándose con precisión (`bottom: -17px; left: 13px`) entre los centros de cada icono.
