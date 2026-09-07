# El recorrido de observación: capturar una corrida y volver a revisarla

**Revisión:** 2026-09-07. **Estado:** herramienta nueva, medida; **sin corte de versión**.
Continúa `estudios/SENSOR-0.8.1-PRIMERA-CORRIDA.md`, que dejó un experimento local y propuso —sin
entregarla— la herramienta general. Esto es esa herramienta. **No agrega nada al lenguaje**: usa
`Referente`, `hechos_de_frescura` y dos medidas meta que ya existían.

## Qué se revisó del experimento anterior, y qué se encontró

El experimento (`registrar_corrida.py`, conservado en LyraGASP) hacía bien lo esencial: corría el
sensor dos veces, exigía que las dos lecturas coincidieran, leía referentes antes y después, los
juzgaba con la medida de frescura y **declaraba la expectativa antes de mirar el resultado**. Eso
se conservó entero.

Lo que no podía sobrevivir a la generalización, y por qué:

| Del experimento | Por qué no sirve como recorrido | Qué hace el recorrido |
| --- | --- | --- |
| `RAIZ = Path('/home/workstation/…')` y cinco rutas absolutas más | una observación con las rutas de una máquina adentro es un souvenir, no un procedimiento | el plan es **relativo a su raíz** y una ruta absoluta se **rechaza al leerlo** |
| `assert veredicto.valor == 37` | el número que dio una corrida es de esa corrida | `espera.valor` es **opcional**; el plan de un consumidor puede fijarlo, la herramienta no lo exige |
| `clips_esperados > 0` | «no vino vacío» escrito contra un campo de ese dominio | el plan declara **qué relaciones exige con filas**, y se cuentan con `separar_clave` |
| `evidencia['clip_ml_deformer'][1:]` | recorta el encabezado `clave` por posición: con una relación sin clave se come una fila real | `separar_clave` del álgebra, la misma función que usa `corpus.py` |
| `Path(fila[campo]).is_file()` | resuelve contra el *cwd* del proceso, no contra el proyecto. Funcionaba **sólo** porque ese sensor emite rutas absolutas; con rutas relativas habría dicho «no está» sin haber mirado | se resuelve contra `plan.raiz`, siempre |
| el caso emitido no pasaba por ningún verificador | un JSON parecido a un caso no es un caso | un test exige que `tools/corpus.py:verificar` lo acepte |

Ninguna de esas es una falla del experimento: era un experimento y lo decía. Son las cinco cosas
que cambian cuando lo mismo tiene que servirle a otro consumidor, en otra máquina, dentro de un año.

## Qué conserva el recorrido, y qué separa

`tools/observar.py` tiene dos verbos y **no importa el código del consumidor**: ejecuta su sensor
como otro proceso.

```bash
python tools/observar.py capturar  --plan <plan.json> --destino <carpeta>
python tools/observar.py revalidar --plan <plan.json> --registro <registro.json>
```

`capturar` corre el sensor dos veces, exige que las dos lecturas sean iguales y que las relaciones
declaradas traigan filas, compara los referentes de antes y después con
`meta.ninguna_evidencia_se_juzga_con_referente_vencido`, evalúa la medida y compara el resultado
contra la expectativa **declarada en el plan**. Recién entonces escribe tres archivos:
`evidencia.json` **byte a byte como salió del sensor**, `registro.json` y el caso, con
`procedencia: observada` y la evidencia incorporada íntegra.

La polaridad no se decide con un `if` de la herramienta: se arma el caso y se lo juzga con
`meta.el_caso_se_pone_como_debe`, la misma medida que usa la aceptación. Así la regla vive en un
solo lugar y la etiqueta no puede reescribirse con el resultado.

**Tres cosas que el registro no confunde**, y que el experimento ya había separado en prosa pero no
en datos:

- **observación histórica** — qué devolvió aquella corrida, con fecha. `revalidar` la lee y **nunca
  la corrige**; hay un test que compara los bytes de la carpeta antes y después.
- **frescura** — si los referentes declarados conservan hoy la misma huella. Es una comparación de
  declaraciones, y la hace una medida.
- **autenticidad** — **no se comprueba, y ninguna huella la comprueba**. Cada registro y cada
  informe llevan `autenticidad.comprobada: false` escrito, con el motivo. Dos controles del test lo
  fijan: huellas distintas dan **rojo 1**, y **dos declaraciones falsas iguales dan verde 0**.

Y separa lo reusable de lo local: `comando_declarado`, `plan.archivo`, `medida.archivo` y los
referentes van **relativos**; lo que sólo vale en esta máquina —la raíz absoluta, el intérprete, el
argv real— vive en un bloque `maquina` que `revalidar` **no** usa. El estado del árbol de git va en
`arbol_git`, con `versionado: false` explícito cuando la raíz no es un repositorio: no se atribuye
un commit que no existe.

## El plan, y por qué la expectativa va antes

Todo lo que el consumidor declara está en un JSON suyo: el comando (con `{salida}` una sola vez y
`{python}` opcional), los referentes, las relaciones que deben traer filas, la medida, la prosa del
caso con su etiqueta y —si quiere— el valor esperado. `presencia` es la generalización de la sexta
huella del experimento: deriva un referente **del propio resultado**, con las rutas que la evidencia
nombra y si son archivos. Alcance idéntico al de aquélla: **rutas y booleanos, no los bytes**.

Si la expectativa se dedujera del veredicto, el caso diría siempre lo que salió y no podría
discrepar nunca: el corpus se llenaría de casos que no pueden fallar. Acá una discordancia **detiene
la captura y no escribe nada**, y la lectura rechazada queda sin borrar para que alguien la mire.

## Medición

- **58 tests** propios. No repiten el camino feliz: rompen una cosa por vez —salida vacía, relación
  ausente, lectura inestable, referente que cambia durante la corrida, sensor que falla, sensor que
  sale 0 sin escribir, destino ocupado, etiqueta que no corresponde, valor declarado que no se
  reproduce, plan mal formado en treinta variantes— y exigen que el recorrido se plante.
- **Mutación de código: 146 mutantes, 146 muertos, 0 sobrevivientes** —medido después del arreglo de abajo—, sin timeouts, sin errores de arnés y **sin
  equivalentes declarados**. La primera ronda dio **44 sobrevivientes**: eran tests que faltaban, y
  se escribieron. Tres constructos sí eran equivalentes genuinos —`shutil.rmtree(…,
  ignore_errors=True)` sobre un temporal que siempre existe— y se **retiraron**, no se declararon.
- Un sobreviviente enseñó algo que vale anotar: el test del recorte de un error largo usaba 600
  caracteres contra un límite de 400, y **cualquier ventana grande contenía lo mismo**. Un test que
  ejecuta la rama no es un test que la fija. Con un error de exactamente 401 y una marca en el
  primer carácter, el borde queda custodiado.
- `tools/observar.py` entra a `HERRAMIENTAS_CUSTODIAS` y a la matriz de mutación de CI, con el
  criterio escrito: custodia que un caso `procedencia: observada` haya salido de una corrida, y
  **nadie más lo comprueba** —`corpus.py` valida la forma, `aceptacion.py` la polaridad—.

## Lo que encontró un ataque, y que la medición no había encontrado

Se le pidió a **codex** que atacara la promesa desde afuera: armar un consumidor de juguete y tratar
de conseguir un caso `procedencia: observada` barato. Corrió diez capturas y cuatro revalidaciones.
Seis ataques, y el resultado separa dos cosas que conviene no mezclar:

| Ataque | Resultado | Qué significa |
| --- | --- | --- |
| A. un «sensor» que no lee nada y escribe una evidencia inventada fija | **pasa** | límite **declarado**: la herramienta no puede saber si un programa leyó el mundo |
| B. un sensor real al que se le agregan filas inventadas | **pasa** | el mismo límite |
| C. `cp` de un JSON escrito a mano como «sensor» | **pasa** | el mismo límite |
| D. un sensor que devuelve `true` en una corrida y `1` en la otra | **pasaba** | **promesa incumplida** — arreglado |
| E. acomodar la etiqueta al resultado (omitirla, declarar una incompatible, reescribir el plan durante la corrida) | no pasa | la valida el plan y la juzga la medida meta |
| F. inyectar otra evidencia en `caso.evidencia` | no pasa | el caso conserva la que emitió el sensor |

A, B y C **no son defectos**: son exactamente el límite que la herramienta escribe en cada archivo
que produce. Ninguna huella distingue una corrida de una transcripción, y por eso los tres pasan
llevando `autenticidad.comprobada: false`.

**D sí era un defecto, y del que más importa.** El control de estabilidad comparaba las dos lecturas
ya parseadas, con `==` de Python — donde `True == 1` y `1 == 1.0`. Un sensor que emitía `true` en una
corrida y `1` en la otra pasaba el control: bytes distintos, tipo distinto, y la comparación decía
que no había cambiado nada. El caso salía como observación de un sensor que no se puede repetir.

Se reprodujo a mano antes de aceptarlo: dos corridas emitiendo `"revisado": true` y `"revisado": 1`
en un campo que la medida no mira, y una captura exitosa. Ahora la comparación es sobre la **forma
canónica** —valor y tipo— y no sobre los bytes: reordenar las claves de un objeto sigue sin ser un
cambio, porque no lo es, y además las dos corridas escriben en rutas distintas que un sensor podría
incluir en su salida. Dos tests nuevos fijan las dos caras.

**Lo que esto enseña sobre la medición:** 146 mutantes muertos no encontraron esto, y no podían.
La mutación pregunta «¿algún test nota si cambio esta línea?»; el ataque pregunta «¿qué puedo hacer
pasar?». El defecto no estaba en una línea que se pudiera mutar, sino en el **significado de `==`**
sobre datos parseados. Cero sobrevivientes no es cero defectos.

## La corrida sobre el consumidor real

Se corrió el recorrido contra el sensor de dataset de LyraGASP, **sin escribir una línea en su
árbol**: el plan y la observación quedaron fuera del repositorio, y su `git status` conserva
exactamente los mismos 47 renglones de antes.

El resultado reproduce el experimento anterior **byte a byte**:

| | experimento (2026-09-07 00:42 UTC) | recorrido (2026-09-07 10:25 UTC) |
| --- | --- | --- |
| evidencia | `sha256:1dda6ee0…`, 20 143 bytes | `sha256:1dda6ee0…`, 20 143 bytes |
| clips / FBX / ground truth | 37 / 37 / 0 | 37 / 37 / 0 |
| `ml_deformer.ground_truth_faltante` | rojo 37 | rojo 37 |
| referentes estables | 6 | 6, con las **mismas seis huellas** |

Las cinco huellas de fuentes coinciden diez horas después, y la sexta —la de presencia, que el
recorrido deriva por otro camino— da el mismo `sha256:15b5e33f…`. El `evidencia.json` que el
experimento dejó guardado coincide con la huella que su propio registro declara.

**Esto verifica la aritmética del turno anterior, no su autenticidad.** Que dos programas
independientes lleguen al mismo número dice que el dataset no cambió y que las dos cuentas están
bien hechas; no dice que alguna de las dos corridas haya ocurrido, porque eso no lo puede decir
ninguna huella.

El caso emitido por el recorrido pasa `tools/corpus.py` (CORPUS OK) y la aceptación lo pone
**ROJO con valor 37**, la etiqueta que el plan declaró antes de correr.

## El recorrido, instalado en el consumidor

Con autorización explícita, el plan y su observación quedaron dentro de LyraGASP. Se agregaron
**tres cosas**, y ninguna toca un archivo suyo existente:

- `medidas/observaciones/dataset-ml-deformer.plan.json` — el plan, con todo relativo a la raíz del
  proyecto (incluido `../_training/…`, que vive afuera y se declara como tal);
- `medidas/observaciones/2026-09-07-dataset/` — la observación: `evidencia.json`, `registro.json`,
  el caso y un `README.md` que explica cómo repetirla y qué no prueba;
- `medidas/corpus/ml_deformer/018-ground-truth-ausente-capturado-por-el-recorrido.json` — el caso,
  copiado tal cual salió.

Su corpus pasa con **28 casos** y la aceptación con **14 rojos y 14 verdes**, con el 018 en ROJO
valor 37. Las tres sombras siguen en **8 / 16 / 9**: el caso 018 mide la misma medida que el 017,
que ya estaba observada, así que no baja el pendiente de evidencia no observada. Su corpus pasa de
1 a **2 casos con `procedencia: observada`**; los otros 26 siguen sin declararla y **no se
reclasificaron**.

Revalidar la observación instalada sale «sin cambios» y deja los tres archivos con las mismas
huellas: `revalidar` lee el pasado, no lo reescribe.

## Lo que sigue sin estar hecho
- **No se autentica nada.** Sigue sin haber forma de distinguir una corrida de una transcripción, y
  el recorrido lo dice en cada archivo que escribe en vez de disimularlo.
- **No se abrió el editor.** Los sensores que necesitan Unreal siguen sin correrse, los 37 ground
  truth siguen ausentes y las sombras de unidades y origen de umbrales no se tocan: obtener
  archivos reales no declara unidades ni explica de dónde salió un número.
- **Sin corte.** Distribución 0.8.0, álgebra 0.6 y sintaxis 0.2 conservadas; las notas de release no
  se tocaron. Una herramienta nueva sube la distribución cuando alguien decida cortar, por §0.
