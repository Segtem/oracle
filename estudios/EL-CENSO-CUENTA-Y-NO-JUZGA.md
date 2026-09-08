# El censo cuenta y no juzga

**Fecha:** 2026-09-08. **Estado:** `oracle censar` en 0.11.0.

Salió de una pregunta del usuario: «¿sirve Oracle para algo como una auditoría o un informe?». La
respuesta corta era que **ya lo era**, sólo que el ensamblado lo hacía una persona: para contestar
«cómo está todo» había que correr seis comandos en tres repositorios y armar la tabla a mano.

## Lo que faltaba, y hoy se vio tres veces

1. **Nada agregaba estado a través de proyectos.** Oracle sabía de sí mismo y cada consumidor del
   suyo; nadie sabía «cómo está todo».
2. **Nada registraba la serie.** El mismo día, una sombra pasó de 9 a 16 y ese CAMBIO era la
   información —más que el valor—, pero sólo vivía en la prosa de un commit.
3. **El veredicto es binario y una auditoría necesita alcance.** «VERDE» no dice con cuántos
   mutadores ni sobre qué corpus. El día anterior se había aprendido por las malas que un número
   sin su denominador miente: **5 de 29**.

## La trampa, y la regla que la evita

Un informe que agrega está a un paso de un tablero, y un tablero a un paso de una métrica que se
vuelve objetivo. El proyecto ya lo vivió: `cifras.py` cuenta que la proporción de falsación «era
además el número que el proyecto publicaba como criterio, y el que nadie estaba midiendo — las dos
cosas a la vez».

`agy` revisó el diseño y formuló la regla mejor de lo que estaba escrita:

> **Ni cocientes, ni porcentajes, ni semáforos, ni booleanos de conformidad. Todo denominador viaja
> como un hecho independiente, y ningún hecho agrega ni compensa entre dos proyectos.**

Esa última mitad importa tanto como la primera: sin ella, la deuda de un proyecto se tapa con el
volumen de otro. Hay un test por cada mitad — uno rechaza cualquier campo flotante o llamado
`tasa`, `salud`, `estado` u `ok`; otro exige que los conteos **cierren** contra su total.

## El bug que el test encontró en el primer intento

El segundo test falló apenas se escribió: los casos daban **183 sobre 189**. Faltaba contar
`generada`, así que seis casos eran invisibles.

Es el problema del denominador, cometido adentro del censo que existe para evitarlo. El arreglo no
fue agregar la línea que faltaba sino **hacer imposible la próxima**: las procedencias se leen del
vocabulario, y si aparece una quinta el censo falla cerrado en vez de dejar de sumar en silencio.

## No compara contra el censo anterior, y es deliberado

«El anterior» es una heurística frágil: ¿el archivo más reciente en disco? ¿el commit padre? Con dos
agentes turnándose un repositorio puede ser de otra rama o de un árbol sucio. Y si la comparación se
equivoca, el número malo queda grabado **dentro** del censo de hoy, que es un registro histórico y
no se corrige.

El precedente está en el corpus: `007-relevo-verde-arbol-sucio`, donde una regla comparó contra HEAD
mientras los cambios estaban sin commitear, el diff salió vacío y la verificación se declaró
vigente. La lección quedó escrita ahí: **«verde» es una foto con fecha**.

Una comparación necesita sus dos puntas declaradas por quien la pide.

## Por qué «censar» y no «relevar»

Era `relevar` hasta que `agy` lo frenó, y el argumento es concreto: en este ecosistema «relevo» ya
significa el traspaso de turno entre sesiones —`RELEVO.md`, `tools/relevo.py` en un consumidor, y
medidas `relevo.*`—. Son **homónimos sin relación operativa**, y `oracle relevar` haría pensar que
sirve para cerrar el turno. Un censo es un empadronamiento sincrónico de una población, que cuenta
sin juzgar.

## Dos vistas, un solo emisor

Terminal y página salen de los mismos hechos, y un test fija el invariante: **la página no dice
ningún número que la terminal no diga** —descontando los pesos tipográficos del CSS, que no son
datos—. Si mostrara uno de más habría dos verdades que sincronizar a mano, que es el defecto que
`cifras.py` existe para evitar en el README.

## Lo que encontró en su primera corrida

Un archivo ilegible nuevo en un consumidor, de un tipo distinto al de la aridad de macros:
`animacion.clip_de_linea_base_ausente_del_lote.json — se esperaba al menos un agregado`. Y que ese
consumidor había avanzado en paralelo hasta 121 casos con dos dominios nuevos.

Nadie lo sabía. Un comando lo dijo, que era exactamente el punto.

## Tres medidas del propio proyecto corrigieron el trabajo

Mientras se escribía, fallaron tres cosas y las tres tenían razón: el verbo tenía que estar en la
ayuda, tenía que estar en el manual, y **la distribución no puede nombrar a un consumidor
conocido** — el docstring traía `../jam/medidas` como ejemplo. La última es la que más vale: el
paquete que se publica no debe conocer a quién lo usa.

## Lo que encontró la rueda instalada, que el árbol no podía encontrar

El verbo andaba desde el repositorio. Corrido desde el wheel en un venv limpio —el chequeo que en
0.10.0 fue el defecto entero— murió al primer proyecto:

```
MedidaMalDeclarada: el id «meta.agrupar_no_agranda_la_relacion» está dos veces:
  …/site-packages/oracle_metalenguaje/catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle
  /home/…/Dev/oracle/catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle
```

**No es un defecto del censo.** `oracle test --proyecto <repo de oracle>` desde el wheel falla
idéntico: el repositorio de Oracle *es* el catálogo base, así que el paquete instalado lo carga dos
veces. Es DECISION-010 —el paquete instalado es otro proyecto— vista desde otro ángulo, y el repo se
mide con su propio árbol.

Lo que **sí** era del censo es la consecuencia: la corrida entera moría, y se llevaba puestos a los
otros dos proyectos, que se leían perfectamente. Un censo de tres que muere en el primero no informa
de nada. Es la misma lección que 0.9.1 le enseñó a `sintaxis.py`, y llegó por el mismo camino: no la
vio nadie leyendo el código, la vio una corrida contra lo que se distribuye.

`censar_uno` sigue levantando la excepción —es la primitiva de a uno, y quien la llama decide—;
`censar` no: anota el motivo en la fila y sigue. La fila ilegible **no trae conteos**, porque un
proyecto que nadie pudo leer no tiene «0 medidas», tiene medidas que nadie contó. Y conserva las
señas que sí se pudieron leer —commit y árbol sucio—, que son la primera pregunta al mirar después
por qué falló.

## Las dos que encontró la mutación, y ninguna era una constante suelta

`tools/censar.py` entra a la matriz de CI y cierra en **38/38, sin equivalentes declarados**. En el
camino, dos hallazgos que no eran ruido:

- **`confiar=True` por omisión** en `censar_uno` y `censar`. El CLI exige `--confiar-escalares` para
  ejecutar el `escalares.py` de un proyecto ajeno, que es correr código de otro; la biblioteca lo
  hacía sola si nadie decía nada. Era la puerta de atrás de esa misma decisión, y sobrevivía porque
  el único test que la tocaba usaba un `escalares.py` que estallaba: levantaba excepción con
  `confiar` en cualquiera de los dos valores, y el test la aceptaba con `assertRaises(Exception)`.
  El mutante no encontró una constante: encontró un test que no distinguía.
- **La página no declaraba su codificación.** Se escribe en UTF-8 y no lo decía, así que un
  navegador que la abre desde el disco adivina — y «días», «más vieja» y «árbol sucio», las palabras
  que este censo usa para lo que importa, son las primeras en salir rotas.
