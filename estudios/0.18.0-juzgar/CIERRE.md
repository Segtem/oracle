# Cierre 0.18.0 — `oracle juzgar`

2026-09-15. Tarea [`20260915-010206-juzgar`](../../tareas/20260915-010206-juzgar/TAREA.md).
Implementó agy; revisó, completó y verificó Claude. El dueño eligió «plan + agy, como 0.17» y la
publicación en PyPI queda a su cargo.

## Qué se entregó

- `tools/juzgar.py`: `oracle juzgar` / `oracle proyecto juzgar`. Catálogo efectivo, sombras,
  `--medida`, `--json`, códigos 0/1/2, lectura acotada a 50 MiB y UTF-8 estricto.
- `ejemplo/seguimiento-tareas/evaluar.py` retirado; README del ejemplo, `verificar_instalacion` y
  `test_tareas_p4_revision` pasan al verbo.
- CI juzga el `tareas/` del propio Oracle con las tres políticas de seguimiento.
- `tools/juzgar.py` como custodia de mutación (lista, prioridades y matriz de CI).

## Recorrido

1. [Plan](../../PLAN-0.18.0-JUZGAR.md) y [encargo](ENCARGO-AGY.md). Antes de escribirlos se midió
   que el `tareas/` de Oracle ya pasaba las tres políticas, así que el paso de CI nace verde.
2. Claude escribió `tests/test_juzgar_revision.py` contra el encargo antes de leer el código.
3. P0 ([avance](AVANCE-AGY.md), confirmado con número en la [revisión](REVISION-CLAUDE.md)):
   `Motor.desde_proyecto` 57 medidas contra 37 de `catalogo_efectivo`; además ignora sombras.
4. Primera entrega: 14 de 15 tests de revisión. Defectos R1–R6 (sombras, despacho triplicado, alias
   hacia sí mismo, `except Exception`, tokens sueltos, documentación con topes inventados). Ronda de
   correcciones de agy; 43 tests del verbo en verde.
5. Claude: retiro de `evaluar.py`, paso de CI, custodia, `test_reportar` y manual por el verbo nuevo.
6. Aparte, al disparar por primera vez el job de mutación de código de CI: tres fallas del job
   (objetivo sin registrar, `setuptools`, plazo de 120 s) y cuatro sobrevivientes de `nucleo/mutacion.py`,
   cerrados con tests y comprobados aplicando cada mutante a mano.

## Verificación final

| Módulo | Muertos | Vivos | Timeouts | Errores de arnés |
|---|--:|--:|--:|--:|
| `tools/juzgar.py` | 112 | 0 | 0 | 0 |
| `tools/cli.py` | 536 | 0 | 0 | 0 |

Sin equivalentes declarados. Tres rondas sobre `juzgar.py`: 14 sobrevivientes en la primera, 12 en
la segunda y 1 en la tercera (`ensure_ascii`), cerrados borrando lo que no tenía conducta —parámetros
que nadie pasaba, un chequeo de estructura que `resolver` ya hacía, la entrada `python tools/juzgar.py`
que estaba rota— y con tests para lo que sí la tenía. `cli.py` tuvo 4 timeouts en su primera ronda:
un test de `reportar --help` sin stdin que colgaba la suite cuando el mutante hacía preguntas.
Rondas en copias aisladas con su propio `TMPDIR`; logs en [verificacion/](verificacion/).

- Suite completa: 1987 tests en verde.
- `tools/verificar_instalacion.py`: `WHEEL OK`, con `oracle juzgar` desde el wheel en verde y con el
  enlace roto construido.
- Paso nuevo de CI simulado local: verde en las tres políticas sobre el `tareas/` de Oracle.
- `tools/cifras.py` sin deriva (1987 tests · 7065 sitios de mutación de código); manual regenerado.

## Tareas abiertas que deja

- `20260915-010454-motor`: la fachada `Motor` con otra selección y sin sombras.
- `20260915-010452-commits`: los commits como hechos del tracker (0.19.0).
- `20260915-010453-sufijo`: `tarea nueva` arma un ID largo con el título.
