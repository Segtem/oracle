# Políticas optativas para el tracker

Este proyecto de ejemplo consume `oracle tarea hechos`. Usa el álgebra y las macros existentes;
no instala políticas universales ni cambia qué se exige para cerrar una tarea. Sus casos son
construidos para fijar decisiones del ejemplo; no describen material personal observado.

La configuración desactiva el catálogo base y los perfiles. Las tres medidas locales tienen
alcance y defensa propios:

- `referencias_locales_presentes`: las referencias locales reconocidas deben apuntar a rutas
  presentes dentro del proyecto. URLs remotas y anclas quedan fuera de esa comprobación.
- `archivos_confirmados_sin_cambios`: requiere consulta Git, archivos presentes en HEAD y sin
  cambios pendientes. Fallará si se crearon o editaron archivos que todavía no están confirmados.
- `lectura_sin_omisiones`: requiere una lectura que no declare omisiones del formato soportado.
  Conviene combinarla con la de referencias para no confundir un análisis parcial con uno completo.

Con Oracle instalado, desde la raíz del checkout:

```bash
oracle tarea hechos --proyecto /ruta/al/proyecto --git > /tmp/hechos-tareas.json
python3 ejemplo/seguimiento-tareas/evaluar.py --con /tmp/hechos-tareas.json
```

`evaluar.py` usa las APIs públicas `Motor.desde_proyecto` y `Medida.evaluar`: carga ese JSON y
las medidas del proyecto contiguo, y muestra veredictos y testigos. Devuelve 0 si todas las
políticas elegidas pasan, 1 si hay incumplimiento o evidencia requerida ausente y 2 si no pudo
cargar/evaluar la entrada. Se puede elegir una política o repetir la opción:

```bash
python3 ejemplo/seguimiento-tareas/evaluar.py --con /tmp/hechos-tareas.json \
  --politica referencias_locales_presentes --politica lectura_sin_omisiones
```

No se pasa la ruta JSON a `oracle medida probar --con`: ese comando recibe texto en superficie
de evidencia. Si se trabaja sin instalar desde el checkout, se puede usar
`python3 -B tools/cli.py tarea hechos ...`; para el script consumidor, agregar el checkout a
`PYTHONPATH` o instalar el wheel en un entorno de prueba. La verificación de instalación de Oracle
ejercita el script con una instalación limpia fuera del checkout.

Para adoptar estas políticas, copiar sólo las medidas y declaraciones de relaciones deseadas a
`catalogos/` y `relaciones/` del proyecto, revisando antes sus alcances. No se activan por importar
Oracle ni por crear `tareas/`. El campo `estado_declarado` no prueba trabajo completado;
la existencia de un archivo no prueba autenticidad ni que haya un backup remoto.

Verificación reproducible del ejemplo desde el checkout:

```bash
python3 -B tools/corpus.py --proyecto ejemplo/seguimiento-tareas
python3 -B tools/mutar.py --proyecto ejemplo/seguimiento-tareas
```
