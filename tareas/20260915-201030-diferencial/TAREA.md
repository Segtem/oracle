# El diferencial no ejercita requiere con condición ni relaciones con variantes

- ESTADO: CERRADA
- PRIORIDAD: 74
- ETIQUETAS: oracle, metalenguaje, diferencial

Medido en el corte 0.21.0 (2026-09-15): `diferencial/simulacion.json` son 4 mundos × 3 medidas de
simulación, y ninguno usa `requiere` con condición ni una relación con `variantes`. La referencia
independiente se re-derivó contra el álgebra 0.7 y sus 21 tests pasan, pero el fixture regenerado
«de acuerdo» no compara a Oracle con la referencia en nada de lo que entró en 0.7: lo que aportó la
referencia fueron las dos decisiones (sin cortocircuito entre filas ni entre entradas), encontradas
leyendo, no el contraste. Es la misma clase de agujero que documenta b250e6c: cada extensión apaga un
pedazo del diferencial si nadie agrega mundos.

A hacer: mundos del diferencial con `requiere` con condición —filas que cumplen, ninguna, otra
variante, un campo ausente en una fila posterior, una relación vacía antes de una condición que
levanta— y con evidencia de `mutante` mezclada; regenerar y clasificar cada desacuerdo como en
`diferencial/referencia/PROCEDENCIA.md`.
