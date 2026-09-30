# pixel art en todas las páginas del sitio

- ESTADO: CERRADA
- PRIORIDAD: 76
- ETIQUETAS: 

### Nota (2026-09-30 22:42:26 UTC)

Por qué: el sitio tiene pixel art en la portada (docs/assets/pixel.js) y en la batalla naval (docs/assets/guia.js), pero las páginas que genera tools/sitio.py son texto plano. Qué: una identidad de pixel art en todas las páginas generadas —cabecera o viñeta por sección (Empezar, Entender, Herramientas, Referencia), sprites chicos por tipo de página, divisores— hecha a mano en el mismo estilo que pixel.js, decorativa (aria-hidden), con prefers-reduced-motion respetado y legible en tema claro y oscuro. Encargado a agy1.

## Avance

- Archivos modificados y creados:
  - `docs/assets/pixel-sitio.js` (nuevo): motor de pixel art sin dependencias externas ni CDN; paleta reactiva a tokens CSS (`--tinta`, `--papel`, etc.); 20 sprites manuales de 14x14; 5 escenas de cabecera de sección de 180x42 (`empezar`, `entender`, `herramientas`, `referencia`, `decisiones`); 1 escena marina de pie de página de 240x44 con barco y faro (`marina`); renderizado de divisores pixelados en `hr.divisor-pixel`; soporte de `prefers-reduced-motion` (fotograma estático completo); reactividad a cambios de tema claro/oscuro y `IntersectionObserver`.
  - `tools/sitio.py`: inyección automática del sprite correspondiente a cada página en el `<h1>`, viñeta/escena de cabecera con lema por sección, divisores `<hr class="divisor-pixel" aria-hidden="true">`, pie de página decorativo con escena marina e inclusión de `assets/pixel-sitio.js` en todas las páginas generadas.
  - `docs/assets/sitio.css`: estilos para `.sprite-titulo`, `.cabecera-seccion`, `.escena-seccion`, `.seccion-texto`, `.seccion-nombre`, `.seccion-lema`, `.divisor-pixel`, `.divisor-canvas`, `.pie-seccion`, `.escena-pie` y adaptabilidad completa para móviles (ancho 400px sin scroll horizontal).
  - Regeneradas todas las páginas `docs/*.html` y `docs/decisiones/*.html` con `python3 tools/sitio.py --escribir`.

- Sprites manuales dibujados (14x14 px, nombres en castellano, qué cuenta cada uno):
  1. `timon`: (`de-cero.html`) — Timón clásico de navío que guía al usuario en su primera travesía y partida contra un LLM.
  2. `mapa`: (`documentacion.html`) — Carta náutica con derrota y waypoints que trazan el camino por la documentación.
  3. `bandera_roja`: (`02-de-cero-a-un-rojo.html`) — Mástil con la bandera roja izada, el primer caso que falla dando sentido a la regla.
  4. `pluma`: (`03-escribir-una-medida.html`) — Pluma caligráfica escribiendo la sintaxis formal de una medida en el cuaderno de bitácora.
  5. `tacometro`: (`13-primer-valor.html`) — Dial con aguja que marca el primer valor numérico medido sobre hechos concretos.
  6. `engranajes`: (`como-funciona.html`) — Mecanismos del motor que articulan la tubería de datos, proyecciones y veredictos.
  7. `mutante_cazado`: (`05-por-que-la-mutacion.html`) — Bicho mutante atrapado bajo la diana y abatido por el corpus.
  8. `conector`: (`07-conectar-a-un-proyecto-propio.html`) — Clavija de acople que enlaza el código del proyecto con el recolector de hechos de Oracle.
  9. `martillo`: (`tutorial-practico.html`) — Martillo de forja donde se templan y ajustan las medidas en el taller práctico.
  10. `matraz`: (`recetas.html`) — Frasco de química combinando patrones, fórmulas y agregaciones de medidas.
  11. `sensor_ojo`: (`14-sensor-prosa.html`) — Autómata vigilante que evalúa la prosa y emite hechos estructurados.
  12. `llave_tuerca`: (`openspec.html`) — Herramienta de ajuste fino que ensambla Oracle con la especificación abierta OpenSpec.
  13. `servidor_antena`: (`mcp.html`) — Torre transmisora que coordina en red las capacidades del servidor MCP.
  14. `chip_memoria`: (`mutacion-memoria.html`) — Circuito integrado de persistencia que retiene el histórico de mutantes analizados.
  15. `boya_campana`: (`reportar.html`) — Boya náutica con campana que alerta de un límite o arrecife no cubierto.
  16. `pergamino_sello`: (`especificacion.html`) — Pliego formal sellado con lacre que consigna el canon estricto del lenguaje.
  17. `encrucijada`: (`decisiones/index.html`) — Poste de señales náuticas con rumbos alternativos en el índice de decisiones.
  18. `faro_destello`: (`notas.html`) — Linterna de faro emitiendo un destello para anunciar una nueva versión liberada.
  19. `ancla_antigua`: (`notas/anteriores-a-0.20.html`) — Ancla histórica descansando en el lecho marino con los orígenes del proyecto.
  20. `brujula`: (`decisiones/DECISION-*.html`) — Aguja magnética que fija e inmoviliza el rumbo de cada decisión arquitectónica adoptada.

- Escenas en viñetas y pie:
  - `empezar`: Barco navegando en la niebla que choca contra un escollo; se iza la bandera roja y el faro confirma el primer caso rojo listo.
  - `entender`: Bicho mutante que intenta corromper el umbral de la regla y cae fulminado por el corpus (`MUTANTE MUERTO`).
  - `herramientas`: Robot sensor con antena MCP emitiendo ondas mientras barre un bloque de hechos y registra límites.
  - `referencia`: Escala de deuda tolerada bajo sombra hasta la cota estricta; si se sobrepasa la cota, el poste salta a rojo.
  - `decisiones`: Brújula con aguja magnética alineada al norte uniendo waypoints de diseño y pergamino sellado.
  - `marina`: En el pie de página, olas mecánicas pixeladas mecidas rítmicamente con un velero navegando bajo estrellas hacia un faro en la costa con haz de luz giratorio.

- Segunda iteración de presencia pixel art (ampliación de escenas, visibilidad y accesibilidad):
  - Escenas de cabecera ampliadas a 320×64 de lienzo:
    - Se removió todo texto dentro del canvas para no competir con el HTML ni quedar ilegible.
    - `empezar`: Barco zarpando del muelle del puerto con la bandera roja izada en lo alto del mástil (el primer rojo), navegando hacia mar abierto con estela de espuma.
    - `entender`: Mutantes que avanzan por la pasarela y, al cruzar el haz de escaneo vertical de la medida, son detectados con chispas de error y caen fulminados al foso de descarte.
    - `herramientas`: Faro vigilante en el acantilado barriendo el mar con un haz rotatorio sobre una boya sensora que emite ondas de telemetría.
    - `referencia`: Cartógrafo en su mesa de roble midiendo derroteros sobre un mapa náutico con compás, con el sello oficial de lacre rojo estampado en la carta.
    - `decisiones`: Timón de maniobra, compás orientado al norte, waypoints interconectados de diseño y libro de bitácora sellado.
  - Corrección de accesibilidad:
    - Se eliminó `aria-hidden="true"` del div `.cabecera-seccion` y del footer `.pie-seccion`, dejándolo únicamente en los `<canvas ... aria-hidden="true">` decorativos. Los textos semánticos (nombre, lema y pie) quedan legibles para lectores de pantalla.
  - Divisores pixelados visibles (2–3 px de alto):
    - Rediseñados en `docs/assets/pixel-sitio.js` y `docs/assets/sitio.css` a 320×10 px con una línea de olas y boyas náuticas cada 32 px; contrastados en `--acento` (`#4338CA` claro / `#A5A0FF` oscuro), `--rojo` y `--ambar` para alta legibilidad en ambos temas.
  - Sprites en subtítulos `<h2>` y escena marina de pie ampliada:
    - Sprite chico de 14×14 px junto a cada `<h2>` representativo de la sección (`timon`, `engranajes`, `martillo`, `pergamino_sello`, `brujula`), sin romper los enlaces ancla ni el índice en la barra lateral.
    - Escena marina de pie de página ampliada a 320×56 px con luna creciente, faro en acantilado, haz giratorio, boya y velero.
    - Responsividad verificada para móviles de 400 px y menores sin desborde ni scroll horizontal (`max-width: 100%`, `aspect-ratio`).
  - Validación:
    - Todas las páginas regeneradas con `python3 tools/sitio.py --escribir`.
    - Pasaron los 92 tests unitarios (`tests.test_sitio`, `tests.test_sitio_rapido`, `tests.test_guia`, `tests.test_manual`).

## Próximo paso

Inspeccionar visualmente las páginas generadas en navegadores en tema claro y oscuro a resoluciones de escritorio y móvil (400 px) para verificar balance visual con la tipografía.

### Nota (2026-09-30 23:29:49 UTC)

Unido por Claude tras dos rondas: la primera era tímida (escena de 180×42 con texto ilegible, divisores invisibles). Queda: escena por sección de 320 px (puerto con bandera roja, mutantes que caen, faro, cartógrafo), sprite junto al título y a cada h2, divisores de olas y pie marino. Revisado en Chrome; Claude corrigió que el sprite del título quedara solo en una línea con títulos largos (flex-wrap). Cabe en 400 px (max-width 100%). Mutación de las líneas con lógica de sitio.py 10/10 (el resto son diccionarios de textos, sin sitios).
