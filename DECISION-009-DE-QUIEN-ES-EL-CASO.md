# DECISIÓN 009 — de quién es el caso

**Fecha:** 2026-09-01
**Estado:** tomada · **el código llega con el descubrimiento de bibliotecas, no antes**
**Resuelve:** la corrección 2 de [`DECISION-007`](DECISION-007-BIBLIOTECAS-DE-POLITICAS.md)

## La pregunta

Una biblioteca de políticas trae su propio corpus. Sus casos declaran `procedencia: observada` con
`origen: {repo, commit}` de **otro repositorio**. Cuando mi proyecto la carga, las medidas meta que
evalúan el corpus, ¿qué casos miran?

`DECISION-007` la dejó abierta con una frase exacta: *«hoy la pregunta ni se puede formular»*.

## Lo que se decide

**Cada medida lo declara explícitamente en su `donde`.** No hay una política global, y el arnés no
filtra nada: produce los hechos de todos los casos con su origen reificado, y el juicio queda en
`catalogos/meta/` como todo lo demás.

Es el mismo movimiento que ya se hizo con `medida_en_uso.es_heredada`, y por el mismo motivo:
esconder el filtro en Python pondría el veredicto en código imperativo mientras el resto del
proyecto exige que los veredictos sean datos.

## Y no es uniforme: dos miran lo propio, dos miran todo

| medida | mira | por qué |
|---|---|---|
| `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` | **sólo lo propio** | si la evidencia de un tercero es fabricada, el rojo es suyo y yo no lo puedo arreglar |
| `meta.el_hueco_declarado_explica_por_que` | **sólo lo propio** | un hueco sin explicar en una biblioteca ajena es responsabilidad de su certificación |
| `meta.el_caso_reclama_una_medida_que_existe` | todo | un caso colgado es peligroso venga de donde venga, y **acá sí puedo actuar**: puede ser que seleccioné políticas a medias |
| `meta.el_caso_se_pone_como_debe` | todo | que un caso ajeno NO se comporte como declara **en mi entorno** es información valiosa sobre mi entorno, no sobre el suyo |

**El criterio que separa las dos columnas:** *un rojo sobre el que no puedo actuar enseña a ignorar
la herramienta.* Es el mismo argumento que sostiene el modo sombra, un nivel más abajo.

## El campo

La relación `caso` gana **dos**, no uno:

```
caso(… , es_heredado, biblioteca)
```

`es_heredado` es el booleano que los `donde` van a leer. `biblioteca` es de qué paquete vino —vacío
si es propio— y existe porque el precedente **no es un calco**: `es_heredada` era binario, proyecto
contra catálogo base de Oracle. Con bibliotecas, un caso puede venir del proyecto, del catálogo base
o de un paquete cualquiera, y «¿cuál de las tres bibliotecas trajo este caso roto?» es una pregunta
que se va a hacer el primer día.

## Por qué el código NO se escribe hoy

**Hoy no existe ningún caso ajeno.** Se verificó: `catalogos/` trae 43 medidas y **cero** casos, y
`tools/aceptacion.py` lee únicamente `proy.corpus`. No hay forma de que un caso llegue de afuera
porque el descubrimiento de bibliotecas no está construido.

Un campo `es_heredado` agregado hoy sería **constante `false`**: ninguna evidencia podría ponerlo en
`true`, ningún test podría distinguir su presencia de su ausencia, y su mutante sobreviviría. Sería
código que nada observa — exactamente lo que este proyecto borra cuando lo encuentra.

Así que la decisión se toma ahora, que es lo que `DECISION-007` pedía, y el código llega junto con
el descubrimiento, que es lo único que puede ejercerlo. **Esta decisión desbloquea ese trabajo:**
codex se negó a construir descubrimiento y selección mientras la corrección 2 estuviera abierta, y
tenía razón.

## Lo que se descartó

**(a) sólo lo propio, para todas.** Perdería `el_caso_se_pone_como_debe` sobre casos ajenos, que es
la señal más útil de todas: un caso de biblioteca que falla en mi entorno dice algo sobre **mi**
configuración.

**(b) sólo lo ajeno.** No corresponde a ninguna pregunta que alguien se haga.

**(c) todo, sin distinguir.** Es lo que hay hoy, y produce rojos sobre los que el consumidor no
puede actuar. Es el escenario que `DECISION-007` describe: *«si la primera experiencia de instalar
una biblioteca es que el proyecto deja de compilar, no se instala una segunda vez»*.

## Cómo se llegó

El análisis se hizo dos veces en paralelo y por separado —acá y por agy— y las dos llegaron a **(d)**.
Las siete citas de código del análisis externo se verificaron una por una contra el repositorio.

Difirieron en una fila de la tabla: `meta.el_hueco_declarado_explica_por_que`. Acá se había puesto
«todo» por inofensivo; el análisis externo argumentó que un hueco sin explicar en una biblioteca
ajena es responsabilidad de su certificación. **Ese argumento ganó**, y es el que está en la tabla.

Y aportó la distinción que faltaba: el precedente de `es_heredada` era **binario**, y esto no lo es.
De ahí el segundo campo.
