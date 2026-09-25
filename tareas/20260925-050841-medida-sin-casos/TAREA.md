# oracle test da VERDE con medidas que no tienen ningún caso: no se mutan ni se nombran

- ESTADO: ABIERTA
- PRIORIDAD: 97
- ETIQUETAS: oracle, mutacion, flaqueza, falso-verde


## Qué pasó

2026-09-25, Claude, armando la guía de la batalla naval. Proyecto con 11 medidas y 10 casos que
fijan sólo 2 de ellas (`naval.barcos_dentro_del_tablero` y `naval.tiros_dentro_del_tablero`); las
otras nueve no tienen ningún caso. Reproducción: [reproducir.sh](reproducir.sh).

- Con `catalogo_base: false`: `oracle test` → `mutantes de medida: 36 · murieron 36 · sobrevivieron
  0` y **VEREDICTO: VERDE**. Las nueve medidas sin casos no se mutan (36 = 2 medidas × 18 mutadores)
  y nada las nombra.
- Con `catalogo_base: true`: `meta.toda_medida_esta_fijada` da **0**, o sea tampoco las ve. El
  proyecto sale ROJO, pero por otras metas (evidencia fabricada, unidades), no por esto.

Es un falso verde de primer orden: el lector de la guía, o un agente, escribe once reglas, prueba dos
y ve verde. Es el verde que decora que el proyecto persigue.

## Qué hacer

Que una medida del catálogo propio sin ningún caso que la ejerza haga fallar `oracle test` con un
mensaje que la nombre y diga qué hacer (escribir un caso rojo y uno verde), **con o sin catálogo
base**. Revisar por qué `meta.toda_medida_esta_fijada` da 0 en ese escenario y corregir la medida o
su emisor. La mutación tiene que informar las medidas que no pudo mutar por falta de casos. Tests
que fallen hoy con el escenario de `reproducir.sh`. Revisar que el ejemplo `ejemplo/batalla-naval`
siga VERDE (tiene casos para las 11).

## Próximo paso

Codex implementa.
