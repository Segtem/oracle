"""Segunda pasada congelada. Sólo correr consume API; no hay reintentos."""
import hashlib, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
D = Path(__file__).resolve().parent

def save(name, obj):
    (D/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def preflight():
    assert not list(D.glob('solicitud-*.json')), 'No repetir una pasada parcial'
    hashes = json.loads((D/'integridad.json').read_text())
    for name, digest in hashes.items():
        assert hashlib.sha256((D/name).read_bytes()).hexdigest() == digest, name
    records = json.loads((D/'ciego/registros.json').read_text())
    juicio = json.loads((D/'juicio-ciego-claude.json').read_text())
    refs = {r['id']: r for r in juicio}
    assert len(refs) == len(juicio) == len(records) == 25
    assert set(refs) == {r['id'] for r in records}
    for r in records:
        j = refs[r['id']]
        assert type(j['porque_origen']) is bool
        assert j['justificacion_origen'] and isinstance(j['cita_origen'], str)
        assert j['cita_origen'] in r['porque']
        assert (type(j['porque_vecino']) is bool) if r['aplica_vecino'] else (j['porque_vecino'] is None)
        assert j['justificacion_vecino']
    save('referencia-sellada.json', dict(
        fecha_registro_utc=datetime.now(timezone.utc).isoformat(),
        sha256=hashlib.sha256((D/'juicio-ciego-claude.json').read_bytes()).hexdigest(),
        entradas=len(juicio), si=sum(j['porque_origen'] for j in juicio),
        version_claude='No consignada en el archivo recibido',
        fecha_juicio='No consignada en el archivo recibido',
        procedencia='Usuario confirma sesión limpia de Claude que sólo vio CRITERIO.md, INSTRUCCIONES.md y registros.json; nota de tarea documenta delegación el 2026-09-23 UTC.',
        exposicion_operador='Leyó el juicio v2 para validarlo antes de llamar; no se envía al modelo ni altera el criterio.',
        hashes_insumos=hashes))

def run():
    batch=json.loads((D/'protocolo.json').read_text()); records=json.loads((D/'lote.json').read_text()); ledger=[]
    preflight()
    assert not (D/'corridas.json').exists(), 'No repetir automáticamente'
    key=os.environ['OPENROUTER_API_KEY']
    for n,start in enumerate(range(0,len(records),12),1):
        assert n<=6 and sum(x['costo_usd'] or 0 for x in ledger)<0.05
        rows=records[start:start+12]
        payload=dict(model='typesafe/jev-1.13',state={'description':(D/'CRITERIO.md').read_text(), 'records':rows},questions={f"{r['id']}__{q}":dict(type='noul',instructions=f"Para el registro {r['id']}: {text}") for r in rows for q,text in batch['preguntas'].items() if q != 'porque_vecino' or r['aplica_vecino']})
        save(f'solicitud-{n:02}.json',payload)
        t=time.perf_counter();stamp=datetime.now(timezone.utc).isoformat()
        try:
            response=requests.post('https://openrouter.ai/api/alpha/decisions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=payload,timeout=60)
        except requests.RequestException:
            save('error-transporte.json',dict(corrida=n,costo_usd=None,estado='Desconocido; no reintentar sin conciliar facturación'))
            raise SystemExit('Error de transporte; detalle omitido para proteger credenciales')
        elapsed=time.perf_counter()-t
        raw=response.content
        assert key.encode() not in raw, 'Respuesta refleja credencial; no guardar'
        (D/f'respuesta-cruda-{n:02}.json').write_bytes(raw)
        data=response.json(); cost=data.get('usage',{}).get('cost')
        ledger.append(dict(corrida=n,fecha=stamp,http=response.status_code,latencia_segundos=elapsed,costo_usd=cost,preguntas=len(payload['questions']),sha256_respuesta=hashlib.sha256(raw).hexdigest()))
        save('corridas.json',ledger)
        print(json.dumps(ledger[-1]),flush=True)
        if response.status_code!=200 or cost is None: raise SystemExit('Detenido: error o costo desconocido')
        assert set(data['answers'])==set(payload['questions'])
        assert all(a['type']=='noul' and 0<=a['noul']<=1 for a in data['answers'].values())
    save('respuestas-guardadas.json',dict(fecha=datetime.now(timezone.utc).isoformat(),corridas=len(ledger),costo_total_usd=sum(x['costo_usd'] for x in ledger),estado='Completo; referencia validada y sellada antes de las llamadas'))


if __name__ == '__main__':
    if sys.argv[1:] != ['correr']:
        raise SystemExit('Uso: correr.py correr (consume API)')
    run()
