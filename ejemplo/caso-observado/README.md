# De una captura JSON a un caso observado

Desde la raíz de Oracle, esta receta recibe tres archivos: captura, metadatos del autor y
destino nuevo. Usa los formatos existentes; no agrega un verbo a Oracle.

## Recorrido reproducible con una captura real

La [captura guardada](../../observaciones/2026-09-09-aceptacion/evidencia.json) proviene del
recorrido de aceptación del 9 de septiembre de 2026. Su
[registro](../../observaciones/2026-09-09-aceptacion/registro.json) identifica comando,
fecha y referentes. [metadatos.json](metadatos.json) copia, sin evidencia, los metadatos del
[caso original](../../observaciones/2026-09-09-aceptacion/494-la-cota-de-la-sombra-observada-por-el-recorrido.caso).
La medida y la etiqueta `verde_correcto` son decisiones explícitas ya documentadas allí.
Esto convierte una observación guardada; no declara una nueva corrida del sensor.

```bash
salida_observado=$(mktemp -d)
mkdir "$salida_observado/corpus"
python3 ejemplo/caso-observado/convertir.py \
  observaciones/2026-09-09-aceptacion/evidencia.json \
  ejemplo/caso-observado/metadatos.json \
  "$salida_observado/corpus/494-la-cota-de-la-sombra-observada-por-el-recorrido.json"
python3 - "$salida_observado/corpus" <<'PY'
import json
import sys
from pathlib import Path
from nucleo.caso import cargar_fuente_caso
from nucleo.medida import cargar
from tools.corpus import verificar

corpus = Path(sys.argv[1])
fallas, casos = verificar(corpus)
assert not fallas, fallas
assert len(casos) == 1
caso = cargar_fuente_caso(corpus / (casos[0]['id'] + '.json'))
captura = json.loads(Path('observaciones/2026-09-09-aceptacion/evidencia.json').read_text())
assert caso['evidencia'] == captura
medida = cargar(Path('catalogos/meta/meta.ninguna_sombra_supera_su_cota.oracle'))
veredicto = medida.evaluar(caso['evidencia'])
assert not veredicto.sin_evidencia
assert veredicto.valor == 0
assert veredicto.ok
assert caso['etiqueta'] == 'verde_correcto'
print('Caso válido; evidencia íntegra; valor 0, compatible con verde_correcto.')
PY
```

## Usarla con otra captura

Prepará un JSON de metadatos con `id`, `fecha`, `origen`, `procedencia`, `titulo`,
`etiqueta`, `sintoma`, `como_se_detecto`, `medida` y `leccion`, sin `evidencia`.
El archivo de ejemplo documenta sólo esa captura histórica: no reutilices su origen para otra.
Declarar `procedencia: observada` requiere haber observado el dominio y poder identificar de
dónde salió la captura. La receta exige esa declaración, pero no certifica su autenticidad.
En `origen` consigná los datos reales disponibles (repositorio, fecha, registro, comando,
referentes); el conversor no los infiere ni ejecuta el comando declarado.

Elegí `medida` y `etiqueta` por lo que el caso debe mostrar: `verde_correcto` espera verde,
`falso_verde` describe un defecto que debe dar rojo. El vocabulario completo está en
`python3 tools/cli.py manual etiqueta`. No se elige la polaridad a partir del resultado de la medida.

La captura debe ser el mapa JSON de relaciones a filas del sensor, no el registro envolvente.
Se conserva toda la evidencia, incluidas relaciones vacías, claves, duplicados y tipos JSON;
no se filtran filas ni se completan campos. Se guarda como `<id>.json`, sin sobrescribir.
Luego verificá el esquema con `tools.corpus.verificar` y evaluá la medida del proyecto con
las herramientas existentes, contrastando el resultado con la etiqueta elegida como en el
recorrido anterior. Recién después incorporá el caso al corpus correspondiente.

Esta receta alcanza para evitar transcribir filas. Obtener nuevas observaciones de Jam o
LyraGASP sigue requiriendo correr los sensores correspondientes en Unreal. No reconstruye
las 94 procedencias históricas de Oracle ni convierte casos construidos en observados.
