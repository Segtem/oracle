"""Reproducciones de auditoría; sólo escribe en temporales. Ejecutar desde cualquier ruta."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import catalogos.escalares
from nucleo import sintaxis, caso
from nucleo.algebra import AGREGADOS
from nucleo.medida import Medida, cargar, como_hechos
from nucleo.macro import macros_base
from nucleo.mutacion import mutantes
from nucleo.proyecto import (Proyecto, catalogo_efectivo, macros_del_proyecto,
                            relaciones_del_proyecto, escalares_del_proyecto)
from nucleo.marco import hechos_de_casos
from nucleo.unidad import hechos_de_unidades
from nucleo.relacion import cargar_fuente_relacion
from nucleo.generador import generar_caso
from nucleo.version import VERSION_DISTRIBUCION, VERSION_ALGEBRA, VERSION_SINTAXIS
from tools.aceptacion import casos

BASE = '''medida demo.prueba:
    de dato a
    donde a.x > 0
    resumen contar(1)
    umbral <= 0 segun contrato porque "prueba"
    ambito universal
    alcance "no ve otros datos"
'''
def titulo(s):
    print('\n### ' + s, flush=True)
def intentar(f):
    try:
        print(f())
    except (ValueError, TypeError) as e:
        print(type(e).__name__ + ': ' + str(e))
def m(texto):
    return Medida.de_datos(sintaxis.leer(texto))
def cli(*args):
    r = subprocess.run([sys.executable, str(ROOT/'tools/cli.py'), *map(str,args)],
                       cwd=ROOT, text=True, capture_output=True, timeout=90)
    print('$ python3 tools/cli.py ' + ' '.join(map(str,args)))
    print('exit=' + str(r.returncode))
    print((r.stdout+r.stderr).strip())
    return r

titulo('versión')
print(VERSION_DISTRIBUCION, VERSION_ALGEBRA, VERSION_SINTAXIS)
print(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
titulo('1.1')
for expr in ('a.x + 1', 'a.x - 1', 'a.x * 2', 'mas(a.x, 1)'):
    print(expr)
    intentar(lambda: sintaxis.leer(BASE.replace('a.x > 0',expr+' > 0'))[2][-1])
naval=Path('/home/workstation/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval')
for nombre in ('naval.alternancia_turnos.oracle','naval.turnos_sin_huecos.oracle'):
    for n,linea in enumerate((naval/nombre).read_text().splitlines(),1):
        if 'mas(' in linea: print(f'{nombre}:{n}: {linea.strip()}')

titulo('1.2')
for op in ('!=','<'):
    medida=m(BASE.replace('    donde a.x > 0',f'    unir dato b\n    donde a.id {op} b.id y a.x == b.x'))
    mutado=Medida.de_datos(next(d for nombre,d in mutantes(medida.a_datos()) if nombre=='aflojar_umbral'))
    for nombre,ev in [('rojo',{'dato':[{'id':'A','x':1},{'id':'B','x':1}]}),('verde',{'dato':[{'id':'A','x':1},{'id':'B','x':2}]})]:
        v,w=medida.evaluar(ev),mutado.evaluar(ev)
        print(f'{op} {nombre}: valor={v.valor}, original.ok={v.ok}, aflojar_umbral.ok={w.ok}')

titulo('2.1')
print('AGREGADOS =',sorted(AGREGADOS))
intentar(lambda:m(BASE.replace('contar(1)','contar_distintos(a.x)')))
agr='''    agrupar:
        clave grupo = a.g
        clave celda = a.x
    agrupar:
        clave grupo = grupo
        agregado distintos = contar(1)
'''
medida=m(BASE.replace('    donde a.x > 0\n',agr).replace('resumen contar(1)','resumen max(distintos)'))
v=medida.evaluar({'dato':[{'g':'A','x':1},{'g':'A','x':1},{'g':'A','x':2}]})
print('doble agrupar:',v.valor,v.testigos)

titulo('2.2')
print('macros:',sorted(macros_base()))
for macro in ('ninguno','ninguno-requiere','ninguno-par'):
    args=['demo.macro','dato','a']+(['b'] if macro=='ninguno-par' else [])
    args += [['y',['>', ['campo','a','x'],0],['<',['campo','a','x'],10]],'prueba','contrato','universal','no ve otros datos']
    medida=Medida.de_datos([macro,*args])
    print(macro,'requiere=',medida.requiere,'filtro compuesto valor=',medida.evaluar({'dato':[{'x':1}]}).valor)
intentar(lambda:sintaxis.leer(BASE.replace('medida demo.prueba:', 'ninguno demo.prueba:').replace('    resumen contar(1)\n','').replace('    ambito universal','    requiere dato\n    ambito universal')))
for nombre in ('naval.flota_reglamentaria.oracle','naval.turnos_sin_huecos.oracle'):
    texto=(naval/nombre).read_text()
    print(nombre + ':\n' + texto)

titulo('3.1')
for pos in ('resumen','umbral','ambito'):
    texto=BASE.replace('    '+pos, '    requiere dato\n    '+pos)
    print('requiere antes de',pos)
    intentar(lambda:m(texto).requiere)

titulo('3.2')
medida=m(BASE)
meta=cargar(ROOT/'catalogos/meta/meta.ninguna_medida_sin_alcance.oracle')
print('alcance=',medida.alcance, '; meta.ok=',meta.evaluar({'medida':como_hechos([medida])}).ok)
proyectos=[ROOT,Path('/home/workstation/Dev/jam/medidas'),Path('/home/workstation/Dev/games/unreal/LyraGASP/medidas')]
for p in proyectos:
    encontrados=[]
    for f in sorted((p/'catalogos').rglob('*')):
        if f.suffix in ('.json','.oracle') and re.search(r'contiene\s*\(|"contiene"',f.read_text()): encontrados.append(str(f.relative_to(p)))
    print(p, 'usos contiene:',encontrados)

titulo('4.1')
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'dato.oracle'
    p.write_text('relacion dato:\n    campo x entero celdas\n')
    intentar(lambda:cargar_fuente_relacion(p))
    p.write_text(json.dumps(['relacion','dato',['campos',['campo','x','entero','celdas']],['alcance','no ve otros datos']]))
    print('JSON dentro de .oracle:',cargar_fuente_relacion(p))

for p in proyectos[1:]:
    titulo('4.2 / 4.3 / 5.2 '+str(p))
    proy=Proyecto(p)
    with escalares_del_proyecto(proy,confiar=True):
        cat=catalogo_efectivo(proy,macros=macros_del_proyecto(proy))
        hechos={'medida':como_hechos(cat.values()),**hechos_de_unidades(cat.values(),relaciones_del_proyecto(proy)),**hechos_de_casos(cat,casos(proy))}
        sombras=json.loads((p/'oracle.json').read_text())['sombra']
        for mid in ('meta.toda_cantidad_comparada_tiene_unidad_derivable','meta.todo_umbral_declara_de_donde_sale','meta.la_medida_no_se_fija_solo_con_evidencia_fabricada'):
            v=cat[mid].evaluar(hechos)
            print(mid,'cota=',sombras[mid]['cota'],'valor=',v.valor,'ok=',v.ok)
        for mid in ('vault.enlace_resuelve','recarga.montage_en_slot_cuerpo_entero'):
            if mid in cat: print(mid,'segun=',cat[mid].segun)

titulo('5.1')
datos={'id':'999-vacio','fecha':'2026-09-23','origen':{'repo':'test','commit':'sin-commit'},'titulo':'vacío','etiqueta':'verde_correcto','sintoma':'prueba','como_se_detecto':'observacion','medida':'demo.prueba','evidencia':{'impacto':[]},'leccion':'prueba'}
superficie=caso.imprimir(datos)
print(superficie)
print('relectura evidencia=',caso.leer(superficie)['evidencia'])

titulo('5.2 conversión sin transcribir filas')
datos['procedencia']='observada'
datos['origen'].update(comando='sensor --hechos',registro='captura.json')
datos['evidencia']={'impacto':[{'x':i,'y':i%10} for i in range(1000)]}
texto=caso.imprimir(datos)
print('1000 filas: leer(imprimir(datos)) == datos:',caso.leer(texto)==datos)
cli('caso','--help')
print('sombra Oracle:',json.loads((ROOT/'oracle.json').read_text()).get('sombra'))

titulo('5.3')
guia=Path('/home/workstation/TestOracleEjemplo/GUIA22.md').read_text()
texto=re.search(r'```\n(medida flota.dos_barcos_en_la_misma_celda:.*?)\n```',guia,re.S).group(1)+'\n'
print(texto)
with tempfile.TemporaryDirectory() as td:
    p=Path(td)
    for d in ('catalogos','corpus','diferencial'): (p/d).mkdir()
    (p/'catalogos/demo.oracle').write_text(texto)
    rc,resultado=generar_caso(Proyecto(p),'flota.dos_barcos_en_la_misma_celda')
    print('exit=',rc,'archivos corpus=',list((p/'corpus').iterdir()))

titulo('6.1 / 6.2')
with tempfile.TemporaryDirectory() as td:
    p=Path(td)
    for d in ('catalogos','corpus','diferencial'): (p/d).mkdir()
    (p/'oracle.json').write_text(json.dumps({'esquema':'oracle.proyecto/v1','catalogo_base':False}))
    (p/'catalogos/demo.oracle').write_text(BASE)
    (p/'hechos.json').write_text('{"otra": []}')
    cli('juzgar','--proyecto',p,'--con',p/'hechos.json')
    (p/'catalogos/otra.oracle').write_text(BASE.replace('demo.prueba','demo.otra').replace('de dato a','de otra a'))
    cli('juzgar','--proyecto',p,'--con',p/'hechos.json')
    (p/'escalares.py').write_text('# Sin funciones; ninguna medida usa escalares externas.\n')
    for args in [('test','--rapido'),('juzgar','--con',p/'hechos.json'),('revisar',p/'catalogos/demo.oracle'),('medida','listar'),('caso','generar','demo.prueba')]:
        cli(*args,'--proyecto',p)
    cli('medida','listar','--proyecto',p,'--confiar-escalares')
    cli('caso','listar','--proyecto',p)


titulo('5.2 deuda de procedencia Oracle')
proy=Proyecto(ROOT)
cat=catalogo_efectivo(proy,macros=macros_del_proyecto(proy))
mid='meta.todo_caso_observado_declara_de_donde_salio'
v=cat[mid].evaluar(hechos_de_casos(cat,casos(proy)))
print(mid,'valor=',v.valor,'ok=',v.ok)

titulo('6.3 reproducción actual en copia del laboratorio')
import shutil
lab=Path('/home/workstation/Dev/lab/batalla_naval_test/batalla_naval_con_oracle')
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'juego'
    shutil.copytree(lab,p)
    for estado in ('conservado','game.js roto','sin casos'):
        if estado=='game.js roto': (p/'game.js').write_text('ESTO NO ES JAVASCRIPT VALIDO {{{\n')
        if estado=='sin casos':
            for f in (p/'corpus').rglob('*.caso'): f.unlink()
        print(estado)
        cli('test','--rapido','--proyecto',p)
