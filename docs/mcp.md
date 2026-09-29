# El servidor MCP

Un agente de programación puede consultar a Oracle por [Model Context Protocol](https://modelcontextprotocol.io):
qué reglas aplican, qué dice una medida sobre estos hechos, qué parte de una medida candidata todavía
no está fijada y cuál es el veredicto del catálogo entero. El servidor es el paquete aparte
[**oracle-mcp**](https://github.com/Segtem/oracle-mcp), que desde Oracle 0.34.0 ya no viene dentro de
`oracle-metalenguaje`.

## Sólo lectura, y por qué

Las cinco herramientas son de **sólo lectura**. No es prudencia genérica: los falsos verdes que un
agente comete ocurren al leer, y una escritura «aprobada» por dos evidencias que el mismo agente
fabricó parece una aprobación sin serlo. El proyecto se fija al arrancar el servidor, y
`--confiar-escalares` sólo se concede ahí: ninguna llamada puede ampliar esa autoridad.

## Instalación

```bash
uv tool install oracle-mcp
```

Trae la versión de Oracle con la que se probó, fijada con `==`: el servidor usa API interna de
Oracle, y una versión distinta podría romperlo sin avisar.

## Configurarlo en un cliente

El servidor habla por stdio. Se le dice qué proyecto mirar con `--proyecto <ruta>`.

**Claude Code**, desde la raíz del proyecto:

```bash
claude mcp add oracle -- oracle-mcp --proyecto .
```

**Codex**, en `~/.codex/config.toml`:

```toml
[mcp_servers.oracle]
command = "oracle-mcp"
args = ["--proyecto", "/ruta/al/proyecto"]
```

## Las herramientas

| herramienta | responde |
|---|---|
| `oracle_effective_catalog` | qué medidas obligan a este proyecto, y por qué |
| `oracle_evaluate` | qué hace una medida —por id o escrita en la llamada, en superficie— con una evidencia: verde, rojo o sin evidencia, testigos y, si está en sombra, si la sombra la perdona |
| `oracle_challenge` | qué parte de una medida candidata todavía no está fijada: las dos polaridades y sus mutantes, sin guardar nada |
| `oracle_judge` | lo mismo que `oracle juzgar`: una evidencia contra el catálogo efectivo, con sombras, cotas y las medidas que no se aplicaron |
| `oracle_tasks` | el tracker de tareas del proyecto ([trackertast](https://github.com/Segtem/trackertast)): listar, ver, buscar y hechos |
| `oracle_requirements` | qué promesas de `requisitos/` mide alguna medida, cuáles en parte y cuáles no: lo que `oracle cobertura` imprime, como datos (desde oracle-mcp 0.1.1) |

Una medida escrita en la llamada se recibe sólo en superficie `.oracle` y en la forma única, igual
que en un archivo. Hasta Oracle 0.33.0 las herramientas se llamaban en español
(`oracle_evaluar`, `oracle_juzgar`, …); desde oracle-mcp 0.1.0 se llaman en inglés.

El contrato completo —esquemas de entrada y salida, errores tipados, huellas y garantías de
transporte— está en [el repositorio de oracle-mcp](https://github.com/Segtem/oracle-mcp/blob/main/docs/contract.md).
