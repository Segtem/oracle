"""Reproduce comparación y calibración descriptiva sin API."""
import hashlib
import json
import math
from pathlib import Path
D = Path(__file__).resolve().parent

def read(n):
    return json.loads((D/n).read_text())

def save(n, x):
    (D/n).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')

def metricas(rows):
    n = len(rows)
    bins = []
    for lo, hi in [(0,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1)]:
        subset = [r for r in rows if lo <= r['p_si'] and (r['p_si'] < hi or hi == 1)]
        if subset:
            bins.append(dict(desde=lo,hasta=hi,n=len(subset),p_media=sum(r['p_si'] for r in subset)/len(subset),fraccion_si=sum(r['claude'] for r in subset)/len(subset)))
    return dict(n=n, acuerdo=sum(r['acuerdo'] for r in rows),
        tp=sum(r['jev'] and r['claude'] for r in rows),
        tn=sum(not r['jev'] and not r['claude'] for r in rows),
        fp=sum(r['jev'] and not r['claude'] for r in rows),
        fn=sum(not r['jev'] and r['claude'] for r in rows),
        brier=sum((r['p_si']-r['claude'])**2 for r in rows)/n,
        log_loss=sum(-math.log(max(1e-15,r['p_si'] if r['claude'] else 1-r['p_si'])) for r in rows)/n,
        p_media=sum(r['p_si'] for r in rows)/n,fraccion_si=sum(r['claude'] for r in rows)/n,
        brier_constante_no=sum(r['claude'] for r in rows)/n,
        ece=sum(b['n']*abs(b['p_media']-b['fraccion_si']) for b in bins)/n,bins=bins)

def main():
    assert hashlib.sha256((D/'juicio-ciego-claude.json').read_bytes()).hexdigest() == read('referencia-sellada.json')['sha256']
    clave={r['id']:r for r in read('clave-operador.json')}
    records={r['id']:r for r in read('lote.json')}
    answers={}; modelos=set(); proveedores=set()
    ledger=read('corridas.json')
    for c in ledger:
        n=c['corrida']; raw=(D/f'respuesta-cruda-{n:02}.json').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==c['sha256_respuesta']
        d=json.loads(raw); req=read(f'solicitud-{n:02}.json')
        assert req['state']['description']==(D/'CRITERIO.md').read_text()
        assert all(r==records[r['id']] for r in req['state']['records'])
        assert set(d['answers'])==set(req['questions'])
        assert not set(answers)&set(d['answers'])
        answers.update(d['answers']); modelos.add(d['model']);proveedores.add(d['provider'])
    esperado={f"{r['id']}__{q}" for r in records.values() for q in ['porque_origen','porque_vecino'] if q=='porque_origen' or r['aplica_vecino']}
    assert set(answers)==esperado
    rows=[]
    for j in read('juicio-ciego-claude.json'):
        rid=j['id']; p=answers[rid+'__porque_origen']['noul']
        rows.append(dict(id=rid,medida=clave[rid]['medida'],control=clave[rid]['control'],claude=j['porque_origen'],p_si=p,jev=p>=.5,acuerdo=(p>=.5)==j['porque_origen'],porque_vecino=None))
    save('comparaciones.json',rows)
    result=dict(modelos=sorted(modelos),proveedores=sorted(proveedores),
        reales=metricas([r for r in rows if not r['control']]),controles=metricas([r for r in rows if r['control']]),total=metricas(rows),
        p2=dict(n_referencia=0,acuerdo=None,nota='25 umbrales <= 0 (límite cero). En lote completo sólo v003 tiene límite 90 y respuesta P2, sin referencia; no se evalúa.'),
        solicitudes=len(ledger),respuestas=len(answers),costo_usd=sum(c['costo_usd'] for c in ledger),latencia_segundos=sum(c['latencia_segundos'] for c in ledger),
        discrepancias=[r for r in rows if not r['acuerdo']],
        sin_referencia=[dict(id=rid,pregunta=q,**v) for k,v in answers.items() for rid,q in [k.split('__')] if q=='porque_vecino'])
    save('analisis.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
