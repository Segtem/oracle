# Encargo 0.18.0 — `oracle juzgar`

2026-09-15. El dueño aprobó el plan [PLAN-0.18.0-JUZGAR.md](../../PLAN-0.18.0-JUZGAR.md) y trabajar
con agy. Revisa y verifica Claude. Leer antes: el plan, `oracle_metalenguaje/motor.py`,
`nucleo/proyecto.py` (`catalogos_a_cargar`, `catalogo_efectivo`, sombras de `oracle.json`),
`nucleo/medida.py` (`Informe`, `medidas_aplicables`), `tools/cli.py` (`cmd_test`, `cmd_probar`,
registro de verbos y ayuda), `tools/aceptacion.py`, `ejemplo/seguimiento-tareas/` completo y
`DECISION-007`, `DECISION-009` y `DECISION-012`.

## Propiedad

Agy: nuevo `tools/juzgar.py`, la integración en `tools/cli.py` (verbo, alias, ayuda, despacho),
`oracle_metalenguaje/motor.py` y `nucleo/proyecto.py` **sólo si P0 demuestra un defecto**, nuevo
`tests/test_juzgar.py`, sección nueva en `docs/12-tareas.md` sobre juzgar los hechos del tracker,
y en `estudios/0.18.0-juzgar/` sus `AVANCE-AGY.md` (primero, con el hallazgo de P0 y el plan de
archivos) e `INFORME-AGY.md` (al final).

Claude: `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/version.py`,
`ejemplo/seguimiento-tareas/` (incluido retirar `evaluar.py`), `tools/verificar_instalacion.py`,
`tools/mutar_codigo.py`, `.github/`, `docs/manual.html`, tests de revisión y todo test existente.
No editar esos archivos. Si un test existente contradice el encargo, anotarlo en el informe.

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.**
Claude ejecuta todo. En el informe no afirmar verificaciones que no se corrieron.

## P0 — con qué catálogo juzga hoy un consumidor

Leer el código y responder con precisión, citando funciones y líneas:

1. Qué selección de medidas usa `oracle test` / `tools/aceptacion.py` para un proyecto externo:
   ¿`catalogos_a_cargar`, `catalogo_efectivo`, otra? ¿Aplica `ambito` y sombras?
2. Qué usa `Motor.desde_proyecto`.
3. Si difieren, describir un proyecto mínimo concreto (archivos y contenido) donde `Motor.evaluar`
   dé un veredicto distinto del que daría la selección de `oracle test`, para que Claude lo
   reproduzca. **No corregir nada todavía**: escribirlo en `AVANCE-AGY.md` y seguir con P1 usando
   la selección de `oracle test`, aislada en una función que ambos puedan compartir después.

## P1 — `tools/juzgar.py`

```bash
oracle proyecto juzgar --con hechos.json [--proyecto RUTA] [--confiar-escalares] [--medida ID]... [--json]
oracle juzgar …        # alias declarado en el registro del CLI, como `ls` de `tarea listar`
```

- `--con` obligatorio. La raíz del proyecto se resuelve como el resto de los verbos de `proyecto`
  (`--proyecto`, `ORACLE_PROYECTO`, directorio actual).
- Evidencia: objeto JSON cuyas claves son textos y cuyos valores son listas de objetos. Cualquier
  otra forma, JSON inválido, archivo ausente o ilegible: **código 2**, diagnóstico con la ruta, sin
  traceback. Leer con un tope de tamaño explícito (declarar cuál) y UTF-8 estricto.
- Catálogo: la selección de `oracle test` (ver P0), con escalares del proyecto sólo bajo
  `--confiar-escalares`; sin la bandera y con `escalares.py` presente, código 2 con el mismo mensaje
  que usa `oracle test`. Proyecto sin `catalogos/` o `oracle.json` inválido: código 2.
- Aplicabilidad: `medidas_aplicables` sobre la evidencia. Ninguna aplicable: **código 1**,
  «SIN MEDIDAS APLICABLES» y las relaciones que trajo la evidencia. Nunca verde.
- `--medida ID` (repetible, sin duplicados): restringe a esas. Un ID que no está en el catálogo o
  que no es aplicable a la evidencia: código 2 que lo nombra. No se completa en silencio con las
  demás.
- Salida: `Informe.texto()` por defecto; con `--json`, `Informe.a_json()` y nada más en stdout
  (diagnósticos a stderr). Código 0 si `informe.ok`, 1 si no.
- No escribe archivos, no usa red, no lee `argv` ni el entorno fuera de lo declarado.
- Ayuda y manual salen de las declaraciones del CLI; revisar que `oracle --help`, `oracle proyecto
  --help` y el manual lo muestren.

## Tests: `tests/test_juzgar.py`

Por CLI (`tools/cli.py`) y proyectos temporales construidos en el test, como los tests del tracker.
Como mínimo: verde con alcance enumerado; rojo con testigo; `--json` parseable y sin ruido en stdout;
cada forma inválida de evidencia (no objeto, valor no lista, fila no objeto, JSON roto, archivo
ausente, UTF-8 inválido, sobre el tope) → 2 sin traceback; nada aplicable → 1; `--medida` válida,
inexistente, no aplicable y repetida; escalares presentes sin `--confiar-escalares` → 2; proyecto
inválido → 2; el alias `juzgar` y `proyecto juzgar` dan la misma salida; ayuda sin escrituras; y un
recorrido con los hechos reales del tracker: `oracle tarea hechos` sobre un tracker temporal,
juzgado con `ejemplo/seguimiento-tareas`, verde y luego rojo con un enlace roto construido.

## Documentación

Sección breve en `docs/12-tareas.md`: cómo juzgar los hechos del tracker con `oracle juzgar`, qué
significa cada política y qué no prueba. Sin afirmaciones que el código no sostenga.
