from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import sys

raiz = Path(sys.argv[1]).resolve()
class Pagina(HTMLParser):
    def __init__(self, ruta):
        super().__init__()
        self.ids, self.refs = [], []
        self.feed(ruta.read_text())
    def handle_starttag(self, tag, attrs):
        datos = dict(attrs)
        if 'id' in datos:
            self.ids.append(datos['id'])
        for atributo in ('href', 'src'):
            if atributo in datos:
                self.refs.append(datos[atributo])

paginas = {p: Pagina(p) for p in sorted((raiz/'docs').rglob('*.html'))}
errores, locales = [], 0
for origen, datos in paginas.items():
    for ident, n in Counter(datos.ids).items():
        if n > 1:
            errores.append(f'{origen.relative_to(raiz)}: ID duplicado {ident}')
    for ref in datos.refs:
        partes = urlsplit(ref)
        if partes.scheme or partes.netloc:
            continue
        locales += 1
        destino = (origen.parent / unquote(partes.path)).resolve() if partes.path else origen
        if destino.is_dir():
            destino /= 'index.html'
        if not destino.exists():
            errores.append(f'{origen.relative_to(raiz)}: no existe {ref}')
        elif partes.fragment and destino in paginas and unquote(partes.fragment) not in paginas[destino].ids:
            errores.append(f'{origen.relative_to(raiz)}: falta ancla {ref}')
print(json.dumps({'paginas':len(paginas),'enlaces_y_recursos_locales':locales,'errores':errores},ensure_ascii=False,indent=2))
raise SystemExit(bool(errores))
