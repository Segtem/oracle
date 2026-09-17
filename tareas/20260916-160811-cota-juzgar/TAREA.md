# oracle juzgar perdona un rojo en sombra aunque supere su cota

- ESTADO: CERRADA
- PRIORIDAD: 72
- ETIQUETAS: oracle, metalenguaje, sombra


Medido el 2026-09-16 al investigar el CI rojo de 0.25.2: `seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre`
está en sombra con `cota: 4` en `ejemplo/seguimiento-tareas/oracle.json`, y dio 30. La cota sólo la
hace cumplir la meta-medida de `oracle test`; `oracle juzgar` la perdona igual que si diera 4.

Una sombra existe para que un rojo conocido no tape los demás, no para que crezca sin límite. A
hacer: que `juzgar` (y, si corresponde, `Motor`) perdone sólo si el valor es ≤ la cota, con tests de
las dos ramas. Cambia colores en consumidores → sube la MENOR.
