# Batalla Naval en HTML5 con Auditoría Formal

Juego táctico de **Batalla Naval (Battleship)** en HTML5/CSS3/JavaScript con verificación formal de reglas mediante **Oracle** (`oracle-metalenguaje`).

---

## 1. Cómo jugar

Podés abrir [`index.html`](index.html) directamente en cualquier navegador moderno:

```bash
# Podés abrirlo con xdg-open o con un servidor web local:
xdg-open index.html
# o
python3 -m http.server 8080
```

### Características del juego:
- **Tableros 10x10** reglamentarios (filas A–J, columnas 1–10).
- **Flota estándar de 5 navíos** (17 casillas en total):
  - Portaaviones (5 casillas)
  - Acorazado (4 casillas)
  - Crucero (3 casillas)
  - Submarino (3 casillas)
  - Destructor (2 casillas)
- **Fase de Despliegue**: colocación interactiva de buques, rotación horizontal/vertical con tecla `R` o botón, o botón **"🎲 Auto-Desplegar"** para despliegue rápido.
- **Fase de Batalla**: radar hostil interactivo con retícula táctica, efectos sonoros sintetizados proceduralmente vía **Web Audio API** (cañonazos, salpicaduras de agua, explosiones, sirenas navales), animaciones de impacto y bitácora cronológica de combate.
- **Inteligencia Artificial**: CPU con estrategia de Caza y Blanco (*Hunt & Target*) y búsqueda con paridad de tablero.
- **Panel de Auditoría integrado**: botón **"⚖ Auditoría & Traza Oracle"** para ver el estado de las reglas en vivo, inspeccionar el JSON de hechos relacionales y descargarlo para auditarlo en terminal.

---

## 2. ¿Cómo comprobamos que las reglas se cumplen de verdad?

Para no depender de afirmaciones de confianza ("funciona porque yo lo digo") ni de aserciones atrapadas dentro del mismo código que ejecuta el juego (que podrían compartir los mismos sesgos y errores lógicos), implementamos una **separación estricta entre ejecución y juicio**:

1. **El juego actúa como sensor fáctico puro**: Durante la partida no se valida a sí mismo; en cambio, emite una **traza relacional inmutable de hechos objetivos**:
   - `celda_barco`: qué casillas `(fila, columna)` ocupa cada buque de cada jugador.
   - `tiro`: la secuencia ordenada de disparos `(turno, tirador, receptor, fila, columna, es_impacto, hundio_barco)`.
   - `partida`: el resultado final `(estado, ganador, perdedor, turno_final, total_tiros, impactos_ganador, impactos_perdedor)`.
2. **Oracle actúa como juez formal externo**: Un catálogo declarativo de 11 medidas en lenguaje Oracle evalúa la evidencia relacional de forma independiente.

---

## 3. ¿Por qué usamos `oracle-metalenguaje`?

Elegimos usar `oracle-metalenguaje` por cuatro razones metodológicas fundamentales:

1. **Independencia del evaluador (Desacoplamiento)**:
   Si las pruebas se limitan a `assert` dentro de JavaScript, cualquier error conceptual en el diseño del modelo suele propagarse al verificador. Oracle corre fuera del runtime de JavaScript, evaluando únicamente la evidencia relacional sin conocer las estructuras de datos internas del juego.
2. **Declaratividad y álgebra relacional**:
   En vez de escribir bucles imperativos con estados mutables, las reglas se declaran mediante álgebra relacional pura (`de`, `unir`, `sin`, `donde`, `agrupar`, `resumen contar(1)`, `umbral <= 0`).
3. **Honestidad epistémica (`alcance` y `porque`)**:
   En Oracle cada medida declara explícitamente su justificación contractual (`porque`) y lo que **NO** mira (`alcance`). Un veredicto verde no oculta supuestos invisibles.
4. **Auditabilidad directa para el usuario**:
   Cualquier jugador puede descargar el archivo `hechos_partida.json` desde la interfaz web o desde el script y ejecutar directamente:
   ```bash
   oracle juzgar --con hechos_partida.json
   ```
   obteniendo un informe matemático con veredicto, umbrales y testigos.

---

## 4. Las 11 Reglas Formalizadas en el Catálogo

Las medidas se encuentran en el directorio [`catalogos/naval/`](catalogos/naval/):

| Medida | Qué verifica |
| :--- | :--- |
| `naval.tiros_dentro_del_tablero` | Ningún disparo tiene coordenadas fuera de $[0, 9] \times [0, 9]$. |
| `naval.tiros_sin_repeticion` | Ningún jugador dispara más de una vez a la misma casilla. |
| `naval.alternancia_turnos` | Los turnos consecutivos alternan estrictamente entre `jugador` y `cpu`. |
| `naval.turnos_sin_huecos` | La secuencia de turnos es monótona y continua desde $0$ hasta $N-1$ sin saltos ni pérdidas. |
| `naval.barcos_dentro_del_tablero` | Todas las casillas ocupadas por buques pertenecen a la cuadrícula de $10 \times 10$. |
| `naval.barcos_sin_solapamiento` | Dos buques del mismo bando no pueden compartir casillas. |
| `naval.flota_reglamentaria` | Cada bando cuenta con exactamente 17 casillas de barco ($5 + 4 + 3 + 3 + 2$). |
| `naval.veracidad_impacto_positivo` | Un disparo reportado como impacto debe tener un barco rival en esa coordenada (prohíbe impactos fantasma). |
| `naval.veracidad_impacto_negativo` | Un disparo en una celda donde hay un barco rival no puede ser reportado como agua (prohíbe impactos omitidos). |
| `naval.fin_de_juego_sin_tiros_posteriores` | No se registran disparos con turno posterior a la finalización de la partida. |
| `naval.ganador_legitimo` | El bando declarado ganador acumula exactamente 17 impactos (destrucción total de la flota rival). |

---

## 5. Demostración práctica y Falsabilidad

Para comprobar que el oráculo funciona y **no es complaciente** (es decir, que sabe ponerse en **ROJO** cuando se rompen las reglas), creamos el script [`verificar_oraculo.py`](verificar_oraculo.py):

```bash
python3 verificar_oraculo.py
```

El script realiza:
1. **Partida real guardada**: lee `partida_real.json` y ejecuta `oracle juzgar`, confirmando **VEREDICTO: verde en 11 medidas**.
2. **Inyección de infracciones (contraejemplos)**:
   - Inyecta un disparo duplicado $\rightarrow$ Atrapado por `naval.tiros_sin_repeticion` (ROJO).
   - Inyecta un disparo en fila 14 $\rightarrow$ Atrapado por `naval.tiros_dentro_del_tablero` (ROJO).
   - Inyecta un impacto fantasma en agua $\rightarrow$ Atrapado por `naval.veracidad_impacto_positivo` (ROJO).
   - Inyecta turnos consecutivos del mismo tirador $\rightarrow$ Atrapado por `naval.alternancia_turnos` (ROJO).

### Cómo juzgar cualquier partida manualmente:
```bash
oracle juzgar --con partida_real.json
```
Salida esperada:
```
✓ naval.alternancia_turnos                            0 (<= 0)
✓ naval.barcos_dentro_del_tablero                     0 (<= 0)
✓ naval.barcos_sin_solapamiento                       0 (<= 0)
✓ naval.fin_de_juego_sin_tiros_posteriores            0 (<= 0)
✓ naval.flota_reglamentaria                           0 (<= 0)
✓ naval.ganador_legitimo                              0 (<= 0)
✓ naval.tiros_dentro_del_tablero                      0 (<= 0)
✓ naval.tiros_sin_repeticion                          0 (<= 0)
✓ naval.turnos_sin_huecos                             0 (<= 0)
✓ naval.veracidad_impacto_negativo                    0 (<= 0)
✓ naval.veracidad_impacto_positivo                    0 (<= 0)

VEREDICTO: verde en 11 medidas.
```
