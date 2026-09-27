# Avance: Implementación de Motor.desde_texto con la forma única

Fecha: 2026-09-27

## Qué se hizo

1. **`Motor.desde_texto` en `oracle_metalenguaje/motor.py`**:
   - Constructor `classmethod` que recibe `textos: Iterable[str]`, `macros` (por defecto `macros_base()`), `registro` (por defecto `registro_base()`) y `limites` (por defecto `limites_predeterminados()`).
   - Lee cada texto con `nucleo.sintaxis.leer_con_mapa` y verifica compatibilidad de versión.
   - Aplica `nucleo.forma.error_forma` comparando el texto sin líneas `#` contra `imprimir(datos, macros=registro_macros)`. Si hay divergencia (doble espacio, CRLF, falta de salto de línea final, etc.), levanta `ErrorDeMotor` con el diff.
   - Si la sintaxis es inválida (como `mas(a, b)`), levanta `ErrorDeMotor` con el diagnóstico de sintaxis.
   - Admite macros dinámicas (`defmacro`) y medidas (canónicas o con macros estándar como `ninguno`).
   - Actualiza `Motor.__new__` para sugerir `desde_texto`.

2. **Docstring de `desde_datos`**:
   - Se actualizó para indicar que es la API programática sobre el árbol canónico (lo que ya se guardó o generó un programa), no una forma de escribir medidas.

3. **Documentación (`README.md` y `docs/tutorial-practico.md`)**:
   - `README.md` (sección de la API): enseña `Motor.desde_proyecto` para proyectos completos, `Motor.desde_texto` para medidas o macros escritas en superficie `.oracle` y `Motor.desde_datos` sólo como API programática sobre árboles canónicos.
   - `docs/tutorial-practico.md`: documenta y ejemplifica el uso de `desde_texto` frente a `desde_proyecto` y `desde_datos`.
   - `docs/tutorial-practico.html` regenerado mediante `python3 -B tools/sitio.py --escribir`.

4. **Suite de pruebas (`tests/test_motor_desde_texto.py`)**:
   - `test_carga_medida_canonica`: carga y valida propiedades de la medida.
   - `test_rechaza_doble_espacio`: verifica que levanta `ErrorDeMotor` con diff unificado.
   - `test_rechaza_crlf`: verifica que levanta `ErrorDeMotor` señalando CRLF.
   - `test_rechaza_sin_salto_final`: verifica que levanta `ErrorDeMotor` señalando falta de salto final.
   - `test_rechaza_mas_a_b`: verifica que levanta `ErrorDeMotor` ante llamadas funcionales de operadores infijos.
   - `test_acepta_lineas_comentario`: verifica que líneas `#` iniciales, internas y finales son admitidas.
   - `test_la_medida_cargada_evalua_igual_que_desde_datos_con_el_mismo_arbol`: verifica veredictos, valores y representaciones JSON idénticas.
   - `test_carga_medida_con_macro_estandar`: verifica carga y evaluación de medidas con la macro `ninguno`.
   - `test_carga_defmacro_dinamica_y_medida_que_la_usa`: verifica macros de autoría definidas en el lote.
   - `test_validaciones_de_entrada`: valida rechazo de tipos incorrectos (no iterables, no cadenas, macros incorrectas, límites y registros inválidos, ids duplicados).

5. **Cifras y verificación**:
   - Se actualizó `README.md` con `python3 -B tools/cifras.py --actualizar` reflejando 2709 tests y 9260 sitios de mutación de código.
   - `python3 -B tools/sitio.py` confirma que todas las páginas están al día.
   - Suite completa ejecutada: `Ran 2709 tests ... OK`.
