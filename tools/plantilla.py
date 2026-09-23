"""Entrega recursos editables al consumidor, sin importar ni ejecutar su sensor."""
from __future__ import annotations

import argparse
from importlib.resources import files
from pathlib import Path
import shlex
import os
import sys


def fuente():
    if __package__ == 'tools':
        raiz = Path(__file__).resolve().parents[1]
        # En el wheel `tools` puede ser un alias del paquete instalado.
        if (raiz / 'ejemplo' / 'sensor-prosa').is_dir():
            return raiz / 'ejemplo' / 'sensor-prosa'
    return files('oracle_metalenguaje.plantilla_sensor_prosa')


def archivos(raiz, prefijo=Path()):
    for entrada in sorted(raiz.iterdir(), key=lambda p: p.name):
        if entrada.name.startswith('__') or entrada.name.endswith('.pyc'):
            continue
        relativa = prefijo / entrada.name
        if entrada.is_dir():
            yield from archivos(entrada, relativa)
        elif entrada.is_file():
            yield relativa, entrada.read_bytes()


def main(argv=None):
    parser = argparse.ArgumentParser(prog='oracle plantilla', description=__doc__)
    parser.add_argument('nombre', choices=['sensor-prosa'])
    parser.add_argument('destino', type=Path, help='directorio nuevo; nunca se mezcla ni sobrescribe')
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == '--sensor-prosa':
        args[0] = 'sensor-prosa'
    if args == ['help']:
        args = ['--help']
    if not args:
        parser.print_help()
        return 0
    opciones = parser.parse_args(args)
    try:
        contenido = list(archivos(fuente()))
        opciones.destino.mkdir(parents=True, exist_ok=False)
        for relativa, datos in contenido:
            destino = opciones.destino / relativa
            destino.parent.mkdir(parents=True, exist_ok=True)
            with destino.open('xb') as salida:
                salida.write(datos)
    except OSError as exc:
        print(f'No se pudo copiar la plantilla (no se pisa un destino existente): {exc}', file=sys.stderr)
        return 1
    destino = shlex.quote(str(opciones.destino))
    print(f'Plantilla copiada en {destino}. El sensor ahora pertenece a tu proyecto.')
    print('Oracle no ejecuta el sensor. Revisá README.md y luego:')
    print('1. Poné OPENROUTER_API_KEY en el entorno.')
    # Si se copia al lado de un proyecto, el catálogo a juzgar es el de ese proyecto, no el de
    # ejemplo que trae la plantilla: seguir la instrucción al pie de la letra no puede juzgar juguetes.
    propio = Path.cwd() / 'catalogos'
    catalogo = (shlex.quote(os.path.relpath(propio, opciones.destino)) if propio.is_dir()
                else 'catalogos')
    print(f'2. cd {destino} && python sensor_prosa.py correr --catalogo {catalogo} --salida corrida')
    print('3. oracle juzgar --proyecto . --con corrida/hechos.json')
    return 0
