# Observar el propio Oracle costaba transcribir a mano

**2026-09-08 · corte 0.12.0**

## El pedido que venía quedando

De la sesión del debate sobre procedencia quedó anotado esto, y sobrevivió a cuatro cortes sin
moverse:

> **Lo que el debate dejó pedido, y sigue pendiente:** que observar sea *lo barato*. `observar.py`
> ya captura y revalida; falta conectarlo al trabajo cotidiano de los dos consumidores.

Y al lado, la deuda que lo explica: **94 casos observados que declaran `repo` y `commit` y nada
más.** Sitúan un árbol, no una corrida. La medida que los persigue lo dice sin vueltas: si un caso
no dice de dónde salió, la afirmación no sólo es inverificable —es **infalsable**, porque nadie sabe
adónde ir a contradecirla.

Los 94 no se pueden cerrar hacia atrás. El árbol contra el que corrieron ya no existe, así que
re-correr hoy da otros números y no prueba nada, y escribir el comando de memoria sería inventar
exactamente la procedencia que la medida existe para hacer visible. Lo único que se puede hacer es
que **los nuevos no nazcan así**.

## Por qué los nuevos nacían así igual

Porque para escribir un caso sobre el propio Oracle había que transcribirlo. Los casos `488` a `493`
de este mismo corte los escribí a mano: corrí la herramienta, miré la salida, copié las filas al
`.caso` y escribí el `comando` yo. Ese `comando` es una afirmación de memoria — la medida la acepta,
y su `alcance` dice explícitamente que no la verifica.

`observar.py capturar` existe justamente para eso y no se podía usar acá, porque le faltaba un
sensor: `aceptacion.py` no tenía forma de entregar su evidencia.

## Un verbo, no dos

`tools/aceptacion.py --hechos <ruta>` escribe la evidencia que la corrida construyó, tal cual se la
sirvió a las medidas.

Lo escribí primero mal, y el recorrido lo rechazó:

```
OBSERVACIÓN RECHAZADA — el sensor salió 1 y una corrida fallida no es una observación
```

Con razón: `aceptacion.py` sale 1 por DECISION-004, permanentemente. La tentación era aflojarle la
regla al recorrido —dejar que el plan declare un código de salida esperado—. Habría sido debilitar
una comprobación buena para que anduviera mi caso.

El error era otro, y era mío: **había mezclado dos verbos en una bandera.** Leer y juzgar son cosas
distintas, y este repositorio ya las separa en todos lados — `tools/sensores/*.py` lee y no importa
`unreal`; `tools/mide_*.py` juzga. Un sensor que devuelve el veredicto no se puede observar nunca, y
la consecuencia es peor que este caso: **`falso_verde` es la mitad del corpus, y un caso
`falso_verde` se escribe justamente sobre una corrida que falló.**

Así que con `--hechos` la salida dice si se **pudo leer**, no el veredicto. El veredicto se sigue
imprimiendo entero, y sigue siendo el que manda cuando nadie pide los hechos.

## El resultado

```
comando:            "{python} -B tools/aceptacion.py --hechos {salida}"
registro:           "observaciones/2026-09-08-aceptacion/registro.json"
evidencia_sha256:   "sha256:6a0629925f750c5318603fe9631c2d3c3a4a718ad03533a66b8bf37a55c6479a"
cuando_utc:         "2026-09-08T19:42:55…"
```

El caso `494` del corpus **no está escrito a mano**. Lo emitió el recorrido, y su `origen` no es una
afirmación de memoria: el comando es el que se ejecutó, el registro está al lado, y la huella
identifica la evidencia exacta que se leyó. Un caso transcrito dice que alguien observó; uno
capturado deja por dónde ir a contradecirlo.

La expectativa, además, estaba escrita en el plan **antes** de correr, y la juzga
`meta.el_caso_se_pone_como_debe`. Eso es lo que separa observar de racionalizar.

## Y el caso se escribe en la superficie

`observar.py` emitía el caso en JSON. Cada observación quedaba en el formato del que el proyecto se
estaba yendo desde el 2026-08-25 — o sea que observar barato costaba legibilidad, y el corpus se
llenaba de casos que nadie iba a leer con gusto.

Ahora emite `.caso`. Seis tests se cayeron con `FileNotFoundError` porque suponían la extensión;
ahora le preguntan al **registro** cómo se llamó el archivo, que además lo comprueba de paso.

## Lo que la mutación borró

Escribí una reserva: si la superficie no pudiera imprimir alguna forma, caer a JSON. La mutación
mostró que ningún test la ejercía, y buscando una forma que el impresor rechace no encontré ninguna.

Una reserva que nadie puede provocar es un constructo, y encima del peor tipo: **cambiar de formato
en silencio esconde que el impresor se rompió.** Se borró. Si algún día pasa, `capturar` falla en
voz alta, y la evidencia y el registro ya están escritos en el disco — se pierde una corrida, no la
observación.

Un equivalente genuino se borra, no se declara.

## Lo que sigue abierto

Esto cierra el camino para el **propio Oracle**. Los dos consumidores siguen igual: LyraGASP tiene un
plan y una observación capturada, de septiembre; Jam no tiene ninguno, y sus 23 casos `sin_declarar`
no se mueven por esto. Conectar el recorrido al trabajo cotidiano de los dos sigue pendiente, y para
los sensores que necesitan Unreal sigue haciendo falta abrir el editor.

Y los 94 siguen siendo 94. Lo que cambió es que ahora hay una **cota** que impide que sean 95.
