# Memoria y rondas de mutación en paralelo

`--limite-memoria-mb` limita el espacio de direcciones virtuales **por proceso**
mediante `RLIMIT_AS` (MiB, aunque la opción diga `mb`). Los hijos heredan el límite,
pero cada uno dispone de su propio cupo. `0` lo desactiva. El arnés no administra
cgroups ni decide cuántas raíces lanzar: esa política vive en esta receta.

## Calcular antes de lanzar

Usar `MemAvailable` de `/proc/meminfo`, no `MemFree`. Reservar la mitad para el
resto de la máquina. El presupuesto común es `B = floor(disponible_MiB / 2)` y el
costo presupuestado por ronda es `C = 2 * limite_MiB + 512`: dos procesos al tope
más 512 MiB para el arnés, copias y caché. La concurrencia es
`N = min(cantidad_de_raices, floor(B / C))`. Si da cero, no lanzar.

Este costo es una reserva operativa, no una cota del árbol de procesos: un test
puede crear más hijos. El techo común es el que contiene ese caso. Si el proyecto
necesita más hijos simultáneos o copias más grandes, aumentar `C`. Recalcular en
cada lote; no lanzar varios lotes independientes con el mismo presupuesto.

## Un scope para todo el lote

Ejecutar desde Oracle, con raíces distintas y previamente preparadas con los
mismos cambios. Pasar cada raíz una sola vez. El bloqueo del arnés impide dos rondas sobre una misma raíz.
Guardar el siguiente bloque como `/tmp/oracle-rondas.sh` y pasar las rutas como
argumentos. Requiere Bash, Linux con cgroup v2 y systemd de usuario con controlador
de memoria disponible. La receta hace una comprobación **parcial** de una línea;
los parámetros `OBJETIVO` y `LINEAS` permiten elegir otra zona.

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# == 0 )); then
    echo 'Uso: bash /tmp/oracle-rondas.sh /ruta/raiz-a /ruta/raiz-b' >&2
    exit 1
fi
# Se lee el valor vigente del código y se pasa explícitamente a todas las raíces.
export LIMITE_MIB
LIMITE_MIB=$(python3 -c 'from tools.mutar_codigo import LIMITE_MEMORIA_MB_PREDETERMINADO; print(LIMITE_MEMORIA_MB_PREDETERMINADO)')
export OBJETIVO=${OBJETIVO:-nucleo/algebra.py}
export LINEAS=${LINEAS:-54}
# DISPONIBLE_MIB permite reducir la lectura del host en contenedores o slices
# con límites propios: usar el menor margen entre memory.max y memory.current
# de todos los ancestros del scope, además de MemAvailable.
# En ese entorno, establecer DISPONIBLE_MIB antes de ejecutar esta receta.
disponible=$(awk '/^MemAvailable:/ {print int($2 / 1024)}' /proc/meminfo)
if [[ -n ${DISPONIBLE_MIB:-} ]]; then
    [[ $DISPONIBLE_MIB =~ ^[0-9]+$ ]] || exit 1
    (( DISPONIBLE_MIB >= disponible )) || disponible=$DISPONIBLE_MIB
fi
presupuesto=$((disponible / 2))
costo=$((2 * LIMITE_MIB + 512))
rondas=$((presupuesto / costo))
(( rondas <= $# )) || rondas=$#
if (( rondas < 1 )); then
    echo "No alcanza: presupuesto ${presupuesto} MiB; ronda ${costo} MiB" >&2
    exit 1
fi
printf 'Tope por proceso: %s MiB; techo común: %s MiB; concurrencia: %s\n' \
    "$LIMITE_MIB" "$presupuesto" "$rondas"
# xargs y todos sus descendientes viven dentro del MISMO scope.
systemd-run --user --scope \
    -p MemoryAccounting=yes -p "MemoryMax=${presupuesto}M" -p MemorySwapMax=0 \
    bash -c '
        paralelas=$1; shift
        printf "%s\0" "$@" | xargs -0 -r -n 1 -P "$paralelas" bash -c '\''
            cd -- "$1" || exit 2
            exec python3 tools/mutar_codigo.py --objetivo "$OBJETIVO" \
                --lineas "$LINEAS" --timeout 300 \
                --limite-memoria-mb "$LIMITE_MIB"
        '\'' _
    ' _ "$rondas" "$@"
```

`MemoryMax` limita el uso conjunto del cgroup; `MemorySwapMax=0` impide que el
lote use swap. Ver la documentación de
[control de recursos de systemd](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.resource-control.xml)
y de [systemd-run](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-run.xml).
Si systemd rechaza el scope, resolver la configuración antes de lanzar el lote;
no sustituirlo por varios scopes con el techo entero cada uno.

Una ronda parcial sale con código 2 aunque mate todos los mutantes; `xargs`
convierte códigos 1–125 de sus comandos en 123. Leer los informes individuales:
un timeout, una muerte por OOM o un error del arnés no demuestran que los tests
mataron un mutante. Esta receta no produce evidencia de release.

## Medición que justifica el predeterminado

El 2026-09-21, en Linux 7.2.6 x86_64 y Python 3.14.7, la línea base completa
(`python3 tools/ejecutar_suite_mutacion.py`, 2386 tests, verde) tardó 152,04 s.
Se muestreó `/proc/<pid>/status` del proceso de la suite cada 10 ms (15011 lecturas):

| Campo | KiB | MiB |
|---|---:|---:|
| `VmPeak` (máximo virtual registrado por el kernel) | 760328 | 742,51 |
| `VmHWM` (máximo residente registrado por el kernel) | 105276 | 102,81 |

El predeterminado baja de 4000 a **1024 MiB**: 281,49 MiB de margen sobre el pico
virtual observado (37,9 %). La decisión usa `VmPeak`, porque `RLIMIT_AS` limita
espacio virtual. No extrapola el RSS histórico de otra versión de la suite.

Se usaron `PYTHONDONTWRITEBYTECODE=1` y un `PYTHONPYCACHEPREFIX` temporal vacío,
igual que en las ejecuciones frías del arnés. El muestreo lee un máximo acumulado
del kernel, pero podría perder asignaciones entre la última lectura y la salida.
La medición corresponde al proceso de la suite, no a la suma de sus descendientes
ni al consumo total del cgroup. Repetirla al cambiar Python, plataforma o suite.

Desde la raíz se puede reproducir con:

```bash
python3 tareas/20260917-011705-memoria/verificacion/medir_baseline.py
```

El script vuelve a escribir `baseline.log` y `baseline-memoria.json` en esa
carpeta. Los tests de `LimiteMemoriaTests` fijan 1024 MiB tanto para el perfil
como para el CLI y comprueban su propagación en bytes, además de mantener la
cobertura del valor explícito, la desactivación con cero y `RLIMIT_AS` real.
