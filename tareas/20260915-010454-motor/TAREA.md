# Motor.desde_proyecto juzga con otro catálogo que oracle test

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, bug

Medido el 2026-09-15 (P0 de 0.18.0): con `catalogo_base: true`, `Motor.desde_proyecto` carga 57 medidas y `catalogo_efectivo` 37; las 20 de más son `del_origen`. Además `Motor` ignora las sombras de `oracle.json`. LyraGASP (`tools/juzga_oracle.py`) y Jam (`oracle_shadow.py`) usan esa fachada. Ver [REVISION-CLAUDE.md](../../vault-kb/estudios/0.18.0-juzgar/REVISION-CLAUDE.md).

## Medido sobre los consumidores (2026-09-15, 0.19.0)

| proyecto | `Motor.desde_proyecto` | `catalogo_efectivo` | sombras que `Motor` ignora |
|---|--:|--:|--:|
| LyraGASP `medidas/` | 84 | 64 | 3 |
| Jam `medidas/` | 101 | 81 | 3 |

Las 20 de más son las mismas `del_origen` de Oracle en los dos (`meta.donde_nunca_agrega_filas`,
`meta.el_diagnostico_no_publica_el_dominio`, …).

## Diseño

- `Motor.desde_proyecto` carga con `catalogo_efectivo`, la misma selección que `oracle juzgar` y la
  aceptación.
- `Informe` gana `en_sombra` (vacío por defecto): `ok` no cuenta los rojos en sombra, `texto()` los
  marca `[EN SOMBRA]` y dice cuántos perdonó, `a_json()` agrega `en_sombra` por medida. La medición
  no se apaga, sólo la consecuencia.
- `Motor.evaluar` devuelve el informe con las sombras del proyecto; `desde_datos` y `desde_medidas`
  no tienen proyecto y no tienen sombras. Los consumidores no cambian una línea.
