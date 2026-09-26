# La invocación de una macro acepta dos cuerpos y el impresor escribe el que no se enseña

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 04:10:06 UTC)

2026-09-26, origen: AUDITORIA.md de una-sintaxis (fila «Invocación de macro»). DECISIÓN (Claude, con delegación de Brian): la forma única es la PLANTILLA —las mismas cláusulas que una medida escrita a mano: de, donde, umbral … segun … porque, requiere, ambito, alcance—, porque quien sabe escribir una medida ya sabe invocar una macro. El impresor pasa a escribir esa forma. La forma de argumentos (relacion/alias/predicado/porque/segun/…) pasa a ser error de sintaxis con un mensaje que muestre la misma invocación en la forma plantilla. Migrar todo archivo de Oracle y de los ejemplos que use la forma de argumentos (oracle convertir de un .oracle a sí mismo, o leer con el lector viejo e imprimir con el nuevo, comprobando que el árbol canónico no cambia). Va en la sintaxis 0.8, que no se publicó. IMPORTANTE: tiene que estar antes de que los consumidores conviertan, porque oracle convertir usa el impresor.

### Nota (2026-09-26 04:22:10 UTC)

Implementado: el impresor de macros escribe las cláusulas variables de la plantilla; la forma de argumentos se rechaza con ErrorSintaxis que muestra la misma invocación reescrita. Migradas 10 fuentes .oracle propias que usaban argumentos y 8 bloques de autoría en docs; comparación ejecutada de 96 árboles .oracle antes/después: idénticos. Actualizados tests, guías, sitio, README y equivalente posicional. Verificación ejecutada: suite completa python3 -m unittest discover -s tests -t .: 2587 tests OK; python3 tools/guia.py --escribir: 1 salida actualizada; python3 tools/sitio.py --escribir: 3 páginas escritas; python3 tools/cifras.py --actualizar: README actualizado; python3 tools/cli.py test --rapido: VERDE, CIFRAS OK; 298 tests focalizados OK; git diff --check OK. No se ejecutó la mutación ni se hizo commit. La tarea queda ABIERTA.

## Próximo paso

Claude: ejecutar la mutación sobre este cambio, revisar sus resultados y registrar el veredicto en esta tarea antes de decidir el cierre.

### Nota (2026-09-26 06:06:15 UTC)

2026-09-26, Claude: unida tras resolver el rebase contra ensenanza-una-sintaxis. La mutación va en la ronda del corte.
