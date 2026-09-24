# Revisión de Claude — 0.24.0 (el arnés le pone tope de memoria a cada mutante)

2026-09-16. Entrega de agy terminada a las 23:10, en el primer intento: leyó el encargo, escribió su
plan en [AVANCE-AGY.md](AVANCE-AGY.md), implementó y cerró con [INFORME-AGY.md](INFORME-AGY.md).

## Lo que se verificó

- El diseño es el del encargo: `resource.setrlimit(RLIMIT_AS)` aplicado **en el hijo** vía
  `preexec_fn`, el padre sin tocar, el tope propagado a la línea base y a cada mutante, y un mutante
  que excede contado como **muerto** —sale 1, que es «los tests lo detectaron»— y no como timeout ni
  error de arnés.
- `--limite-memoria-mb` con 4000 por omisión, `0` para desactivar, y la conversión a bytes en un solo
  lugar.
- Que el tope viaja en la identidad de la ronda: dos rondas con topes distintos no son la misma
  ronda al reanudar.
- Que `relaciones/corrida_mutacion.json` no necesitaba cambios: esa relación publica lo que la ronda
  MIDIÓ, no los parámetros con que se la invocó. Lo argumentó agy y es correcto.

## Defectos, corregidos por Claude

### R1. Los tests de la entrega no corrían

Siete de los diez fallaban al primer intento, contra una API que no existe: `ResultadoTests.murio`
(quien muere es el mutante; el resultado dice `tests_fallaron`), un conteo `muertos` en la corrida
(publica `tests_fallaron`), `_identidad_ronda(comando=…, codigos_fallo=…)` con parámetros por nombre
que esa función no tiene, un doble del informe al que le faltaban cuatro campos y la relación
`mutante_equivalente`, y una constante `LIMITE_MEMORIA_MB_PREDETERMINADO` que el informe declaraba y
que no llegó al archivo. Es el costo conocido de escribir tests sin poder correrlos —el mismo de
0.22.0— y es barato al lado de lo que sí quedó bien. Corregidos contra la API real; la constante se
escribió y la usa también la ayuda del comando.

### R2. La misma validación, escrita tres veces

`ejecutar_tests`, `_correr_en_raiz` y `correr` repetían las cinco líneas que validan el tope. Las tres
son puertas de entrada legítimas —la herramienta entra por `correr`, un test por `ejecutar_tests`—,
así que la validación tiene que estar en las tres; lo que no tiene que estar tres veces es la regla.
Queda en `_normalizar_limite_memoria`, al lado de la constante.

### R3. `preexec_fn` sin su nota

Es la única forma de ponerle un límite al hijo sin tocar el del arnés —`Popen` no tiene parámetro de
rlimits—, y la biblioteca estándar advierte que es peligroso con varios hilos. Acá no aplica: los dos
hilos lectores se crean DESPUÉS del `Popen`, y entre el fork y el exec no se toma ningún lock. Eso
ahora está escrito donde se lee el código, porque quien lo mire va a hacerse la misma pregunta.

## Lo que sólo se ve corriendo

- Una ronda real con el tope por omisión y **sin** `ulimit` externo: `nucleo/version.py`, 15 mutantes,
  15 muertos, 0 timeouts, 0 errores de arnés. El tope no rompe una ronda normal, que era el riesgo:
  `RLIMIT_AS` limita memoria **virtual**, y una suite que lanza subprocesos reserva más direcciones
  que páginas.
- El primer intento de esa ronda salió `LineaBaseFallida` por **timeout**, no por memoria: la corrí
  con `--timeout 120` y la suite con bytecode frío no entra. Queda anotado porque el diagnóstico
  dice «la línea base no fue verde (timeout, código None)» y es fácil leerlo como un fallo del tope.

## Test existente actualizado (propiedad de Claude)

- `test_la_politica_operativa_predeterminada_es_unica_y_explicita`: la política operativa se declara
  en un solo test y ahora incluye `LIMITE_MEMORIA_PREDETERMINADO`. agy lo dejó sin tocar por la regla
  de no editar tests existentes, y lo anotó en su informe, que es exactamente lo que había que hacer.
