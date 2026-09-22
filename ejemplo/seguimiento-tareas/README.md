# Políticas optativas para el tracker

Este proyecto de ejemplo consume `oracle tarea hechos`. Usa el álgebra y las macros existentes;
no instala políticas universales ni cambia qué se exige para cerrar una tarea. Sus casos son
construidos para fijar decisiones del ejemplo; no describen material personal observado.

La configuración desactiva el catálogo base y los perfiles. Las medidas locales tienen
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
oracle juzgar --proyecto ejemplo/seguimiento-tareas --con /tmp/hechos-tareas.json
```

`oracle juzgar` carga el catálogo efectivo de este proyecto, evalúa las medidas aplicables a esa
evidencia y muestra veredictos y testigos. Sale 0 si pasan, 1 si hay un rojo fuera de sombra o
ninguna medida aplica, y 2 si la entrada o el proyecto son inválidos. `--medida` restringe a una
política y se puede repetir:

```bash
oracle juzgar --proyecto ejemplo/seguimiento-tareas --con /tmp/hechos-tareas.json \
  --medida seguimiento.referencias_locales_presentes --medida seguimiento.lectura_sin_omisiones
```

Sin instalar, desde el checkout, los mismos verbos corren con `python3 -B tools/cli.py`. Hasta 0.17.0
esto lo hacía un script de este ejemplo, `evaluar.py`; `oracle juzgar` lo reemplaza desde 0.18.0.

Para adoptar estas políticas, copiar sólo las medidas y declaraciones de relaciones deseadas a
`catalogos/` y `relaciones/` del proyecto, revisando antes sus alcances. No se activan por importar
Oracle ni por crear `tareas/`. El campo `estado_declarado` no prueba trabajo completado;
la existencia de un archivo no prueba autenticidad ni que haya un backup remoto.

Verificación reproducible del ejemplo desde el checkout:

```bash
python3 -B tools/corpus.py --proyecto ejemplo/seguimiento-tareas
python3 -B tools/mutar.py --proyecto ejemplo/seguimiento-tareas
```

## Cierre con medidas del dominio

`tarea_cierre_medida` declara los criterios `CIERRA CON`; `aceptacion_medida` aporta
los veredictos individuales actuales. La política
`seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre` exige un verde para cada
criterio de una tarea CERRADA. Abiertas y cerradas sin criterios cumplen por vacuidad.
Si falta la relación de aceptación la política no aplica; si está vacía, sí aplica.
Una medida inexistente o no evaluada no acredita verde.

El flujo consumidor corre `juzgar --json` sobre el dominio, convierte `medidas[].id/ok`,
extrae el tracker y juzga únicamente esta política sobre la composición. Conserva
el `ok` individual incluso ante sombras; omite `no_aplicadas`. Sólo admite informes
válidos de ejecuciones con código 0/1. Ante errores aborta con código 2 y sin informe
por stdout; el archivo temporal es nuevo por corrida y se elimina, sin reutilizar
aceptaciones anteriores. El código final 0/1 es el veredicto de la política de cierre,
no el veredicto global del dominio. `oracle test` no es evidencia de dominio verde.

Desde el checkout:

```bash
python3 -B ejemplo/seguimiento-tareas/cierre_medidas.py \
  --proyecto /ruta/al/dominio --con /ruta/evidencia-actual.json \
  --tracker /ruta/al/dominio
```

Para usar una instalación, agregar `--oracle oracle` al final. Al copiar el flujo,
copiar también la política y sus tres declaraciones de relaciones, o indicar
`--politicas /ruta/al/catalogo-de-seguimiento`. `--git` agrega el diagnóstico Git.
La evidencia del dominio debe corresponder al estado que se quiere aceptar: el
flujo la evalúa de nuevo, pero no produce ni autentica esos hechos. El tracker
continúa independiente del motor y no impide editar o cerrar una tarea; esta
política se exige ejecutando el flujo en el proceso de revisión o CI.
