# pixel art en la portada, con escenas de lo nuevo

- ESTADO: CERRADA
- PRIORIDAD: 76
- ETIQUETAS: 

### Nota (2026-09-30 22:42:27 UTC)

Por qué: la portada (docs/index.html, portada.css, pixel.js) tiene escenas de pixel art para la mutación y los agentes, pero nada para lo que llegó en 0.35–0.38: requisitos y cobertura con veredicto, oracle cambios vigilando sensores, OpenSpec, el generador que busca. Qué: más pixel art en la portada, con escenas nuevas para eso, en el mismo estilo y con la misma accesibilidad. Encargado a agy2.

## Avance

Se incorporaron cuatro nuevas escenas de pixel art en `docs/assets/pixel.js`, dibujadas a mano con la paleta del sistema, resolución de 192x108 px y compatibilidad completa con temas claro y oscuro, `prefers-reduced-motion` y pantallas móviles:

1. **`generador` (El generador busca y encoge evidencia)**:
   - *Qué cuenta*: Ante un mutante vivo que no se mataba con reglas simples, `oracle caso generar` explora el espacio de evidencia perturbando campos y vecinos hasta hallar discrepancia entre la regla y el mutante. Una vez encontrada, encoge la evidencia podando filas y datos superfluos hasta dejar el contraejemplo mínimo irreducible (`procedencia: generada`) que mata al mutante. Refleja cómo los mutantes no generables pasaron de 28 a 0 en 0.38.0.

2. **`cambios` (oracle cambios vigilando sensores)**:
   - *Qué cuenta*: Alguien intenta aflojar una regla (subir un umbral de `<= 0` a `<= 3` conservando el mismo `porque`) o modificar un archivo en la ruta de sensores declarada en `oracle.json` (`sensores/radar.py`) para evitar un rojo sin arreglar el código. El centinela de `oracle cambios` compara contra el commit de referencia, detecta el debilitamiento en el acto y lo atrapa en rojo con alarma y error explícito.

3. **`requisitos` (Requisitos y cobertura con veredicto)**:
   - *Qué cuenta*: Las promesas del producto expresadas en archivos `.requisito` son evaluadas por `oracle cobertura --con hechos.json`. Cada requisito recibe su veredicto exacto: cumplido por completo (`✓`, verde), cumplido en lo medido con escenarios pendientes (`◐`, ámbar con `sin_medir`), roto/fallido (`✗`, rojo, incluso si está en sombra) o sin juicio (`?`, gris/sin evidencia). El panel resume los estados y resalta la salida 1 ante fallos sin perdonar.

4. **`openspec` (OpenSpec entra como spec y sale como requisitos)**:
   - *Qué cuenta*: El flujo de `oracle requisito importar spec.md`. Una especificación formal en Markdown de OpenSpec (con secciones `### Requirement:` y cláusulas `SHALL`) entra al importador y se transforma en archivos estructurados `.requisito` con `texto`, `fuente`, `medido_por` y `sin_medir`, vinculando las promesas de la spec con el catálogo de medidas medibles de Oracle.

En `docs/index.html` se agregaron las secciones y figuras correspondientes con alternancia visual armónica (`dos-escenas` / `dos-escenas invertido`), textos descriptivos, `role="img"`, `aria-label` detallado y `figcaption`.
En `docs/assets/portada.css` se reforzaron las reglas de cancelación de animaciones para `prefers-reduced-motion`.

Correcciones tras revisión visual en Chrome:
- **Control de cajas y desbordes en todas las escenas (`pixel.js`)**: Se incorporó la función `verificarTexto(s, x, maxW, alineado)` que calcula el ancho con el avance fijo de 6 px/carácter y emite `console.warn` si un texto excede su panel o el ancho del lienzo (192 px). Se revisaron las 8 escenas (incluyendo escenas previas como `agente` y `testigos`) acortando textos y eliminando «...» que desbordaban.
- **Separación de etiqueta `PODA` en `generador`**: Se organizaron los valores de las filas y la etiqueta `PODA` en columnas independientes con holgura de más de 20 px, eliminando la sobreimpresión sobre los números.
- **Flujo de dos tiempos en `openspec`**: Se corrigió el error conceptual: la importación genera el requisito con `sin_medir` ("sin medida todavía") sin inventar `medido_por`. En un segundo tiempo aparece la medida vinculada (`medido_por auth.expira`) simulando el paso posterior con `oracle medida nueva`.
- **Muerte del mutante en `generador`**: La búsqueda y encogimiento concluyen indefectiblemente con el mutante muerto (`MUTANTE MUERTO`) abatido por el caso mínimo generado, tanto en la animación como en el cuadro final estático.

## Próximo paso

Verificar visualmente en el navegador que la consola de desarrollo no presente advertencias de `verificarTexto` y que la fluidez estética de las animaciones en tema claro y oscuro sea óptima.

### Nota (2026-09-30 23:29:50 UTC)

Unido por Claude tras dos rondas. La primera tenía texto que se salía de su panel en cuatro escenas, una etiqueta PODA sobre los números y un error de contenido: la escena de OpenSpec mostraba al importador escribiendo medido_por, que es justo lo que nunca hace. Corregido y visto en Chrome: generador (busca, encoge, el mutante queda hallado y muere), cambios vigilando un sensor, cobertura con ✓◐✗?, OpenSpec que nace sin medir. pixel.js avisa por consola si un texto excede su caja: 0 avisos.
