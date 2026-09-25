"""Re-juicio ciego de las ocho defensas reescritas, con Jev y el criterio fijado de jev-porque-v2.

    python3 rejuicio.py preparar   → lote.json (16 registros: las 8 nuevas y las 8 viejas, mezcladas)
    python3 rejuicio.py correr     → una sola llamada; guarda solicitud, respuesta cruda y resultado

Las viejas van como control: el juez ya las marcó «no» en la pasada anterior. El registro lleva lo
mismo que entonces (alcance, porque, umbral, segun, tubería, resumen, límite) y un id opaco; el
nombre de la medida y qué texto es nuevo quedan en clave.json, que no se manda.
"""
import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

D = Path(__file__).resolve().parent
RAIZ = D.parents[1]
V2 = RAIZ / "tareas" / "20260922-220029-jev-porque-v2"
sys.path.insert(0, str(RAIZ))


def guardar(nombre, obj):
    (D / nombre).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preparar():
    from nucleo.proyecto import Proyecto
    from tools.juzgar import catalogo_para_juzgar
    viejos = json.loads((D / "viejos.json").read_text(encoding="utf-8"))
    catalogo = catalogo_para_juzgar(Proyecto(RAIZ))
    registros, clave = [], {}
    for mid, porque_viejo in viejos.items():
        datos = catalogo[mid].a_datos()
        umbral = datos[4]
        base = {"alcance": catalogo[mid].alcance, "umbral": f"{umbral[1]} {umbral[2]}",
                "segun": umbral[4] if len(umbral) > 4 else "sin_declarar",
                "tuberia": datos[2], "resumen": datos[3], "limite": umbral[2],
                "aplica_vecino": False}
        for version, porque in (("nueva", catalogo[mid].porque), ("vieja", porque_viejo)):
            registros.append({**base, "porque": porque, "_medida": mid, "_version": version})
    random.Random(20260925).shuffle(registros)
    lote = []
    for n, r in enumerate(registros, 1):
        rid = f"w{n:03}"
        clave[rid] = {"medida": r.pop("_medida"), "version": r.pop("_version")}
        lote.append({"id": rid, **r})
    guardar("lote.json", lote)
    guardar("clave.json", clave)
    print(f"{len(lote)} registros")


def correr():
    import requests
    assert not (D / "respuesta-cruda.json").exists(), "No repetir: ya hay una respuesta guardada"
    lote = json.loads((D / "lote.json").read_text(encoding="utf-8"))
    pregunta = json.loads((V2 / "protocolo.json").read_text(encoding="utf-8"))["preguntas"]["porque_origen"]
    payload = {"model": "typesafe/jev-1.13",
               "state": {"description": (V2 / "CRITERIO.md").read_text(encoding="utf-8"), "records": lote},
               "questions": {f"{r['id']}__porque_origen": {"type": "noul",
                             "instructions": f"Para el registro {r['id']}: {pregunta}"} for r in lote}}
    guardar("solicitud.json", payload)
    clave_api = (Path.home() / ".config" / "openrouter" / "key").read_text().strip()
    inicio = time.perf_counter()
    respuesta = requests.post("https://openrouter.ai/api/alpha/decisions",
                              headers={"Authorization": "Bearer " + clave_api,
                                       "Content-Type": "application/json"},
                              json=payload, timeout=120)
    crudo = respuesta.content
    assert clave_api.encode() not in crudo, "La respuesta refleja la credencial; no se guarda"
    (D / "respuesta-cruda.json").write_bytes(crudo)
    datos = respuesta.json()
    clave = json.loads((D / "clave.json").read_text(encoding="utf-8"))
    filas = []
    for q, a in sorted(datos["answers"].items()):
        rid = q.split("__")[0]
        filas.append({"id": rid, **clave[rid], "p_si": a["noul"]})
    guardar("resultado.json", {
        "fecha_utc": datetime.now(timezone.utc).isoformat(), "http": respuesta.status_code,
        "latencia_segundos": round(time.perf_counter() - inicio, 2),
        "costo_usd": datos.get("usage", {}).get("cost"),
        "sha256_respuesta": hashlib.sha256(crudo).hexdigest(), "filas": filas})
    for f in sorted(filas, key=lambda f: (f["medida"], f["version"])):
        print(f"{f['version']:<6} {f['p_si']:.2f}  {f['medida']}")


if __name__ == "__main__":
    {"preparar": preparar, "correr": correr}[sys.argv[1]]()
