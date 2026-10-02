# Publicar Oracle 0.38.1 en PyPI desde los paquetes verificados

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: release

Brian pidió preparar el corte para subirlo personalmente. No se ejecutó ningún upload.
Paquetes construidos desde el commit fuente `068f4e8308c1a9a4365c241382a8c696f5229a63`;
el tag del corte es `v0.38.1`. La última versión consultada en PyPI fue 0.38.0.
Validación y hashes: [corte-web](../20261002-100421-corte-web/VERIFICACION.md).

Desde la raíz del repo, los archivos a publicar son exactamente:

```bash
uvx --from twine==7.0.0 twine upload dist/0.38.1/oracle_metalenguaje-0.38.1-py3-none-any.whl dist/0.38.1/oracle_metalenguaje-0.38.1.tar.gz
```

Antes de subir, se pueden comprobar los hashes desde la carpeta de paquetes:

```bash
cd dist/0.38.1
sha256sum -c ../../tareas/20261002-100421-corte-web/SHA256SUMS
cd ../..
```

Después de subir, instalar `oracle-metalenguaje==0.38.1` en un entorno nuevo desde PyPI,
comprobar `oracle --version`, anotar la URL publicada y cerrar esta tarea con commit
`20261002-104608-pypi-0-38-1: done`.

### Nota (2026-10-02 15:42:36 UTC)

Corte publicado en GitHub: main y tag anotado v0.38.1 apuntaron a 790a95e7c32d41cd5ac12309005345b4c771b0df. Tras el reinicio, git fsck y hashes de ambos paquetes correctos. GitHub Pages no inició automáticamente: se solicitó la construcción; despliegue 37028523403 success y HTML público idéntico al commit, incluido #t-enfoques. CI verificar todavía en curso al entregar: runs 37028165102 y 37028163663. Consultar su resultado antes del upload; pruebas locales y paquetes ya verificados. No se publicó en PyPI.

## Próximo paso

Brian: comprobar la CI de v0.38.1 en GitHub Actions, subir los dos archivos verificados con el comando anterior y comprobar la instalación desde PyPI. La portada y el tag ya están publicados.
