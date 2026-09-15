# LyraGASP y Jam siguen en 0.17.0 y usan la fachada Motor que 0.20.0 corrigió

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, consumidores

Los dos consumidores fijan `oracle-metalenguaje==0.17.0` (LyraGASP en `requirements.txt`, Jam en
`vendor/oracle-pkg/`). Los dos juzgan con `Motor.desde_proyecto` (`tools/juzga_oracle.py`,
`Content/Python/jam/oracle_shadow.py`), que en 0.20.0 dejó de cargar las 20 `del_origen` de Oracle y
empezó a respetar sus tres sombras: su veredicto cambia.

Seguir «Subir un consumidor» de `~/CLAUDE.md`: medir cada uno con 0.20.0 (`oracle test --proyecto
medidas --confiar-escalares` y su uso de `Motor`) **antes** de tocar el número; después LyraGASP sólo
`requirements.txt`, Jam los tres lugares de su `AGENTS.md` y reinstalar `vendor/oracle-pkg/`.
Commits y push en cada repo, con autorización del dueño.
