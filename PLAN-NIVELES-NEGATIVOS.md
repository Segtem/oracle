# Plan — L−1 y L−2, los dos niveles que miran hacia el mundo

**Estado:** L−1 cerrado e integrado (2026-08-28) · L−2 cerrado en esta rama.
La numeración y por qué la torre se cierra en L−2 están en
[`DECISION-005`](DECISION-005-CINCO-NIVELES-DE-REPRESENTACION.md).

```
L2   medidas sobre medidas   enunciados sobre L1                        ✓
L1   medidas                 enunciados sobre L0                        ✓
L0   evidencia               filas                                      ✓
────────────────────────────────────────────────────────────────────────
L−1  qué lee el sensor       su alcance y las unidades de cada campo    ✓ integrado
L−2  qué leyó, y en qué      identidad y frescura del referente         ✓ en esta rama
────────────────────────────────────────────────────────────────────────
     el terreno              no es un nivel: no se representa
```

---

## L−1 — qué lee el sensor

### El agujero, con el ejemplo que lo define

Una medida dice `umbral <= 1.0` sobre la altura de una pieza, pensando en **metros**. El sensor que
llena esa evidencia emite **centímetros**. Todo lo de arriba funciona: el sensor es fiel a lo que
leyó, la evidencia es válida, la medida es correcta, y el veredicto está mal. Nadie se entera.

Hoy no hay dónde escribir «el campo `alto` de `pieza` viene en centímetros», ni «este sensor lee el
AABB del asset y NO lee la malla real». Lo segundo se escribe en la prosa del `alcance` de cada
medida que consume esa relación —repetido, y sin que nada compare las copias entre sí.

### Qué lo cierra

Una **declaración de relación**: nombre, campos con tipo y unidad —o «sin unidad» explícito, nunca
un default— y el `alcance` del sensor, obligatorio por la misma razón que en una medida.

### Cómo se sabe que está terminado

Poder escribir, en el lenguaje y sin tocar Python:

- «ningún campo se entrega sin unidad declarada»;
- «ninguna medida compara un campo contra un umbral de otra unidad».

### Resultado medido el 2026-08-28

La relación declara la unidad de cada campo y `@escalar` declara la de cada argumento con
`unidades_argumentos`; un hecho entero o un texto usa `sin_unidad` de forma explícita. La ausencia
no impide cargar una escalar anterior, pero vuelve `sin_declarar` la cantidad que depende de ella.

Sin modificar Jam, sus 89 cantidades comparadas quedaron en 41 derivables y 48 no derivables. Las
dos apariciones de `snap.grilla` —filtro y resumen— quedaron no derivables porque
`desvio_de_grilla(hecho(a), 100.0)` todavía declara sólo el retorno `cm`: ahora el `100.0` sin unidad
de argumento ya no queda tapado por esa unidad de retorno.

### Lo que ya se sabe que va a doler

Convertir la unidad automáticamente está **prohibido**. Detectar el desajuste es el trabajo;
convertir por atrás fabrica un verde y el error deja de verse.

---

## L−2 — qué leyó, y en qué versión

### El agujero, con su propio ejemplo

El sensor leyó el `.uasset` del disco. El juego embarca la variante cocinada. **Todo lo que el
sensor reportó es cierto**, y el veredicto no habla de la cosa que se embarca. L−1 no lo ve: el
sensor está bien declarado y fue fiel a lo que leyó. El fallo está una capa más abajo — en *a qué*
le apuntó.

Tres formas del mismo fallo, las tres reales en este entorno:

| | el sensor leyó | el veredicto habla de |
|---|---|---|
| variante | el asset del disco | la variante cocinada que embarca el juego |
| momento | el estado en memoria del editor | lo que corre en el runtime |
| caché | un valor guardado antes | el valor de ahora |

### Lo que YA existe de L−2, resuelto de a uno en Python

No es terreno virgen, y ése es el mejor argumento de que el nivel es real:

- **`nucleo/fixtures.py`** — cada fixture diferencial lleva `frescura.huellas` con cuatro SHA-256
  (`emisor`, `referencia`, `catalogo`, `configuracion`) y se declara vencido cuando alguna cambió:
  `fixture vencido: cambió referencia (fd9fca09… → 9a79cad1…)`. Es exactamente una pregunta de L−2,
  contestada a mano para un solo caso de uso.
- **`proceso.verificacion_vigente`** — un verde con código vivo tocado ya no vale. Y su `alcance`
  confiesa el hueco: *«NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio
  vivo la invalida. Hace falta comparar contra el commit de la verificación»*.
- **`origen: {repo, commit}`** en cada caso del corpus — la declaración de referente ya está, y
  **nadie la verifica**: 42 de 112 casos apuntan a un commit que existe, el resto dice prosa.

### La forma que propongo

Que **la evidencia declare su referente y su huella**, por relación y no por fila: una relación la
llena un sensor leyendo un conjunto de referentes, y ésa es la unidad natural.

```
evidencia:
    pieza: id, alto
        "a", 180
    referente de pieza:
        que:    "Content/Props/silla.uasset"
        huella: "sha256:9a79cad14237…"
        cuando: "2026-08-27T09:14:00"
```

### El límite que hay que declarar antes de escribir una línea

**Oracle no puede verificar un referente, nunca.** No sabe abrir un `.uasset`, ni debe. Lo único que
puede hacer es **comparar dos declaraciones hechas en momentos distintos** — que es, exactamente, lo
que `fixtures.py` ya hace. Recalcular la huella es trabajo del sensor.

Eso fija el `alcance` de todo lo que se escriba en este nivel, y conviene escribirlo antes de
empezar para no descubrirlo tarde:

> NO verifica que el referente exista, ni que la huella corresponda a él, ni que quien la escribió
> haya leído algo. Compara la huella declarada al leer contra la declarada ahora.

Es el mismo límite que ya tiene `procedencia`, un nivel más arriba, y por el mismo motivo: **debajo
está el terreno.**

### Cómo se sabría que está terminado

Poder escribir, en el lenguaje y sin tocar Python:

- «ninguna evidencia se juzga contra un referente que cambió después de leerla»;
- «ninguna evidencia declara un referente sin huella»;
- y, la que hoy sólo existe como prosa dentro de un `alcance`:
  «ninguna verificación vigente se apoya en un commit anterior al último cambio vivo».

Y que **`nucleo/fixtures.py` deje de tener su propio mecanismo de frescura** y use éste. Mientras el
fixture diferencial siga comparando huellas por su cuenta, L−2 está a medias: sería una capa nueva
al lado de la vieja en vez de la vieja expresada en el lenguaje.

### Resultado medido el 2026-08-28

`referente_declarado` hace observable la identidad, huella y momento de lectura;
`referente_comparado` empareja por identidad las declaraciones de lectura y actualidad, sin decidir
si coinciden. La decisión está escrita en
`meta.ninguna_evidencia_se_juzga_con_referente_vencido` como
`r.huella_leida != r.huella_actual`. La misma relación alcanza para el commit de una verificación:
el sensor de proceso tiene que presentarlo como otra identidad, no hace falta otro campo ni otro
comparador Python.

`nucleo.diferencial.py` quedó como sensor que calcula huellas. `nucleo/fixtures.py` las presenta a
la medida y usa sus testigos para el diagnóstico `fixture vencido: cambió …`; ya no compara huellas
por su cuenta. La prueba diferencial conservó sus 4 acuerdos globales y 12 veredictos individuales.

La pregunta de si L−2 colapsaba dentro de L−1 queda respondida por la implementación: las
declaraciones de unidad y de referente se producen y se miden por separado. Son dos niveles.

### La pregunta abierta, que se resuelve construyendo

`DECISION-005` la deja anotada y sigue abierta: **¿es L−2 un nivel debajo de L−1, o un parámetro
suyo?** «A qué le apuntaste» podría ser parte de la declaración del sensor. Se eligió separarlos
porque los dos modos de falla son independientes —un sensor perfectamente declarado puede apuntar al
archivo equivocado—, pero si al construirlo resulta que nunca se declaran por separado, entonces era
uno solo y se colapsan.

---

## El orden, y por qué

L−1 primero. Un referente sin saber qué se leyó de él no dice nada útil: la huella de un archivo
importa **porque** el sensor declara que de ahí saca el campo `alto` en centímetros. Al revés no se
sostiene.

Y hay un tercer trabajo, en curso, que habilita a los dos: la superficie tiene hoy **una rama de
parseo y de impresión escrita a mano por cada forma** en `nucleo/sintaxis.py`. Mientras siga así,
cada declaración nueva —de relación, de referente— cuesta una edición del núcleo. Sería el mismo
mecanismo propio por cuarta vez.
