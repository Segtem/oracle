"""Un dominio verificado, declarado en vez de escrito.

Es la parte de «herramienta que crea herramientas». Incorporar un dominio con verificación suele
repetir la misma estructura:
armar el escenario, extraer los hechos, inyectar un defecto, correr la implementación de referencia,
comprobar las polaridades, escribir el fixture. Igual que las 22 medidas con la misma forma, eso se
declara.

## Qué declara un dominio

    Dominio(
        nombre     = "ejemplo",
        montar     = lambda defecto, i: …,  # arma el escenario n° i, con el defecto puesto o sin ninguno
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
instrumentos existentes; omitirla deja medidas sin fijar aunque el acuerdo global parezca correcto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .diferencial import (ESQUEMA_DIFERENCIAL, Procedencia, crear_frescura)
from .medida import evaluar


class DominioMalDeclarado(ValueError):
    """La declaración no alcanza para generar un fixture con sentido."""


@dataclass(frozen=True)
class Dominio:
    nombre: str
    montar: Callable[[str | None, int], Any]
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
        for mid, ok in esc["oracle_al_generar"]["por_medida"].items():
            vistos[mid].add(ok)
    return vistos


def _configuracion(dominio: Dominio) -> dict:
    return {
        "nombre": dominio.nombre,
        "descripcion": dominio.descripcion,
        "defectos": list(dominio.defectos),
        "repeticiones": dominio.repeticiones,
        "extra": dominio.extra,
    }


def generar(dominio: Dominio, medidas, *, procedencia: Procedencia) -> dict:
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
            # `i` va aparte del defecto: un dominio con azar lo usa de semilla y uno determinista lo
            # ignora. Antes se le mangleaba el nombre del defecto, que era una forma de pasar dos
            # cosas por un solo parámetro.
            ctx = dominio.montar(defecto, i)
            evidencia = dominio.hechos(ctx)
            informe = evaluar(medidas, evidencia)
            escenarios.append({
                "id": f"{defecto or 'sin-defecto'}" + (f"·{i}" if dominio.repeticiones > 1 else ""),
                "defecto": defecto or "",
                "evidencia": evidencia,
                "referencia_ok": bool(dominio.referencia(ctx)),
                "oracle_al_generar": {
                    "global_ok": informe.ok,
                    "por_medida": {v.id: v.ok for v in informe.veredictos},
                },
            })

    desacuerdos = []
    for esc in escenarios:
        oracle = esc["oracle_al_generar"]
        if oracle["global_ok"] != esc["referencia_ok"]:
            rojas = [mid for mid, ok in oracle["por_medida"].items() if not ok]
            desacuerdos.append(
                f"«{esc['id']}»: la referencia dice ok={esc['referencia_ok']} y las medidas dicen "
                f"{oracle['global_ok']}" + (f" (rojas: {rojas})" if rojas else ""))
    if desacuerdos:
        raise DominioMalDeclarado(
            f"{dominio.nombre}: el sensor y la referencia no coinciden — una de las dos miente:\n  "
            + "\n  ".join(desacuerdos))

    flojas = [mid for mid, vistos in _polaridades(medidas, escenarios).items() if len(vistos) < 2]
    if flojas:
        raise DominioMalDeclarado(
            f"{dominio.nombre}: sin las dos polaridades no quedan fijadas {flojas} — "
            "hay que declarar un defecto que las active")

    configuracion = _configuracion(dominio)
    return {"esquema": ESQUEMA_DIFERENCIAL,
            "origen": dominio.descripcion or f"dominio «{dominio.nombre}» vs su referencia",
            "dominio": dominio.nombre,
            # Las medidas van DECLARADAS en el fixture y no se deducen del prefijo del id: un dominio
            # puede usar medidas compartidas cuyo nombre no comparte su prefijo.
            "medidas": [m.id for m in medidas],
            "mundos": len(escenarios),
            "frescura": crear_frescura(procedencia, medidas, configuracion),
            "escenarios": escenarios}
