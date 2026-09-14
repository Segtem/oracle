# Revisión P2 — correcciones antes del cierre

2026-09-12. Primera corrida: 44 tests, 6 fallos y 2 errores. Resultado íntegro conservado
por Codex en el log inicial. Corregir sólo tus archivos, sin comandos shell ni tests de Codex.

Actualización de cierre: las observaciones fueron corregidas y verificadas. Este registro conserva
la revisión histórica; ver [CIERRE-P2.md](CIERRE-P2.md) para el estado final y su evidencia.

## Reproducciones

- `buscar` abre un FIFO `.txt` y se bloquea (timeout a 3s). Comprobar archivo regular antes
  de abrir; omitir especiales con motivo. No convertir errores de stat/apertura/recorrido
  en omisiones exitosas: código1 con ruta para errores operacionales.
- `referencias` devuelve0 sobre TAREA.md corrupto. Auditar registros primero, como buscar/resumen.
- `anotar` aplica strip al texto de nota y pierde sangría/espacios significativos. Preservar
  exactamente texto aportado, también la marca; validar vacío sin reescribir contenido.
- Tus tests: falta importar shutil; el test de opciones inválidas debe aportar posicionales
  requeridos para probar realmente opciones desconocidas, no fallos por argumentos ausentes.

## Revisión de código

- `_es_archivo_de_texto` no usa EXTENSIONES_TEXTO_ADMITIDAS y lee todo, luego vuelve a leerse.
  Unificar lectura acotada (límite+1) y clasificación. Aplicar extensiones declaradas, incluir
  `.oracle` y permitir nombres sin extensión si lo documentás. Reportar omisiones de binario,
  tamaño, tipo/enlace, extensión desconocida; errores reales de lectura =>1.
- Buscar sólo recorre un nivel de adjuntos: debe encontrar notas en subcarpetas de la tarea,
  sin seguir enlaces ni repositorios anidados. Informar carpetas excluidas/enlaces también.
- Salida humana de buscar/referencias omite TODAS las omisiones, incluso con cero resultados.
  Mostrar motivos también sin --json. No esconder error o alcance parcial tras un listado vacío.
- `os.walk` en referencias silencia errores por defecto: usar onerror que falle con diagnóstico.
- Revisar captura: errores al crear el temporal de anotar están fuera del try y producen
  traceback. Asegurar frontera pública para errores operacionales en todos los comandos P2.
- Adjuntar controla tamaño antes de copiar pero no durante: límite acumulado por bloques salvo
  --permitir-grande. Si crece el origen, abortar y revertir sólo la copia creada.
- En etiqueta Markdown de adjunto escapar backslash antes que corchetes. Nombres con saltos de
  línea/control: rechazar explícitamente antes de copiar, no generar enlaces partidos.
- `resumen` convierte etiquetas a minúsculas, distinto de listar que filtra exacto. Conservar
  etiquetas originales y deduplicar sólo identidades iguales, documentar mayúsculas consistentes.

Codex mantiene archivos Git, tests independientes e instalación. No modificar éstos. Actualizar
tu informe y guía con la conducta corregida; no inventar nuevas garantías. Entregar para que
Codex ejecute nuevamente las pruebas. No tocar versiones ni iniciar mutación.
