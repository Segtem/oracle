# Implementación de 0.8.0: umbrales y fabricación de casos

**Fecha:** 2026-09-06. **Base:** corte 0.7.0, commit `f57b67f`.
Implementación y corte local verificados; sin commit ni publicación de 0.8.0.

## Lo reproducido

Se construyeron dos medidas de prueba, ambas con `de dato x` y `donde x.valor > 0`. Una resume
`contar(1)` con `<= 5`; la otra, `max(x.valor)` con `<= 10`. En las dos, el generador anterior
entregaba un candidato etiquetado `falso_verde` cuyo valor era 1 y cuyo veredicto era verde.
La evidencia de esta reproducción es construida, no una observación de un consumidor.

El estudio inicial exageraba el efecto externo: `evaluar_utilidad` ya descartaba la polaridad
incorrecta antes de escribir. El defecto era generar la propuesta contradictoria y ocultar el
motivo del descarte como falta de utilidad. No se comprobó que escribiera un `.caso` inválido.

## El primer cambio

`fabricar_candidatos` comprueba todos los veredictos antes de entregar candidatos. La heurística
anterior vive en `_proponer_candidatos`: una propuesta todavía no afirma que cumpla su etiqueta.

Para `contar` con cota superior, una fuente `de` y sólo filtros, repetir la evidencia escala el
conteo. Se calcula cuántas repeticiones superan el límite declarado: `<= 5` requiere seis filas
ofensoras y `< 5`, cinco. Se conservan las filas limpias y la multiplicidad de las bolsas, y se
comprueba el presupuesto antes de reservar la evidencia ampliada. Se vuelve a evaluar el resultado.

No se extrapola ese cálculo a un máximo, a una unión ni a una agrupación. Si la propuesta existente
ya produce la polaridad correcta, se acepta; si no, se informa `GeneracionNoPosible`. Una relación
requerida ausente tampoco se acepta como demostración de un defecto.

El comando primero comprueba si quedan mutantes por matar. Si la medida ya está fijada, conserva
la salida de «ruido» sin exigir una fabricación innecesaria. Si quedan mutantes y la fabricación
falla, devuelve código 1 con la medida, el umbral y el motivo, sin crear el directorio de salida.

Hay 22 pruebas del generador: bordes enteros y fraccionarios, magnitudes, agrupaciones, presupuesto,
ausencia de evidencia, rechazo sin escritura y lectura/evaluación de los archivos generados. El
caso de seis filas mata `convertir_conteo_en_existencia`, que era precisamente el camino ausente.
La mutación dirigida a la nueva función `fabricar_candidatos` cerró en **22/22 sitios muertos**,
sin tiempos agotados, errores de arnés ni equivalentes declarados. Ese número no mide el resto
del generador histórico ni todo el despacho del comando.

La primera entrega pasó 1280 tests y 180 casos. Los resultados de la integración completa se
registran al final de esta revisión.

## Los once sitios del inventario, revisados

| Sitio del estudio | Estado contra el corte 0.7.0 y este avance |
| --- | --- |
| 1. Premisa global en `nucleo/mutacion.py` | Ya corregida: el predicado recibe una medida, y la exclusión se decide por medida. |
| 2. Exclusión al importar mutadores ajenos | Ya corregida: el registro conserva todos los mutadores ofrecidos. Lo custodia `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`. |
| 3. `contar → suma(0)` | La acusación de bomba silenciosa no se sostiene como regla general. Con `contar >= 1`, una evidencia con una fila es verde y el mutante es rojo: el arnés registra una detección conductual. Además compara valores y testigos, no sólo polaridad. Un corpus compuesto únicamente por ausencia no demuestra presencia. Se conserva el mutador. |
| 4. `_direccion_monotona` sólo reconoce conteos y sumas de predicados | Limitación real de cobertura, declarada y pendiente. No basta agregar `max` o `min`: el cero de las relaciones vacías rompe la monotonía para ciertas magnitudes negativas. La ampliación necesita un contrato y casos que la distingan. Se conserva la procedencia del segundo autor. |
| 5. `vaciar_tuberia_si_cero_aprueba` | Correcto: consulta el comparador y el límite antes de asumir que cero aprueba. |
| 6. `convertir_conteo_en_existencia` | Disponible en el arnés; la exclusión local de cero ya no lo oculta para `<= 5`. La prueba nueva comprueba la divergencia con seis filas. |
| 7. Agregados vacíos que dan cero | Contrato del álgebra, no un defecto a corregir incidentalmente. Cambiarlo exige evaluar compatibilidad por §0. Sigue pendiente estudiar sus límites de dominio; esta entrega no cambia la semántica. |
| 8. Guarda `requiere` | Correcta: devuelve `sin_evidencia` sin consultar si el umbral aprobaría el cero. El comentario usa `<= 0` como ejemplo, no como condición ejecutable. |
| 9. Generación con una sola fila ofensora | Corregida para conteos simples de cota superior; los demás casos se aceptan sólo si su evaluación confirma la polaridad o se rechazan explícitamente. |
| 10. Plantilla basada en `ninguno` | Corregida: orienta hacia `oracle manual peor` para magnitudes y distingue tolerancia del dominio de conteo de defectos, sin elegir el contrato por el usuario. |
| 11. Test que excluía globalmente el mutador | Ya corregido: exige que esté en el registro y comprueba que aparece para `<= 5`. La cifra histórica de su comentario no define una restricción del arnés. |

## La medida propia de magnitud

El censo previo era **54 medidas base y 3 del perfil Python**, todas con umbral `<= 0`; ninguna
resumía con `max`. Ahora 53 medidas base conservan `<= 0` y una usa `max` con `<= 90`.

Se migró `meta.ninguna_sombra_envejece_sin_revisarse` a la macro existente `peor`, con tolerancia
90 días. El contrato ya existía; no se inventó una magnitud para ejercitar el lenguaje. Se conservan
el identificador, el ámbito universal, las polaridades y los testigos del corpus anterior. El valor
publicado sí cambia: ahora informa la edad del peor incumplimiento, no cuántas sombras incumplen.
Si no hay incumplimientos publica cero y ningún testigo, incluso si hay sombras recientes; no es
la edad máxima de todas las sombras. No corresponde `requiere`: no tener sombras es correcto.

Los casos 479 y 480 agregan edades distintas (91, 244 y 12 días) y la ausencia de sombras. La medida
cierra **9/9 mutantes**, sin sobrevivientes; las pruebas comparan también polaridad y testigos con
la formulación anterior. Los consumidores siguen verdes, con tres sombras cada uno.

## Custodia del generador

`tools/sondear_generador.py` ejecuta cinco sondas: conteos inclusivo, estricto y fraccionario;
una magnitud que exige negativa explícita; y la medida real de sombras. Publica 17 comprobaciones
de entrega, ambas polaridades y concordancia entre etiqueta y veredicto. Las expectativas se fijan
antes de ejecutar: negarse siempre, entregar una lista vacía o devolver sólo rojos no puede dar verde.
La medida existente `meta.el_caso_se_pone_como_debe` juzga esos hechos. No se agregó una relación,
una medida redundante ni un nodo del lenguaje. La sonda y su mutación completa corren en CI.

El caso 481 reproduce con evidencia construida la antigua contradicción. El 482 registra los 17
hechos de una ejecución real de la sonda: se observa el comportamiento del programa sobre entradas
construidas, no un dominio externo. Su evidencia coincide con la salida de `--hechos`. Al sustituir
el generador por la heurística anterior se obtienen cinco discordancias; al rechazar todo, cuatro.

La sonda tiene 11 tests y cierra **27/27 mutantes**, cero sobrevivientes, tiempos agotados, errores
de arnés o equivalentes declarados. La primera ronda encontró expectativas insuficientes sobre el
filtro y los argumentos; se agregaron entradas independientes y pruebas del uso real de `sys.argv`.
Se retiraron los constructos equivalentes de inserción e impresión JSON, en vez de declararlos.

Al ampliar la plantilla se detectó además un equivalente histórico de `tools/medida.py`: el valor
por defecto de `getattr` era imposible para `ErrorSintaxis`, que exige línea y columna. Se retiraron
ambos valores por defecto y la declaración obsoleta de `equivalentes.json`; las pruebas ahora usan
la excepción real. Los tres sitios de coordenadas modificados cierran **3/3** en mutación dirigida.
Este número no es una nueva medición completa de `tools/medida.py`.

## Verificación y límites

Suite final: **1295 tests OK**. Corpus: **184 casos**. Mutación de medidas: **902/902**, con 750 detecciones conductuales y 152
rechazos del álgebra. Aceptación de Oracle: la única medida meta roja conserva valor 2 y la línea
literal de CI `la_medida_no_se_fija_solo_con_evidencia_fabricada        2 (<= 0)`. Jam y LyraGASP
pasan con 23 y 26 casos. Los avisos de evidencia insuficiente al cruzar medidas de mutación de código
y de medidas siguen explícitos: esos informes no se certifican mutuamente si falta el campo esperado.

Las limitaciones de monotonía de `max`/`min`, agregados vacíos y fabricación general de magnitudes
quedan declaradas arriba; no se amplió su contrato incidentalmente. El corte sube distribución a
**0.8.0** y conserva álgebra **0.6** y sintaxis **0.2**, con argumento en §0: cambia una fórmula del
catálogo, no el evaluador ni el lector. Las notas advierten que el valor publicado de la medida
cambia de cantidad a días y no es comparable con la serie histórica sin distinguir el catálogo.
No se modificó el servidor MCP, ni se hizo commit, publicación o push de 0.8.0.

## Comprobación del corte

Se repitieron suite (1295), corpus (184), aceptación propia y de ambos consumidores, mutación de
medidas (902/902) y mutación completa de la sonda (27/27) con la distribución en 0.8.0. Cifras y
manual regenerados. Wheel y sdist construidos con `uvx --from build pyproject-build --wheel --sdist`:
sus 121 archivos de código y datos coinciden byte a byte con el árbol. Setuptools mantiene avisos
sobre directorios de datos no declarados como paquetes; el contenido sí está incluido.

La instalación limpia fuera del árbol ejecuta `oracle --version`, `oracle reportar --help`, las
17 comprobaciones de la sonda empaquetada y la medida de sombras (244 días y ausencia). El verificador
amplio de instalación también pasa: diez ejecutables, datos, espacio de nombres y motores aislados.

Se pidió revisión conceptual a Gemini mediante `ask-agy`: coincide con conservar álgebra y sintaxis
y advierte la discontinuidad de las series y el nuevo rechazo explícito. No verificó código; su
suposición de una salida previamente garantizada no aplica: antes el filtro de utilidad ya podía
descartar la propuesta. El cero sin sombras vencidas es el contrato explícito de `peor`, no una
edad máxima general. La revisión de código por OpenCode Go leyó los archivos pero agotó el límite
de cuatro minutos sin entregar conclusiones; no se cuenta como revisión aprobada.
