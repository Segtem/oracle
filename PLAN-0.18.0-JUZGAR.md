# Roadmap 0.18.0 — juzgar evidencia real desde el CLI

Fecha: 2026-09-15. Base: distribución 0.17.0, álgebra 0.6, sintaxis 0.4.
Implementa agy; revisa, mide y corta Claude. Encargo: [estudios/0.18.0-juzgar/ENCARGO-AGY.md](estudios/0.18.0-juzgar/ENCARGO-AGY.md).

## El problema

Oracle verifica bien su catálogo (`oracle test`: corpus, aceptación, diferencial, mutación), pero
no tiene un verbo para lo que un consumidor hace después: **juzgar evidencia real** —un JSON de
hechos— con ese catálogo. Cada uno lo resolvió por su cuenta con la fachada `Motor`:

- `ejemplo/seguimiento-tareas/evaluar.py` (las políticas del tracker, 0.16.0);
- `tools/juzga_oracle.py` en LyraGASP;
- `Content/Python/jam/oracle_shadow.py` en Jam.

Tres adaptadores para la misma operación son la señal de que falta en Oracle. Y el tracker sigue
siendo un vecino: `oracle tarea hechos` emite relaciones que ningún comando de Oracle juzga, y el
propio Oracle no mide su `tareas/`.

Medido el 2026-09-15: el `tareas/` de Oracle pasa hoy las tres políticas de seguimiento con el
adaptador (5 archivos, 9 referencias locales presentes, 0 omisiones, Git comprobado).

## Decisión de diseño: `juzgar` no es `oracle test`

`oracle test` responde «¿este catálogo está bien fijado?». Juzgar evidencia responde «¿estos hechos
cumplen el catálogo?». Mezclarlos en un comando haría que un VERDE signifique dos cosas distintas.
Va un verbo aparte: `oracle proyecto juzgar` (alias `oracle juzgar`).

## Entregas

### P0 — ¿con qué catálogo juzga un consumidor hoy?

`Motor.desde_proyecto` carga con `catalogos_a_cargar` (base + proyecto). `nucleo/proyecto.py`
también tiene `catalogo_efectivo`, que aplica el `ambito` de cada medida (`del_origen` sólo en su
origen). Hay que medir —no suponer— qué selección usan `oracle test` y la aceptación, y si
`Motor.desde_proyecto` evalúa medidas que el proyecto no debería evaluar o ignora las sombras de
`oracle.json`. Si hay diferencia, es un defecto de la fachada que hoy afecta a LyraGASP y a Jam, y
se decide antes de construir P1 encima.

Salida: reproducción mínima con número, o nota de que coinciden con la prueba que lo muestra.

### P1 — el verbo

```bash
oracle juzgar --con hechos.json [--proyecto RUTA] [--confiar-escalares] [--medida ID]... [--json]
```

- La evidencia es un objeto `relación → lista de filas` (objetos). Otra forma, JSON inválido o
  archivo ilegible: código 2 con diagnóstico, sin traceback.
- Carga el mismo catálogo que corresponde según P0, con escalares sólo bajo `--confiar-escalares`.
- `--medida` (repetible) restringe a esas medidas; pedir una que no existe o que no es aplicable a
  la evidencia es error, no un verde vacío.
- Ninguna medida aplicable: código 1 con el mensaje de `SinMedidasAplicables`, nunca verde.
- Salida `Informe.texto()` (un verde enumera lo que no miró) o `Informe.a_json()` con `--json`.
- Códigos: 0 todo verde; 1 algún rojo o nada aplicable; 2 entrada o proyecto inválidos.
- No escribe archivos. Ayuda, manual y `oracle --help` desde las declaraciones del CLI.

### P2 — el tracker deja de ser un vecino

- `ejemplo/seguimiento-tareas/evaluar.py` se retira; su README y `docs/12-tareas.md` pasan a
  `oracle tarea hechos --git > hechos.json && oracle juzgar --proyecto ejemplo/seguimiento-tareas --con hechos.json`.
- `tools/verificar_instalacion.py` ejercita `oracle juzgar` desde el wheel, en verde y con el
  defecto construido que ya usa (enlace roto → código 1 con su testigo).
- CI juzga el `tareas/` del propio Oracle con las tres políticas, en el job `contratos`.

## Fuera de alcance

- Publicar las políticas de seguimiento como **biblioteca** (DECISION-007): exige certificarla con
  corpus y mutación propios; va después de que `juzgar` exista.
- Cambiar los adaptadores de LyraGASP y Jam: cada consumidor decide cuándo adoptarlo.
- Nuevas medidas, álgebra o sintaxis. `VERSION_ALGEBRA` y `VERSION_SINTAXIS` no deberían cambiar.

## Criterios de salida del corte

Suite completa verde; tests del verbo de ambos lados (agy y revisión independiente); mutación del
módulo nuevo y de los que cambien, sin sobrevivientes ni equivalentes; `verificar_instalacion` con
el recorrido nuevo; CI verde con el paso de `tareas/`; notas, especificación y cifras al día.
