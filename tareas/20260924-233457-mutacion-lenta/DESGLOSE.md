# Desglose temporal de dos mutantes de `tools/cli.py`

Fecha: 2026-09-24. Python 3.14.7, x86_64, revisión `8b4e511`. Tiempos de pared en segundos, `time.perf_counter`. Cada celda muestra las repeticiones 1 / 2 / 3.

## Mutantes y resultado

- **Muerte temprana:** `tools/cli.py:293:7:comparador` (`In → NotIn`); falla en `tests.test_reportar`, después de 14 tests de ese módulo. Código 1 (`tests_fallaron`) en las tres repeticiones.
- **Muerte tardía:** `tools/cli.py:83:19:constante` (`10 → 11`); pasa `test_reportar` (21), `test_vigilar` (33), `test_biblioteca` (27) y `test_tareas` (21), y falla en `test_cli` tras 91 tests de ese módulo. Código 1 (`tests_fallaron`) en las tres repeticiones.
- Ambos IDs están en `tareas/20260924-154951-corte-030/verificacion/tools_cli.log`; el cierre de ese log registra 595 muertos y ningún superviviente.

## Medidas

| Fase | Temprano: 1 / 2 / 3 (s) | Tardío: 1 / 2 / 3 (s) |
|---|---:|---:|
| Preparar fuente mutada (AST) | 0.0173 / 0.0147 / 0.0150 | 0.0150 / 0.0171 / 0.0153 |
| Escritura atómica del mutante | 0.0002 / 0.0001 / 0.0002 | 0.0001 / 0.0002 / 0.0002 |
| Barrido previo de cachés | 0.0015 / 0.0012 / 0.0016 | 0.0013 / 0.0017 / 0.0017 |
| Limpieza previa de cachés | 0.0021 / 0.0022 / 0.0023 | 0.0022 / 0.0024 / 0.0023 |
| Popen (dentro de ejecutar_tests) | 0.0012 / 0.0012 / 0.0012 | 0.0012 / 0.0016 / 0.0013 |
| Desde inicio de Popen hasta primera marca del runner | 0.0101 / 0.0101 / 0.0101 | 0.0102 / 0.0103 / 0.0103 |
| Import del runner y sus dependencias | 0.1056 / 0.1045 / 0.1047 | 0.1056 / 0.1060 / 0.1058 |
| Import tests.test_reportar | 0.1854 / 0.1864 / 0.1861 | 0.1859 / 0.1869 / 0.1881 |
| Carga de suite tests.test_reportar | 0.0001 / 0.0001 / 0.0001 | 0.0001 / 0.0001 / 0.0001 |
| Ejecución tests.test_reportar | 0.0018 / 0.0018 / 0.0018 | 0.0032 / 0.0032 / 0.0032 |
| Import tests.test_vigilar | — / — / — | 0.0041 / 0.0042 / 0.0042 |
| Carga de suite tests.test_vigilar | — / — / — | 0.0001 / 0.0001 / 0.0001 |
| Ejecución tests.test_vigilar | — / — / — | 0.0157 / 0.0159 / 0.0159 |
| Import tests.test_biblioteca | — / — / — | 0.0023 / 0.0023 / 0.0024 |
| Carga de suite tests.test_biblioteca | — / — / — | 0.0001 / 0.0001 / 0.0001 |
| Ejecución tests.test_biblioteca | — / — / — | 0.2389 / 0.2334 / 0.2361 |
| Import tests.test_tareas | — / — / — | 0.0109 / 0.0107 / 0.0112 |
| Carga de suite tests.test_tareas | — / — / — | 0.0002 / 0.0002 / 0.0002 |
| Ejecución tests.test_tareas | — / — / — | 0.0098 / 0.0096 / 0.0098 |
| Import tests.test_cli | — / — / — | 0.0084 / 0.0075 / 0.0077 |
| Carga de suite tests.test_cli | — / — / — | 0.0004 / 0.0004 / 0.0004 |
| Ejecución tests.test_cli | — / — / — | 7.0922 / 7.0978 / 7.0837 |
| Subproceso completo (ejecutar_tests) | 0.3656 / 0.3655 / 0.3654 | 7.7268 / 7.7277 / 7.7276 |
| Barrido posterior de cachés | 0.0023 / 0.0021 / 0.0018 | 0.0019 / 0.0017 / 0.0023 |
| Limpieza posterior de cachés | 0.0022 / 0.0022 / 0.0027 | 0.0029 / 0.0022 / 0.0022 |
| Restauración atómica | 0.0002 / 0.0002 / 0.0002 | 0.0002 / 0.0002 / 0.0002 |
| Total medido por mutante | 0.3913 / 0.3882 / 0.3891 | 7.7503 / 7.7532 / 7.7517 |

El descubrimiento general **no ocurrió** en ninguna de las seis ejecuciones: ambos mutantes murieron en módulos prioritarios, antes de `discover`. Tampoco se cargaron los módulos prioritarios posteriores a `test_cli` para el tardío. `failfast=True` permaneció activo.

`Popen`, arranque, import del runner y fases del hijo están **incluidos** en `ejecutar_tests_total`: sus filas no deben sumarse otra vez. El intervalo «desde inicio de Popen hasta primera marca» incluye `Popen` y la inicialización del intérprete; el tiempo exclusivo de inicialización es aproximadamente ese intervalo menos `Popen`. Las marcas de import miden `importlib.import_module` (incluidas dependencias transitivas); las de carga miden `loadTestsFromName` después del import. La diferencia entre el total del subproceso y la suma de marcas internas contiene argumentos, creación de cargador, salida, hilos lectores, espera y cierre del prefijo temporal de pyc. `total_mutante` suma las fases externas sin duplicar las subfases del hijo. La copia inicial del proyecto se hizo una vez y quedó fuera del total por mutante; no se corrió línea base durante esta medición.

## Reproducción exacta

Desde la raíz del repositorio en la revisión indicada, guardar el siguiente bloque Python como `/tmp/medir_mutacion_lenta.py` y ejecutar:

```bash
python3 /tmp/medir_mutacion_lenta.py tools/cli.py:293:7:comparador tools/cli.py:83:19:constante --reps 3 > /tmp/medicion_final.jsonl
```

El script usa `_copiar_proyecto` para crear una única copia temporal, instrumenta **sólo** `tools/ejecutar_suite_mutacion.py` dentro de esa copia, aplica cada mutante con las funciones de producción, ejecuta el mismo comando y las mismas prioridades de `tools/mutar_codigo.py`, comprueba y limpia cachés antes y después, y restaura `tools/cli.py` en `finally`. La copia se elimina al terminar. El arnés original y el repositorio de trabajo no se instrumentan. Cada línea JSON de salida conserva los tiempos sin redondear y el estado del resultado.

```python
import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ORIG = Path.cwd()
sys.path.insert(0, str(ORIG))
from perfiles.python import mutacion_codigo as m
from tools.mutar_codigo import PRIORIDADES

p = argparse.ArgumentParser()
p.add_argument('ids', nargs='+')
p.add_argument('--reps', type=int, default=3)
a = p.parse_args()
original = (ORIG / 'tools/cli.py').read_text()
runner = (ORIG / 'tools/ejecutar_suite_mutacion.py').read_text()
runner = runner.replace('from __future__ import annotations\n', 'from __future__ import annotations\nimport time as _ti\nimport sys as _sy\n_sy.stderr.write(f"@@PHASE runner_start {_ti.perf_counter():.9f}\\n")\n')
runner = runner.replace('import argparse\n', 'import argparse\nimport importlib\n')
runner = runner.replace('from pathlib import Path\n', 'from pathlib import Path\n_sy.stderr.write(f"@@PHASE runner_ready {_ti.perf_counter():.9f}\\n")\n')
runner = runner.replace('            suite_prioritaria = cargador.loadTestsFromName(modulo)', '            _t = _ti.perf_counter()\n            importlib.import_module(modulo)\n            _sy.stderr.write(f"@@PHASE import:{modulo} {_ti.perf_counter()-_t:.9f}\\n")\n            _t = _ti.perf_counter()\n            suite_prioritaria = cargador.loadTestsFromName(modulo)\n            _sy.stderr.write(f"@@PHASE load:{modulo} {_ti.perf_counter()-_t:.9f}\\n")')
runner = runner.replace('            resultado_prioritario = _correr_suite(suite_prioritaria)', '            _t = _ti.perf_counter()\n            resultado_prioritario = _correr_suite(suite_prioritaria)\n            _sy.stderr.write(f"@@PHASE run:{modulo} {_ti.perf_counter()-_t:.9f} tests={resultado_prioritario.testsRun}\\n")')
runner = runner.replace('        suite = _sin_modulos(cargador.discover(', '        _t = _ti.perf_counter()\n        suite = _sin_modulos(cargador.discover(')
runner = runner.replace('            start_dir=args.inicio, top_level_dir=args.tope), args.prioridad)', '            start_dir=args.inicio, top_level_dir=args.tope), args.prioridad)\n        _sy.stderr.write(f"@@PHASE discover {_ti.perf_counter()-_t:.9f}\\n")')
runner = runner.replace('        resultado = _correr_suite(suite)', '        _t = _ti.perf_counter()\n        resultado = _correr_suite(suite)\n        _sy.stderr.write(f"@@PHASE run:general {_ti.perf_counter()-_t:.9f} tests={resultado.testsRun}\\n")')

sites = {s.id:s for s in m.sitios_de(ORIG / 'tools/cli.py', ORIG)}
for mid in a.ids:
    if mid not in sites:
        raise SystemExit(f'ID no existe: {mid}')

with tempfile.TemporaryDirectory(prefix='oracle-medicion-') as td:
    raiz=Path(td)/'repo'
    m._copiar_proyecto(ORIG, raiz)
    target=raiz/'tools/cli.py'
    (raiz/'tools/ejecutar_suite_mutacion.py').write_text(runner)
    comando=[sys.executable,'tools/ejecutar_suite_mutacion.py','--inicio','tests','--tope','.']
    for mod in PRIORIDADES['tools/cli.py']:
        comando.extend(['--prioridad',mod])
    for mid in a.ids:
        for rep in range(1,a.reps+1):
            d={'id':mid,'rep':rep}
            t=time.perf_counter()
            mutated=m.mutar_fuente(original,sites[mid]); d['preparar_mutante']=time.perf_counter()-t
            if mutated is None: raise SystemExit(f'no mutable: {mid}')
            t=time.perf_counter(); m._escribir_atomico(target,mutated); d['escribir_mutante']=time.perf_counter()-t
            try:
                t=time.perf_counter(); caches=m._caches_bajo(raiz); d['cache_pre_scan']=time.perf_counter()-t
                if caches: raise SystemExit(f'cache previo: {caches}')
                t=time.perf_counter(); m.limpiar_cache(raiz); d['cache_pre_limpieza']=time.perf_counter()-t
                with tempfile.TemporaryDirectory(prefix='oracle-pyc-') as pref:
                    env=os.environ.copy(); env['PYTHONPYCACHEPREFIX']=pref; env['PYTHONDONTWRITEBYTECODE']='1'
                    popen_orig=m.subprocess.Popen
                    def timed_popen(*args,**kwargs):
                        d['popen_inicio']=time.perf_counter()
                        proc=popen_orig(*args,**kwargs)
                        d['popen_fin']=time.perf_counter()
                        return proc
                    m.subprocess.Popen=timed_popen
                    try:
                        t=time.perf_counter()
                        result=m.ejecutar_tests(comando,raiz,timeout=300,entorno=env,limite_memoria=m.LIMITE_MEMORIA_PREDETERMINADO)
                        d['ejecutar_tests_total']=time.perf_counter()-t
                    finally: m.subprocess.Popen=popen_orig
                d['estado']=result.estado.value; d['codigo']=result.codigo_salida
                d['popen']=d['popen_fin']-d['popen_inicio']
                phases=[]
                for line in result.stderr.splitlines():
                    if line.startswith('@@PHASE '): phases.append(line.split(' ',2)[1:])
                for key,val in phases:
                    if key in ('runner_start','runner_ready'): d[key]=float(val)
                    else: d[key]=val
                if 'runner_start' in d:
                    d['arranque_hasta_runner']=d['runner_start']-d['popen_inicio']
                    d['import_runner']=d['runner_ready']-d['runner_start']
                t=time.perf_counter(); caches=m._caches_bajo(raiz); d['cache_post_scan']=time.perf_counter()-t
                if caches: raise SystemExit(f'cache posterior: {caches}')
            finally:
                t=time.perf_counter(); m.limpiar_cache(raiz); d['cache_post_limpieza']=time.perf_counter()-t
                t=time.perf_counter(); m._escribir_atomico(target,original); d['restauracion']=time.perf_counter()-t
            d['total_mutante']=sum(d[k] for k in ('preparar_mutante','escribir_mutante','cache_pre_scan','cache_pre_limpieza','ejecutar_tests_total','cache_post_scan','cache_post_limpieza','restauracion'))
            print(json.dumps(d,ensure_ascii=False),flush=True)
```
