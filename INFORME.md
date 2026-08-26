# Informe de mutación de código — los siete módulos restantes del núcleo

Se ejecutó la mutación de código completa para los 7 objetivos asignados en `TAREA.md`:
`nucleo/grafo.py`, `nucleo/marco.py`, `nucleo/dominio.py`, `nucleo/diferencial.py`, `nucleo/simulacion.py`, `nucleo/fixtures.py` y `nucleo/mutacion.py`.

Los 7 objetivos terminaron en **CERO sobrevivientes**, sin declarar ningún mutante equivalente artificial ni tocar `corpus/` ni `vendor/`.

---

## 1. Qué cambié y por qué

### `tests/test_fixtures.py`
- Se agregó el test `test_fila_malformada_con_clave_no_intenta_validar_unicidad`.
- **Por qué**: Mató el mutante `nucleo/fixtures.py:59:32:constante` (`False → True` en `bien_formados = False`). Ningún test de la suite pasaba una relación con cláusula `["clave", [...]]` donde una de las filas fuera un tipo no estructurado (ej. un entero). Al mutar a `True`, el arnés intentaba ejecutar `validar_unicidad` sobre enteros y levantaba `TypeError`. El test fija que las filas malformadas cortan la validación de unicidad y reportan el error de fila correspondiente.

### `tests/test_mutacion.py`
- Se agregó el test `test_quitar_requiere_remueve_el_nodo_conservando_el_resto`.
- Se fijó la aserción exacta `self.assertEqual(m["rechazos_del_algebra"], 2)` en `test_morir_por_excepcion_no_es_morir_por_conducta`.
- **Por qué**: Mató 4 mutantes en `nucleo/mutacion.py`:
  - `88:17:constante` (`7 → 8` en `quitar_requiere`): la función no estaba ejercitada con medidas con `requiere`.
  - `90:4:retorno` (`return <algo> → return None` en `quitar_requiere`).
  - `90:16:constante` (`5 → 6` en `return [*d[:5], d[6]]` en `quitar_requiere`).
  - `339:41:constante` (`1 → 2` en `f["rechazos_del_algebra"] += 1`): el test existente chequeaba verdad booleana (`if m["rechazos_del_algebra"]`) sin fijar el número exacto de rechazos observados (2 casos).

### `README.md`
- Se actualizó el bloque de cifras mediante `python tools/cifras.py --actualizar` para reflejar el conteo de 561 tests (+2 tests nuevos).

---

## 2. Reparto de sobrevivientes por archivo

| Archivo | Mutantes | Muertos | Sobrevivientes iniciales | Falta test | Equivalente | Código sobra | Bug |
|---|---|---|---|---|---|---|---|
| `nucleo/grafo.py` | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| `nucleo/marco.py` | 35 | 35 | 0 | 0 | 0 | 0 | 0 |
| `nucleo/dominio.py` | 19 | 19 | 0 | 0 | 0 | 0 | 0 |
| `nucleo/diferencial.py` | 48 | 48 | 0 | 0 | 0 | 0 | 0 |
| `nucleo/simulacion.py` | 50 | 50 | 0 | 0 | 0 | 0 | 0 |
| `nucleo/fixtures.py` | 131 | 131 | 1 | 1 | 0 | 0 | 0 |
| `nucleo/mutacion.py` | 153 | 153 | 4 | 4 | 0 | 0 | 0 |
| **Total** | **440** | **440** | **5** | **5** | **0** | **0** | **0** |

---

## 3. Salida real de cada objetivo de mutación de código

### `python tools/mutar_codigo.py --objetivo nucleo/grafo.py`
```
objetivos: nucleo/grafo.py

     ·  nucleo/grafo.py:43:27:constante                      constante: 0 → 1
     ·  nucleo/grafo.py:48:19:comparador                     comparador: NotIn → In
     ·  nucleo/grafo.py:49:44:constante                      constante: 1 → 2
     ·  nucleo/grafo.py:52:4:retorno                         retorno: return <algo> → return None

mutantes: 4 · murieron 4 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/marco.py`
```
objetivos: nucleo/marco.py

     ·  nucleo/marco.py:38:14:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:39:17:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:39:31:comparador                     comparador: In → NotIn
     ·  nucleo/marco.py:40:19:comparador                     comparador: Eq → NotEq
     ·  nucleo/marco.py:55:32:comparador                     comparador: Eq → NotEq
     ·  nucleo/marco.py:58:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/marco.py:78:23:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:79:16:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:84:38:constante                      constante: 0 → 1
     ·  nucleo/marco.py:86:14:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:87:11:comparador                     comparador: In → NotIn
     ·  nucleo/marco.py:88:30:constante                      constante: 1 → 2
     ·  nucleo/marco.py:89:42:comparador                     comparador: In → NotIn
     ·  nucleo/marco.py:89:37:constante                      constante: 1 → 2
     ·  nucleo/marco.py:89:71:constante                      constante: 0 → 1
     ·  nucleo/marco.py:91:34:constante                      constante: 0 → 1
     ·  nucleo/marco.py:92:34:constante                      constante: 0 → 1
     ·  nucleo/marco.py:93:26:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:94:11:negacion                       negacion: se borra el `not`
     ·  nucleo/marco.py:97:11:booleano                       booleano: and ↔ or
     ·  nucleo/marco.py:97:11:negacion                       negacion: se borra el `not`
     ·  nucleo/marco.py:97:39:comparador                     comparador: NotIn → In
     ·  nucleo/marco.py:100:15:booleano                      booleano: and ↔ or
     ·  nucleo/marco.py:100:15:comparador                    comparador: IsNot → Is
     ·  nucleo/marco.py:100:37:comparador                    comparador: Lt → LtE
     ·  nucleo/marco.py:100:41:constante                     constante: 0 → 1
     ·  nucleo/marco.py:104:22:constante                     constante: 1 → 2
     ·  nucleo/marco.py:107:11:negacion                      negacion: se borra el `not`
     ·  nucleo/marco.py:108:26:constante                     constante: 1 → 2
     ·  nucleo/marco.py:114:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/marco.py:116:54:comparador                    comparador: In → NotIn
     ·  nucleo/marco.py:117:32:booleano                      booleano: and ↔ or
     ·  nucleo/marco.py:117:32:comparador                    comparador: NotIn → In
     ·  nucleo/marco.py:117:57:comparador                    comparador: Gt → GtE
     ·  nucleo/marco.py:117:74:constante                     constante: 0 → 1

mutantes: 35 · murieron 35 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/dominio.py`
```
objetivos: nucleo/dominio.py

     ·  nucleo/dominio.py:59:24:constante                    constante: 1 → 2
     ·  nucleo/dominio.py:63:11:booleano                     booleano: and ↔ or
     ·  nucleo/dominio.py:63:11:negacion                     negacion: se borra el `not`
     ·  nucleo/dominio.py:63:30:comparador                   comparador: In → NotIn
     ·  nucleo/dominio.py:65:11:negacion                     negacion: se borra el `not`
     ·  nucleo/dominio.py:51:18:constante                    constante: True → False
     ·  nucleo/dominio.py:77:4:retorno                       retorno: return <algo> → return None
     ·  nucleo/dominio.py:81:4:retorno                       retorno: return <algo> → return None
     ·  nucleo/dominio.py:100:7:negacion                     negacion: se borra el `not`
     ·  nucleo/dominio.py:113:25:booleano                    booleano: and ↔ or
     ·  nucleo/dominio.py:113:67:comparador                  comparador: Gt → GtE
     ·  nucleo/dominio.py:113:90:constante                   constante: 1 → 2
     ·  nucleo/dominio.py:114:27:booleano                    booleano: and ↔ or
     ·  nucleo/dominio.py:126:11:comparador                  comparador: NotEq → Eq
     ·  nucleo/dominio.py:127:72:negacion                    negacion: se borra el `not`
     ·  nucleo/dominio.py:136:82:comparador                  comparador: Lt → LtE
     ·  nucleo/dominio.py:136:96:constante                   constante: 2 → 3
     ·  nucleo/dominio.py:143:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/dominio.py:144:22:booleano                    booleano: and ↔ or

mutantes: 19 · murieron 19 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/diferencial.py`
```
objetivos: nucleo/diferencial.py

     ·  nucleo/diferencial.py:39:15:booleano                 booleano: and ↔ or
     ·  nucleo/diferencial.py:39:15:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:39:47:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:41:19:booleano                 booleano: and ↔ or
     ·  nucleo/diferencial.py:41:19:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:41:45:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:43:12:booleano                 booleano: and ↔ or
     ·  nucleo/diferencial.py:43:12:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:44:19:comparador               comparador: NotIn → In
     ·  nucleo/diferencial.py:27:18:constante                constante: True → False
     ·  nucleo/diferencial.py:51:8:retorno                   retorno: return <algo> → return None
     ·  nucleo/diferencial.py:52:32:constante                constante: False → True
     ·  nucleo/diferencial.py:52:49:constante                constante: True → False
     ·  nucleo/diferencial.py:53:22:constante                constante: False → True
     ·  nucleo/diferencial.py:59:4:retorno                   retorno: return <algo> → return None
     ·  nucleo/diferencial.py:64:7:booleano                  booleano: and ↔ or
     ·  nucleo/diferencial.py:64:33:comparador               comparador: In → NotIn
     ·  nucleo/diferencial.py:64:59:comparador               comparador: Eq → NotEq
     ·  nucleo/diferencial.py:67:42:constante                constante: True → False
     ·  nucleo/diferencial.py:72:42:constante                constante: True → False
     ·  nucleo/diferencial.py:78:4:retorno                   retorno: return <algo> → return None
     ·  nucleo/diferencial.py:84:42:constante                constante: True → False
     ·  nucleo/diferencial.py:90:11:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:97:46:constante                constante: True → False
     ·  nucleo/diferencial.py:101:4:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:109:4:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:114:7:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:116:4:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:120:7:negacion                 negacion: se borra el `not`
     ·  nucleo/diferencial.py:122:4:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:140:7:comparador               comparador: In → NotIn
     ·  nucleo/diferencial.py:141:8:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:142:4:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:151:65:comparador              comparador: In → NotIn
     ·  nucleo/diferencial.py:152:54:comparador              comparador: NotIn → In
     ·  nucleo/diferencial.py:154:8:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:165:11:booleano                booleano: and ↔ or
     ·  nucleo/diferencial.py:165:11:comparador              comparador: In → NotIn
     ·  nucleo/diferencial.py:165:33:comparador              comparador: NotEq → Eq
     ·  nucleo/diferencial.py:167:63:constante               constante: 12 → 13
     ·  nucleo/diferencial.py:167:93:constante               constante: 12 → 13
     ·  nucleo/diferencial.py:168:4:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:182:7:comparador               comparador: Is → IsNot
     ·  nucleo/diferencial.py:183:8:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:187:8:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:189:7:comparador               comparador: NotEq → Eq
     ·  nucleo/diferencial.py:190:8:retorno                  retorno: return <algo> → return None
     ·  nucleo/diferencial.py:192:4:retorno                  retorno: return <algo> → return None

mutantes: 48 · murieron 48 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/simulacion.py`
```
objetivos: nucleo/simulacion.py

     ·  nucleo/simulacion.py:59:17:constante                 constante: 0 → 1
     ·  nucleo/simulacion.py:44:18:constante                 constante: True → False
     ·  nucleo/simulacion.py:79:11:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:82:15:booleano                  booleano: and ↔ or
     ·  nucleo/simulacion.py:82:15:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:82:41:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:72:18:constante                 constante: True → False
     ·  nucleo/simulacion.py:98:7:negacion                   negacion: se borra el `not`
     ·  nucleo/simulacion.py:101:7:booleano                  booleano: and ↔ or
     ·  nucleo/simulacion.py:101:7:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:101:68:comparador               comparador: Lt → LtE
     ·  nucleo/simulacion.py:101:78:constante                constante: 0 → 1
     ·  nucleo/simulacion.py:104:7:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:107:7:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:110:7:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:120:11:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:122:11:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:126:11:booleano                 booleano: and ↔ or
     ·  nucleo/simulacion.py:126:11:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:126:38:comparador               comparador: NotIn → In
     ·  nucleo/simulacion.py:126:54:comparador               comparador: NotIn → In
     ·  nucleo/simulacion.py:134:15:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:136:15:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:139:4:retorno                   retorno: return <algo> → return None
     ·  nucleo/simulacion.py:143:23:constante                constante: 500 → 501
     ·  nucleo/simulacion.py:143:46:constante                constante: True → False
     ·  nucleo/simulacion.py:150:7:booleano                  booleano: and ↔ or
     ·  nucleo/simulacion.py:150:7:negacion                  negacion: se borra el `not`
     ·  nucleo/simulacion.py:150:62:comparador               comparador: Lt → LtE
     ·  nucleo/simulacion.py:150:69:constante                constante: 0 → 1
     ·  nucleo/simulacion.py:153:7:booleano                  booleano: and ↔ or
     ·  nucleo/simulacion.py:153:7:comparador                comparador: IsNot → Is
     ·  nucleo/simulacion.py:153:44:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:161:11:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:165:12:booleano                 booleano: and ↔ or
     ·  nucleo/simulacion.py:165:37:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:166:19:booleano                 booleano: and ↔ or
     ·  nucleo/simulacion.py:166:44:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:170:15:booleano                 booleano: and ↔ or
     ·  nucleo/simulacion.py:170:15:negacion                 negacion: se borra el `not`
     ·  nucleo/simulacion.py:175:15:comparador               comparador: In → NotIn
     ·  nucleo/simulacion.py:182:28:booleano                 booleano: and ↔ or
     ·  nucleo/simulacion.py:182:28:comparador               comparador: Eq → NotEq
     ·  nucleo/simulacion.py:182:55:comparador               comparador: Eq → NotEq
     ·  nucleo/simulacion.py:183:32:comparador               comparador: Eq → NotEq
     ·  nucleo/simulacion.py:183:55:comparador               comparador: Eq → NotEq
     ·  nucleo/simulacion.py:185:31:comparador               comparador: Is → IsNot
     ·  nucleo/simulacion.py:186:23:comparador               comparador: In → NotIn
     ·  nucleo/simulacion.py:196:7:booleano                  booleano: and ↔ or
     ·  nucleo/simulacion.py:198:4:retorno                   retorno: return <algo> → return None

mutantes: 50 · murieron 50 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/fixtures.py`
```
objetivos: nucleo/fixtures.py

     ·  nucleo/fixtures.py:24:18:constante                   constante: True → False
     ·  nucleo/fixtures.py:32:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/fixtures.py:32:11:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:32:38:comparador                  comparador: IsNot → Is
     ·  nucleo/fixtures.py:36:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/fixtures.py:36:11:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:36:54:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:40:7:booleano                     booleano: and ↔ or
     ·  nucleo/fixtures.py:40:7:negacion                     negacion: se borra el `not`
     ·  nucleo/fixtures.py:40:42:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:41:8:retorno                      retorno: return <algo> → return None
     ·  nucleo/fixtures.py:45:11:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:45:11:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:45:44:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:48:11:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:56:24:constante                   constante: True → False
     ·  nucleo/fixtures.py:58:15:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:59:32:constante                   constante: False → True
     ·  nucleo/fixtures.py:63:19:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:63:19:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:63:49:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:65:19:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:69:11:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:74:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/fixtures.py:78:7:negacion                     negacion: se borra el `not`
     ·  nucleo/fixtures.py:79:8:retorno                      retorno: return <algo> → return None
     ·  nucleo/fixtures.py:82:7:comparador                   comparador: NotEq → Eq
     ·  nucleo/fixtures.py:85:7:booleano                     booleano: and ↔ or
     ·  nucleo/fixtures.py:85:7:negacion                     negacion: se borra el `not`
     ·  nucleo/fixtures.py:85:51:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:87:7:booleano                     booleano: and ↔ or
     ·  nucleo/fixtures.py:87:7:comparador                   comparador: IsNot → Is
     ·  nucleo/fixtures.py:87:47:comparador                  comparador: LtE → Lt
     ·  nucleo/fixtures.py:87:70:constante                   constante: 0 → 1
     ·  nucleo/fixtures.py:90:7:negacion                     negacion: se borra el `not`
     ·  nucleo/fixtures.py:92:8:retorno                      retorno: return <algo> → return None
     ·  nucleo/fixtures.py:94:7:comparador                   comparador: NotEq → Eq
     ·  nucleo/fixtures.py:96:7:comparador                   comparador: NotIn → In
     ·  nucleo/fixtures.py:99:7:negacion                     negacion: se borra el `not`
     ·  nucleo/fixtures.py:104:19:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:104:19:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:104:47:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:105:20:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:105:43:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:105:75:comparador                 comparador: In → NotIn
     ·  nucleo/fixtures.py:108:7:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:112:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:112:7:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:112:40:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:114:13:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:114:13:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:114:39:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:116:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:122:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:122:7:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:122:40:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:124:9:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:124:13:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:124:58:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:127:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:127:7:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:127:43:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:129:8:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:130:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:130:7:comparador                  comparador: Is → IsNot
     ·  nucleo/fixtures.py:130:44:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:138:11:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:142:11:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:144:13:comparador                 comparador: In → NotIn
     ·  nucleo/fixtures.py:148:11:comparador                 comparador: IsNot → Is
     ·  nucleo/fixtures.py:153:11:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:157:15:comparador                 comparador: IsNot → Is
     ·  nucleo/fixtures.py:159:15:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:159:15:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:159:51:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:159:74:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:162:21:comparador                 comparador: IsNot → Is
     ·  nucleo/fixtures.py:166:23:comparador                 comparador: In → NotIn
     ·  nucleo/fixtures.py:168:19:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:168:19:comparador                 comparador: Is → IsNot
     ·  nucleo/fixtures.py:168:47:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:170:20:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:170:20:comparador                 comparador: Is → IsNot
     ·  nucleo/fixtures.py:170:48:comparador                 comparador: Is → IsNot
     ·  nucleo/fixtures.py:171:28:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:174:7:comparador                  comparador: NotEq → Eq
     ·  nucleo/fixtures.py:174:23:constante                  constante: False → True
     ·  nucleo/fixtures.py:174:30:constante                  constante: True → False
     ·  nucleo/fixtures.py:176:61:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:176:72:constante                  constante: False → True
     ·  nucleo/fixtures.py:176:79:constante                  constante: True → False
     ·  nucleo/fixtures.py:179:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:184:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:184:7:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:184:39:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:185:8:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:189:11:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:191:11:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:191:11:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:191:42:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:194:11:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:194:11:comparador                 comparador: Is → IsNot
     ·  nucleo/fixtures.py:194:35:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:199:15:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:202:15:comparador                 comparador: IsNot → Is
     ·  nucleo/fixtures.py:207:11:comparador                 comparador: NotEq → Eq
     ·  nucleo/fixtures.py:207:27:constante                  constante: False → True
     ·  nucleo/fixtures.py:207:34:constante                  constante: True → False
     ·  nucleo/fixtures.py:209:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:215:7:negacion                    negacion: se borra el `not`
     ·  nucleo/fixtures.py:216:8:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:217:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:217:7:comparador                  comparador: NotEq → Eq
     ·  nucleo/fixtures.py:217:54:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:218:8:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:219:37:comparador                 comparador: In → NotIn
     ·  nucleo/fixtures.py:219:60:comparador                 comparador: In → NotIn
     ·  nucleo/fixtures.py:220:7:booleano                    booleano: and ↔ or
     ·  nucleo/fixtures.py:228:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:234:7:comparador                  comparador: NotEq → Eq
     ·  nucleo/fixtures.py:234:8:comparador                  comparador: Is → IsNot
     ·  nucleo/fixtures.py:234:26:comparador                 comparador: Is → IsNot
     ·  nucleo/fixtures.py:244:11:booleano                   booleano: and ↔ or
     ·  nucleo/fixtures.py:244:11:negacion                   negacion: se borra el `not`
     ·  nucleo/fixtures.py:244:29:comparador                 comparador: IsNot → Is
     ·  nucleo/fixtures.py:250:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/fixtures.py:256:7:comparador                  comparador: In → NotIn
     ·  nucleo/fixtures.py:268:7:comparador                  comparador: In → NotIn
     ·  nucleo/fixtures.py:270:15:comparador                 comparador: NotIn → In

mutantes: 131 · murieron 131 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/mutacion.py`
```
objetivos: nucleo/mutacion.py

     ·  nucleo/mutacion.py:48:7:comparador                   comparador: In → NotIn
     ·  nucleo/mutacion.py:50:7:booleano                     booleano: and ↔ or
     ·  nucleo/mutacion.py:50:47:comparador                  comparador: In → NotIn
     ·  nucleo/mutacion.py:52:17:comparador                  comparador: In → NotIn
     ·  nucleo/mutacion.py:54:33:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:54:55:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:56:7:booleano                     booleano: and ↔ or
     ·  nucleo/mutacion.py:56:32:negacion                    negacion: se borra el `not`
     ·  nucleo/mutacion.py:58:14:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:59:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/mutacion.py:64:15:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:64:40:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:65:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/mutacion.py:72:28:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:72:31:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:72:38:comparador                  comparador: NotEq → Eq
     ·  nucleo/mutacion.py:72:40:constante                   constante: 0 → 1
     ·  nucleo/mutacion.py:73:7:comparador                   comparador: Eq → NotEq
     ·  nucleo/mutacion.py:73:29:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:73:35:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:75:6:constante                    constante: 2 → 3
     ·  nucleo/mutacion.py:76:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/mutacion.py:88:7:comparador                   comparador: NotEq → Eq
     ·  nucleo/mutacion.py:88:17:constante                   constante: 7 → 8
     ·  nucleo/mutacion.py:90:4:retorno                      retorno: return <algo> → return None
     ·  nucleo/mutacion.py:90:16:constante                   constante: 5 → 6
     ·  nucleo/mutacion.py:96:37:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:96:40:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:96:51:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:95:11:constante                   constante: False → True
     ·  nucleo/mutacion.py:96:18:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:96:21:constante                   constante: 2 → 3
     ·  nucleo/mutacion.py:97:11:comparador                  comparador: Eq → NotEq
     ·  nucleo/mutacion.py:97:16:constante                   constante: 0 → 1
     ·  nucleo/mutacion.py:98:17:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:98:34:constante                   constante: 1 → 2
     ·  nucleo/mutacion.py:99:19:constante                   constante: True → False
     ·  nucleo/mutacion.py:100:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/mutacion.py:106:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/mutacion.py:132:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/mutacion.py:137:30:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:138:16:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:139:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/mutacion.py:143:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/mutacion.py:147:11:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:147:16:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:149:13:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:149:18:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:150:35:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:150:47:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:151:35:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:151:47:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:155:40:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:155:43:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:155:54:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:156:11:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:156:16:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:157:19:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:157:30:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:158:13:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:158:18:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:160:23:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:160:34:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:160:47:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:161:43:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:162:23:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:162:34:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:162:47:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:163:11:constante                  constante: 3 → 4
     ·  nucleo/mutacion.py:163:14:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:169:48:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:169:59:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:174:34:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:174:37:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:174:42:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:174:45:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:175:32:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:178:15:comparador                 comparador: NotEq → Eq
     ·  nucleo/mutacion.py:178:34:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:179:47:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:180:65:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:189:53:negacion                   negacion: se borra el `not`
     ·  nucleo/mutacion.py:190:17:booleano                   booleano: and ↔ or
     ·  nucleo/mutacion.py:191:30:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:192:19:comparador                 comparador: In → NotIn
     ·  nucleo/mutacion.py:194:59:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:195:21:comparador                 comparador: In → NotIn
     ·  nucleo/mutacion.py:196:37:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:198:59:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:199:21:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:201:71:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:205:11:constante                  constante: 3 → 4
     ·  nucleo/mutacion.py:205:14:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:205:19:constante                  constante: 3 → 4
     ·  nucleo/mutacion.py:205:22:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:205:32:constante                  constante: 3 → 4
     ·  nucleo/mutacion.py:205:35:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:206:40:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:206:43:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:206:54:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:207:11:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:207:16:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:208:53:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:209:24:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:209:35:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:209:48:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:210:24:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:210:35:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:210:48:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:210:61:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:215:11:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:219:57:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:232:15:negacion                   negacion: se borra el `not`
     ·  nucleo/mutacion.py:232:20:booleano                   booleano: and ↔ or
     ·  nucleo/mutacion.py:232:56:comparador                 comparador: In → NotIn
     ·  nucleo/mutacion.py:232:61:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:234:44:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:234:49:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:234:37:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:235:35:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:235:40:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:235:30:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:235:59:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:240:22:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:241:11:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:241:16:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:243:49:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:245:25:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:245:49:constante                  constante: 2 → 3
     ·  nucleo/mutacion.py:272:11:comparador                 comparador: IsNot → Is
     ·  nucleo/mutacion.py:275:4:retorno                     retorno: return <algo> → return None
     ·  nucleo/mutacion.py:289:11:booleano                   booleano: and ↔ or
     ·  nucleo/mutacion.py:289:11:negacion                   negacion: se borra el `not`
     ·  nucleo/mutacion.py:289:22:comparador                 comparador: NotIn → In
     ·  nucleo/mutacion.py:294:22:comparador                 comparador: Eq → NotEq
     ·  nucleo/mutacion.py:296:11:comparador                 comparador: NotEq → Eq
     ·  nucleo/mutacion.py:304:27:comparador                 comparador: NotEq → Eq
     ·  nucleo/mutacion.py:305:34:comparador                 comparador: NotEq → Eq
     ·  nucleo/mutacion.py:306:31:comparador                 comparador: NotEq → Eq
     ·  nucleo/mutacion.py:307:28:constante                  constante: False → True
     ·  nucleo/mutacion.py:309:60:constante                  constante: False → True
     ·  nucleo/mutacion.py:310:28:constante                  constante: True → False
     ·  nucleo/mutacion.py:331:49:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:332:47:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:333:40:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:334:36:constante                  constante: 0 → 1
     ·  nucleo/mutacion.py:336:11:booleano                   booleano: and ↔ or
     ·  nucleo/mutacion.py:337:45:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:339:41:constante                  constante: 1 → 2
     ·  nucleo/mutacion.py:341:4:retorno                     retorno: return <algo> → return None

mutantes: 153 · murieron 153 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

---

## 4. Salida real de las nueve verificaciones de DOCTRINA.md

### Verificación 1: `python3 -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 561 tests in 9.378s

OK
```

### Verificación 2: `python3 tools/cifras.py`
```
CIFRAS OK
  cifras: 561 tests · 547/547 mutantes de medida · **2268 sitios de mutación de código** (2063 + 205 del motor Python).
  escala: **5674 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,2 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5674 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### Verificación 3: `python3 tools/corpus.py`
```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### Verificación 4: `python3 tools/aceptacion.py`
```
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
  ROJO  025-mutante-de-codigo-sobreviviente    proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  027-ronda-de-codigo-sin-mutantes-no-concluye proceso.codigo_con_mutante_que_lo_mata  (valor 0)
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
  verde 109-mutantes-de-codigo-todos-muertos   proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  verde 110-mutante-de-codigo-equivalente-declarado-verde proceso.codigo_con_mutante_que_lo_mata  (valor 0)
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

defectos que se pusieron rojos: 67 · verdes correctos: 34 · huecos declarados: 0
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

ACEPTACIÓN ✓ — 67 defectos en rojo, 34 verdes correctos, 0 huecos declarados sin tapar
```

### Verificación 5: `python3 tools/diferencial.py`
```
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### Verificación 6: `python3 tools/trazar.py`
```
evaluaciones trazadas: 92
hechos: 182 pasos · 339 nodos lógicos · 11 productos

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

### Verificación 7: `python3 tools/metamorficas.py`
```
equivalencias comprobadas: 331
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_casos_cubre_casos                     5 (5 construidas, 0 del catálogo)
  sintaxis_casos_ida_y_vuelta                  104 (0 construidas, 104 del catálogo)
  sintaxis_cubre_algebra                        94 (94 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         37 (0 construidas, 37 del catálogo)
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

### Verificación 8: `python3 tools/sintaxis.py --verificar`
```
medidas convertidas: 37
macros convertidas: 3
casos convertidos: 104
ida JSON: OK
vuelta texto: OK
caracteres: JSON 142369 · superficie 139406
puntuación: JSON 25487 (17,9%) · superficie 10489 (7,5%)
bloques de documentación: 21 verificados · 8 declarados como gramática o fragmento
```

### Verificación 9: `python3 tools/mutar.py`
```
mutantes de medida (medida × mutador): 547 · murieron 547 · sobrevivieron 0
  de los muertos: 422 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 125 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1924

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.codigo_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'estado'], 'pasaron'] en `2.2.1.1`
```

---

## 5. Qué NO hice y por qué

1. **No agregué mutantes equivalentes en `equivalentes.json`**: Ninguno de los mutantes sobrevivientes observados era un cambio equivalente real; todos correspondían a huecos de fijación en la suite de tests (`quitar_requiere` desatendido, conteo exacto de rechazos por álgebra sin comparar como entero exacto, y validación de unicidad de clave sobre filas malformadas). Escribir un equivalente en lugar de fijar la conducta observable habría ocultado un punto ciego real.
2. **No modifiqué el código fuente del núcleo (`nucleo/`)**: El código del núcleo estaba correctamente implementado; los 5 mutantes sobrevivientes iniciales murieron agregando las pruebas de cobertura exactas en la suite de `tests/`.
3. **No toqué `corpus/` ni `vendor/`**: La evidencia para los nuevos tests se construyó dentro de las funciones de prueba en `tests/test_fixtures.py` y `tests/test_mutacion.py`.
4. **No omití ninguno de los 7 objetivos**: Se ejecutaron los 7 módulos completos hasta alcanzar 0 sobrevivientes en cada uno.

---

## 6. Lo que descubrí que no me pediste

1. **`PRIORIDADES` en `tools/mutar_codigo.py`**: El mapeo de prioridades asigna `"nucleo/grafo.py": ("tests.test_nucleo",)`. Sin embargo, los tests que ejercitaban `cierre` estaban en `tests.test_perfiles` (a través de `perfiles/python/marco.py`). Al mutar `grafo.py`, el arnés corría primero `test_nucleo` (que pasaba) y luego toda la suite hasta llegar a `test_perfiles`.
2. **Rechazo por álgebra vs. Conducta en conteos de mutantes**: En `nucleo/mutacion.py:339`, `rechazos_del_algebra` contabiliza cuántas veces un mutante de medida provocó una excepción de álgebra. El test existente `test_morir_por_excepcion_no_es_morir_por_conducta` filtraba con `if m["rechazos_del_algebra"]`, lo que permitía que un mutante aritmético `1 → 2` pasara desapercibido si no se comparaba el valor entero exacto (2) del conteo.
