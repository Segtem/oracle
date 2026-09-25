# El camino

Hay una sola puerta de entrada, y el resto es referencia: cada documento contesta una pregunta y
tiene algo que no está en ningún otro.

## Empezá por acá

**[Tu primer juego con un LLM](de-cero.md)**. Una batalla naval en nueve misiones, desde una carpeta
vacía: el juego, el registro de lo que pasa, el primer caso rojo, la regla, los mutantes, once reglas
y una partida juzgada. En el sitio se juega: predecís cada salida, rompés la regla en un tablero y
cazás sus mutantes. Si nunca usaste Oracle, no hace falta leer nada antes.

## Después, según lo que necesites

| si querés… | leé | y ahí está, sólo ahí… |
|---|---|---|
| saber qué problema resuelve | [Por qué Oracle](por-que.html) | la batalla naval que dio verde sin medir nada, y un test contra una medida |
| entender qué hace Oracle, en qué orden y qué contesta | [Cómo funciona Oracle](como-funciona.md) | los seis pasos de `juzgar`, las capas de `oracle test` en orden y cada estado posible, todo ejecutado |
| tu primer rojo en cinco minutos, si ya programás | [De cero a un rojo](02-de-cero-a-un-rojo.md) | `oracle medida probar` con evidencia en la línea de comandos |
| medir tu propio producto | [La primera medida real](13-primer-valor.md) | Oracle contra un `assert`, y cuándo apagar el catálogo base |
| conectar un proyecto que ya existe | [Conectar un proyecto](07-conectar-a-un-proyecto-propio.md) | el sensor partido en puro y adaptador, las escalares propias y la sombra |
| escribir medidas con soltura | [Escribir una medida](03-escribir-una-medida.md) | cómo se aíslan las escalares, por qué los ids son ASCII, cuánto se usa cada macro |
| ver un dominio completo con geometría | [Tutorial práctico](tutorial-practico.md) | un `LEFT JOIN` sin nulos, escalares de volumen y penetración, la API `Motor` desde Python |
| saber por qué hace falta mutar | [Por qué la mutación](05-por-que-la-mutacion.md) | los dos autores de los mutadores y qué hacer con un sobreviviente |
| correr la mutación sin quedarte sin memoria | [Memoria de la mutación](mutacion-memoria.md) | cómo medir la memoria y limitar las rondas con systemd |
| llevar las tareas del proyecto | [El tracker de tareas](12-tareas.md) | `oracle tarea` y el próximo paso como relevo |
| usar un modelo como sensor de prosa | [Un modelo como sensor](14-sensor-prosa.md) | el patrón optativo, con calibración y revisión humana |
| conectar un agente por MCP | [El servidor MCP](mcp-contrato.md) | el contrato de las herramientas, sólo de lectura |
| implementar el álgebra sin ver el núcleo | [Especificación](../ESPECIFICACION.md) | el álgebra entera y la crónica de cada versión |
| escribir medidas en tu editor, con diagnósticos | [Editores](../editores/README.md) | el servidor de lenguaje y la configuración de cada editor |
| saber por qué algo es como es | [Decisiones](decisiones/README.md) | las decisiones de diseño, con lo que se descartó |

## Lo que no es un documento

- **`oracle manual`**, en la terminal o [en el sitio](manual.html): la referencia del lenguaje armada
  de sus propias declaraciones —los vocabularios cerrados, las relaciones que emite, los verbos del
  comando y las medidas universales con qué NO ve cada una—, así que no hay dónde quede vieja.
  `oracle manual --instalar-man <dir>` deja `man oracle` funcionando.
- **`oracle contexto [--compacto]`**: lo que tu proyecto declara hoy (relaciones, campos, operadores,
  escalares y medidas), para pasárselo a un modelo en unos 1.600 tokens.

Las guías con comandos —la de la batalla naval, *Cómo funciona*, *De cero a un rojo*, *Por qué la
mutación*, *Conectar un proyecto* y *La primera medida real*— se ejecutan en la suite del
repositorio desde una carpeta vacía, y cada salida que muestran es la de esa corrida. Si alguna no
te da igual, es un defecto de la documentación: [abrí un issue](https://github.com/Segtem/oracle/issues).
