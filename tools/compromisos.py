"""Sensor de los compromisos prerregistrados: la puerta de abandono del propio Oracle.

    python tools/compromisos.py            → informe
    python tools/compromisos.py --hechos   → evidencia JSON

Oracle le exige a toda afirmación un umbral, una defensa escrita y un testigo. No tenía ninguno para
sí mismo, y su criterio declarado —la proporción— ya disparó en contra dos veces sin que nada
frenara: la respuesta publicada fue reinterpretarlo. Un prerregistro en prosa habría corrido la misma
suerte, porque este proyecto arranca diciendo que **una regla escrita como consejo se lee y se
olvida**. Así que la puerta es una medida, y la corre el CI.

Lo que el mecanismo puede y lo que no: no impide editar `COMPROMISOS.json` —nada puede—, pero
convierte cambiar de criterio en un commit fechado y visible en vez de un párrafo nuevo que
reinterpreta el anterior. Eso es todo lo que un prerregistro da, y es lo que faltaba.

El sensor produce HECHOS y no juzga: si la fecha pasó lo decide una medida.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402
from nucleo.medida import cargar_catalogo, evaluar, medidas_aplicables  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogos_a_cargar,  # noqa: E402
                             macros_del_proyecto)

ARCHIVO = RAIZ / "COMPROMISOS.json"
ESQUEMA = "oracle.compromisos/v1"

OBLIGATORIOS = ("id", "abierto", "vence", "condicion", "umbral", "cumplido",
                "testigo", "consecuencia")

# Un compromiso puede traer `medicion` y entonces `observado` se OBSERVA en vez de escribirse. Es la
# diferencia entre una puerta que se entera y una que hay que acordarse de actualizar: mientras el
# número lo tipeaba una persona, que la condición se cumpliera no lo detectaba nadie, y la puerta
# sólo servía para el lado de fallar. Un compromiso sobre una decisión humana no se puede observar y
# sigue declarando su `observado`; el que se puede medir, se mide.
MEDIBLES = ("medidas_de_consumidores",)


class CompromisoInvalido(ValueError):
    pass


def _fecha(valor, campo: str) -> date:
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError) as e:
        raise CompromisoInvalido(f"`{campo}` no es una fecha ISO: {valor!r}") from e


def leer(ruta: Path = ARCHIVO) -> list[dict]:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except OSError as e:
        raise CompromisoInvalido(f"no se pudo leer {ruta}: {e}") from e
    except json.JSONDecodeError as e:
        raise CompromisoInvalido(f"{ruta.name} no es JSON válido: {e}") from e
    if not isinstance(datos, dict) or datos.get("esquema") != ESQUEMA:
        raise CompromisoInvalido(f"{ruta.name}: falta el esquema {ESQUEMA!r}")
    if not isinstance(datos.get("porque"), str) or not datos["porque"].strip():
        raise CompromisoInvalido(f"{ruta.name}: el prerregistro necesita su propia defensa")
    lista = datos.get("compromisos")
    # Cero compromisos NO es un archivo vacío inocente: es la manera de librarse de la puerta
    # borrando el contenido en vez de declarando que se cambió de criterio.
    if not isinstance(lista, list) or not lista:
        raise CompromisoInvalido(f"{ruta.name}: `compromisos` no puede estar vacío")
    vistos = set()
    for i, c in enumerate(lista):
        if not isinstance(c, dict):
            raise CompromisoInvalido(f"{ruta.name}: compromiso[{i}] debe ser un objeto")
        faltan = [k for k in OBLIGATORIOS if k not in c]
        if faltan:
            raise CompromisoInvalido(f"{ruta.name}: compromiso[{i}] sin {faltan}")
        medicion = c.get("medicion")
        if medicion is None:
            if "observado" not in c:
                raise CompromisoInvalido(
                    f"{ruta.name}: {c['id']}: sin `medicion` hace falta `observado` declarado")
        else:
            if not isinstance(medicion, dict) or medicion.get("tipo") not in MEDIBLES:
                raise CompromisoInvalido(
                    f"{ruta.name}: {c['id']}: `medicion.tipo` debe ser uno de {list(MEDIBLES)}")
            fuentes = medicion.get("fuentes")
            if not isinstance(fuentes, list) or not fuentes:
                raise CompromisoInvalido(
                    f"{ruta.name}: {c['id']}: `medicion.fuentes` no puede estar vacío")
            if "observado" in c:
                raise CompromisoInvalido(
                    f"{ruta.name}: {c['id']}: trae `medicion` y además `observado` escrito a mano; "
                    "un número medido y otro declarado no pueden convivir, porque el declarado gana "
                    "sin que nadie lo note")
        if c["id"] in vistos:
            raise CompromisoInvalido(f"{ruta.name}: id repetido: {c['id']}")
        vistos.add(c["id"])
        for campo in ("condicion", "testigo", "consecuencia"):
            if not isinstance(c[campo], str) or not c[campo].strip():
                raise CompromisoInvalido(f"{ruta.name}: {c['id']}: `{campo}` vacío")
        if type(c["cumplido"]) is not bool:
            raise CompromisoInvalido(f"{ruta.name}: {c['id']}: `cumplido` debe ser booleano")
        for campo in ("umbral", "observado", "nucleo_maximo"):
            if campo in c and (type(c[campo]) is not int or c[campo] < 0):
                raise CompromisoInvalido(
                    f"{ruta.name}: {c['id']}: `{campo}` debe ser un entero >= 0")
        if _fecha(c["vence"], "vence") <= _fecha(c["abierto"], "abierto"):
            raise CompromisoInvalido(f"{ruta.name}: {c['id']}: `vence` no es posterior a `abierto`")
    return lista


def medidas_de_consumidores(fuentes: list[str]) -> int:
    """Cuenta las medidas escritas en los catálogos de los proyectos que consumen Oracle.

    Una fuente declarada que no existe es un ERROR, no un cero. Un cero silencioso convertiría
    «borré el proyecto» y «el proyecto no creció» en el mismo número, y sería además la manera más
    barata de bajar el observado cuando conviene.
    """
    total = 0
    for fuente in fuentes:
        raiz = Path(fuente).expanduser()
        if not raiz.is_dir():
            raise CompromisoInvalido(
                f"la fuente declarada no existe o no es un directorio: {fuente}")
        total += sum(1 for _ in raiz.rglob("*.json"))
    return total


def lineas_del_nucleo(raiz: Path = RAIZ) -> int:
    """Las mismas líneas que publica `tools/cifras.py`, contadas por su misma función.

    Se importa en vez de recontar: dos lecturas del mismo número divergen, y acá la divergencia
    dejaría a la puerta midiendo un núcleo distinto del que el README publica.
    """
    from tools.cifras import _lenguaje, _lineas

    return _lineas(_lenguaje())


def hechos(hoy: date | None = None, ruta: Path = ARCHIVO) -> dict:
    """Los compromisos COMO RELACIÓN. Ningún campo es un veredicto: `vencido` es aritmética de
    fechas, `observado` es un conteo y `alcanza_el_umbral` una comparación. Si esa combinación es
    aceptable lo dice una medida."""
    hoy = hoy or date.today()
    filas = []
    for c in leer(ruta):
        vence = _fecha(c["vence"], "vence")
        medicion = c.get("medicion")
        observado = (medidas_de_consumidores(medicion["fuentes"]) if medicion
                     else c["observado"])
        # Un compromiso sin tope de núcleo declarado no lo tiene, y el hecho lo dice como tal: se
        # publica un tope infinito antes que omitir el campo, porque comparar contra un campo
        # ausente levanta error en el álgebra y una medida no debería tener que esquivarlo.
        tope = c.get("nucleo_maximo")
        nucleo = lineas_del_nucleo()
        filas.append({
            "id": c["id"],
            "vence": c["vence"],
            "dias_restantes": (vence - hoy).days,
            "vencido": hoy >= vence,
            "cumplido": bool(c["cumplido"]),
            "umbral": c["umbral"],
            "observado": observado,
            "medido": medicion is not None,
            "alcanza_el_umbral": observado >= c["umbral"],
            "lineas_nucleo": nucleo,
            "nucleo_maximo": tope if tope is not None else nucleo,
            "nucleo_dentro_del_tope": tope is None or nucleo <= tope,
        })
    return {"compromiso": filas}


def _informe(evidencia: dict) -> int:
    proy = Proyecto(RAIZ)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    juezas = medidas_aplicables(catalogo.values(), evidencia)
    for fila in evidencia["compromiso"]:
        alcanzado = fila["alcanza_el_umbral"] and fila["nucleo_dentro_del_tope"]
        estado = ("ALCANZADO" if alcanzado
                  else "VENCIDO" if fila["vencido"]
                  else f"abierto · faltan {fila['dias_restantes']} días")
        fuente = "medido" if fila["medido"] else "declarado"
        print(f"  {fila['id']:<38} vence {fila['vence']} · "
              f"{fila['observado']}/{fila['umbral']} ({fuente}) · {estado}")
        if not fila["nucleo_dentro_del_tope"]:
            print(f"      núcleo {fila['lineas_nucleo']} líneas, sobre el tope de "
                  f"{fila['nucleo_maximo']}")
    if not juezas:
        print("\nsin políticas meta activas — se informa sólo el estado")
        return 0
    informe = evaluar(juezas, evidencia)
    print("\njuzgado por las medidas del catálogo:")
    for v in informe.veredictos:
        print(" ", v.linea())
    return 0 if informe.ok else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        evidencia = hechos()
    except CompromisoInvalido as e:
        print(f"COMPROMISOS INVÁLIDOS — {e}")
        return 1
    if "--hechos" in argv:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0
    return _informe(evidencia)


if __name__ == "__main__":
    raise SystemExit(main())
