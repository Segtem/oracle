# Diagnóstico del corte en las corridas de mutación de la CLI (2026-08-28)

> Actualización: el corte operativo quedó superado y `tools/cli.py` ya tuvo dos corridas completas
> con manifiesto. La evidencia y los 64 sobrevivientes restantes están en
> `estudios/2026-08-28-cli-tanda-1.md`.

## 1. Desacople: Corte de corrida vs. Sobrevivientes observados

El problema observado en `estudios/2026-08-28-la-cli-sin-vigilar.md` mezcla dos fenómenos independientes que deben separarse formalmente:

1. **El corte abrupto de la corrida cerca del sitio ~120 sin resumen ni traza**: Su causa no quedó registrada. La hipótesis que mejor explica los tiempos es un **límite externo de ejecución** alcanzado por el costo acumulado de los mutantes que sobreviven y disparan suites pesadas y redundantes.
2. **La alta tasa de sobrevivientes (~57 % en `cli.py` y ~58 % en `medida.py`)**: Es un problema de **cobertura y discriminación de tests** en la interfaz de usuario (caminos de error, validación de argumentos, mensajes de ayuda y formato no fijados).

Modificar la lógica de la CLI o agregar tests a ciegas confundiría ambos problemas. La evidencia disponible explica la escala temporal del corte, pero no identifica al proceso externo que lo produjo.

---

## 2. Hipótesis explicativas ordenadas por evidencia

### Hipótesis 1 (la mejor respaldada, todavía no confirmada): límite externo cercano a una hora

- **Evidencia en el arnés de mutación (`tools/ejecutar_suite_mutacion.py:36-58`)**:
  El runner ejecuta primero los módulos prioritarios asignados en `tools/mutar_codigo.py:66-68` (`tests.test_cli` y `tests.test_herramientas`). Si el mutante muere, el proceso sale en el primer test discriminante. Si el mutante **sobrevive**, la suite prioritaria pasa entera y el arnés ejecuta **descubrimiento completo de unittest** (`ejecutar_suite_mutacion.py:48-57`).
- **Evidencia en la jerarquía de tests (`tests/test_cli.py:25, 429, 514`)**:
  Las clases `InitDejaLasGuardasPuestasTests` (línea 429) y `NounVerbCliTests` (línea 514) heredan de `OracleCliTests` (línea 25). Al no sobreescribir los tests base, **todos los tests de la clase base se ejecutan 3 veces** en una sola corrida de `tests.test_cli`.
- **Evidencia en el test de empaquetado (`tests/test_cli.py:314-366`)**:
  `test_wheel_instalado_trae_datos_y_ejecuta_oracle_test` compila un wheel (`pip wheel`), crea un virtualenv con pip (`venv.EnvBuilder(with_pip=True)`), instala el wheel y ejecuta múltiples invocaciones de `oracle`. La herencia anterior hace que ese trabajo se repita tres veces en `tests.test_cli`.
- **Costo medido el 2026-08-28 en este worktree**:
  - `python -m unittest tests.test_cli -q`: 61 tests, **18,247 s** de pared.
  - `python -m unittest tests.test_herramientas -q`: 85 tests, **2,755 s** de pared.
  - `python -m unittest discover -s tests -t . -q`: 703 tests, **29,628 s** de pared.
  - Un mutante que supera las prioridades cuesta por lo tanto alrededor de **50,630 s**, porque el descubrimiento completo vuelve a incluir esos módulos.
- **Correlación cuantitativa con las corridas observadas**:
  - `tools/corpus.py`: 51 sobrevivientes aportan por sí solos unos **43,0 min**, más el tiempo de los 72 que murieron; la corrida de 123 sitios completó.
  - `tools/cli.py`: los 68 sobrevivientes observados en los primeros 119 sitios aportan por sí solos unos **57,4 min**, más el tiempo de los que murieron.
  - `tools/medida.py`: los 67 sobrevivientes observados en los primeros 115 sitios aportan por sí solos unos **56,5 min**, más el tiempo de los que murieron.
  - Los dos cortes parciales son, por tanto, compatibles con un límite externo cercano a una hora. **No hay en el repositorio un log del supervisor, estado de salida o configuración que permita confirmar ese límite ni atribuirlo a una herramienta concreta.**
- **Evidencia del corte limpio sin traza (`perfiles/python/mutacion_codigo.py:707-727`)**:
  `_senales_de_ronda` captura `SIGTERM`, `SIGINT` y `SIGHUP` lanzando `SystemExit(128 + sig)`. Una terminación externa puede impedir que se alcancen las líneas de resumen en `tools/mutar_codigo.py:274-324`; el registro conservado no permite distinguir qué señal o mecanismo actuó.

---

### Hipótesis 2 (Secundaria): Invocación sin manifiesto ni partición persistente

- **Evidencia en `tools/mutar_codigo.py:145-148` y `perfiles/python/mutacion_codigo.py:936-960`**:
  El arnés soporta `--manifiesto <ruta>` y `--reanudar` para escritura atómica tras cada mutante. Sin esta bandera, el estado se conserva únicamente en memoria; al expirar el tiempo de pared, todo el progreso previo se pierde y la herramienta no puede imprimir el resumen final.

---

### Hipótesis 3 (menos consistente con lo observado): fallo interno del arnés o timeout individual

- **Evaluación en `perfiles/python/mutacion_codigo.py:464, 480-489`**:
  Si un mutante individual generara un bucle infinito o bloqueo en subprocesos (`tests/test_cli.py:331`), el arnés tiene un timeout por ejecución de 60 s (`TIMEOUT_PREDETERMINADO = 60.0`). Al vencer, `ejecutar_tests` clasifica el resultado como `EstadoTests.TIMEOUT` (`TIEMPO`) y el bucle principal (`perfiles/python/mutacion_codigo.py:797-837`) **continúa con el siguiente mutante**. No detiene la ejecución ni omite el resumen.
- **Evaluación de excepciones de aislamiento (`perfiles/python/mutacion_codigo.py:237-256`)**:
  Los errores previstos de `CacheNoLimpio`, `AislamientoRoto` u `OSError` imprimen `MUTACIÓN NO CONFIABLE — <Tipo>`. Esa marca no aparece en el registro conservado, aunque su ausencia no permite descartar toda falla no prevista.

---

## 3. Afirmaciones que NO se pueden comprobar sin repetir una corrida larga

1. **Comportamiento de los sitios restantes**: No se puede afirmar qué porcentaje de los sitios no alcanzados (sitios 120 a 328 en `tools/cli.py`, y sitios 116 a 225 en `tools/medida.py`) sobrevivirá o morirá sin evaluarlos.
2. **Ausencia de mutantes con timeout individual**: No se puede descartar con certeza absoluta que algún mutante posterior al sitio 120 introduzca un cuelgue real de 60 s en `pip` o `git` sin ejecutarlo.
3. **Tiempo total exacto de corrida completa sin optimizaciones**: Depende de cuántos sitios restantes sobrevivan y de dónde mueran los demás; no puede extrapolarse con precisión a partir de estas corridas parciales.

---

## 4. Experimento mínimo siguiente

Para verificar la hipótesis de persistencia y completar la evaluación sin riesgo de pérdida de progreso ante timeouts de pared, se debe usar `--manifiesto`:

```bash
python tools/mutar_codigo.py --objetivo tools/cli.py --manifiesto /tmp/progreso-cli.json > /tmp/mutacion-cli.log 2>&1
```

Si la corrida es interrumpida por tiempo de sesión, se reanuda inmediatamente conservando los sitios ya evaluados:

```bash
python tools/mutar_codigo.py --objetivo tools/cli.py --manifiesto /tmp/progreso-cli.json --reanudar > /tmp/mutacion-cli.log 2>&1
```

Antes de una corrida larga conviene separar el test caro de empaquetado de las clases heredadas. El ahorro exacto debe medirse después del cambio; este diagnóstico no lo implementa.

---

## 5. Tres tareas pequeñas para mirar sobrevivientes (sin casos imposibles)

Siguiendo la doctrina de no inventar entradas artificiales (`None`, `[]`) para sostener guardas redundantes:

1. **Persistir y terminar una sola partición**: correr `tools/cli.py` con `--manifiesto` y reanudarla ante un corte. Esto produce la lista exacta de vivos sin volver a perder una hora de evidencia.
2. **Clasificar una tanda pequeña de IDs vivos**: para cada ID, fijar una conducta observable real de la interfaz o demostrar que la guarda revalida un contrato ya garantizado y retirarla. No fabricar `None`, listas vacías ni árboles inválidos que la interfaz nunca entrega.
3. **Tratar equivalencias sólo después de ver el mutante exacto**: agregar un ID a `equivalentes.json` únicamente con una justificación verificable y volver a ejecutar ese sitio. No presumir que cambios de formato o rutas son equivalentes antes de observar su efecto contractual.
