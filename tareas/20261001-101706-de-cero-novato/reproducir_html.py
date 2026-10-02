from html.parser import HTMLParser
from pathlib import Path
import difflib
import os
import re
import shlex
import subprocess
import sys

class Bloques(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pre = None
        self.code = False
        self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag == 'pre': self.pre = [dict(attrs), '']
        elif tag == 'code' and self.pre is not None: self.code = True
    def handle_endtag(self, tag):
        if tag == 'code': self.code = False
        elif tag == 'pre' and self.pre is not None:
            self.blocks.append(self.pre)
            self.pre = None
    def handle_data(self, data):
        if self.code: self.pre[1] += data

root = Path('/tmp/oracle-cierre-novato')
page = Path('/home/workstation/Dev/oracle/docs/de-cero.html')
parser = Bloques()
parser.feed(page.read_text())
work = root / 'recorrido-html-final'
work.mkdir()
cwd = work
env = os.environ.copy()
env.pop('ORACLE_PROYECTO', None)
env.pop('PYTHONPATH', None)
env['PATH'] = str(root / 'agy2/uv-isolated/bin') + os.pathsep + env['PATH']
for who in ('AUTHOR', 'COMMITTER'):
    env['GIT_'+who+'_NAME'] = 'Validacion de guia'
    env['GIT_'+who+'_EMAIL'] = 'guia@example.invalid'

def normalizar(text):
    text = text.replace(str(work/'batalla-naval'), 'batalla-naval').replace(str(work), '.')
    text = re.sub(r'\b\d+(?:[.,]\d+)?\s*(?:ms|s|segundos?)\b', '<tiempo>', text)
    return text.rstrip('\n')

pending = None
files = 0
steps = 0
for attrs, body in parser.blocks:
    kind = attrs.get('class', '')
    label = attrs.get('data-lenguaje', '')
    if kind == 'archivo':
        dest = cwd / label
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding='utf-8')
        files += 1
    elif label == 'bash':
        pending = ''
        steps += 1
        for line in body.splitlines():
            args = shlex.split(line)
            if args[:3] == ['uv', 'tool', 'install']:
                print('INSTALACIÓN: se reutiliza oracle 0.38.0 aislado que instaló agy2; no se repite la descarga.')
                continue
            if args[0] == 'cd':
                cwd = cwd / args[1]
                continue
            p = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
            print('$', line, '| código', p.returncode)
            print(p.stdout+p.stderr)
            if args[0] != 'git': pending += p.stdout+p.stderr
            elif p.returncode: raise AssertionError('Falló Git')
    elif kind == 'salida' and pending is not None:
        a, b = normalizar(body), normalizar(pending)
        if a != b:
            print(''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile='HTML', tofile='real')))
            raise AssertionError(f'Salida distinta en paso {steps}')
        pending = None
p = subprocess.run([sys.executable, 'verificar_oraculo.py'], cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
print('$ python3 verificar_oraculo.py | código', p.returncode)
print(p.stdout+p.stderr)
assert p.returncode == 0
assert 'Leída de hechos_partida.json' in p.stdout
print(f'REPRODUCCIÓN HTML OK: {steps} bloques de comandos, {files} escrituras de archivos, salidas comparadas; script complementario OK.')
