# Informe

## Qué cambié

- `tests/test_sintaxis.py`: agregué tests de la superficie de casos que comparan el fragmento completo de `ErrorSintaxis`, con línea, columna, caret y `llegó ...`. Cubren indentación, JSON de campos, origen, evidencia, filas tabulares/escape, encabezado, id, EOF y texto extra. También agregué bordes válidos que antes no estaban fijados: comentario inicial, fila sin espacio tras coma y clave sin espacio tras `;`.
- `tests/test_sintaxis.py`: agregué checks fail-closed del impresor para ids inválidos y claves no imprimibles, más un caso de escape con `ñ` y campo con coma para fijar que no se convierta en tabla.
- `tests/test_sintaxis.py`: agregué un test de `rutas_de_corpus` para distinguir directorio ausente (`[]`) de raíz no física (error).
- `equivalentes.json`: declaré 6 mutantes equivalentes de `nucleo/caso.py`, todos con razón. Son bordes donde el mutante agrega una vuelta sentinela sin efecto o cambia una condición contra un valor imposible por el prefijo ya verificado.
- `README.md`: actualicé la cifra de tests con `python tools/cifras.py --actualizar`, porque los 5 tests nuevos vencieron el bloque publicado.

No toqué `nucleo/caso.py`.

## Reparto de los 57 vivos

- Test nuevo: 51.
- Equivalente declarado: 6.
- Código que sobra: 0.
- Bug: 0.

Equivalentes declarados:

- `nucleo/caso.py:63:10:comparador`
- `nucleo/caso.py:201:14:comparador`
- `nucleo/caso.py:224:15:comparador`
- `nucleo/caso.py:224:21:constante`
- `nucleo/caso.py:245:14:comparador`
- `nucleo/caso.py:262:18:comparador`

Los otros 51 ids de `VIVOS.txt` quedaron clasificados como test nuevo:

```text
nucleo/caso.py:29:31:constante
nucleo/caso.py:31:44:comparador
nucleo/caso.py:36:7:booleano
nucleo/caso.py:37:49:constante
nucleo/caso.py:64:14:comparador
nucleo/caso.py:66:11:comparador
nucleo/caso.py:75:17:constante
nucleo/caso.py:80:13:constante
nucleo/caso.py:105:11:booleano
nucleo/caso.py:115:16:booleano
nucleo/caso.py:122:71:constante
nucleo/caso.py:143:15:booleano
nucleo/caso.py:145:22:constante
nucleo/caso.py:148:11:comparador
nucleo/caso.py:149:39:constante
nucleo/caso.py:150:12:retorno
nucleo/caso.py:165:52:constante
nucleo/caso.py:167:52:constante
nucleo/caso.py:169:57:constante
nucleo/caso.py:177:53:constante
nucleo/caso.py:177:69:constante
nucleo/caso.py:193:24:constante
nucleo/caso.py:193:27:constante
nucleo/caso.py:207:15:booleano
nucleo/caso.py:208:40:constante
nucleo/caso.py:210:53:constante
nucleo/caso.py:212:40:constante
nucleo/caso.py:213:80:constante
nucleo/caso.py:216:24:constante
nucleo/caso.py:216:27:constante
nucleo/caso.py:233:51:constante
nucleo/caso.py:234:30:constante
nucleo/caso.py:250:43:constante
nucleo/caso.py:253:15:booleano
nucleo/caso.py:254:43:constante
nucleo/caso.py:257:43:constante
nucleo/caso.py:259:62:constante
nucleo/caso.py:269:52:constante
nucleo/caso.py:272:73:constante
nucleo/caso.py:275:52:constante
nucleo/caso.py:277:77:constante
nucleo/caso.py:279:52:constante
nucleo/caso.py:284:59:constante
nucleo/caso.py:289:24:constante
nucleo/caso.py:289:27:constante
nucleo/caso.py:297:23:constante
nucleo/caso.py:300:46:constante
nucleo/caso.py:327:76:constante
nucleo/caso.py:341:7:booleano
nucleo/caso.py:370:8:retorno
nucleo/caso.py:371:7:booleano
```

## Qué no hice

- No toqué `corpus/`.
- No toqué `vendor/`.
- No aflojé verificaciones, timeouts ni mutadores.
- No declaré equivalentes sin razón.
- No cambié la superficie de casos ni agregué sintaxis.

## Lo que encontré

- Seis vivos de la lista no eran falta de test sino equivalentes reales: bucles que en `i == len(...)` sólo ejecutan una vuelta sentinela y salen igual, o un `find(")")` donde el valor `0` es imposible después de `startswith("clave(")`.
- Al subir de 528 a 533 tests, `tools/cifras.py` hizo fallar el README por cifras vencidas. Lo actualicé con la herramienta del repo.

## Salidas reales

### `python tools/cifras.py --actualizar`

```text
README.md actualizado
```

### `python tools/mutar_codigo.py --objetivo nucleo/caso.py`

```text
objetivos: nucleo/caso.py

     ·  nucleo/caso.py:18:13:constante                       constante: 2 → 3
     ·  nucleo/caso.py:19:13:constante                       constante: 3 → 4
     ·  nucleo/caso.py:29:31:constante                       constante: False → True
     ·  nucleo/caso.py:31:44:comparador                      comparador: NotEq → Eq
     ·  nucleo/caso.py:36:7:booleano                         booleano: and ↔ or
     ·  nucleo/caso.py:36:7:negacion                         negacion: se borra el `not`
     ·  nucleo/caso.py:37:49:constante                       constante: 1 → 2
     ·  nucleo/caso.py:39:4:retorno                          retorno: return <algo> → return None
     ·  nucleo/caso.py:49:4:retorno                          retorno: return <algo> → return None
     ·  nucleo/caso.py:54:7:negacion                         negacion: se borra el `not`
     ·  nucleo/caso.py:56:4:retorno                          retorno: return <algo> → return None
     ·  nucleo/caso.py:61:8:constante                        constante: 0 → 1
     ·  nucleo/caso.py:63:10:comparador                      comparador: Lt → LtE
     ·  nucleo/caso.py:64:14:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:64:14:comparador                      comparador: Lt → LtE
     ·  nucleo/caso.py:65:17:constante                       constante: 1 → 2
     ·  nucleo/caso.py:66:11:comparador                      comparador: GtE → Gt
     ·  nucleo/caso.py:74:14:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:74:14:comparador                      comparador: Lt → LtE
     ·  nucleo/caso.py:75:17:constante                       constante: 1 → 2
     ·  nucleo/caso.py:76:11:comparador                      comparador: GtE → Gt
     ·  nucleo/caso.py:78:11:comparador                      comparador: NotEq → Eq
     ·  nucleo/caso.py:80:13:constante                       constante: 1 → 2
     ·  nucleo/caso.py:81:7:negacion                         negacion: se borra el `not`
     ·  nucleo/caso.py:83:4:retorno                          retorno: return <algo> → return None
     ·  nucleo/caso.py:87:4:retorno                          retorno: return <algo> → return None
     ·  nucleo/caso.py:87:42:constante                       constante: False → True
     ·  nucleo/caso.py:92:4:retorno                          retorno: return <algo> → return None
     ·  nucleo/caso.py:96:7:negacion                         negacion: se borra el `not`
     ·  nucleo/caso.py:100:7:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:100:36:constante                      constante: 0 → 1
     ·  nucleo/caso.py:100:50:comparador                     comparador: Eq → NotEq
     ·  nucleo/caso.py:100:61:constante                      constante: 0 → 1
     ·  nucleo/caso.py:100:68:constante                      constante: 2 → 3
     ·  nucleo/caso.py:100:74:comparador                     comparador: Eq → NotEq
     ·  nucleo/caso.py:100:81:constante                      constante: 0 → 1
     ·  nucleo/caso.py:100:84:constante                      constante: 0 → 1
     ·  nucleo/caso.py:101:23:constante                      constante: 0 → 1
     ·  nucleo/caso.py:101:26:constante                      constante: 1 → 2
     ·  nucleo/caso.py:102:24:constante                      constante: 1 → 2
     ·  nucleo/caso.py:104:7:comparador                      comparador: IsNot → Is
     ·  nucleo/caso.py:105:11:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:105:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:105:42:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:108:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:109:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:111:57:constante                      constante: 0 → 1
     ·  nucleo/caso.py:111:25:constante                      constante: 0 → 1
     ·  nucleo/caso.py:113:8:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:114:16:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:114:40:comparador                     comparador: Eq → NotEq
     ·  nucleo/caso.py:115:16:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:115:22:comparador                     comparador: Eq → NotEq
     ·  nucleo/caso.py:115:41:comparador                     comparador: NotIn → In
     ·  nucleo/caso.py:117:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:120:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:122:71:constante                      constante: False → True
     ·  nucleo/caso.py:123:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:126:7:comparador                      comparador: IsNot → Is
     ·  nucleo/caso.py:129:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:138:17:constante                      constante: 0 → 1
     ·  nucleo/caso.py:141:14:comparador                     comparador: Lt → LtE
     ·  nucleo/caso.py:143:15:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:143:33:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:145:22:constante                      constante: 1 → 2
     ·  nucleo/caso.py:148:11:comparador                     comparador: GtE → Gt
     ·  nucleo/caso.py:149:39:constante                      constante: 1 → 2
     ·  nucleo/caso.py:150:12:retorno                        retorno: return <algo> → return None
     ·  nucleo/caso.py:151:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:151:24:constante                      constante: 1 → 2
     ·  nucleo/caso.py:153:53:constante                      constante: 1 → 2
     ·  nucleo/caso.py:156:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:160:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:164:26:constante                      constante: 1 → 2
     ·  nucleo/caso.py:165:52:constante                      constante: 2 → 3
     ·  nucleo/caso.py:166:13:comparador                     comparador: Eq → NotEq
     ·  nucleo/caso.py:167:52:constante                      constante: 1 → 2
     ·  nucleo/caso.py:169:57:constante                      constante: 1 → 2
     ·  nucleo/caso.py:170:18:constante                      constante: 1 → 2
     ·  nucleo/caso.py:171:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:173:54:constante                      constante: 1 → 2
     ·  nucleo/caso.py:175:11:comparador                     comparador: Is → IsNot
     ·  nucleo/caso.py:177:53:constante                      constante: 1 → 2
     ·  nucleo/caso.py:177:69:constante                      constante: 1 → 2
     ·  nucleo/caso.py:179:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:186:14:comparador                     comparador: Lt → LtE
     ·  nucleo/caso.py:188:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:191:22:constante                      constante: 1 → 2
     ·  nucleo/caso.py:192:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:193:24:constante                      constante: 1 → 2
     ·  nucleo/caso.py:193:27:constante                      constante: 1 → 2
     ·  nucleo/caso.py:194:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:201:14:comparador                     comparador: Lt → LtE
     ·  nucleo/caso.py:203:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:205:39:constante                      constante: 2 → 3
     ·  nucleo/caso.py:207:15:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:207:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:207:26:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:208:40:constante                      constante: 1 → 2
     ·  nucleo/caso.py:209:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:210:53:constante                      constante: 2 → 3
     ·  nucleo/caso.py:211:15:comparador                     comparador: In → NotIn
     ·  nucleo/caso.py:212:40:constante                      constante: 1 → 2
     ·  nucleo/caso.py:213:46:constante                      constante: 1 → 2
     ·  nucleo/caso.py:213:80:constante                      constante: 3 → 4
     ·  nucleo/caso.py:214:22:constante                      constante: 1 → 2
     ·  nucleo/caso.py:215:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:216:24:constante                      constante: 1 → 2
     ·  nucleo/caso.py:216:27:constante                      constante: 1 → 2
     ·  nucleo/caso.py:217:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:224:15:comparador                     comparador: Lt → LtE
     ·  nucleo/caso.py:224:21:constante                      constante: 0 → 1
     ·  nucleo/caso.py:228:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:230:32:constante                      constante: 1 → 2
     ·  nucleo/caso.py:232:19:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:233:51:constante                      constante: 1 → 2
     ·  nucleo/caso.py:234:30:constante                      constante: 1 → 2
     ·  nucleo/caso.py:236:11:comparador                     comparador: NotEq → Eq
     ·  nucleo/caso.py:238:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:245:14:comparador                     comparador: Lt → LtE
     ·  nucleo/caso.py:247:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:250:43:constante                      constante: 1 → 2
     ·  nucleo/caso.py:251:43:constante                      constante: 2 → 3
     ·  nucleo/caso.py:253:15:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:253:15:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:253:26:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:254:43:constante                      constante: 1 → 2
     ·  nucleo/caso.py:256:15:comparador                     comparador: In → NotIn
     ·  nucleo/caso.py:257:43:constante                      constante: 1 → 2
     ·  nucleo/caso.py:259:62:constante                      constante: 2 → 3
     ·  nucleo/caso.py:260:22:constante                      constante: 1 → 2
     ·  nucleo/caso.py:262:18:comparador                     comparador: Lt → LtE
     ·  nucleo/caso.py:264:19:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:266:53:constante                      constante: 3 → 4
     ·  nucleo/caso.py:269:52:constante                      constante: 1 → 2
     ·  nucleo/caso.py:272:73:constante                      constante: 1 → 2
     ·  nucleo/caso.py:274:23:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:275:52:constante                      constante: 1 → 2
     ·  nucleo/caso.py:277:77:constante                      constante: 1 → 2
     ·  nucleo/caso.py:278:23:comparador                     comparador: NotEq → Eq
     ·  nucleo/caso.py:279:52:constante                      constante: 1 → 2
     ·  nucleo/caso.py:282:26:constante                      constante: 1 → 2
     ·  nucleo/caso.py:283:15:booleano                       booleano: and ↔ or
     ·  nucleo/caso.py:283:26:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:284:59:constante                      constante: 2 → 3
     ·  nucleo/caso.py:286:43:comparador                     comparador: IsNot → Is
     ·  nucleo/caso.py:288:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:289:24:constante                      constante: 1 → 2
     ·  nucleo/caso.py:289:27:constante                      constante: 1 → 2
     ·  nucleo/caso.py:290:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:296:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:297:23:constante                      constante: 1 → 2
     ·  nucleo/caso.py:298:22:constante                      constante: 1 → 2
     ·  nucleo/caso.py:299:11:comparador                     comparador: Is → IsNot
     ·  nucleo/caso.py:300:46:constante                      constante: 1 → 2
     ·  nucleo/caso.py:303:18:constante                      constante: 1 → 2
     ·  nucleo/caso.py:308:59:constante                      constante: 0 → 1
     ·  nucleo/caso.py:310:73:constante                      constante: 0 → 1
     ·  nucleo/caso.py:312:34:comparador                     comparador: Eq → NotEq
     ·  nucleo/caso.py:315:11:comparador                     comparador: IsNot → Is
     ·  nucleo/caso.py:316:48:constante                      constante: 0 → 1
     ·  nucleo/caso.py:318:15:comparador                     comparador: IsNot → Is
     ·  nucleo/caso.py:319:26:constante                      constante: 1 → 2
     ·  nucleo/caso.py:325:11:comparador                     comparador: NotEq → Eq
     ·  nucleo/caso.py:327:76:constante                      constante: 1 → 2
     ·  nucleo/caso.py:329:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:333:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:337:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:339:7:comparador                      comparador: NotIn → In
     ·  nucleo/caso.py:341:7:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:341:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:341:43:comparador                     comparador: Is → IsNot
     ·  nucleo/caso.py:354:53:comparador                     comparador: IsNot → Is
     ·  nucleo/caso.py:355:7:comparador                      comparador: In → NotIn
     ·  nucleo/caso.py:358:11:comparador                     comparador: In → NotIn
     ·  nucleo/caso.py:364:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:369:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:370:8:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:371:7:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:371:28:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:379:11:comparador                     comparador: NotIn → In
     ·  nucleo/caso.py:388:11:negacion                       negacion: se borra el `not`
     ·  nucleo/caso.py:391:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:395:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:404:7:comparador                      comparador: Eq → NotEq
     ·  nucleo/caso.py:409:9:comparador                      comparador: Eq → NotEq
     ·  nucleo/caso.py:417:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:420:7:booleano                        booleano: and ↔ or
     ·  nucleo/caso.py:420:7:negacion                        negacion: se borra el `not`
     ·  nucleo/caso.py:420:35:comparador                     comparador: Is → IsNot
     ·  nucleo/caso.py:424:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/caso.py:434:15:comparador                     comparador: In → NotIn
     ·  nucleo/caso.py:439:4:retorno                         retorno: return <algo> → return None

mutantes: 187 · murieron 187 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 6
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python -m unittest discover -s tests -t . -q`

```text
----------------------------------------------------------------------
Ran 533 tests in 9.363s

OK
```

### `python tools/cifras.py`

```text
CIFRAS OK
  cifras: 533 tests · 535/535 mutantes de medida · **2263 sitios de mutación de código** (2058 + 205 del motor Python).
  escala: **5606 líneas de lenguaje** (`nucleo/`, código y macros) y **255 negativas explícitas** (`raise`). Contra las 36 medidas universales escritas en él (218 líneas): **25,7 a 1**. 29 de las 36 pasan por una macro.
  corpus: **99 casos**: 67 defectos y 32 verdes correctos. De los defectos, 64 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 62 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5606 líneas de lenguaje y **255 negativas explícitas** (`raise`).
  deteccion: Los 67 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 48 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### `python tools/corpus.py`

```text
CORPUS OK · 99 casos · esquema, evidencia L0 y trazabilidad en regla
```

### `python tools/aceptacion.py`

```text
catálogo: 36 medidas · corpus: 99 casos

  ROJO  049-donde-agrego-filas                 meta.donde_nunca_agrega_filas  (valor 1)
  verde 050-donde-filtra-como-debe             meta.donde_nunca_agrega_filas  (valor 0)
  ROJO  051-agrupar-invento-un-grupo           meta.agrupar_no_agranda_la_relacion  (valor 1)
  verde 052-agrupar-colapsa-como-debe          meta.agrupar_no_agranda_la_relacion  (valor 0)
  ROJO  053-unir-perdio-un-par                 meta.unir_materializa_el_producto  (valor 1)
  verde 054-unir-materializa-el-producto       meta.unir_materializa_el_producto  (valor 0)
  ROJO  055-logico-cortocircuito               meta.los_logicos_evaluan_todos_sus_operandos  (valor 2)
  verde 056-logico-evalua-todo                 meta.los_logicos_evaluan_todos_sus_operandos  (valor 0)
  ROJO  057-un-solo-cortocircuito              meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  ROJO  061-ausencia-sin-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-cubierta-o-no-aplica      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  063-ausencia-sin-terminos-no-concluye  meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  064-medida-sin-filtro-ni-grupo         meta.toda_medida_filtra_o_agrupa  (valor 1)
  verde 065-medida-filtra-o-agrupa             meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  066-filtro-sin-terminos-no-concluye    meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  067-umbral-de-igualdad                 meta.ningun_umbral_de_igualdad  (valor 1)
  verde 068-umbral-de-orden                    meta.ningun_umbral_de_igualdad  (valor 0)
  ROJO  069-filtro-no-toma-terminos-ajenos     meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  100-donde-no-compone                   meta.donde_compone  (valor 1)
  verde 101-donde-compone-bien                 meta.donde_compone  (valor 0)
  ROJO  102-unir-no-conmuta                    meta.unir_conmuta  (valor 1)
  verde 103-unir-conmuta-bien                  meta.unir_conmuta  (valor 0)
  ROJO  104-agrupar-sin-claves-difiere         meta.agrupar_sin_claves_es_el_resumen_global  (valor 1)
  verde 105-agrupar-sin-claves-coincide        meta.agrupar_sin_claves_es_el_resumen_global  (valor 0)
  ROJO  106-macro-expande-distinto             meta.una_macro_equivale_a_su_expansion  (valor 1)
  verde 107-macro-equivale                     meta.una_macro_equivale_a_su_expansion  (valor 0)
  ROJO  108-donde-compone-un-campo-por-vez     meta.donde_compone  (valor 3)
  ROJO  109-unir-conmuta-un-campo-por-vez      meta.unir_conmuta  (valor 3)
  ROJO  110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez meta.agrupar_sin_claves_es_el_resumen_global  (valor 2)
  ROJO  111-una-macro-equivale-a-su-expansion-un-campo-por-vez meta.una_macro_equivale_a_su_expansion  (valor 3)
  ROJO  120-sintaxis-no-vuelve-igual           meta.sintaxis_ida_y_vuelta  (valor 1)
  verde 121-sintaxis-vuelve-exacta             meta.sintaxis_ida_y_vuelta  (valor 0)
  ROJO  122-sintaxis-revienta-al-leer          meta.sintaxis_ida_y_vuelta  (valor 1)
  ROJO  123-sintaxis-un-campo-por-vez          meta.sintaxis_ida_y_vuelta  (valor 3)
  ROJO  124-sintaxis-cubre-algebra-no-vuelve-igual meta.sintaxis_cubre_algebra  (valor 1)
  verde 125-sintaxis-cubre-algebra-vuelve-exacta meta.sintaxis_cubre_algebra  (valor 0)
  ROJO  126-sintaxis-cubre-algebra-un-campo-por-vez meta.sintaxis_cubre_algebra  (valor 4)
  ROJO  127-sintaxis-casos-no-vuelve-igual     meta.sintaxis_casos_ida_y_vuelta  (valor 1)
  verde 128-sintaxis-casos-vuelve-exacta       meta.sintaxis_casos_ida_y_vuelta  (valor 0)
  ROJO  129-sintaxis-casos-generados-no-vuelve-igual meta.sintaxis_casos_cubre_casos  (valor 1)
  verde 130-sintaxis-casos-generados-vuelve-exacta meta.sintaxis_casos_cubre_casos  (valor 0)
  ROJO  131-sintaxis-casos-un-campo-por-vez    meta.sintaxis_casos_ida_y_vuelta  (valor 4)
  ROJO  132-sintaxis-casos-generados-un-campo-por-vez meta.sintaxis_casos_cubre_casos  (valor 4)
  ROJO  400-umbral-flotante-de-igualdad        meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  ROJO  401-umbral-flotante-de-desigualdad     meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  verde 402-umbral-flotante-de-orden-y-entero  meta.ningun_umbral_flotante_de_igualdad  (valor 0)
  ROJO  403-umbral-sin-defensa                 meta.ningun_umbral_sin_defensa  (valor 1)
  verde 404-umbral-con-defensa                 meta.ningun_umbral_sin_defensa  (valor 0)
  ROJO  405-medida-sin-alcance                 meta.ninguna_medida_sin_alcance  (valor 1)
  verde 406-medida-con-alcance                 meta.ninguna_medida_sin_alcance  (valor 0)
  ROJO  001-verde-acumulativo                  proceso.afirmacion_declara_alcance  (valor 3)
  ROJO  002-mutante-firma-por-id               proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  003-mutante-fondo-nunca-ejercitado     proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  005-mutante-yaw-sin-franja             proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  006-arnes-bytecode-viejo               proceso.arnes_con_bytecode_frio  (valor 1)
  ROJO  007-relevo-verde-arbol-sucio           proceso.verificacion_vigente  (valor 2)
  ROJO  008-vault-falso-rojo                   proceso.verificador_sin_falsos_rojos  (valor 2)
  ROJO  009-modulo-sin-consumidor              proceso.modulo_con_consumidor  (valor 3)
  ROJO  010-sed-desindenta                     proceso.sintaxis_valida_tras_edicion_masiva  (valor 1)
  ROJO  013-comparadores-del-algebra-sin-ejercitar proceso.test_con_mutante_que_lo_mata  (valor 6)
  ROJO  014-mutador-dejo-un-archivo-mutado-al-ser-matado proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  015-racimo-inalcanzable                proceso.modulo_alcanzable  (valor 12)
  ROJO  016-timeout-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  017-error-de-arnes-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  018-mutante-de-cache-borro-la-copia-del-proyecto proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  019-ronda-sin-mutantes-declarada-verde proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  020-una-afirmacion-sin-alcance-alcanza proceso.afirmacion_declara_alcance  (valor 1)
  ROJO  021-un-cambio-vivo-invalida-la-verificacion proceso.verificacion_vigente  (valor 1)
  ROJO  022-un-falso-rojo-ya-rompe-el-verificador proceso.verificador_sin_falsos_rojos  (valor 1)
  ROJO  023-un-import-ajeno-no-es-consumidor   proceso.modulo_con_consumidor  (valor 1)
  ROJO  024-una-variante-no-vacia-inalcanzable proceso.modulo_alcanzable  (valor 1)
  ROJO  043-ausencia-total-sale-verde          proceso.modulo_con_consumidor  (valor 0)
  ROJO  044-sin-grafo-de-alcance-sale-verde    proceso.modulo_alcanzable  (valor 0)
  verde 058-rechazo-del-algebra-no-es-deteccion proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 059-clave-declarada-en-un-caso         proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 101-mutantes-todos-muertos             proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 102-verificacion-vigente               proceso.verificacion_vigente  (valor 0)
  verde 103-vault-sin-falsos-rojos             proceso.verificador_sin_falsos_rojos  (valor 0)
  verde 104-afirmacion-con-alcance             proceso.afirmacion_declara_alcance  (valor 0)
  verde 105-arnes-con-cache-frio               proceso.arnes_con_bytecode_frio  (valor 0)
  verde 106-modulos-con-consumidor             proceso.modulo_con_consumidor  (valor 0)
  verde 107-reruteo-sin-romper-sintaxis        proceso.sintaxis_valida_tras_edicion_masiva  (valor 0)
  verde 108-ronda-mutacion-concluyente         proceso.ronda_mutacion_concluyente  (valor 0)
  verde 116-todo-el-nucleo-es-alcanzable       proceso.modulo_alcanzable  (valor 0)
  ROJO  200-corrida-sin-ninguna-corrida        simulacion.corrida_reproducible  (valor 0)
  ROJO  201-presupuesto-sin-ninguna-corrida    simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  202-traza-sin-ningun-evento            simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  301-simulador-que-ignora-la-semilla    simulacion.corrida_reproducible  (valor 2)
  verde 302-corridas-reproducibles             simulacion.corrida_reproducible  (valor 0)
  ROJO  303-el-presupuesto-no-alcanzo          simulacion.no_se_agoto_el_presupuesto  (valor 3)
  verde 304-el-presupuesto-alcanzo             simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  305-traza-con-hueco                    simulacion.la_traza_no_tiene_huecos  (valor 2)
  verde 306-traza-completa                     simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  307-una-corrida-no-reproducible-alcanza simulacion.corrida_reproducible  (valor 1)
  ROJO  308-una-corrida-agota-el-presupuesto   simulacion.no_se_agoto_el_presupuesto  (valor 1)
  ROJO  309-una-traza-con-un-hueco             simulacion.la_traza_no_tiene_huecos  (valor 1)

defectos que se pusieron rojos: 64 · verdes correctos: 32 · huecos declarados: 0
  resuelto       004-testigos-duplicados
  resuelto       012-umbral-duplicado-en-filtro-y-umbral
  limite_humano  011-conclusion-errada-desvan

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ningun_umbral_sin_defensa                      0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)

ACEPTACIÓN ✓ — 64 defectos en rojo, 32 verdes correctos, 0 huecos declarados sin tapar
```

### `python tools/diferencial.py`

```text
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### `python tools/trazar.py`

```text
evaluaciones trazadas: 87
hechos: 174 pasos · 330 nodos lógicos · 11 productos

el álgebra, juzgada por medidas escritas en el álgebra:
  ✓ meta.agrupar_no_agranda_la_relacion                 0 (<= 0)
  ✓ meta.donde_nunca_agrega_filas                       0 (<= 0)
  ✓ meta.los_logicos_evaluan_todos_sus_operandos        0 (<= 0)
  ✓ meta.unir_materializa_el_producto                   0 (<= 0)

contrastado con la implementación independiente: 4 propiedades, 0 desacuerdos

  · meta.agrupar_no_agranda_la_relacion: compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción
  · meta.donde_nunca_agrega_filas: compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción
  · meta.los_logicos_evaluan_todos_sus_operandos: cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción
  · meta.unir_materializa_el_producto: compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción
```

### `python tools/metamorficas.py`

```text
equivalencias comprobadas: 325
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_casos_cubre_casos                     5 (5 construidas, 0 del catálogo)
  sintaxis_casos_ida_y_vuelta                   99 (0 construidas, 99 del catálogo)
  sintaxis_cubre_algebra                        94 (94 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         36 (0 construidas, 36 del catálogo)
  una_macro_equivale_a_su_expansion             69 (0 construidas, 69 del catálogo)
  unir_conmuta                                  16 (1 construidas, 15 del catálogo)

juzgado por las medidas aplicables:
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_casos_cubre_casos                     0 (<= 0)
  ✓ meta.sintaxis_casos_ida_y_vuelta                    0 (<= 0)
  ✓ meta.sintaxis_cubre_algebra                         0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

### `python tools/sintaxis.py --verificar`

```text
medidas convertidas: 36
macros convertidas: 3
casos convertidos: 99
ida JSON: OK
vuelta texto: OK
caracteres: JSON 135414 · superficie 132861
puntuación: JSON 24219 (17,9%) · superficie 9906 (7,5%)
bloques de documentación: 21 verificados · 8 declarados como gramática o fragmento
```

### `python tools/mutar.py`

```text
mutantes de medida (medida × mutador): 535 · murieron 535 · sobrevivieron 0
  de los muertos: 412 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 123 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1864

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)
```
