# El perfil de mutación deja afuera partes de la herramienta, incluido el propio arnés, y nadie lo informa

- ESTADO: ABIERTA
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

## Próximo paso

Leer cómo arma el perfil `perfiles/python/mutacion_codigo.py` y por qué rechaza esos módulos.
