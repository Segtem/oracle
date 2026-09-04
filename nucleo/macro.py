"""Macros: medidas que escriben medidas — y que ahora se declaran EN DATOS.

## Por qué cambió

Hasta este corte `MACROS` era un diccionario de funciones de Python acá adentro. O sea: las medidas
eran datos, pero **los medios de abstracción no**. Un proyecto que quería una forma propia tenía que
editar el núcleo de Oracle, y eso contradice de frente lo que el repositorio afirma de sí mismo — que
sin homoiconicidad el lenguaje tiene dueño, y que el dueño sería el LLM. El dueño *era* quien podía
editar este archivo.

Ahora una macro es un archivo de datos, con la misma forma para las que trae Oracle y para las que
escribe un proyecto:

```json
["defmacro", "<nombre>",
  ["<parametro>", ...],
  [["guarda", <expresion>, "<mensaje>"], ...],
  <plantilla>]
```

La plantilla es la forma canónica con huecos `["$", "<parametro>"]`. Expandir es sustituir. Las
macros universales viven en `nucleo/macros/` y se cargan como cualquier otra: son la biblioteca
estándar del lenguaje, no un privilegio del núcleo.

## Las guardas no traen evaluador nuevo

`ninguno-par` exige que sus dos alias difieran, y una plantilla pura no sabe expresar eso. La guarda
se sustituye primero y se evalúa después con `evaluar_expr` del álgebra sobre una **fila vacía**: una
expresión sin accesores nunca toca la fila, así que el mecanismo ya existía. De regalo hereda todo el
contrato del álgebra — comparación entre familias incompatibles, prohibición de igualdad exacta entre
flotantes, límites de profundidad.

## Esto no cuesta inspeccionabilidad

Una macro **expande a los mismos datos**, igual que en LISP: la expansión ocurre antes de construir la
medida, así que el evaluador, la mutación, el inventario y el nivel L2 siguen viendo formas canónicas
y no se enteran de que hubo macro. `tools/medida.py --expandir` muestra el resultado.

## Las macros son azúcar, no un embudo

La forma canónica sigue siendo válida y hay medidas que no pasan por macro. Un sistema de macros que
obliga a todo a pasar por él se vuelve una camisa de fuerza: si la forma no encaja, se escribe
canónica y listo.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .algebra import (AGREGADOS, COMPARADORES, ErrorDeAlgebra, LimitesAlgebra, LOGICOS,
                      ACCESORES, evaluar_expr)


class MacroMalUsada(ValueError):
    """La invocación no tiene la forma que la macro necesita."""


class MacroMalDeclarada(ValueError):
    """La declaración de la macro es inválida. Se rompe al LEERLA, no al usarla."""


NOMBRE_MACRO_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
HUECO = "$"

# Un nombre de macro no puede tapar una palabra del lenguaje: si `donde` fuera macro, leer una
# tubería dejaría de significar una sola cosa. Falla cerrado al declararla, no al expandir.
RESERVADAS = frozenset({
    "defmacro", "guarda", HUECO,
    "medida", "desde", "resumen", "umbral", "segun", "ambito", "alcance",
    "de", "unir", "donde", "agrupar",
    *COMPARADORES, *LOGICOS, *ACCESORES, *AGREGADOS,
})


def _texto(valor, que: str, error=MacroMalDeclarada) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise error(f"{que} tiene que ser texto no vacío, no {valor!r}")
    return valor


def _es_hueco(nodo) -> bool:
    return isinstance(nodo, list) and bool(nodo) and nodo[0] == HUECO


def _huecos_de(nodo, encontrados: set[str]) -> None:
    """Recolecta los parámetros usados. Un hueco mal formado se denuncia acá, en la declaración."""
    if not isinstance(nodo, list):
        return
    if _es_hueco(nodo):
        if len(nodo) != 2:
            raise MacroMalDeclarada(f"un hueco va ['{HUECO}', parametro] — recibió {nodo!r}")
        encontrados.add(_texto(nodo[1], "el nombre de un hueco"))
        return
    for hijo in nodo:
        _huecos_de(hijo, encontrados)


def _sustituir(nodo, valores: dict):
    """Reemplaza cada hueco por su argumento. Devuelve el MISMO objeto, no una copia: si un
    parámetro aparece dos veces —la tolerancia de `peor`, el caso 012 del corpus— las dos
    apariciones son literalmente el mismo dato y no pueden divergir."""
    if not isinstance(nodo, list):
        return nodo
    if _es_hueco(nodo):
        nombre = nodo[1]
        if nombre not in valores:
            raise MacroMalUsada(f"el hueco «{nombre}» no tiene argumento")
        return valores[nombre]
    return [_sustituir(hijo, valores) for hijo in nodo]


def _quitar_segun_sin_declarar(nodo) -> None:
    if not isinstance(nodo, list):
        return
    if len(nodo) == 5 and nodo[0] == "umbral" and nodo[4] == "sin_declarar":
        del nodo[4]
        return
    for hijo in nodo:
        _quitar_segun_sin_declarar(hijo)


def _quitar_ambito_sin_declarar(nodo) -> None:
    """El espejo de la de arriba: una invocación anterior a `ambito` no escribe la cláusula.

    Emitir `ambito sin_declarar` en la forma canónica diría que el autor eligió el estado de
    migración, y no eligió nada: la cláusula no existía cuando escribió la medida. Se conserva la
    ausencia, que es lo que `Medida` reifica igual como `sin_declarar` y lo que la medida de
    presencia va a señalar.
    """
    if not isinstance(nodo, list):
        return
    for indice, hijo in enumerate(nodo):
        if (isinstance(hijo, list) and len(hijo) == 2
                and hijo[0] == "ambito" and hijo[1] == "sin_declarar"):
            del nodo[indice]
            return
        _quitar_ambito_sin_declarar(hijo)


@dataclass(frozen=True)
class Macro:
    nombre: str
    parametros: tuple[str, ...]
    guardas: tuple[tuple, ...]
    plantilla: list

    @classmethod
    def de_datos(cls, datos) -> "Macro":
        if not isinstance(datos, list) or len(datos) != 5 or datos[0] != "defmacro":
            raise MacroMalDeclarada(
                "una macro es ['defmacro', nombre, parametros, guardas, plantilla]")
        _, nombre, parametros, guardas, plantilla = datos

        _texto(nombre, "el nombre de una macro")
        if NOMBRE_MACRO_RE.fullmatch(nombre) is None:
            raise MacroMalDeclarada(
                f"«{nombre}»: el nombre usa minúsculas ASCII, dígitos, `_` y `-`")
        if nombre in RESERVADAS:
            raise MacroMalDeclarada(
                f"«{nombre}» es una palabra del lenguaje y no puede ser nombre de macro")

        if not isinstance(parametros, list) or not parametros:
            raise MacroMalDeclarada(f"{nombre}: los parámetros van en una lista no vacía")
        for parametro in parametros:
            _texto(parametro, f"{nombre}: el nombre de un parámetro")
        if len(set(parametros)) != len(parametros):
            raise MacroMalDeclarada(f"{nombre}: hay parámetros repetidos")

        if not isinstance(plantilla, list) or not plantilla:
            raise MacroMalDeclarada(f"{nombre}: la plantilla tiene que ser una lista no vacía")

        if not isinstance(guardas, list):
            raise MacroMalDeclarada(
                f"{nombre}: las guardas van en una lista — sin guardas se escribe []")
        normalizadas = []
        for guarda in guardas:
            if not isinstance(guarda, list) or len(guarda) != 3 or guarda[0] != "guarda":
                raise MacroMalDeclarada(
                    f"{nombre}: una guarda va ['guarda', expresion, mensaje]")
            _texto(guarda[2], f"{nombre}: el mensaje de una guarda")
            normalizadas.append((guarda[1], guarda[2]))

        usados: set[str] = set()
        _huecos_de(plantilla, usados)
        for expresion, _mensaje in normalizadas:
            _huecos_de(expresion, usados)

        desconocidos = sorted(usados - set(parametros))
        if desconocidos:
            raise MacroMalDeclarada(
                f"{nombre}: usa huecos que no son parámetros: {desconocidos}")
        # Un parámetro que nadie usa es decoración: se pide al invocar, se cuenta en la aridad, y no
        # llega a ninguna parte. Es la misma regla que `meta.toda_medida_esta_ejercitada`.
        sin_usar = sorted(set(parametros) - usados)
        if sin_usar:
            raise MacroMalDeclarada(
                f"{nombre}: declara parámetros que la plantilla nunca usa: {sin_usar}")

        return cls(nombre, tuple(parametros), tuple(normalizadas), plantilla)

    def _omisibles_por_legado(self) -> int:
        """Cuántos parámetros finales puede no traer una invocación anterior a ellos.

        Se cuentan desde `alcance` hacia atrás, y sólo mientras se llamen `segun` o `ambito`: son
        los dos que se agregaron después de que había medidas escritas. No hay un corte fijo escrito
        a mano —`parametros[-3:-1]` y cosas así— porque un número acá sería una suposición sobre el
        largo de una firma ajena: un proyecto declara sus propias macros y no tienen por qué medir
        lo mismo. Además una constante que el filtro vuelve irrelevante no la fija nada, y la
        mutación lo señaló.
        """
        # Sin guarda de lista vacía: `de_datos` ya rechaza una macro sin parámetros, así que esa
        # rama no la puede ejercitar nada y la mutación la deja viva. Una rama muerta no se declara.
        if self.parametros[-1] != "alcance":
            return 0
        cuenta = 0
        for parametro in reversed(self.parametros[:-1]):
            if parametro not in ("segun", "ambito"):
                break
            cuenta += 1
        return cuenta

    def expandir(self, datos: list, limites: LimitesAlgebra | None = None) -> list:
        esperados = len(self.parametros)
        recibidos = len(datos) - 1
        # Compatibilidad con invocaciones anteriores a `segun` y a `ambito`. No se elige un valor
        # creíble: se conserva la AUSENCIA como `sin_declarar`, igual que un umbral canónico de 4
        # elementos. La diferencia con un default importa — un default afirmaría que el autor
        # eligió, y las medidas de presencia (`meta.todo_umbral_declara_de_donde_sale`, y la del
        # ámbito) existen justamente para reclamar que elija.
        #
        # Los dos parámetros son los que preceden a `alcance`, en ese orden, y una invocación vieja
        # puede no traer ninguno, sólo el último, o los dos. Sin esto, agregar `ambito` deja de
        # cargar el catálogo entero de un consumidor: en los dos que se midieron, la mayoría de
        # sus medidas pasan por una macro.
        faltantes = esperados - recibidos
        # `range` y no `0 < faltantes <= n`: con la comparación, `faltantes == 0` entra al cuerpo y
        # no cambia nada —multiplicar por cero da la lista vacía—, así que mover el `<` a `<=` no se
        # puede distinguir y el mutante sobrevive. Acá los dos extremos cargan peso: el 1 excluye la
        # invocación completa y el `+ 1` es el último faltante que todavía se perdona.
        if faltantes in range(1, self._omisibles_por_legado() + 1):
            datos = [*datos[:-1], *["sin_declarar"] * faltantes, datos[-1]]
            recibidos = esperados
        legado_sin_segun = faltantes > 0
        if recibidos != esperados:
            firma = ", ".join(self.parametros)
            raise MacroMalUsada(
                f"«{self.nombre}» va [{firma}] — recibió {recibidos} argumento(s)")
        valores = dict(zip(self.parametros, datos[1:]))

        for expresion, mensaje in self.guardas:
            sustituida = _sustituir(expresion, valores)
            try:
                cumple = evaluar_expr(sustituida, {}, limites)
            except ErrorDeAlgebra as e:
                raise MacroMalUsada(f"{self.nombre}: la guarda no se pudo evaluar: {e}") from e
            if not cumple:
                # `datos[1]` existe siempre: la aridad ya se comprobó y ninguna macro tiene cero
                # parámetros, así que acá hay al menos cabeza y primer argumento. La guarda
                # `if len(datos) > 1` que había antes era una rama muerta —la mutación la marcó
                # equivalente— y una rama que nada puede ejercitar no se declara, se borra.
                raise MacroMalUsada(f"{datos[1]}: {mensaje}")

        expandida = _sustituir(self.plantilla, valores)
        if legado_sin_segun:
            _quitar_segun_sin_declarar(expandida)
            _quitar_ambito_sin_declarar(expandida)
        return expandida


class RegistroMacros(dict[str, Macro]):
    """Registro copiable que un consumidor puede poseer sin compartir estado global."""

    def copiar(self) -> "RegistroMacros":
        return RegistroMacros(self)

    def declarar(self, macro: Macro) -> None:
        if macro.nombre in self:
            raise MacroMalDeclarada(f"la macro «{macro.nombre}» ya está declarada")
        self[macro.nombre] = macro


DIRECTORIO_BASE = Path(__file__).resolve().parent / "macros"


# Los dos formatos de una macro, con la misma regla que el catálogo: `.oracle` es cómo se escribe,
# `.json` es cómo se guarda. Una macro es la otra mitad del lenguaje —la superficie que cubre las
# medidas y no las macros es la sintaxis de la mitad del lenguaje— así que se lee de los dos lados.
EXTENSIONES_DE_MACRO = (".json", ".oracle")


def _datos_de_macro(ruta: Path, macros: RegistroMacros | None = None) -> list:
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as e:
        raise MacroMalDeclarada(f"no se pudo leer la macro {ruta}: {e}") from e
    if ruta.suffix == ".oracle":
        from .sintaxis import ErrorSintaxis, fragmento_de_error, leer_con_mapa
        from .version import VersionInvalida, exigir_sintaxis_compatible

        try:
            lectura = leer_con_mapa(texto, macros=macros)
        except ErrorSintaxis as e:
            raise MacroMalDeclarada(f"{ruta}: {fragmento_de_error(e, texto)}") from e
        try:
            exigir_sintaxis_compatible(lectura.version)
        except VersionInvalida as e:
            raise MacroMalDeclarada(f"{ruta}: {e}") from e
        return lectura.datos
    try:
        return json.loads(texto)
    except json.JSONDecodeError as e:
        raise MacroMalDeclarada(f"no se pudo leer la macro {ruta}: {e}") from e


def cargar_macros(*directorios, registro: RegistroMacros | None = None) -> RegistroMacros:
    """Lee `.json` y `.oracle` de cada directorio. Un nombre repetido es un error, no una
    sobrescritura — y eso incluye el mismo nombre en los dos formatos: ahí no gana ninguno, porque
    un ganador silencioso es una divergencia esperando a que alguien edite la copia equivocada."""
    destino = RegistroMacros() if registro is None else registro
    if len(directorios) == 1 and isinstance(directorios[0], (list, tuple)):
        directorios = directorios[0]
    rutas = sorted(x for d in directorios for x in Path(d).rglob("*")
                   if x.suffix in EXTENSIONES_DE_MACRO and x.is_file())
    for ruta in rutas:
        try:
            destino.declarar(Macro.de_datos(_datos_de_macro(ruta, destino)))
        except MacroMalDeclarada as e:
            raise MacroMalDeclarada(f"{ruta.name}: {e}") from e
    return destino


def macros_base() -> RegistroMacros:
    """Copia independiente de la biblioteca estándar del lenguaje."""
    return _base().copiar()


def exigir_biblioteca(registro: RegistroMacros, directorio: Path) -> RegistroMacros:
    """`rglob` sobre un directorio ausente devuelve vacío, así que una instalación a la que le
    falten los datos se quedaría sin biblioteca estándar EN SILENCIO: cada medida escrita con
    `ninguno` fallaría después con «una medida es [...]», culpando al archivo equivocado. Se
    denuncia acá, donde está la causa."""
    if not registro:
        raise MacroMalDeclarada(
            f"no hay macros en {directorio}: la biblioteca estándar del lenguaje falta o la "
            "instalación quedó incompleta")
    return registro


_BASE: RegistroMacros | None = None


def _base() -> RegistroMacros:
    """Carga perezosa y memorizada de la biblioteca estándar.

    Antes esto corría al importar el módulo, y la mutación de código lo denunció: un mutante que
    rompía la validación de `Macro.de_datos` hacía fallar el **descubrimiento** de los tests, así que
    el arnés reportaba «error» en vez de «muerto». Es el caso `017` del corpus —un error del arnés no
    es una muerte— provocado por el propio diseño. Cargar al primer uso devuelve esos mutantes al
    lugar donde un test puede matarlos.
    """
    global _BASE
    if _BASE is None:
        _BASE = exigir_biblioteca(cargar_macros(DIRECTORIO_BASE), DIRECTORIO_BASE)
    return _BASE


def _registro(macros: RegistroMacros | None) -> RegistroMacros:
    if macros is None:
        return _base()
    if not isinstance(macros, RegistroMacros):
        raise MacroMalDeclarada("`macros` debe ser una instancia de RegistroMacros")
    return macros


def es_macro(datos, macros: RegistroMacros | None = None) -> bool:
    return (isinstance(datos, list) and bool(datos)
            and isinstance(datos[0], str) and datos[0] in _registro(macros))


def expandir(datos: list, macros: RegistroMacros | None = None,
             limites: LimitesAlgebra | None = None) -> list:
    """Datos → forma canónica. Idempotente sobre lo que ya es canónico.

    Una macro puede expandir a otra: ahora que un proyecto declara las suyas, negarle construir sobre
    `ninguno` lo obligaría a copiar el cuerpo, que es justo lo que la macro vino a evitar. La torre
    está acotada por `expansiones_maximas`, porque una macro que se expande a sí misma es un cuelgue,
    no un error de sintaxis.
    """
    registro = _registro(macros)
    tope = (limites or LimitesAlgebra()).expansiones_maximas
    vistas = []
    for _ in range(tope):
        if not es_macro(datos, registro):
            return datos
        vistas.append(datos[0])
        datos = registro[datos[0]].expandir(datos, limites)
    raise MacroMalUsada(
        f"la expansión superó las {tope} vueltas declaradas; cadena: {' → '.join(vistas)}")
