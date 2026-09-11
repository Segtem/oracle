# Capturar una observación

`aceptacion.plan.json` observa la aceptación de Oracle. `jam-aceptacion.plan.json` hace el mismo
recorrido sobre el corpus de Jam, con los dos repositorios como hermanos (`oracle/` y `jam/`).
La raíz del plan se resuelve respecto del archivo del plan. Si cambia esa disposición, hay que
ajustar `raiz`, el comando y las rutas declaradas antes de capturar.

Desde Oracle, elegí un destino nuevo **fuera del corpus de Jam**:

```bash
python3 -B tools/observar.py capturar \
  --plan observaciones/jam-aceptacion.plan.json --destino /tmp/jam-observacion-nueva
python3 -B tools/observar.py revalidar \
  --plan observaciones/jam-aceptacion.plan.json \
  --registro /tmp/jam-observacion-nueva/registro.json
```

El plan ejecuta la aceptación con las escalares del consumidor (`--confiar-escalares`), exige filas
de casos y espera cero discrepancias de polaridad. Conserva evidencia y registro de ese recorrido;
no observa escenas de Unreal ni prueba cómo se obtuvieron los casos antiguos. No cambia su
procedencia, no incorpora automáticamente el caso capturado al corpus y no alcanza a LyraGASP.

El 2026-09-10 se probó captura y revalidación con 162 referentes declarados y 31 filas de casos:
valor 0, sin cambios, autenticidad no comprobada. Los referentes enumeran configuración, escalares,
corpus y catálogo de Jam, más núcleo, catálogo y herramienta de aceptación de Oracle. Es una lista
explícita, **no una clausura demostrada de dependencias**: las bibliotecas instaladas, el intérprete
y posibles dependencias adicionales de las escalares quedan fuera de esa afirmación. No se midió
el tamaño de ese hueco. Cuando se agreguen archivos relevantes, hay que revisar el plan y capturar
una observación nueva; una lista vieja no descubre por sí sola archivos que nunca enumeró.

El registro se mantiene fuera del corpus porque incorporarlo modifica el mundo que acaba de medir.
La captura sirve para comenzar evidencia nueva con un comando probado, no para reparar
retroactivamente los 23 casos de Jam sin procedencia. El límite de autenticidad está estudiado en
[Una relectura correcta no demuestra una ejecución pasada](../estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md).

Después de optimizar el validador, ese mismo día, la observación inicial detectó el cambio de huella
de `nucleo/algebra.py` aunque la evidencia era igual. Se conservó intacta y se capturó una nueva,
que revalidó sin cambios. El [contraste de ambas lecturas](../estudios/2026-09-10-validacion/jam-tras-validacion.json)
distingue esas historias; una optimización compatible también cambia un referente de código.
