# Prueba viva de medidas al guardar — 2026-08-30

## Alcance

Se implementó solamente el primer paso de `PLAN-IDE.md`:

```text
oracle medida probar <archivo> --con <filas> --vigilar
```

No se inició un servidor LSP ni se modificaron los entornos consumidores. El comando conserva la
prueba única existente cuando no recibe `--vigilar`; con la opción activa observa la medida y la
vuelve a cargar, parsear y evaluar cada vez que cambia el archivo.

La vigilancia detecta cambios por fecha de modificación en nanosegundos, tamaño e inode. Así cubre
tanto el guardado sobre el mismo archivo como el reemplazo atómico que usan muchos editores. Si el
archivo desaparece durante ese reemplazo o queda transitoriamente inválido, muestra el problema y
sigue esperando. `Ctrl-C` termina de manera explícita con código 0.

El bucle entero corre dentro del mismo contexto de escalares externas que la prueba única: falla
cerrado sin confianza y respeta `--confiar-escalares`. El entorno sólo muestra veredicto y testigos;
no escribe el umbral, `porque` ni `alcance`.

## Evidencia ejecutable

`tests/test_vigilar.py` agrega seis contratos focalizados:

- guardado normal, reemplazo atómico y archivo ausente;
- reevaluación inicial y posterior, con salida visible antes de esperar;
- una medida realmente inválida que se corrige sin reiniciar el proceso;
- despacho de `--vigilar` y rechazo de `--con` sin evidencia;
- elección excluyente entre prueba única y vigilancia, propagando el código de salida;
- confianza y falla cerrada para escalares externas.

La prueba inválida→válida usa un proyecto temporal real y ejercita el parser y el evaluador, no un
doble de esas capas. La batería de la rama quedó en **737 tests OK**; las seis pruebas focalizadas y
las 55 pruebas de CLI también pasaron por separado. Agy revisó el diff reconstruido después del
corte de luz y no encontró bloqueos en parsing, escalares, bucle, salida ni `Ctrl-C`.

Además se ejecutó el comando real sobre `/tmp/oracle-vigilar-demo`: con una fila de altura `450.0`,
el umbral `> 400.0` mostró `ROJO` y, al guardar el mismo archivo con `> 500.0`, el proceso mostró
`VERDE` sin reiniciarse. Una señal `SIGINT` real imprimió `Vigilancia terminada.` y devolvió 0.

## Mutación

La CLI quedó otra vez en cero, con una ronda fresca y manifiesto completo:

```text
mutantes: 317 · murieron 317 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
```

El aumento respecto de los 308 sitios anteriores corresponde a la superficie nueva y su despacho;
no se declaró ninguna equivalencia. La ronda completa de `tools/medida.py` terminó así:

```text
mutantes: 232 · murieron 110 · sobrevivieron 122 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
```

El manifiesto quedó `completa`; el código de salida 1 corresponde a los sobrevivientes, no a una
ronda inconclusa. La deuda es anterior a este trabajo y queda visible, sin ampliar el alcance para
cerrarla. Dentro del bloque nuevo, `_firma_de_archivo` quedó **1/1** y `vigilar` **8/8**: los
**9/9** mutantes murieron y no quedó ningún sobreviviente en esas funciones.

## Corte de luz y recuperación

Un apagado de la máquina eliminó el worktree y los manifiestos que vivían bajo `/tmp`. El código se
reconstruyó desde el diff conservado en el relevo de la conversación, se volvió a comprobar con las
6 pruebas focalizadas y las 737 pruebas completas, y se guardó en el commit `271b98e` antes de
reiniciar las rondas largas. Los nuevos manifiestos se escriben atómicamente y permiten reanudar.
