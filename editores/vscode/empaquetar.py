#!/usr/bin/env python3
"""Arma el `.vsix` de la extensión de VS Code desde esta carpeta.

    python editores/vscode/empaquetar.py [--salida <ruta.vsix>]

Sin `npm`, sin `vsce`, sin dependencias: un `.vsix` es un ZIP con dos archivos de
metadatos y la extensión adentro. La misma restricción que tiene el núcleo, por el mismo
motivo — que esto se pueda correr en un aula sin instalar nada.

La versión sale de `package.json`, que es la única que hay. Estuvo escrita en tres lugares
—el `package.json`, el manifiesto del `.vsix` y el `install.sh` de otro repositorio— y las
tres divergieron: mientras la extensión iba por la 1.2.1, la copia incrustada en
`cs50-vscode` seguía en la 1.1.4, sin CodeLens.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ARCHIVOS = ("package.json", "extension.js", "lenguaje.json", "oracle.tmLanguage.json")

MANIFIESTO = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{nombre}" Version="{version}" Publisher="{editor}"/>
    <DisplayName>{titulo}</DisplayName>
    <Description xml:space="preserve">{descripcion}</Description>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
  </Assets>
</PackageManifest>
"""

TIPOS = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="js" ContentType="application/javascript"/>
  <Default Extension="vsixmanifest" ContentType="text/xml"/>
</Types>
"""


def _sin_xml(texto: str) -> str:
    """Escapa lo que rompería el manifiesto. Un `&` suelto lo deja ilegible y sin aviso."""
    return (texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace('"', "&quot;"))


def empaquetar(salida: Path | None = None) -> Path:
    datos = json.loads((AQUI / "package.json").read_text(encoding="utf-8"))
    faltan = [a for a in ARCHIVOS if not (AQUI / a).is_file()]
    if faltan:
        raise SystemExit(f"faltan archivos de la extensión: {', '.join(faltan)}")

    destino = salida or AQUI / f"{datos['name']}-{datos['version']}.vsix"
    manifiesto = MANIFIESTO.format(
        nombre=_sin_xml(datos["name"]), version=_sin_xml(datos["version"]),
        editor=_sin_xml(datos["publisher"]), titulo=_sin_xml(datos["displayName"]),
        descripcion=_sin_xml(datos["description"]))

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("extension.vsixmanifest", manifiesto)
        z.writestr("[Content_Types].xml", TIPOS)
        for archivo in ARCHIVOS:
            z.write(AQUI / archivo, f"extension/{archivo}")
    return destino


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=None)
    ruta = empaquetar(parser.parse_args().salida)
    print(f"{ruta}  ({ruta.stat().st_size} bytes)")
    print(f"instalalo con:  code --install-extension {ruta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
