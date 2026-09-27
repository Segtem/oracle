# oracle formatear como chequeo: código de salida y ayuda al día

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: 

### Nota (2026-09-26 23:54:09 UTC)

2026-09-26, Claude, visto al rehacer la web con 0.32.0: (1) oracle formatear sin --escribir sale 0 aunque haya archivos que requieren formato, así que no sirve como chequeo de CI (como black --check o gofmt -l); proponer que salga 1 si algo requiere formato. (2) Con --escribir imprime el diff con la sugerencia «oracle formatear … --escribir» justo antes de decir «escrito»: sobra la sugerencia en ese modo. (3) La ayuda de oracle convertir <directorio> --a-superficie dice «Migra medidas y casos»; migra también relaciones. Son cambios de código de tools/cli.py: van con su test y su mutación en la próxima versión.
