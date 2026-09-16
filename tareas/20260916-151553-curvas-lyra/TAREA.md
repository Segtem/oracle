# Un test de LyraGASP falla por las mayúsculas de una curva, ajeno a Oracle

- ESTADO: ABIERTA
- PRIORIDAD: 25
- ETIQUETAS: oracle, consumidores

Medido el 2026-09-16 al subir LyraGASP a 0.24.0: `tests/test_extrae_curvas.py`
(`test_extraccion_sobre_archivo_real_de_locomocion`) falla porque espera la curva
`Enable_TurnInPlaceSteering` y el asset `M_Neutral_Stand_Turn_090_L.uasset` la trae como
`enable_turninplacesteering`. El test no importa Oracle: la falla es de LyraGASP y es anterior a la
subida.

Se carga acá porque apareció al verificar un consumidor de Oracle y deja su suite en rojo. A decidir en
LyraGASP: si el extractor tiene que conservar las mayúsculas del asset, o si el test tiene que comparar
sin distinguirlas.
