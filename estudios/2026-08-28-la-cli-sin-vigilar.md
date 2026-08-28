# La CLI, medida por primera vez (2026-08-28)

## El hueco

`tools/mutar_codigo.py` tenía 22 objetivos: los de `nucleo/`, dos de `oracle_metalenguaje/`, dos de
`perfiles/python/` y `tools/cifras.py`. **Toda la CLI estaba afuera.**

Se descubrió aplicándole al proyecto su propia vara: el 2026-08-27 se agregaron dos verbos
—`oracle medida probar` y la derivación de `fecha`/`origen` desde git— y no se les pudo correr la
mutación porque el arnés se negaba:

```
ValueError: objetivos desconocidos o fuera del perfil activo: ['tools/medida.py']
```

## Los números

| | sitios | sobrevivientes | |
|---|---:|---:|---|
| `tools/corpus.py` | 123 | **51** | 41 % · corrida completa |
| `tools/cli.py` | 119 | **68** | 57 % · **parcial**, la corrida se cortó |
| `tools/medida.py` | 115 | **67** | 58 % · **parcial**, la corrida se cortó |
| `nucleo/*`, todos | ~2.400 | **0** | 0 % |

⚠️ Dos de las tres son **parciales**: la corrida se corta en seco cerca de los 120 sitios, sin error
ni traza, y no se llega a la línea de resumen. No está diagnosticado. Los porcentajes de esas dos son
sobre lo evaluado, no sobre el total, y el total real es mayor.

## Qué dice

El núcleo está vigilado hasta el último `and` —cero sobrevivientes en todos sus archivos, medido
repetidas veces— y **la CLI tiene más de la mitad de sus roturas pasando sin que nada se queje.**

No es casualidad dónde caen: manejo de argumentos, mensajes de error, textos de ayuda. Lo ejercitan
tests que recorren el camino feliz. Y es justo la superficie que toca quien está aprendiendo el
lenguaje: donde un error se ve más y donde menos se estaba mirando.

## El matiz, para no exagerar

Un mutante vivo en la CLI pesa menos que uno en el álgebra. Si se rompe un texto de ayuda, alguien
lee algo raro; si se rompe un `unir`, un veredicto sale mal en silencio. Pero 57 % es demasiado para
decir «son sólo mensajes» sin haberlos mirado uno por uno.

## Lo que falta

1. Terminar las dos corridas parciales, y antes averiguar por qué se cortan.
2. Mirar los sobrevivientes **de a uno**. Ojo con la trampa que ya apareció dos veces esta semana:
   si un mutante sobrevive en una guarda que revalida algo que otra capa ya garantiza, la salida no
   es inventar una entrada inválida para recorrerla —es **borrar la guarda**. El 2026-08-27 se
   sacaron seis assertions que pasaban `None`, `[]` y `["campo"]` a funciones que sólo reciben
   árboles validados: el código y los tests se sostenían mutuamente y ninguno tocaba nada real.
3. Decidir si estos tres objetivos entran al workflow. Hoy **no**: la cuenta agotó los 2.000 minutos
   de Actions y la matriz ya está corta a propósito.
