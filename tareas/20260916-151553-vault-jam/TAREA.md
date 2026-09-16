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

### Nota (2026-09-16 15:23:30 UTC)

2026-09-16, CAUSA ENCONTRADA: no le faltan defectos al dominio (los cuatro existen). El vault real de Jam está en rojo hoy —tools/vault.py da 4 de 10— por una nota SIN COMMITEAR del 2026-09-10, Vault-kb/05-DSL/El DSL (Domain-Specific Language) de Jam.md: texto pegado, sin frontmatter, con un nombre fuera de convención y en una carpeta que no está en la lista. Como el emisor copia el vault del disco, el mundo sin defecto ya nace rojo y el dominio pierde su polaridad verde; y la huella de referencia cambia. Medido en una copia sin esa carpeta: vault.py verde, el emisor escribe vault.json (10 medidas x 11 escenarios) y oracle test de Jam da VERDE. La nota es del dueño: qué hacer con ella lo decide él.
