# Nada vigila que una medida o un caso se escriba en JSON a mano: una medida meta que lo diga

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, parte de una-sintaxis. En vez de prohibirlo en el lector (que tiene que seguir leyendo JSON), una medida meta del catálogo base: meta.se_escribe_en_superficie, que no admite ninguna medida, caso ni relación de un proyecto cuyo archivo fuente sea .json dentro de catalogos/, corpus/ o relaciones/. Necesita que el lenguaje emita el formato del archivo fuente en alguna relación que ya tenga la ruta (medida / caso / relacion_declarada), con sus casos rojo y verde. Un consumidor en migración la pone en sombra con cota (el número de archivos JSON que le quedan), así que la deuda baja y no puede volver a subir. Va después de que Oracle mismo esté todo en superficie.

### Nota (2026-09-26 03:45:33 UTC)

Implementé meta.se_escribe_en_superficie y la relación archivo_de_autoria (declarada en .relacion y documentada en ESPECIFICACION §1.1). La aceptación emite tipo, ruta relativa y formato de cada medida/caso/relación propios en catalogos/, corpus/ y relaciones/, sin sumar bases ni bibliotecas del consumidor. Cinco casos en corpus/meta: tres rojos JSON, un verde sintético y un verde observado sobre Oracle; test de integración temporal para los tres formatos JSON. Actualicé fixtures de proyectos verdes, inventario de mutación, equivalentes y salidas generadas. Evidencia: aceptación Oracle verde con meta.se_escribe_en_superficie=0; suite completa 2591 OK; guia.py 0 salidas pendientes; sitio.py --escribir sin cambios pendientes; test --rapido VERDE; cifras.py CIFRAS OK: 63 medidas, 217 casos (105 defectos rojos, 18 sin evidencia, 87 verdes), 1018/1018 mutantes de medida históricos y 8787 sitios de mutación de código. No corrí mutación ni hice commit; tarea abierta.

## Próximo paso

Claude: correr la mutación completa, revisar los sobrevivientes de `meta.se_escribe_en_superficie` y `nucleo/autoria.py`, y registrar el resultado en esta tarea antes del cierre.

### Nota (2026-09-26 03:49:58 UTC)

2026-09-26, Claude: unida. Probada contra copias de los consumidores: Jam original 79 (41 medidas + 35 casos + 3 relaciones en JSON) y 0 después de oracle convertir; LyraGASP 223 y 0. Al subir a esta versión, cada consumidor la pone en sombra con cota = sus archivos JSON, convierte, y la cota baja a 0. La mutación va en la ronda del corte.
