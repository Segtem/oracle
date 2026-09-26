# El lector de la superficie sigue aceptando formas que ya no se enseñan: mas()/menos()/por() y relaciones .oracle con JSON adentro

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 04:10:07 UTC)

2026-09-26, origen: AUDITORIA.md de una-sintaxis (filas «Expresión» y «Relación»). DECISIÓN: en la superficie, una llamada mas(a, b), menos(a, b) o por(a, b) es error de sintaxis con el mensaje «escribí a + b» (o -, *); las escalares de dominio (las de escalares.py del proyecto) se siguen llamando como funciones, sólo estas tres tienen operador. col(p) y hecho(p): decidir con el mismo criterio si tienen una forma sin llamada (col(p) ↔ p) y quedarse con una. Una relación en un archivo .oracle con JSON adentro es error («una relación se escribe en .relacion»). Los lectores JSON de archivos .json se QUEDAN (formato canónico de intercambio y migración) y se documentan así. Va en la sintaxis 0.8. Medir antes en los consumidores: sus catálogos son JSON (usan ["mas", …], que es la forma canónica y no se ve afectada).

### Nota (2026-09-26 06:07:06 UTC)

2026-09-26, Claude: el código lo implementó Codex en el primer intento (se cortó por límite de uso antes de anotar) y entró a main con la rama de macro-invocacion-unica, que compartía worktree. Verificado ejecutando: mas()/menos()/por() son error «escribí a + b»; col(k) es error «escribí p en vez de col(p)»; una relación .oracle con JSON es error «una relación se escribe en .relacion». hecho(p) se queda: es la ÚNICA manera de pasar el hecho entero a una escalar (p sola es una columna), no una segunda escritura. Los tests de mas() y de la relación ya estaban; se agregó el de col(). Los lectores de archivos .json se quedan como formato de intercambio.
