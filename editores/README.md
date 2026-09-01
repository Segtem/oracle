# Editores

Un solo servidor LSP —`oracle-lsp`, que instala el paquete— y dos clientes finos que le hablan.

Los clientes **no reimplementan nada**: piden diagnósticos, completado y CodeLens, y dibujan lo
que llega. Si un cliente calculara por su cuenta si una medida está ejercitada, habría dos
definiciones de lo mismo y con el tiempo dirían cosas distintas.

| | |
|---|---|
| `vscode/` | extensión para VS Code: resaltado, diagnósticos, completado con unidades, CodeLens |
| `emacs/` | cliente para `lsp-mode` |

## VS Code

```bash
uv tool install oracle-metalenguaje      # trae `oracle-lsp` y lo deja en el PATH
python editores/vscode/empaquetar.py     # arma el .vsix
code --install-extension editores/vscode/oracle-lenguaje-*.vsix
```

También podés bajar el `.vsix` ya armado de
[el release](https://github.com/Segtem/oracle/releases/latest) y saltear el paso del medio.

`uv tool install` en vez de `pip` porque en Arch, Debian 12+, Ubuntu 23.04+ y Fedora
instalar al Python del sistema falla con `externally-managed-environment` (PEP 668), y
lo que los editores buscan es `oracle-lsp` **en el PATH**. Con `pip` en un venv, el
ejecutable queda dentro del venv y el editor no lo encuentra salvo que esté activado.

No hace falta `npm` ni `vsce`: un `.vsix` es un ZIP, y el empaquetador son cien líneas de Python
sin dependencias.

## Emacs

Necesita [`lsp-mode`](https://emacs-lsp.github.io/lsp-mode/). Copiá `emacs/oracle-lsp.el` a tu
`load-path` y agregá:

```elisp
(require 'oracle-lsp)
```

Enciende `oracle-mode` para `.oracle` y `.caso`, y arranca el servidor solo.

## Cómo encuentran el servidor

Los dos buscan en el mismo orden, del más específico al más portable:

1. **`ORACLE_LSP`** — la ruta a un `tools/lsp.py` concreto. Es lo que querés mientras desarrollás
   Oracle: el editor usa tu checkout y no el paquete instalado.
2. **`oracle-lsp` en el `PATH`** — el que dejó `pip install`. Es el caso normal.
3. **`~/Dev/oracle/tools/lsp.py`** — último recurso, la máquina donde se escribió Oracle.

Si no encuentran ninguno lo dicen y explican qué hacer, en vez de nombrar un archivo que no existe.

## Límite conocido

**El servidor necesita un proyecto.** `oracle-lsp` sale con código 1 si no resuelve uno —un
`oracle.json` en el directorio de trabajo, o `--proyecto` explícito—. Los editores le pasan la
carpeta abierta: con una carpeta de proyecto abierta funciona; con un `.oracle` suelto el servidor
se apaga y no hay diagnósticos.

Lo correcto es que siga dando diagnósticos de **sintaxis** —que no necesitan proyecto— y degrade
sólo lo que sí lo necesita. Cambia el contrato del servidor, así que va en una versión próxima.

## Publicar en los marketplaces

Todavía no está publicado en el Marketplace de VS Code ni en Open VSX. Los dos son gratuitos y
piden una cuenta de editor; el `.vsix` del release funciona sin ninguna de las dos.
