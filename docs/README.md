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
| conectar un proyecto que ya existe | [Conectar un proyecto](07-conectar-a-un-proyecto-propio.md) | el sensor partido en puro y adaptador, vigilar sensores con `oracle cambios`, las escalares propias y la sombra |
| escribir medidas con soltura | [Escribir una medida](03-escribir-una-medida.md) | las reglas de la forma única (comentarios, aritmética, `.relacion`), cómo se aíslan las escalares, por qué los ids son ASCII |
| patrones para pares sin duplicar y contar distintos | [Recetas de medidas](recetas.md) | pares no orientados con `<`, y recuento de distintos con doble `agrupar` |
| ver un dominio completo con geometría | [Tutorial práctico](tutorial-practico.md) | un `LEFT JOIN` sin nulos, escalares de volumen y penetración, la API `Motor` desde Python |
| saber por qué hace falta mutar | [Por qué la mutación](05-por-que-la-mutacion.md) | los dos autores de los mutadores, qué hacer con un sobreviviente y qué mide el respaldo real |
| correr la mutación sin quedarte sin memoria | [Memoria de la mutación](mutacion-memoria.md) | cómo medir la memoria y limitar las rondas con systemd |
| llevar las tareas del proyecto | [trackertast](https://github.com/Segtem/trackertast) (paquete aparte) | el comando `tasks` y el próximo paso como relevo |
| usar un modelo como sensor de prosa | [Un modelo como sensor](14-sensor-prosa.md) | el patrón optativo, con calibración y revisión humana |
| verificar una spec de OpenSpec | [OpenSpec y Oracle](openspec.md) | `oracle requisito importar`, medir cada escenario y `oracle cobertura --con` en CI o `/opsx:verify` |
| conectar un agente por MCP | [El servidor MCP](mcp.md) (paquete aparte, oracle-mcp) | cómo configurarlo en Claude Code y Codex, y por qué es sólo de lectura |
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
- **`oracle cobertura [--con <hechos.json>]`**: qué requisitos están medidos; con evidencia, cuáles
  se cumplen (✓), cuáles en parte (◐ con su `SIN MEDIR`) y cuáles no (✗).
- **`oracle cambios [--desde <ref>]`**: qué medidas se aflojaron, qué relaciones o escalares cambiaron,
  y qué archivos de sensores declarados en `oracle.json` fueron tocados.
- **`oracle caso generar <medida>`**: busca evidencia discriminante en el corpus y literales de la medida,
  encuentra dónde discrepan la regla y el mutante, y encoge el caso resultante.

Las guías con comandos —la de la batalla naval, *Cómo funciona*, *De cero a un rojo*, *Por qué la
mutación*, *Conectar un proyecto*, *La primera medida real* y *Recetas de medidas*— se ejecutan en la suite del
repositorio desde una carpeta vacía, y cada salida que muestran es la de esa corrida. Si alguna no
te da igual, es un defecto de la documentación: [abrí un issue](https://github.com/Segtem/oracle/issues).
