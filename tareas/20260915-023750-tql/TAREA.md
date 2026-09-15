# Lo que le falta de tatr: TQL, orden de ls, ref desde la tarea e init sin README

- ESTADO: CERRADA
- PRIORIDAD: 75
- ETIQUETAS: oracle, tatr

Terminar lo que [tatr](https://github.com/tsoding/tatr) tiene y `oracle tarea` no. Revisado contra
su `src/tatr.c` y sus commits el 2026-09-15 (último: `20260914-105224: JSON reports`).

## 1. TQL, el lenguaje de consultas

En tatr una consulta selecciona tareas en `ls` y en `untag`:

```
tatr ls :bug and not :ui
tatr ls not tagged
tatr ls :bug and priority lt 50
tatr untag -t viejo :scope
```

Gramática de tatr, tal como la publica:

```
<expr>       ::= <or>
<or>         ::= <and> *('or' <and>)
<and>        ::= <compare> *('and' <compare>)
<compare>    ::= <primary> *(<compare-op> <primary>)
<compare-op> ::= 'lt' | 'le' | 'gt' | 'ge' | 'eq' | 'ne'
<primary>    ::= <tag> | '[' <expr> ']' | 'not' <primary> | 'any' | 'tagged'
               | 'priority' | <number> | <huid>
```

Corchetes y no paréntesis, y `lt`/`gt` y no `<`/`>`, para no pelear con la shell. `ls -debug`
imprime los opcodes de la consulta compilada.

Hoy Oracle filtra con `listar --etiqueta` (una sola) y `--texto`, y `desetiquetar` sólo por estado.
TQL quedó fuera en 0.16.0 a propósito; esta tarea lo trae. A decidir con el diseño:

- nombres en español o los de tatr (`:etiqueta`, `y`/`o`/`no`, `prioridad`, `etiquetada`,
  `cualquiera`) y si se acepta también la forma de tatr;
- `listar <consulta>` y `desetiquetar <consulta>` convivendo con las banderas actuales;
- el equivalente de `-debug`;
- errores de consulta como diagnóstico con posición, código 2, nunca un listado vacío;
- cómo se mide: Oracle ya tiene álgebra, sintaxis y mutación; una gramática es exactamente lo que
  sabe poner a prueba.

## 2. Orden de `listar`

tatr: `ls -a` invierte el orden y `ls -id` ordena por ID. Oracle ordena siempre por prioridad
descendente y desempata por ID.

## 3. `referencias` sin argumento dentro de una tarea

tatr: `tatr ref` sin HUID, parado en la carpeta de una tarea, busca las menciones de esa tarea.
Oracle exige el ID siempre.

## 4. `init` sin README

tatr: `init -no-readme` crea `tasks/` sin el `README.md`. Oracle siempre lo crea.

Salida: los cuatro con contrato en `docs/12-tareas.md`, tests de ambos lados y mutación de los
módulos que toquen, en un corte de distribución.
