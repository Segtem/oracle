# Contraste de la revisión

Los informes de agy1 y agy2 se conservan como propuestas, no como prueba automática de cada afirmación.
La revisión de Codex contrastó las citas contra las fuentes y ejecutó las comprobaciones indicadas abajo.

## Cambios integrados

- Portada: inicio a Desde cero, explicación de tests sin afirmaciones absolutas, alcance de `oracle juzgar`, retiro del «0 mutantes vivos en el núcleo» sin una ronda completa vigente y sintaxis explícita del comando de crear medidas.
- MCP: consultas de sólo lectura no equivalen a protección del catálogo por permisos.
- Menú: abrir al pasar de móvil a escritorio; copiar: selección del código si falta la API o se deniega el permiso.
- Notas: no mostrar comentarios internos de generación; títulos en flujo normal para admitir código y anclas sin forzar una fila.
- CSS: permitir partir nombres de medidas y rutas dentro de la prosa; aumentar contraste del ámbar claro.
- Escenas de portada: registrar cambios de tema y repintar también en reposo y con movimiento reducido.
- Tutorial práctico: carpeta diferencial/, operador sin con predicado obligatorio y advertencia sobre el producto vacío del patrón histórico con agrupar.
- Cómo funciona: omitir ambito en la macro del ejemplo es error, no un valor por defecto.
- Escribir una medida: lista real de operadores y las seis macros.
- Tutorial corto: la relación con unidades resuelve el segundo problema de aceptación, no el de evidencia construida.
- Enlace histórico del tracker al tag v0.33.0 donde el archivo existe; enlaces del Markdown de-cero a las fuentes Markdown.

## Correcciones a los informes

- Agy1 dice que los enlaces .html de de-cero producen 404 en GitHub: los archivos HTML sí existen. Llevaban al código generado, no a la lectura de la fuente. Se cambiaron por comodidad de navegación, no por inexistencia.
- No se adopta el «0 mutantes vivos» del encabezado de agy1 como certificación de todo el núcleo.
- La gramática sugerida por agy1 para sin ponía el predicado como opcional: el parser exige `donde`. La documentación corregida conserva esa exigencia.
- `desde` aparece en el inventario del CLI, pero no se adopta la descripción propuesta de «fuente parametrizada»; también representa la tubería en la forma canónica.
- El JSON inicial de agy2 decía «82 pre / 78 copiar»: no es un defecto; las salidas y los árboles no deben copiarse. Tampoco sus ceros iniciales de celdas prueban un fallo: el informe posterior describe el recorrido completo.
- La medición de navegador y los desbordes son evidencia entregada por agy2. Codex no tuvo una superficie de navegador conectada. Las correcciones finales se contrastaron con fuente, enlaces y seis pruebas JS en VM; no se presentan como una nueva inspección visual final.

## Evidencia propia

- `auditar_enlaces.py`: 35 páginas y 2132 enlaces/recursos locales, sin destinos, anclas ni IDs duplicados problemáticos.
- Reproducción del proyecto del tutorial práctico: sin diferencial/ sale 1; agregándola, verde y 14/14 mutantes de medidas muertos (`tutorial-practico.log`).
- Macro sin ambito: el CLI rechaza la entrada, confirmando el error documental. Se abrió expandir-error porque además muestra traceback.
- `oracle contexto` y `oracle manual macros`: inventarios contrastados con los cambios documentales.
- Seis pruebas de interacción ejecutan el JavaScript publicado: menú, copiado exacto, dos fallbacks y repintado de temas con/sin movimiento reducido.
- `git cat-file -e v0.33.0:docs/12-tareas.md`: confirma el destino del enlace histórico.

## Mejoras posteriores registradas

- web-navegacion: jerarquía de títulos/índice de releases, metadatos y navegación entre decisiones.
- expandir-error: diagnóstico breve de una macro inválida.
- El piloto humano real sigue en pilotos-externos; una reproducción automática no lo sustituye.
