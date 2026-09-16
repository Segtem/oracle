# tools/diferencial.py no es custodia del arnés y nadie fija al que comprueba el acuerdo

- ID: 20260916-014457-custodia
- ESTADO: ABIERTA
- PRIORIDAD: 60
- ETIQUETAS: oracle, metalenguaje, mutacion
- CREADA: 2026-09-16

Medido el 2026-09-16, al cerrar `20260915-201030-diferencial`: pedirle al arnés la ronda de
`tools/diferencial.py` sale con «objetivos desconocidos o fuera del perfil activo». No está en
`HERRAMIENTAS_CUSTODIAS` ni declarado en `CUSTODIAS_SIN_MEDIR`, así que ni entra ni dice por qué no.

El criterio escrito para ser custodia es «si se rompe, una afirmación queda sin verificar», y este
archivo es el que comprueba el acuerdo con la implementación independiente y la frescura de cada
fixture. Si su comparación se rompe en silencio, el diferencial sigue diciendo ✓ y nadie más mira
eso: el corpus valida la forma y la aceptación la polaridad.

A hacer: medir una ronda completa (cuántos sitios, cuántos sobreviven, cuánto tarda) y después
decidir —entrar a `HERRAMIENTAS_CUSTODIAS` y a la matriz de CI, o declararlo en `CUSTODIAS_SIN_MEDIR`
con su razón—. Mirar en la misma pasada `tools/generar_diferencial.py`, que tampoco está: ahí viven
los mundos y las medidas del contraste.
