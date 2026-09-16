# LyraGASP y Jam siguen en 0.17.0 y usan la fachada Motor que 0.20.0 corrigió

- ESTADO: CERRADA
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

### Nota (2026-09-16 05:02:33 UTC)

MEDIDO el 2026-09-16 con 0.24.0 instalado en un entorno aparte, sin tocar el de ninguno de los dos.

oracle test --proyecto medidas --confiar-escalares:
- LyraGASP: VERDE. Corpus 190, sintaxis 27 medidas, aceptacion 76 rojos / 114 verdes, diferencial 580 acuerdos y 1740 veredictos estables, mutacion de medidas 466/466. Igual que con 0.17.0, y ademas proceso.codigo_con_mutante_que_lo_mata ahora sale SIN EVIDENCIA en vez de no poder juzgar: es el requiere con condicion de 0.21.0.
- Jam: el mismo ROJO previo, solo por medidas/diferencial/vault.json vencido (deuda propia, su emisor no corre porque al dominio le falta una polaridad). Corpus 31, sintaxis 41 medidas, aceptacion 28 / 3.

Motor.desde_proyecto, que es lo que 0.20.0 cambio:
- LyraGASP: 84 medidas (54 de Oracle, 0 sombras respetadas) con 0.17.0 -> 66 medidas (36 de Oracle, 3 sombras respetadas) con 0.24.0.
- Jam: 101 medidas (57 de Oracle, 0 sombras) -> 83 medidas (39 de Oracle, 3 sombras).
Las 18 que dejan de viajar en cada uno son las del_origen de Oracle, que no obligan a un consumidor.

FALTA, y depende de que 0.24.0 este en PyPI: LyraGASP requirements.txt; Jam los tres lugares de su AGENTS.md mas reinstalar vendor/oracle-pkg/. Las seis sombras de los dos ya quedaron con cota (tarea exigentes).

### Nota (2026-09-16 14:56:03 UTC)

2026-09-16: subidos los dos a 0.24.0 (PyPI verificado: los archivos coinciden con dist/). LyraGASP a1345c2c: requirements.txt, .venv y herramienta global; oracle test VERDE igual que antes. Jam fde0f7a: los dos lugares de AGENTS.md, ORACLE_VERSION y vendor/oracle-pkg reinstalado; suite 1240 con la misma falla previa y oracle test con el mismo rojo previo de vault.json. Commits locales, sin empujar: el push de cada repo queda para el dueño.

### Nota (2026-09-16 15:04:49 UTC)

2026-09-16: empujados con autorización del dueño: LyraGASP a1345c2c, Jam ef0abe2 (el fde0f7a de la nota anterior, con el mensaje corregido antes del push).
