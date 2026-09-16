# El diferencial de Jam sigue rojo porque a su dominio vault le falta una polaridad

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: oracle, consumidores, diferencial

Medido el 2026-09-16 al subir Jam a 0.24.0 y a 0.25.1: `oracle test` de Jam sigue ROJO sólo por
`medidas/diferencial/vault.json` vencido, y no se puede regenerar. `tools/emitir_hechos_vault.py`
muere con:

    vault: sin las dos polaridades no quedan fijadas ['vault.area_es_la_carpeta',
    'vault.carpeta_conocida', 'vault.frontmatter_completo', 'vault.nombre_sigue_la_convencion']
    — hay que declarar un defecto que las active

Al dominio `vault` le faltan defectos que pongan en rojo esas cuatro medidas; sin ellos el emisor se
niega a escribir un fixture que no las fija. Es deuda de Jam —figura en `~/CLAUDE.md` como previa y
«igual con 0.9.1»—, pero deja a un consumidor de Oracle permanentemente en rojo, y un rojo permanente
es un rojo que nadie mira.

A hacer: declarar en `tools/emitir_hechos_vault.py` los defectos que activen cada una de las cuatro
(p. ej. un documento en una carpeta que no coincide con su `area`, una carpeta fuera de la lista, un
frontmatter incompleto, un nombre fuera de la convención), re-emitir `vault.json` y ver `oracle test`
de Jam en verde. Trabajo en el repositorio de Jam, con su `AGENTS.md`.
