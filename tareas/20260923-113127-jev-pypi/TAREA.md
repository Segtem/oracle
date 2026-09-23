# Quien instala Oracle desde PyPI no recibe el patrón de Jev

- ESTADO: CERRADA
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

### Nota (2026-09-23 11:38:49 UTC)

Implementación: oracle plantilla sensor-prosa <destino>, destino nuevo obligatorio para no pisar archivos ni enlaces. Se empaqueta la fuente existente del ejemplo (sensor, configuración, relación, medida, corpus y README), sin ejecutar el sensor desde Oracle. Verificación prevista: suite completa y wheel instalado fuera del checkout en venv limpio.

### Nota (2026-09-23 11:41:55 UTC)

Implementado el empaquetado desde ejemplo/sensor-prosa (sin duplicar recursos), el verbo plantilla registrado en ayuda/manual y copia a destino nuevo con escritura exclusiva. README raíz y de plantilla: costo observado, límites, enlace absoluto y recorrido sin red. verificar_instalacion ejecutó literalmente ese recorrido desde README del wheel en venv limpio y cwd externo: WHEEL OK, copia fiel y repetición rechazada sin alterar bytes. Pruebas focalizadas verdes; suite completa en ejecución. No se llamó a la API ni se hicieron commits en el repositorio.

- Adjunto: [jev-suite-verificada.log](jev-suite-verificada.log)

- Adjunto: [jev-wheel-verificado.log](jev-wheel-verificado.log)

### Nota (2026-09-23 11:44:21 UTC)

Validación final: python3 -m unittest discover -s tests -t . -q: 2414 pruebas, OK (suite completa). python3 tools/verificar_instalacion.py: WHEEL OK con plantilla completa, copia fiel, recorrido literal del README sin red desde venv limpio y directorio vacío externo, corpus verde, preparación y juzgar; sobrescritura rechazada. git diff --check sin errores. Se regeneró docs/manual.html y se actualizó el inventario documental del CLI. Evidencia adjunta: jev-suite-verificada.log y jev-wheel-verificado.log. Sin llamadas a API ni commits en el repositorio.

## Próximo paso

Ninguno pendiente en esta tarea: implementación y verificación completas, tarea CERRADA. Los cambios quedan sin commit por pedido del usuario.

### Nota (2026-09-23 12:01:19 UTC)

2026-09-23, revisión de Claude desde un venv limpio: la plantilla viaja en el wheel y el verbo la copia a un proyecto nuevo, al lado del del usuario. Corregido: la instrucción que imprimía mandaba a correr el sensor con --catalogo catalogos, que es el catálogo de ejemplo de la plantilla; quien la siguiera al pie de la letra juzgaba las medidas de juguete y no las suyas. Ahora, si hay un catalogos/ donde se corre, la instrucción apunta a ése (probado también con un destino con espacios).
