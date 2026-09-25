# El perfil de mutación deja afuera partes de la herramienta, incluido el propio arnés, y nadie lo informa

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: oracle, mutacion


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.5: en los cortes 0.29.0 y 0.30.0 el perfil rechazó como objetivo `tools/mcp_contrato.py`,
`tools/mutar_codigo.py`, `tools/plantilla.py`, `tools/verificar_instalacion.py`, `tools/estudio.py`
y `tools/mutar.py`. El arnés de mutación no se muta a sí mismo.

## Qué hacer

1. El perfil declara explícitamente qué entra y qué no, y por qué, igual que una medida declara su
   alcance.
2. `oracle test --todo` informa cuánto de `nucleo/` y `tools/` queda fuera.
3. Hacer entrar lo que se pueda, empezando por `mutar_codigo.py` y `mutar.py`, y matar los vivos.

**Quién:** Codex.

### Nota (2026-09-25 12:12:14 UTC)

2026-09-25, Claude: el punto 3 lo resolvió custodia (fases 1-3: mutar, generar_diferencial, trazar, ejecutar_suite_mutacion, mutar_codigo y verificar_instalacion entraron, sin vivos). Quedan 1 (el perfil declara qué queda fuera y por qué: estudio, lsp, mcp_contrato, oracle, plantilla, sesion, con la razón que ya da custodia/ANALISIS.md) y 2 (oracle test --todo informa lo que queda fuera). Implementa Codex.

### Nota (2026-09-25 12:35:30 UTC)

2026-09-25 Codex: puntos 1 y 2 implementados. El perfil inventaría 23/25 módulos de nucleo/ y 29/38 de tools/; declara razones para los 2 y 9 excluidos y falla si aparece una exclusión sin declarar. oracle test --todo imprime cantidades, rutas y razones. Dos tests nuevos fallaron antes del cambio y pasan ahora. Reapuntado 1 equivalente de mutar_codigo.py; cifras README: 2559 tests y 8595 sitios. Verificación: unittest discover -s tests 2559 OK; test --rapido VERDE; guia.py 9 pasos OK; sitio.py OK; cifras.py --actualizar OK. Sin commits por .git de sólo lectura.

## Próximo paso

Integrar este diff en una rama con Git escribible; la tarea funcional está cerrada y verificada.
