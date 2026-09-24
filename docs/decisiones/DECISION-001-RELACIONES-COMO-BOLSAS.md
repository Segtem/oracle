# Decisión 001 — las relaciones son bolsas

**Estado:** aceptada el 2026-07-30.

## Contexto

La especificación 0.2 llamaba “conjunto” a una relación, pero la representación y el evaluador
conservaban cada aparición de un hecho. No existía una identidad universal con la que deduplicar:
algunos dominios tienen `id`, otros usan claves compuestas y dos observaciones iguales pueden ser dos
eventos reales distintos. Deduplicar por el contenido completo también habría borrado multiplicidad
sin que el sensor lo pidiera.

## Decisión

Una relación de L0 es una **bolsa nombrada de hechos homogéneos**:

- la multiplicidad es parte de la evidencia;
- el orden de almacenamiento no es parte de la semántica;
- `de`, `donde`, `unir`, `agrupar`, los agregados y los testigos conservan la multiplicidad que les
  corresponde;
- si un dominio necesita unicidad, su sensor debe producirla o una medida debe comprobarla mediante
  una clave declarada; Oracle no inventa la identidad del hecho.

## Consecuencias

Dos hechos idénticos cuentan dos veces. Un producto multiplica multiplicidades y los agregados operan
sobre todas las apariciones. Esto coincide con el comportamiento anterior, que ahora queda fijado por
regresiones en vez de ser un accidente de usar listas.

La alternativa de conjunto se rechaza porque exigiría un contrato de identidad nuevo, específico de
cada relación. Si en el futuro hace falta deduplicar dentro del álgebra, deberá entrar como operador
explícito con su clave y con dos usuarios reales; no como normalización silenciosa.

## Consecuencia registrada después (2026-08-24)

La cláusula «su sensor debe producirla o una medida debe comprobarla» tenía un hueco: la carga de
unicidad recaía en cada sensor, y un duplicado accidental inflaba `contar`, `suma` y los testigos sin
alarma. Se cubre con una **clave de unicidad declarable por relación**, un nodo opcional
`["clave", [<campo>, …]]` a la cabeza de la lista de hechos. No es un operador ni una normalización
silenciosa — la bolsa no cambia—: es un contrato que el sensor declara y Oracle valida **antes de
medir**, fail-closed, nombrando la clave y la fila que la viola. Sin el nodo, cero cambios de
conducta; la multiplicidad intencional sigue siendo expresable sin declarar nada.
