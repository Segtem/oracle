"""La medida: un dato que se lee, se evalúa y se puede medir a su vez.

Forma canónica, tal como se guarda en `catalogos/`:

```json
["medida", "<id>",
  ["desde", ["de", "<relacion>", "<alias>"], ["donde", <pred>]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "<la defensa del número>", "<de dónde salió>"],
  ["alcance", "<qué NO ve>"]]
```

Dos campos son obligatorios y son la razón de ser del módulo: **`alcance`**, para que un informe en
verde no pueda decir «todo bien» a secas, y **`segun`**, para que el origen del número sea
inspeccionable. La defensa en prosa sigue existiendo, pero ya no es obligatoria: dice por qué ése y
no otro, no de dónde salió.

Los **testigos no se declaran**: son las filas con las que terminó la tubería. Declararlos aparte
obliga a escribir la misma condición dos veces y a mantenerlas sincronizadas a mano — el caso
`004-testigos-duplicados` del corpus.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path

from .algebra import (COMPARADORES, ErrorDeAlgebra, LimitesAlgebra, comparar, desde, resumir,
                      validar_finito, validar_resumen, validar_tuberia)
from .macro import es_macro, expandir
from .proyecto import ID_MEDIDA_RE


class MedidaMalDeclarada(ValueError):
    pass


RELACIONES_DE_CATALOGO = frozenset({
    "ancestro",
    "medida",
    "paso_de_medida",
    "fuente",
    "termino",
    "requiere",
})

EXTENSIONES_DE_MEDIDA = frozenset({".json", ".oracle"})
SEGUN_SIN_DECLARAR = "sin_declarar"
ORIGENES_DE_UMBRAL = frozenset({"medicion", "contrato", "convencion", "tanteo"})


def _extraer_textos_ast(valor: ast.AST) -> set[str]:
    if isinstance(valor, ast.Call):
        if (isinstance(valor.func, ast.Name) and valor.func.id in ("frozenset", "set")
                and valor.args):
            return _extraer_textos_ast(valor.args[0])
        raise MedidaMalDeclarada("llamada no soportada al declarar relaciones del lenguaje")
    if isinstance(valor, (ast.Set, ast.List, ast.Tuple)):
        salida = set()
        for elt in valor.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str) and elt.value.strip():
                salida.add(elt.value)
            else:
                raise MedidaMalDeclarada(
                    "las relaciones declaradas deben ser textos no vacíos")
        return salida
    if isinstance(valor, ast.BinOp) and isinstance(valor.op, ast.BitOr):
        return _extraer_textos_ast(valor.left) | _extraer_textos_ast(valor.right)
    raise MedidaMalDeclarada("expresión no soportada al declarar relaciones del lenguaje")


def _extraer_relaciones_de_arbol(arbol: ast.AST) -> set[str]:
    relaciones: set[str] = set()
    for nodo in getattr(arbol, "body", []):
        if isinstance(nodo, ast.Assign):
            for target in nodo.targets:
                if isinstance(target, ast.Name) and (
                    target.id == "RELACIONES_DEL_LENGUAJE"
                    or target.id.startswith("RELACIONES_DE_")
                    or target.id == "RELACIONES"
                ):
                    relaciones.update(_extraer_textos_ast(nodo.value))
        elif isinstance(nodo, ast.AnnAssign):
            if isinstance(nodo.target, ast.Name) and (
                nodo.target.id == "RELACIONES_DEL_LENGUAJE"
                or nodo.target.id.startswith("RELACIONES_DE_")
                or nodo.target.id == "RELACIONES"
            ) and nodo.value is not None:
                relaciones.update(_extraer_textos_ast(nodo.value))
    return relaciones


class HechosCatalogo(list):
    """Lista de `medida` con las demás relaciones estructurales colgadas.

    Hereda de `list` para conservar la interfaz histórica: quien esperaba `como_hechos(...)` como
    relación `medida` sigue recibiendo una lista JSON-serializable.
    """

    def __init__(self, por_relacion: dict[str, list[dict]]) -> None:
        if "medida" not in por_relacion:
            raise ValueError("los hechos de catálogo tienen que traer la relación «medida»")
        self.por_relacion = {nombre: list(filas) for nombre, filas in por_relacion.items()}
        super().__init__(self.por_relacion["medida"])


MARCA_DE_DECLARACION = "RELACIONES_"


def relaciones_del_lenguaje_declaradas(raiz: Path | None = None) -> frozenset[str]:
    """Deriva el conjunto de relaciones del lenguaje a partir de lo que los emisores declaran."""
    raiz_proy = Path(__file__).resolve().parents[1] if raiz is None else Path(raiz)
    relaciones: set[str] = set()
    for dir_nombre in ("nucleo", "tools"):
        directorio = raiz_proy / dir_nombre
        if not directorio.is_dir() or directorio.is_symlink():
            continue
        for ruta in sorted(directorio.glob("*.py")):
            if ruta.is_symlink() or not ruta.is_file() or ruta.name.startswith("."):
                continue
            fuente = ruta.read_text(encoding="utf-8")
            # Sólo se parsea un archivo que DICE declarar relaciones. Sin este filtro, cualquier
            # script a medio escribir en `tools/` —que no tiene nada que ver con el lenguaje—
            # hace fallar la pregunta «¿esta medida es meta?», y el fallo no se ve: quien la hace
            # la envuelve en un `except` y se queda con un conjunto vacío. Un archivo que SÍ
            # declara y no parsea sigue siendo un error, que es el fail-closed que corresponde.
            if MARCA_DE_DECLARACION not in fuente:
                continue
            try:
                arbol = ast.parse(fuente, filename=str(ruta))
            except Exception as e:
                raise MedidaMalDeclarada(f"no se pudo parsear {ruta.name}: {e}") from e
            relaciones.update(_extraer_relaciones_de_arbol(arbol))
    return frozenset(relaciones)


def evidencia_con_derivadas(evidencia: dict) -> dict:
    """Despliega relaciones colgadas en valores de la evidencia."""
    salida = dict(evidencia)
    for filas in list(evidencia.values()):
        por_relacion = getattr(filas, "por_relacion", None)
        if por_relacion is None:
            continue
        for nombre, derivadas in por_relacion.items():
            if nombre in salida:
                if salida[nombre] is filas or salida[nombre] == derivadas:
                    continue
                raise ValueError(
                    f"la evidencia trae «{nombre}» dos veces con contenidos distintos")
            salida[nombre] = derivadas
    return salida


@dataclass(frozen=True)
class ClasificacionMeta:
    """Contrato extensible para distinguir lenguaje y mundo.

    El núcleo trae las relaciones que él mismo produce, pero no pretende conocer las relaciones
    reflexivas de cada proyecto. Un perfil puede añadirlas y también declarar sus prefijos.
    """

    # `paso`, `nodo` y `producto` son la traza del evaluador midiéndose a sí mismo: describen lo que
    # hizo el álgebra, no el mundo. Son tan reflexivas como `medida`.
    relaciones_del_lenguaje: frozenset[str] = field(
        default_factory=relaciones_del_lenguaje_declaradas)
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
    segun: str = SEGUN_SIN_DECLARAR
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
        # La gramática del id se comprobaba SÓLO al crear el archivo (`ruta_de_medida_nueva`), así
        # que un catálogo podía guardar ids que la propia herramienta se niega a crear. Se comprueba
        # también al cargar: la razón del ASCII está escrita al lado de `ID_MEDIDA_RE`.
        if not isinstance(mid, str) or ID_MEDIDA_RE.fullmatch(mid) is None:
            raise MedidaMalDeclarada(
                f"id inválido: «{mid}» — debe ser `dominio.nombre`, sólo con minúsculas ASCII, "
                "dígitos y `_`")
        try:
            validar_tuberia(tuberia, limites, registro=registro)
            validar_resumen(resumen, limites, registro=registro)
        except ErrorDeAlgebra as e:
            raise MedidaMalDeclarada(f"{mid}: {e}") from e
        if not (isinstance(umbral, list) and len(umbral) in (4, 5)
                and umbral[0] == "umbral"):
            raise MedidaMalDeclarada(
                f"{mid}: el umbral es ['umbral', op, valor, porque, segun]")
        if len(umbral) == 5:
            _, op, limite, porque, segun = umbral
            if segun != SEGUN_SIN_DECLARAR and segun not in ORIGENES_DE_UMBRAL:
                raise MedidaMalDeclarada(
                    f"{mid}: `segun` debe ser uno de {sorted(ORIGENES_DE_UMBRAL)}; "
                    f"recibió {segun!r}")
        else:
            _, op, limite, porque = umbral
            segun = SEGUN_SIN_DECLARAR
        if op not in COMPARADORES:
            raise MedidaMalDeclarada(f"{mid}: operador «{op}» no está en {list(COMPARADORES)}")
        if not isinstance(limite, (str, int, float, bool)):
            raise MedidaMalDeclarada(
                f"{mid}: el valor del umbral tiene que ser escalar, no {type(limite).__name__}")
        try:
            validar_finito(limite, "el valor del umbral")
        except ErrorDeAlgebra as e:
            raise MedidaMalDeclarada(f"{mid}: {e}") from e
        # La igualdad exacta sobre un flotante NO se valida acá: es una POLÍTICA, no un contrato de
        # carga. Un umbral `== 3.14` está bien formado y se puede cargar; el juicio de que es una
        # mala idea vive en dos lugares: `algebra.comparar`, que sigue fallando cerrado al EVALUAR, y
        # `meta.ningun_umbral_flotante_de_igualdad`, que lo vuelve inspeccionable en L2. Quitar el
        # `raise` de carga no abre un hueco: la medida no puede producir un verde porque el álgebra
        # la frena antes de comparar.
        # La prosa ya no es obligatoria: `segun` es lo evaluable. Sigue teniendo que ser texto para
        # que una medida no pueda esconder datos estructurados en la ranura humana.
        if not isinstance(porque, str):
            raise MedidaMalDeclarada(
                f"{mid}: la defensa del umbral tiene que ser texto, no {type(porque).__name__}")
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
                   porque=porque, alcance=alcance[1], segun=segun, requiere=nombres,
                   fuente=tuple(fuente) if es_macro(fuente, macros) else ())

    def evaluar(self, evidencia: dict, limites: LimitesAlgebra | None = None, *,
                registro=None) -> Veredicto:
        evidencia = evidencia_con_derivadas(evidencia)
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
                    ["umbral", self.op, self.limite, self.porque, self.segun]]
        # Una medida sin `requiere` NO emite el nodo: la forma canónica de las que ya existían no
        # cambia, y con ella no cambian sus huellas ni las rutas de sus mutantes.
        if self.requiere:
            canonica.append(["requiere", *self.requiere])
        return [*canonica, ["alcance", self.alcance]]

    def a_fuente(self) -> list:
        """Cómo está escrita en el archivo: la macro si vino de una, la canónica si no."""
        return list(self.fuente) if self.fuente else self.a_datos()


def _normalizar_directorios(directorios) -> tuple:
    if len(directorios) == 1 and isinstance(directorios[0], (list, tuple)):
        return tuple(directorios[0])
    return tuple(directorios)


def _rutas_en_catalogo(directorio) -> list[Path]:
    base = Path(directorio)
    if not base.exists():
        return []
    if base.is_symlink() or not base.is_dir():
        raise MedidaMalDeclarada(f"el catálogo debe ser un directorio físico: {base}")
    try:
        base_fisica = base.resolve()
    except OSError as e:
        raise MedidaMalDeclarada(f"no se pudo resolver el catálogo {base}: {e}") from e
    rutas = []
    for ruta in base.rglob("*"):
        if ruta.suffix not in EXTENSIONES_DE_MEDIDA:
            continue
        if ruta.is_symlink():
            raise MedidaMalDeclarada(f"una medida de catálogo no puede ser symlink: {ruta}")
        try:
            fisica = ruta.resolve()
            fisica.relative_to(base_fisica)
        except (OSError, ValueError) as e:
            raise MedidaMalDeclarada(f"la medida {ruta} no está confinada en {base_fisica}") from e
        if not fisica.is_file():
            raise MedidaMalDeclarada(f"la medida debe ser un archivo físico: {ruta}")
        rutas.append(ruta)
    return sorted(rutas)


def rutas_de_catalogo(*directorios) -> list[Path]:
    """Archivos de medidas del catálogo, en todos los formatos declarados."""
    return sorted(
        ruta
        for directorio in _normalizar_directorios(directorios)
        for ruta in _rutas_en_catalogo(directorio)
    )


def ruta_de_medida(mid: str, *directorios) -> Path:
    """El archivo de una medida por su id, en el formato en que esté guardada.

    Existe porque una decena de tests apuntaban a `catalogos/<dominio>/<id>.json` a mano, y al
    pasar el catálogo a `.oracle` fallaron todos por el RENOMBRE en vez de por lo que dicen medir.
    Un test que se cae cuando cambia el formato de almacenamiento no está midiendo el formato:
    está acoplado a él sin querer.
    """
    candidatos = [r for r in rutas_de_catalogo(*directorios) if r.stem == mid]
    if len(candidatos) != 1:
        raise MedidaMalDeclarada(
            f"«{mid}» no está una sola vez en el catálogo: {len(candidatos)} archivos")
    return candidatos[0]


def cargar_fuente_medida(ruta: Path, *, macros=None) -> list:
    """Lee una medida de catálogo y devuelve su forma de datos."""
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as e:
        raise MedidaMalDeclarada(f"no se pudo leer la medida {ruta}: {e}") from e
    if ruta.suffix == ".json":
        try:
            return json.loads(texto)
        except json.JSONDecodeError as e:
            raise MedidaMalDeclarada(f"{ruta}: JSON inválido — {e}") from e
    if ruta.suffix == ".oracle":
        from .sintaxis import ErrorSintaxis, fragmento_de_error, leer_con_mapa
        from .version import VersionInvalida, exigir_sintaxis_compatible

        try:
            lectura = leer_con_mapa(texto, macros=macros)
        except ErrorSintaxis as e:
            raise MedidaMalDeclarada(f"{ruta}: {fragmento_de_error(e, texto)}") from e
        try:
            exigir_sintaxis_compatible(lectura.version)
        except VersionInvalida as e:
            raise MedidaMalDeclarada(f"{ruta}: {e}") from e
        return lectura.datos
    raise MedidaMalDeclarada(
        f"formato de medida no soportado: {ruta} (esperaba .json u .oracle)")


def cargar(ruta: Path, *, registro=None,
           limites: LimitesAlgebra | None = None, macros=None) -> Medida:
    return Medida.de_datos(
        cargar_fuente_medida(ruta, macros=macros),
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
    fuentes: dict[str, Path] = {}
    for p in rutas_de_catalogo(*directorios):
        m = cargar(p, registro=registro, limites=limites, macros=macros)
        if m.id in salida:
            raise MedidaMalDeclarada(
                f"el id «{m.id}» está dos veces: {fuentes[m.id]} y {p}")
        salida[m.id] = m
        fuentes[m.id] = p
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
    relaciones = set(evidencia_con_derivadas(evidencia))
    return [medida for medida in medidas
            if set(relaciones_de_medida(medida)) <= relaciones]

def inventario(medidas) -> list[dict]:
    """Todos los umbrales con su defensa. Antes vivían escondidos en firmas de funciones."""
    return [
        {"id": m.id, "umbral": f"{m.op} {m.limite}", "porque": m.porque, "segun": m.segun}
        for m in medidas
    ]


def puntos_ciegos(medidas) -> list[dict]:
    return [{"id": m.id, "alcance": m.alcance} for m in medidas]


def hechos_de_catalogo(medidas, clasificacion: ClasificacionMeta) -> HechosCatalogo:
    medidas = tuple(medidas)
    por_relacion = {nombre: [] for nombre in sorted(RELACIONES_DE_CATALOGO)}
    for medida in medidas:
        por_relacion["medida"].append(_hecho_medida(medida, clasificacion))
        por_relacion["paso_de_medida"].extend(_pasos_de(medida))
        por_relacion["fuente"].extend(_fuentes_de_medida(medida))
        por_relacion["termino"].extend(_terminos_de_medida(medida))
        por_relacion["ancestro"].extend(_ancestros_de_medida(medida))
        por_relacion["requiere"].extend(_requiere_de(medida))
    return HechosCatalogo(por_relacion)


def _hecho_medida(medida, clasificacion: ClasificacionMeta) -> dict:
    relaciones = relaciones_de_medida(medida)
    relacion = relaciones[0] if relaciones else ""
    return {
        "id": medida.id,
        "dominio": medida.id.split(".")[0],
        "relacion": relacion,
        "agregado": medida.resumen[1],
        "comparador": medida.op,
        "umbral": medida.limite,
        "umbral_op": medida.op,
        "umbral_valor": medida.limite,
        "umbral_es_flotante": isinstance(medida.limite, float),
        "porque": medida.porque,
        "segun": getattr(medida, "segun", SEGUN_SIN_DECLARAR),
        "alcance": medida.alcance,
        "pasos": max(0, len(medida.tuberia) - 1),
        "declara_requiere": bool(medida.requiere),
        "es_meta_por_el_nombre": medida.id.startswith(clasificacion.prefijos_meta),
        "es_meta_por_lo_que_mide": bool(
            relacion and relacion in clasificacion.relaciones_del_lenguaje),
    }


def _ruta(indices: tuple[int, ...]) -> str:
    return ".".join(str(i) for i in indices)


def _tipo(valor) -> str:
    if isinstance(valor, list):
        return "lista"
    if isinstance(valor, bool):
        return "booleano"
    if isinstance(valor, int):
        return "entero"
    if isinstance(valor, float):
        return "flotante"
    if isinstance(valor, str):
        return "texto"
    if valor is None:
        return "ausente"
    return type(valor).__name__


def _cabeza(nodo) -> str:
    return nodo[0] if isinstance(nodo, list) and nodo and isinstance(nodo[0], str) else ""


def _texto_literal(valor) -> str:
    """Representación visible de literales en `termino.texto`.

    Uso un solo campo textual en vez de campos opcionales por tipo: las cadenas quedan como el valor
    que ya publicaba `termino`, y enteros, flotantes, booleanos y `null` se escriben como JSON
    compacto. `tipo` desambigua, por ejemplo, el texto `"null"` de un ausente real, sin meter
    defaults silenciosos para columnas que no aplican.
    """
    if isinstance(valor, str):
        return valor
    if isinstance(valor, (bool, int, float)) or valor is None:
        try:
            return json.dumps(valor, separators=(",", ":"), allow_nan=False)
        except ValueError as e:
            raise MedidaMalDeclarada(f"literal no reificable en `termino`: {valor!r}") from e
    raise MedidaMalDeclarada(f"literal no reificable en `termino`: {type(valor).__name__}")


def _terminos_de_medida(medida) -> list[dict]:
    return list(_terminos(medida.id, medida.a_datos(), (), (), ""))


def _terminos(medida: str, nodo, ruta: tuple[int, ...],
              padre: tuple[int, ...], cabeza_padre: str):
    base = {
        "medida": medida,
        "ruta": _ruta(ruta),
        "padre": _ruta(padre),
        "cabeza_padre": cabeza_padre,
    }
    if isinstance(nodo, list):
        yield {
            **base,
            "tipo": "lista",
            "cabeza": _cabeza(nodo),
            "texto": "",
            "longitud": len(nodo),
        }
        for indice, hijo in enumerate(nodo):
            yield from _terminos(medida, hijo, (*ruta, indice), ruta, _cabeza(nodo))
        return
    yield {
        **base,
        "tipo": _tipo(nodo),
        "cabeza": "",
        "texto": "" if isinstance(nodo, list) else _texto_literal(nodo),
        "longitud": 0,
    }


def _ancestros_de_medida(medida) -> list[dict]:
    return list(_ancestros(medida.id, medida.a_datos(), (), (), ""))


def _ancestros(medida: str, nodo, ruta: tuple[int, ...],
               ancestros: tuple[tuple[tuple[int, ...], str], ...], cabeza_padre: str):
    """Un hecho por (nodo, ancestro suyo), CON los atributos del nodo repetidos en cada fila.

    La repetición es deliberada y tiene una razón medida. La forma normalizada —`ancestro` con la
    ruta sola, y los atributos del nodo sólo en `termino`— obliga a que toda pregunta sobre la
    estructura una las dos relaciones. Y `unir` arma el producto completo antes de filtrar: sobre
    este catálogo son 1917 × 4699 = 9 millones de pares para quedarse con 1917, muy por encima del
    límite de un millón que protege la memoria. La medida no corría.

    Salir de ahí por el lado del evaluador —enseñarle a indexar el `unir` seguido de `donde`— se
    probó y se midió: 228 líneas nuevas en `nucleo/algebra.py` y 31 mutantes de código vivos, contra
    0 en todo lo que ya estaba. Código sin vigilar en el módulo donde un error da veredictos
    equivocados en silencio.

    Repetir cinco campos por fila cuesta memoria y no cuesta mecanismo. La pregunta se contesta con
    un `de` y un `donde`, que es lo que el lenguaje ya sabía hacer.
    """
    for ruta_ancestro, cabeza_ancestro in ancestros:
        yield {
            "medida": medida,
            "ruta": _ruta(ruta),
            "ancestro": _ruta(ruta_ancestro),
            "cabeza_ancestro": cabeza_ancestro,
            "tipo": _tipo(nodo),
            "cabeza": _cabeza(nodo),
            "cabeza_padre": cabeza_padre,
            "texto": "" if isinstance(nodo, list) else _texto_literal(nodo),
        }
    if not isinstance(nodo, list):
        return
    propios = (*ancestros, (ruta, _cabeza(nodo)))
    for indice, hijo in enumerate(nodo):
        yield from _ancestros(medida, hijo, (*ruta, indice), propios, _cabeza(nodo))


def _pasos_de(medida) -> list[dict]:
    pasos = []
    for indice, paso in enumerate(medida.tuberia[1:]):
        pasos.append({
            "medida": medida.id,
            "indice": indice,
            "ruta": _ruta((2, indice + 1)),
            "operador": _cabeza(paso),
        })
    return pasos


def _fuentes_de_medida(medida) -> list[dict]:
    return list(_fuentes(medida.id, medida.tuberia[1], (2, 1)))


def _fuentes(medida: str, fuente, ruta: tuple[int, ...]):
    if not isinstance(fuente, list) or not fuente:
        return
    if fuente[0] == "de":
        yield {
            "medida": medida,
            "ruta": _ruta(ruta),
            "relacion": fuente[1],
            "alias": fuente[2],
        }
    elif fuente[0] == "unir":
        yield from _fuentes(medida, fuente[1], (*ruta, 1))
        yield from _fuentes(medida, fuente[2], (*ruta, 2))


def _requiere_de(medida) -> list[dict]:
    return [
        {"medida": medida.id, "indice": indice, "relacion": relacion}
        for indice, relacion in enumerate(medida.requiere)
    ]


def como_hechos(medidas, clasificacion: ClasificacionMeta | None = None) -> list[dict]:
    """Las medidas COMO RELACIONES, para poder medirlas con el mismo álgebra (L2 = L1 sobre L1).

    Es la pieza que vuelve esto un metalenguaje: no hay mecanismo nuevo, sólo se sirve el catálogo
    como una relación más.
    """
    clasificacion = clasificacion or clasificacion_meta_base()
    if not isinstance(clasificacion, ClasificacionMeta):
        raise MedidaMalDeclarada("`clasificacion` debe ser ClasificacionMeta")
    return hechos_de_catalogo(medidas, clasificacion)
