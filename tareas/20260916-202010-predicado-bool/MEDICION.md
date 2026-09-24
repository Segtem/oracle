# Medición de predicados booleanos

Fecha: 2026-09-24. Alcance pedido: medidas de `catalogos/` y `ejemplo/` de Oracle, y catálogos propios de Jam y LyraGASP. No se cambió el lenguaje ni `nucleo/` del checkout. El script copia Oracle a un directorio temporal, instrumenta esa copia y la elimina al terminar.

## Resultado

| Proyecto | Medidas propias | Predicados `donde`/`sin`/`requiere` | Medidas con nodo estático sospechoso | Predicados completos no `bool` observados |
| --- | ---: | ---: | ---: | ---: |
| Oracle `catalogos/` | 59 | 64 | 0 | 0 |
| Oracle `ejemplo/` (tres proyectos y una biblioteca) | 11 | 13 | 0 | 0 |
| Jam `catalogos/` | 41 | 42 | 0 | 0 |
| LyraGASP `catalogos/` | 28 | 28 | 1 | 0 |
| **Total** | **139** | **147** | **1** | **0** |

**Si se exige `type(valor) is bool` al resultado completo de `donde`, `sin` y `requiere`, ninguna medida de estos corpus cambia de color.** No apareció un resultado completo no booleano. Es una conclusión sobre los casos ejecutados; no prueba que toda evidencia futura tenga esos tipos. `requiere` ya exige `bool` al evaluar y valida su forma al cargar.

El único nodo sospechoso está en [personaje.ancla_requerida_ausente.json](LyraGASP medidas/catalogos/personaje/personaje.ancla_requerida_ausente.json:38): `['campo', 'a', 'presente']` es operando de `no` dentro de `donde`. La instrumentación observó **10 evaluaciones con `None` (`NoneType`)** en ese operando. `no None` produce `True`, y el predicado completo (`y`) siempre entrega `bool`; por eso la exigencia de `bool` **en el resultado completo** no cambia su color. Si se decidiera exigir `bool` también en cada operando lógico, este hallazgo requeriría una decisión y medición de impacto separadas.

Las llamadas escalares usadas directamente como condiciones en Jam y LyraGASP declaran `-> bool` en sus respectivos `escalares.py`. La comprobación estática trata comparadores, lógicos con hijos booleanos, literales booleanos y esas llamadas como booleanos; marca accesos a campos y llamadas sin esa garantía. No infiere tipos de los hechos. La presencia de un nodo sospechoso es posibilidad estática, no dependencia demostrada de coerción en el filtro.

## Ejecución y límites

Se corrió `test --rapido --confiar-escalares` en la copia instrumentada contra los corpus y la aceptación de los seis proyectos, más `biblioteca verificar` para la biblioteca del ejemplo. Las aceptaciones informaron: Oracle 120 rojos esperados y 85 verdes; los tres proyectos de ejemplo 5/1, 6/9 y 20/13; Jam 28/3; LyraGASP 77/115. La biblioteca certificó 3 casos. El registro de predicados completos no booleanos quedó vacío; el registro de operandos de `no` contiene las 10 observaciones anteriores, todas mapeadas a archivo y línea.

Los comandos de Oracle, Jam y LyraGASP terminaron con código 1 **después** de la aceptación: Oracle por cifras vencidas en `README.md`; Jam y LyraGASP por procedencia diferencial que apunta a rutas del producto ausentes de estos checkouts de consumidores. Los tres ejemplos y la biblioteca terminaron con código 0. `--rapido` omite mutación y, en Oracle, tests unitarios; esa omisión no afecta la observación de predicados durante corpus y aceptación. El censo propio excluye medidas heredadas: el catálogo efectivo ejecutado contiene 62 medidas en Oracle, 83 en Jam y 67 en LyraGASP.

## Reproducir

Desde la raíz de este checkout:

```bash
python3 tareas/20260916-202010-predicado-bool/medir.py --solo-estatico
python3 tareas/20260916-202010-predicado-bool/medir.py > /tmp/pbool-medicion.json
```

La salida JSON incluye los conteos por proyecto, cada hallazgo con `archivo:línea`, los valores y repeticiones observados, las aceptaciones y los códigos de salida. El script crea una copia temporal de Oracle e instrumenta allí los resultados completos de `donde`, `sin`, `requiere` y los operandos de `no`; no altera la evaluación. Las funciones escalares externas se ejecutan con `--confiar-escalares`, igual que en los proyectos. El resultado depende del contenido actual de los corpus.
