# Los 32 sobrevivientes del informe de tools/diferencial.py

- ID: 20260916-035324-informe
- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: oracle, mutacion
- CREADA: 2026-09-16

Medido el 2026-09-16 al declarar `tools/diferencial.py` como custodia
([`20260916-014457-custodia`](../20260916-014457-custodia/TAREA.md)): **57 mutantes, 24 muertos, 32
sobrevivientes y 1 error de arnés**. Por eso entró a `CUSTODIAS_SIN_MEDIR` y no a la matriz de CI: la
deuda es previa y entrar hoy pondría el CI en rojo por tests que faltan desde antes.

Dónde caen los 32: en la **impresión del informe** —las marcas `✓`/`✗` de acuerdo global y
estabilidad individual, los conteos de escenarios verdes y rojos, los mensajes de falla—, no en
`comparar_dominio`, que es lo que decide. Es el mismo cuadro que tuvo `tools/medida.py`: el archivo
tarda y sobrevive porque está mal fijado, no por su tamaño.

El error de arnés es conocido: mutar `if __name__ == "__main__"` a `!=` hace que el módulo corra
`main()` al importarse. Lo cierra el patrón `_entrada_directa` que ya usan `observar.py`,
`sondear_generador.py` y `sondear_procedencia.py`.

A hacer: tests que fijen la salida del informe (qué marca sale con cuántos desacuerdos, qué se
imprime cuando un fixture está vencido), el patrón `_entrada_directa`, y después mover
`diferencial.py` de `CUSTODIAS_SIN_MEDIR` a la matriz de CI.
