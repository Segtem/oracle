# 13 · De un producto nuevo a su primera medida observable

Un recorrido breve, ejecutable y reproducible para conectar un producto con Oracle y juzgarlo con una medida pertinente de sus reglas, sin rituales innecesarios.

## Entorno y preparación verificados

Ejecutado el 2026-09-21 con Python 3.14.7 y Oracle 0.27.0 (álgebra 0.8, sintaxis 0.6), desde una copia sin `.git` del checkout base `3d27050a50cc949dc3fc6bf6dc9df168bf5f9ab5` más los cambios de esta tarea. Se construyó un wheel local y se instaló sin red en un venv nuevo; los comandos de abajo se ejecutaron desde la raíz de esa copia, sin `PYTHONPATH` ni `ORACLE_PROYECTO` heredados.

Para preparar otra copia del repositorio con este ejemplo, desde su raíz (el Python de construcción necesita `pip` y `setuptools>=68`):

```bash
python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir /tmp/oracle-primer-valor-ruedas .
python3 -m venv /tmp/oracle-primer-valor-venv
/tmp/oracle-primer-valor-venv/bin/python -m pip install --no-index /tmp/oracle-primer-valor-ruedas/oracle_metalenguaje-0.27.0-py3-none-any.whl
source /tmp/oracle-primer-valor-venv/bin/activate
unset PYTHONPATH ORACLE_PROYECTO
```

Las salidas siguientes son capturas reales. Cada exportación termina con exit 0 e imprime `Hechos exportados a /tmp/hechos-defecto.json` o `Hechos exportados a /tmp/hechos-corregido.json`, respectivamente. El test del catálogo termina con exit 0.

---

## 1. El objetivo de este recorrido

Cuando alguien se acerca a Oracle para medir un desarrollo —especialmente en iteraciones guiadas por agentes o LLMs— surgen con frecuencia dos confusiones habituales:

1. **Confundir la verificación de medidas con la certificación del producto.** Correr `oracle test` y ver una pantalla verde significa únicamente que el catálogo y el corpus son consistentes entre sí; no significa que el código fuente de la aplicación haya sido ejecutado ni que sus reglas de negocio funcionen.
2. **Confundir el tracker con el motor de medición.** El subsistema `oracle tarea` es un gestor documental local en Git. Es completamente optativo: no hace falta inicializar tareas ni escribir bitácoras para formular medidas sobre un producto.

Este documento presenta la **ruta mínima de primer valor**:
1. Elegir una regla concreta del producto.
2. Extraer hechos observables estructurados (nivel L0).
3. Escribir una medida y casos de ambas polaridades en el catálogo propio.
4. Validar el catálogo con `oracle test`.
5. Juzgar una corrida real del producto con `oracle juzgar`.

El ejemplo completo y reproducible se encuentra en el repositorio bajo [`ejemplo/primer-valor/`](../ejemplo/primer-valor/README.md).

---

## 2. Paso 1: Elegir una regla y extraer hechos

En el juego de Batalla Naval, una regla elemental de colocación establece:

> **Regla de colocación:** Toda celda ocupada por un barco debe ubicarse dentro de la cuadrícula de 10×10 (coordenadas de fila y columna entre 0 y 9).

### El sensor del producto

Oracle no inspecciona el DOM ni adivina el estado interno del juego: el producto debe emitir hechos observables estructurados en formato JSON (una tabla o relación de filas).

En nuestro ejemplo, el producto [`ejemplo/primer-valor/colocador.py`](../ejemplo/primer-valor/colocador.py) expone la opción `--exportar <archivo>` para volcar las celdas ocupadas por la flota:

```json
{
  "celda_ocupada": [
    {"barco": "fragata", "fila": 1, "columna": 2},
    {"barco": "fragata", "fila": 1, "columna": 3},
    {"barco": "fragata", "fila": 1, "columna": 4},
    {"barco": "destructor", "fila": 8, "columna": 5},
    {"barco": "destructor", "fila": 9, "columna": 5}
  ]
}
```

Cada hecho es un dato puro: no hay juicios de valor en el JSON, sólo hechos del mundo (nivel L0).

---

## 3. Paso 2: Crear el proyecto y enunciar la regla en una medida

Un proyecto Oracle se inicializa con `oracle init <directorio>` o creando `catalogos/`, `corpus/`, `diferencial/` y un archivo `oracle.json`:

```json
{
  "esquema": "oracle.proyecto/v1",
  "catalogo_base": false,
  "perfiles": []
}
```

> [!TIP]
> Si tu proyecto recién comienza y busca verificar reglas de negocio propias, podés fijar `"catalogo_base": false` para concentrarte exclusivamente en tus medidas de dominio sin evaluar políticas de proceso universales heredadas.

### La medida: `catalogos/colocacion/colocacion.dentro_del_tablero.oracle`

En Oracle, las medidas se enuncian buscando **lo que ofende** (el defecto), no lo que está bien:

```oracle
medida colocacion.dentro_del_tablero:
    de celda_ocupada c
    donde c.fila < 0 o c.fila > 9 o c.columna < 0 o c.columna > 9
    resumen contar(1)
    umbral <= 0 segun contrato porque "el tablero es de 10x10 (coordenadas 0 a 9); cualquier casilla fuera de ese rango corrompe el estado del juego"
    requiere celda_ocupada
    ambito universal
    alcance "valida que las celdas reportadas estén en el rango 0..9. NO ve si los buques tienen la longitud declarada ni si se solapan entre sí"
```

Los cuatro componentes esenciales:
- **`donde` (filtro)**: Selecciona únicamente las filas que violan la regla (`fila < 0 o fila > 9 ...`).
- **`umbral` con `segun`**: Exige `<= 0` violaciones y declara su origen (`contrato`) con la defensa que lo justifica.
- **`requiere`**: Exige la presencia de la relación `celda_ocupada` para evitar falsos verdes si el sensor devolviera una estructura vacía o errónea.
- **`alcance`**: Declara obligatoriamente el punto ciego de la medida (lo que **no** mira).

---

## 4. Paso 3: Fijar la medida con casos de ambas polaridades en el corpus

Una medida sin casos es una intención sin comprobar: podría estar invertida y pasar sin ser detectada. El corpus en `corpus/` necesita al menos dos casos:

### Caso 1: Polaridad negativa (`falso_verde` esperado ROJO)

Archivo [`corpus/colocacion/001-desborde-tablero.caso`](../ejemplo/primer-valor/corpus/colocacion/001-desborde-tablero.caso):

```caso
caso 001-desborde-tablero:
    fecha: "2026-09-21"
    origen:
        repo: "Segtem/oracle/ejemplo/primer-valor"
        commit: "sin-commit"
    procedencia: construida
    titulo: "Buque colocado parcialmente fuera del tablero (fila 10)"
    etiqueta: falso_verde
    sintoma:
        Un buque destructor colocado verticalmente en fila 9 desborda hacia la fila 10, fuera de la cuadrícula 10x10.
    como_se_detecto: persona
    medida: colocacion.dentro_del_tablero
    evidencia:
        celda_ocupada: barco, fila, columna
            "destructor", 9, 5
            "destructor", 10, 5
    leccion:
        La medida debe detectar la celda fuera de rango (10, 5) y ponerse en rojo para evitar desbordes de memoria o estado inválido.
```

- Este caso contiene exactamente 1 celda ofensiva (`fila: 10`).
- Falla la condición del umbral (`1 <= 0` es falso), por lo que la medida se pone en **ROJO**.
- Como declara `etiqueta: falso_verde`, la suite de aceptación confirma que la medida atrapó el defecto.
- Mata el mutante `aflojar_umbral` (que probaría relajar el umbral a `<= 1`).

### Caso 2: Polaridad positiva (`verde_correcto` esperado VERDE)

Archivo [`corpus/colocacion/002-colocacion-valida.caso`](../ejemplo/primer-valor/corpus/colocacion/002-colocacion-valida.caso):

```caso
caso 002-colocacion-valida:
    fecha: "2026-09-21"
    origen:
        repo: "Segtem/oracle/ejemplo/primer-valor"
        commit: "sin-commit"
    procedencia: construida
    titulo: "Flota colocada enteramente dentro de la cuadrícula 10x10"
    etiqueta: verde_correcto
    sintoma:
        Despliegue reglamentario de buques con todas sus celdas dentro del rango válido de 0 a 9.
    como_se_detecto: persona
    medida: colocacion.dentro_del_tablero
    evidencia:
        celda_ocupada: barco, fila, columna
            "fragata", 1, 2
            "fragata", 1, 3
            "fragata", 1, 4
            "destructor", 8, 5
            "destructor", 9, 5
    leccion:
        Una colocación reglamentaria debe dar 0 testigos ofensivos y resultar verde; fija la medida contra mutaciones que eliminen el filtro.
```

- Este caso contiene 5 celdas legítimas.
- La medida obtiene valor 0, resultando en **VERDE**.
- Mata el mutante `quitar_filtro` (que al suprimir el filtro contaría las 5 celdas y daría 5 > 0, disparando un falso rojo).

---

### Casos adicionales necesarios

Los dos casos anteriores no alcanzan: dejaban seis mutantes vivos. El corpus incluye también fila -1, columna -1, columna 10 y una relación vacía (`celda_ocupada:` sin filas). Este último queda ROJO aunque el valor sea 0 porque incumple `requiere`. Los seis casos son construidos; `sin-commit` evita atribuirles un commit ficticio.

El directorio obligatorio `diferencial/` se conserva con `.gitkeep`. No contiene fixtures: esta ruta mínima no aporta una comparación con un evaluador independiente y `oracle test` lo informa como salteado.

## 5. Paso 4: Validar el catálogo con `oracle test`

Corremos `oracle test` para verificar que las medidas del catálogo compilen, satisfagan los contratos sintácticos y queden fijadas contra mutación:

```bash
oracle test --proyecto ejemplo/primer-valor
```

### Salida real registrada de `oracle test`:

```text
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 6 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 6 casos

catálogo: 1 medidas · corpus: 6 casos

  ROJO  001-desborde-tablero                   colocacion.dentro_del_tablero  (valor 1)
  verde 002-colocacion-valida                  colocacion.dentro_del_tablero  (valor 0)
  ROJO  003-fila-negativa                      colocacion.dentro_del_tablero  (valor 1)
  ROJO  004-columna-negativa                   colocacion.dentro_del_tablero  (valor 1)
  ROJO  005-columna-desbordada                 colocacion.dentro_del_tablero  (valor 1)
  ROJO  006-sin-celdas                         colocacion.dentro_del_tablero  (valor 0)

defectos que se pusieron rojos: 5 · verdes correctos: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 5 defectos en rojo, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 20 · murieron 20 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver DECISION-011)
  de los muertos: 20 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 120

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```

> [!IMPORTANT]
> Este veredicto verde indica que **el catálogo satisface las verificaciones aplicables y los casos presentes**. No certifica en absoluto el estado del código del juego en este momento.

---

## 6. Paso 5: Juzgar una corrida real con `oracle juzgar`

Ahora sí conectamos el producto vivo con Oracle.

### Escenario A: Corrida con defecto

El colocador tiene un bug y posiciona un destructor en la fila 9 vertical, desbordando hacia la fila 10:

```bash
# 1. Ejecutar el producto y extraer hechos reales
python3 ejemplo/primer-valor/colocador.py --defecto --exportar /tmp/hechos-defecto.json

# 2. Juzgar los hechos contra el catálogo
oracle juzgar --proyecto ejemplo/primer-valor --con /tmp/hechos-defecto.json
```

**Salida real registrada (exit code 1):**

```text
✗ colocacion.dentro_del_tablero                       1 (<= 0)
      → c={'barco': 'destructor', 'fila': 10, 'columna': 5}

VEREDICTO: 1 de 1 medidas en rojo
```

Oracle rechaza la corrida y señala exactamente el testigo infractor: `fila: 10`.

### Escenario B: Corrida corregida

Arreglamos el defecto en el producto (el destructor se ubica en la fila 8 vertical, ocupando filas 8 y 9):

```bash
# 1. Regenerar los hechos tras la corrección
python3 ejemplo/primer-valor/colocador.py --exportar /tmp/hechos-corregido.json

# 2. Juzgar los nuevos hechos
oracle juzgar --proyecto ejemplo/primer-valor --con /tmp/hechos-corregido.json
```

**Salida real registrada (exit code 0):**

```text
✓ colocacion.dentro_del_tablero                       0 (<= 0)

VEREDICTO: verde en 1 medidas. SIN MIRAR:
  · colocacion.dentro_del_tablero: valida que las celdas reportadas estén en el rango 0..9. NO ve si los buques tienen la longitud declarada ni si se solapan entre sí
```

La corrida pasa limpiamente y el reporte final imprime de forma transparente el alcance declarado: qué fue lo que **no se miró**.

---

## 7. Clarificaciones fundamentales

### Evidencia guardada vs. Evidencia regenerada

- Los archivos en `corpus/` (`001-desborde-tablero.caso`, etc.) son **evidencia histórica guardada** para comprobar las medidas. Si editás el producto, estos archivos no cambian ni deben cambiar automáticamente.
- Los archivos generados por el sensor (`/tmp/hechos-*.json`) son **evidencia viva de una corrida particular**. Si modificás el producto, debés volver a ejecutar el sensor para generar un nuevo archivo de hechos antes de invocar `oracle juzgar`.

### ¿Cuándo basta un `assert` y cuándo aporta Oracle?

- **Basta un `assert`** cuando estás programando una comprobación interna rápida en una función (`assert 0 <= fila < 10`), o en una prueba unitaria clásica donde el mismo desarrollador escribe el código y el test.
- **Aporta Oracle** cuando:
  1. **Hay riesgo de Goodhart:** Quien escribe el código (por ejemplo, un LLM o agente) tiende a adaptar el test para que dé verde; en Oracle las medidas están desacopladas y custodiadas por mutación obligatoria.
  2. **Se necesita explicitar el punto ciego:** Un `assert` que pasa produce silencio; una medida de Oracle que pasa concluye enumerando su `alcance` (lo que no puede garantizar).
  3. **Auditoría de artefactos en caja negra:** Querés evaluar la validez de los datos producidos por un proceso sin acoplarte a cómo está implementado el generador por dentro.

### El tracker es una herramienta independiente

La gestión de tareas (`oracle tarea init`, `oracle tarea nueva`, etc.) no es un requisito previo para usar medidas ni para juzgar hechos. Podés medir cualquier producto sin inicializar `tareas/`.

El tutorial completo es una opción para profundizar; el tracker y ese tutorial son independientes de este recorrido.
