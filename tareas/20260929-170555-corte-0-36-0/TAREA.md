# corte 0.36.0

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle

### Nota (2026-09-29 17:17:40 UTC)

Mutación del corte con el disco sano (11 GB libres): nucleo/generador.py 327/327 (+2 equivalentes) y perfiles/python/mutacion_codigo.py 298/298; tools/lsp.py fuera del perfil con razón declarada. oracle test VERDE, 2205 tests. Build desde clon limpio (uv build) y verificar_instalacion OK. sha256 wheel f32dbfee20ab8ecc4351eb8d39ffdf7b6a3f427c5db0d4b53180d271dfb5f9d1 · sdist 6aecddd56c0b26d599aa4c62860346a24fd4ee41426be7d32e455e7f7f6e7d43.

### Nota (2026-09-29 18:48:30 UTC)

Publicado en PyPI por Brian; sha256 del wheel y del sdist coinciden. Instalación limpia desde PyPI (tras esperar al índice simple): oracle 0.36.0, sintaxis 1.1; oracle test VERDE y oracle cobertura 12/3/9 sobre el experimento de OpenSpec. Consumidores medidos antes del pin, mismas cifras que con 0.35.0: LyraGASP 6a853f5 (78/116, 580, 487/487, suite 151), Jam 490ece9 (28/4/3, 1099, 448/448, suite 1429), commander 1654418 (sin medidas propias). Herramienta global 0.36.0 con trackertast 0.1.0.
