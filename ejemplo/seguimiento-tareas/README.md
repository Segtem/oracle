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
