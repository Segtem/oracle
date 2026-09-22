"""Preparación local reproducible; no llama a modelos ni lee juicios anteriores."""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import catalogos  # registra las escalares del catálogo
from nucleo.medida import cargar_catalogo

D = Path(__file__).resolve().parent
ANTERIOR = ROOT / 'tareas/20260922-190222-jev-prueba'


def construir():
    leer = lambda n: json.loads((ANTERIOR / n).read_text())
    originales = leer('catalogo-congelado.json')
    muestra = set(leer('muestra-jev.json'))
    catalogo = cargar_catalogo(ROOT / 'catalogos', ROOT / 'perfiles/python/catalogos')
    assert set(catalogo) == {r['medida'] for r in originales}
    for r in originales:
        m = catalogo[r['medida']]
        actual = dict(medida=m.id, alcance=m.alcance, porque=m.porque,
                      umbral=f'{m.op} {m.limite}', segun=m.segun)
        assert actual == r, f'Cambió la prosa o el umbral: {m.id}'
    anteriores = {r['id']: r for r in leer('lote.json')['records']}
    pares = leer('clave-controles.json')
    random.Random(20260923).shuffle(pares)
    lote, clave = [], []
    for i, par in enumerate(pares, 1):
        m = catalogo[par['medida']]
        rid = f'v{i:03}'
        fila = dict(anteriores[par['id']], id=rid, tuberia=m.tuberia,
                    resumen=m.resumen, limite=m.limite,
                    aplica_vecino=m.limite != 0)
        lote.append(fila)
        clave.append(dict(id=rid, anterior=par['id'], medida=m.id,
                          control=par['control'], muestra=m.id in muestra and not par['control'],
                          esperado={'porque_origen': False,
                                    'porque_vecino': False if m.limite != 0 else None}
                          if par['control'] else None))
    ids_ciegos = {r['id'] for r in clave if r['muestra'] or r['control']}
    ciego = [r for r in lote if r['id'] in ids_ciegos]
    plantilla = [dict(id=r['id'], porque_origen=None, porque_vecino=None,
                       justificacion_origen='', cita_origen='',
                       justificacion_vecino='', cita_vecino='') for r in ciego]
    return {'lote.json': lote, 'clave-operador.json': clave,
            'ciego/registros.json': ciego, 'ciego/plantilla.json': plantilla}


def main():
    verificar = sys.argv[1:] == ['--verificar']
    datos = construir()
    for nombre, contenido in datos.items():
        ruta = D / nombre
        texto = json.dumps(contenido, ensure_ascii=False, indent=2) + '\n'
        if verificar:
            assert ruta.read_text() == texto, f'Artefacto alterado: {nombre}'
        else:
            ruta.parent.mkdir(exist_ok=True)
            with ruta.open('x') as f:
                f.write(texto)
    archivos = list(datos) + ['CRITERIO.md', 'ciego/INSTRUCCIONES.md', 'protocolo.json']
    hashes = {n: hashlib.sha256((D / n).read_bytes()).hexdigest() for n in archivos}
    if verificar:
        assert json.loads((D / 'integridad.json').read_text()) == hashes
    else:
        with (D / 'integridad.json').open('x') as f:
            json.dump(hashes, f, indent=2)
            f.write('\n')
    print('OK: 62 reales + 10 controles; paquete ciego: 15 reales + 10 controles; hashes verificados.')


if __name__ == '__main__':
    main()
