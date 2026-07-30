# Corpus

Casos donde **la medición dijo bien y no estaba bien** — o al revés. Son datos, no anécdotas: cada
caso trae la evidencia en forma de relaciones, así que se puede volver a juzgar cuando exista el
evaluador.

El corpus es el **criterio de aceptación** del resto del repositorio: cuando haya medidas, cada caso
tiene que ponerse en rojo. El que quede verde señala lenguaje faltante o medida faltante, y hay que
decir cuál.

```bash
python tools/corpus.py --resumen
```

## De dónde salen estos 11

Todos de una sola sesión de trabajo, el 2026-07-29, construyendo el plugin
[Jam](https://github.com/Brianholl/jam) con un LLM. Se capturaron **el mismo día en que ocurrieron y
antes de existir nada que los midiera**, por dos motivos: un LLM no recuerda sus fallas entre
sesiones, y un corpus escrito después del framework se escribe para que pase.

## Lo que dicen los números

```
8 de 11   falsos verdes            el modo de falla dominante, con diferencia
4         los vio una persona
3         los atrapó la MUTACIÓN   ← el único mecanismo sistemático que atrapó algo
3         aparecieron de casualidad haciendo otra cosa
1         lo detectó una herramienta ajena (un parser que no pudo leer el archivo)
```

**Ningún caso lo atrapó un verificador propio por diseño.** Ésa es la medición que justifica este
repositorio: el proyecto tenía 489 tests en verde, un verificador de documentación y un verificador
de entrega, y los 11 defectos pasaron por el costado.

Y explica por qué la primera medida a escribir es `proceso.test_con_mutante_que_lo_mata`: la
mutación es el único detector que ya se pagó solo, y tres casos la reclaman.

## Esquema de un caso

| Campo | Qué es |
|---|---|
| `id` | igual al nombre del archivo |
| `fecha`, `origen` | procedencia: repo y commit donde ocurrió |
| `titulo` | una línea |
| `etiqueta` | `falso_verde` · `falso_rojo` · `deuda_de_diseño` · `medida_correcta_conclusion_errada` |
| `sintoma` | qué dijo la medición y qué era verdad |
| `como_se_detecto` | `mutacion` · `persona` · `accidente` · `herramienta_ajena` |
| `medida` | la regla que debería atraparlo, o `null` |
| `estado_sin_medida` | si `medida` es null: `abierto`, `resuelto` o `limite_humano` |
| `sin_medida_todavia` | obligatorio sólo para un estado `abierto` |
| `resuelto` / `limite_humano` | cierre por construcción o frontera que requiere juicio humano |
| `evidencia` | mapa de relación → filas de campos **escalares** (el contrato L0) |
| `leccion` | qué se aprende, en una o dos frases |

El estado explícito evita mezclar deuda abierta con memoria de diseño o con una frontera humana. Hoy
no hay huecos abiertos: `004` y `012` están resueltos por construcción; `011` conserva el límite de
una atribución causal que una herramienta genérica no puede validar.


## Cómo se agrega un caso

Cuando una medición diga bien y no lo esté: un JSON acá, con la evidencia mínima que una medida
necesitaría para atraparlo. **No hace falta que la medida exista** — de hecho es mejor que no exista,
porque así el caso define la medida y no al revés.
