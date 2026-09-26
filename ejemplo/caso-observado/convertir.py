"""Receta: captura JSON + metadatos explícitos → caso .caso en la forma única, sin ejecutar sensores."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nucleo.caso import DETECCIONES, ETIQUETAS, imprimir
from nucleo.proyecto import ID_CASO_RE
from tools.corpus import OBLIGATORIOS, revisar_evidencia


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captura', type=Path)
    parser.add_argument('metadatos', type=Path)
    parser.add_argument('destino', type=Path)
    args = parser.parse_args()
    try:
        datos = json.loads(args.metadatos.read_text(encoding='utf-8'))
        evidencia = json.loads(args.captura.read_text(encoding='utf-8'))
        if not isinstance(datos, dict):
            raise ValueError('metadatos debe ser un objeto JSON')
        if 'evidencia' in datos:
            raise ValueError('evidencia debe venir sólo de la captura')
        for campo in (*OBLIGATORIOS, 'procedencia'):
            if campo != 'evidencia' and not datos.get(campo):
                raise ValueError(f'falta metadato explícito: {campo}')
        if datos['procedencia'] != 'observada':
            raise ValueError('procedencia debe ser observada, decidida por el autor')
        if not isinstance(datos['origen'], dict):
            raise ValueError('origen debe ser un objeto con la procedencia documentada')
        for campo, opciones in (('etiqueta', ETIQUETAS), ('como_se_detecto', DETECCIONES)):
            if not isinstance(datos[campo], str) or datos[campo] not in opciones:
                raise ValueError(f'{campo} debe ser uno de {sorted(opciones)}')
        if not isinstance(datos['id'], str) or not ID_CASO_RE.fullmatch(datos['id']):
            raise ValueError('id inválido: se espera NNN-descripcion')
        if args.destino.name != datos['id'] + '.caso':
            raise ValueError('destino debe llamarse <id>.caso')
        fallas = revisar_evidencia(str(args.captura), evidencia)
        if fallas:
            raise ValueError('; '.join(fallas))
        datos['evidencia'] = evidencia
        # Una sola sintaxis: el caso se escribe en superficie, exactamente como lo imprime Oracle.
        texto = imprimir(datos)
        with args.destino.open('x', encoding='utf-8') as salida:
            salida.write(texto)
    except (OSError, ValueError) as error:
        parser.exit(1, f'No se pudo convertir: {error}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
