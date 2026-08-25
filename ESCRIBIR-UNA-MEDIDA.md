# Escribir una medida

Esto existe para que **no haga falta pedirle permiso a nadie**. Todo el argumento del repositorio es
que quien ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que saber cómo está
hecho el evaluador, el único que puede escribir reglas es quien lo escribió — y ese es exactamente el
problema que veníamos a resolver.

**La superficie es cómo se escribe; el JSON es cómo se guarda.** Este documento enseña a
escribir medidas y casos directamente en su superficie de autoría (`.oracle` y `.caso`), que el
sistema carga por igual sin paso de traducción.

## El orden importa: primero el caso, después la medida

**Escribí el caso del corpus antes que la medida.** No es prolijidad:

- una medida escrita primero se escribe para pasar, no para atrapar;
- la herramienta puede decirte si tu medida está mal *formada*, pero **no puede saber qué quisiste
  decir**. Una condición invertida —que selecciona lo que está bien en vez de lo que ofende— pasa
  todas las comprobaciones automáticas. El caso es lo único que lo detecta.

```bash
# 1. el caso: la evidencia del defecto, y que se espera ROJO
#    (el andamio ya nace en superficie .caso, o copiá uno que exista)
python tools/corpus.py --nuevo proceso/0NN-lo-que-paso   # crea corpus/proceso/0NN-lo-que-paso.caso

# 2. mirá con qué contás
python tools/medida.py --relaciones     # los hechos y sus campos, derivados de la evidencia real
python tools/medida.py --escalares      # las funciones de dominio, operadores y agregados

# 3. la medida: el andamio ya nace en superficie infija, y el catálogo lo carga tal cual
python tools/medida.py --nueva colocacion.mi_regla     # crea catalogos/colocacion/colocacion.mi_regla.oracle
python tools/medida.py catalogos/colocacion/colocacion.mi_regla.oracle

# 4. que todo siga cerrando
python tools/aceptacion.py    # tu caso tiene que ponerse rojo
python tools/mutar.py         # y el corpus tiene que fijar tu medida
```

### Los dos formatos del catálogo y del corpus

El catálogo y el corpus cargan **superficie (`.oracle`, `.caso`) y `.json` por igual**: los
archivos en superficie no necesitan traducirse a nada para funcionar. El mismo id en los dos
formatos es un error que nombra los dos archivos — no gana ninguno, porque un ganador silencioso es
una divergencia esperando.

- `python tools/corpus.py --nuevo <grupo/NNN-descripcion>`: crea el andamio del caso, ya en superficie `.caso`.
- `python tools/medida.py --nueva <dominio.nombre>`: crea el andamio de la medida, ya en superficie `.oracle`.
- `python tools/sintaxis.py --imprimir <archivo.json>`: pasa una medida vieja a la superficie.
- `python tools/sintaxis.py --leer <archivo.oracle>`: el camino inverso para medidas, si alguna vez lo necesitás.

El id tiene gramática cerrada y **ASCII**: `dominio.nombre` para medidas y `NNN-descripcion` para
casos (minúsculas, dígitos y `_`/`-`). No es que el proyecto no sea en español —la prosa de
`porque` y de `alcance` lo es entera—: es que el id es también un nombre de archivo, y en Unicode
`dueño` puede ser dos secuencias de bytes distintas que se dibujan idénticas (NFC contra NFD). Dos
ids que nadie puede distinguir mirando son una divergencia silenciosa, y eso se cierra por
gramática.

### Frontera de confianza

Si el proyecto declara funciones en `escalares.py`, los comandos que cargan o evalúan su catálogo
requieren `--confiar-escalares`. Esa bandera autoriza cargar código Python externo, pero Oracle lo
ejecuta en un trabajador separado: el proceso principal sólo recibe metadatos y resultados JSON. El
trabajador puede leer el proyecto, Oracle y la biblioteca estándar; sólo puede escribir dentro del
proyecto, no puede abrir red ni crear procesos. Si una UDF necesita más autoridad, no pertenece a una
medida: generá ese dato antes y entregalo como evidencia.

`--relaciones` y `--escalares` sin la bandera son seguros: no ejecutan el archivo externo.

El id tiene una gramática cerrada: `dominio.nombre`, con segmentos en minúsculas ASCII, dígitos o
`_`. No se aceptan rutas ni `..`; el archivo se resuelve y confina debajo de `catalogos/` antes de
crear cualquier directorio.

## La forma corta: las macros

**La mayoría de las medidas del catálogo están escritas como macro.** Son azúcar que expande a la forma
canónica —`python tools/medida.py --expandir <archivo>` te muestra en qué—, así que el evaluador, la mutación y el inventario no se
enteran de que existen.

```oracle
ninguno proceso.test_con_mutante_que_lo_mata:
    de mutante m
    donde m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    umbral <= 0 porque "un mutante que sobrevive es un test que no discrimina"
    alcance "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"
```

| Macro | Para qué | Cuántas la usan |
|---|---|---|
| `ninguno` | ninguna fila debe cumplir el predicado | 26 |
| `ninguno-par` | lo mismo sobre PARES de la misma relación | 2 |
| `peor` | el peor caso de una expresión no pasa de una tolerancia | 2 |

**`peor` recibe la tolerancia una sola vez** y genera con ella el filtro y el umbral:

```oracle
peor snap.grilla:
    de pieza a
    expresion desvio_de_grilla(hecho(a), 100.0)
    tolerancia 1.0
    umbral <= 1.0 porque "por debajo de 1 cm el desvío no se ve"
    alcance "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"
```

Antes había que escribir la tolerancia dos veces y nada las mantenía juntas — era el caso `012` del corpus, cerrado por
construcción.

Las macros no son un embudo: si tu caso no encaja, la forma canónica sigue siendo válida.
`colocacion.interpenetracion` está escrita así porque une dos relaciones DISTINTAS.

## La forma canónica

```oracle-gramatica
medida dominio.nombre:
    de relacion x
    donde <lo que OFENDE>
    resumen contar(1)
    umbral <= 0 porque "por qué ese número y no otro"
    requiere relacion
    alcance "qué NO ve esta medida"
```

Las piezas obligatorias están por una razón:

- **`umbral` con `porque`** — un número que nadie puede discutir es una métrica esperando a volverse objetivo. Un umbral de igualdad (`==`) no se usa y está prohibido.
- **`alcance`** — un verde que no dice lo que no miró se lee como «está bien». Con esto, el informe
  termina enumerando sus propios puntos ciegos.
- **`requiere`** — declara qué relaciones de evidencia son indispensables para concluir. Si una relación requerida viene vacía o falta, la evaluación no emite un verde espurio sino `SIN EVIDENCIA`.

Y una que **no se declara**: los **testigos** son las filas que sobrevivieron al `donde`. No los
calculás aparte — si lo hicieras, tendrías la misma condición escrita dos veces y nada que las
mantenga sincronizadas. Tampoco se permite componer medidas entre sí (`DECISION-002`): cada medida
es una unidad de juicio aislada sobre evidencia directa.

## El formato de almacenamiento: por qué JSON

La superficie infija es cómo un humano la escribe, pero el archivo en `catalogos/` se guarda como una
lista JSON. Por ejemplo, la forma canónica anterior se almacena así:

```json
["medida", "dominio.nombre",
  ["desde", ["de", "relacion", "x"],
            ["donde", ["==", ["campo", "x", "activo"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "por qué ese número y no otro"],
  ["requiere", "relacion"],
  ["alcance", "qué NO ve esta medida"]]
```

¿Por qué almacenar una medida como JSON y no como texto plano? Porque **es homoicónico: el JSON es directamente el árbol de sintaxis abstracta (AST)**. Al ser una estructura de datos estándar y pura:
- Las medidas pueden inspeccionarse, mutarse y validarse mecánicamente sin requerir un parser complejo en cada etapa.
- **Las medidas pueden hablar de medidas**: es el nivel **L2** del proyecto. El propio catálogo de medidas se convierte en una relación (`medida_en_uso`), y se puede juzgar con el mismo álgebra de siempre (por ejemplo, verificando que ninguna medida use umbrales de igualdad flotante o que todas declaren su defensa y alcance).

## Tres ejemplos, de menor a mayor

### 1. Contar lo que ofende

```oracle
medida proceso.test_con_mutante_que_lo_mata:
    de mutante m
    donde m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    resumen contar(1)
    umbral <= 0 porque "un mutante que sobrevive es un test que no discrimina: pasa con el código roto"
    alcance "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió"
```

El 90% de las medidas son así: filtrás lo malo, contás, y el umbral es `<= 0` (un umbral `==` no se usa y está prohibido por `meta.ningun_umbral_de_igualdad`).

### 2. Medir una magnitud, no contar

```oracle
medida snap.grilla:
    de pieza a
    donde desvio_de_grilla(hecho(a), 100.0) > 1.0
    resumen max(desvio_de_grilla(hecho(a), 100.0))
    umbral <= 1.0 porque "por debajo de 1 cm el desvío no se ve"
    alcance "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"
```

Acá el valor es centímetros y no una cuenta, y eso dice más en el informe. **Escrita a mano en forma canónica, la
tolerancia aparece dos veces** —en el `donde` y en el `umbral`— y nada las mantiene juntas: era el
caso `012` del corpus. Por eso esta forma se escribe habitualmente con la macro `peor`, que la recibe una sola vez.

### 3. Comparar filas entre sí

```oracle
medida vault.nombre_unico_en_el_vault:
    de documento a
    unir documento b
    donde a.nombre == b.nombre y a.carpeta != b.carpeta
    resumen contar(1)
    umbral <= 0 porque "un wikilink apunta por NOMBRE y no por ruta: dos homónimos dejan el enlace a cara o cruz"
    alcance "NO ve nombres parecidos pero distintos, que confunden aunque no rompan un enlace"
```

`unir` hace el producto de una relación consigo misma. Es como se comparan cosas de a pares:
piezas que se clavan, documentos homónimos, las dos puntas de un relevo.

## Los errores que la herramienta sí te dice

| Qué pasa | Qué dice |
|---|---|
| falta la defensa del umbral | *el umbral `<= 0` no trae defensa* |
| falta `alcance` | *hay que declarar qué NO ve* |
| un campo mal escrito | *«>» sobre un valor ausente* — mirá `--relaciones` |
| nunca se pone roja | *una medida que no puede fallar no mide nada* |
| nunca se pone verde | *probablemente la condición esté invertida* |

Comparar contra un campo que no existe **es un error**, no un `False`. Un `False` silencioso
convertiría un nombre mal escrito en un verde, que es la peor falla posible acá.

## Lo que NO te puede decir

**Si la condición dice lo que quisiste decir.** Una medida que selecciona lo que está bien en vez de
lo que ofende pasa todas las comprobaciones: está bien formada, discrimina, y mide exactamente al
revés. La herramienta no lee intenciones.

Por eso el caso va primero. Y por eso `tools/mutar.py` existe: comprueba que el corpus **fije** tu
medida, o sea que si alguien la escribiera distinta, algún caso lo notaría.

## Si te falta un hecho

Si lo que querés medir no está en `--relaciones`, no se agrega acá: se agrega en el **sensor**, que
vive con el proyecto que produce los datos. El sensor produce hechos y
**no juzga**; el álgebra juzga y **no mira el mundo**. Mezclarlos es cómo se llega a un verificador
que nadie puede discutir.
