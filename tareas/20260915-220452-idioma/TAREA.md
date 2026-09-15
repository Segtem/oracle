# Oracle en inglés, con léxicos intercambiables: español hoy, francés o alemán después

- ESTADO: ABIERTA
- PRIORIDAD: 60
- ETIQUETAS: oracle, metalenguaje, idioma

Pedido del dueño (2026-09-15): que Oracle esté todo en inglés y que el léxico pueda ponerse en español,
y más adelante en otros idiomas (francés, alemán…).

## Medido (2026-09-15, con 0.21.0/0.22.0)

Hoy todo es español, y en capas distintas que no se traducen igual:

| capa | qué hay | cuánto |
|---|---|---|
| forma canónica (JSON guardado) | cabezas `desde`, `de`, `donde`, `resumen`, `unir`, `agrupar`, `y`/`o`/`no`, agregados, `umbral`, `requiere`, `filas`, `ambito`, `alcance`, `campo`/`hecho`/`col` | la define `ESPECIFICACION.md` §2–§3 |
| vocabularios cerrados | `segun` (`contrato`, `convencion`, `medicion`, `tanteo`), `ambito` (`universal`, `del_origen`), etiqueta, procedencia y detección de un caso | 5 vocabularios (`nucleo/vocabulario.py`, `nucleo/caso.py`) |
| superficie `.oracle` y `.caso` | palabras (`medida`, `ninguno`, `porque`, `segun`…), macros (`ninguno`, `ninguno-par`, `ninguno-requiere`, `peor`), claves de caso (`titulo`, `sintoma`, `leccion`…) | `nucleo/sintaxis.py`, `nucleo/caso.py`, `nucleo/macros/` |
| CLI y TQL | 6 sustantivos, decenas de verbos y banderas; `y`, `o`, `no`, `cualquiera`, `prioridad`, `menor`… | `tools/cli.py`, `tools/tareas_consulta.py` |
| nombres | ids de medida (61 en Oracle), relaciones del lenguaje (26) y sus campos, relaciones declaradas (12) | catálogo, emisores, `relaciones/` |
| mensajes | errores, avisos y salidas | ~988 `print`/`raise` con texto en `nucleo/`, `tools/`, `perfiles/` |
| documentación | ESPECIFICACION (883 líneas), README (780), 10 páginas en `docs/`, manual generado | |
| consumidores | escriben todo en español y lo tienen que seguir leyendo | LyraGASP 27 medidas y 190 casos; Jam 41 medidas y 32 casos |

## Por qué se puede

La superficie ya está separada de la forma canónica: el lector y el impresor traducen entre texto y JSON
con ida y vuelta verificada (`tools/sintaxis.py --verificar`), y los vocabularios cerrados ya declaran su
sentido junto a su nombre. Un léxico es una tabla más en esa frontera: palabra de la superficie ↔ símbolo
canónico. Cambiar de idioma no toca el álgebra si lo que se guarda no depende del idioma.

## Decisiones del dueño antes del plan

1. **Idioma de la forma canónica.** Pasarla a inglés (`from`, `where`, `summary`…) cambia la forma
   guardada de todas las medidas y casos: sube la MAYOR del álgebra (1.0) y exige migrar consumidores y
   re-derivar la referencia del diferencial. Alternativa: la forma canónica queda como está y el inglés es
   un léxico más, con inglés por omisión en la superficie.
2. **Qué es léxico y qué es dato.** Las palabras del lenguaje y de los vocabularios cerrados se traducen;
   ¿los ids de medida de Oracle (`meta.toda_medida_…`), los nombres de relaciones del lenguaje y sus
   campos, y los textos `porque`/`alcance` del catálogo base también? Los ids de un consumidor son suyos y
   no se tocan.
3. **Cómo declara su idioma un archivo.** Una primera línea como la de versión (`idioma es`), el
   `oracle.json` del proyecto, o las dos con precedencia.
4. **Mensajes y documentación.** Catálogo de mensajes por idioma o sólo inglés; documentación en inglés
   con la española como traducción mantenida, o sólo inglés.
5. **Orden.** Probablemente varios cortes: léxico de superficie y vocabularios (con español e inglés),
   luego CLI y TQL, luego mensajes y documentación, luego un tercer idioma para probar que la tabla alcanza.

## Criterio de salida (a precisar en el plan)

Un proyecto escrito en español carga y da los mismos veredictos; el mismo catálogo impreso en inglés y
releído es idéntico (ida y vuelta por léxico); agregar un idioma es agregar una tabla y sus tests, sin
tocar el lector, el impresor ni el álgebra; LyraGASP y Jam no cambian una línea para seguir andando.
