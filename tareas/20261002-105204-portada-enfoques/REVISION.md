# Diagrama de enfoques en portada

Se agregó la sección `#t-enfoques`: cuatro recorridos con sprites SVG propios del sitio,
texto HTML accesible y flechas pixel art. El contenido funciona sin JavaScript. En móvil,
las filas se vuelven verticales; los colores siguen el tema mediante variables compartidas.

## Referencias

- [Video de IBM Technology](https://www.youtube.com/watch?v=mViFYTwWvcM), solicitado por Brian: compara la iteración por prompts con un ciclo de desarrollo y con especificaciones, diseño y tareas revisadas antes de implementar.
- La página de YouTube permitió leer la descripción; los subtítulos se consultaron mediante su [transcripción publicada](https://prepublish.ai/youtube-transcript/mViFYTwWvcM). No se afirma haber visto los fotogramas ni se copió su arte.
- [SDLC, IBM](https://www.ibm.com/think/topics/sdlc): ciclo de trabajo iterativo que incluye entrega y mantenimiento.
- [SDD, IBM](https://www.ibm.com/think/topics/spec-driven-development): especificación como guía del trabajo y variantes de mantenimiento de la spec.
- Oracle se contrastó con README, docs/como-funciona.md y docs/openspec.md. Su fila es nuestra propuesta; no se atribuye al video.

## Revisión y decisiones

- Agy1 cuestionó una posible lectura de escalera de superioridad. Se cambió el título a «Dónde entra Oracle en el desarrollo con IA», se usó el acento de marca para todas las rutas y se aclaró cómo se combinan dentro del SDLC.
- Oracle muestra un ciclo de construir, observar, juzgar y corregir, con reglas/casos revisados como entrada aparte. El último nodo incluye el alcance.
- Se agregó una explicación breve del respaldo observado frente a los casos construidos. El texto anterior sobre mutación era correcto, pero la aclaración evita atribuirle más de lo que mide.
- Agy2 no encontró bloqueos estáticos. Se eliminó el sprite sin uso y se permitió partir rótulos largos; los iconos principales usan escalas enteras de píxel.
- No se adopta la afirmación general de agy2 de cumplimiento completo de accesibilidad/contraste: una lectura de CSS no certifica eso.

## Verificación

31 pruebas focalizadas del sitio e interacciones, correctas. El auditor de enlaces recorre las 35 páginas,
incluidos los href de los símbolos SVG. Los siete sprites tienen sus píxeles dentro del viewBox 20×20.
Sin JavaScript, los diagramas y textos permanecen. No hay navegador conectado a Codex;
no se afirma una inspección visual final ni una prueba real con lector de pantalla.

El corte 0.38.1 se mantiene; antes del push se reconstruyen los paquetes desde el commit final.
