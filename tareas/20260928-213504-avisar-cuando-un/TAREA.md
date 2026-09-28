# avisar cuando un cambio al catálogo afloja un umbral, borra un caso o agranda un alcance

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: oracle

### Nota (2026-09-28 23:24:12 UTC)

Hecho. oracle cambios [--desde <ref>] (tools/cambios.py) compara el árbol de trabajo contra un commit, leyendo el ref con git show y los mismos cargadores. Regla: aflojar no se prohíbe, se declara. Error (sale 1): umbral aflojado con el mismo porque, requiere quitado, cota de sombra subida con el mismo porque. Aviso: umbral aflojado con porque nuevo, medida borrada, caso borrado o con otra etiqueta, alcance cambiado, sombra nueva. Cambiar de sentido nunca cuenta como endurecer. En el CI corre en el job contratos: en un PR contra la base, en un push contra el commit de antes del push. Mutación: 52/52 más un equivalente declarado (el check=True de un git show sobre lo que ls-tree acaba de listar), con --timeout 600. oracle test VERDE, 2158 tests. Límite conocido: el ref se expande con las macros de hoy; si usaba una macro ya borrada no carga y lo dice. El alcance se señala cuando cambia, no cuando se agranda: si ve más o menos es prosa.
