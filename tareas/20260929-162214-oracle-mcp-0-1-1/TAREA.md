# oracle-mcp 0.1.1: cobertura de requisitos para un agente y Oracle 0.35.0

- ESTADO: CERRADA
- PRIORIDAD: 55
- ETIQUETAS: oracle

### Nota (2026-09-29 16:25:25 UTC)

oracle-mcp 0ea2bf8, tag v0.1.1 y release en GitHub. Herramienta nueva oracle_requirements: la cobertura de requisitos/*.requisito como datos (totales por cobertura, requisitos con medido_por, sin_medir y medidas_inexistentes, y medidas propias sin requisito); REQUISITO_INVALIDO sin respuesta parcial. oracle-metalenguaje==0.35.0. 156 tests (5 nuevos). Build desde clon limpio: instala 0.1.1 con 0.35.0 y trackertast 0.1.0, lista las seis herramientas, y sobre el experimento de OpenSpec da 12 requisitos, 3 medidos y 9 en parte (igual que oracle cobertura). sha256 wheel b9693c04395160854e3c538ef9c68d227b093789e668d1d7d26e346506d5406e · sdist f1244dce1f8ffb570550064b67b57b6d638f330fd196e2a27831418e23264d2a. docs/mcp.md del sitio de Oracle con la herramienta. Falta: que Brian suba a PyPI, verificar sha256, uv tool install oracle-mcp==0.1.1.

### Nota (2026-09-29 16:57:59 UTC)

Publicado en PyPI por Brian; sha256 del wheel y del sdist coinciden con los locales. Herramienta global: uv tool install oracle-mcp==0.1.1 (antes 0.1.0), con oracle-metalenguaje 0.35.0 en su entorno; responde serverInfo 0.1.1 y oracle_requirements da 12/3/9 sobre el experimento. Claude Code y Codex usan ese mismo comando.
