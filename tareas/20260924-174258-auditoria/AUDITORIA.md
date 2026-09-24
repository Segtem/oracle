# Auditoría de oracle-metalenguaje — 2026-09-24

Estado auditado: `main` en 0.30.0 sin publicar (álgebra 0.8, sintaxis 0.7). Todas las cifras de acá
se midieron ese día en el árbol o salen de tareas cerradas que se citan. Donde algo es opinión, lo
digo.

## Veredicto en una línea

**El rigor de ingeniería está muy por encima de lo que se espera de un proyecto de dos meses y un
autor. La madurez de producto, en cambio, está por debajo:** la validación de Oracle es sobre todo
interna, cuesta entrar, el lenguaje todavía tiene un falso verde conocido y quedan partes de la
herramienta sin mutar.

## 1. Qué está a un nivel alto

| Aspecto | Evidencia |
|---|---|
| **Se verifica a sí mismo en serio** | 2440 tests; 1010/1010 mutantes de medida; mutación de código de lo tocado en cada corte con 0 vivos (0.29.0: `sintaxis` 1140/1140, `cli` 595/595, `mcp` 363/363…); 9 equivalentes declarados con su razón en todo el árbol. Pocos proyectos mutan su propio código en cada release. |
| **Honestidad del veredicto** | `alcance` y `porque` son obligatorios; `SIN MIRAR`, `NO SE APLICARON`, `SIN EVIDENCIA`, `SIN MEDICIÓN`, sombras con cota. Es lo más distintivo del proyecto: casi ninguna herramienta de verificación declara lo que no miró. |
| **Especificación con versiones que significan algo** | álgebra, sintaxis y distribución versionadas por separado, con reglas de qué sube cada una (§0). La implementación de referencia y el diferencial fallan si se desfasan. |
| **Validación por tercer autor** | La implementación de Codex a ciegas (tarea `codex`) encontró tres huecos de la especificación y un defecto de la referencia. Eso es lo que hace un estándar serio, y está hecho. |
| **Cero dependencias y aislamiento** | `dependencies = []`; las escalares del proyecto corren en un proceso aislado sin red, sin escritura fuera y sin procesos hijos. |
| **Decisiones escritas** | 12 decisiones con fecha y estado, y un test que falla si se cita una que no existe. |
| **Ritmo con control** | 634 commits y 30 cortes desde el 2026-07-29, cada uno con notas, crónica y verificación. |

## 2. Dónde flaquea, ordenado por impacto

### 2.1 El falso verde conocido del álgebra (impacto alto, costo bajo, decisión MAYOR)

`predicado-bool` sigue abierta desde el 2026-09-16: en `donde`, `sin` y `requiere`, un predicado
que no es booleano se evalúa por verdad de Python. Un 2 pasa y un 0 no, así que un campo numérico
usado por error como condición filtra sin avisar. Es exactamente el tipo de falso verde que el
proyecto existe para impedir, y la referencia ya lo trata como error. Cambiarlo sube la **mayor**
del álgebra: es la decisión natural para 1.0. **Recomendación:** medir en Oracle, Jam y LyraGASP
cuántas medidas dependen de la coerción (probablemente cero o casi), exigir `bool` y cortar álgebra
1.0 con eso.

### 2.2 Validación externa: casi nula (impacto alto, costo medio)

Los consumidores son el propio autor (Jam, LyraGASP, commander). Además, su evidencia es mayormente
sintética: Jam tiene 16 medidas y LyraGASP 17 que dependen sólo de evidencia construida (tarea
`evidencia-real` de Jam), y cargan deuda en sombra: 51/61 comparaciones sin unidad derivable y
41/27 umbrales sin procedencia. El catálogo es coherente, pero eso no prueba que el mundo esté bien.
El único experimento externo, la batalla naval hecha por agy, terminó con un verde que no medía nada
(`vault-kb/postmortems/`). **Recomendación:** dos o tres pilotos con alguien que no sea el autor y
sobre un dominio que no sea de juegos, midiendo el tiempo hasta la primera medida roja real. Y en
los consumidores, bajar la evidencia sintética antes de sumar medidas nuevas.

### 2.3 El costo de entrada (impacto alto, costo medio)

- Hay cinco caminos para empezar que se pisan entre sí: `docs/02-de-cero-a-un-rojo.md`,
  `docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`, `docs/tutorial-practico.md` y
  `docs/de-cero.html`. A eso se suma un README de 868 líneas y 23 verbos en la CLI.
- El postmortem naval midió que el ritual (instalar, `init`, tareas, casos, `oracle test`) se come
  la atención de un agente, y que el resultado puede ser un catálogo vacío en verde. 0.28 lo mitigó
  con `SIN MEDICIÓN` y el primer valor, pero el recorrido sigue siendo largo.
- **Recomendación:** un solo camino de entrada, el de `de-cero-naval` (pedagógico, de a un paso y
  verificado por un test), y los otros cuatro reducidos a referencia. Más un `oracle nueva` que
  arme de una vez la medida junto con su caso rojo y su caso verde. Hoy son pasos separados, y un
  agente se saltea el caso.

### 2.4 El lenguaje todavía pide rodeos (impacto medio, costo bajo a medio)

El inventario de fricciones (`ergonomia/VERIFICACION.md`) tiene 10 ciertas; 0.29 y 0.30 resolvieron
cuatro (orden de `requiere`, confianza, observados y aritmética). Quedan, entre otras:

- **contar distintos por grupo**, que hoy exige un doble `agrupar` (2.1 del inventario);
- **una relación vacía en `.caso`**, que hoy no se puede escribir;
- `/`: no existe, y es lo primero que un LLM escribe para una proporción.

La regla del proyecto («no se agrega un operador hasta que una segunda medida lo necesite») es
buena; conviene aplicarla midiendo los catálogos de los consumidores, no esperando a que alguien
se queje.

### 2.5 Partes de la herramienta que nunca se mutan (impacto medio, costo bajo)

En los cortes 0.29.0 y 0.30.0, el perfil de mutación rechazó como objetivo `tools/mcp_contrato.py`,
`tools/mutar_codigo.py`, `tools/plantilla.py`, `tools/verificar_instalacion.py`, `tools/estudio.py` y
`tools/mutar.py`. Que el arnés de mutación (`mutar_codigo.py`, `mutar.py`) no se mute a sí mismo es la
grieta más irónica del proyecto. **Recomendación:** declarar el perfil explícitamente (qué entra, qué
no y por qué) y hacer que `oracle test --todo` informe el porcentaje de `nucleo/` y `tools/` que
queda fuera, igual que una medida declara su alcance.

### 2.6 La herramienta creció más que el lenguaje (impacto medio, costo alto)

`tools/` tiene 16 415 líneas y `nucleo/` 10 848. El tracker (`tareas.py`, `tareas_contexto.py`,
`tareas_hechos.py`) y el MCP (1962 líneas) son subsistemas grandes dentro de un paquete que se
presenta como un metalenguaje. El refactor de 0.29 borró 132 líneas duplicadas, pero la tendencia
sigue. *Opinión:* el tracker vale como banco de prueba de Oracle, porque se juzga con sus propias
medidas. Aun así, conviene decidir si es parte del producto o un consumidor que vive en el mismo
repo, antes de que la API pública lo fije.

### 2.7 Liberar es lento (impacto medio, costo medio)

Mutar lo tocado en un corte lleva horas (sólo `nucleo/sintaxis.py` tarda cerca de dos) y ya hubo
cortes por memoria. **Recomendación:** mutación incremental, sólo las líneas cambiadas desde el
último tag, con la corrida completa reservada para el `--todo` nocturno. Eso bajaría el costo de
cada corte sin bajar el criterio.

### 2.8 El idioma (impacto alto a largo plazo, costo alto)

Las palabras clave y los mensajes están en español (`de`, `donde`, `umbral`, `alcance`). Para el
autor y para quien lo usa hoy es una virtud, pero es la barrera más grande a la adopción externa. La
tarea `idioma` (léxicos intercambiables) está bien pensada y bien ubicada: va antes de 1.0, pero
después de 2.1 y 2.2.

### 2.9 Detalles de distribución (impacto bajo, costo bajo)

- `oracle-estudio` instalado desde PyPI no funciona (tarea `estudio-instalado`).
- La página de PyPI de versiones anteriores enlaza rutas que se movieron.
- `NOTAS-DE-RELEASE.md` tiene 3169 líneas; conviene un índice o partirlo por versión mayor.

## 3. Cómo se ubica frente a lo que existe (opinión)

Por su forma, Oracle se parece a un lenguaje de políticas (Rego/OPA) o a Datalog sobre relaciones de
hechos. Lo que ninguno de esos trae de fábrica, y Oracle sí, es esto:

- la obligación de declarar el alcance y la procedencia del umbral;
- un corpus con las dos polaridades por medida;
- la mutación de las medidas mismas;
- veredictos que dicen qué no miraron.

Ése es el diferencial y conviene decirlo así en la web. La contracara es que un lenguaje de políticas
maduro trae ecosistema, un lenguaje en inglés y herramientas que Oracle no tiene.

## 4. Qué haría, en orden

1. **Álgebra 1.0 con `predicado-bool`**: medir el impacto, exigir `bool` y cortar. Cierra el único
   falso verde conocido.
2. **Una sola entrada**: `de-cero-naval` como camino, los demás a referencia, y un `oracle nueva`
   que cree la medida junto con sus dos casos.
3. **Perfil de mutación declarado y reportado**, empezando por mutar el propio arnés.
4. **Dos pilotos externos**, medidos por el tiempo hasta el primer rojo real.
5. **Menos evidencia sintética en Jam y LyraGASP** antes de medidas nuevas.
6. **Mutación incremental** para cortar más seguido.
7. **`idioma`**, después.
