# Una implementación 0.8 hecha de cero, por un tercer autor

Tarea [`20260915-201030-codex`](../../tareas/20260915-201030-codex/TAREA.md).

## Por qué

La referencia del diferencial tiene hoy **dos autores encadenados**: Codex la escribió contra el
álgebra 0.6 (2026-08-24) y agy la re-derivó contra 0.7 (2026-09-15) y contra 0.8 (2026-09-16)
**mirando la de Codex**. Eso deja
afuera justo lo que hizo útil al diferencial la primera vez: que implementaciones independientes se
**dividan entre sí**. Cuando eso pasa, lo que falla no es una implementación, es la especificación
—es lo que encontraron las tres de 2026-08-24—.

Lo que falta es una implementación 0.8 escrita **sin ver ninguna otra**, sólo con la especificación
vigente.

## Cómo se corre

```bash
# 1. el encargo, en un directorio fuera del repositorio (frena solo si Codex no tiene cuota)
vault-kb/estudios/0.26.0-codex/lanzar.sh /ruta/fuera/del/repo/codex-08 [modelo]

# 2. el contraste contra la referencia actual
python3 vault-kb/estudios/0.26.0-codex/contrastar.py /ruta/fuera/del/repo/codex-08/evaluador.py
```

- `lanzar.sh` copia **sólo** `ESPECIFICACION.md`, `DECISION-001`, `DECISION-002` y
  [`CONTRATO.md`](CONTRATO.md) —no `diferencial/referencia/`—, deja las huellas de lo que entregó al
  lado del directorio y no adentro, y corre Codex confinado a ese directorio, sin la configuración
  ni las reglas del usuario. Se niega si el directorio está dentro del repositorio o no está vacío.
- `contrastar.py` compara el veredicto entero —`ok`, valor, si levantó y si se escapó una excepción
  que no es `ErrorDeAlgebra`— sobre los 9 mundos del diferencial con sus 5 medidas y sobre cada caso
  del corpus: 248 comparaciones al 2026-09-16.

## Comprobado antes de tener la entrega

- `contrastar.py` con la propia referencia como candidato: 248 comparaciones, 0 desacuerdos.
- Con un candidato que ignora `requiere`: 29 desacuerdos, en los mundos y en el corpus.
- `lanzar.sh` sin cuota sale 3 sin crear nada; con un directorio dentro del repositorio, sale 2.

## Lo que queda

Correr los dos pasos cuando Codex tenga cuota, y clasificar cada desacuerdo en las tres clases de
[`diferencial/referencia/PROCEDENCIA.md`](../../diferencial/referencia/PROCEDENCIA.md): la
especificación no decide, el núcleo contra todas, o un defecto de una implementación. Las dos
primeras son deuda de la especificación, y son lo que se busca. Si coinciden en todo, se registra en
`PROCEDENCIA.md` igual: también es un resultado.

Al 2026-09-16, Codex respondía «usage limit» con `gpt-5.6-luna` y con `gpt-6-astra`; `luna-gpt-5.6`,
`gpt-5.6` y `luna` no son nombres de modelo que acepte para esta cuenta.

## Lo que ya se sabe de 0.8

Al re-derivar la referencia contra 0.8 aparecieron dos rincones de `sin` que la especificación no
decidía, y que §3 ahora decide (el alias repetido cuando no llega ninguna fila, y el alias que
coincide con una columna de `agrupar`): la referencia actual quedó en desacuerdo con el documento en
esos dos. Y uno anterior, el predicado que no da booleano (`20260916-202010-predicado-bool`). Una
implementación de Codex que coincida con la especificación y no con la referencia en esos puntos es
el resultado esperado, no una falla. Las sondas están en
[`../0.26.0-antijunta/referencia/sonda_sin.py`](../0.26.0-antijunta/referencia/sonda_sin.py).
