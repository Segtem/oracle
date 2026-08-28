# Plan — un entorno para escribir Oracle, cuando L−1 y L−2 estén

**Estado:** guardado, sin empezar (2026-08-27) · **Depende de:** que L−1 y L−2 cierren primero.
No es una hoja de ruta comprometida: es lo averiguado, para no volver a averiguarlo.

## Por qué esperar

Dos de las tres opciones se apoyan en el **álgebra**, que lleva meses igual: cinco operadores, el
umbral con su defensa, el alcance. La tercera —un servidor LSP— se acopla a la **superficie**, y la
superficie está en obra: el 2026-08-27 se reescribió cómo se parsean las macros y el umbral cambió
de forma para aceptar `segun`. Un LSP construido contra eso nace desactualizado.

## Lo que ya está hecho y no hay que construir

Lo caro de cualquier editor es entender el programa. Acá está resuelto, y no como pieza de IDE sino
como parte del lenguaje:

- **El programa es dato.** Una medida ES su AST en JSON. No hay que parsear nada para manipularla.
- **Hay mapa de posiciones.** `nucleo/sintaxis.py` guarda `Ubicacion(linea, columna)` por ruta del
  AST, y `ErrorSintaxis` ya trae `linea`, `columna`, `esperado` y `encontrado` como campos. Eso es
  un diagnóstico de LSP sin trabajo extra.
- **El programa se consulta en el propio lenguaje.** Con `termino` y `ancestro`, «mostrame las
  medidas que usan `unir`» no es un plugin: es una medida de cuatro líneas.
- **Ya existe un linter semántico**: `oracle medida revisar` dice «nunca se pone roja» o «nunca se
  pone verde», que para un taller vale más que el autocompletado.
- **Ya existe el bucle**: `oracle medida probar <archivo> --con <filas>` da veredicto y testigos sin
  pasar por el corpus.

## Las opciones, en el orden en que las haría

### 1. `oracle medida probar --vigilar` — el bucle en vivo, sin IDE

Que se quede mirando el archivo y re-evalúe al guardar. El alumno usa el editor que ya tiene y una
terminal al lado que se actualiza sola. **Es una tarde de trabajo**, y entrega la mitad del valor de
todo lo demás.

### 2. Una página web con Pyodide — cero instalación

**Oracle es Python puro con cero dependencias** (`dependencies = []` en `pyproject.toml`), así que
corre en el navegador bajo Pyodide. Una sola página: la medida a la izquierda, la evidencia a la
derecha, el veredicto y los testigos abajo, actualizándose mientras se escribe.

En un aula eso no es comodidad: es la diferencia entre dar clase y pasar la primera hora instalando
Python en máquinas ajenas.

### 3. Un servidor LSP — la jugada de «lenguaje normal»

Diagnósticos (ya existen), autocompletado de los conjuntos cerrados —`etiqueta`, `procedencia`,
`segun`, y los campos que declara cada relación—, y el `alcance` derivado al pasar el mouse. Un solo
servidor sirve VS Code, Emacs, Neovim y Zed: no se construye un IDE, se enchufa a todos.

**Va último** porque es el único que se acopla a la superficie.

### Descartado por ahora

- **Extender FORJA**, el IDE educativo en Emacs: **no está en el disco** (verificado el 2026-08-27,
  igual que los vaults de `~/Dev/kb/`). Si vuelve, se reconsidera.
- **Una TUI**: lo más barato y lo menos visual. Para enseñar, lo visual pesa.

## Las tres pantallas que valdrían la pena en un aula

1. **El veredicto en vivo con sus testigos.** Que una medida señala *filas concretas* y no da una
   opinión es la mitad de la lección.
2. **El momento en que el mutante sobrevive.** Un botón que rompe la medida a propósito —invierte el
   comparador, borra el filtro— y muestra si la evidencia se dio cuenta. *«Le di vuelta el `<=` y tu
   caso siguió en verde»* enseña testing como ningún discurso. **Ningún otro lenguaje tiene esta
   pantalla.**
3. **El mapa de puntos ciegos.** Todos los `alcance` del catálogo juntos: «esto es todo lo que el
   sistema NO mira».

## La regla que no se negocia

**El entorno puede mostrar, medir y confrontar. No puede escribir las tres cosas que decide un
humano**: el umbral, su defensa y lo que la medida no ve.

La fricción de Oracle no es toda igual. Hay una que enseña —elegir un umbral, elegir `procedencia`,
declarar qué no se mira— y otra que sólo cansa —tipear la fecha, inventar un commit, redactar un
caso entero para ver si una idea anda—. La segunda se saca sin costo, y se sacó: `oracle medida
probar`, la fecha y el origen leídos de git, el `alcance` derivado, `segun` en vez de un párrafo
obligatorio.

La primera es la clase. Un entorno que la autocomplete con un LLM no ahorra tipeo: deja el mismo
verde vacío que Oracle existe para denunciar, con mejor tipografía.
