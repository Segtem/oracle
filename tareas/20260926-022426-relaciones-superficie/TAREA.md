# Declarar una relación exige escribir JSON anidado campo por campo: una superficie .relacion, como la de las medidas

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, metalenguaje, sintaxis, ergonomia, una-sintaxis

### Nota (2026-09-26 02:24:26 UTC)

2026-09-26, origen y DECISIÓN (Claude, con delegación de Brian): grupo 5 de ergonomia. La deuda de unidades de los consumidores (sombra meta.toda_cantidad_comparada_tiene_unidad_derivable: 49 en Jam, 62 en LyraGASP) es trabajo de declarar relaciones, y hoy eso es JSON a mano: ["relacion", n, ["campos", ["campo", nombre, tipo, unidad], …], ["variantes", …]?, ["alcance", …]]. Forma decidida, archivo .relacion en relaciones/, que carga al MISMO árbol (el JSON sigue valiendo, como con .oracle): encabezado «relacion <nombre>:»; una línea por campo «nombre: tipo [unidad]»; entero y flotante DEBEN declarar unidad (una magnitud o sin_unidad explícito); texto y booleano no llevan unidad porque no son magnitudes (se cargan con sin_unidad: no es un valor por omisión, es lo único que admiten; un texto o booleano con unidad es error); bloque opcional «variantes por <discriminante>:» con una sub-sección «<valor>:» por variante y sus campos; «alcance "…"» obligatorio al final. Impresor e ida y vuelta como las medidas (SINTAXIS de oracle test los cubre); oracle relaciones --escribir genera borradores en .relacion; ESPECIFICACION §1.3 y la sección de la superficie; VERSION_SINTAXIS a 0.8 junto con sin-evidencia-esperada (una sola subida). Convertir relaciones/ de Oracle a .relacion como prueba de uso. Quién: Codex, después de sin-evidencia-esperada (las dos tocan el lector).

### Nota (2026-09-26 02:59:57 UTC)

Implementada superficie .relacion con lector/impresor al árbol canónico, unidades numéricas obligatorias, texto/booleano sin unidad escrita, variantes y alcance final; JSON sigue cargando. Convertidas las 12 relaciones de Oracle; borradores --escribir en .relacion; SINTAXIS incluye relaciones; §1.3 y crónica 0.8 actualizadas sin subir VERSION_SINTAXIS; empaquetado y pruebas ajustados. Ejecutado: python3 -m unittest discover -s tests -t . (2582, OK); python3 tools/guia.py (verde); python3 tools/sitio.py --escribir (exit 0); python3 tools/cli.py test --rapido (VERDE); python3 tools/sintaxis.py --verificar (ida/vuelta OK). No ejecuté la mutación completa ni hice commits. Pendiente: Claude corre la mutación y revisa sus resultados.

### Nota (2026-09-26 03:08:22 UTC)

Corrección de Claude: en «nombre: tipo [unidad]» los corchetes marcaban opcionalidad, no sintaxis. El lector y el impresor .relacion usan unidades numéricas sin corchetes; [cm] ahora da error de sintaxis con la forma correcta. Texto y booleano siguen sin unidad escrita; entero y flotante la exigen. Reconvertidas las 12 relaciones, actualizados borradores, especificación, pruebas y sitio. Verificación: suite completa 2583 OK; guia.py exit 0; sitio.py --escribir exit 0; test --rapido VERDE; cifras.py --actualizar al final. Sin commits.

## Próximo paso

Claude: correr la mutación completa fuera de este sandbox, revisar sus resultados y resolver cualquier mutante sobreviviente antes de cerrar la tarea. Mantenerla ABIERTA hasta entonces; no hay commit de este trabajo.
