# Sensor de prosa opcional

Proyecto aislado con relación, medida y corpus propios. Ver el
[patrón, límites y comandos](../../docs/14-sensor-prosa.md).

Desde la raíz del repositorio: `python3 tools/cli.py test --proyecto ejemplo/sensor-prosa`.
No usa red ni necesita claves. `sensor_prosa.py preparar` tampoco llama al proveedor;
sólo `correr` consume API de forma explícita. Un sensor probabilístico no es un juez.
