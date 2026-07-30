"""La medida: un dato que se lee, se evalúa y se puede medir a su vez.

Forma canónica, tal como se guarda en `catalogos/`:

```json
["medida", "<id>",
  ["desde", ["de", "<relacion>", "<alias>"], ["donde", <pred>]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "<la defensa del número>"],
  ["alcance", "<qué NO ve>"]]
```

Dos campos son obligatorios y son la razón de ser del módulo: **`alcance`**, para que un informe en
verde no pueda decir «todo bien» a secas, y **la defensa del umbral**, para que el número se pueda
discutir. Una medida sin uno de los dos no se carga: falla al leerse, no al usarse.

Los **testigos no se declaran**: son las filas con las que terminó la tubería. Declararlos aparte
obliga a escribir la misma condición dos veces y a mantenerlas sincronizadas a mano — el caso
`004-testigos-duplicados` del corpus.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .algebra import COMPARADORES, _cmp, desde, resumir
from .macro import es_macro, expandir


class MedidaMalDeclarada(ValueError):
    pass


@dataclass(frozen=True)
class Veredicto:
    """La MISMA forma para toda medida, de cualquier dominio. La interfaz uniforme de REST, que es
    la única de sus restricciones que sirve acá."""

    id: str
    valor: float
    ok: bool
    umbral: str
    porque: str
    alcance: str
    testigos: tuple

    def linea(self) -> str:
        marca = "✓" if self.ok else "✗"
        base = f"{marca} {self.id:<44} {self.valor:>8} ({self.umbral})"
        if self.testigos and not self.ok:
            muestra = "; ".join(_resumir_fila(t) for t in self.testigos[:3])
            resto = f" +{len(self.testigos) - 3}" if len(self.testigos) > 3 else ""
            base += f"\n      → {muestra}{resto}"
        return base

    def a_dict(self) -> dict:
        return {"id": self.id, "valor": self.valor, "ok": self.ok, "umbral": self.umbral,
                "porque": self.porque, "alcance": self.alcance,
                "testigos": [dict(t) for t in self.testigos]}


def _resumir_fila(fila: dict) -> str:
    partes = []
    for alias, hecho in fila.items():
        if isinstance(hecho, dict):
            clave = hecho.get("id") or hecho.get("nombre") or hecho.get("archivo") or hecho.get("ruta")
            partes.append(f"{alias}={clave}" if clave else f"{alias}={hecho}")
    return ", ".join(partes)


@dataclass(frozen=True)
class Medida:
    id: str
    tuberia: list
    resumen: list
    op: str
    limite: float
    porque: str
    alcance: str
    fuente: tuple = ()          # cómo estaba escrita: macro o canónica

    @classmethod
    def de_datos(cls, d: list) -> "Medida":
        # Las macros se expanden ANTES de construir, como en LISP: de acá para adentro nadie sabe
        # que existieron, así que el evaluador, la mutación, el inventario y el L2 no cambian.
        fuente = d
        d = expandir(d)
        if not isinstance(d, list) or len(d) != 6 or d[0] != "medida":
            raise MedidaMalDeclarada(
                "una medida es ['medida', id, tuberia, resumen, umbral, alcance]")
        _, mid, tuberia, resumen, umbral, alcance = d
        if not isinstance(mid, str) or not mid.strip() or " " in mid:
            raise MedidaMalDeclarada(f"id inválido: «{mid}»")
        if not (isinstance(umbral, list) and len(umbral) == 4 and umbral[0] == "umbral"):
            raise MedidaMalDeclarada(f"{mid}: el umbral es ['umbral', op, valor, porque]")
        _, op, limite, porque = umbral
        if op not in COMPARADORES:
            raise MedidaMalDeclarada(f"{mid}: operador «{op}» no está en {list(COMPARADORES)}")
        # las dos reglas que hacen a esto un oráculo y no un validador
        if not str(porque).strip():
            raise MedidaMalDeclarada(
                f"{mid}: el umbral {op} {limite} no trae defensa — un número que nadie puede "
                f"discutir es una métrica esperando a volverse objetivo")
        if not (isinstance(alcance, list) and len(alcance) == 2 and alcance[0] == "alcance"
                and str(alcance[1]).strip()):
            raise MedidaMalDeclarada(f"{mid}: falta `alcance` — hay que declarar qué NO ve")
        return cls(id=mid, tuberia=tuberia, resumen=resumen, op=op, limite=limite,
                   porque=str(porque), alcance=str(alcance[1]),
                   fuente=tuple(fuente) if es_macro(fuente) else ())

    def evaluar(self, evidencia: dict) -> Veredicto:
        testigos = desde(self.tuberia, evidencia)
        valor = resumir(self.resumen, testigos)
        return Veredicto(id=self.id, valor=valor, ok=_cmp(self.op)(valor, self.limite),
                         umbral=f"{self.op} {self.limite}", porque=self.porque,
                         alcance=self.alcance, testigos=tuple(testigos))

    def a_datos(self) -> list:
        """La forma CANÓNICA, siempre. Es lo que muta el sensor: mutar la expansión llega más lejos
        que mutar la invocación de la macro."""
        return ["medida", self.id, self.tuberia, self.resumen,
                ["umbral", self.op, self.limite, self.porque], ["alcance", self.alcance]]

    def a_fuente(self) -> list:
        """Cómo está escrita en el archivo: la macro si vino de una, la canónica si no."""
        return list(self.fuente) if self.fuente else self.a_datos()


def cargar(ruta: Path) -> Medida:
    return Medida.de_datos(json.loads(Path(ruta).read_text(encoding="utf-8")))


def cargar_catalogo(*directorios) -> dict[str, Medida]:
    """Una o varias carpetas de medidas. Un id repetido entre carpetas es un error, no una
    sobrescritura silenciosa: si el proyecto quiere cambiar una medida base, la renombra."""
    salida: dict[str, Medida] = {}
    if len(directorios) == 1 and isinstance(directorios[0], (list, tuple)):
        directorios = directorios[0]
    for p in sorted(x for d in directorios for x in Path(d).rglob("*.json")):
        m = cargar(p)
        if m.id in salida:
            raise MedidaMalDeclarada(f"el id «{m.id}» está dos veces (último: {p.name})")
        salida[m.id] = m
    return salida


@dataclass(frozen=True)
class Informe:
    veredictos: tuple

    @property
    def ok(self) -> bool:
        return all(v.ok for v in self.veredictos)

    def texto(self) -> str:
        """Nunca dice «TODO VERDE» a secas: un verde termina enumerando lo que no miró."""
        lineas = [v.linea() for v in self.veredictos]
        malas = [v for v in self.veredictos if not v.ok]
        if malas:
            lineas.append(f"\nVEREDICTO: {len(malas)} de {len(self.veredictos)} medidas en rojo")
        else:
            lineas.append(f"\nVEREDICTO: verde en {len(self.veredictos)} medidas. SIN MIRAR:")
            lineas += [f"  · {v.id}: {v.alcance}" for v in self.veredictos]
        return "\n".join(lineas)

    def a_json(self) -> str:
        return json.dumps({"ok": self.ok, "medidas": [v.a_dict() for v in self.veredictos]},
                          ensure_ascii=False)


def evaluar(medidas, evidencia: dict) -> Informe:
    return Informe(tuple(m.evaluar(evidencia) for m in medidas))


# ---- derivados de la declaración: el «OpenAPI» del oráculo ----

def inventario(medidas) -> list[dict]:
    """Todos los umbrales con su defensa. Antes vivían escondidos en firmas de funciones."""
    return [{"id": m.id, "umbral": f"{m.op} {m.limite}", "porque": m.porque} for m in medidas]


def puntos_ciegos(medidas) -> list[dict]:
    return [{"id": m.id, "alcance": m.alcance} for m in medidas]


def como_hechos(medidas) -> list[dict]:
    """Las medidas COMO RELACIÓN, para poder medirlas con el mismo álgebra (L2 = L1 sobre L1).

    Es la pieza que vuelve esto un metalenguaje: no hay mecanismo nuevo, sólo se sirve el catálogo
    como una relación más.
    """
    return [{"id": m.id, "umbral_op": m.op, "umbral_valor": m.limite, "porque": m.porque,
             "alcance": m.alcance, "relacion": m.tuberia[1][1] if len(m.tuberia) > 1 else ""}
            for m in medidas]
