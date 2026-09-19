# Documentar un camino corto desde un producto nuevo hasta su primera medida observable

- ESTADO: ABIERTA
- PRIORIDAD: 65
- ETIQUETAS: oracle, documentacion

## Problema y evidencia

Derivada de 20260919-134424-naval-pm; ver [postmortem](../../estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md).
La tarea naval prometió medidas de reglas del juego, pero terminó con catálogo propio vacío y un caso que declara sintaxis válida. El README abre con init → nueva → test y “ya tiene quién lo juzgue”; la guía GUIA22 explica correctamente sensores y límites, pero su recorrido completo tiene 1.171 líneas y cuatro medidas. No hay evidencia para atribuirle el 60 % de atención ni afirmar que el tracker fuera obligatorio.

## Resultado buscado

Un recorrido breve, ejecutable desde cero, que termine juzgando hechos del producto con una sola medida pertinente. El lector debe distinguir preparar Oracle, fijar una medida con casos y medir una corrida real.

## Alcance y aceptación

- Agregar o enlazar desde la instalación del README una ruta mínima: elegir una regla del producto → extraer hechos → una medida y casos de ambas polaridades → test → juzgar una corrida real.
- Usar un ejemplo reproducible dentro de Oracle; no modificar /home/workstation/Dev/lab/. Registrar origen verificable de los hechos, comando real y su alcance; no presentar node -c como comprobación de HTML/CSS ni de jugabilidad.
- Mostrar un defecto detectable, su corrección y lo que no mira la medida. Diferenciar evidencia guardada de evidencia regenerada tras cambiar producto.
- Aclarar que tracker y tutorial completo son opciones separadas; indicar cuándo basta un assert y cuándo aporta Oracle. No recortar exigencias de las medidas para lograr una pantalla verde.
- Recorrer los comandos en una copia/entorno limpio con versión fijada y guardar sus resultados. No hace falta diseñar un nuevo comando CLI sin demostrar antes que documentación y ejemplo no alcanzan.

## Próximo paso

Elegir una regla mínima de colocación o disparos y diseñar un ejemplo pequeño con exportación de hechos. Redactar el recorrido junto a las salidas esperadas y comprobarlo de punta a punta antes de enlazarlo desde README.
