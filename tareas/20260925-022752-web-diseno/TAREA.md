# La web es críptica: una sola página apelmazada, sin explicaciones y con enlaces a .md en texto plano

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, web, diseno, flaqueza


## Qué dijo Brian (2026-09-24)

«Quedó muy críptica, sin espacio, todo apelmazado en una sola página. Muy acotada, sin explicaciones
profundas. Los links te mandan a .md que se ven como texto plano, feo para leer. Me gustaría que
tenga rigurosidad en UX/UI, un buen diseño; si querés podés hacer pixel art y crear animaciones y
diagramas que ayuden a entender por qué usar Oracle.»

**La hace Claude**: la web, las animaciones y el pixel art como recurso gráfico. No se delega.

## Qué está mal hoy

- `docs/index.html` (reescrito en `web-028`) mete doce secciones en una página densa: correcto en
  contenido, pero sin aire, sin jerarquía visual y sin llevar de la mano a quien no conoce Oracle.
- Explica poco el **por qué**: qué problema resuelve, para quién, qué pasa sin Oracle.
- Los enlaces llevan a `.md` en GitHub (o crudos), que no son parte del sitio.

## Qué tiene que tener

1. **Varias páginas con recorrido**, no una sola: portada (el problema y la promesa en 30 segundos),
   por qué Oracle, el lenguaje paso a paso, juzgar un producto, el tracker, el MCP y los agentes, Jev,
   empezar. Navegación clara y un camino recomendado para quien llega nuevo.
2. **La documentación dentro del sitio**, renderizada como HTML con el mismo diseño: guías, decisiones,
   especificación, notas de release. Nada de enlazar un `.md` crudo. Una herramienta del repo genera
   las páginas desde los `.md` (una sola fuente), y un test falla si una página quedó vieja, como hace
   `cifras.py` con los bloques.
3. **Rigor de UX/UI**: tipografía y ritmo vertical, contraste AA, modo claro y oscuro, que funcione en
   un teléfono, foco visible y navegación por teclado, `prefers-reduced-motion` respetado.
4. **Recursos gráficos propios**: pixel art (un personaje o emblema de Oracle, iconos por concepto),
   **animaciones** que muestren la idea (una medida que se pone roja y señala sus testigos; un mutante
   que muere; la sombra que perdona hasta su cota; el agente que escribe y Oracle que juzga) y
   **diagramas** (las capas L−2…L2, el bucle sensor → hechos → medida → veredicto, el MCP). Livianos,
   sin dependencias pesadas: SVG, CSS o canvas, todo en el repo.
5. **Rigor de contenido intacto**: toda salida de terminal sigue viniendo de una corrida guardada
   (regla de `web-028`), los ejemplos son archivos reales o recortes marcados, y las cifras las
   mantiene `cifras.py`.

## Próximo paso

Claude: primero un mapa del sitio y un boceto de la portada para que Brian lo apruebe; después el
generador de páginas desde los `.md`, el sistema visual (tipografía, color, componentes) y los
recursos gráficos, página por página.

### Nota (2026-09-25 02:43:44 UTC)

2026-09-25, Claude (de noche, en la rama t-web-diseno, SIN unir a main para no publicar antes de que Brian lo vea): (1) tools/sitio.py genera 26 páginas HTML desde los .md (guías, especificación, notas, decisiones) con Markdown de la biblioteca estándar, enlaces .md→.html y archivos del repo→GitHub; tests/test_sitio.py falla si una página quedó vieja. (2) Sistema visual en docs/assets/sitio.css: Schibsted Grotesk (títulos/UI), Source Serif 4 (lectura a 68ch), JetBrains Mono (código), Silkscreen (etiquetas pixel); papel frío, tinta azulada, acento índigo; rojo/verde/ámbar reservados para veredictos; claro y oscuro; menú lateral e índice de la página. (3) Emblema pixel (docs/assets/emblema.svg): el ojo del oráculo con las dos lámparas. (4) docs/assets/pixel.js: cuatro escenas animadas en canvas, en reposo muestran el cuadro final y respetan prefers-reduced-motion: la medida que señala su testigo (el barco en la fila 10 del ejemplo real), el mutante (aflojar_umbral) que el corpus mata, la sombra que supera su cota, el agente que corrige con el testigo. (5) Portada nueva (docs/index.html) en capítulos y página Por qué (docs/por-que.html) con la historia real de la batalla naval, la tabla test vs medida, los cinco niveles y cuándo no usar Oracle. Pendiente: que Brian lo vea; rehacer de-cero.html, donde-entra.html y reportar.html (viejos, del 6/09) o redirigirlos; revisar con Jev si cada página explica el porqué.

### Nota (2026-09-25 02:52:08 UTC)

2026-09-25, Claude: Jev (typesafe/jev-1.13) como sensor de la prosa de la web, dos preguntas por capítulo (¿explica POR QUÉ serviría Oracle? ¿se entiende sin jerga?) y dos controles fabricados (tareas/…/jev/jev_web.py, corridas en jev/corrida y jev/corrida-2). Los controles se comportan en la primera pregunta (sin-porque 0,04) y en la segunda sólo el de jerga (0,13); la segunda pregunta está menos calibrada. Con esa señal se reescribieron tres pasajes: el hero 0,57→0,81, el capítulo del barco 0,28→0,79 y los cinco niveles 0,30→0,53 (sigue en zona media: revisión humana). Recorridos, empezar y cuándo-no dan 'no' en porqué, como corresponde a navegación. Un sensor, no un juez: la decisión es de Brian.
