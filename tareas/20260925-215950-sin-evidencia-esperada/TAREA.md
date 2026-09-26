# Un caso de defecto se da por cumplido con SIN EVIDENCIA: que pueda declarar que espera sin_evidencia, distinto de un rojo medido

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, metalenguaje, sintaxis

### Nota (2026-09-25 21:59:50 UTC)

2026-09-25, origen: auditoria-verde ronda 2 (Codex), RONDA2.md fila 2. Hoy un caso falso_verde pasa la aceptación si la medida sale ROJO medido o SIN EVIDENCIA: los dos son «no ok». Los casos 029/030 de la batalla naval y 006 de primer-valor lo usan a propósito para fijar el requiere. El riesgo: un caso rojo que sale SIN EVIDENCIA no fija el donde; hoy lo cubre la mutación (los mutantes del filtro sobreviven), no la aceptación. Propuesta: un campo opcional en el caso (p. ej. «espera: sin_evidencia») que la aceptación compare exacto: un caso que lo declara tiene que salir SIN EVIDENCIA, y uno que no lo declara tiene que salir ROJO medido. Es cambio de sintaxis de .caso (sube VERSION_SINTAXIS) y de esquema; decidir antes de implementar si el campo es obligatorio para los casos que prueban requiere.

### Nota (2026-09-26 02:22:44 UTC)

2026-09-26, DECISIÓN (Claude, con delegación de Brian) y ENCARGO a Codex: (1) Campo opcional del caso «espera: sin_evidencia» en la superficie .caso, después de etiqueta; en JSON "espera": "sin_evidencia"; único valor admitido por ahora; sólo válido con una etiqueta que no sea verde_correcto (si no, CasoMalDeclarado con mensaje claro). (2) La aceptación compara exacto: un caso con espera: sin_evidencia tiene que salir SIN EVIDENCIA (un rojo medido o un verde es FALLA); un caso de defecto SIN el campo tiene que salir ROJO medido: si sale SIN EVIDENCIA es FALLA con el mensaje «salió SIN EVIDENCIA; si es lo que el caso prueba, declaralo con espera: sin_evidencia». (3) VERSION_SINTAXIS 0.7 → 0.8 con su párrafo en la crónica de ESPECIFICACION.md (sección de la superficie); la distribución no se toca (se sube en el corte). El impresor imprime el campo y la ida y vuelta lo conserva. (4) Migrar todo caso que hoy dependa de SIN EVIDENCIA declarándolo: corpus/ de Oracle, ejemplo/batalla-naval (029, 030), ejemplo/primer-valor (006), ejemplo/como-funciona (006) y los demás ejemplos; guías con salidas (tools/guia.py --escribir) y sitio. (5) Tests que fallen antes del cambio para las tres situaciones. (6) El manual (oracle manual) tiene que listar el campo si lista los campos del caso. Suite completa, guia.py, sitio.py --escribir, oracle test --rapido VERDE, cifras al final. Sin commits. Los consumidores (Jam, LyraGASP) NO se tocan: anotá en esta tarea qué casos suyos van a necesitar el campo (buscalos leyendo ~/Dev/jam/medidas/corpus y ~/Dev/games/unreal/LyraGASP/medidas/corpus, sin editarlos).

### Nota (2026-09-26 02:37:17 UTC)

Implementado espera: sin_evidencia en .caso y JSON, validación CasoMalDeclarado, impresión e ida y vuelta, aceptación exacta con rojo medido separado de SIN EVIDENCIA, sintaxis 0.8 sin subir distribución, manual y contrato MCP. Pruebas nuevas: el módulo falló antes por ausencia de _resultado_esperado y luego pasó (4 tests). Migrados 18 casos de corpus propio y 8 de ejemplos (naval 029/030, primer-valor 006, como-funciona 006, seguimiento-tareas 010/020, sensor-prosa 014/015). Regeneradas guías, sitio, manual y cifras; equivalentes reapuntados. Verificado: suite completa 2580 tests OK; guia.py sin cambios pendientes; sitio.py sin cambios pendientes; mcp_contrato --check OK; cifras.py CIFRAS OK; git diff --check OK; oracle test --rapido VERDE. Aceptación propia: 102 rojos medidos, 18 SIN EVIDENCIA esperados, 85 verdes, 0 huecos. Consumidores revisados sólo leyendo corpus y catálogos: Jam necesita espera en geometria-011-al-ras-sin-piezas-no-concluye, geometria-013-comparte-cara-sin-evidencia-no-concluye, physics-004-apoyado-sin-asentamiento-no-concluye y scatter-006-cobertura-sin-evidencia-no-concluye. En LyraGASP no se encontró ninguna cláusula requiere en catalogos JSON, por lo que no se identificó ningún caso para migrar mediante esa revisión estática. No se editaron consumidores ni se hicieron commits; tarea sigue abierta.

## Próximo paso

Revisar el diff de Oracle y, en el corte correspondiente, subir la distribución y coordinar la migración de los cuatro casos identificados de Jam; mantener esta tarea abierta hasta esa revisión.

### Nota (2026-09-26 02:40:57 UTC)

2026-09-26, Claude: revisado y unido a main (sintaxis 0.8; la distribución sube en el próximo corte). Los cuatro casos de Jam que van a necesitar «espera: sin_evidencia» quedan anotados en la tarea una-sintaxis de Jam, que es cuando Jam sube a la versión con esto. Se cierra.
