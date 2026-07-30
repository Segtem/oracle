"""Un dominio verificado, declarado en vez de escrito.

Es la parte de «herramienta que crea herramientas». Hoy incorporar un dominio con verificación cuesta
unas doscientas líneas de instrumento a mano, y los tres que existen son la misma estructura repetida:
armar el escenario, extraer los hechos, inyectar un defecto, correr la implementación de referencia,
comprobar las polaridades, escribir el fixture. Igual que las 22 medidas con la misma forma, eso se
declara.

## Qué declara un dominio

    Dominio(
        nombre     = "vault",
        montar     = lambda defecto: …,   # arma el escenario, con el defecto puesto o sin ninguno
        hechos     = lambda ctx: {...},   # el SENSOR: contexto → relaciones. No juzga.
        referencia = lambda ctx: bool,    # la implementación INDEPENDIENTE: ¿le parece bien?
        defectos   = ("nombre_roto", …),
    )

## Lo que se va: `espera()`

Los arneses a mano traían una función que decía, medida por medida, qué debería dar cada una. Eso
**reimplementa las medidas en Python**: dos definiciones de lo mismo que nadie mantiene sincronizadas
— el mismo defecto que los testigos duplicados del caso `004`.

Acá no existe. El fixture guarda sólo **los hechos y el veredicto de la referencia**, que es la única
información independiente que hay. La comprobación es global: *las medidas del dominio, todas juntas,
dan verde exactamente cuando la referencia da verde*. Reclamar granularidad por medida era inventar
información que la referencia no daba.

## La guarda de polaridad

Sin evidencia de los dos signos una medida no queda fijada: `aflojar_umbral` sólo lo detecta un caso
rojo, y quitarle el filtro sólo se nota si hay filas que no ofenden. Así que `generar` **se niega a
escribir** el fixture si alguna medida del dominio sale siempre igual. Eso lo comprobaban dos de los
tres arneses; el tercero no, y por eso `vault.nombre_es_ascii` estuvo sin fijar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .medida import evaluar


class DominioMalDeclarado(ValueError):
    """La declaración no alcanza para generar un fixture con sentido."""


@dataclass(frozen=True)
class Dominio:
    nombre: str
    montar: Callable[[str | None], Any]
    hechos: Callable[[Any], dict]
    referencia: Callable[[Any], bool]
    defectos: tuple[str, ...] = ()
    descripcion: str = ""
    repeticiones: int = 1              # para dominios con azar: cuántos escenarios por defecto
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.nombre or "." in self.nombre:
            raise DominioMalDeclarado(f"nombre inválido: «{self.nombre}»")
        if not self.defectos:
            raise DominioMalDeclarado(
                f"{self.nombre}: sin defectos declarados no hay evidencia roja, y sin evidencia roja "
                "ninguna medida queda fijada")


def _polaridades(medidas, escenarios: list[dict]) -> dict[str, set]:
    """Por medida, qué veredictos aparecen en el fixture. Es la cobertura, no la corrección."""
    vistos: dict[str, set] = {m.id: set() for m in medidas}
    for esc in escenarios:
        for v in evaluar(medidas, esc["evidencia"]).veredictos:
            vistos[v.id].add(v.ok)
    return vistos


def generar(dominio: Dominio, medidas) -> dict:
    """Corre el dominio contra la referencia y devuelve el fixture. Levanta si no discrimina.

    Dos cosas se comprueban y ninguna se promete:

      1. **acuerdo global** — las medidas juntas coinciden con la referencia en cada escenario. Si no,
         una de las dos implementaciones miente y no se sabe cuál;
      2. **polaridad** — cada medida sale verde en algún escenario y roja en otro.
    """
    medidas = list(medidas)
    if not medidas:
        raise DominioMalDeclarado(f"{dominio.nombre}: no hay medidas para este dominio")

    escenarios = []
    for defecto in [None, *dominio.defectos]:
        for i in range(dominio.repeticiones):
            ctx = dominio.montar(defecto) if dominio.repeticiones == 1 else dominio.montar(
                defecto if i == 0 else f"{defecto}#{i}" if defecto else f"#{i}")
            escenarios.append({
                "id": f"{defecto or 'sin-defecto'}" + (f"·{i}" if dominio.repeticiones > 1 else ""),
                "defecto": defecto or "",
                "evidencia": dominio.hechos(ctx),
                "referencia_ok": bool(dominio.referencia(ctx)),
            })

    desacuerdos = []
    for esc in escenarios:
        informe = evaluar(medidas, esc["evidencia"])
        if informe.ok != esc["referencia_ok"]:
            rojas = [v.id for v in informe.veredictos if not v.ok]
            desacuerdos.append(
                f"«{esc['id']}»: la referencia dice ok={esc['referencia_ok']} y las medidas dicen "
                f"{informe.ok}" + (f" (rojas: {rojas})" if rojas else ""))
    if desacuerdos:
        raise DominioMalDeclarado(
            f"{dominio.nombre}: el sensor y la referencia no coinciden — una de las dos miente:\n  "
            + "\n  ".join(desacuerdos))

    flojas = [mid for mid, vistos in _polaridades(medidas, escenarios).items() if len(vistos) < 2]
    if flojas:
        raise DominioMalDeclarado(
            f"{dominio.nombre}: sin las dos polaridades no quedan fijadas {flojas} — "
            "hay que declarar un defecto que las active")

    return {"origen": dominio.descripcion or f"dominio «{dominio.nombre}» vs su referencia",
            "dominio": dominio.nombre,
            # las medidas van DECLARADAS en el fixture y no se deducen del prefijo del id: el dominio
            # `relevo` usa `proceso.verificacion_vigente`, que es compartida, y deducirla la perdería
            "medidas": [m.id for m in medidas],
            "mundos": len(escenarios),
            "escenarios": escenarios}
