# El MCP no sabe de sombras, no juzga la evidencia entera y no lee el tracker

- ESTADO: ABIERTA
- PRIORIDAD: 68
- ETIQUETAS: oracle, mcp, metalenguaje


Medido el 2026-09-16 contra el árbol de 0.26.0. El servidor `oracle-mcp` no cambia desde 0.7.0 y
tiene tres huecos:

1. **Sombras.** `oracle_evaluar` por id de la política de cierres del tracker devuelve `rojo 4` y
   no dice que la medida está en sombra con cota 4. `estudios/MCP-CONTRATO.md` no nombra las
   sombras.
2. **No hay juzgar.** Evalúa una medida por llamada; no hay una herramienta que juzgue una evidencia
   contra el catálogo efectivo, así que lo de 0.27.0 —cotas que se respetan, medidas propias que no
   se aplicaron— no llega al MCP.
3. **El tracker.** Un agente sin shell (agy) no puede leer `tareas/`. Decisión del dueño: **sólo
   lectura**. Crear, anotar y cerrar siguen en el CLI, junto al commit que les corresponde.

Plan y encargo: `estudios/0.27.0-mcp/`. Entra en 0.27.0.
