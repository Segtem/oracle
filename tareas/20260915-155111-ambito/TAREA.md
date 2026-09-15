# meta.toda_medida_declara_su_ambito es del_origen a propósito y nada fija cuándo pasa a universal

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, metalenguaje, deuda

`PLAN-0.5.0-AMBITO.md` («El ámbito de la medida de presencia es temporal, y hay que decirlo»):
`meta.toda_medida_declara_su_ambito` se declara `del_origen` para no poner en rojo a los
consumidores con medidas anteriores a la cláusula, pero el estado final **exige** la declaración. Hoy
nada registra ni el plan ni la fecha del cambio a `universal`; el plan mismo avisa que es la clase de
decisión temporal que se vuelve permanente por olvido.

A hacer: medir cuántas medidas sin `ambito` declarado quedan en LyraGASP y Jam; si son cero, pasar la
medida a `universal`; si no, declarar el paso con fecha y cota (una sombra con `desde`, `porque` y
`cota` en los consumidores es el mecanismo que el proyecto ya tiene para esto).
