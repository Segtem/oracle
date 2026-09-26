# Recetas de medidas

Esta página reúne dos patrones frecuentes al escribir medidas en Oracle que resuelven problemas del
álgebra y de la mutación sin necesidad de operadores nuevos:

1. **Pares no orientados sin contarlos dos veces**: por qué usar `<` en lugar de `!=` al unir una
   relación consigo misma, para no inflar el conteo de testigos y permitir que la mutación compruebe
   el umbral.
2. **Contar distintos por grupo con doble `agrupar`**: cómo calcular un recuento de valores
   distintos (`DISTINCT`) agrupados por clave, colapsando filas repetidas sin un agregador especial.

No hay ninguna salida inventada: la suite del repositorio arma el proyecto de esta página desde una
carpeta vacía, corre cada comando y comprueba lo que ves acá.

## El proyecto de ejemplo

Arrancamos desde una carpeta limpia e inicializamos el proyecto. Desactivamos el catálogo base en
`oracle.json` para concentrarnos exclusivamente en las dos reglas de dominio:

```bash paso
oracle init .
```

```text salida
Proyecto Oracle inicializado en .:
  · catalogos/
  · corpus/
  · diferencial/
  · relaciones/
  · oracle.json

Próximos pasos:
  1. Creá un caso:     oracle caso <grupo/id>
  2. Creá una medida:  oracle nueva <dominio.nombre>
  3. Verificá todo:    oracle test
```

```json archivo=oracle.json incluir=ejemplo/recetas/oracle.json
```

---

## 1. Pares no orientados: la clave ordenable `<`

### El problema: `!=` infla el conteo y deja vivos mutantes

Al comparar elementos de una misma relación entre sí para detectar colisiones o incompatibilidades
—por ejemplo, dos servicios que reclaman el mismo puerto de red, dos barcos superpuestos o dos
reuniones encimadas en la misma sala—, la intuición suele llevar a una auto-unión con desigualdad:

```oracle
de servicio a
unir servicio b
donde a.nombre != b.nombre y a.puerto == b.puerto
```

El problema no se nota al juzgar, pero **rompe la mutación de medidas**:

- Si el servicio `api` y el servicio `web` comparten el puerto 8080, la unión produce **dos**
  filas de testigos: `(api, web)` y `(web, api)`.
- El valor mínimo de una colisión es **2**.
- Cuando `oracle test` ataca la medida con el mutador `aflojar_umbral` (sustituyendo el umbral
  `<= 0` por `<= 1`), el defecto sigue teniendo valor 2, que es `> 1`: el mutante sigue dando ROJO.
- El mutante se comporta igual que la medida original sobre el caso de prueba, por lo que
  **sobrevive** y la verificación falla.

### La solución: imponer orden con `<`

Si la clave es ordenable (un identificador alfanumérico, un timestamp o un número de secuencia),
reemplazar `!=` por `<` impone una orientación estricta:

```oracle
de servicio a
unir servicio b
donde a.nombre < b.nombre y a.puerto == b.puerto
```

- El par no orientado `{api, web}` se evalúa una sola vez: `"api" < "web"` es verdadero, mientras
  que `"web" < "api"` es falso.
- El valor de la colisión es exactamente **1**.
- Ante el mutador `aflojar_umbral` (`<= 1`), el valor 1 ahora pasa en verde (`1 <= 1`).
- La inversión de veredicto sobre el caso rojo **mata al mutante**.

### La medida copiable

```oracle archivo=catalogos/red/red.puerto_exclusivo.oracle incluir=ejemplo/recetas/catalogos/red/red.puerto_exclusivo.oracle
```

### Los casos: rojo y verde

Un caso rojo que presenta dos servicios en colisión y espera que la regla lo atrape:

```caso archivo=corpus/red/001-puerto-duplicado.caso incluir=ejemplo/recetas/corpus/red/001-puerto-duplicado.caso
```

Y un caso verde donde cada servicio tiene su propio puerto:

```caso archivo=corpus/red/002-puertos-distintos.caso incluir=ejemplo/recetas/corpus/red/002-puertos-distintos.caso
```

---

## 2. Contar distintos por grupo: doble `agrupar`

### El problema: no existe `contar_distintos`

El álgebra de Oracle no incluye un agregado `contar_distintos` ni una función escalar `distinto()`.
Esta omisión es deliberada: el núcleo no incorpora operadores hasta que al menos dos medidas
independientes lo requieran como primitiva irreducible.

Además, en evidencia real (métricas de réplicas, trazas de auditoría o eventos de despliegue),
una relación suele traer filas repetidas con la misma clave. Un simple `contar(1)` contaría filas
totales, inflando la cuenta con eventos duplicados en lugar de medir entidades distintas.

### La solución: encadenar dos pasos `agrupar`

El álgebra relacional de Oracle permite encadenar pasos `agrupar`. Cada uno cumple un rol:

1. **Primer `agrupar` (deduplicar)**: Se agrupa por la clave del grupo (`d.nodo`) **y** por la clave
   del elemento (`d.servicio`), sin declarar agregados. En Oracle, un `agrupar:` sin agregados
   colapsa todas las filas idénticas en una sola por combinación de claves (equivalente a un
   `DISTINCT`).
2. **Segundo `agrupar` (contar)**: Se agrupa únicamente por la clave del grupo (`nodo`), calculando
   `agregado distintos = contar(1)`. Dado que el paso previo dejó una fila por elemento único, este
   conteo refleja con exactitud la cantidad de elementos distintos por grupo.
3. **Filtro y umbral**: Con `donde distintos > 2` se aíslan los grupos que superan la cota permitida,
   y `resumen contar(1)` totaliza las infracciones.

### La medida copiable

En este ejemplo, la regla exige que ningún nodo del clúster aloje más de dos tipos de servicios
distintos:

```oracle archivo=catalogos/red/red.servicios_por_nodo.oracle incluir=ejemplo/recetas/catalogos/red/red.servicios_por_nodo.oracle
```

### Los casos: rojo y verde

Un caso rojo con filas repetidas donde un nodo aloja tres servicios distintos (`web`, `api`, `db`),
violando el límite:

```caso archivo=corpus/red/003-nodo-con-tres-servicios.caso incluir=ejemplo/recetas/corpus/red/003-nodo-con-tres-servicios.caso
```

Y un caso verde con réplicas duplicadas que confirman que las repeticiones no inflan la cuenta de
distintos:

```caso archivo=corpus/red/004-nodo-dentro-del-limite.caso incluir=ejemplo/recetas/corpus/red/004-nodo-dentro-del-limite.caso
```

---

## 3. Verificación con `oracle test`

Con ambas medidas y sus cuatro casos en el proyecto, ejecutamos la verificación completa:

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 4 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 2 medidas · 0 macros · 4 casos

catálogo: 2 medidas · corpus: 4 casos

  ROJO  001-puerto-duplicado                   red.puerto_exclusivo  (valor 1)
  verde 002-puertos-distintos                  red.puerto_exclusivo  (valor 0)
  ROJO  003-nodo-con-tres-servicios            red.servicios_por_nodo  (valor 1)
  verde 004-nodo-dentro-del-limite             red.servicios_por_nodo  (valor 0)

defectos que se pusieron rojos: 2 · verdes correctos: 2 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 2 defectos en rojo, 0 sin evidencia esperada, 2 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 30 · murieron 30 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 24 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 6 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 60

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```

Tanto la sintaxis como el corpus y la aceptación pasan en verde. Además, la suite de mutación ejecuta
los 30 mutadores del motor: los 30 mueren y ninguno sobrevive, demostrando que ambos patrones fijan
estrictamente el comportamiento esperado sin relajar el rigor del catálogo.
