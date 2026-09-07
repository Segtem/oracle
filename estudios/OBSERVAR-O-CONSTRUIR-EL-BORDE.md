# Observar o construir: qué procedencia le toca a un caso de borde

**Fecha:** 2026-09-07. **Estado:** decidido para los once sobrevivientes de 0.10.0; la pregunta
general queda abierta y con deuda declarada.

Cuando Oracle 0.10.0 empezó a distribuir los mutadores del segundo autor, sus dos consumidores
vieron por primera vez **11 mutantes sobrevivientes** que siempre habían tenido. Matarlos pide casos
cuyo valor caiga en una franja estrecha: un gap entre 1,0 y 2,0 cm, un volumen exactamente igual a
0,001, una malla partida en exactamente 2 piezas.

La pregunta que abrió el usuario fue directa: *«¿no sería lo normal observarlos?»*. Se puso a los dos
agentes a defender posiciones opuestas, cada uno con la consigna de terminar reconociendo el punto
más fuerte del otro.

## La posición de que observar debería ser la norma

**El mejor argumento fue que fabricar un asset no equivale a fabricar su lectura.** Construir en
Unreal una separación nominal de 1,5 cm y pasarla por el adaptador real le da la oportunidad a las
transformaciones, las unidades, la precisión o la extracción de **contradecir** ese 1,5. Escribir
`gap: 1.5` en un archivo suprime todas esas oportunidades de descubrir un error.

Y un segundo, incómodo: la medida que persigue la evidencia fabricada
—`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`— salta cuando *todos* los casos de una
medida son fabricados, así que **una sola observación lejana puede acompañar cien bordes inventados
sin que nadie proteste**. Es un piso fácil de confundir con un techo.

## La posición de que construir es el método para el borde

**El mejor argumento fue que son dos preguntas incompatibles.** Un caso observado contesta «¿qué
defectos produce la práctica real cuando nadie está forzando los números?»; un caso de borde
contesta «¿dónde termina exactamente la frontera del predicado?». El borde no es un evento del
mundo: es un límite de la regla. Exigirle al mundo un caso en el límite exacto confunde observación
con calibración.

Y el argumento de honestidad: como `estudios/OBSERVAR-0.8.1-RECORRIDO.md` midió con ataques reales,
**nadie puede distinguir una corrida de una transcripción**. Así que la etiqueta descansa en la
palabra de quien la escribe, y abaratarla le quita significado a los casos que sí salieron del
mundo. Modelar un cubo para complacer a un mutante y llamarlo `observada` es fabricación con más
pasos.

## Lo que los dos concedieron, y que dejó de ser teórico en el acto

Los dos, por separado, concedieron el mismo punto: **un valor de borde escrito a mano supone un
universo platónico** donde el sensor emite números puros, y queda ciego a si ese valor es siquiera
representable.

Diez minutos antes de leer los informes, eso pasó. El primer diseño del caso de `colocacion.bounds`
—cuyo predicado es `volumen <= 0.001`— usaba una pieza de 0,1 × 0,1 × 0,1. En punto flotante:

```
0.1 * 0.1 * 0.1  =  0.0010000000000000002   →  NO es <= 0.001  →  la medida daba VERDE
0.001 * 1.0 * 1.0 =  0.001                  →  sí              →  ROJO, y mata al mutante
```

**El borde que se creía estar tocando no existía.** Y no lo encontró la lectura del diseño sino la
comprobación contra el mutante, que es la única que mira lo que pasa de verdad.

## La decisión, y lo que se lleva del debate

Para estos once, **`construida`**: interrogan a la regla, no al mundo. Pero el debate cambió cómo se
escriben:

- El `sintoma` de cada caso dice **por qué ese valor exacto** y a qué mutante mata, no sólo qué
  defecto describe. Un borde sin su justificación es un número mágico.
- El caso de `colocacion.bounds` lleva escrito el traspié del `0.1³`, porque es la prueba de que un
  borde escrito a mano puede no existir.
- Queda **deuda declarada**: cuáles de los once podrían observarse el día que se abra el editor. El
  corpus no debe premiar una muerte sintética como si fuera cobertura observada.

**El único que se intentó observar no se pudo.** El caso de `malla.solido_esta_cerrado` necesita
`aristas_sueltas == 1`, que sólo produce un triángulo degenerado —los tres índices iguales—. Se
buscó en toda la evidencia guardada del consumidor y **sólo aparecen los valores 0 y 3**, que es
exactamente lo que predice una búsqueda exhaustiva sobre mallas bien formadas. El 1 existe, es un
defecto real y frecuente en mallas de juego, y hoy no se puede ver sin abrir Unreal.

## La pregunta general queda abierta

Nada de esto decide que construir sea la norma. La posición contraria tiene un pedido concreto y
razonable: que observar sea **lo barato**. `tools/observar.py` ya captura, registra y revalida; lo
que falta es conectarlo al trabajo cotidiano de los consumidores y a los adaptadores que necesitan
el editor. Mientras eso no pase, cada caso construido debería declarar qué recorrido se omitió — que
es lo que se hizo acá.
