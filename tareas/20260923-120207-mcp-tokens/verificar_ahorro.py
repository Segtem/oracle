"""Compara el cambio con la captura original sin sobrescribir medicion/."""
from pathlib import Path
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))
from tools import mcp


def size(value):
    return len(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode())


def delta(before, after):
    a, b = size(before), size(after)
    return {'antes_bytes': a, 'despues_bytes': b, 'ahorro_bytes': a-b,
            'ahorro_estimado_bytes_div_4': (a-b)/4}


originales = {r['id']: r for r in map(json.loads, (BASE/'medicion/respuestas.jsonl').read_text().splitlines())}
run = subprocess.run([sys.executable, 'tools/mcp.py', '--proyecto', str(ROOT)],
                     input=(BASE/'medicion/pedidos.jsonl').read_bytes(),
                     capture_output=True, cwd=ROOT, check=True)
assert not run.stderr, run.stderr
actuales = {r['id']: r for r in map(json.loads, run.stdout.splitlines())}
for r in actuales.values():
    result = r.get('result') or {}
    if 'structuredContent' in result:
        assert not result['isError']
        assert json.loads(result['content'][0]['text']) == result['structuredContent']
for i in range(3, 7):
    anterior = dict(originales[i]['result']['structuredContent'])
    actual = dict(actuales[i]['result']['structuredContent'])
    if i == 3:
        assert len(actual.pop('huella_proyecto')) == 64
        anterior.pop('huella_proyecto')
    assert anterior == actual, i
before = originales[8]['result']['structuredContent']
after = json.loads(json.dumps(before))
for row in after['resultado']:
    del row['cuerpo']
assert after == json.loads((BASE/'medicion/candidato_tareas_listar_sin_cuerpos.json').read_text())
proy = mcp.Proyecto(ROOT)
tareas, problemas = mcp.auditar_tareas(ROOT/'tareas')
assert not problemas, problemas
full = dict(actuales[8]['result']['structuredContent'])
full['resultado'] = [t.a_dict() for t in mcp.filtrar_tareas(tareas, estado='ABIERTA', etiqueta=None, por_id=False, invertir=False, todas=False)]
report = {
    'regla': 'Bytes UTF-8 de JSON compacto / 4; estimación, no tokens reales ni facturación. Captura original inmutable.',
    'tools_list': delta(originales[2]['result'], actuales[2]['result']),
    'listar_captura_fija': delta(before, after),
    'listar_tracker_actual': delta(full, actuales[8]['result']['structuredContent']),
    'evaluar_desafiar_juzgar_catalogo': 'Payloads idénticos salvo huella_proyecto del catálogo; se conservan alcance, testigos y metadatos.',
    'transporte': 'Se conservan ambas copias y outputSchema.',
}
(BASE/'verificacion/ahorro.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
