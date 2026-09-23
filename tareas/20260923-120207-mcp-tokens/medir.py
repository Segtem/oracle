"""Medición reproducible; sólo escribe artefactos dentro de esta tarea."""
from pathlib import Path
import collections
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))
from tools import mcp
OUT = BASE / 'medicion'
OUT.mkdir(exist_ok=True)
def dump(x): return json.dumps(x, ensure_ascii=False, separators=(',', ':'))
def size(x): return len(dump(x).encode())
def metric(x):
    n = size(x)
    return {'bytes': n, 'tokens_estimados': n / 4}
def save(name, x): (OUT / name).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def delta(a, b): return {'antes':metric(a), 'despues':metric(b), 'ahorro_bytes':size(a)-size(b), 'ahorro_tokens_estimados':(size(a)-size(b))/4}
MID = 'meta.donde_nunca_agrega_filas'
# Evidencia transcrita literalmente del caso observado 049; no se atribuye una corrida nueva.
evidence = {'paso':[{'t':0,'operador':'de','filas_antes':0,'filas_despues':3}, {'t':1,'operador':'donde','filas_antes':3,'filas_despues':4}]}
calls = [
 ('catalogo', 'oracle_catalogo_efectivo', {}),
 ('evaluar', 'oracle_evaluar', {'medida':{'id':MID}, 'evidencia':evidence}),
 ('desafiar', 'oracle_desafiar', {'medida':{'id':MID}}),
 ('juzgar', 'oracle_juzgar', {'evidencia':evidence}),
 ('tareas', 'oracle_tareas', {'accion':'ver','id':'mcp-tokens'}),
 ('tareas_listar', 'oracle_tareas', {'accion':'listar','estado':'ABIERTA'}),
]
requests = [{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':mcp.PROTOCOLO,'capabilities':{},'clientInfo':{'name':'medicion-mcp-tokens','version':'1'}}}, {'jsonrpc':'2.0','method':'notifications/initialized'}, {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}}]
for i, (_, name, args) in enumerate(calls,3): requests.append({'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':name,'arguments':args}})
requests += [{'jsonrpc':'2.0','id':99,'method':'shutdown'}, {'jsonrpc':'2.0','method':'exit'}]
raw = ''.join(dump(x)+'\n' for x in requests).encode()
if '--replay' in sys.argv:
    response_bytes = (OUT/'respuestas.jsonl').read_bytes()
else:
    (OUT/'pedidos.jsonl').write_bytes(raw)
    run = subprocess.run([sys.executable, str(ROOT/'tools/mcp.py'),'--proyecto',str(ROOT)],input=raw,capture_output=True,cwd=ROOT)
    assert run.returncode == 0, run.stderr
    assert not run.stderr, run.stderr
    response_bytes = run.stdout
    (OUT/'respuestas.jsonl').write_bytes(response_bytes)
responses = {x['id']:x for x in map(json.loads,response_bytes.splitlines())}
tools = responses[2]['result']['tools']
base = {'tools':tools}
report = {'entorno':{'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'python':sys.version,'raiz':str(ROOT),'oracle':mcp.VERSION_DISTRIBUCION,'mcp_sha256':hashlib.sha256((ROOT/'tools/mcp.py').read_bytes()).hexdigest(),'tokenizadores_instalados':{m:bool(importlib.util.find_spec(m)) for m in ['tiktoken','tokenizers','transformers']},'regla':'bytes UTF-8 / 4; no son tokens reales ni facturación'}, 'tools_list':{'lista_sola':metric(tools),'result':metric(base),'jsonrpc_sin_lf':metric(responses[2]),'desglose':[]},'respuestas':{},'propuestas':{}}
for h in tools:
    parts = {k:size(h)-size({kk:vv for kk,vv in h.items() if kk!=k}) for k in ['description','inputSchema','outputSchema']}
    parts['resto'] = size(h)-sum(parts.values())
    report['tools_list']['desglose'].append({'name':h['name'],'total':metric(h),'bytes_por_campo_incluye_clave_y_coma':parts})
# Repeticiones exactas de propiedades inmediatas de esquemas: no cuenta nodos anidados otra vez.
repeated = collections.defaultdict(list)
for h in tools:
 for kind in ['inputSchema','outputSchema']:
  for key,value in h[kind].get('properties',{}).items(): repeated[(key,dump(value))].append(h['name']+'/'+kind)
report['repeticiones'] = [{'campo':k,'esquema':json.loads(v),'apariciones':locs,'bytes_valor_repetido_extra':(len(locs)-1)*len(v.encode())} for (k,v),locs in repeated.items() if len(locs)>1]
short = [
 'Consulta medidas efectivas del proyecto fijado. Sin ids: índice; con ids: detalle. No evalúa evidencia.',
 'Evalúa por id o texto sin guardar. Distingue verde, rojo y sin_evidencia; incluye umbral, testigos y alcance. No demuestra corrección de la medida.',
 'Desafía por id o texto con corpus, diferenciales y casos efímeros. Exige ambas polaridades y muta; informa discordancias, sobrevivientes y rechazos. No demuestra corrección semántica.',
 'Juzga evidencia contra el catálogo efectivo o ids. Informa no aplicadas, sombras y cotas. ok incluye sombras dentro de cota; no ejecuta escalares no autorizadas.',
 'Lee el tracker tareas/: listar, ver por id o prefijo, buscar texto o extraer hechos. Sin tracker: TRACKER_AUSENTE.',
]
no_out = copy.deepcopy(base)
for h in no_out['tools']: del h['outputSchema']
brief = copy.deepcopy(base)
for h, description in zip(brief['tools'],short): h['description']=description
both = copy.deepcopy(brief)
for h in both['tools']: del h['outputSchema']
for name, candidate in [('sin_outputSchema',no_out),('descripciones_breves',brief),('combinadas',both)]:
 report['propuestas'][name]=delta(base,candidate)
 save('candidato_'+name+'.json',candidate)
for i, (label,name,args) in enumerate(calls,3):
 r=responses[i]; result=r['result']
 assert not result['isError'], result
 payload=result['structuredContent']
 assert json.loads(result['content'][0]['text']) == payload
 (OUT/(label+'.payload.json')).write_text(dump(payload)+'\n')
 report['respuestas'][label]={'herramienta':name,'argumentos':args,'payload':metric(payload),'texto_decodificado_bytes':len(result['content'][0]['text'].encode()),'result':metric(result),'jsonrpc_sin_lf':metric(r)}
 only=copy.deepcopy(result); del only['structuredContent']
 report['propuestas']['una_copia_'+label]=delta(result,only)
 for fields,tag in [(['oracle_version','proyecto'],'sin_metadatos_'), (['entrada_sha256'],'sin_huella_')]:
  candidate={k:v for k,v in payload.items() if k not in fields}
  report['propuestas'][tag+label]=delta(payload,candidate)
 if label=='tareas_listar':
  candidate=copy.deepcopy(payload)
  for row in candidate['resultado']: del row['cuerpo']
  report['propuestas']['tareas_listar_sin_cuerpos']=delta(payload,candidate)
  save('candidato_tareas_listar_sin_cuerpos.json',candidate)
 if label=='catalogo':
  groups={}
  for row in payload['medidas']: groups.setdefault((row['origen'],row['fijacion']),[]).append(row['id'])
  candidate={k:v for k,v in payload.items() if k!='medidas'}
  candidate['grupos']=[{'origen':o,'fijacion':f,'ids':ids} for (o,f),ids in groups.items()]
  report['propuestas']['catalogo_agrupado']=delta(payload,candidate)
  save('candidato_catalogo_agrupado.json',candidate)
 if label in ['evaluar','juzgar']:
  def strip(x):
   if isinstance(x,dict): return {k:strip(v) for k,v in x.items() if k not in ['testigos','alcance','alcance_derivado']}
   if isinstance(x,list): return [strip(v) for v in x]
   return x
  report['propuestas']['NO_recortar_falsabilidad_'+label]=delta(payload,strip(payload))
save('resultados.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2))
