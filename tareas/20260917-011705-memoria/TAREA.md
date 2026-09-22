# La mutación en paralelo puede comerse la memoria de la máquina

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, mutacion, infra


## Qué pasó

El 2026-09-16 Claude Code detuvo dos veces una tarea de fondo «porque el sistema se queda sin
memoria», mientras corrían cuatro rondas de `tools/mutar_codigo.py` en paralelo. No es la primera
vez: el 2026-09-15 una ronda se comió la RAM y el sistema mató procesos ajenos (eso trajo
`--limite-memoria-mb` en 0.24.0).

## Lo medido (2026-09-16, 01:1x)

- **No fue el kernel.** `journalctl -k` no registra ningún OOM; no hay `earlyoom` ni
  `systemd-oomd`. Lo que corta es el monitor de memoria de Claude Code, que detiene tareas de fondo
  cuando la memoria disponible baja.
- **No es el tmpfs.** `/tmp` (16 GB, en RAM) tiene 1,7 GB ocupados; las copias de las rondas pesan
  entre 40 y 400 MB cada una.
- **En reposo, una ronda usa ~100 MB** (arnés + suite). El pico de un proceso de la suite completa
  es **310 MB** de RSS.
- **El tope por mutante es 4000 MB** (`RLIMIT_AS`), trece veces lo que la suite necesita. Un mutante
  que entra en un bucle que asigna —como el de `tareas_consulta.py` de 0.24.0— llega hasta ahí y se
  queda hasta el timeout de 300 s.
- **El tope es por proceso, no por ronda ni por máquina.** Cuatro rondas en paralelo pueden tener
  cuatro mutantes desbocados a la vez: 16 GB. Y `RLIMIT_AS` se hereda, pero cada subproceso que
  lanza un test (el CLI, el servidor MCP) recibe **su propio** tope entero.
- **La máquina no está vacía:** el escritorio (Chrome, Steam, JetBrains, Plasma) usa ~9 GB de 31.
- **Hay cgroups de usuario:** `systemd-run --user --scope -p MemoryMax=…` funciona, y es un techo
  que cubre a todos los procesos de adentro juntos, nietos incluidos.

## Qué hacer

1. **Bajar el tope por omisión** a algo proporcional a lo que la suite usa de verdad: medir el pico
   de memoria virtual (no sólo RSS, porque el tope es `RLIMIT_AS`) de la línea base y elegir un
   número con margen, defendido con esa medición.
2. **Un techo para todas las rondas juntas.** Las rondas en paralelo se lanzan dentro de un scope de
   systemd con `MemoryMax` (y sin swap), para que ningún conjunto de mutantes pueda llevar la
   máquina al límite. Decidir si eso vive en el arnés (`--techo-memoria`, cuando haya cgroups) o en
   la receta de cómo se corren rondas en paralelo, y escribirlo donde se lea.
3. **Que el paralelismo no se elija a ojo:** la cantidad de rondas simultáneas sale de la memoria
   disponible y del tope, no de «4 porque sí».
4. Un test que fije el tope nuevo, y la medición en las notas.

### Nota (2026-09-21 21:46:26 UTC)

Medición de línea base completa con bytecode frío: Python 3.14.7, Linux 7.2.6 x86_64, 2386 tests verdes en 152,04 s; /proc/PID/status cada 10 ms (15011 muestras): VmPeak 760328 KiB = 742,51 MiB; VmHWM 105276 KiB = 102,81 MiB. Evidencia y script reproducible en verificacion/. Tope predeterminado reducido de 4000 a 1024 MiB (37,9 % de margen virtual), con una fuente en el perfil reutilizada por el CLI y tests actualizados. docs/mutacion-memoria.md documenta concurrencia N=min(raíces, floor((MemAvailable_MiB/2)/(2*tope_MiB+512))) y un único scope systemd con MemoryMax y MemorySwapMax=0; sin integración systemd en el arnés. En curso: suite final y ronda parcial --objetivo nucleo/algebra.py --lineas 54 --timeout 300.

### Nota (2026-09-21 21:47:41 UTC)

Primera verificación final: 2386 tests, un fallo por ejecutar simultáneamente la ronda parcial y la suite en la misma raíz: test_cli_filtro_vacio_retorna_codigo_2 recibió RondaEnCurso. Es interferencia del bloqueo del arnés, no fallo del límite. Se conserva suite-concurrente.log y se repetirá la suite sola una vez terminada la ronda parcial. Receta validada con bash -n y lanzadores simulados (presupuestos insuficiente, 5000 y 8000 MiB; concurrencias 0, 1 y 2); no se ejecutó un scope real de systemd.

### Nota (2026-09-22 10:56:31 UTC)

Continuación completada el 2026-09-22, sin commits. Revisados el límite único de 1024 MiB, su propagación al CLI y la receta de concurrencia/techo común; la medición previa de VmPeak 742,51 MiB respalda 37,9 % de margen. Agregada sección Sin publicar en NOTAS-DE-RELEASE.md con la medición y enlace a la receta. Verificación secuencial: python3 -m unittest tests.test_mutacion_codigo.LimiteMemoriaTests -v: 13 tests OK (2,520 s); python3 -m unittest discover -s tests -t . -q: 2386 tests OK (80,389 s). Ronda python3 tools/mutar_codigo.py --objetivo nucleo/algebra.py --lineas 54 --timeout 300 --hechos: baseline verde, bytecode frío, 1 mutante muerto por tests, 0 timeouts, 0 errores de arnés, fuentes originales intactas. Evidencia en verificacion/tests-memoria.log, suite-final.log y parcial.json; --hechos salió 0 al emitir evidencia, pero parcial=true no acredita una ronda completa de release. La receta de systemd mantiene la validación simulada previa; no se probó un scope real en este entorno. El relevo obsoleto de la tarea cerrada 20260915-112728-memoria se reemplazó por una referencia a esta tarea. Quedan para Claude los commits, la integración y el cierre; .git no se modificó.

## Próximo paso

Claude: revisar los cambios y la evidencia en `verificacion/`, hacer los commits con
el ID `20260917-011705-memoria`, integrar a `main` y cerrar la tarea con el commit
`20260917-011705-memoria: done`. Implementación y verificación terminadas:
13 tests de memoria y suite completa de 2386 tests en verde; ronda parcial con
línea base verde y su único mutante muerto por tests. No quedan cambios de código
pendientes de este relevo. Codex no hizo commits porque `.git` es de sólo lectura.
