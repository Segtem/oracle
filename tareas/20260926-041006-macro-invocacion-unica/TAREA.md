# La invocación de una macro acepta dos cuerpos y el impresor escribe el que no se enseña

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 04:10:06 UTC)

2026-09-26, origen: AUDITORIA.md de una-sintaxis (fila «Invocación de macro»). DECISIÓN (Claude, con delegación de Brian): la forma única es la PLANTILLA —las mismas cláusulas que una medida escrita a mano: de, donde, umbral … segun … porque, requiere, ambito, alcance—, porque quien sabe escribir una medida ya sabe invocar una macro. El impresor pasa a escribir esa forma. La forma de argumentos (relacion/alias/predicado/porque/segun/…) pasa a ser error de sintaxis con un mensaje que muestre la misma invocación en la forma plantilla. Migrar todo archivo de Oracle y de los ejemplos que use la forma de argumentos (oracle convertir de un .oracle a sí mismo, o leer con el lector viejo e imprimir con el nuevo, comprobando que el árbol canónico no cambia). Va en la sintaxis 0.8, que no se publicó. IMPORTANTE: tiene que estar antes de que los consumidores conviertan, porque oracle convertir usa el impresor.
