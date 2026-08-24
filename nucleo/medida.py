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

from .algebra import (COMPARADORES, ErrorDeAlgebra, LimitesAlgebra, comparar, desde, resumir,
                      validar_finito, validar_resumen, validar_tuberia)
from .macro import es_macro, expandir


class MedidaMalDeclarada(ValueError):
    pass


@dataclass(frozen=True)
class ClasificacionMeta:
    """Contrato extensible para distinguir lenguaje y mundo.

    El núcleo trae las relaciones que él mismo produce, pero no pretende conocer las relaciones
    reflexivas de cada proyecto. Un perfil puede añadirlas y también declarar sus prefijos.
    """

    # `paso`, `nodo` y `producto` son la traza del evaluador midiéndose a sí mismo: describen lo que
    # hizo el álgebra, no el mundo. Son tan reflexivas como `medida`.
    relaciones_del_lenguaje: frozenset[str] = frozenset(
        {"medida", "caso", "medida_en_uso", "paso", "nodo", "producto"})
    prefijos_meta: tuple[str, ...] = ("meta.",)

    def __post_init__(self) -> None:
        if (not isinstance(self.relaciones_del_lenguaje, frozenset)
                or any(not isinstance(r, str) or not r.strip()
                       for r in self.relaciones_del_lenguaje)):
            raise MedidaMalDeclarada(
                "las relaciones del lenguaje deben ser un frozenset de textos no vacíos")
        if (not isinstance(self.prefijos_meta, tuple) or not self.prefijos_meta
                or any(not isinstance(p, str) or not p for p in self.prefijos_meta)):
            raise MedidaMalDeclarada("los prefijos meta deben ser una tupla de textos no vacíos")

    def con(self, *, relaciones=(), prefijos=()) -> "ClasificacionMeta":
        """Devuelve un contrato ampliado sin mutar el compartido por otro consumidor."""
        return ClasificacionMeta(
            self.relaciones_del_lenguaje.union(relaciones),
            tuple(dict.fromkeys((*self.prefijos_meta, *prefijos))))


_CLASIFICACION_BASE: ClasificacionMeta | None = None


def clasificacion_meta_base() -> ClasificacionMeta:
    """El contrato por omisión, construido al primer uso y memorizado.

    Mismo motivo que `limites_predeterminados()` en el álgebra: como constante de módulo, un mutante
    de `__post_init__` rompía el **import** de `nucleo.medida` —del que cuelga casi toda la suite— y
    el arnés lo reportaba como «error» en vez de «muerte». Siete mutantes quedaban sin veredicto por
    una línea que no necesitaba ejecutarse al importar.
    """
    global _CLASIFICACION_BASE
    if _CLASIFICACION_BASE is None:
        _CLASIFICACION_BASE = ClasificacionMeta()
    return _CLASIFICACION_BASE


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
    # Qué relación declarada como necesaria vino vacía. No es un rojo cualquiera: un rojo dice «el
    # mundo está mal», y esto dice «no hay con qué mirar». `ok` sigue en False porque lo único
    # inaceptable es que salga verde.
    sin_evidencia: str = ""

    def linea(self) -> str:
        if self.sin_evidencia:
            return (f"⊘ {self.id:<44} {'SIN EVIDENCIA':>8} "
                    f"(«{self.sin_evidencia}» vacía; no se midió)")
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
                "sin_evidencia": self.sin_evidencia,
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
    # Relaciones sin las cuales esta medida no puede concluir nada. Es el espejo de `alcance`: uno
    # declara qué NO ve, y éste declara qué NECESITA ver. Existe porque el álgebra no puede
    # expresarlo: `unir` con un lado vacío no produce pares, y sin pares no hay grupos, así que la
    # medida más fuerte —«un módulo que nadie importa»— salía VERDE justo cuando el mundo estaba
    # peor. Declararlo en el `alcance` volvía visible el hueco; no lo cerraba.
    requiere: tuple = ()
    fuente: tuple = ()          # cómo estaba escrita: macro o canónica

    @classmethod
    def de_datos(cls, d: list, *, registro=None,
                 limites: LimitesAlgebra | None = None, macros=None) -> "Medida":
        # Las macros se expanden ANTES de construir, como en LISP: de acá para adentro nadie sabe
        # que existieron, así que el evaluador, la mutación, el inventario y el L2 no cambian.
        fuente = d
        d = expandir(d, macros, limites)
        if not isinstance(d, list) or len(d) not in (6, 7) or d[0] != "medida":
            raise MedidaMalDeclarada(
                "una medida es ['medida', id, tuberia, resumen, umbral, [requiere,] alcance]")
        # `requiere` es OPCIONAL y va antes de `alcance`: las medidas que no lo declaran no cambian,
        # y las rutas de mutación —que indexan tubería, resumen y umbral— tampoco se corren.
        if len(d) == 7:
            _, mid, tuberia, resumen, umbral, requiere, alcance = d
        else:
            _, mid, tuberia, resumen, umbral, alcance = d
            requiere = ["requiere"]
        if not isinstance(mid, str) or not mid.strip() or " " in mid:
            raise MedidaMalDeclarada(f"id inválido: «{mid}»")
        try:
            validar_tuberia(tuberia, limites, registro=registro)
            validar_resumen(resumen, limites, registro=registro)
        except ErrorDeAlgebra as e:
            raise MedidaMalDeclarada(f"{mid}: {e}") from e
        if not (isinstance(umbral, list) and len(umbral) == 4 and umbral[0] == "umbral"):
            raise MedidaMalDeclarada(f"{mid}: el umbral es ['umbral', op, valor, porque]")
        _, op, limite, porque = umbral
        if op not in COMPARADORES:
            raise MedidaMalDeclarada(f"{mid}: operador «{op}» no está en {list(COMPARADORES)}")
        if not isinstance(limite, (str, int, float, bool)):
            raise MedidaMalDeclarada(
                f"{mid}: el valor del umbral tiene que ser escalar, no {type(limite).__name__}")
        try:
            validar_finito(limite, "el valor del umbral")
        except ErrorDeAlgebra as e:
            raise MedidaMalDeclarada(f"{mid}: {e}") from e
        if op in ("==", "!=") and isinstance(limite, float):
            raise MedidaMalDeclarada(
                f"{mid}: la igualdad exacta de umbral sobre un flotante está prohibida; "
                "usá una comparación de orden con tolerancia")
        # las dos reglas que hacen a esto un oráculo y no un validador
        if not isinstance(porque, str) or not porque.strip():
            raise MedidaMalDeclarada(
                f"{mid}: el umbral {op} {limite} no trae defensa — un número que nadie puede "
                f"discutir es una métrica esperando a volverse objetivo")
        if not (isinstance(alcance, list) and len(alcance) == 2 and alcance[0] == "alcance"
                and isinstance(alcance[1], str) and alcance[1].strip()):
            raise MedidaMalDeclarada(f"{mid}: falta `alcance` — hay que declarar qué NO ve")
        if not (isinstance(requiere, list) and requiere and requiere[0] == "requiere"
                and all(isinstance(r, str) and r.strip() for r in requiere[1:])):
            raise MedidaMalDeclarada(
                f"{mid}: `requiere` es ['requiere', <relación>, …] con nombres no vacíos")
        nombres = tuple(requiere[1:])
        if len(set(nombres)) != len(nombres):
            raise MedidaMalDeclarada(f"{mid}: `requiere` repite una relación: {list(nombres)}")
        return cls(id=mid, tuberia=tuberia, resumen=resumen, op=op, limite=limite,
                   porque=porque, alcance=alcance[1], requiere=nombres,
                   fuente=tuple(fuente) if es_macro(fuente, macros) else ())

    def evaluar(self, evidencia: dict, limites: LimitesAlgebra | None = None, *,
                registro=None) -> Veredicto:
        # ANTES de medir: si falta con qué, no hay veredicto que dar. Medir igual produciría el
        # agregado sobre cero filas —que es 0— y un umbral `<= 0` lo leería como verde.
        faltante = next((r for r in self.requiere if not evidencia.get(r)), "")
        if faltante:
            return Veredicto(id=self.id, valor=0, ok=False,
                             umbral=f"{self.op} {self.limite}", porque=self.porque,
                             alcance=self.alcance, testigos=(), sin_evidencia=faltante)
        testigos = desde(self.tuberia, evidencia, limites, registro=registro)
        valor = resumir(self.resumen, testigos, limites, registro=registro)
        return Veredicto(id=self.id, valor=valor, ok=comparar(self.op, valor, self.limite),
                         umbral=f"{self.op} {self.limite}", porque=self.porque,
                         alcance=self.alcance, testigos=tuple(testigos))

    def a_datos(self) -> list:
        """La forma CANÓNICA, siempre. Es lo que muta el sensor: mutar la expansión llega más lejos
        que mutar la invocación de la macro."""
        canonica = ["medida", self.id, self.tuberia, self.resumen,
                    ["umbral", self.op, self.limite, self.porque]]
        # Una medida sin `requiere` NO emite el nodo: la forma canónica de las que ya existían no
        # cambia, y con ella no cambian sus huellas ni las rutas de sus mutantes.
        if self.requiere:
            canonica.append(["requiere", *self.requiere])
        return [*canonica, ["alcance", self.alcance]]

    def a_fuente(self) -> list:
        """Cómo está escrita en el archivo: la macro si vino de una, la canónica si no."""
        return list(self.fuente) if self.fuente else self.a_datos()


def cargar(ruta: Path, *, registro=None,
           limites: LimitesAlgebra | None = None, macros=None) -> Medida:
    return Medida.de_datos(
        json.loads(Path(ruta).read_text(encoding="utf-8")),
        registro=registro,
        limites=limites,
        macros=macros,
    )


def cargar_catalogo(*directorios, registro=None,
                    limites: LimitesAlgebra | None = None,
                    macros=None) -> dict[str, Medida]:
    """Una o varias carpetas de medidas. Un id repetido entre carpetas es un error, no una
    sobrescritura silenciosa: si el proyecto quiere cambiar una medida base, la renombra.

    `macros` es el registro con el que se expanden: sin él, sólo la biblioteca estándar. Un catálogo
    que use una macro del proyecto y se cargue sin su registro falla al leerse, que es lo correcto —
    la alternativa sería tratar la invocación como una medida canónica malformada y culpar al archivo
    equivocado.
    """
    salida: dict[str, Medida] = {}
    if len(directorios) == 1 and isinstance(directorios[0], (list, tuple)):
        directorios = directorios[0]
    for p in sorted(x for d in directorios for x in Path(d).rglob("*.json")):
        m = cargar(p, registro=registro, limites=limites, macros=macros)
        if m.id in salida:
            raise MedidaMalDeclarada(f"el id «{m.id}» está dos veces (último: {p.name})")
        salida[m.id] = m
    return salida


@dataclass(frozen=True)
class Informe:
    veredictos: tuple

    @property
    def ok(self) -> bool:
        return bool(self.veredictos) and all(v.ok for v in self.veredictos)

    def texto(self) -> str:
        """Nunca dice «TODO VERDE» a secas: un verde termina enumerando lo que no miró."""
        if not self.veredictos:
            return "VEREDICTO: SIN MEDIDAS — no hay nada que evaluar"
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


def evaluar(medidas, evidencia: dict, limites: LimitesAlgebra | None = None, *,
            registro=None) -> Informe:
    return Informe(tuple(
        m.evaluar(evidencia, limites, registro=registro) for m in medidas))


# ---- derivados de la declaración: el «OpenAPI» del oráculo ----

def relaciones_de_fuente(fuente) -> tuple[str, ...]:
    """Relaciones de una fuente canónica, sin inferirlas del id ni del dominio de la medida."""
    match fuente:
        case ["de", relacion, _alias]:
            return (relacion,)
        case ["unir", izquierda, derecha]:
            return tuple(dict.fromkeys((
                *relaciones_de_fuente(izquierda),
                *relaciones_de_fuente(derecha),
            )))
        case _:
            return ()


def relaciones_de_medida(medida) -> tuple[str, ...]:
    tuberia = medida.tuberia
    return relaciones_de_fuente(tuberia[1]) if isinstance(tuberia, list) and len(tuberia) > 1 else ()


def medidas_aplicables(medidas, evidencia: dict) -> list:
    """Selecciona juezas por su entrada declarada, no por ids conocidos por la herramienta."""
    relaciones = set(evidencia)
    return [medida for medida in medidas
            if set(relaciones_de_medida(medida)) <= relaciones]

def inventario(medidas) -> list[dict]:
    """Todos los umbrales con su defensa. Antes vivían escondidos en firmas de funciones."""
    return [{"id": m.id, "umbral": f"{m.op} {m.limite}", "porque": m.porque} for m in medidas]


def puntos_ciegos(medidas) -> list[dict]:
    return [{"id": m.id, "alcance": m.alcance} for m in medidas]


def como_hechos(medidas, clasificacion: ClasificacionMeta | None = None) -> list[dict]:
    """Las medidas COMO RELACIÓN, para poder medirlas con el mismo álgebra (L2 = L1 sobre L1).

    Es la pieza que vuelve esto un metalenguaje: no hay mecanismo nuevo, sólo se sirve el catálogo
    como una relación más.
    """
    def relacion_de(m):
        relaciones = relaciones_de_medida(m)
        return relaciones[0] if relaciones else ""

    clasificacion = clasificacion or clasificacion_meta_base()
    if not isinstance(clasificacion, ClasificacionMeta):
        raise MedidaMalDeclarada("`clasificacion` debe ser ClasificacionMeta")
    salida = []
    for m in medidas:
        rel = relacion_de(m)
        salida.append({
            "id": m.id, "umbral_op": m.op, "umbral_valor": m.limite, "porque": m.porque,
            "alcance": m.alcance, "relacion": rel,
            # Los dos EJES, derivados y no convenidos. El dominio sale del nombre; el NIVEL sale de
            # sobre qué se mide: una medida es meta cuando su relación es `medida`, no cuando alguien
            # la guardó en la carpeta `meta/`. Que se puedan comparar es lo que permite verificar que
            # la convención se cumpla en vez de confiar en ella.
            "dominio": m.id.split(".")[0],
            "es_meta_por_el_nombre": m.id.startswith(clasificacion.prefijos_meta),
            "es_meta_por_lo_que_mide": rel in clasificacion.relaciones_del_lenguaje,
        })
    return salida
