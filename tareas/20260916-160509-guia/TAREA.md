# La guía de la batalla naval, recorrida de verdad con 0.25.2

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: oracle, docs, aprendizaje


Brian está aprendiendo Oracle desde cero con un proyecto propio (una batalla naval en HTML5) y una
guía, `~/TestOracleEjemplo/GUIA22.md`, escrita contra 0.22.0. A hacer: recorrerla paso a paso con
0.25.2 instalado desde PyPI en un proyecto de prueba, y corregir en la guía cada comando y salida que
no coincida (versiones, cantidad de medidas universales, `oracle relaciones --escribir`,
herramientas que la guía nombra y no existen).

Lo que salga mal en Oracle mientras se recorre —mensajes confusos, pasos que faltan— se anota acá o
en una tarea propia, no se arregla de paso.

### Nota (2026-09-16 20:16:56 UTC)

2026-09-16: recorrida entera con 0.25.2 en un proyecto de prueba (juego simulado con node para la evidencia del navegador). Corregidas en ~/TestOracleEjemplo/GUIA22.md: versiones y salidas reales; 58 medidas heredadas; oracle relaciones --escribir; caso observado armado en JSON (el corpus lo acepta); la medida del defecto 2 no lo veía en una partida real (contaba impactos, no celdas distintas: doble agrupar); tres casos más para matar mutantes (diagonal, horizontal, eta/zeta); con los defectos arreglados el juego seguía rojo por la variante de torneo; --confiar-escalares lo piden todos los verbos que cargan el catálogo; mide.py y tools/sensor.js no existían. Final: VERDE, 122/122 mutantes. Hallazgos de Oracle: 20260916-200751-traceback-mutar y 20260916-201124-juzgar-omite; además la lista de oracle test muestra un caso SIN EVIDENCIA como «ROJO (valor 0)».
