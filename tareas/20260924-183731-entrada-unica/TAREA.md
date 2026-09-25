# Hay cinco caminos para empezar con Oracle que se pisan entre sí

- ESTADO: CERRADA
- PRIORIDAD: 78
- ETIQUETAS: oracle, documentacion


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.3: `docs/02-de-cero-a-un-rojo.md`, `docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`,
`docs/tutorial-practico.md` y `docs/de-cero.html`, más un README de 868 líneas.

## Qué hacer

1. Un inventario: qué enseña cada uno, qué se repite y qué sólo está en uno.
2. Un solo camino de entrada, que es la guía de `de-cero-naval`, y los demás como referencia enlazada
   desde ahí. Nada se pierde: lo que sólo está en uno pasa a la guía o a la referencia.
3. El README arranca con ese camino, no con la historia.

**Quién:** agy (el inventario); Codex o Claude (la reescritura, después de `de-cero-naval`).

## Avance

- Se completó el punto 1 en [INVENTARIO.md](INVENTARIO.md), analizando exhaustivamente los seis documentos: `docs/02-de-cero-a-un-rojo.md`, `docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`, `docs/tutorial-practico.md`, `docs/de-cero.html` y la nueva guía `docs/de-cero.md`.
- Cada afirmación sobre lo que enseña cada documento quedó respaldada por su cita textual y su número de línea exacto.
- Se documentaron en detalle las convergencias/repeticiones metodológicas (dualidad superficie/JSON, el caso antes que la medida, dos polaridades para mutación, alcance obligatorio, rol de testigos) y los contenidos exclusivos de cada documento a preservar en la unificación.

## Próximo paso

Avanzar con el punto 2 (Codex o Claude tras completarse `de-cero-naval`): unificar el camino de entrada tomando `docs/de-cero.md` como entrada principal y reestructurar los demás documentos como referencias enlazadas, migrando o integrando los contenidos exclusivos identificados en `INVENTARIO.md` sin pérdida de material valioso.

### Nota (2026-09-25 03:35:05 UTC)

2026-09-25, Claude: el inventario cita textualmente; un script verificó 139 de 202 citas tal cual y una muestra a mano de las 63 restantes también existe (sólo difiere el formato Markdown: backticks, negritas, saltos de línea). docs/de-cero.md, que se leyó como sexta entrada, vive en la rama t-web-diseno hasta que se publique la web.

### Nota (2026-09-25 21:49:08 UTC)

2026-09-25, Claude: hecho. El inventario mostró que cada documento tiene algo que ningún otro tiene, así que la unificación no funde documentos: hay UNA puerta —la guía de la batalla naval, que en el sitio se juega— y el resto es referencia, cada una con la pregunta que contesta y lo que sólo está ahí (docs/README.md, «El camino», reescrito como tabla). El README arranca con esa puerta, antes de la historia. De paso: el índice decía «54 medidas universales» y la portada «62 medidas universales»: son 62 en el catálogo, 42 universales y 20 del_origen; la portada y cifras.py dicen ahora «medidas en el catálogo», y la ayuda de la CLI y la guía 03 ya no escriben el número a mano.
