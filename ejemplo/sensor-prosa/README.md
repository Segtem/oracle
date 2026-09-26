# Sensor de prosa opcional

Plantilla editable: un modelo emite `afirmacion_prosa` y Oracle juzga esas filas sin red.
Oracle entrega el sensor; sólo vos decidís ejecutarlo y sos dueño de su código y política.
Costo observado del primer estudio: US$ 0.000877044 en seis solicitudes; no es una tarifa ni un tope futuro.
Un sensor probabilístico no es un juez: un verde no certifica verdad y la zona media requiere revisión humana.
[Patrón, mediciones y límites](https://github.com/Segtem/oracle/blob/main/docs/14-sensor-prosa.md).

## Probar la instalación sin red ni clave

Con `oracle-metalenguaje` instalado, desde un directorio vacío:

```bash
oracle plantilla sensor-prosa prosa
cd prosa
oracle test --proyecto .
python sensor_prosa.py preparar --catalogo catalogos --salida preparada
python -c "import json; from pathlib import Path; from nucleo.caso import leer; c=leer(Path('corpus/prosa/013-vacio-favorable.caso').read_text()); Path('hechos-construidos.json').write_text(json.dumps(c['evidencia']))"
oracle juzgar --proyecto . --con hechos-construidos.json
```

El destino `prosa` debe ser nuevo: se rechaza incluso un directorio vacío o un enlace existente.
El corpus es construido; este recorrido comprueba la política y la instalación, no la precisión del modelo.
`preparar` guarda el lote para inspeccionarlo sin llamar al proveedor.

## Corrida opcional con API

1. Definí `OPENROUTER_API_KEY` en el entorno, nunca en archivos del proyecto.
2. Revisá el lote preparado y ejecutá explícitamente el sensor desde `prosa`:

   ```bash
   python sensor_prosa.py correr --catalogo catalogos --salida corrida
   ```

   Usa el protocolo decisions/noul, por defecto OpenRouter y `typesafe/jev-1.13`.
   `--proveedor`, `--modelo` y `--clave-entorno` permiten adaptarlo. Envía la prosa al proveedor
   y consume API sin tope monetario automático. La salida debe ser nueva; no hay reintentos.
3. Si hay `corrida/hechos.json`, ejecutá:

   ```bash
   oracle juzgar --proyecto . --con corrida/hechos.json
   ```

El sensor sale 2 con filas entre 0,4 y 0,6 inclusive: revisá `corrida/revision-humana.json`
y registrá la decisión humana aunque Oracle dé verde. Si sale 1, la corrida falló y no publica
hechos parciales. Los cortes 0,2/0,8 de la medida son ilustrativos, no calibrados para tu proyecto.
