# Roadmap 0.22.0 — toda medida lee campos que existen, y un campo ausente se informa igual en todas partes

Fecha: 2026-09-15. Base: distribución 0.21.0, álgebra 0.7, sintaxis 0.5.
Tarea: [`20260915-155654-campos`](tareas/20260915-155654-campos/TAREA.md). Implementa agy; revisa, mide y
corta Claude.

## El problema, medido

`medidas_aplicables` elige juezas por relación presente, no por campos. Una medida que lee un campo
que la evidencia no trae se declara aplicable y levanta `ErrorDeAlgebra` dentro del `donde`. Nada lo
detecta antes, y al evaluar cada herramienta lo trata distinto: `mutar` y `mutar_codigo` lo listan
como «NO pudieron juzgar», `juzgar` sale 2, `observar` lo vuelve `SensorFallido` y `aceptacion` no lo
ataja (traceback, visto con el caso 059 en 0.21.0).

Lecturas `["campo", alias, nombre]` por la relación que leen (2026-09-15, con 0.21.0):

| proyecto | lecturas | del lenguaje | declarada, campo declarado | declarada, campo NO declarado | de proceso sin declarar | sin declarar |
|---|--:|--:|--:|--:|--:|--:|
| Oracle | 140 | 119 | 11 | 0 | 10 | 0 |
| `ejemplo/seguimiento-tareas` | 7 | 0 | 7 | 0 | 0 | 0 |
| LyraGASP | 72 | 0 | 0 | 0 | 0 | 72 (21 relaciones) |
| Jam | 51 | 0 | 2 | 0 | 0 | 49 (18 relaciones) |

- Hoy nadie lee un campo no declarado de una relación declarada. El caso que abrió la tarea
  (`mutante`) era de **proceso sin declarar**, y las 119 lecturas del lenguaje no las alcanza
  `relaciones/`: esas relaciones no se declaran (§1.1), sus campos los conoce sólo el emisor.
- Las 25 relaciones del lenguaje emiten filas **uniformes** (una sola forma por relación, medido sobre
  el catálogo de Oracle): un esquema fijo por relación alcanza.

## Decisiones del dueño

1. La regla alcanza las relaciones **declaradas y las que emite Oracle**; las relaciones sin declarar
   de un consumidor no se juzgan.
2. En evaluación, el álgebra **sigue levantando** —un campo ausente no es `False`— y el núcleo ofrece
   **una sola forma** de evaluar un conjunto de medidas que separa las que no pudieron juzgar, con su
   motivo; las herramientas la usan y lo informan igual.

## Diseño

### 1. Los campos de lo que emite el núcleo

Junto a cada `RELACIONES_*` y `AMBITOS_DE_RELACIONES`, un mapa literal:

```python
CAMPOS_DE_RELACIONES = {
    "medida": ("id", "agregado", "comparador", …),
    "requiere": ("medida", "indice", "relacion", "con_condicion"),
}
```

- Se lee sin importar el módulo, igual que los ámbitos (`campos_de_relaciones_declarados()`, al lado de
  `ambitos_de_relaciones_declarados()`), y falla cerrado ante un literal que no entiende.
- Cada relación de un `RELACIONES_*` tiene sus campos, y ninguna declara campos sin estar en un
  `RELACIONES_*`.
- Un test por emisor comprueba que las filas emitidas traen **exactamente** esos campos: la
  declaración no puede envejecer sin que un test caiga.

### 2. Las relaciones de proceso que lee el catálogo, declaradas

`corrida_mutacion`, `archivo`, `modulo`, `alcanzable`, `afirmacion` y `hallazgo` —las de proceso que las
medidas de Oracle leen— se declaran en `relaciones/` (las del perfil python en `perfiles/python/`, si
ahí vive su emisor), con los campos que emiten sus productores o, para `afirmacion` y `hallazgo`, que no
emite nadie en Oracle, los que sus medidas leen. Pasan a contar como **declaradas**. Las de proceso que
ninguna medida lee (`importa`, `cambio`, `paquete`, `veredicto`, `hecho_historia`) quedan fuera.

### 3. `campo_leido`, una relación del lenguaje nueva

Una fila por lectura `["campo", alias, nombre]` de cada medida del catálogo:

| campo | qué |
|---|---|
| `medida` | id |
| `relacion` | la relación del alias, resuelta por las fuentes y por las entradas con condición de `requiere` |
| `campo` | el nombre leído |
| `origen` | `declarada` (en `relaciones/`, campos comunes o de variante), `lenguaje` (emitida por el núcleo) o `sin_declarar` |
| `existe` | si el campo está entre los conocidos de esa relación; `false` para `sin_declarar` |

`hecho` (la fila entera) y `col` (columnas derivadas) no son lecturas de campo y no entran. Se emite
donde hoy se emiten `campo_declarado` y `cantidad_comparada` para las medidas meta, con sus campos y su
ámbito declarados, y figura en la tabla de §1.1.

### 4. `meta.toda_medida_lee_campos_que_existen`

```
ninguno meta.toda_medida_lee_campos_que_existen:
    de campo_leido c
    donde c.origen != "sin_declarar" y c.existe == false
    umbral <= 0 segun contrato porque "…"
    ambito universal
    alcance "…"
```

Hoy da 0 en Oracle, LyraGASP y Jam. Corpus: un `falso_verde` (una medida que lee `m.estadoo` de
`mutante`) y un `verde_correcto`.

### 5. Una sola forma de evaluar que separa lo que no se pudo juzgar

- `nucleo/medida.py`: una función que evalúa un conjunto de medidas y devuelve un `Informe` con un campo
  nuevo, `no_juzgaron` (tuplas `(id, motivo)`, vacío por defecto). Una medida que levanta
  `ErrorDeAlgebra` al evaluar no se pierde ni corta la corrida: queda ahí con su motivo.
- `Informe.ok` es falso si alguna no juzgó; `texto()` las lista aparte; `a_json()` suma `no_juzgaron`.
- La usan `tools/aceptacion.py` (medidas meta y la evaluación de cada caso), `tools/juzgar.py`,
  `tools/mutar.py` y `tools/mutar_codigo.py`, en vez de sus `try` propios. Cada herramienta conserva su
  contrato de salida: `aceptacion` y `mutar` cuentan una que no juzgó como falla, igual que un rojo;
  `juzgar` sigue saliendo 2; `mutar_codigo` sigue sin depender de los veredictos del catálogo.
- `tools/observar.py` conserva `SensorFallido`: ahí «la evidencia no le sirve a la medida» es un error
  del sensor, con semántica propia.
- `Motor.evaluar` no cambia (sigue levantando): cambiar la fachada pública es otra decisión.

## Entregas y dueños

| quién | qué |
|---|---|
| agy | `CAMPOS_DE_RELACIONES` en los emisores y su lector; `campo_leido` y su emisión; la función de evaluación y `Informe.no_juzgaron`; las herramientas que la usan; las declaraciones en `relaciones/`; la medida meta; tests de todo eso; `AVANCE`/`INFORME` |
| Claude | tests de revisión antes de leer la entrega; corpus; `ESPECIFICACION.md` (§1.1, §1.3, evaluación); versiones, NOTAS, README, manual; mutación y corte |

## Versiones

- `VERSION_DISTRIBUCION` 0.21.0 → **0.22.0**: una relación del lenguaje nueva, una medida universal
  nueva y un campo nuevo en `Informe`.
- `VERSION_ALGEBRA` queda en **0.7** y `VERSION_SINTAXIS` en **0.5**: `campo_leido` es una relación de
  hechos como `sombra` o `verbo_del_cli` (mismo criterio que el corte 0.11.0), sin nodo, operador ni
  gramática nuevos. La referencia del diferencial no se re-deriva.

## Fuera de alcance

- Exigir que un consumidor declare las relaciones que lee.
- Que la variante de una lectura coincida con el filtro de `tipo` de la medida.
- Cambiar `Motor.evaluar`.

## Criterios de salida del corte

Suite completa verde; aceptación ✓ con el falso verde nuevo en rojo; ningún traceback de `aceptacion`
ante un campo ausente; `meta.toda_medida_lee_campos_que_existen` en verde sobre Oracle, LyraGASP y Jam;
mutación de los módulos tocados sin sobrevivientes o con equivalentes defendidos; `verificar_instalacion`
y cifras.
