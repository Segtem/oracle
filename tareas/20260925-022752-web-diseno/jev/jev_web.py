"""Jev como sensor de la prosa de la web: ¿cada capítulo explica el porqué y se entiende sin jerga?

    OPENROUTER_API_KEY=… python3 jev_web.py docs/index.html docs/por-que.html --salida corrida/

Un sensor, no un juez: la zona media (0,4–0,6) va a revisión humana. Dos controles fabricados, uno sin
porqué y otro con jerga, sirven para ver si el modelo distingue lo obvio. Reusa `enviar` de la
plantilla del sensor de prosa (sin redirecciones, sin volcar la credencial).
"""
import html
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "ejemplo" / "sensor-prosa"))
from sensor_prosa import enviar  # noqa: E402

PREGUNTAS = {
    "explica_porque": "¿El texto le explica a alguien que no conoce Oracle POR QUÉ le serviría, es "
                      "decir qué problema concreto le resuelve, y no sólo QUÉ es o cómo se usa?",
    "sin_jerga": "¿Se entiende el texto sin conocer de antemano los términos internos de Oracle "
                 "(por ejemplo sombra, cota, testigo, alcance, L0, mutante), porque los que usa los explica?",
}
CONTROLES = [
    dict(id="control-sin-porque", titulo="Comandos disponibles",
         texto="Oracle tiene los comandos init, test, juzgar, mutar, tarea y manual. El comando test "
               "acepta --rapido y --todo. El comando juzgar acepta --con y --proyecto."),
    dict(id="control-jerga", titulo="Sombra y cota",
         texto="La sombra perdona hasta su cota salvo que el L0 del sensor no emita la relación del "
               "requiere, en cuyo caso el testigo no llega al L1 y el mutante de aflojar_umbral sobrevive."),
]


def capitulos(ruta: Path):
    t = ruta.read_text(encoding="utf-8")
    t = re.sub(r"<(script|style|pre|figure|footer|header)[^>]*>.*?</\1>", " ", t, flags=re.S)
    for i, s in enumerate(re.findall(r"<section[^>]*>(.*?)</section>", t, flags=re.S)):
        h = re.search(r"<h[12][^>]*>(.*?)</h[12]>", s, flags=re.S)
        texto = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()
        if h and len(texto) > 120:
            yield dict(id=f"{ruta.stem}-{i}", titulo=html.unescape(re.sub(r"<[^>]+>", "", h.group(1))).strip(),
                       texto=texto)


def main(argv):
    salida = Path(argv[argv.index("--salida") + 1])
    paginas = [RAIZ / a for a in argv if a.endswith(".html")]
    registros = [c for p in paginas for c in capitulos(p)] + CONTROLES
    pedido = dict(model="typesafe/jev-1.13",
                  state=dict(description="Capítulos de la web de Oracle, un lenguaje para escribir "
                                         "reglas verificables de un proyecto.", records=registros),
                  questions={f"{r['id']}__{q}": dict(type="noul", instructions=f"Para el registro {r['id']}: {t}")
                             for r in registros for q, t in PREGUNTAS.items()})
    salida.mkdir(parents=True, exist_ok=False)
    (salida / "pedido.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
    datos = enviar("https://openrouter.ai/api/alpha/decisions", os.environ["OPENROUTER_API_KEY"], pedido)
    (salida / "respuesta.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    filas = []
    for r in registros:
        fila = {"id": r["id"], "titulo": r["titulo"]}
        for q in PREGUNTAS:
            fila[q] = datos["answers"][f"{r['id']}__{q}"]["noul"]
        filas.append(fila)
    (salida / "resultado.json").write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in filas:
        marca = lambda p: "REVISAR" if 0.4 <= p <= 0.6 else ("sí" if p > 0.6 else "no")
        print(f"{f['explica_porque']:.2f} {marca(f['explica_porque']):7} {f['sin_jerga']:.2f} "
              f"{marca(f['sin_jerga']):7} {f['id']:20} {f['titulo'][:60]}")


if __name__ == "__main__":
    main(sys.argv[1:])
