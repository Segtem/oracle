# Relevo — 2026-09-07

## Para Claude: empezar acá

**Corte 0.8.1 hecho, commiteado y empujado, con autorización explícita del usuario.** El árbol
declara distribución `0.8.1`, álgebra `0.6` y sintaxis `0.2`; el argumento está en
`ESPECIFICACION.md` §0 y las notas en `NOTAS-DE-RELEASE.md`.

Los tres trabajos que estaban sin commitear —el corte 0.8.0, el experimento del sensor y el
recorrido reusable— entraron en **un solo commit** sobre `f57b67f`, y conviene saber por qué: los
archivos compartidos (`nucleo/version.py`, `ESPECIFICACION.md` §0, `NOTAS-DE-RELEASE.md`,
`README.md`, la matriz de CI y `tools/mutar_codigo.py`) mezclan las tres tandas **en los mismos
hunks**. Partirlo en tres habría exigido inventar contenidos intermedios que nunca existieron, y
dos de esos commits no habrían pasado su propia suite. El mensaje del commit enumera las tres
tandas y el `git status` de cada una está descrito abajo.

**Las releases de GitHub quedaron al día el 2026-09-07**, con autorización del usuario:
`v0.7.0` sobre `f57b67f` y `v0.8.1` sobre `efb8df2`, las dos con tag anotado y el cuerpo tomado de
`NOTAS-DE-RELEASE.md`. **0.8.1 es Latest.**

**No hay `v0.8.0` y no puede haberla:** ningún árbol del repositorio declara
`VERSION_DISTRIBUCION = "0.8.0"` —`f57b67f` dice `0.7.0` y `b2f9935` ya dice `0.8.1`—, así que un
tag `v0.8.0` apuntaría a un árbol que dice otra cosa. Se decidió no crearlo y meter la sección
entera de 0.8.0 dentro del cuerpo de `v0.8.1`, precedida por un bloque que lo explica. Las notas
del repositorio conservan las dos secciones separadas, como estaban.

**PyPI: `0.8.1` publicada el 2026-09-07 por el usuario, y verificada.** Los dos digests que
sirve PyPI coinciden **bit a bit** con el build local de `dist/` (`whl ba790bb7…`,
`tar.gz 77747958…`). Instalada en un venv limpio bajando **desde PyPI**, no desde el archivo:
`oracle 0.8.1`, álgebra `0.6`, sintaxis `0.2`, los diez ejecutables presentes, y
`python -m oracle_metalenguaje.tools.observar capturar` corrió de punta a punta contra el plan y el
sensor reales de LyraGASP dando la misma evidencia `sha256:1dda6ee0…` que el árbol y que la
observación conservada en ese repositorio.

PyPI **saltó de `0.6.0` a `0.8.1`**: `0.7.0` y `0.8.0` nunca se subieron y ya no se van a subir.
Es coherente con GitHub, donde tampoco hay `v0.8.0`; `v0.7.0` sí tiene release y tag.

### Corte 0.9.2: Oracle imprimía algo que no podía volver a leer

**Commiteado, sin push y sin publicar en PyPI.** Distribución `0.9.2`, álgebra `0.6`, **sintaxis
`0.3`** — la primera vez que la superficie se mueve desde que ganó la cláusula `ambito`. Detalle en
[`estudios/LA-AUSENCIA-VISIBLE-NO-SE-PODIA-ESCRIBIR.md`](estudios/LA-AUSENCIA-VISIBLE-NO-SE-PODIA-ESCRIBIR.md).

El impresor emitía `segun sin_declarar` en una invocación de macro —los argumentos son posicionales
y no se pueden omitir— y el lector lo rechazaba. `meta.sintaxis_ida_y_vuelta` no lo veía porque el
catálogo propio no tiene ninguna medida con esos campos sin declarar.

**No afloja nada, y está medido:** un valor inventado se sigue rechazando, y las tres sombras del
consumidor que lo destapó quedaron en los mismos **9 / 54 / 41**.

**Números:** suite **1400** · corpus **188** (casos 485 y 486 nuevos) · medidas **915/915** ·
`nucleo/sintaxis.py` **993/993 sin sobrevivientes** · las cuatro comprobaciones de CI en verde ·
artefactos con 121 archivos byte a byte contra el árbol.

```
whl    sha256:2b96ba60a697fb3b858067603f516c56fa87b02ef240d2e8734ac95bb4c192b3
tar.gz sha256:35a6aae5d67daa9e12f19a9cbd196e56f9e3d9016e8758600056c36a2964b9a0
```

**Jam quedó migrado en su árbol, sin commitear:** sus 33 medidas pasaron a la aridad vigente con las
79 formas canónicas idénticas (huella `83f04f33d6b0282e`), y `oracle test` le dice
`SINTAXIS OK · 41 medidas`. Se commitea allá cuando 0.9.2 esté publicada.

### Los 11 sobrevivientes que 0.10.0 destapó ya están cerrados

Los dos consumidores pasaron a **VEREDICTO VERDE por primera vez**, y la deuda que 0.10.0 hizo
visible se cerró el mismo día:

| | mutantes | sobrevivientes | tests propios |
|---|---|---|---|
| Jam (`84ce326`) | 428 | **0** (eran 9) | 1240 OK |
| LyraGASP (`85d68af9`) | 139 | **0** (eran 2) | 33 OK |

Los dos empujados. Nueve mutantes de Jam se cerraron con **ocho** casos: el del volumen orientado
cero mata dos, porque el cero cae en la franja de las dos mutaciones a la vez.

**Todos son `construida`, y hubo debate.** La discusión está en
[`estudios/OBSERVAR-O-CONSTRUIR-EL-BORDE.md`](estudios/OBSERVAR-O-CONSTRUIR-EL-BORDE.md), con las
dos posiciones defendidas en serio por los dos agentes y lo que cada una concedió. Lo que decidió:
un caso de borde interroga a la frontera de la regla, no al mundo.

⚠ **El precio es visible: la sombra de evidencia fabricada de Jam SUBIÓ de 9 a 16.** Siete medidas
que no tenían ningún caso ahora lo tienen, y es construido. Cerrar la deuda de mutación hizo
visible una deuda de procedencia en vez de taparla, que es como tiene que ser.

**Deuda declarada:** el caso `018` de Jam necesita `aristas_sueltas == 1`, que ninguna malla bien
formada produce —búsqueda exhaustiva: los valores alcanzables son 0, 3, 4, 5…— y que sólo da un
triángulo degenerado. Se buscó en toda la evidencia guardada y sólo aparecen 0 y 3. Es un defecto
real y frecuente; verlo exige abrir el editor.

**Lo que el debate dejó pedido, y sigue pendiente:** que observar sea *lo barato*. `observar.py` ya
captura y revalida; falta conectarlo al trabajo cotidiano de los dos consumidores y a los
adaptadores que necesitan Unreal.

### Corte 0.10.0: el paquete medía con 5 de 29 mutadores

**PyPI: `0.10.0` publicada y verificada el 2026-09-07.** Digests y tamaños idénticos al build
local. La herramienta global quedó reinstalada y ya mide con los 29 mutadores: Jam pasa de 315/0 a
**428 con sus 9 sobrevivientes** y LyraGASP de 116/0 a **139 con sus 2**.

⚠ **`uv tool install --force` NO alcanza: hace falta `--refresh`.** Sin él falla con «no version of
oracle-metalenguaje==0.10.0 … requirements are unsatisfiable» aunque PyPI ya la sirva, porque `uv`
resuelve contra su caché. El comando completo es:

```bash
uv tool install --force --refresh "oracle-metalenguaje==<version>"
```

**Commiteado, sin push y sin publicar en PyPI.** Distribución `0.10.0`, álgebra `0.6`, sintaxis
`0.3`. Detalle en
[`estudios/EL-PAQUETE-MEDIA-CON-CINCO-DE-VEINTINUEVE.md`](estudios/EL-PAQUETE-MEDIA-CON-CINCO-DE-VEINTINUEVE.md).

`mutadores/` no estaba en `pyproject.toml` y nunca viajó: una instalación mutaba con los 5 propios
en vez de los 29 declarados, sin decirlo. Medido sobre los dos consumidores reales, el mismo comando
sobre el mismo proyecto:

| | desde el paquete | desde el árbol |
|---|---|---|
| Jam | 315 mutantes · **0** sobrevivientes | 428 · **9** |
| LyraGASP | 116 mutantes · **0** sobrevivientes | 139 · **2** |

Los sobrevivientes reales de los dos salen de mutadores del segundo autor, o sea invisibles desde el
paquete. Es el defecto que `DECISION-011` fue a arreglar, sobreviviendo en lo que se distribuye.

**Arreglado en dos partes:** `mutadores/` viaja como `oracle_metalenguaje.mutadores` —no de nivel
superior, que repetiría el defecto de `tools` que 0.3.3 arregló— y el informe declara el
denominador, que es lo que sirve en una instalación anterior, donde empaquetar no llega.

**Sube la MENOR y no el parche**, y es el caso más claro del criterio: los dos consumidores pasan de
VERDE a ROJO al actualizar sin tocar una línea. Se escribió primero `0.9.3` con el argumento de que
la exigencia ya existía; eso explica por qué corresponde hacerlo, no por qué podría esconderse en un
parche.

⚠ **Los números de mutación reportados sobre los consumidores antes de este corte** salieron del
Oracle instalado: ciertos, pero sobre un espacio 5,8 veces más chico. Conviene leerlos con este dato
al lado.

**Números:** suite **1405** · corpus **189** (caso 487, resuelto por construcción) · medidas
**915/915** · las cuatro comprobaciones de CI en verde · artefactos con **123 archivos byte a byte**
contra el árbol · desde un venv limpio, los dos consumidores ven los mismos números que el árbol.

```
whl    sha256:2922c151968f65aad0b2376910ba999534f56a9a47a857b86d7f6d05838b8adc
tar.gz sha256:378310a7823386c06373132815f3c99b775c65702c1d40ca140bd55ae04ed01c
```

**Jam sigue migrado y sin commitear**, esperando que 0.10.0 esté publicada. Y ahora tiene un rojo
real que ver: sus **9 sobrevivientes**, que hasta hoy no podía medir.

### Corte 0.9.1: una herramienta que se cae no informa nada

**Commiteado (`e7ec9b2`), empujado, con tag anotado `v0.9.1` y release en GitHub como Latest. Sin
publicar en PyPI.** Distribución `0.9.1`, álgebra `0.6`, sintaxis `0.2`. `oracle test` informaba **nada** y moría con un traceback cuando el impresor no podía
procesar un archivo del consumidor; ahora lo informa con nombre y motivo, y las etapas siguientes se
ejecutan. Detalle en
[`estudios/UNA-HERRAMIENTA-QUE-SE-CAE-NO-INFORMA.md`](estudios/UNA-HERRAMIENTA-QUE-SE-CAE-NO-INFORMA.md).

No es una regresión: se reproduce idéntico con 0.5.0, 0.8.1 y 0.9.0 en entornos limpios. Venía
pasando desde al menos cuatro versiones sobre el comando que el `AGENTS.md` de Jam manda correr.

**Parche y no menor**, revisado con `agy` contra la regla escrita: nadie cambia de color. Un
proyecto sano seguía y sigue en verde; uno con un archivo ilegible ya salía distinto de cero, por
la excepción. Lo que cambia es qué se puede leer cuando ya estaba rojo.

**Números, y `codex` los midió aparte:** suite **1394** · corpus **186** · mutación de medidas
**915/915** · mutación de `tools/cli.py` **500/500** · aceptación con un rojo que tumba y uno en
sombra, las cuatro comprobaciones de CI en verde · Jam ✓ 20/3 y LyraGASP ✓ 14/14 ·
`verificar_instalacion.py` WHEEL OK. Artefactos en `dist/`, **121 archivos byte a byte** contra el
árbol.

```
whl    sha256:2bd47314aef9d0194c6d4e05040e887ef3d4eaea978882cd6e2a27992f238321
tar.gz sha256:fd2e11a1b047025211412bc4cb3259e8d9caccb822c7fbcfe16e500bb5c92c87
```

**`tools/sintaxis.py` se midió y NO entró al perfil de mutación:** 95 mutantes, 52 muertos, **42
sobrevivientes**, 1 error de arnés, 2353 s. Los 42 son deuda previa —30 en `main()` y **cero** en
el código nuevo—, así que meterlo pondría al proyecto en rojo por algo ajeno. Queda en
`PRIORIDADES` con el número escrito, como se hizo con `aceptacion.py`.

**Dos cosas que este corte NO arregla y conviene no perder:** las 33 medidas de Jam con aridad vieja
de `ninguno`, `peor` y `ninguno-par` —son de ese repositorio—, y los 9 mutantes sobrevivientes de
428 que `codex` encontró en la mutación de Jam, también previos.

**PyPI: `0.9.1` publicada el 2026-09-07 por el usuario, y verificada.** Los dos digests y los dos
tamaños que sirve PyPI coinciden con el build local y con los que este relevo tenía anotados antes
de la subida. Instalada en un venv limpio bajando desde PyPI: `oracle 0.9.1`, los diez ejecutables,
y `oracle test` sobre Jam informa los 33 archivos con **cero tracebacks**, ejecutando aceptación y
diferencial.

**El arreglo llegó a los tres lugares donde vive Oracle en esta máquina**, que era el riesgo
concreto de este corte:

| dónde | antes | ahora |
|---|---|---|
| paquete de PyPI | 0.9.0 | **0.9.1** |
| herramienta global del PATH (`uv tool`) | 0.9.0, **crasheaba** | 0.9.1, informa |
| wheel vendorizado de Jam (`vendor/oracle-pkg`) | 0.9.0 | **0.9.1** |

El antes/después de la herramienta global se midió en la misma máquina y con el mismo comando:
**1 traceback → 0**. Jam quedó commiteado y empujado en `dfe3529`, con el número movido en los tres
lugares que su `AGENTS.md` declara y sus 1240 tests en verde.

⚠ **La propagación del CDN de PyPI volvió a morder**, igual que con 0.9.0: la API JSON ya servía
0.9.1 y el índice de `pip` todavía no. Se resolvió sola entre un comando y el siguiente. Antes de
concluir que una subida falló, se mira el índice simple.

**Lo que queda pendiente y NO es de Oracle:** migrar las 33 medidas de Jam a la aridad vigente de
`ninguno`, `peor` y `ninguno-par`. Ahora al menos están listadas en vez de matar la corrida.

### Corte 0.9.0: un caso observado dice por dónde ir a contradecirlo

**Commiteado (`fdee004`), empujado, con tag anotado `v0.9.0` y release en GitHub como Latest. Sin
publicar en PyPI.** El árbol declara distribución `0.9.0`, álgebra
`0.6` y sintaxis `0.2`; el argumento está en `ESPECIFICACION.md` §0 y las notas en
`NOTAS-DE-RELEASE.md`. Sube la **menor** y no el parche porque la medida nueva es de ámbito
universal: obliga también a los consumidores, y uno que actualice sin usar nada nuevo puede pasar de
verde a rojo.

Qué entra: `meta.todo_caso_observado_declara_de_donde_salio`, el campo `declara_de_donde_salio` en
la relación `caso`, `tools/sondear_procedencia.py` con sus 9 tests, los casos 483 y 484, la sombra
sobre el propio corpus en `oracle.json`, el chequeo de CI partido en dos números y el estudio
[`estudios/PROCEDENCIA-DE-DONDE-SALIO-UN-CASO.md`](estudios/PROCEDENCIA-DE-DONDE-SALIO-UN-CASO.md).

**Lo que NO demuestra:** nada de esto es autenticidad ni acerca a ella. Sigue sin haber forma de
distinguir una corrida de una transcripción, y `observar.py` sigue escribiendo
`autenticidad.comprobada: false`. Lo que cambia se puede afirmar entero: de un caso `observada` ya
se puede exigir que diga por dónde ir a contradecirlo.

**Números del corte:** corpus **186** · suite **1381** · mutación de medidas **915/915** · mutación
de `tools/sondear_procedencia.py` **17/17** · aceptación con un rojo que tumba y uno en sombra, las
cuatro comprobaciones de CI en verde · Jam ✓ 20/3 y LyraGASP ✓ 14/14, los dos con la medida nueva en
**cero** · `verificar_instalacion.py` WHEEL OK con los diez ejecutables · cifras y manual
regenerados.

**Artefactos en `dist/`, verificados:** sus **121 archivos de código y datos coinciden byte a byte
con el árbol**, y en un venv limpio fuera del checkout `oracle 0.9.0` corre la sonda nueva y
revalida la observación de LyraGASP con la misma evidencia `sha256:1dda6ee0…`.

```
whl    sha256:8644d3981c5171d930bc2a1378bd590ae7f18b84b82a21b1208b5f726e50ae67
tar.gz sha256:e546a7717b26b39ab63bd15a1a87c7613f0f51d319c1d47fe8e653d0430e2ff2
```

**PyPI: `0.9.0` publicada el 2026-09-07 por el usuario, y verificada.** Los dos digests y los dos
tamaños que sirve PyPI coinciden con el build local y con los que este relevo tenía anotados **antes**
de la subida. Instalada en un venv limpio bajando desde PyPI: `oracle 0.9.0`, los diez ejecutables,
la medida nueva y `tools/sondear_procedencia.py` empaquetadas, la sonda corriendo desde el paquete,
y `oracle-aceptacion` midiendo a los dos consumidores reales —LyraGASP ✓ 14/14 y Jam ✓ 20/3, los dos
con la medida nueva en cero—. El recorrido de 0.8.1 revalida la observación de LyraGASP con la misma
evidencia `sha256:1dda6ee0…`.

⚠ Al minuto de subir, la **API JSON de PyPI ya servía 0.9.0 y el índice de `pip` todavía no**:
`Could not find a version that satisfies the requirement oracle-metalenguaje==0.9.0`. Es propagación
del CDN y se resolvió sola. Si pasa, se mira el índice simple
(`curl -s https://pypi.org/simple/oracle-metalenguaje/ | grep 0.9.0`) antes de concluir que la
subida falló.

### Orden de lectura

1. `NOTAS-DE-RELEASE.md` — qué entra en 0.8.1 y qué NO empieza a demostrar.
2. `estudios/OBSERVAR-0.8.1-RECORRIDO.md` — la herramienta, qué se le encontró al experimento
   anterior, y el defecto que encontró un ataque y la mutación no.
3. `tools/observar.py` — el docstring describe el formato del plan; es la referencia.
4. `PLAN-0.8.1-SENSOR.md` — las tres decisiones y cómo quedaron respondidas.

### Qué es 0.8.1

`tools/observar.py`, con dos verbos: `capturar` y `revalidar`. Ejecuta el sensor **del consumidor**
como otro proceso, conserva su salida **byte a byte**, se niega ante una lectura vacía o inestable y
ante un referente que cambia durante la corrida, y compara el resultado contra la expectativa
**declarada en el plan antes de correr**. La polaridad la dictamina `meta.el_caso_se_pone_como_debe`,
no un `if` de la herramienta. **No agrega nada al lenguaje.**

### Lo que NO demuestra, y hay que seguir diciendo

**La autenticidad no se comprueba, y ninguna huella la comprueba.** Medido con ataques reales: un
«sensor» que no lee nada, uno que le agrega filas inventadas a una lectura real, y un `cp` de un
JSON escrito a mano **pasan los tres**, y salen con `autenticidad.comprobada: false`. De un caso
`observada` NO se puede deducir que alguien midió el mundo; se puede deducir que un programa corrió,
que su salida se conservó sin tocar y que no cambió entre dos lecturas seguidas.

**El defecto que encontró el ataque, y la lección que dejó.** El control de estabilidad comparaba
las dos lecturas ya parseadas con el `==` de Python, donde `True == 1`. Un sensor que emitía `true`
y después `1` pasaba —bytes y tipos distintos— y el caso salía como observación de algo no
reproducible. Los **146 mutantes del archivo estaban muertos** mientras el defecto seguía ahí: la
mutación pregunta «¿algún test nota si cambio esta línea?», y esto vivía en el *significado* de `==`
sobre datos parseados. **Cero sobrevivientes no es cero defectos.** Lo encontró `codex` atacando;
`agy`, leyendo el mismo archivo con cuatro preguntas dirigidas, no lo encontró.

### Números del corte

| | |
|---|---|
| suite | **1353 tests**, verde |
| corpus | **184 casos** |
| aceptación | 1 medida meta roja, línea literal de CI intacta |
| mutación de medidas | **902/902** |
| mutación de `tools/observar.py` | **146 · 146 muertos · 0 sobrevivientes · 0 equivalentes declarados**, medido después del arreglo |
| `trazar.py` · `sondear_generador.py` · `cifras.py` | verdes y vigentes |
| `verificar_instalacion.py` | WHEEL OK, 10 entry points |
| Jam | 23 casos, sombras 9 / 54 / 41 — sin cambios |
| LyraGASP | 28 casos, 14 rojos y 14 verdes, sombras 8 / 16 / 9 |

### Lo que queda pendiente

- **LyraGASP sigue sin commitear.** Sus agregados nuestros son de dos turnos y su árbol tiene 45
  renglones de trabajo ajeno. **No se commiteó nada ahí**; hace falta decisión del usuario sobre qué
  entra. Jam no se tocó en ningún turno.
- **Nada autentica una corrida.** Sigue sin haber forma de distinguirla de una transcripción.
- **No se abrió el editor.** Los sensores que necesitan Unreal siguen sin correrse, los 37 ground
  truth siguen ausentes, y las sombras de unidades y origen de umbrales no se mueven por esto.

### Los artefactos, verificados

`dist/oracle_metalenguaje-0.8.1-py3-none-any.whl` y `dist/oracle_metalenguaje-0.8.1.tar.gz`.
Sus **119 archivos de código y datos coinciden byte a byte con el árbol**. En un venv limpio, desde
un cwd vacío fuera del checkout: `oracle 0.8.1`, y `python -m oracle_metalenguaje.tools.observar
capturar` corrió de punta a punta contra el sensor real de LyraGASP, cargando sus medidas meta del
catálogo empaquetado y dando la misma evidencia `sha256:1dda6ee0…`.

```
whl    sha256:ba790bb72dc71266cca0a93ab342af621ba9c91d747d55f5625ad77a0381e1d7
tar.gz sha256:777479585b6baf80b6630364dd08640f6a61f315983a7521b69662e6582ea702
```

### Cómo se sube a PyPI

**Lo sube el usuario, y lo sube con `uvx`:**

```bash
cd /home/workstation/Dev/oracle
uvx twine upload dist/oracle_metalenguaje-<version>*
```

⚠ **Hasta el 2026-09-07 acá decía `python3 -m twine`, y en esta máquina eso NO CORRE**: no hay
`twine` instalado para el intérprete del sistema (`No module named twine`), igual que no hay
`build`. La receta vivió varios cortes sin que nadie la ejecutara como estaba escrita — el mismo
defecto que el `==0.3.3` de LyraGASP, que declaraba una versión que el entorno no tenía. Si alguna
vez hay que construir los artefactos, es un venv aparte con `build` adentro, no `python3 -m build`.

Se suben **sólo** los dos archivos de la versión que se corta: `dist/` conserva artefactos de
cortes anteriores —hoy están ahí los de 0.7.0 y 0.8.0, que nunca se publicaron— y un
`upload dist/*` intentaría resubirlos.

Después de subir, la verificación que corresponde no es abrir la página: es comparar los digests
que sirve PyPI contra el build local e instalar desde PyPI en un venv limpio.

```bash
curl -s https://pypi.org/pypi/oracle-metalenguaje/<version>/json |
  python3 -c "import json,sys; [print(a['filename'], a['digests']['sha256']) for a in json.load(sys.stdin)['urls']]"
sha256sum dist/oracle_metalenguaje-<version>*
```

### Comprobaciones para retomar

```bash
python3 -B -m unittest discover -s tests -q
python3 tools/corpus.py --proyecto . --resumen
python3 tools/aceptacion.py --proyecto .
python3 tools/aceptacion.py --proyecto /home/workstation/Dev/jam/medidas --confiar-escalares
python3 tools/aceptacion.py --proyecto /home/workstation/Dev/games/unreal/LyraGASP/medidas --confiar-escalares
python3 tools/mutar_codigo.py --objetivo tools/observar.py
```

Esperados: Oracle 184 casos y **1** medida meta roja; Jam 23 y Lyra 28, los dos en **0** conservando
tres sombras cada uno. CI exige exactamente:

```text
la_medida_no_se_fija_solo_con_evidencia_fabricada        2 (<= 0)
```

⚠ **Una ronda de mutación tarda ~40 minutos y toma un bloqueo sobre la raíz.** No edites el árbol
mientras corre. Y ojo con `pgrep -f <patrón>`: **se matchea a sí mismo**, y con el truco de los
corchetes igual matchea si tu propia línea de comandos menciona el archivo sin corchetes. Pasó dos
veces en este turno: una ronda leyó una copia anterior de los tests y reportó un sobreviviente que
ya estaba muerto, y otra vez creí que había una ronda viva cuando no la había.

### Sobre LyraGASP y su Oracle

⚠ **NO consume Oracle por subtree.** No existe `vendor/` en ese repositorio. Según su propio
`docs/ORACLE.md`, usa un venv de `uv` con **`oracle-metalenguaje==0.3.3` desde PyPI**, fijado con
`==` a propósito. El `CLAUDE.md` de la máquina dice «subtree en `vendor/oracle`» y **está
desactualizado para este consumidor** (Jam sí usa subtree).

La consecuencia: hasta que 0.8.1 esté en PyPI **y** alguien suba ese pin, el recorrido no corre
desde el Oracle instalado de Lyra. Se corre desde el árbol de trabajo, apuntando con rutas:

```bash
cd /home/workstation/Dev/oracle
python3 tools/observar.py revalidar \
  --plan     <LyraGASP>/medidas/observaciones/dataset-ml-deformer.plan.json \
  --registro <LyraGASP>/medidas/observaciones/2026-09-07-dataset/registro.json
```

Lo agregado en LyraGASP, sin commitear: el plan y la carpeta `2026-09-07-dataset/` (este turno), el
caso `018-…json` (este turno), y del turno anterior el caso `017-…json` y
`medidas/observaciones/2026-09-06-dataset/`. Se comprobó contra el `arbol` que guarda el registro
del turno anterior: desde entonces sólo aparecieron esos dos casos y esa carpeta, y no desapareció
nada.

### Límites y autorizaciones

- El servidor MCP **no se modificó**; sólo las expectativas de versión de sus tests, como en 0.7.0.
- La autorización ejecutada fue: commit y push de Oracle. **PyPI lo sube el usuario.**
- No desactivar sombras ni reclasificar evidencia vieja para mejorar cifras. No se hizo.
- Si aparece un equivalente real, retirar el constructo, no declararlo. Se retiraron tres.
- `ask-agy` es el wrapper de Gemini, no `ask-gemini`. `ask-opencode` sólo con Go
  (`OPENCODE_MODEL=opencode-go/...`); su predeterminado es OpenRouter.
- **`ask-codex` con un encargo adversario fue lo más rentable de este turno.** Encontró el único
  defecto real; la lectura conceptual de `agy` no encontró nada. Si algo tiene una promesa cara,
  conviene pedir que la ataquen antes que pedir que la lean.

## Avance actual: primer recorrido real del plan del sensor

El usuario pidió seguir con `PLAN-0.8.1-SENSOR.md`. Se ejecutó el sensor existente de dataset de
LyraGASP sobre archivos reales, sin abrir Unreal: 37 clips declarados, 37 FBX presentes y 0 ground
truth. La medida correspondiente dio rojo 37. Con autorización se agregaron cinco archivos nuevos
al consumidor: el caso observado 017 y `medidas/observaciones/2026-09-06-dataset/` con evidencia,
registro, registrador del experimento y README. No se tocaron sus archivos existentes ni assets.
La corrida fue el 2026-09-07 00:42:45 UTC; la carpeta usa el día local de Salta, 2026-09-06.

Lyra pasa corpus y aceptación con 27 casos, 13 rojos esperados y 14 verdes. Sus pendientes de
evidencia observada bajan de 9 a 8, sin quitar ninguna sombra. Jam mantiene 23 casos y sus sombras
9/54/41. Oracle mantiene 184 y la línea literal de los dos pendientes declarados. Pasan los cuatro
tests del sensor/adaptador y 9/9 mutantes de la medida de ground truth, por conducta; el caso nuevo
detecta seis y no sustituye los bordes sintéticos. No se repitió la suite completa de Oracle en
este avance: su código no cambió y la última medición sigue siendo la del corte de abajo.

La evidencia del caso coincide exactamente con el JSON emitido. Se comprobaron sus huellas y seis
referentes estables. Un control construido confirma el límite: huellas distintas dan rojo 1, dos
declaraciones falsas iguales dan verde 0. L−2 compara declaraciones, no autentica una corrida.
El sensor sólo consultó presencia de FBX/ABC; no leyó ni certificó sus contenidos.

Detalle y siguientes pasos en `estudios/SENSOR-0.8.1-PRIMERA-CORRIDA.md`. El registrador conservado
es un experimento local, no una herramienta general con su código fijado. Queda propuesto un camino
reutilizable de captura/revalidación del consumidor. No se inició la parte que requiere el editor,
no se arreglaron los ground truth y no se hizo corte, commit, push o publicación. Las versiones
siguen en 0.8.0 / 0.6 / 0.2 y el servidor MCP sigue intacto.

## Estado del corte anterior: 0.7.0 en commit, corte local 0.8.0 verificado

El usuario autorizó el commit del corte: `f57b67f`, «Corte 0.7.0: canal de reporte verificado y
documentado». No se hizo push ni se publicó. El corte de 0.8.0 queda sin commitear:
`nucleo/generador.py` comprueba la polaridad, amplifica conteos simples según su umbral y explica
la negativa cuando la propuesta no sirve, sin escribir archivos. Distribución subió a 0.8.0;
álgebra 0.6 y sintaxis 0.2 se conservan con argumento en §0: cambia la fórmula distribuida de una
medida, no la interpretación de una misma fórmula. Las notas explican el cambio de conteos a días.

El estado detallado y el inventario revisado están en `estudios/UMBRAL-0.8.0-REVISION.md`.
El generador tiene 22 pruebas; los 22 sitios de mutación de los controles nuevos quedaron muertos.
Esto no afirma que el generador histórico entero esté fijado.

La medida de edad de las sombras usa ahora `peor` con tolerancia 90 días: conserva identidad,
polaridad y testigos, pero informa la edad máxima incumplida, no el conteo. Sin incumplimientos,
informa cero. Tiene seis casos y cierra 9/9 mutantes. `tools/sondear_generador.py` ejecuta cinco
sondas, publica 17 comprobaciones y las juzga con `meta.el_caso_se_pone_como_debe`. Corre en CI,
tiene 11 tests y su mutación completa cierra 27/27, sin sobrevivientes ni equivalentes declarados.
Los casos 479–482 custodian ambos recorridos; el 482 registra la ejecución del programa sobre
entradas construidas, no una observación de un dominio externo.

Verificación final: **1295 tests OK, corpus 184, mutación de medidas 902/902** (750 por conducta,
152 rechazos del álgebra). Aceptación conserva los dos pendientes declarados y la línea literal de
CI intacta; Jam y LyraGASP pasan con 23 y 26 casos y tres sombras cada uno. Cifras y manual regenerados.

Se retiraron constructos equivalentes de la nueva sonda. También se eliminó el valor por defecto
imposible de las coordenadas de `ErrorSintaxis` en `tools/medida.py` y su declaración histórica en
`equivalentes.json`; los tres sitios afectados cierran 3/3 en mutación dirigida. No se midió otra
vez todo ese archivo. La plantilla ahora orienta hacia `peor` cuando el dominio es una magnitud.

El corte repitió suite, corpus, aceptaciones y mutaciones de medidas y sonda con los números
anteriores. Wheel y sdist en `dist/`, 0.8.0; sus 121 archivos de código y datos coinciden con el
árbol. Instalación limpia en `/tmp/oracle-080-instalacion-0T6lTR/venv`: versión, ayuda de reportar,
sonda empaquetada y medida de sombras comprobadas. `tools/verificar_instalacion.py` pasa también
los diez ejecutables, datos y motores aislados. Persisten los avisos de setuptools sobre directorios
de datos, pero el contenido fue verificado. No se tocó el servidor MCP.

Gemini (`ask-agy`) dio una segunda lectura conceptual de versiones y compatibilidad; no es una
verificación de código. OpenCode Go leyó los archivos pero agotó cuatro minutos sin informe; no
se cuenta como aprobación. Detalle en la revisión. El inventario de once sitios está triado;
permanecen declarados el límite de monotonía de `max`/`min`, el contrato de agregados vacíos y la
falta de fabricación general de magnitudes. No son capacidades implementadas.

Queda la autorización de commit/publicación que corresponda. El plan del sensor se inició después
de este corte; su avance y sus límites están en el encabezado de este relevo.

## Actualización: corte local 0.7.0

El corte solicitado quedó en `f57b67f`, sin push ni publicación. Distribución
`0.7.0`; álgebra `0.6` y sintaxis `0.2` conservadas por la regla de §0: el canal agrega una
herramienta, ningún nodo ni forma del lenguaje. El servidor MCP no se modificó; sólo se
actualizaron las expectativas de versión de sus tests.

Verificación independiente: 1266 tests OK, corpus 180, aceptación con la única medida meta roja
en valor 2 y la línea literal de CI intacta; mutación de `tools/reportar.py`, 19/19 sin
sobrevivientes, tiempos agotados, errores de arnés ni equivalentes declarados. Jam y LyraGASP
pasan con 23 y 26 casos, respectivamente, conservando tres sombras cada uno. La suite y la
mutación requieren permiso para el test que crea un temporal bajo `Path.home()`.

Se corrigió la identidad visual de `docs/reportar.html` y el contraste de los enlaces del pie
bajo el cursor: de 2,57:1 a un mínimo de página de 6,65:1. Se comprobaron 62 elementos con texto,
escritorio y teléfono, en reposo y bajo el cursor. La plantilla coincide con el reporte y el
impresor de `.caso`. README y manual HTML regenerados.

Wheel y sdist locales en `dist/`, versión 0.7.0; instalación limpia y ambos comandos pedidos OK.
El venv de prueba está en `/tmp/oracle-070-instalacion-7IeSN1/venv`. Las notas de release registran
los números y dos advertencias que no se ocultaron: una medida de mutación de medidas no juzga
la evidencia de mutación de código por falta de `detecciones_conductuales`, y setuptools advierte
sobre directorios de datos aunque se verificó que los 117 archivos se empaquetan íntegros.

El texto que sigue es el estado anterior al corte, conservado como contexto histórico.

---

Estado al cortar por falta de crédito. Escrito para que quien siga —persona o agente— no tenga que
reconstruir nada leyendo commits.

## Dónde está todo, ahora mismo

| | |
|---|---|
| **PyPI** | `0.6.0` publicada y verificada bit a bit contra el build local |
| **GitHub** | `main` en `8adfe74` · Releases `v0.5.0` y `v0.6.0` creadas · 0.6.0 es Latest |

> Las dos filas de arriba son del corte 0.6.0 y quedaron **desactualizadas**: al 2026-09-07 GitHub
> tiene además `v0.7.0` y `v0.8.1` —`v0.8.1` es Latest— y PyPI está en `0.8.1`, sin 0.7.0 ni 0.8.0.
> Se conservan porque este bloque es contexto histórico, no el estado de hoy; el estado de hoy está
> arriba de todo.
| **El sitio** | `segtem.github.io/oracle` con inicio, **dónde entra**, **de cero** y el manual |
| **La versión en el repo** | **0.6.0**, y se queda ahí. Sube en el corte, no al empezar |
| **La suite** | 1266 tests, verde |

## Qué se está haciendo justo ahora

**codex está cerrando 0.7.0**, despachado con orden de trabajar solo hasta terminar. Su orden está
en el scratchpad de la sesión; lo que le pedí, en orden:

1. la plantilla de issue en `.github/ISSUE_TEMPLATE/` — **la mitad faltante del canal**;
2. documentar el canal en el README y en el sitio;
3. escribir el camino de promoción de issue a `.caso`;
4. las notas de release de 0.7.0.

Con tres reglas duras: **no subir la versión**, **no commitear ni pushear**, **no tocar el servidor
MCP**. Cuando termine, hay que leer su informe y verificar por cuenta propia antes de commitear —
las dos veces anteriores subió la versión por su cuenta y hubo que revertirla junto con los tests.

## 0.7.0 — el canal de reporte

**Hecho:** las cuatro decisiones (`estudios/CANAL-DE-REPORTE.md`), y `oracle reportar`, que mide
**19/19 sin sobrevivientes**.

La propiedad que custodia, comprobada corriéndola: **sin pedirlo explícitamente no sale un solo dato
del dominio**. La medida y la evidencia entran sólo con `--incluir-medida` o `--incluir-evidencia`.

**Falta:** lo que está haciendo codex.

## 0.8.0 — el umbral > 0 y el generador · `PLAN-0.8.0-UMBRAL.md`

Decidido, sin empezar. El catálogo base es **55 de 55 en `umbral <= 0`**: Oracle nunca ejerce el otro
camino de su propio lenguaje. No es teórico — por eso vivió meses la exclusión global de mutadores.
Y la misma ceguera está en `nucleo/generador.py`, que fabrica un `falso_verde` con una sola fila
asumiendo que rompe cualquier umbral.

**Lo que el plan prohíbe:** escribir una medida con umbral > 0 sólo para tener una. Si no aparece
una candidata legítima, el hallazgo es ése.

## 0.8.1 — que la evidencia venga del mundo · `PLAN-0.8.1-SENSOR.md`

Anotado. Hoy todo lo que Oracle demuestra es coherencia interna. El número es provisorio: si agrega
algo al lenguaje sube la menor por §0.

## Deudas vivas, que no están en ningún plan de versión

- **El ámbito `del_origen` de `meta.toda_medida_declara_su_ambito` es temporal** y nada registra
  cuándo debe volverse universal. Está anotado en `PLAN-0.5.0-AMBITO.md`. El precedente de que esto
  se olvida: `segun` lleva meses con 41 umbrales en sombra en un consumidor.
- **Jam tiene tres medidas universales en sombra.** No es deuda de Jam: son tres medidas de Oracle
  demasiado exigentes para el estado real de un consumidor.
- **LyraGASP tiene una medida que no puede juzgar** (`proceso.codigo_con_mutante_que_lo_mata` espera
  un campo `m.estado` que su evidencia no trae). Verificado contra 0.4.0: es previa, no la trajimos.

## Lo que aprendí en esta sesión y conviene no volver a aprender

**No editar el árbol mientras corre una ronda de mutación.** Lo hice cuatro veces. El arnés se
defiende —se niega a entregar un número— pero la corrida se pierde.

**`pgrep -f <patrón>` se matchea a sí mismo.** Un bucle de espera con el patrón adentro nunca
termina; me costó hora y media. El truco es `mutar_codigo[.]py`: los corchetes hacen que la línea de
comandos del propio bucle no coincida con su regex.

**Verificar lo que ya estabas mirando no es verificar.** El diagrama de `donde-entra.html` se
corrigió cuatro veces: el `<dt>` y no el `<h2>`; `color` y no `fill` —en SVG el texto sin `fill` es
negro, no toma `color`—; y coordenadas a ojo. Recién se cerró cuando el chequeo dejó de ser mirar y
pasó a ser un script que recorre las cajas y falla si un trazo atraviesa una.

**Un test que ejecuta una rama no es un test que la fija.** Dos veces escribí la entrada que corre
el código en vez de la que lo distingue de su mutante. El caso más claro: un acumulador cuyo valor
inicial sólo importa si el contenido ARRANCA con la corrida.

**Un equivalente genuino se borra, no se declara.** Pasó dos veces —`split(maxsplit)` bajo un `[0]`,
y un acumulador bajo un piso `max(3, ...)`—. Anotar un equivalente es aceptar para siempre un
mutante que nadie puede matar; sacar el constructo lo elimina.

## Sobre los agentes

- **agy** entregó todo lo que se le dio y respetó todos los frenos: paró cuando le dije que parara,
  no reclasificó cuando le dije que no, no inventó un caso observado.
- **codex** es fuerte en lo mecánico y paró dos veces ante un defecto real en vez de tocar
  producción, que es exactamente lo que se le pidió. Su falla repetida es subir la versión por su
  cuenta.
- **opencode falló 3 de 3** en tareas reales, incluida una completamente especificada. Sólo funcionó
  con un encargo de juguete. No usarlo para nada del proyecto.
