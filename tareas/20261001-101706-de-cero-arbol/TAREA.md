# de-cero muestra el árbol de archivos en cada etapa, escrito y verificado por el test de la guía

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: 

### Nota (2026-10-01 10:17:06 UTC)

Brian quiere un árbol de rutas para saber si cada archivo está donde tiene que estar. Qué: un bloque de árbol en los puntos clave de docs/de-cero.md (después de oracle init, con el juego armado, con la primera regla, con todas las reglas, al final) cuyo contenido lo escribe tools/guia.py --escribir listando la carpeta real de la corrida, y que tools/guia.py (verificar) compara: un árbol viejo hace fallar el test, como una salida vieja. Encargado a Codex.

### Nota (2026-10-01 10:28:15 UTC)

Agregué cinco bloques text arbol en docs/de-cero.md (tras init, juego, primera regla, once reglas y final). tools/guia.py lista la carpeta temporal real, con directorios primero y orden alfabético, ignora .git y __pycache__, escribe y compara los árboles. Agregué test que falla ante árbol viejo. La guía se reconstruyó sin cambios pendientes y la suite completa pasó (2250 tests).

### Nota (2026-10-01 10:33:24 UTC)

Verificación final: python3 tools/guia.py --escribir (0 salidas actualizadas), python3 tools/sitio.py --escribir (sin páginas pendientes), python3 -m unittest discover -s tests (2250 tests, OK), python3 tools/oracle.py test (VEREDICTO: VERDE; mutación de código salteada). No se hizo commit.

### Nota (2026-10-02 10:50:49 UTC)

Cierre formal registrado durante corte-web: el cambio estaba integrado y la tarea CERRADA, pero faltaba el asunto exacto <ID>: done. Guía y árboles pasan en la suite final; tools/guia.py completo está cubierto por la mutación del corte. Este commit sólo completa el protocolo.

## Próximo paso

Trabajo integrado, verificado y con cierre formal. Sin pendientes; evidencia adicional en corte-web.
