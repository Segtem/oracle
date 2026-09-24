# Un LLM escribe a + 1 y Oracle lo rechaza: la aritmética infija como azúcar de la superficie

- ESTADO: ABIERTA
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

## Próximo paso

Codex implementa en un worktree; se une después del corte 0.29.0 y entra en 0.30.0.
