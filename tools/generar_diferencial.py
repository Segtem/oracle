"""Emite los fixtures `oracle.diferencial/v1` desde la implementación de referencia.

    python tools/generar_diferencial.py            → comprueba que lo versionado esté al día
    python tools/generar_diferencial.py --escribir → reescribe los fixtures

Quién decide `referencia_ok` es `diferencial/referencia/evaluador.py`, escrito por otro autor que
nunca vio `nucleo/` (ver `diferencial/referencia/PROCEDENCIA.md`). Oracle no se copia a sí mismo: si
las dos implementaciones ya discrepan al generar, **no se emite el fixture**, porque un fixture que
nace en desacuerdo congela el desacuerdo en vez de exponerlo.

Regenerar dos veces con las mismas entradas produce exactamente los mismos bytes: la serialización es
JSON canónico con orden estable y sin `NaN`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402  registra las UDF declaradas
from nucleo.diferencial import (Procedencia, comprobar_version_referencia,  # noqa: E402
                                crear_frescura)
from nucleo.fixtures import (registro_de_veredicto, valor_comparable,  # noqa: E402
                             validar_fixture)
from nucleo.medida import Medida, cargar_catalogo  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogos_a_cargar,  # noqa: E402
                             macros_del_proyecto)

REFERENCIA = RAIZ / "diferencial" / "referencia" / "evaluador.py"

# Los escenarios son el material del fixture, y se escriben acá y no en un JSON suelto para que la
# huella del emisor los cubra: un mundo que cambia sin que cambie su huella es un fixture que miente.
#
# El contrato del esquema pide ambas polaridades GLOBALES y ambas por MEDIDA. No es burocracia: un
# fixture de puros verdes no distingue una implementación correcta de una que devuelve `True`.
MUNDOS = [
    ("todo-en-orden", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "sigue"},
                   {"corrida": "c1", "t": 2, "actor": "a", "que": "termina"}],
    }),
    ("corrida-que-no-se-reproduce", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": False, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
    }),
    ("presupuesto-agotado", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "sin_pasos", "determinista": True, "presupuesto_agotado": True}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
    }),
    ("traza-con-un-hueco", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        # falta el instante 1: hay dos eventos y el último es t=2
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 2, "actor": "a", "que": "termina"}],
    }),
    # Los mundos de abajo ejercitan lo que entró en el álgebra 0.7 —`requiere` con condición y
    # evidencia de una relación con variantes—, que hasta 0.23.0 el diferencial no contrastaba:
    # la referencia se re-derivó contra 0.7, pero ningún mundo la hacía pasar por ahí.
    ("mutantes-de-codigo-muertos", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
        "mutante": [{"tipo": "codigo", "id": "m1", "estado": "murieron"},
                    {"tipo": "codigo", "id": "m2", "estado": "murieron"}],
    }),
    ("un-mutante-de-codigo-vivo", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
        "mutante": [{"tipo": "codigo", "id": "m1", "estado": "murieron"},
                    {"tipo": "codigo", "id": "m2", "estado": "pasaron"}],
    }),
    # Sólo mutantes de la OTRA variante: la condición de `requiere` no la cumple ninguna fila, y la
    # medida sale SIN EVIDENCIA en vez de verde. En un booleano eso era indistinguible de un rojo.
    ("solo-mutantes-de-medida", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
        "mutante": [{"tipo": "medida", "id": "m1", "mutador": "umbral", "murio": True}],
    }),
    # `mutante` vacía: la relación está declarada en la evidencia y no trae una sola fila.
    ("sin-un-solo-mutante", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
        "mutante": [],
    }),
    # La variante `medida` no trae `estado`. La primera fila cumple la condición, la segunda no
    # tiene el campo: si alguna de las dos implementaciones cortocircuitara al primer acierto, acá
    # una levantaría y la otra no. Es la decisión que 0.21.0 tomó leyendo, y que nadie contrastaba.
    ("una-variante-sin-el-campo-de-la-condicion", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "termina"}],
        "mutante": [{"tipo": "codigo", "id": "m1", "estado": "murieron"},
                    {"tipo": "medida", "id": "m2", "mutador": "umbral", "murio": True}],
    }),
    # Álgebra 0.8: una corrida sin un solo evento, y otra cuya traza nunca termina. Es la polaridad
    # roja de las medidas con `sin`, que en los mundos de arriba encuentran siempre su pareja.
    ("una-corrida-sin-eventos", {
        "corrida": [{"id": "c1", "escenario": "base", "semilla": 7, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False},
                    {"id": "c2", "escenario": "base", "semilla": 8, "pasos": 3,
                     "razon": "termino", "determinista": True, "presupuesto_agotado": False}],
        "evento": [{"corrida": "c1", "t": 0, "actor": "a", "que": "empieza"},
                   {"corrida": "c1", "t": 1, "actor": "a", "que": "sigue"}],
        "mutante": [],
    }),
]

MEDIDAS_DEL_CATALOGO = [
    "simulacion.corrida_reproducible",
    "simulacion.la_traza_no_tiene_huecos",
    "simulacion.no_se_agoto_el_presupuesto",
]

# Estas dos no están en el catálogo distribuido y no obligan a nadie: existen para que el contraste
# pase por `requiere` con condición, que ninguna medida de `simulacion` usa. Viven acá, con los
# mundos, porque la huella del emisor las cubre —una medida del contraste que cambia sin que cambie
# la huella sería un fixture que miente.
MEDIDAS_DEL_EMISOR = [
    # Cuenta eventos de falla, y no concluye si la ronda no trae mutantes de código.
    ["medida", "simulacion.traza_sin_fallas_con_mutantes_de_codigo",
     ["desde", ["de", "evento", "e"], ["donde", ["==", ["campo", "e", "que"], "falla"]]],
     ["resumen", "contar", 1],
     ["umbral", "<=", 0, "un evento de falla en la traza es el defecto que la medida persigue; se "
      "mide sólo cuando la ronda trajo mutantes de código, y si no los trajo no concluye"],
     ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]],
     ["ambito", "del_origen"],
     ["alcance", "cuenta eventos `falla` de la traza. NO ve los mutantes: sólo exige que haya al "
      "menos uno de código para concluir"]],
    # La condición lee `estado`, que la variante `medida` de `mutante` no tiene.
    ["medida", "simulacion.corrida_con_mutantes_que_pasaron",
     ["desde", ["de", "mutante", "m"],
      ["donde", ["==", ["campo", "m", "estado"], "pasaron"]]],
     ["resumen", "contar", 1],
     ["umbral", "<=", 0, "un mutante que pasó es un punto ciego de los tests; la medida no "
      "concluye si la ronda no trajo ninguno de código"],
     ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "estado"], "murieron"]]],
     ["ambito", "del_origen"],
     ["alcance", "cuenta mutantes con estado «pasaron». NO distingue variantes: una fila sin "
      "`estado` hace levantar al álgebra, y eso es lo que el contraste mira"]],
    # Las tres de abajo pasan por `sin` (álgebra 0.8). La primera es la anti-junta de manual; la
    # segunda la aplica después de `agrupar`, con la condición leyendo una columna; la tercera tiene
    # una condición que no mira la fila de la izquierda y que levanta en la variante sin `estado`:
    # sin cortocircuito, una implementación que corte al primer acierto discrepa acá. Y en los
    # mundos sin `mutante`, la relación ausente tiene que ser error en las dos.
    ["medida", "simulacion.corrida_sin_ningun_evento",
     ["desde", ["de", "corrida", "c"],
      ["sin", ["de", "evento", "e"], ["==", ["campo", "e", "corrida"], ["campo", "c", "id"]]]],
     ["resumen", "contar", 1],
     ["umbral", "<=", 0, "una corrida sin eventos no dejó traza que juzgar"],
     ["ambito", "del_origen"],
     ["alcance", "cruza corridas con eventos por id. NO mira qué eventos hubo"]],
    ["medida", "simulacion.actor_que_nunca_termina",
     ["desde", ["de", "evento", "e"],
      ["agrupar", [["actor", ["campo", "e", "actor"]]], [["eventos", "contar", 1]]],
      ["sin", ["de", "evento", "f"],
       ["y", ["==", ["campo", "f", "actor"], ["col", "actor"]],
             ["==", ["campo", "f", "que"], "termina"]]]],
     ["resumen", "contar", 1],
     ["umbral", "<=", 0, "un actor sin evento de fin dejó su trabajo a medias"],
     ["ambito", "del_origen"],
     ["alcance", "busca un evento «termina» por actor, en cualquier corrida. NO separa corridas"]],
    ["medida", "simulacion.corrida_sin_mutante_muerto",
     ["desde", ["de", "corrida", "c"],
      ["sin", ["de", "mutante", "m"], ["==", ["campo", "m", "estado"], "murieron"]]],
     ["resumen", "contar", 1],
     ["umbral", "<=", 0, "una ronda sin ningún mutante de código muerto no probó nada"],
     ["ambito", "del_origen"],
     ["alcance", "no correlaciona el mutante con la corrida. Una fila sin `estado` hace levantar "
      "al álgebra, y eso es lo que el contraste mira"]],
]

SALIDA = RAIZ / "diferencial" / "simulacion.json"


def cargar_referencia():
    spec = importlib.util.spec_from_file_location("referencia_diferencial", REFERENCIA)
    modulo = importlib.util.module_from_spec(spec)
    # Registrarlo ANTES de ejecutarlo no es ceremonia: `@dataclass` resuelve sus anotaciones
    # buscando el módulo en `sys.modules`, y sin esto revienta con un AttributeError que no dice
    # nada. Una referencia escrita por otro autor puede usar cualquier cosa del lenguaje, y el
    # cargador no puede exigirle que se limite a lo que hoy funciona por casualidad.
    sys.modules[spec.name] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def _de_la_referencia(referencia, medida, evidencia, escalares) -> dict:
    """Lo mismo que `registro_de_veredicto`, del otro lado: la referencia expone un diccionario y
    su propia `ErrorDeAlgebra`, y su SIN EVIDENCIA viaja en el valor."""
    try:
        r = referencia.evaluar(medida.a_datos(), evidencia, escalares)
    except referencia.ErrorDeAlgebra:
        return {"ok": False, "levanta": True}
    return {"ok": bool(r["ok"]), "valor": valor_comparable(r["valor"])}


def construir(catalogo: dict) -> dict:
    from nucleo.algebra import ESCALARES

    referencia = cargar_referencia()
    # ANTES de evaluar nada: la referencia declara contra qué versión se escribió. Si el núcleo
    # avanzó y la referencia quedó atrás, emitir el fixture congelaría el desacuerdo en vez de
    # exponerlo — el defecto exacto que este versionado existe para matar.
    desfasada = comprobar_version_referencia(referencia)
    if desfasada:
        raise SystemExit(
            "NO SE EMITE — la referencia no está a la versión del núcleo:\n  · "
            + "\n  · ".join(desfasada))
    medidas = ([catalogo[mid] for mid in MEDIDAS_DEL_CATALOGO]
               + [Medida.de_datos(datos) for datos in MEDIDAS_DEL_EMISOR])
    escenarios = []
    for nombre, evidencia in MUNDOS:
        ref_por_medida, oracle_por_medida = {}, {}
        for medida in medidas:
            ref_por_medida[medida.id] = _de_la_referencia(referencia, medida, evidencia,
                                                          dict(ESCALARES))
            oracle_por_medida[medida.id] = registro_de_veredicto(medida, evidencia)
        # El desacuerdo se informa acá y aborta: fijarlo en un archivo lo convertiría en el nuevo
        # esperado, que es exactamente la manera de perder el hallazgo.
        difieren = [mid for mid in ref_por_medida
                    if ref_por_medida[mid] != oracle_por_medida[mid]]
        if difieren:
            detalle = "\n".join(
                f"  · {mid}: referencia {ref_por_medida[mid]} · Oracle {oracle_por_medida[mid]}"
                for mid in difieren)
            raise SystemExit(
                f"NO SE EMITE — en «{nombre}» la referencia y Oracle ya discrepan:\n{detalle}\n"
                "Un fixture que nace en desacuerdo congela el desacuerdo. Resolvé cuál de las dos "
                "tiene razón (y si la especificación lo decide) antes de versionarlo.")
        escenarios.append({
            "id": nombre,
            "evidencia": evidencia,
            "referencia_ok": all(r["ok"] for r in ref_por_medida.values()),
            "oracle_al_generar": {
                "global_ok": all(r["ok"] for r in oracle_por_medida.values()),
                "por_medida": oracle_por_medida,
            },
        })

    procedencia = Procedencia(
        raiz=RAIZ,
        emisor=("tools/generar_diferencial.py",),
        referencia=("diferencial/referencia/evaluador.py",),
        desde_proyecto=".")
    return {
        "esquema": "oracle.diferencial/v1",
        "origen": "implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md",
        "medidas": [m.id for m in medidas],
        # Las que no están en ningún catálogo viajan escritas: quien revise el fixture tiene que
        # poder reconstruirlas sin este emisor.
        "medidas_declaradas": {m.id: m.a_datos() for m in medidas
                               if m.id not in MEDIDAS_DEL_CATALOGO},
        "mundos": len(MUNDOS),
        "escenarios": escenarios,
        # La huella del catálogo cubre las medidas publicadas; las del emisor viajan en su propia
        # huella, que es la del archivo donde están escritas.
        "frescura": crear_frescura(procedencia, [m for m in medidas
                                                 if m.id in MEDIDAS_DEL_CATALOGO],
                                   {"dominio": "simulacion"}),
    }


def serializar(datos: dict) -> str:
    return json.dumps(datos, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    proy = Proyecto(RAIZ)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    datos = construir(catalogo)

    fallas = validar_fixture(datos, SALIDA.name)
    if fallas:
        print("FIXTURE INVÁLIDO — no se escribe:")
        for f in fallas:
            print(f"  · {f}")
        return 1

    texto = serializar(datos)
    if "--escribir" in argv:
        SALIDA.write_text(texto, encoding="utf-8")
        print(f"{SALIDA.relative_to(RAIZ)} escrito · {len(MUNDOS)} mundos · "
              f"{len(MEDIDAS_DEL_CATALOGO) + len(MEDIDAS_DEL_EMISOR)} medidas")
        return 0
    if not SALIDA.exists():
        print(f"falta {SALIDA.relative_to(RAIZ)}; ejecutá "
              "`python tools/generar_diferencial.py --escribir`")
        return 1
    if SALIDA.read_text(encoding="utf-8") != texto:
        print(f"{SALIDA.relative_to(RAIZ)} no coincide con lo que emite la referencia hoy; "
              "ejecutá `python tools/generar_diferencial.py --escribir`")
        return 1
    print(f"DIFERENCIAL AL DÍA — {len(MUNDOS)} mundos × "
          f"{len(MEDIDAS_DEL_CATALOGO) + len(MEDIDAS_DEL_EMISOR)} medidas, "
          "referencia y Oracle de acuerdo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
