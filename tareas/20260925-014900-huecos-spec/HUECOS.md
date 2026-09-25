# Preguntas sin contestar en ESPECIFICACION.md (álgebra 0.8)

Este documento registra los huecos de especificación identificados al leer [`ESPECIFICACION.md`](../../ESPECIFICACION.md) desde la perspectiva de una implementación independiente, contrastando el texto con la implementación del núcleo ([`nucleo/algebra.py`](../../nucleo/algebra.py), [`nucleo/medida.py`](../../nucleo/medida.py)) y la implementación de referencia independiente ([`diferencial/referencia/evaluador.py`](../../diferencial/referencia/evaluador.py), [`diferencial/referencia/DECISIONES.md`](../../diferencial/referencia/DECISIONES.md)).

Siguiendo el criterio fijado en [`TAREA.md`](../../tareas/20260925-014900-huecos-spec/TAREA.md):
- **Especificación incompleta**: puntos donde `ESPECIFICACION.md` deja el margen abierto pero el núcleo y la referencia resuelven igual. Se incorporan a la especificación con lo que ya hacen.
- **Defectos**: puntos donde el núcleo y la referencia resuelven de forma distinta ante la ambigüedad o silencio de `ESPECIFICACION.md`.
- **Decisiones de Brian**: puntos que ninguno resuelve o requieren definición de diseño exterior.

---

## 1. Especificación incompleta (núcleo y referencia resuelven igual)

### 1.1. Evaluación de operadores lógicos `y` y `o` sin cortocircuito
- **Pregunta sin contestar:** ¿Los operadores lógicos `y` y `o` cortocircuitan al encontrar un operando determinante (como `False` en `y` o `True` en `o`), o evalúan obligatoriamente todos sus operandos?
- **Párrafo en `ESPECIFICACION.md`:** §3, líneas 848-852. Menciona que comparar contra un campo ausente levanta error (líneas 848-849) y que `y`/`o` aceptan dos o más operandos (línea 851), pero omite explicitar la ausencia de cortocircuito en expresiones lógicas generales (sólo lo detalla para `requiere` en §2:716 y para `sin` en §3:826).
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L530-L546`](../../nucleo/algebra.py#L530-L546), `_evaluar_expr` evalúa todos los operandos antes de aplicar `all()` o `any()`, con el comentario explícito: *"SIN cortocircuito, y es deliberado... `["y", <falso>, ["==", ["campo","a","typo"], 1]]` no llegaba nunca a mirar el campo inexistente y devolvía un `False` silencioso"*.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L624-L632`](../../diferencial/referencia/evaluador.py#L624-L632), evalúa todos los argumentos en una lista por comprensión antes de computar el resultado; documentado en [`diferencial/referencia/DECISIONES.md#L57-L63`](../../diferencial/referencia/DECISIONES.md#L57-L63).
- **Resolución:** Escribir en §3 de la especificación que `y` y `o` evalúan todos sus operandos sin cortocircuito para evitar silenciar errores en ramas no determinantes.

### 1.2. Existencia y aridad del operador lógico `no`
- **Pregunta sin contestar:** ¿Existe el operador de negación lógica `no` y cuál es su aridad?
- **Párrafo en `ESPECIFICACION.md`:** §3, líneas 843-859. En la subsección "Acceso a los datos" sólo se nombran `y` y `o` (línea 851); el operador `no` no figura en §3 ni en su tabla (sólo se nombra de paso en §2:762 como parte del inventario de mutaciones).
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L386`](../../nucleo/algebra.py#L386) declara `LOGICOS = ("y", "o", "no")`; en [`nucleo/algebra.py#L450-L452`](../../nucleo/algebra.py#L450-L452) exige aridad exacta 1 (`len(expr) == 2`); en [`nucleo/algebra.py#L547-L548`](../../nucleo/algebra.py#L547-L548) evalúa `not _evaluar_hijo(expr, 1, fila, escalares)`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L633-L639`](../../diferencial/referencia/evaluador.py#L633-L639), valida aridad 1 y evalúa la negación lógica.
- **Resolución:** Incorporar `no` formalmente en §3 como operador lógico unario de la forma `["no", expr]`.

### 1.3. Relación ausente de la evidencia en `requiere`
- **Pregunta sin contestar:** Si una relación requerida en `requiere` no figura en el mapa de evidencia recibido (ausencia de clave, en lugar de estar presente como `[]`), ¿es un `ErrorDeAlgebra` o equivale a ausencia de evidencia devolviendo `SIN EVIDENCIA`?
- **Párrafo en `ESPECIFICACION.md`:** §2, líneas 688-692. Dice: *"Si alguna de las relaciones listadas viene vacía, la evaluación no mide: devuelve SIN EVIDENCIA"*, pero no aclara qué ocurre si la relación directamente no está en el diccionario provisto.
- **Qué hace `nucleo/`:** En [`nucleo/medida.py#L482-L483`](../../nucleo/medida.py#L482-L483), `evidencia.get(entrada)` devuelve `None` si la relación no existe en el dict; `not bool(None)` se evalúa como vacía y emite `sin_evidencia`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L191-L196`](../../diferencial/referencia/evaluador.py#L191-L196), `evidencia.get(req.relacion)` trata la clave ausente idénticamente a `[]`; documentado en [`diferencial/referencia/DECISIONES.md#L81-L88`](../../diferencial/referencia/DECISIONES.md#L81-L88): *"para requiere, una relacion ausente equivale a una relacion vacia y devuelve SIN EVIDENCIA. Para ['de', relacion, alias], una relacion ausente sigue siendo error de algebra"*.
- **Resolución:** Escribir en §2 que para `requiere`, una relación omitida en el mapa de evidencia equivale a una relación vacía y emite `SIN EVIDENCIA`.

### 1.4. Comportamiento de `agrupar` sobre cero filas de entrada
- **Pregunta sin contestar:** Si `agrupar` recibe 0 filas de entrada, ¿produce 0 filas resultantes o produce una fila con valores agregados por omisión (en 0), especialmente cuando la lista de claves de agrupación está vacía?
- **Párrafo en `ESPECIFICACION.md`:** §3, líneas 795-796 y §8, líneas 988-1007. §3 dice que *"Los agregados sobre cero filas dan 0"*, pero no aclara si `agrupar` emite o no grupos cuando no entran filas.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L820-L839`](../../nucleo/algebra.py#L820-L839), `_agrupar` agrupa iterando sobre `filas`; si `filas` está vacía, no se crea ningún grupo y retorna `salida = []`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L474-L497`](../../diferencial/referencia/evaluador.py#L474-L497), retorna `[]`; documentado en [`diferencial/referencia/DECISIONES.md#L33-L40`](../../diferencial/referencia/DECISIONES.md#L33-L40): *"si agrupar recibe cero filas, produce cero grupos. Por lo tanto no emite una fila artificial con agregados en 0, aun si la lista de claves esta vacia"*.
- **Resolución:** Escribir en §3 que `agrupar` sobre cero filas de entrada produce cero filas de salida, sin filas sintéticas.

### 1.5. Ubicación de `resumen` respecto a `desde`
- **Pregunta sin contestar:** La tabla de §3 lista `resumen` junto con los demás operadores de relación (`de`, `donde`, `unir`, `sin`, `agrupar`). ¿Puede `resumen` figurar como un paso interno dentro de la tubería `desde`?
- **Párrafo en `ESPECIFICACION.md`:** §3, líneas 776-778, 792, 800. Dice que colapsa a un escalar y por eso va último, pero la tabla lo incluye como uno de los operadores activos.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L903-L953`](../../nucleo/algebra.py#L903-L953), `_validar_paso` rechaza cualquier paso con operador `resumen` con `ErrorDeAlgebra("operador desconocido: «resumen»")`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L317, L351-L352`](../../diferencial/referencia/evaluador.py#L317), levanta `ErrorDeAlgebra("resumen no es un paso valido de desde")`; documentado en [`diferencial/referencia/DECISIONES.md#L41-L48`](../../diferencial/referencia/DECISIONES.md#L41-L48).
- **Resolución:** Aclarar en §3 que `resumen` sólo es válido en el nodo de nivel superior `["resumen", agg, expr]` de la medida y nunca como paso dentro de `desde`.

### 1.6. Restricción posicional de `sin` en la tubería
- **Pregunta sin contestar:** ¿Puede `sin` figurar como la fuente inicial de una tubería `desde` (`["desde", ["sin", ...], ...]`) o como operando de `unir`?
- **Párrafo en `ESPECIFICACION.md`:** §3, línea 818. Dice: *"sin es un paso de la tubería, como donde"*, pero no aclara taxativamente si está prohibido en posiciones de fuente relacional.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L882-L901`](../../nucleo/algebra.py#L882-L901), `_validar_fuente` solo admite `de` y `unir`. En [`nucleo/algebra.py#L911-L922`](../../nucleo/algebra.py#L911-L922), `_validar_paso` lo admite únicamente como paso subsiguiente en `desde`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L349-L350`](../../diferencial/referencia/evaluador.py#L349-L350), `_evaluar_relacion` levanta `ErrorDeAlgebra("sin solo puede aparecer como paso de desde")`; documentado en [`diferencial/referencia/DECISIONES.md#L162-L167`](../../diferencial/referencia/DECISIONES.md#L162-L167).
- **Resolución:** Escribir en §3 que `sin` sólo puede figurar a partir del segundo elemento de `desde` y nunca como fuente primaria ni dentro de `unir`.

### 1.7. Vocabulario cerrado admisible en `ambito`
- **Pregunta sin contestar:** ¿Cuáles son los valores textuales permitidos para el nodo opcional `ambito`?
- **Párrafo en `ESPECIFICACION.md`:** §2, líneas 677-686. El texto muestra `["ambito", "del_origen"]` pero no enumera los valores válidos en la definición de la medida (sólo se mencionan de pasada `universal` y `sin_declarar` en §0).
- **Qué hace `nucleo/`:** En [`nucleo/medida.py#L411-L420`](../../nucleo/medida.py#L411-L420) valida contra `AMBITOS = ("universal", "del_origen")` o `AMBITO_SIN_DECLARAR = "sin_declarar"`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L18, L173-L180`](../../diferencial/referencia/evaluador.py#L18), define `_AMBITOS = {"sin_declarar", "universal", "del_origen"}` y rechaza cualquier otro valor.
- **Resolución:** Listar explícitamente en §2 los tres valores reconocidos para `ambito`: `"universal"`, `"del_origen"` y `"sin_declarar"`.

### 1.8. Cero claves en `agrupar`
- **Pregunta sin contestar:** ¿El álgebra admite `agrupar` con una lista vacía de claves (`["agrupar", [], agregados]`)?
- **Párrafo en `ESPECIFICACION.md`:** §3, línea 792. La tabla muestra `[claves]` sin especificar cardinalidad mínima; en §0:320 se menciona en la crónica que *"cero claves se aceptó siempre"*, pero §3 no lo formaliza.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L932-L935`](../../nucleo/algebra.py#L932-L935), comprueba que `claves` sea `list` y que sus elementos sean listas de 2 elementos; una lista vacía cumple y colapsa toda la relación en un solo grupo global.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L500-L512`](../../diferencial/referencia/evaluador.py#L500-L512), `_parsear_claves` acepta `claves == []`.
- **Resolución:** Establecer en §3 que `claves` en `agrupar` puede ser una lista vacía `[]`, agrupando la totalidad de las filas recibidas.

---

## 2. Defectos (núcleo y referencia resuelven distinto)

### 2.1. Comparador `!=` sobre números flotantes
- **Párrafo en `ESPECIFICACION.md`:** §8, líneas 1037-1053 ("Igualdad de flotantes"). Establece: *"La igualdad exacta sólo tiene sentido sobre cosas que se cuentan o se nombran... y ahí sigue permitida. Sobre cosas que se miden hace falta una tolerancia... Las comparaciones de ORDEN sobre flotantes siguen permitidas: una tolerancia es una comparación de orden."* El texto habla de igualdad exacta (`==`), pero no aclara explícitamente si la desigualdad `!=` está prohibida.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L375-L378`](../../nucleo/algebra.py#L375-L378), `comparar` prohíbe taxativamente TANTO `==` COMO `!=` si cualquiera de los dos operandos es flotante:
  `if op in ("==", "!=") and (_es_flotante(a) or _es_flotante(b)): raise ErrorDeAlgebra(...)`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L702-L708`](../../diferencial/referencia/evaluador.py#L702-L708), prohíbe `==` para flotantes pero **permite** `!=` entre flotantes finitos; documentado en [`diferencial/referencia/DECISIONES.md#L49-L56`](../../diferencial/referencia/DECISIONES.md#L49-L56): *"se prohibe exactamente `["==", a, b]` cuando ambos operandos evaluan a float... `["!=", a, b]` queda permitido si los tipos son compatibles y los floats son finitos"*.
- **Defecto:** Divergencia de contrato en comparaciones flotantes. Si la doctrina prohíbe comprobar igualdad exacta por tolerancias numéricas, `!=` entre flotantes adolece del mismo defecto numérico.

### 2.2. Codificación del valor del veredicto ante `SIN EVIDENCIA`
- **Párrafo en `ESPECIFICACION.md`:** §2, líneas 688-693. Dice: *"devuelve `SIN EVIDENCIA`, que no es verde y tampoco es un rojo del mundo"*, pero no fija el tipo de dato del campo `valor` en la estructura de salida.
- **Qué hace `nucleo/`:** En [`nucleo/medida.py#L235-L250, L493-L495`](../../nucleo/medida.py#L235-L250), `Medida.evaluar` devuelve un dataclass `Veredicto` donde `valor: float = 0`, `ok: bool = False`, y la relación que faltó se almacena en el atributo `sin_evidencia: str`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L74-L80`](../../diferencial/referencia/evaluador.py#L74-L80), `evaluar` retorna un diccionario donde `valor` es la cadena `"SIN EVIDENCIA"` (`"valor": "SIN EVIDENCIA"`), `ok` es `False`, y no existe campo `sin_evidencia`; documentado en [`diferencial/referencia/DECISIONES.md#L72-L80`](../../diferencial/referencia/DECISIONES.md#L72-L80).
- **Defecto:** Incompatibilidad de contrato de API pública. En el núcleo `v.valor` sigue siendo numérico (`0`) y la causa viaja en `v.sin_evidencia`; en la referencia `v["valor"]` muta a string `"SIN EVIDENCIA"`. (Nota: en §6:943-944 el formato de fixture diferencial espera `"valor": "SIN EVIDENCIA"`).

### 2.3. Formato sintáctico de los agregados en `agrupar`
- **Párrafo en `ESPECIFICACION.md`:** Contradicción interna en la propia especificación:
  - En §3, tabla de operadores (línea 792): declara `["agrupar", [claves], [nombre, agg, expr]]` (un solo agregado en lista llana).
  - En §8, ejemplo de ausencia (líneas 996-998): declara `["agrupar", [claves], [[nombre, agg, expr]]] ` (lista de agregados).
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L936-L939`](../../nucleo/algebra.py#L936-L939), `_validar_paso` exige estrictamente que cada elemento dentro de `paso[2]` sea una lista de longitud 3 (`isinstance(agg, list) and len(agg) == 3`). Si se pasa la forma de la tabla de §3 (`["agrupar", claves, ["x", "contar", 1]]`), levanta `ErrorDeAlgebra` porque `"x"` no es lista.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L514-L533`](../../diferencial/referencia/evaluador.py#L514-L533), `_parsear_agregados_grupo` detecta con `_parece_agregado_grupo` si es un agregado individual y lo envuelve en una lista, tolerando ambas sintaxis; documentado en [`diferencial/referencia/DECISIONES.md#L15-L32`](../../diferencial/referencia/DECISIONES.md#L15-L32).
- **Defecto:** La tabla de §3 de `ESPECIFICACION.md` publica una forma que el núcleo rechaza. La referencia tuvo que agregar código de compatibilidad para aceptar lo que la tabla decía.

### 2.4. Semántica de testigos cuando hay pasos posteriores a `donde` (`agrupar` o `sin`)
- **Párrafo en `ESPECIFICACION.md`:** §2, líneas 768-769: *"Los testigos no se declaran. Son las filas que sobrevivieron al último donde."* No especifica qué ocurre si después de un `donde` se ubica un `agrupar` o un `sin`.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L1076, L1104-L1109`](../../nucleo/algebra.py#L1076) y [`nucleo/medida.py#L496`](../../nucleo/medida.py#L496), `desde` no preserva un estado especial para `donde`; simplemente encadena los pasos y retorna las filas finales. Los testigos asignados a `Veredicto` son siempre las filas que salen al final de toda la tubería `desde` (por ejemplo, filas con columnas derivadas `_` si hubo `agrupar`, o filas filtradas por `sin`).
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L303, L310-L312, L321-L323`](../../diferencial/referencia/evaluador.py#L303), `_evaluar_desde` asigna `ultimos_testigos` exclusivamente al ejecutar un paso `donde`. Si después de `donde` ocurre `agrupar` o `sin`, `ultimos_testigos` NO se actualiza y la referencia devuelve las filas del `donde` previo; documentado en [`diferencial/referencia/DECISIONES.md#L5-L14, L192-L197`](../../diferencial/referencia/DECISIONES.md#L5-L14).
- **Defecto:** Desacuerdo en la definición de testigos: el núcleo toma la salida terminal de `desde`, mientras que la referencia congela la foto del último `donde`.

### 2.5. Validación estricta de tipo booleano en predicados (`donde`, `sin`, `y`, `o`, `no`)
- **Párrafo en `ESPECIFICACION.md`:** §3, líneas 789, 818-821, 851. Describe el filtrado de `donde` y `sin`, y los lógicos `y`/`o`, sin especificar si los predicados exigen tipo de dato `bool` estricto o si aplican coerción de verdad (truthiness).
- **Qué hace `nucleo/`:**
  - En [`nucleo/algebra.py#L875`](../../nucleo/algebra.py#L875) (`donde`): `[f for f in filas if evaluar_expr(...)]` usa truthiness de Python.
  - En [`nucleo/algebra.py#L793`](../../nucleo/algebra.py#L793) (`sin`): `if evaluar_expr(...): hubo_coincidencia = True` usa truthiness.
  - En [`nucleo/algebra.py#L546, L548`](../../nucleo/algebra.py#L546) (`y`, `o`, `no`): usa `all()`, `any()` y `not` sobre valores cualesquiera sin validar que sean de tipo `bool`.
- **Qué hace la referencia:**
  - En [`diferencial/referencia/evaluador.py#L402-L404`](../../diferencial/referencia/evaluador.py#L402-L404) (`donde`): `if not isinstance(valor, bool): raise ErrorDeAlgebra("donde espera un predicado booleano")`.
  - En [`diferencial/referencia/evaluador.py#L450-L452`](../../diferencial/referencia/evaluador.py#L450-L452) (`sin`): `if not isinstance(cumple, bool): raise ErrorDeAlgebra("la condicion de sin espera un predicado booleano")`.
  - En [`diferencial/referencia/evaluador.py#L742-L745`](../../diferencial/referencia/evaluador.py#L742-L745) (`y`, `o`): `_validar_booleanos` exige `isinstance(valor, bool)`; para `no` (línea 637) lo mismo.
  - Documentado en [`diferencial/referencia/DECISIONES.md#L186-L191`](../../diferencial/referencia/DECISIONES.md#L186-L191).
- **Defecto:** Divergencia de tipeo dinámico. En el núcleo expresiones no booleanas (como números o cadenas de una función escalar) se evalúan con verdad de Python; en la referencia levantan `ErrorDeAlgebra`.

### 2.6. Momento y alcance de la validación de claves declaradas
- **Párrafo en `ESPECIFICACION.md`:** §1, líneas 544-545: *"La clave es opcional y se valida antes de medir, fail-closed: si dos hechos repiten la clave declarada, la evaluación levanta un error que nombra la clave responsable y la fila que la viola"*. No dice si se validan todas las relaciones del mapa de evidencia o sólo las relaciones que la medida utiliza.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L692-L710`](../../nucleo/algebra.py#L692-L710), `validar_unicidad` se ejecuta de forma perezosa dentro de `_de`. Si la evidencia trae relaciones con claves violadas pero la medida no las usa en su tubería, el núcleo no se entera ni levanta error.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L72, L218-L223, L248-L250`](../../diferencial/referencia/evaluador.py#L72), `_normalizar_evidencia` valida de forma ansiosa todas las claves de todas las relaciones presentes en `evidencia` antes de evaluar la medida; documentado en [`diferencial/referencia/DECISIONES.md#L89-L98`](../../diferencial/referencia/DECISIONES.md#L89-L98): *"se validan todas las claves declaradas en la evidencia recibida antes de medir, incluso si la relacion no aparece en la tuberia"*.
- **Defecto:** Discrepancia fail-closed: la referencia falla ante cualquier clave rota en la evidencia recibida; el núcleo sólo si la relación es consultada por la medida.

### 2.7. Numeración de filas en error de clave de unicidad
- **Párrafo en `ESPECIFICACION.md`:** §1, líneas 544-546: *"si dos hechos repiten la clave declarada, la evaluación levanta un error que nombra la clave responsable y la fila que la viola"*. No define si el índice de fila cuenta o no el nodo cabecera `["clave", ...]`.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L648, L660`](../../nucleo/algebra.py#L648), `separar_clave` descarta el nodo cabecera `hechos[0]` y devuelve `hechos[1:]`. `validar_unicidad` recibe solo los hechos y numera con `enumerate(filas)` desde 0.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L237, L274, L279`](../../diferencial/referencia/evaluador.py#L237), `_validar_clave_unica` suma `comienzo_hechos` (que vale 1 cuando hay nodo clave): `indice = comienzo_hechos + offset`. El primer hecho es reportado como fila 1; documentado en [`diferencial/referencia/DECISIONES.md#L96-L98`](../../diferencial/referencia/DECISIONES.md#L96-L98): *"La fila informada en errores es el indice dentro de la lista JSON de la relacion, contando el nodo clave si existe"*.
- **Defecto:** El mismo hecho duplicado se reporta con índice `0` en el núcleo y con índice `1` en la referencia.

### 2.8. Subexpresiones relacionales admitidas en `unir`
- **Párrafo en `ESPECIFICACION.md`:** §3, línea 790. La tabla lista `["unir", izq, der]` sin detallar si `izq` y `der` pueden ser sub-tuberías `desde` o únicamente fuentes nombradas.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L682, L725-L726`](../../nucleo/algebra.py#L682), define `FUENTES = ("de", "unir")` y en `_unir` valida: `if lado[0] not in FUENTES: raise ErrorDeAlgebra(...)`. Prohíbe cualquier operador distinto de `de` o `unir`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L340-L349`](../../diferencial/referencia/evaluador.py#L340-L349), `_unir` evalúa ambos lados con `_evaluar_relacion`, la cual admite explícitamente `de`, `unir` y sub-tuberías `desde`: `if operador == "desde": filas, _testigos = _evaluar_desde(expr, ...); return filas`.
- **Defecto:** La referencia admite productos cartesianos sobre subconsultas anidadas `desde`; el núcleo lo rechaza fail-closed permitiendo sólo fuentes planas `de` y productos anidados `unir`.

### 2.9. Tratamiento de `None` / `null` como escalar en hechos y expresiones
- **Párrafo en `ESPECIFICACION.md`:** §1, línea 527: *"Sin objetos, sin punteros, sin nulos implícitos."* No explicita si un campo con valor `null` explícito en JSON es un valor escalar válido o si la evidencia debe ser rechazada.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L348-L350, L388`](../../nucleo/algebra.py#L348-L350), `LITERALES_ESCALARES` incluye `type(None)`. `_familia_escalar` mapea `None` a `"ausente"`, y sólo al intentar comparar en `comparar` (línea 362) levanta error de valor ausente.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L12, L602, L748-L753`](../../diferencial/referencia/evaluador.py#L12), define `Scalar = bool | int | float | str`. Al normalizar hechos en la evidencia ([`evaluador.py#L245`](../../diferencial/referencia/evaluador.py#L245)) y al evaluar literales ([`evaluador.py#L602`](../../diferencial/referencia/evaluador.py#L602)), `_validar_escalar` rechaza tajantemente `None` con `ErrorDeAlgebra("... no es escalar")`.
- **Defecto:** Si una evidencia trae `{"campo": null}`, la referencia rechaza inmediatamente la carga; el núcleo lo admite y sólo falla si una expresión intenta comparar contra dicho campo.

### 2.10. Validación del vocabulario del origen de umbral `segun`
- **Párrafo en `ESPECIFICACION.md`:** §0, líneas 18-19: *"La 0.4 hace explícito de dónde sale cada umbral con el campo segun: medición, contrato, convención o tanteo."* En §2, líneas 680-686, no se especifica si el evaluador valida este campo como vocabulario cerrado al evaluar una medida en datos.
- **Qué hace `nucleo/`:** En [`nucleo/medida.py#L381-L387`](../../nucleo/medida.py#L381-L387), valida que `segun` pertenezca a `ORIGENES_DE_UMBRAL` (`"medicion"`, `"contrato"`, `"convencion"`, `"tanteo"`), o sea `"sin_declarar"`.
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L131-L132`](../../diferencial/referencia/evaluador.py#L131-L132), sólo valida que si tiene 5 elementos sea de tipo `str` (`isinstance(umbral[4], str)`), aceptando cualquier valor de texto arbitrario.
- **Defecto:** La referencia no restringe `segun` a los 4 orígenes cerrados del lenguaje.

### 2.11. Nombres y valores por defecto en `LimitesAlgebra`
- **Párrafo en `ESPECIFICACION.md`:** §9, líneas 1064-1068. Menciona que `LimitesAlgebra` acota filas por relación, producto cartesiano y profundidad de expresión con valores por omisión finitos, pero no nombra los campos ni sus números.
- **Qué hace `nucleo/`:** En [`nucleo/algebra.py#L99-L106`](../../nucleo/algebra.py#L99-L106):
  - `filas_por_relacion: int = 100_000`
  - `producto_cartesiano: int = 1_000_000`
  - `profundidad_expresion: int = 64`
  - `expansiones_maximas: int = 16`
- **Qué hace la referencia:** En [`diferencial/referencia/evaluador.py#L44-L46`](../../diferencial/referencia/evaluador.py#L44-L46) y [`diferencial/referencia/DECISIONES.md#L99-L106`](../../diferencial/referencia/DECISIONES.md#L99-L106):
  - `filas_por_relacion: int = 100_000`
  - `filas_materializadas: int = 1_000_000` (nombre distinto: `filas_materializadas` vs `producto_cartesiano`)
  - `profundidad_expr: int = 100` (nombre distinto y valor distinto: 100 vs 64)
- **Defecto:** Divergencia en los identificadores de la estructura pública y en la profundidad máxima por omisión.
