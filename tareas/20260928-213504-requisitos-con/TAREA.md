# requisitos con cobertura: una promesa en prosa, las medidas que la cubren y oracle cobertura

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle

### Nota (2026-09-28 22:07:30 UTC)

Hecho. Superficie .requisito (nucleo/requisito.py): texto, fuente opcional, medido_por y/o sin_medir → cobertura total/parcial/ninguna. El enlace va del requisito a la medida: ningún árbol de medida cambia, álgebra sigue 1.0, sintaxis sube a 1.1. Hechos requisito_declarado y requisito_medido_por; meta.el_requisito_nombra_medidas_que_existen (casos 514/515 construidos, 517 observado sobre los requisitos del experimento). oracle cobertura (tools/cobertura.py, en la matriz del CI). De paso: meta.toda_medida_filtra_o_agrupa cuenta sin como filtro (caso 516) y test_macro acepta sin como razón para no ser macro. Mutación de código: requisito.py 70/70, cobertura.py 17/17. oracle test VERDE: 2143 tests, 1026/1026. Uso real: los 12 requisitos de cli-validate en el experimento dan 3 medidos, 9 en parte. Queda para después: diagnóstico de .requisito en el LSP y una herramienta en oracle-mcp; sale publicado en el corte 0.35.0.
