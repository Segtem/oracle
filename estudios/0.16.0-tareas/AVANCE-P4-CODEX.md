# P4 — uso propio, revisión y mutación del tracker

Actualizado el 2026-09-13. En curso; no es un cierre de 0.16.0.

## Uso propio

Oracle ya tiene tres registros reales en `tareas/`, derivados exclusivamente de los pendientes
vigentes de P4: mutación del tracker, uso propio y preparación del corte. La tarea de uso propio
`20260912-223233-uso-propio` está cerrada tras crear, anotar, buscar, encontrar referencias,
adjuntar una observación JSON y revisar el tracker. Las otras dos siguen abiertas.

La captura adjunta conserva el estado anterior a incorporarla: tres tareas, seis referencias
locales presentes, cero omisiones. Se volvieron a evaluar referencias y lectura después del
cierre, ambas en verde. La política de Git falló correctamente sobre los archivos nuevos sin
confirmar. No se migraron pendientes históricos cerrados ni material personal del dueño.

## Revisión con agy

Se retomó la conversación `da43a174-e2fb-4796-a4e1-9eed95f37150` en modo de sólo lectura,
sin shell ni ediciones. Terminó con código 0. El [informe](verificacion-p4/revision-agy.md)
identifica pasos incompletos del tutorial y una hipótesis sobre errores de Git.

Codex reprodujo cuatro defectos: el consumidor del ejemplo no importaba desde el checkout,
`hechos --git` filtraba ValueError con un core.worktree externo, se perdían saltos de línea
finales del nombre del repositorio y `hechos` emitía bytes no UTF-8 ante nombres Unix inválidos.
Se corrigieron y se añadieron diez tests de revisión. El conjunto P3/Git/revisión pasó 69 tests.
El wheel volvió a pasar fuera del checkout. El tutorial ahora crea un proyecto temporal,
usa el ID real y un adjunto de texto construido, y genera una mención que referencias puede hallar.

## Mutación

La primera ronda completa de Git midió 47 mutantes: 38 detectados y 9 sobrevivientes, sin timeouts
ni errores del motor. Se conserva en [verificacion-p4/mutacion-git-inicial](verificacion-p4/mutacion-git-inicial).
El script de coordinación tuvo un KeyError al calcular su código de salida después de guardar
los hechos y completar el manifiesto; se corrigió el cálculo. No se atribuye ese error a los tests.

Se añadieron tests de límite de espera, exclusión de directorios simbólicos sin Git, retiro del
índice, salida humana y código del despacho. Se quitaron argumentos predeterminados redundantes
de `os.walk` y del escape JSON, y la sangría opcional del JSON de seguimiento; los datos se conservan.
La protección de nombres Unix se fija mediante una prueba que exige JSON decodificable como UTF-8.

`medir_tracker.py` usa el motor existente, sin equivalentes y con timeout 120. Por defecto corre
la suite completa con prioridades. `--diagnostico` usa sólo los módulos propios para localizar
huecos más rápido: una ronda diagnóstica no se presenta como cierre de la verificación completa.
No se edita el árbol durante rondas. La repetición completa de Git terminó en **44/44**, sin
sobrevivientes, timeouts, errores de arnés ni equivalentes. Su evidencia histórica está en
[mutacion-git-final](verificacion-p4/mutacion-git-final); las dependencias cambiaron después.

Los diagnósticos iniciales de los otros módulos dieron:

| Módulo | Mutantes | Detectados | Sobrevivientes | Timeouts | Errores de arnés |
|---|---:|---:|---:|---:|---:|
| tareas | 320 | 162 | 156 | 1 | 1 |
| tareas_contexto | 254 | 111 | 143 | 0 | 0 |
| tareas_hechos | 312 | 182 | 127 | 3 | 0 |

No se cuentan los inconclusos como detecciones. Se retiró un generador de ID sin consumidores
del runtime: los tests ejercitan ahora la reserva real de carpetas. El despacho directo evita
ejecutar el CLI al importar. El lector de código inline usa rachas finitas de backticks completos;
se corrigió además la doble interpretación de `- URL: <https://...>`.

Cerrar, anotar y adjuntar comparten ahora la escritura atómica. Un fallo al conservar el modo
del documento aborta antes del reemplazo; adjuntar revierte su copia si falla el registro. Los
tests fijan bytes UTF-8/CRLF, modo POSIX, limpieza de temporales y fallos de stat/fsync/chmod/replace.
No se promete serialización de escritores concurrentes.

Agy aportó 24 tests directos de P1; dos colaboradores aportaron 27 de contexto y 22 de hechos.
Codex añadió cuatro de escritura atómica y ejecutó todas las pruebas: **230 tests del tracker**
y **1766 tests de la suite completa**, ambos conjuntos en verde. La afirmación de agy de menos
de 300 ms era una estimación sin ejecución propia; el registro válido es el comando de Codex
(68 tests de P1, revisión y escritura en 3,899 s). Falta repetir mutación sobre este árbol.


La versión permanece 0.15.0 / 0.6 / 0.4. No hubo commit, push ni publicación.

## Segunda ronda de tareas y correcciones posteriores

El diagnóstico r2 terminó con **274 sitios: 185 detectados, 89 sobrevivientes, cero timeouts y
cero errores de arnés**. La evidencia está en `verificacion-p4/diagnostico-r2-tareas/`.
Agy aportó después 49 tests de errores y despacho; Codex los ejecutó todos en verde. Los tests
exigen códigos precisos de salida y preservan los archivos ante fallos operacionales.

Codex añadió ocho pruebas de límites y recorrido. Se reproduce el documento mínimo sin línea
vacía tras el título, el rechazo de documentos vacíos y rutas rotas, y el agotamiento del
presupuesto de reservas. Listar, revisar y resolver prefijos traducen fallos de enumeración a
código 1. Adjuntar conserva el error de acceso al origen en lugar de llamar ausencia a un fallo
de permisos; 72 tests de contexto pasaron con la regresión incluida.

Simplificaciones con premisas: el alfabeto cerrado del ID ya excluye separadores y vacío;
`is_file` ya probó la existencia del destino central antes de resolverlo en un recorrido estable;
la creación exclusiva del README rechaza entradas preexistentes, incluidos enlaces rotos.
Se conserva su modo mediante constantes simbólicas POSIX. El registro interno Tarea no exige
congelación (ningún consumidor modifica sus atributos ni existe ese contrato público), y la
salida humana separa el cuerpo mediante una línea vacía sin imponer un ancho decorativo.
Estas correcciones todavía requieren una ronda sobre el árbol nuevo.

## Ronda completa r3 de tareas

La suite completa detectó **263/266** mutantes, sin timeouts ni errores de arnés. Los tres
sobrevivientes corresponden a dos huecos: inicializar con padres de proyecto ausentes y exigir
el retorno entero 0 de `ver --json`. Dos tests nuevos fijan ambos comportamientos. Se conserva
la ronda en `verificacion-p4/mutacion-r3-tareas/`; todavía no se declara cerrado P1 por mutación.

Además se reprodujo un falso negativo del extractor: una apertura de código escapada ocultaba
un enlace roto. Se corrigió distinguiendo apertura y cierre, incluidas rachas de varios backticks.
La referencia consultada es [CommonMark 0.31.2, escapes](https://spec.commonmark.org/0.31.2/#backslash-escapes):
fuera del código se escapa el primer carácter; dentro del código las barras son literales.
La extracción mantiene su gramática parcial. Pasaron 81 tests de límites y hechos con los casos
nuevos. La siguiente secuencia mide tareas con suite completa y diagnostica contexto y hechos.

## Secuencia r4/r2 y revisión posterior

La secuencia terminó sin inconclusos: tareas **266/266** con suite completa (191,464 s),
contexto **193/207** en diagnóstico (183,284 s) y hechos **231/246** en diagnóstico (391,053 s).
Se conservan las tres rondas y comandos en `verificacion-p4/secuencia-rondas.json`.
No hubo ediciones del árbol durante la secuencia; las correcciones se prepararon en copias aisladas.

La revisión adicional detectó separadores Unicode que partían títulos/metadatos o nombres de
adjuntos; posibles errores de rollback que ocultaban la causa inicial; referencias con NUL
codificado, barras codificadas y sufijos que exigen directorio; títulos Markdown capaces de
producir referencias falsas. Estas correcciones y los 29 sobrevivientes diagnósticos se están
integrando y verificando. La ronda 266/266 identifica el árbol anterior al ajuste de separadores
Unicode de P1; sus 125 tests pasaron en la copia aislada antes de integrarlo.

## Integración y custodia en CI

Las correcciones aisladas se integraron y pasaron **315 tests del tracker**. Se preservó el test
previo de permiso denegado al integrar el archivo de errores de contexto. El extractor acepta
títulos entre comillas simples/dobles y omite el resto de la línea si no puede localizar el cierre;
no afirma soporte completo de CommonMark. Las seis regresiones específicas del último análisis
fallaron contra el runtime anterior (16 fallos contando subtests), con log conservado.

Se declararon los cuatro módulos como custodias: integridad y escritura del registro; captura y
consultas con límites; seguimiento frente a Git; hechos y omisiones consumidos por políticas.
Se incorporaron sus perfiles y jobs a la matriz. Los 151 tests de herramientas pasaron, y las
cifras se regeneraron. La admisión preparada exige confirmar ahora sus rondas sobre el código
integrado; no se afirma haber ejecutado GitHub Actions. El estudio reutiliza los mismos perfiles
que CI para evitar mantener dos listas diferentes.

## Rondas oficiales del árbol integrado

El CLI oficial de mutación cerró tareas **263/263** (204,794 s), contexto **197/197** (177,609 s)
y Git **44/44** (172,027 s), con suite completa, cero sobrevivientes, cero timeouts, cero errores
de arnés y cero equivalentes. Cada ronda conserva sus fuentes y dependencias en el manifiesto.
El cambio posterior únicamente añade una prueba de títulos y adelanta gramática en el módulo
de tests del extractor, conservando todos los casos descubiertos y futuras clases.

El diagnóstico de hechos dio **255/258** (296,823 s); los tres vivos del helper de títulos están
cubiertos por esa nueva prueba. Los 79 tests de hechos pasaron en la copia aislada. Falta la
ronda oficial completa del extractor y la secuencia de cierre, incluido el paquete instalado.

## Cierre P4 — 2026-09-13

El extractor cerró su ronda oficial en **258/258** (258,140 s), sin inconclusos.
Los cuatro módulos suman **762/762**. La secuencia final pasó: **1852 tests**, corpus,
aceptación, mutación de medidas y políticas, wheel, sondas, traza y consumidor Jam.
El tutorial literal también pasó desde un wheel nuevo fuera del checkout.
P4 queda cerrado en [CIERRE-P4.md](CIERRE-P4.md), con resultados, límites y propuesta
de distribución 0.16.0. El dato de versión sigue en 0.15.0; no hubo commit, push ni publicación.
No queda agy trabajando en segundo plano.
