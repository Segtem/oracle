# El último rojo de DECISION-004

**2026-09-09 · veintitrés días después de que se declarara**

## Lo que estaba declarado

El 26 de agosto de 2026, Oracle escribió una decisión incómoda sobre sí mismo. Doce de sus medidas
estaban sostenidas **sólo por evidencia fabricada**: ninguna se apoyaba en una corrida real. Diez se
cerraron transcribiendo evidencia que ya existía. Dos no.

Y en vez de aflojar la medida que las señalaba, la decisión declaró la consecuencia:

> **Consecuencia:** `tools/aceptacion.py` sale con código 1 mientras esto siga así.

Durante veintitrés días, el verificador del proyecto salió 1 a propósito. Su CI llevaba un
`|| true` para tolerarlo, y tres comprobaciones literales que contaban exactamente cuántos rojos
había, para que ninguno más se colara sin que alguien lo notara.

## Cómo cayeron las tres

Ninguna transcribiendo evidencia. **Las tres haciendo observable algo que ya ocurría** — que era el
único camino que la decisión admitía.

| | fecha | qué se hizo observable |
|---|---|---|
| `meta.ninguna_evidencia_declara_un_referente_sin_huella` | 2026-09-01 | los referentes **ya se calculaban** dentro de `revisar_frescura` y morían ahí; exponerlos bastó |
| `meta.sintaxis_cubre_algebra` | 2026-09-08 | un `agrupar:` sin agregados que el álgebra aceptaba, el impresor escribía y el lector rechazaba |
| `meta.sintaxis_casos_cubre_casos` | 2026-09-09 | un nombre de campo con un espacio, escrito como cabecera de tabla que el lector no puede partir |

**Y las tres veces el defecto estaba donde el `alcance` decía que no se miraba.**

## El último, y el desacuerdo del que salió

La búsqueda se le encargó a un segundo autor con una instrucción explícita: *si no encontrás nada,
decilo; inventar un defecto para cerrar el rojo es exactamente lo que la decisión prohíbe*.

Entregó un **resultado negativo riguroso**: 97 esquinas del modelo de casos, 25 casos ortogonales
agregados al generador, todas las direcciones probadas con su comando y su salida. Y no inventó
nada, que era el freno que importaba.

Pero en el camino encontró dos asimetrías de la gramática y las descartó con este argumento:

> *En Oracle, `NOMBRE_CAMPO_RE = ^[a-z][a-z0-9_]*$`. Los campos con espacios no existen ni pueden
> existir en el álgebra relacional.*

La afirmación es cierta **para las relaciones que declara el lenguaje**. Pero los nombres de campo
de la **evidencia de un caso** no los pone el álgebra: los pone el JSON que emite el sensor de un
consumidor, y nada los valida contra ese patrón. Es una demostración correcta bajo una premisa que
el sistema no garantiza — la misma forma de error que ese mismo autor ya había cometido semanas
antes, demostrando que una malla no podía tener exactamente una arista suelta bajo el supuesto de
que no hubiera triángulos degenerados, que el sensor no exige.

Comprobado en tres líneas:

```
corpus.py       CORPUS OK · 1 casos · evidencia L0 en regla
caso.imprimir   lo escribe
caso.leer       ErrorSintaxis: se esperaba ',' entre campos; llegó 'con'
```

Tres piezas del mismo proyecto en desacuerdo sobre la misma forma.

## El arreglo: una condición, y no había que rechazar nada

El impresor de casos ya tiene **dos formas**: la tabla, con una cabecera de campos separados por
comas, y el escape `fila {...}`, que usa cuando las filas son heterogéneas. La guarda que elige
entre las dos decía:

```python
all(c and c.strip() == c and "," not in c for c in campos)
```

`c.strip() == c` atrapa el espacio **al borde**. `"," not in c` atrapa la coma. **El espacio de
adentro no lo atrapaba nada.** Así que `campo con espacio` pasaba las dos comprobaciones, iba a la
forma de tabla, y el lector después lo partía en el espacio.

La forma de escape ya sabía escribirlo: se comprobó que un caso con ese mismo campo **más una fila
heterogénea** —que fuerza el escape— daba la vuelta idéntico. **Lo único que estaba mal era cuál de
las dos formas se elegía.**

```python
all(c and not any(ch.isspace() for ch in c) and "," not in c for c in campos)
```

Nada se rechaza, ningún caso existente cambia de forma. El corpus de Oracle tiene un campo llamado
`cubre_franja_0.5_a_5_grados` —con puntos, fuera del patrón de nombres— que sigue imprimiéndose en
tabla, idéntico.

## Por qué la sonda no lo veía

`_generar_casos_candidatos` producía cinco casos: una relación ausente, una, dos y tres relaciones,
y uno sin medida. **Ningún nombre de campo que no fuera un identificador limpio.** La sonda
recorría el espacio de las *formas* de la evidencia y no el de los *nombres*.

Se agregaron tres esquinas —espacio, coma, tabulación— y contra el impresor viejo la sonda devuelve
**dos rojos**, con el error exacto. La coma no aparece entre ellos, y eso también dice algo: la
guarda vieja sí la atrapaba. Lo que faltaba era el espacio.

## Lo que queda demostrado, más allá de esta medida

**Un resultado negativo riguroso y un defecto encontrado no son excluyentes.** El informe que
concluyó «no hay defecto» contenía el defecto, en la sección de lo descartado. Lo que falló no fue
la búsqueda —fue exhaustiva— sino el **argumento con el que se descartó un hallazgo**.

De ahí la regla que este proyecto ya aplica a las medidas y que conviene aplicar a los informes:
cuando algo se descarta, **el argumento que lo descarta tiene que declarar su premisa**. «No puede
existir en el álgebra» era cierto; «no puede llegar a un caso» era lo que hacía falta demostrar, y
es falso.
