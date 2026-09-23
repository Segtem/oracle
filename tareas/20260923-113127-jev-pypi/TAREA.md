# Quien instala Oracle desde PyPI no recibe el patrón de Jev

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, sensores, jev, distribucion


## Lo medido

`ejemplo/sensor-prosa/` (la relación `afirmacion_prosa`, la medida de ejemplo, su corpus y el sensor
`sensor_prosa.py`) y `docs/14-sensor-prosa.md` existen **sólo en el repositorio**. El wheel de
0.28.0 lleva `catalogos`, `mutadores`, `nucleo`, `perfiles`, `relaciones` y `tools`: ni `ejemplo/` ni
`docs/`. Quien hace `pip install oracle-metalenguaje` no recibe nada del patrón, y tendría que clonar
el repo para enterarse de que existe. Para decir «Jev listo para usar» en 0.30.0, eso no alcanza.

## Lo que NO se hace

Oracle no llama a un modelo desde el núcleo ni desde un verbo que corra solo: hoy funciona sin red y
su veredicto es reproducible, y eso es lo que lo hace creíble.

## Qué hacer

La forma más corta que respeta eso: **que el paquete traiga la plantilla y un verbo que la copie al
proyecto del usuario**, que desde ese momento es dueño del sensor.

1. Empaquetar `ejemplo/sensor-prosa/` como datos del paquete (el sensor, la relación, la medida, un
   corpus mínimo y su README).
2. Un verbo, por ejemplo `oracle plantilla sensor-prosa <destino>`, que copie esos archivos al
   proyecto —sin pisar nada que exista— y diga los tres pasos siguientes: poner la clave en el
   entorno, correr el sensor, correr `oracle juzgar`. Oracle no ejecuta el sensor: lo entrega.
3. El README (con enlace absoluto a GitHub, porque en PyPI no hay árbol) dice en cinco líneas qué
   es, cuánto cuesta lo medido y sus límites: un sensor probabilístico no es un juez.
4. `verificar_instalacion` comprueba que la plantilla viaja en el wheel y que el verbo la copia.
5. Probarlo como lo haría alguien de afuera: instalar el wheel en un venv limpio, en un directorio
   vacío, y seguir sólo lo que dice el README.

## Próximo paso

Decidir el nombre del verbo y qué archivos entran en la plantilla; después, empaquetado y test.
