# oracle cambios no lee el ref de un proyecto que vive en un subdirectorio del repositorio

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle

### Nota (2026-09-29 21:56:37 UTC)

Encontrado al probar el hook pre-push de LyraGASP: con el proyecto en medidas/ (subdirectorio del repositorio), git ls-tree devolvía rutas relativas al directorio actual y _extraer les quitaba el prefijo otra vez, así que el catálogo del ref salía vacío. Arreglo: --full-name. Además, un árbol de trabajo que no carga ahora se dice («no se pudo leer el catálogo del árbol de trabajo») en vez de una traza. Tests de los dos casos; mutación de las líneas cambiadas 2/2; oracle test VERDE, 2213 tests. Sale en 0.36.1.
