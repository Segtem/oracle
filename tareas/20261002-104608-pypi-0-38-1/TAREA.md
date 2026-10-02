# Publicar Oracle 0.38.1 en PyPI desde los paquetes verificados

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: release

Brian pidió preparar el corte para subirlo personalmente. No se ejecutó ningún upload.
Paquetes construidos desde el commit fuente `afad7f8a6c8fc45ba92cada497d29e3635fdb2ce`;
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

## Próximo paso

Brian: subir los dos archivos verificados con el comando anterior y comprobar la instalación desde PyPI.
