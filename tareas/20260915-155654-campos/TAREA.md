# Una medida se declara aplicable por el nombre de la relación aunque lea campos que la evidencia no trae

- ESTADO: ABIERTA
- PRIORIDAD: 78
- ETIQUETAS: oracle, metalenguaje

Salió de `20260915-155111-mutante` (el dueño decidió tratarla aparte, 2026-09-15).

`medidas_aplicables` (`nucleo/medida.py`) elige juezas por relación presente, no por campos. Una
medida que lee un campo que la evidencia no trae se declara aplicable y revienta dentro del `donde`
con `ErrorDeAlgebra` («sobre un valor ausente»); las herramientas lo atajan como «NO pudieron
juzgar», que es no juzgar en silencio con un aviso impreso.

El lenguaje ya tiene cómo declarar una relación con sus campos (`relaciones/*.json`: `relacion`,
`campos`, tipo y unidad) y medidas meta sobre esas declaraciones (`campo_declarado`,
`meta.ningun_campo_sin_unidad_declarada`).

A decidir y medir:

- una medida meta: toda medida lee sólo campos declarados de su relación (con relaciones de
  proceso sin declarar hoy, ¿rojo, sombra o `del_origen` hasta declararlas?);
- qué pasa en evaluación cuando falta un campo: error de declaración antes de evaluar, rojo, o
  SIN EVIDENCIA; hoy es un traceback atajado por cada herramienta por separado.

## Medido (2026-09-15, con 0.21.0)

Lecturas `["campo", alias, nombre]` de cada medida, clasificadas por la relación que leen (alias
resuelto por las fuentes y por las entradas con condición de `requiere`):

| proyecto | medidas | lecturas | del lenguaje | declarada, campo declarado | declarada, campo NO declarado | de proceso sin declarar | sin declarar |
|---|--:|--:|--:|--:|--:|--:|--:|
| Oracle (catálogo efectivo) | 60 | 140 | 119 | 11 | 0 | 10 | 0 |
| `ejemplo/seguimiento-tareas` | 3 | 7 | 0 | 7 | 0 | 0 | 0 |
| LyraGASP (propias) | 27 | 72 | 0 | 0 | 0 | 0 | 72 (21 relaciones) |
| Jam (propias) | 41 | 51 (+24 `hecho`) | 0 | 2 | 0 | 0 | 49 (18 relaciones) |

- Hoy **ninguna** medida lee un campo no declarado de una relación declarada: una regla restringida a
  eso no pone a nadie en rojo, es una guarda.
- El caso que abrió la tarea (`mutante`) era una relación de **proceso sin declarar**; las 119 lecturas
  de relaciones del lenguaje tampoco las alcanza `relaciones/`, porque esas relaciones no se declaran
  (ESPECIFICACION §1.1): sus campos los conoce sólo el emisor.
- Exigir que toda relación leída esté declarada pone en rojo a los dos consumidores (39 relaciones).
- En evaluación, un campo ausente levanta `ErrorDeAlgebra` y cada herramienta lo trata distinto:
  `corpus`, `observar`, `mutar` y `mutar_codigo` lo atajan (las dos últimas lo listan como «NO pudieron
  juzgar»), `juzgar` sale 2 y `aceptacion` no lo ataja (traceback, visto con el caso 059 en 0.21.0).

## Decisiones del dueño (2026-09-15)

1. **Alcance de la regla:** relaciones declaradas **y** las que emite Oracle (el núcleo publica sus
   campos); las sin declarar de un consumidor no se juzgan. Descartado: sólo declaradas (no cubría el
   caso de `mutante`) y exigir declarar todo (39 relaciones en rojo en los consumidores).
2. **Campo ausente al evaluar:** el álgebra sigue levantando y el núcleo ofrece una sola forma de
   evaluar que separa las medidas que no pudieron juzgar; las herramientas la usan. Descartado: un
   veredicto NO JUZGÓ (cambia el contrato de evaluación, MAYOR) y dejarlo como está.

Medido además: las 25 relaciones del lenguaje emiten filas uniformes sobre el catálogo de Oracle, así
que un esquema fijo por relación alcanza. Plan: [`PLAN-0.22.0-CAMPOS.md`](../../PLAN-0.22.0-CAMPOS.md).
