"""Preparación y única pasada de Jev. No lee el juicio ciego. Ejecutar desde el repo."""
import hashlib, json, os, random, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import catalogos
from nucleo.medida import cargar_catalogo
D = Path(__file__).resolve().parent

def save(name, obj):
    (D/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def prepare():
    assert not (D/'lote.json').exists(), 'No sobrescribir un lote fijado'
    cat = cargar_catalogo(ROOT/'catalogos', ROOT/'perfiles/python/catalogos')
    rows = [dict(medida=m.id, alcance=m.alcance, porque=m.porque, umbral=f'{m.op} {m.limite}', segun=m.segun) for m in sorted(cat.values(), key=lambda m:m.id)]
    save('catalogo-congelado.json', rows)
    qs = {'alcance_concreto':'¿El alcance nombra algo concreto que la medida no mira?',
          'porque_defiende':'¿El porque explica por qué ESE número del umbral y no otro?',
          'alcance_vacio':'¿El alcance es una promesa vacía del tipo «no ve todo lo demás»?'}
    rng = random.Random(20260922)
    controls=[]
    for i, original in enumerate(rng.sample(rows,10)):
        row=dict(original)
        row['alcance']=['No ve nada más.','No cubre otros casos.','No ve todo lo demás.','No cubre el resto.','No mira otras cosas.'][i%5]
        row['porque']=['Porque sí.','Es lo razonable.','Es el número adecuado.','Porque se decidió así.','Es lo que corresponde.'][i%5]
        controls.append((row, original['medida']))
    tagged=[(r,False,None) for r in rows]+[(r,True,src) for r,src in controls]
    rng.shuffle(tagged)
    mapping=[]; wire=[]
    for i,(r,control,src) in enumerate(tagged):
        rid=f'r{i+1:03}'
        wire.append(dict(id=rid,**{k:v for k,v in r.items() if k!='medida'}))
        mapping.append(dict(id=rid,medida=r['medida'],control=control,esperado={k:v for k,v in zip(qs,[False,False,True])} if control else None))
    save('lote.json',dict(preguntas=qs,records=wire))
    save('clave-controles.json',mapping)
    save('protocolo.json',dict(fecha=datetime.now(timezone.utc).isoformat(),semilla=20260922,modelo='typesafe/jev-1.13',reales=len(rows),controles=10,preguntas=qs,umbral_si=0.5,tamano_lote=12,regla='Sí si noul >= 0.5; control atrapado si alguna respuesta señala defecto; informar también patrón completo.',presupuesto_local_usd=0.05,max_corridas=6,fuente_api='https://openrouter.ai/labs/jev/triage',limitaciones='La tarea revela el patrón agregado de Claude. No se leyó su archivo. Controles sustituyen ambos campos para fijar las tres polaridades opuestas.',sha256_lote=hashlib.sha256((D/'lote.json').read_bytes()).hexdigest()))
    print('Lote fijado:',len(rows),'reales + 10 controles')

def run():
    batch=json.loads((D/'lote.json').read_text()); records=batch['records']; ledger=[]
    assert not (D/'corridas.json').exists(), 'No repetir automáticamente'
    key=os.environ['OPENROUTER_API_KEY']
    for n,start in enumerate(range(0,len(records),12),1):
        assert n<=6 and sum(x['costo_usd'] or 0 for x in ledger)<0.05
        rows=records[start:start+12]
        payload=dict(model='typesafe/jev-1.13',state={'description':'Prosa de medidas de Oracle. alcance declara puntos ciegos; porque defiende el umbral. Evaluar sólo el registro indicado, sin completar ni mejorar su texto.', 'records':rows},questions={f"{r['id']}__{q}":dict(type='noul',instructions=f"Para el registro {r['id']}: {text}") for r in rows for q,text in batch['preguntas'].items()})
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
    save('respuestas-guardadas.json',dict(fecha=datetime.now(timezone.utc).isoformat(),corridas=len(ledger),costo_total_usd=sum(x['costo_usd'] for x in ledger),estado='Completo; habilitada lectura del juicio ciego'))

if __name__=='__main__':
    {'preparar':prepare,'correr':run}[sys.argv[1]]()
