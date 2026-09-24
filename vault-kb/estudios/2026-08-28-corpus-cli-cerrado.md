# El custodio del corpus quedó cerrado por mutación

Fecha: 2026-08-28

## Punto de partida reproducido

La ronda fresca inicial sobre `tools/corpus.py` produjo 123 mutantes: 71 murieron, 51
sobrevivieron y uno terminó como error de arnés. No hubo timeouts ni equivalentes declarados.
El error de arnés correspondía al comparador del guard canónico de `__main__`: al mutarlo, el
módulo ejecutaba la CLI durante la carga prioritaria.

## Qué se cambió

- Se extrajo la lectura Git a `_git_del_repositorio`, con contrato observable para código de
  salida, excepciones, captura de texto y timeout.
- Se normalizó el remoto sin una bifurcación especial para HTTPS y se fijó que una ruta remota
  profunda conserve sólo `propietario/repositorio`.
- Se eliminaron guardas y valores por defecto redundantes en la ruta nueva y el listado.
- El entrypoint selecciona `main` por nombre sin un comparador mutable durante la importación.
- Se agregó `tests/test_corpus_cli.py`, que fija rutas, creación sin sobrescritura, metadatos Git,
  generación, validación de procedencia, resumen, listado y despacho completo de `main`.
- `tests.test_corpus_cli` pasó a ser la primera prioridad de mutación de esta herramienta.

Durante el cierre apareció una rama que elegía entre `"1 con medida"` y exactamente el mismo
texto interpolado. Se eliminó la redundancia en producción; no se la ocultó como equivalente.
También apareció una falta observable en `main(None)`, corregida con una prueba sobre
`sys.argv[1:]`.

## Resultado fresco

Comando:

```text
python tools/mutar_codigo.py --objetivo tools/corpus.py \
  --manifiesto /tmp/progreso-corpus-cierre-3.json
```

Resultado: **112/112 mutantes muertos**, 0 supervivientes, 0 timeouts, 0 errores de arnés y
0 equivalentes declarados. La salida completa quedó en `/tmp/mutacion-corpus-cierre-3.txt`.

La reducción de 123 a 112 sitios proviene de simplificar decisiones redundantes, no de exclusiones
del inventario ni declaraciones de equivalencia.
