# Un LLM escribe a + 1 y Oracle lo rechaza: la aritmética infija como azúcar de la superficie

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: oracle, metalenguaje, ergonomia, sintaxis


## Por qué

2026-09-24, Brian: Oracle tiene que amoldarse a cómo escriben los LLM, sin trabas. Un modelo escribe
`t2.turno == t1.turno + 1`; hoy el tokenizador rechaza `+` y `-`, y hay que escribir
`mas(t1.turno, 1)`. La fricción está verificada en `20260923-120207-ergonomia/VERIFICACION.md`
(entrada 1.1), con dos medidas navales reales que ya usan `mas`.

## Qué hacer

- Que la superficie infija lea `a + b`, `a - b` y `a * b` como azúcar de las escalares existentes
  `mas`, `menos` y `por` (`catalogos/escalares.py`). Precedencia usual (`*` antes que `+`/`-`),
  asociatividad a izquierda, paréntesis. La forma canónica NO cambia: `a + 1` produce exactamente
  `["mas", a, 1]`. `VERSION_ALGEBRA` queda en 0.8 y `VERSION_SINTAXIS` sube a 0.7 (menor: agrega).
- Que no rompa los literales negativos (`-1`) ni nada que hoy parsea.
- La ida y vuelta (`meta.sintaxis_ida_y_vuelta`) tiene que seguir: si el impresor emite `+`, que
  sea consistente; si sigue emitiendo `mas()`, que parsear las dos formas dé lo mismo.
- Mensaje claro para `/` u otros operadores que no existan (qué usar en su lugar).
- Tests que fallen hoy, ESPECIFICACION.md §0 (crónica de la sintaxis) y el manual.

### Nota (2026-09-24 11:14:16 UTC)

Leída la tarea y revisados _tokenizar, _Expr, _expr y las escalares mas/menos/por antes de editar. La forma canónica se conservará mediante nodos de llamada.

### Nota (2026-09-24 11:16:00 UTC)

Añadidos tests de precedencia, asociación, paréntesis, literales negativos, equivalencia infija/funcional e ida y vuelta; se comprobó que fallaban antes de implementar. Implementado lector infijo sin cambiar forma canónica ni impresor; actualizados versión, especificación y manual.

### Nota (2026-09-24 11:22:06 UTC)

Implementación terminada. Pruebas nuevas fallaron antes del cambio; suite completa final: 2435 tests, OK. python3 tools/cli.py test --rapido: VEREDICTO VERDE. python3 tools/cifras.py --actualizar: README.md actualizado. Reapuntados dos ids de equivalentes.json. VERSION_ALGEBRA sigue 0.8 y VERSION_DISTRIBUCION sigue 0.28.0. Sin commits por .git de sólo lectura.

### Nota (2026-09-24 11:23:38 UTC)

2026-09-24, revisión de Claude: queda una trampa. t1.turno-1 (sin espacios, como lo escribe un LLM) se lee como el campo «turno-1», no como una resta: IDENT_RE admite «-». En todo Oracle, Jam y LyraGASP el guion sólo aparece en nombres de macro (ninguno-requiere, ninguno-par), nunca en un campo, alias o relación dentro de una expresión. Dentro de una expresión, «-» tiene que ser siempre la resta: t1.turno-1 → ["menos", ["campo","t1","turno"], 1] y a.x-a.y → ["menos", …, …]. Los nombres de macro con guion tienen que seguir funcionando.

### Nota (2026-09-24 11:27:23 UTC)

Revisión final: el tokenizador usa EXPR_IDENT_RE sin guion sólo en expresiones; IDENT_RE y encabezados de macro conservan ninguno-par y ninguno-requiere. Tests nuevos reprodujeron fallos previos en t1.turno-1, a.x-a.y, turno-1 y a-b; ahora leen resta canónica. Error de nombre de campo con guion explica que «-» es resta. Manual y especificación actualizados; equivalentes.json reapuntado. Suite completa: 2436 tests, OK; test --rapido: VEREDICTO VERDE tras actualizar cifras. Sin commits.

## Próximo paso

Integrar este worktree después del corte 0.29.0 para incluir la sintaxis 0.7 en 0.30.0.
