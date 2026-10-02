# Preparar el próximo corte de Oracle con tag y paquetes listos para PyPI

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS:

### Nota (2026-10-02 10:22:17 UTC)

Corte elegido: 0.38.1, mantenimiento sin cambios de álgebra 1.0 ni sintaxis 1.1. PyPI consultado: última 0.38.0; 0.38.1 libre. Instalación aislada WHEEL OK. Primera suite 2257 tests: dos fallos por salidas oracle --version todavía en 0.38.0; se regeneraron con tools/guia.py. Se preparó build/twine en /tmp/oracle-web-corte/empaquetado. No se publicó nada en PyPI.

### Nota (2026-10-02 10:46:38 UTC)

Mutación --alto sobre nucleo/version.py, tools/guia.py y tools/sitio.py completos desde v0.38.0: 412 mutantes no equivalentes, 411 muertos, 0 vivos y 1 timeout a 90 s; 8 equivalentes existentes. Reintento aislado del único timeout nucleo/version.py:82:7:negacion con 240 s: 1/1 muerto, sin timeout ni error. Unión de ambos ensayos: 412/412 muertos. La segunda invocación es parcial por diseño (exit 2); no se presenta como una corrida completa única. Fuentes mutadas idénticas a afad7f8; luego sólo se completaron documentos, CSS y pruebas JS.

### Nota (2026-10-02 10:48:40 UTC)

Paquetes finales construidos desde git archive del commit afad7f8. Twine strict PASSED en wheel y sdist. Verificación de instalación WHEEL OK y prueba adicional del wheel exacto fuera del checkout: versión 0.38.1, plantilla y oracle test verdes. Artefactos en dist/0.38.1; hashes SHA256SUMS y evidencia VERIFICACION.md en esta tarea. Publicación de Brian registrada en pypi-0-38-1; no se ejecutó upload.

### Nota (2026-10-02 10:51:43 UTC)

Chequeo del tracker detectó tres cierres históricos recientes sin commit exacto: de-cero-a-mano, de-cero-arbol y resaltado-web. Se registraron sus cierres sin tocar implementación. Tracker vuelve a VERDE dentro de la sombra histórica ya declarada (4, sin subir cota); evidencia tracker-final.log. El tag del corte incluye estos cierres; desde el commit fuente sólo cambió tareas/.

## Próximo paso

Preparación terminada: corte v0.38.1 con paquetes y comprobaciones en VERIFICACION.md. Brian continúa la publicación en pypi-0-38-1.
