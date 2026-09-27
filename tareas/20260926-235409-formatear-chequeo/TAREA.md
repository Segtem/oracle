# oracle formatear como chequeo: código de salida y ayuda al día

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: 

### Nota (2026-09-26 23:54:09 UTC)

2026-09-26, Claude, visto al rehacer la web con 0.32.0: (1) oracle formatear sin --escribir sale 0 aunque haya archivos que requieren formato, así que no sirve como chequeo de CI (como black --check o gofmt -l); proponer que salga 1 si algo requiere formato. (2) Con --escribir imprime el diff con la sugerencia «oracle formatear … --escribir» justo antes de decir «escrito»: sobra la sugerencia en ese modo. (3) La ayuda de oracle convertir <directorio> --a-superficie dice «Migra medidas y casos»; migra también relaciones. Son cambios de código de tools/cli.py: van con su test y su mutación en la próxima versión.

### Nota (2026-09-27 18:37:18 UTC)

2026-09-27, ENCARGO (agy2, en contenedor, worktree propio): (1) oracle formatear sin --escribir sale 1 si algún archivo requiere formato (0 si todos ya tienen forma única), para usarlo como chequeo de CI como black --check o gofmt -l; con --escribir sale 0 si pudo escribir; un error de lectura o de sintaxis sigue saliendo como hoy (con ✗). (2) Con --escribir no imprime la sugerencia «oracle formatear … --escribir» que hoy aparece justo antes de «escrito»: muestra el diff y «escrito». (3) La ayuda de oracle convertir <directorio> --a-superficie dice «Migra medidas y casos»: migra también relaciones. (4) Documentarlo donde se enseña formatear (docs/03-escribir-una-medida.md; en docs/como-funciona.md la salida la regenera tools/guia.py --escribir). Tests que fallen sin el cambio. Suite entera verde; si el sitio o las cifras quedan vencidos, python3 tools/sitio.py --escribir y python3 tools/cifras.py --actualizar; si cambian líneas de un archivo del perfil de mutación, python3 tools/mutar_codigo.py --reapuntar-equivalentes. Sin commits. Informe en tareas/20260926-235409-formatear-chequeo/AVANCE.md.
