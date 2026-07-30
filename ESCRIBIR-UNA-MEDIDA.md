# Escribir una medida

Esto existe para que **no haga falta pedirle permiso a nadie**. Todo el argumento del repositorio es
que quien ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que saber cómo está
hecho el evaluador, el único que puede escribir reglas es quien lo escribió — y ese es exactamente el
problema que veníamos a resolver.

## El orden importa: primero el caso, después la medida

**Escribí el caso del corpus antes que la medida.** No es prolijidad:

- una medida escrita primero se escribe para pasar, no para atrapar;
- la herramienta puede decirte si tu medida está mal *formada*, pero **no puede saber qué quisiste
  decir**. Una condición invertida —que selecciona lo que está bien en vez de lo que ofende— pasa
  todas las comprobaciones automáticas. El caso es lo único que lo detecta.

```bash
# 1. el caso: la evidencia del defecto, y que se espera ROJO
#    (corpus/proceso/0NN-lo-que-paso.json — copiá uno que exista y cambialo)

# 2. mirá con qué contás
python tools/medida.py --relaciones     # los hechos y sus campos, derivados de la evidencia real
python tools/medida.py --escalares      # las funciones de dominio, operadores y agregados

# 3. la medida
python tools/medida.py --nueva colocacion.mi_regla
#    editás el archivo…
python tools/medida.py catalogos/colocacion/colocacion.mi_regla.json

# 4. que todo siga cerrando
python tools/aceptacion.py    # tu caso tiene que ponerse rojo
python tools/mutar.py         # y el corpus tiene que fijar tu medida
```

Si el proyecto declara funciones en `escalares.py`, los comandos que cargan o evalúan su catálogo
requieren `--confiar-escalares`. Esa bandera autoriza código Python con los mismos permisos del
proceso. `--relaciones` y `--escalares` sin la bandera son seguros: no ejecutan el archivo externo.

El id tiene una gramática cerrada: `dominio.nombre`, con segmentos en minúsculas ASCII, dígitos o
`_`. No se aceptan rutas ni `..`; el archivo se resuelve y confina debajo de `catalogos/` antes de
crear cualquier directorio.

## La forma corta: las macros

**26 de las 27 medidas del catálogo están escritas como macro.** Son azúcar que expande a la forma
canónica —`--expandir` te muestra en qué—, así que el evaluador, la mutación y el inventario no se
enteran de que existen.

```json
["ninguno", "proceso.test_con_mutante_que_lo_mata",
  "mutante", "m",
  ["==", ["campo", "m", "murio"], false],
  "un mutante que sobrevive es un test que no discrimina",
  "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"]
```

| Macro | Para qué | Cuántas la usan |
|---|---|---|
| `ninguno` | ninguna fila debe cumplir el predicado | 22 |
| `ninguno-par` | lo mismo sobre PARES de la misma relación | 2 |
| `peor` | el peor caso de una expresión no pasa de una tolerancia | 2 |

**`peor` recibe la tolerancia una sola vez** y genera con ella el filtro y el umbral. Antes había que
escribirla dos veces y nada las mantenía juntas — era el caso `012` del corpus, cerrado por
construcción.

Las macros no son un embudo: si tu caso no encaja, la forma canónica sigue siendo válida.
`colocacion.interpenetracion` está escrita así porque une dos relaciones DISTINTAS.

## La forma canónica

```json
["medida", "dominio.nombre",
  ["desde", ["de", "relacion", "x"],
            ["donde", <lo que OFENDE>]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "por qué ese número y no otro"],
  ["alcance", "qué NO ve esta medida"]]
```

Cinco piezas, y dos son obligatorias por una razón:

- **`porque`** — un número que nadie puede discutir es una métrica esperando a volverse objetivo.
- **`alcance`** — un verde que no dice lo que no miró se lee como «está bien». Con esto, el informe
  termina enumerando sus propios puntos ciegos.

Y una que **no se declara**: los **testigos** son las filas que sobrevivieron al `donde`. No los
calculás aparte — si lo hicieras, tendrías la misma condición escrita dos veces y nada que las
mantenga sincronizadas.

## Tres ejemplos, de menor a mayor

### 1. Contar lo que ofende

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["==", ["campo", "m", "murio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa con el código roto"],
  ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió"]]
```

El 90% de las medidas son así: filtrás lo malo, contás, y el umbral es `<= 0`.

### 2. Medir una magnitud, no contar

```json
["medida", "snap.grilla",
  ["desde", ["de", "pieza", "a"],
            ["donde", [">", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0]]],
  ["resumen", "max", ["desvio_de_grilla", ["hecho", "a"], 100.0]],
  ["umbral", "<=", 1.0, "por debajo de 1 cm el desvío no se ve"],
  ["alcance", "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"]]
```

Acá el valor es centímetros y no una cuenta, y eso dice más en el informe. **Escrita a mano, la
tolerancia aparece dos veces** —en el `donde` y en el `umbral`— y nada las mantiene juntas: era el
caso `012` del corpus. Por eso esta forma se escribe con la macro `peor`, que la recibe una sola vez.

### 3. Comparar filas entre sí

```json
["medida", "vault.nombre_unico_en_el_vault",
  ["desde", ["unir", ["de", "documento", "a"], ["de", "documento", "b"]],
            ["donde", ["y", ["==", ["campo", "a", "nombre"], ["campo", "b", "nombre"]],
                            ["!=", ["campo", "a", "carpeta"], ["campo", "b", "carpeta"]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un wikilink apunta por NOMBRE y no por ruta: dos homónimos dejan el enlace a cara o cruz"],
  ["alcance", "NO ve nombres parecidos pero distintos, que confunden aunque no rompan un enlace"]]
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
vive con el que produce los datos (en Jam, `tools/emitir_hechos_*.py`). El sensor produce hechos y
**no juzga**; el álgebra juzga y **no mira el mundo**. Mezclarlos es cómo se llega a un verificador
que nadie puede discutir.
