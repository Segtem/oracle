# Declarar una relación exige escribir JSON anidado campo por campo: una superficie .relacion, como la de las medidas

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, metalenguaje, sintaxis, ergonomia

### Nota (2026-09-26 02:24:26 UTC)

2026-09-26, origen y DECISIÓN (Claude, con delegación de Brian): grupo 5 de ergonomia. La deuda de unidades de los consumidores (sombra meta.toda_cantidad_comparada_tiene_unidad_derivable: 49 en Jam, 62 en LyraGASP) es trabajo de declarar relaciones, y hoy eso es JSON a mano: ["relacion", n, ["campos", ["campo", nombre, tipo, unidad], …], ["variantes", …]?, ["alcance", …]]. Forma decidida, archivo .relacion en relaciones/, que carga al MISMO árbol (el JSON sigue valiendo, como con .oracle): encabezado «relacion <nombre>:»; una línea por campo «nombre: tipo [unidad]»; entero y flotante DEBEN declarar unidad (una magnitud o sin_unidad explícito); texto y booleano no llevan unidad porque no son magnitudes (se cargan con sin_unidad: no es un valor por omisión, es lo único que admiten; un texto o booleano con unidad es error); bloque opcional «variantes por <discriminante>:» con una sub-sección «<valor>:» por variante y sus campos; «alcance "…"» obligatorio al final. Impresor e ida y vuelta como las medidas (SINTAXIS de oracle test los cubre); oracle relaciones --escribir genera borradores en .relacion; ESPECIFICACION §1.3 y la sección de la superficie; VERSION_SINTAXIS a 0.8 junto con sin-evidencia-esperada (una sola subida). Convertir relaciones/ de Oracle a .relacion como prueba de uso. Quién: Codex, después de sin-evidencia-esperada (las dos tocan el lector).
