# Cuatro preguntas de diseño sobre verdes que podrían no medir: sombra y sin evidencia, macros sin requiere, agregados vacíos y medidas no aplicadas

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: oracle, diseno, flaqueza


## Qué hacer

`auditoria-verde` (HALLAZGOS.md 3, 4, 5 y 6) deja cuatro preguntas que no son defectos comprobados sino
decisiones: (3) una sombra perdona también un `SIN EVIDENCIA`; (4) las macros base `ninguno`, `peor` y
`ninguno-par` no emiten `requiere`; (5) los agregados sobre cero filas dan 0 (lo dice la
especificación); (6) las medidas propias que no se aplicaron se listan pero no invalidan el
veredicto. Para cada una: qué pasa hoy (con archivo:línea y, si se puede, el caso del corpus que lo
muestra), qué alternativas hay, qué rompería cada una en Oracle, Jam y LyraGASP, y una recomendación
alineada con el «fail-closed» del proyecto. Brian decide. En `ANALISIS.md`.

## Avance

Se completó el análisis exhaustivo en `ANALISIS.md` de las cuatro decisiones de diseño derivadas de `auditoria-verde` (`tareas/20260925-023140-auditoria-verde/HALLAZGOS.md:72-166`):
1. Sombra y `SIN EVIDENCIA` (`nucleo/medida.py:479-495, 705-707`, `tools/juzgar.py:348`, `corpus/proceso/043-ausencia-total-sale-verde.caso:1-21`). Alternativas, impacto en Jam y LyraGASP, y recomendación fail-closed de no perdonar nunca `sin_evidencia` por sombra.
2. Macros base sin `requiere` (`nucleo/macros/ninguno.oracle:4-12`, `peor.oracle:4-12`, `ninguno-par.oracle:4-14` frente a `ninguno-requiere.oracle:4-13`). Alternativas, preservación del caso de uso de relaciones de infracciones donde `[]` es éxito, e impacto de versionado.
3. Agregados sobre cero filas dando 0 (`nucleo/algebra.py:580-593`, `ESPECIFICACION.md:802-803`, `diferencial/referencia/DECISIONES.md:25-32`). Demostración de por qué levantar error en `max([])` destruiría el funcionamiento de la macro `peor` ante cero transgresiones, y recomendación de preservar la especificación delegando la guarda en `requiere`.
4. Medidas no aplicadas en `juzgar` (`tools/juzgar.py:159-170, 348`, `nucleo/medida.py:710-714`, `tareas/20260916-201124-juzgar-omite/TAREA.md:8-17`). Alternativas, impacto en arquitecturas de CI particionadas en Jam y LyraGASP, y recomendación fail-closed de fallar por defecto en corridas totales exigiendo `--parcial` para ejecuciones modulares.

### Nota (2026-09-25 12:12:13 UTC)

2026-09-25, Brian delegó: «tomá las mejores decisiones». Decidido: 1.A (la sombra nunca perdona un SIN EVIDENCIA), 2.B (se conservan ninguno/peor/ninguno-par abiertas y se agregan peor-requiere y ninguno-par-requiere, con la regla escrita: si la relación es el universo a evaluar, se usa la variante -requiere), 3.A (los agregados sobre cero filas siguen dando 0; la guarda es requiere) y 4.C (oracle juzgar falla por omisión si hay medidas propias sin aplicar; --parcial lo permite explícitamente). Implementa Codex antes del corte 0.31.0.

### Nota (2026-09-25 12:20:39 UTC)

Implementadas 1.A, 2.B, 3.A y 4.C: sombra no perdona SIN EVIDENCIA (incluida aceptación L2); macros peor-requiere y ninguno-par-requiere; agregados vacíos conservan 0; juzgar falla ante medidas propias omitidas salvo --parcial. Pruebas nuevas reprodujeron fallas previas. Especificación, manual, tutorial, guía y sitio actualizados. Medición: batalla-naval 11/11 verde, primer-valor 1/1 verde; seguimiento-tareas con evidencia real 6 evaluadas, 4 rojas, 1 omitida, sigue rojo; con sólo referencia_seguimiento 1 verde y 6 omitidas, antes rc 0, ahora rc 1 y con --parcial rc 0. Verificaciones finales en curso; sin commits por .git de sólo lectura.

### Nota (2026-09-25 12:21:28 UTC)

Verificación final: python3 -m unittest discover -s tests: 2557 tests OK; tests de sombras: 8 OK; python3 tools/cli.py test --rapido VERDE: VERDE; python3 tools/guia.py: 9 pasos, 0 salidas pendientes; python3 tools/sitio.py: sin páginas vencidas; python3 tools/cifras.py --actualizar: README.md actualizado; equivalentes.json reapuntado por corrimiento en tools/verificar_instalacion.py y 7 tests de equivalencias OK. No se hicieron commits, según lo pedido.

## Próximo paso

Integrar el diff en un checkout con Git escribible y preparar el corte 0.31.0; esta tarea de implementación queda cerrada sin commits por la restricción de `.git`.
