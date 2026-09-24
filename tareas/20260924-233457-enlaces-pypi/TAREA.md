# Los enlaces de la página de PyPI apuntan a main y se rompen cuando un archivo se mueve

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, distribucion, flaqueza


## Por qué

El README es la descripción de PyPI (`pyproject.toml`, `readme = "README.md"`), y sus enlaces van a
`github.com/Segtem/oracle/blob/main/...`. Cuando en 0.30.0 se movieron las decisiones y los estudios,
la página de PyPI de 0.28.0 y de las versiones anteriores quedó con enlaces 404, y no tiene arreglo:
PyPI no deja editar una descripción publicada.

## Qué hacer

Que cada versión publicada enlace a **su** tag (`blob/v0.30.0/...`), que no se mueve: el build
reescribe los enlaces relativos y los de `blob/main` del README a la URL del tag de
`VERSION_DISTRIBUCION`, sin tocar el README del repo. Con un test y la comprobación en
`verificar_instalacion` (la METADATA del wheel no tiene enlaces a `main`).

## Próximo paso

Implementar.
