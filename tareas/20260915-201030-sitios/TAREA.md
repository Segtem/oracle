# mutar_codigo sólo muta archivos enteros

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: oracle, mutacion, idea

`tools/mutar_codigo.py --objetivo` acepta archivos; no hay forma de mutar sólo unos sitios o un rango
de líneas. En el corte 0.21.0 (2026-09-15) cada simplificación de unas pocas líneas de
`nucleo/medida.py` o `nucleo/relacion.py` obligó a relanzar la ronda completa del archivo (~1 h cada
una, tres veces), o a verificar sobrevivientes aplicando el mutante a mano sobre una copia, que no
queda registrado como ronda.

A decidir: `--sitio <id>` repetible o `--lineas a-b`, con la condición de que el informe diga que la
ronda es parcial y no pueda confundirse con una completa (un denominador recortado es la forma más
barata de sastrear la cifra; ver `tools/cifras.py`). Relacionada: `20260915-112728-memoria`.
