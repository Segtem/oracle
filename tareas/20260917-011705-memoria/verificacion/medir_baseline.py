import json, os, subprocess, tempfile, time
from pathlib import Path
salida = Path('tareas/20260917-011705-memoria/verificacion')
with tempfile.TemporaryDirectory(prefix='oracle-cache-medicion-') as cache, (salida / 'baseline.log').open('w') as log:
    env = dict(os.environ, PYTHONPYCACHEPREFIX=cache, PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.Popen(['python3', 'tools/ejecutar_suite_mutacion.py'], env=env, stdout=log, stderr=subprocess.STDOUT)
    pico = rss = muestras = 0
    inicio = time.monotonic()
    while p.poll() is None:
        try:
            datos = dict(line.split(':', 1) for line in Path(f'/proc/{p.pid}/status').read_text().splitlines())
            pico = max(pico, int(datos.get('VmPeak', '0 kB').split()[0]))
            rss = max(rss, int(datos.get('VmHWM', '0 kB').split()[0]))
            muestras += 1
        except FileNotFoundError:
            pass
        time.sleep(.01)
    medicion = dict(comando=p.args, codigo=p.returncode, vmpeak_kib=pico, vmhwm_kib=rss, muestras=muestras, segundos=round(time.monotonic()-inicio, 2), python=subprocess.check_output(['python3','--version'], text=True).strip(), intervalo_ms=10)
    (salida / 'baseline-memoria.json').write_text(json.dumps(medicion, indent=2)+'\n')
    print(json.dumps(medicion))
