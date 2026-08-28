# La CLI queda bajo mutación — cierre del 2026-08-28

## Resultado final

`tools/cli.py` quedó en **cero sobrevivientes**, sin equivalentes declarados:

```text
mutantes: 308 · murieron 308 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
```

El manifiesto terminó `completa`; sus 308 filas quedaron en `tests_fallaron`, sin timeout ni error
del arnés. Las tres medidas de proceso dieron 0: todo mutante tuvo un test que lo mató, la ronda fue
concluyente y el bytecode quedó frío.

## Cómo se cerraron los 64 vivos anteriores

### `convertir` y herramientas

- `cmd_convertir` ahora está fijado con ruta relativa al proyecto, archivo ausente, UTF-8 visible en
  `.oracle` y `.caso`, JSON legible de dos espacios y diagnóstico útil para un archivo sin extensión.
  La sangría es parte de la salida de autoría de este comando: el JSON es la forma de almacenamiento
  que la persona puede redirigir a un archivo, no sólo un valor que el test vuelve a parsear.
- `_ejecutar_unitarios` tiene observación directa de `cwd`, `capture_output=True`, `text=True`,
  stdout, stderr, mensaje OK/rojo y código propagado.
- `cmd_test` distingue niveles incompatibles, estructura inválida, una escalar externa no confiada,
  una escalar inválida con confianza y un catálogo inválido. Los tres últimos ya no pueden colapsar
  en el mismo `return 1` sin que la salida lo denuncie.

### Sintaxis y aceptación

- La sintaxis exige las dos direcciones (`json_igual` y `texto_igual`) y una falla documental no
  puede imprimir a la vez `SINTAXIS OK`.
- La ausencia de entradas se expresa con las colecciones, no con seis comparaciones de `len(...)`
  contra cero. Catálogo sin casos falla; ausencia de catálogo y casos saltea aceptación.
- Ese refactor eliminó condiciones numéricas redundantes sin inventar estados inválidos.

### Despacho y atajos

- Las formas canónicas y planas propagan el código de su comando y el argumento exacto para
  `revisar`, `expandir`, `caso generar`, `nueva`, `caso`, `relaciones` y `escalares`.
- Los errores por argumento ausente incluyen `medida probar`, `caso generar`, `--caso` y `--nuevo`.
- Un archivo relativo que existe bajo la raíz del proyecto entra a `revisar`, aunque no exista bajo
  el directorio de trabajo actual. Un proyecto inválido devuelve exactamente 1 por stderr.

Agy clasificó la familia de `convertir`/herramientas y no modificó producción ni tests. Sus
recomendaciones se contrastaron con el código antes de implementar. No se agregó ninguna entrada a
`equivalentes.json`.

## Historia medible

| Ronda | Mutantes | Muertos | Vivos | Timeout | Arnés |
|---|---:|---:|---:|---:|---:|
| Inventario completo inicial | 328 | 227 | 100 | 0 | 1 |
| Después de la primera tanda | 324 | 260 | 64 | 0 | 0 |
| Cierre | 308 | 308 | **0** | 0 | 0 |

La baja de denominador no ocultó vivos: cuatro sitios desaparecieron en la primera tanda al retirar
redundancias estructurales; dieciséis en el cierre al reemplazar comparaciones repetidas por las
colecciones que expresan el mismo contrato. Cada ronda se hizo contra la huella nueva completa.

## Verificación final propia

- Suite: **698 tests OK**.
- Cifras: 698 tests, **605/605** mutantes de medida y 4058 sitios de código totales.
- Corpus: **122 casos OK**.
- Aceptación: sólo los dos rojos deliberados, con valores 1 y 2; no apareció un tercero.
- Diferencial: **4** acuerdos globales y **12** veredictos individuales, 0 desacuerdos.
- Traza: 110 evaluaciones, 224 pasos, 866 nodos, 13 productos y 0 desacuerdos.
- Metamórficas y sintaxis: OK.
- Mutación de medidas: **605/605** muertos, 0 vivos.
- Mutación de `tools/cli.py`: **308/308** muertos, 0 vivos, 0 timeout, 0 errores.

No se integró a `main`, no se hizo push y no se tocó el IDE.
