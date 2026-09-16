# Encargo 0.25.0 — mutar unos sitios, y que la ronda diga que fue parcial

2026-09-16. Tarea [`20260915-201030-sitios`](../../tareas/20260915-201030-sitios/TAREA.md).
Revisa, mide y corta Claude.

## El problema, medido

`tools/mutar_codigo.py --objetivo` acepta archivos enteros y nada más fino. En el corte 0.21.0 cada
simplificación de unas pocas líneas de `nucleo/medida.py` o `nucleo/relacion.py` obligó a relanzar la
ronda completa del archivo —alrededor de una hora, tres veces— o a aplicar el mutante a mano sobre
una copia, que no queda registrado como ronda. La noche del 2026-09-15 al 16 volvió a pasar cuatro
veces.

Lo que falta es poder decir «mutá sólo esto», y —esto es la mitad del encargo— que el resultado **no
se pueda confundir con una ronda completa**. Un denominador recortado es la forma más barata de
sastrear una cifra: si una ronda parcial se informa igual que una completa, «227/227» pasa a
significar dos cosas distintas y nadie lo nota.

## Leer antes

- `tools/mutar_codigo.py`: `argumentos()`, `resolver_objetivos`, `objetivos_disponibles`, cómo se
  arma el informe y cómo se emiten los hechos con `--hechos`.
- `perfiles/python/mutacion_codigo.py`: cómo se descubren los sitios (`SitioMutacion` y su `id`
  `archivo:linea:columna:mutador`), `_correr_en_raiz`, y el diccionario `corrida_mutacion` que
  publica la evidencia de la ronda.
- `relaciones/corrida_mutacion.json` y el `CAMPOS_DE_RELACIONES` de su emisor: desde 0.22.0 los
  campos de una relación que emite Oracle están declarados al lado del emisor, y un test los compara
  con las filas emitidas. Esta vez **sí** hay que tocarlos.
- `catalogos/proceso/proceso.codigo_con_mutante_que_lo_mata.oracle` y
  `catalogos/proceso/proceso.ronda_mutacion_concluyente.oracle`: las dos medidas que juzgan una ronda.
- `ESPECIFICACION.md` §5 y `tools/cifras.py` (el numerador de sitios), para no contradecirlos.

## Qué hay que entregar

1. **Un filtro de sitios en `tools/mutar_codigo.py`**, con las dos formas, repetibles y combinables
   entre sí y con `--objetivo`:
   - `--lineas a-b` (rango inclusivo, sobre el objetivo);
   - `--sitio <id>` (el id completo del sitio, tal como lo imprime el informe).
   Un filtro que no selecciona ningún sitio es un error con mensaje claro, no una ronda vacía en
   verde: una ronda que no mutó nada no puede decir «todos muertos».
2. **La ronda declara que fue parcial.** El diccionario `corrida_mutacion` gana un campo —`parcial`,
   booleano— y, si te parece que hace falta para que la evidencia se defienda sola, el total de
   sitios que el objetivo tenía. Actualizá `relaciones/corrida_mutacion.json` y el
   `CAMPOS_DE_RELACIONES` del emisor.
3. **El informe en pantalla lo dice en su primera línea y en el resumen**, no en una nota al pie: una
   ronda parcial tiene que leerse como parcial de un vistazo, incluso en un log largo.
4. **Las dos medidas que juzgan rondas no aceptan una ronda parcial como si fuera completa.**
   `proceso.ronda_mutacion_concluyente` y `proceso.codigo_con_mutante_que_lo_mata`: decidí si las
   filas parciales se excluyen (con `requiere` o en el `donde`) o si hace falta otra medida, y
   escribilo con su `porque` y su `alcance`. **No inventes un umbral nuevo**: si la decisión correcta
   no se puede escribir sin cambiar `nucleo/`, anotala en el informe.
5. **Casos del corpus** para lo que agregues al catálogo, con las dos polaridades.
6. **Tests** en `tests/test_mutacion_codigo.py`: el filtro por rango, el filtro por id, los dos
   juntos, un filtro que no selecciona nada, que la evidencia declara `parcial`, y que una ronda sin
   filtro sigue declarando `parcial` en falso.
7. **La ayuda del comando** y el docstring del módulo, con un ejemplo de cada forma.

## Propiedad

**Agy:** `tools/mutar_codigo.py`, `perfiles/python/mutacion_codigo.py`,
`tests/test_mutacion_codigo.py`, `relaciones/corrida_mutacion.json`,
`catalogos/proceso/proceso.ronda_mutacion_concluyente.oracle`,
`catalogos/proceso/proceso.codigo_con_mutante_que_lo_mata.oracle`, `corpus/proceso/` para los casos
nuevos, y en `estudios/0.25.0-sitios/` sus `AVANCE-AGY.md` (primero, con el plan de archivos) e
`INFORME-AGY.md` (al final).

**Claude:** `nucleo/`, `ESPECIFICACION.md`, `NOTAS-DE-RELEASE.md`, `README.md`, `nucleo/version.py`,
`docs/`, `.github/`, `tools/cifras.py`, y **todo test existente**. Si un test existente contradice el
encargo, no lo edites: anotalo en el informe con su nombre y por qué.

## Reglas

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.** En
el informe no afirmes verificaciones que no corriste — no vas a poder correr ninguna, y está bien:
las corre Claude. Decilo así.

Cuidado con una trampa de esta tarea en particular: el arnés se muta a sí mismo. `mutar_codigo.py` no
es objetivo del perfil activo, pero `perfiles/python/mutacion_codigo.py` sí, y su ronda es de 227
sitios. Si tu cambio agrega ramas ahí, van a necesitar tests que las maten.
