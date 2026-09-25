# Primer valor observable: Batalla Naval mínima

Este ejemplo demuestra el camino más corto para conectar un producto con Oracle:
desde una regla de dominio hasta juzgar una corrida real mediante hechos observables.

No usa medidas de proceso ni de sintaxis genérica: evalúa una regla concreta de la lógica del juego.

Los comandos se ejecutan desde la raíz del repositorio. La [guía completa](../../../../docs/13-primer-valor.md) registra el entorno, la preparación y la salida real de `oracle test`.

---

## 1. El producto y su regla

El producto es [`colocador.py`](colocador.py), un módulo que ubica buques en una cuadrícula de 10×10.

- **Regla del juego**: Ningún buque puede tener celdas fuera del tablero (las coordenadas `fila` y `columna` deben estar en el rango `0..9`).
- **El sensor**: El mismo producto expone una función o CLI (`--exportar <archivo>`) que emite la relación de nivel L0:
  `celda_ocupada(barco, fila, columna)`.

---

## 2. Estructura del proyecto

```text
ejemplo/primer-valor/
  oracle.json                                           ← catalogo_base: false (sólo evalúa reglas de este proyecto)
  colocador.py                                          ← producto con lógica de colocación y exportación de hechos
  catalogos/
    colocacion/
      colocacion.dentro_del_tablero.oracle              ← la regla enunciada en Oracle
  diferencial/.gitkeep                                ← directorio requerido; aún sin fixtures
  corpus/
    colocacion/
      001-desborde-tablero.caso                         ← caso negativo (falso_verde): espera ROJO
      002-colocacion-valida.caso                        ← caso positivo (verde_correcto): espera VERDE
      003-fila-negativa.caso                            ← fila -1
      004-columna-negativa.caso                         ← columna -1
      005-columna-desbordada.caso                       ← columna 10
      006-sin-celdas.caso                               ← relación vacía
```

---

## 3. La medida: enunciar lo que ofende

Archivo [`catalogos/colocacion/colocacion.dentro_del_tablero.oracle`](catalogos/colocacion/colocacion.dentro_del_tablero.oracle):

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

Notar tres principios fundamentales:
1. **Filtra lo que está mal**: el `donde` busca las casillas fuera de rango, no las válidas. El umbral exige `<= 0` casillas inválidas.
2. **`requiere` obligatorio**: evita un falso verde si la relación viniese vacía.
3. **`alcance` explícito**: declara abiertamente sus puntos ciegos (no comprueba superposición ni longitudes).

---

## 4. Fijar la medida con el corpus (`oracle test`)

Antes de juzgar el producto, comprobamos que la medida funcione y discrimine usando casos guardados en `corpus/`:

- [`001-desborde-tablero.caso`](corpus/colocacion/001-desborde-tablero.caso): declara una celda en `(10, 5)`. Como tiene `etiqueta: falso_verde`, la prueba exige que la medida dé **ROJO**. Además, al tener exactamente 1 celda ofensiva, mata el mutante `aflojar_umbral` (que prueba relajar a `<= 1`).
- [`002-colocacion-valida.caso`](corpus/colocacion/002-colocacion-valida.caso): declara 5 celdas legales en rango `0..9`. Con `etiqueta: verde_correcto`, la prueba exige que la medida dé **VERDE**. Esto mata el mutante `quitar_filtro` (que al contar todas las filas daría 5 > 0, haciendo fallar el caso).

El corpus agrega fila -1, columna -1, columna 10 y una relación vacía para fijar todos los predicados y `requiere`: seis casos, 20 mutantes muertos y ninguno vivo. `diferencial/.gitkeep` conserva el directorio obligatorio; no hay fixtures diferenciales y la CLI informa esa omisión.

Comando de verificación:

```bash
oracle test --proyecto ejemplo/primer-valor
```

> **¿Qué valida `oracle test`?** Valida la consistencia de las **medidas contra los casos guardados**. **NO ejecuta el juego ni certifica el código actual del producto**.

---

## 5. Medir una corrida real del producto (`oracle juzgar`)

Este es el paso donde Oracle juzga el producto vivo.

### Paso 5.1: Corrida con defecto (desborde)

Ejecutamos el producto simulando un colocador con bug que ubica un destructor en la fila 9 vertical (ocupando filas 9 y 10):

```bash
python3 ejemplo/primer-valor/colocador.py --defecto --exportar /tmp/hechos-defecto.json
oracle juzgar --proyecto ejemplo/primer-valor --con /tmp/hechos-defecto.json
```

**Salida real registrada (falla, exit 1):**

```text
✗ colocacion.dentro_del_tablero                       1 (<= 0)
      → c={'barco': 'destructor', 'fila': 10, 'columna': 5}

VEREDICTO: 1 de 1 medidas en rojo
```

Oracle señala exactamente la celda que violó el contrato: `fila: 10`.

### Paso 5.2: Corrida corregida

Ejecutamos el colocador con la validación de límites activa:

```bash
python3 ejemplo/primer-valor/colocador.py --exportar /tmp/hechos-corregido.json
oracle juzgar --proyecto ejemplo/primer-valor --con /tmp/hechos-corregido.json
```

**Salida real registrada (pasa, exit 0):**

```text
✓ colocacion.dentro_del_tablero                       0 (<= 0)

VEREDICTO: verde en 1 medidas. SIN MIRAR:
  · colocacion.dentro_del_tablero: valida que las celdas reportadas estén en el rango 0..9. NO ve si los buques tienen la longitud declarada ni si se solapan entre sí
```

El veredicto verde concluye recordando lo que **no miró**.

---

## 6. Diferencias clave

| Concepto | `oracle test` | `oracle juzgar` |
|---|---|---|
| **Qué evalúa** | El catálogo contra los casos guardados en `corpus/` | Hechos reales contra el catálogo del proyecto |
| **Cuándo se corre** | Al diseñar o modificar medidas y casos | Tras ejecutar el producto y extraer hechos |
| **Si cambiás el producto** | El resultado **no cambia** (el corpus es estático) | Cambia si regenerás el JSON de hechos |
| **Qué detecta** | Medidas flojas, mutantes vivos, inconsistencias | Defectos reales en la ejecución del producto |

### ¿Cuándo basta un `assert` y cuándo aporta Oracle?

- Un `assert 0 <= r < 10` dentro de `colocador.py` basta para un fallo temprano local en una función interna.
- Oracle aporta valor cuando:
  1. Necesitás auditar el resultado observable de un sistema sin acoplarte a cómo está implementado por dentro (caja negra).
  2. Un generador o LLM construye la solución: si el LLM escribe el test y el código con la misma mano, tenderá a ajustar el `assert` para que pase; con Oracle, las medidas y los casos exigen mutación cero y no se pueden aflojar sin romper el veredicto.
  3. Necesitás registrar explícitamente qué se garantizó y qué quedó como punto ciego (`alcance`).
