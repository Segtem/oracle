# Decimocuarta auditoría adversarial: una sintaxis

2026-09-26. Apliqué el criterio de `ESPECIFICACION.md`, sección «La superficie tiene su propia versión»: un texto por árbol, exceptuadas las líneas completas cuyo primer carácter no blanco es `#`; el orden de relaciones, columnas y claves de objeto, salvo `origen`, pertenece al árbol. JSON en `.json` sigue siendo intercambio; sólo lo cuento si un componente lo **produce como caso, medida o relación de un corpus o catálogo**. Trabajé con sondas temporales en `/tmp`. No cambié código ni hice commits.

## Hallazgo: un productor interno vuelve a escribir casos JSON

`tools/sondear_procedencia.py:61-72` construye un `corpus/dominio/` temporal y escribe allí cada caso con `json.dumps` en `<id>.json`. Luego `hechos()` lo carga mediante `cargar_casos`. No es una indicación al usuario para que escriba JSON ni un corpus persistente, pero sí es un productor empaquetado de **casos de corpus** en la segunda forma. Ejecuté:

```bash
python3 tools/sondear_procedencia.py
PYTHONPATH=. python3 - <<'PY'
from tools.sondear_procedencia import escribir_corpus, SONDAS
from nucleo.caso import cargar_casos
from pathlib import Path
r = escribir_corpus(SONDAS['un_caso_observado_no_dice_de_donde_salio'][0])
print([(p.name, p.suffix) for p in sorted(r.rglob('*')) if p.is_file()])
print(len(cargar_casos(r)))
print(next(p for p in sorted(r.rglob('*')) if p.is_file()).read_text()[:90])
PY
```

Salida recortada:

```text
PROCEDENCIA — 2 sondas sobre corpus reales ...
  ✓ un_caso_observado_no_dice_de_donde_salio
  ✓ todos_los_observados_dicen_de_donde_salieron
[('001-corrida-sin-registro.json', '.json'), ('002-corrida-con-registro.json', '.json'), ('003-escrito-a-mano.json', '.json')]
3
{"fecha": "2026-09-07", "titulo": "t", "etiqueta": "falso_verde", ...
```

La escritura sucede dentro de `escribir_corpus`, no en la capa de intercambio de `juzgar` ni en `oracle.json`. El wheel que construí contiene `tools/sondear_procedencia.py`. Este hallazgo tiene alcance limitado al diagnóstico interno; no demuestra que una entrada de autoría acepte dos grafías de superficie.

## Inserción exhaustiva de comentarios

Ejecuté `PYTHONPATH=. python3 /tmp/oracle_audit14_matrix.py`. El script temporal tomó cuatro archivos reales: `catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle`, `nucleo/macros/ninguno.oracle`, `corpus/simulacion/301-simulador-que-ignora-la-semilla.caso` y `relaciones/mutante.relacion`. En **cada límite de línea**, antes de la primera y después de la última, insertó `# auditoria 14` con sangría vacía, cuatro espacios y tab. Para cada variante comparó `leer` con el árbol original; llamó al cargador de la superficie; comprobó `sin_comentarios(texto) == imprimir(árbol)`; ejecutó `cmd_formatear(..., escribir=True)` y verificó que preservó exactamente el texto; y llamó a `lsp.diagnosticar` esperando cero diagnósticos. Salida completa:

```text
medida lines 6 positions 7 probes 21 {'pass': 21}
macro lines 9 positions 10 probes 30 {'pass': 30}
caso lines 21 positions 22 probes 66 {'pass': 66}
relacion lines 19 positions 20 probes 60 {'pass': 60}
```

Esto reejecuta, ahora sin fallas en esas posiciones, el hallazgo de AUDITORIA-13 sobre `origen`, `sintoma`, `evidencia` y `leccion` de `.caso`, así como el de AUDITORIA-12 sobre `.relacion`. Es una prueba exhaustiva **de posiciones de esos cuatro archivos**, no de todas las estructuras posibles del lenguaje.

## Grafías anteriores y bordes de la forma única

Ejecuté `PYTHONPATH=. python3 /tmp/oracle_audit13_probe.py`, `PYTHONPATH=. python3 /tmp/oracle_audit13_legacy.py` y `PYTHONPATH=. python3 /tmp/audit12_matrix.py`. Esos scripts temporales comparan lector, impresor y cargador sobre fuentes reales y variantes de AUDITORIA-2 a -13; el primero también llama al LSP. Salidas recortadas, conservando cada clase:

```text
medida/caso/relacion/macro: base y comentarios al inicio, con sangría y al final: igual, OK, LSP=0
medida/caso/relacion/macro: CRLF, falta de LF final y blanco extra: distinto, error de forma, LSP=1
medida/caso/relacion/macro: BOM e inline # sobre código: error de lector, LSP=1
medida triple_espacio, version, cientifica, resta_sin_espacios, parentesis: distinto, MedidaMalDeclarada forma
medida agrupar_invertido, requiere_doble: distinto, MedidaMalDeclarada forma
medida funcion_mas, funcion_col, mayuscula: ErrorSintaxis, MedidaMalDeclarada
caso clave_sin_puntoycoma: ErrorSintaxis; origen_invertido: distinto, CasoMalDeclarado forma
relacion comillas: distinto, RelacionMalDeclarada forma; mayuscula: error de lector
macro version: distinto, MacroMalDeclarada forma; invocacion_argumentos: error de lector
medida ambito_omitido, dos_donde, dos_donde_vs_y: igual, OK
relacion campo_invertido: igual, OK
```

En el último script `macro/espacio-final` dio `igual, OK` porque esa variante alteró una línea **de comentario**; no es código alternativo. Dos `donde` frente a un `donde` con `y`, y orden de campos de relación, son árboles distintos cuando ambas grafías salen del impresor. `ambito` omitido tiene su propio árbol impreso. Los escapes `fila {...}` para filas heterogéneas siguen siendo una representación necesaria; el script de esta ronda no repitió por separado ese ejemplo.

Sobre una medida real modifiqué `medida ` a `medida   ` y ejecuté `tools/sintaxis.py --leer`, `oracle medida revisar`, `oracle medida probar --con '[]'`, `tools/medida.py --expandir`, `oracle formatear`, `_medida_en_memoria` de MCP y `lsp.diagnosticar`/`lentes`. Salida recortada:

```text
--leer, revisar, probar, expandir: rc 1; «fuera de la forma única»
formatear: rc 0; «requiere formato»
MCP: ErrorHerramienta MEDIDA_INVALIDA — ... fuera de la forma única
LSP: 1 diagnóstico, 0 lentes
```

Ejecuté `python3 tools/sintaxis.py --verificar`: `vuelta texto: OK`, `forma única: OK`, `24` bloques de documentación verificados. Ejecuté `python3 tools/cli.py test --rapido`: `VEREDICTO: VERDE` con las omisiones que el propio comando anuncia. Estas corridas verifican el corpus actual, no sustituyen las sondas de variantes.

## Enseñanza, paquete y plantilla

Ejecuté `python3 tools/cli.py --help`, `python3 tools/cli.py manual aritmetica` y `python3 tools/cli.py contexto --compacto`; la ayuda dice que `formatear` conserva líneas `#`, el manual escribe `a - b` y aclara que `a-b` queda fuera de forma, y contexto muestra umbral y alcance de superficie. Ejecuté `rg` sobre README, especificación, docs, notas, `ejemplo/`, `tools/` y `nucleo/` buscando `.json` junto a corpus/catálogos/relaciones, operadores funcionales y resta pegada. `NOTAS-DE-RELEASE.md` y `docs/notas.html` mantienen `t1.turno-1` como historia con la aclaración de sintaxis 1.0. `docs/tutorial-practico.md` dice que `oracle caso nuevo` crea `.caso`. La búsqueda encontró el productor `sondear_procedencia.py` de arriba; no interpreto los archivos de hechos, configuración, diferenciales ni el JSON canónico como segunda autoría.

Ejecuté `UV_CACHE_DIR=/tmp/oracle-audit14-uv-cache uv build --python /usr/bin/python3 --no-build-isolation --out-dir /tmp/oracle-audit14-dist`: sdist y wheel construidos. Inspeccioné el wheel con `ZipFile`: `plantilla_sensor_prosa` contiene 1 `.oracle`, 15 `.caso`, 1 `.relacion` y 1 `oracle.json`; también contiene `tools/sondear_procedencia.py`. Instalé el wheel con `pip install --no-index --no-deps` en `/tmp/oracle-audit14-venv`, ejecuté `oracle plantilla sensor-prosa /tmp/oracle-audit14-template` y `oracle test --rapido --proyecto /tmp/oracle-audit14-template`: plantilla copiada y `VEREDICTO: VERDE`. Eliminé el `oracle_metalenguaje.egg-info` generado por el build; `git status --short` quedó vacío antes de escribir este informe.

## Tabla final

| Punto | Estado observado | Evidencia ejecutada |
|---|---|---|
| Comentarios léxicos en las cuatro superficies | Conforme en los cuatro archivos probados; hallazgos 12 y 13 cerrados en estas sondas | 177/177 inserciones: mismo árbol, carga, `formatear --escribir` conserva, LSP=0. |
| Texto de superficie no impreso en medida, caso, relación y macro | Rechazado en las variantes reejecutadas | Tres matrices de lector/impresor/cargador; CRLF, LF final, blancos, BOM, encabezado, versión, `requiere`, `agrupar`, origen, comillas, macro y operadores. |
| Órdenes de relaciones, columnas y claves; dos `donde` y `y`; `ambito` ausente | Árboles o textos impresos propios bajo el criterio público | Matrices reejecutadas; ninguno resultó un segundo texto cargable para el mismo árbol, fuera de comentarios. |
| CLI, MCP y LSP sobre triple espacio | Rechazo, propuesta de formato o diagnóstico | Comandos y llamadas indicados: MCP error; LSP 1 diagnóstico/0 lentes. |
| Manual, contexto, ayuda, notas históricas, verificador y plantilla del wheel | Sin segunda enseñanza en lo inspeccionado | Comandos, búsquedas, build, inventario, instalación y `test --rapido`. |
| `tools/sondear_procedencia.py` | **Hallazgo: productor interno de casos `.json` en un corpus temporal** | Escritura real de tres `<id>.json` con `json.dumps` y carga real por `cargar_casos`; el script va en el wheel. |
| JSON de intercambio en `.json` | Admitido por decisión; no hallazgo por sí solo | El hallazgo anterior se refiere a la **producción** de casos, no a la mera capacidad de leer JSON. |

**una sola sintaxis de escritura: no, porque `tools/sondear_procedencia.py` todavía produce casos de corpus en JSON, aunque sólo en temporales internos; no encontré una segunda grafía de superficie cargable en las variantes ejecutadas.**
