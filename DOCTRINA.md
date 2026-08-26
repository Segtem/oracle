# Reglas del repositorio — leelas antes de tocar nada

Oracle es un metalenguaje para escribir **medidas**: afirmaciones falsables sobre evidencia. El
proyecto existe para evitar un modo de falla concreto —que quien escribe una herramienta escriba
también su verificador y ambos compartan el mismo punto ciego—. Por eso las reglas de abajo NO son
estilo: son el producto.

## Innegociables

1. **Toda medida declara `umbral` con su defensa escrita (`porque`) y `alcance` (qué NO ve).** Sin
   eso no carga, y eso es deliberado.
2. **Fail-closed siempre.** Ante lo ambiguo, lo ausente o lo mal formado: `raise`, nunca un default
   silencioso, nunca un `except: pass`, nunca «si falta lo salteo».
3. **La mutación tiene que terminar en CERO sobrevivientes.** `python tools/mutar.py`.
4. **Nada entra al lenguaje hasta que una medida real lo necesite.** Si tu cambio agrega una
   capacidad que ninguna medida usa, no la agregues: decilo en el informe y parás.
5. **El primer eslabón de una cadena se mide por la cadena entera.** Si lo que te piden sólo sirve
   con dos cosas más que no están, decilo antes de escribir código muerto.
6. **No inventes sintaxis ni nodos nuevos.** Los cinco operadores son `de`, `donde`, `unir`,
   `agrupar`, `resumen`; `desde` es la tubería.

## Cómo se verifica (TODO tiene que dar verde antes de que informes)

```bash
python -m unittest discover -s tests -t . -q     # ~533 tests
python tools/cifras.py
python tools/corpus.py
python tools/aceptacion.py
python tools/diferencial.py
python tools/trazar.py
python tools/metamorficas.py
python tools/sintaxis.py --verificar
python tools/mutar.py                            # el más lento; 0 sobrevivientes
```

Si algo se pone rojo por tu cambio: **arreglalo o revertí**. No informes verde sin haberlo corrido.

## Prohibido

- `git stash`, `git clean`, `git checkout .`, `git reset --hard`, `git push`, `git rebase`.
  Trabajás en un worktree tuyo; commiteá ahí y nada más.
- Tocar `vendor/`.
- Reformatear JSON de catálogo con `indent=2`. El formato compacto —un nodo por línea— es
  deliberado: reformatearlo infla la proporción publicada sin que nada lo detecte.
- Bajar un test, marcarlo `skip` o aflojar una aserción para que pase. Si un test tuyo no pasa,
  el problema es tu código.
- Escribir en el informe que corriste algo que no corriste.

## Qué me devolvés

Un archivo `INFORME.md` en la raíz de tu worktree con:

- **Qué cambiaste**, archivo por archivo, y por qué.
- **La salida real** de cada verificación de arriba (pegada, no parafraseada).
- **Qué NO hiciste** y por qué. Esto vale tanto como lo que sí.
- **Lo que descubriste que no te pedí** — un supuesto falso en la tarea, un camino más barato, una
  contradicción en el repo. Si encontraste que la tarea no vale la pena, decilo: «no vale la pena»
  es una respuesta legítima y no la trato como fracaso.

Escribí en español rioplatense, sin adornos. Nada de «¡Listo!» ni resúmenes triunfales.
