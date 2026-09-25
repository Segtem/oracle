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
