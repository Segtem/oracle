"""Servidor MCP de sonda: ¿qué partes de una respuesta llegan al modelo en cada cliente?

Cada lugar de la respuesta lleva una marca aleatoria distinta, generada al arrancar y guardada en
el archivo que se pasa como argumento. Después se le pide al modelo que copie las marcas que vio:
las que aparecen llegaron, las que no, el cliente las dejó afuera.

  D- descripción de la herramienta      S- description dentro de outputSchema
  T- bloque de texto de content         E- structuredContent

Dos herramientas: `sonda_con_texto` (texto + structuredContent) y `sonda_sin_texto`
(`content: []` + structuredContent), para ver si el cliente expone structuredContent cuando falta el texto.
"""
import json
import secrets
import sys
from pathlib import Path


def marca(prefijo):
    return f'{prefijo}-{secrets.randbelow(9000) + 1000}'


M = {h: {p: marca(p) for p in 'DSTE'} for h in ('con_texto', 'sin_texto')}
Path(sys.argv[1]).write_text(json.dumps(M, indent=2) + '\n', encoding='utf-8')


def herramienta(h):
    m = M[h]
    return {
        'name': f'sonda_{h}',
        'description': f'Sonda de diagnóstico. Marca de descripción: {m["D"]}.',
        'inputSchema': {'type': 'object', 'properties': {}},
        'outputSchema': {
            'type': 'object',
            'description': f'Marca de esquema: {m["S"]}.',
            'properties': {'marca': {'type': 'string'}},
            'required': ['marca'],
        },
    }


def resultado(h):
    m = M[h]
    contenido = [] if h == 'sin_texto' else [{'type': 'text', 'text': f'Marca de texto: {m["T"]}.'}]
    return {'content': contenido, 'structuredContent': {'marca': m['E']}}


def responder(pedido):
    metodo = pedido.get('method')
    if metodo == 'initialize':
        version = pedido.get('params', {}).get('protocolVersion', '2025-06-18')
        return {'protocolVersion': version, 'capabilities': {'tools': {}},
                'serverInfo': {'name': 'sonda', 'version': '1'}}
    if metodo == 'tools/list':
        return {'tools': [herramienta(h) for h in M]}
    if metodo == 'tools/call':
        return resultado(pedido['params']['name'].removeprefix('sonda_'))
    return {}


for linea in sys.stdin:
    pedido = json.loads(linea)
    if 'id' not in pedido:
        continue
    print(json.dumps({'jsonrpc': '2.0', 'id': pedido['id'], 'result': responder(pedido)}), flush=True)
