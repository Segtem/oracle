"""Análisis sin red; requiere que las seis respuestas estén guardadas."""
import json, hashlib, statistics
from pathlib import Path
from datetime import datetime, timezone
D=Path(__file__).resolve().parent

def load(p): return json.loads((D/p).read_text())
def save(p,x):
    target=D/p;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
assert load('respuestas-guardadas.json')['corridas']==6
blind=load('juicio-ciego-claude.json'); qs=list(load('lote.json')['preguntas']); mapping=load('clave-controles.json')
answers={}
for n in range(1,7): answers.update(load(f'respuesta-cruda-{n:02}.json')['answers'])
rows=[]; comparisons=[]
for rec in mapping:
    for j,q in enumerate(qs):
        p=answers[f"{rec['id']}__{q}"]['noul'];value=p>=0.5
        row=dict(registro=rec['id'],medida=rec['medida'],pregunta=q,respuesta=value,probabilidad=p)
        rows.append(row)
        expected=rec['esperado'][q] if rec['control'] else (blind['respuestas'][rec['medida']][j]=='si' if rec['medida'] in blind['respuestas'] else None)
        if expected is not None: comparisons.append(dict(**row,control=rec['control'],esperado=expected,acuerdo=value==expected))
save('afirmacion_prosa.json',{'afirmacion_prosa':rows})
save('comparaciones.json',comparisons)
real=[c for c in comparisons if not c['control']];ctrl=[c for c in comparisons if c['control']]
metrics={}
for q in qs:
    a=[c for c in real if c['pregunta']==q];b=[c for c in ctrl if c['pregunta']==q]
    metrics[q]=dict(reales_acuerdo=sum(c['acuerdo'] for c in a),reales_total=len(a),controles_acuerdo=sum(c['acuerdo'] for c in b),controles_total=len(b))
ledger=load('corridas.json')
summary=dict(preguntas=metrics,reales_acuerdo=sum(c['acuerdo'] for c in real),reales_total=len(real),reales_patron_completo=sum(all(c['acuerdo'] for c in real if c['registro']==r) for r in {c['registro'] for c in real}),controles_acuerdo=sum(c['acuerdo'] for c in ctrl),controles_total=len(ctrl),controles_atrapados=sum(any(c['acuerdo'] for c in ctrl if c['registro']==r) for r in {c['registro'] for c in ctrl}),controles_patron_completo=sum(all(c['acuerdo'] for c in ctrl if c['registro']==r) for r in {c['registro'] for c in ctrl}),costo_total_usd=sum(c['costo_usd'] for c in ledger),latencia_total_segundos=sum(c['latencia_segundos'] for c in ledger),latencia_mediana_segundos=statistics.median(c['latencia_segundos'] for c in ledger),desacuerdos=[c for c in real if not c['acuerdo']],sha256_juicio=hashlib.sha256((D/'juicio-ciego-claude.json').read_bytes()).hexdigest(),fecha_analisis=datetime.now(timezone.utc).isoformat())
save('analisis.json',summary)
# Corpus antes de escribir la medida; cuatro casos fijan las tres ramas y el verde.
project=Path('proyecto-sensor');mid='prosa.senales_de_prosa_deficiente'
for i,(q,answer) in enumerate([(qs[0],False),(qs[1],False),(qs[2],True),(qs[0],True)],1):
    row=next(r for r in rows if r['pregunta']==q and r['respuesta']==answer)
    cid=f'{i:03}-'+('senal-'+q.replace('_','-') if i<4 else 'sin-senal')
    evidence={'afirmacion_prosa':[row]}
    if i==4:
        healthy=next(rec['id'] for rec in mapping if all(r['respuesta']==(r['pregunta']!=qs[2]) for r in rows if r['registro']==rec['id']))
        evidence={'afirmacion_prosa':[r for r in rows if r['registro']==healthy]}
    save(str(project/'corpus/prosa'/f'{cid}.json'),dict(id=cid,fecha='2026-09-22',origen={'repo':'Oracle', 'comando':'python3 tareas/20260922-190222-jev-prueba/experimento.py correr','archivo':'../respuesta-cruda-01.json a respuesta-cruda-06.json'},procedencia='observada',titulo=cid,etiqueta='falso_verde' if i<4 else 'verde_correcto',sintoma='Señal probabilística observada; se comprueba el cableado del sensor, no la verdad de la prosa.',como_se_detecto='persona',medida=mid,evidencia=evidence,leccion='Oracle juzga respuestas del sensor; no certifica su exactitud semántica.'))
    save(f'caso-evidencia-{i:02}.json',evidence)
save(str(project/'oracle.json'),{'esquema':'oracle.proyecto/v1','algebra':'0.7','catalogo_base':False})
path=D/project/'catalogos/prosa'/f'{mid}.oracle';path.parent.mkdir(parents=True,exist_ok=True)
path.write_text('''medida prosa.senales_de_prosa_deficiente:
    de afirmacion_prosa a
    donde (a.pregunta == "alcance_concreto" y a.respuesta == false) o (a.pregunta == "porque_defiende" y a.respuesta == false) o (a.pregunta == "alcance_vacio" y a.respuesta == true)
    resumen contar(1)
    umbral <= 0 segun contrato porque "cero señales adversas para declarar verde en esta prueba del sensor; cada señal exige revisión de la prosa, no prueba un defecto"
    requiere afirmacion_prosa
    ambito universal
    alcance "Hechos probabilísticos producidos por Jev typesafe/jev-1.13-20260917, con respuesta sí desde P(sí) >= 0.5. El margen de error se mide en analisis.json: muestra pequeña, sin garantía de calibración ni generalización. NO juzga la verdad de la prosa, ni detecta preguntas o medidas ausentes de una relación parcialmente entregada."
''')
save(str(project/'relaciones/afirmacion_prosa.json'),['relacion','afirmacion_prosa',['campos',*(['campo',k,t,'sin_unidad'] for k,t in [('registro','texto'),('medida','texto'),('pregunta','texto'),('respuesta','booleano'),('probabilidad','flotante')])],['alcance','Respuestas del sensor Jev; probabilidad es P(sí), no probabilidad de que la clasificación sea correcta.']])
print(json.dumps(summary,ensure_ascii=False,indent=2))
