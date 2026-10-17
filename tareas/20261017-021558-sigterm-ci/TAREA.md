# test_SIGTERM de la mutación de código falla a veces en CI con Python 3.13.16

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: ci, mutacion

### Nota (2026-10-17 02:15:58 UTC)

Visto el 2026-10-17 al publicar 0.39.0: tests.test_mutacion_codigo.CorrerTests.test_SIGTERM_no_toca_el_original_y_termina_el_subproceso venció el proc.wait(timeout=15) en contratos (3.13) de GitHub (Python 3.13.16; la última corrida verde fue con 3.13.15), dos veces sobre 6542f41 (run 38988391795 y su reintento) y pasó otra (ci-head-b, run 38992290669); v0.38.2 pasó dos veces (runs 38991810170 y 38992292899). En local pasa siempre, también con 3.13.16 y dentro de la suite. El log muestra que correr() borra su TemporaryDirectory mientras el subproceso del mutante sigue vivo: 'OSError: [Errno 39] Directory not empty: .../slot_0/proyecto' y 'ResourceWarning: subprocess N is still running'. Hipótesis: tras SIGTERM, la ronda limpia antes de esperar a que muera el grupo del mutante. No lo toca el cambio de --con.

### Nota (2026-10-17 12:10:58 UTC)

Causa: el handler de SIGTERM levantaba SystemExit en el hilo principal mientras esperaba h.join(); los trabajadores seguían tomando sitios y lanzando mutantes mientras se borraba la carpeta de la ronda (se ve determinísticamente: la limpieza de oracle-mutacion-* empezaba con un trabajador vivo). Arreglo en 8c3d9a2: _TERMINANDO, join de los trabajadores antes de limpiar, sin lanzar ni anotar después, y kill del proceso registrado tarde. Falta: ver el CI de GitHub en verde con 3.13.
