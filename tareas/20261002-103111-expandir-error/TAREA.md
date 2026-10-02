# Mostrar diagnóstico breve al expandir una medida mal declarada

- ESTADO: ABIERTA
- PRIORIDAD: 45
- ETIQUETAS:

### Nota (2026-10-02 10:32:03 UTC)

Reproducido durante revisión web: oracle medida expandir archivo.oracle, con macro ninguno-requiere sin ambito, muestra traceback MedidaMalDeclarada en vez de diagnóstico breve. Se corrigió docs/como-funciona.md que decía que omitir ambito era válido. Falta capturar el error de lectura en la ruta expandir y probar salida breve con exit 1; no cambiar el parser.

## Próximo paso

Reproducir la expansión de una macro sin ambito y devolver el error de dominio sin traceback, con prueba del CLI.
