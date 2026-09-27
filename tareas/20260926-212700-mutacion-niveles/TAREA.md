# Mutación por niveles: --bajo, --medio, --alto, --muy-alto, con paralelismo y selección de tests

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: 

### Nota (2026-09-26 21:27:00 UTC)

2026-09-26, pedido de Brian: niveles para correr la mutación, porque una ronda de tools/cli.py tarda horas (734 mutantes; carga 1,5 sobre 32 núcleos: corre de a un mutante). DISEÑO (Claude): dos ejes separados. (1) VELOCIDAD, igual en todos los niveles y sin cambiar el veredicto: varios mutantes a la vez, cada uno en su copia (-j N, por omisión la mitad de los núcleos); para matar, primero sólo los tests que pasan por la línea mutada (mapa de cobertura), porque un test que falla mata de verdad; todo sobreviviente se confirma con la suite entera, como hoy. (2) ALCANCE, que es lo que eligen los niveles: --bajo = líneas cambiadas desde el último commit (parcial, sale 2); --medio = líneas cambiadas desde el último tag publicado (parcial); --alto = módulos ENTEROS cambiados desde el último tag (completo; lo que pide un corte); --muy-alto = todo el perfil (completo). Criterio de hecho: el veredicto de --alto con -j y selección es idéntico al de la ronda secuencial de hoy sobre los mismos módulos (comparar lista de muertos y vivos), y se mide el tiempo de las dos. Se empieza DESPUÉS de publicar 0.32.0: cambiar el arnés en medio del corte invalidaría la ronda en curso.
