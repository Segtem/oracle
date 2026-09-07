# El paquete medía con 5 de 29 mutadores

**Fecha:** 2026-09-07. **Estado:** arreglado en 0.10.0.

Apareció comparando el árbol contra el wheel al cerrar 0.9.2, y no buscándolo. El mismo comando,
sobre el mismo proyecto, daba distinto según de dónde saliera Oracle:

| | desde el paquete | desde el árbol |
|---|---|---|
| Jam | 315 mutantes · **0** sobrevivientes | 428 · **9** |
| LyraGASP | 116 mutantes · **0** sobrevivientes | 139 · **2** |
| `oracle test` sobre Jam | **VERDE** | **ROJO** |

## La causa

`mutadores/` —el directorio con los 24 mutadores del segundo autor— **no estaba en
`pyproject.toml`**, así que nunca viajó. Una instalación mutaba con los **5** mutadores propios en
vez de los **29** declarados, y el informe no lo mencionaba.

Y no es una diferencia de relleno: los sobrevivientes reales de los dos consumidores salen de
`alejar_limite_de_defecto` y `hacer_estricta_comparacion_interna`, **los dos del segundo autor**.
Desde el paquete publicado eran literalmente invisibles.

## Por qué duele

Es el defecto que `DECISION-011` fue a arreglar, sobreviviendo en lo que se distribuye. Esa decisión
lo dice sin rodeos:

> «un mutador que nadie escribió no puede producir un sobreviviente. El 100% acotaba menos de lo que
> parecía, y el `README` lo declaraba como límite conocido sin hacer nada al respecto.»

Se escribió un segundo autor en aislamiento verificable para cerrarlo, y después no se lo distribuyó.
**Todo consumidor siguió viviendo en el mundo anterior a la decisión, sin que nada se lo dijera.**

El código conocía la ausencia y la manejaba con cuidado para no romperse, con un comentario que la
justificaba: «ahí el mutador no está ausente porque alguien lo excluyera sino porque nadie lo
distribuyó, y eso no es un defecto de nadie». Esa frase describía bien el mecanismo y era una coartada
para el empaquetado. Medida la consecuencia, sí era el defecto de alguien.

## El arreglo, en dos partes, y las dos hacen falta

**Empaquetarlos**, como `oracle_metalenguaje.mutadores` y no como `mutadores` de nivel superior. Eso
último repetiría un defecto ya vivido: hasta 0.3.3 instalar la biblioteca registraba `tools` como
nombre de nivel superior y **le borraba al consumidor su propio `tools/`**. El resolvedor prueba el
nombre del paquete PRIMERO, para que un `mutadores/` que el consumidor tenga en su cwd no le gane al
distribuido.

**Informar el denominador**, que es lo que sirve donde empaquetar no llega: quien ya tiene instalada
una versión anterior a 0.10.0 no se entera de nada por más que se corrija el paquete. Ahora el
informe dice `con 29 mutadores: 5 de quien escribió el lenguaje y 24 de otro autor`, y cuando faltan:
`⚠ con 5 mutadores, TODOS del mismo autor que las medidas … este número acota menos de lo que
parece`.

## Lo que NO se hizo

**No se agregó una medida al catálogo.** Sería universal, se pondría roja en el consumidor, y el
consumidor **no puede arreglar el empaquetado de Oracle**. Es el mismo razonamiento del corte
anterior y de `DECISION-012`: «un rojo sobre el que el receptor no puede actuar enseña a ignorar la
herramienta». La cobertura de mutadores pertenece al arnés operativo, no al catálogo de evaluación.

**No se cambió `mutadores_declarados_por_sus_autores()`.** Su trabajo es distinguir «excluido» de «no
distribuido», y lo hace bien: si fingiera que el módulo existe, acusaría al arnés del consumidor de
filtrar un mutador que nadie le dio. Lo que faltaba estaba afuera de esa función.

## La versión, y una corrección

`VERSION_DISTRIBUCION` **0.9.2 → 0.10.0**. Se escribió primero `0.9.3`, con el argumento de que la
exigencia ya existía y el paquete simplemente no la aplicaba. Es cierto, y es la explicación de por
qué corresponde hacerlo — no una razón para esconderlo en un parche.

El criterio que este proyecto practica es si un consumidor puede cambiar de color, y acá **cambian
los dos, medido**: Jam y LyraGASP pasan de VERDE a ROJO al actualizar sin haber tocado una línea. En
0.9.0 la menor subió por un cambio de color que era *posible*; éste es el caso más claro hasta ahora.
Un parche dice «actualizá sin mirar», y esto pone en rojo una corrida que ayer daba verde.

## Un efecto que conviene decir en voz alta

Los números de mutación que este proyecto reportó sobre sus consumidores durante el día —«116/116
sin sobrevivientes» en LyraGASP, entre otros— salieron del Oracle instalado. Eran ciertos y estaban
medidos, pero sobre un espacio **5,8 veces más chico** de lo que parecían. No se reescriben los
commits donde están; queda escrito acá que hay que leerlos con este dato al lado.
