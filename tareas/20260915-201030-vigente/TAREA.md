# ESPECIFICACION §0 no dice de un vistazo cuál es la versión vigente

- ESTADO: ABIERTA
- PRIORIDAD: 52
- ETIQUETAS: oracle, metalenguaje, docs

La referencia independiente re-derivada contra 0.7 registró como ambigüedad
(`diferencial/referencia/DECISIONES.md`, «Version del algebra vigente»): §0 mezcla la crónica de los
cortes —varios dicen «`VERSION_ALGEBRA` queda en `0.6`»— con la regla de subida, y quien sólo lee la
especificación tiene que deducir la versión vigente de la última línea de la historia. Una
especificación que otro autor implementa sin ver el núcleo tiene que decirla explícitamente.

A hacer: una línea al principio de §0 con las versiones vigentes (álgebra, sintaxis) que se actualice
en cada corte —y un test o una medida que la compare con `nucleo/version.py`, para que no envejezca
como la prosa—; evaluar si la crónica de cortes pertenece a `NOTAS-DE-RELEASE.md` y no a §0.
