"""Reproduce en temporales; nunca escribe en el laboratorio. Ejecutar desde Oracle."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(sys.argv[1] if len(sys.argv) > 1 else '/home/workstation/Dev/lab/batalla_naval_test')
OUT = Path(__file__).resolve().parent
inventory = []
for p in sorted(LAB.rglob('*')):
    if p.is_file():
        b = p.read_bytes()
        inventory.append(dict(path=str(p.relative_to(LAB)), bytes=len(b),
                              lines=len(b.decode().splitlines()), sha256=hashlib.sha256(b).hexdigest(),
                              named_functions=len(re.findall(rb'\bfunction\s+[A-Za-z_$][\w$]*\s*\(', b))))
(OUT / 'inventario.json').write_text(json.dumps(inventory, indent=2) + '\n')
with tempfile.TemporaryDirectory(prefix='naval-pm-') as tmp:
    p = Path(tmp) / 'juego'
    shutil.copytree(LAB / 'batalla_naval_con_oracle', p)
    reports = []
    def run(label, args):
        r = subprocess.run([sys.executable, str(ROOT / 'tools/cli.py'), *args, '--proyecto', str(p)],
                           capture_output=True, text=True, cwd=ROOT, timeout=120)
        reports.append(f'=== {label} | exit={r.returncode} ===\n' + r.stdout + r.stderr)
    run('conservado: test --rapido', ['test', '--rapido'])
    run('conservado: test completo', ['test'])
    (p / 'game.js').write_text('ESTO NO ES JAVASCRIPT VALIDO {{{\n')
    run('game.js roto; caso intacto: test --rapido', ['test', '--rapido'])
    case = p / 'corpus/juego/001-flota-completa.caso'
    original = case.read_text()
    case.write_text(original.replace('"game.js", true', '"game.js", false'))
    run('evidencia game.js false: test --rapido', ['test', '--rapido'])
    case.unlink()
    run('sin casos ni medidas propias: test --rapido', ['test', '--rapido'])
    (OUT / 'oracle-resultados.txt').write_text('\n'.join(reports).replace(tmp, '<TEMP>'))
print('Inventario y reproducciones guardados en', OUT)
