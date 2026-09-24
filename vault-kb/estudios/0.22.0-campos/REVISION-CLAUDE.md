# Revisión de Claude — 0.22.0 (campos de las relaciones y lo que no se pudo juzgar)

2026-09-15. Entrega de agy terminada a las 18:31, en el primer intento de la cadena con reintentos (el
lanzamiento anterior había cortado a las 18:11 por falta de capacidad del servidor, sin tocar nada).

## Lo que se verificó

- `tests/test_campos_revision.py`, escrito contra el encargo antes de leer la entrega: sus 9 tests pasaron
  sobre ella sin cambios.
- El diseño coincide con el plan: `CAMPOS_DE_RELACIONES` junto a cada emisor (26 relaciones, incluida
  `campo_leido`) y su lector por AST; las 6 relaciones de proceso declaradas; `campo_leido` en un módulo
  propio (`nucleo/campo_leido.py`, porque un test fija `RELACIONES_DE_UNIDAD`); la medida meta;
  `evaluar_conjunto` e `Informe.no_juzgaron`, usados por aceptación, `juzgar`, `mutar` y `mutar_codigo`.
- Sobre el catálogo de Oracle, `meta.toda_medida_lee_campos_que_existen` da verde; los casos 504 y 505
  salen rojo y verde.

## Defectos, corregidos por Claude

### R1. Los tests de la entrega usaban una API que no existe

`tests/test_campos_de_relaciones.py` y `tests/test_no_juzgaron.py` no importaban (`cargar_proyecto`,
`cargar_medida`, `ConfiguracionSombra`, `EntradaSombra` no existen) y, con los imports corregidos,
fallaban 25 de 31: `Veredicto(relacion=…)`, `.datos` sobre un diccionario, medidas con nodos `conteo` y
`filtrar` que el lenguaje no tiene, y proyectos temporales que el lector nunca recorre. Es el costo de
escribir tests sin poder correrlos. Se reescribió `tests/test_campos_de_relaciones.py` con proyectos
temporales reales y medidas canónicas (lector y cada rechazo, `campo_leido` por origen, la condición de
`requiere`, `hecho` y `col`, `evaluar_conjunto`), y se borró `tests/test_no_juzgaron.py`: lo que tenía de
válido ya lo fija `tests/test_campos_revision.py`.

### R2. `_MedidaSegura` abría un falso verde en el corpus

Para que `aceptacion` no terminara en traceback, la entrega envolvía el catálogo que recibe
`hechos_de_casos` en un objeto que, ante `ErrorDeAlgebra`, devolvía un veredicto con `ok = False`. Para un
caso `falso_verde` eso cuenta como «se puso rojo, como debía»: un caso que su medida **no pudo juzgar**
pasaba por fijado en `meta.el_caso_se_pone_como_debe`. La entrega no podía tocar `nucleo/marco.py`, que era
el lugar. Corregido ahí: un caso que no se puede juzgar nunca «se pone como debe», sea cual sea su
polaridad. El envoltorio se borró.

### R3. El lector de campos copiaba el lector de `RELACIONES_*`

`nucleo/relacion.py` traía copias de `_extraer_textos_ast` y `_extraer_relaciones_del_arbol`, que ya viven
en `nucleo/medida.py`. `campos_de_relaciones_declarados` usa ahora `relaciones_del_lenguaje_declaradas`
(import local: `medida` importa `relacion` al cargarse) y las copias se borraron. Dos lectores del mismo
contrato terminan divergiendo; es el caso `012` del corpus.

### R4. `campo_leido.py` duplicaba y confundía

Traía su propia `extraer_alias_de_fuente`, idéntica a la de `nucleo/unidad.py`; una `como_hechos` con el
mismo nombre que la de `nucleo/medida.py` y otra firma; y una rama para diccionarios que la forma canónica
de una medida nunca contiene. Reusa la de `unidad`, y lo demás se borró.

### R5. `mutar.py` perdió su explicación, y quedaron imports sin uso

El docstring de `_politicas_ok` perdía por qué un SIN EVIDENCIA no hace fallar la ronda (la corrección de
0.21.0). Se repuso junto con la regla nueva. `ErrorDeAlgebra` y `evaluar` quedaban sin uso en
`tools/mutar.py`, y `ErrorDeAlgebra` en `tools/mutar_codigo.py` y `tools/aceptacion.py`.

### R6. El módulo nuevo quedaba fuera del arnés

`nucleo/campo_leido.py` no estaba en los objetivos de `tools/mutar_codigo.py` ni en la matriz de CI, y dos
tests lo exigen. Registrado con sus tests prioritarios.

### R7. El plan dejaba fuera dos relaciones de proceso que el catálogo sí lee

El plan decía que `importa` y `cambio` no las lee ninguna medida. El volcado real de `campo_leido` sobre
el catálogo de Oracle (`tools/aceptacion.py --hechos … --hechos-solo campo_leido`) mostró tres lecturas
de relaciones sin declarar: `importa.b` e `importa.es_test` en `proceso.modulo_con_consumidor`, y
`cambio.es_codigo_vivo` en `proceso.verificacion_vigente`. La medición previa al plan no resolvía los
alias de un `unir`. Se declararon las dos: `importa` con los campos que emite
`perfiles/python/marco.py` y `cambio` con el que lee su medida, porque nadie la emite en Oracle. Con eso
las 160 lecturas del catálogo son de relaciones del lenguaje (131) o declaradas (29), todas existentes.

### R8. La medida nueva quedaba fijada sólo con evidencia fabricada

`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` puso la aceptación en rojo: los dos casos de
`meta.toda_medida_lee_campos_que_existen` (504 y 505) son construidos. Se agregó el caso observado `506`,
con las filas reales que emitió el comando anterior y el comando en su `origen`.

## Lo que encontró la mutación, corregido por Claude

### R9. La sombra tapaba un «no juzgó» en la aceptación

`tools/aceptacion.py` perdonaba en sombra una medida meta que no pudo juzgar (los dos sobrevivientes
de las líneas 209 y 212 lo mostraron: la rama no la distinguía ningún test). La sombra apaga la
consecuencia de un rojo; una medida que lee algo que la evidencia no trae es un defecto de la medida.
La rama se borró: un «no juzgó» es falla siempre.

### R10. `campo_leido.py` validaba lo que el álgebra ya validó

Los sobrevivientes de `extraer_alias_de_medida` y de `_extraer_lecturas_de_arbol` estaban en guardas
sobre formas que `Medida.de_datos` y el álgebra rechazan antes (una tubería sin fuente, un `campo` cuyo
alias o nombre no es un nombre). Se borraron. La rama del alias que ninguna fuente liga sí se alcanza
—el álgebra lo acepta— y ganó su test.

### R11. Ramas sin test

- `nucleo/marco.py`: que un caso que no se puede juzgar nunca «se ponga como debe», en las dos polaridades.
- `nucleo/relacion.py`: una clave del mapa que no es texto se rechaza por su forma, y un directorio o un
  enlace con nombre de módulo no se leen.
- `nucleo/medida.py`: `Informe.ok` es `False`, no un falsy cualquiera.
- 33 errores de arnés en la ronda de `nucleo/relacion.py`: `tests/test_campos_de_relaciones.py` construía
  una relación al importarse, y un mutante que rompía `Relacion.de_datos` impedía cargar el módulo en vez
  de matar un test. Se construye dentro de una función.

## Tests existentes actualizados (propiedad de Claude)

- `test_medida`: `campo_leido` en las relaciones del lenguaje; 61 medidas, 41 universales.
- `test_relacion`: 26 ámbitos declarados y 26 filas de `ambito_de_relacion`.
- `test_juzgar` (r4): parchea `evaluar_conjunto`, que es lo que `juzgar` llama ahora.
- `test_manual`: 41 medidas universales en el manual.
- `docs/manual.html` regenerado por la medida nueva.
