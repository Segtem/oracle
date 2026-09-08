"""Captura la corrida de un sensor del consumidor y la vuelve a revisar después.

    python tools/observar.py capturar  --plan <plan.json> --destino <carpeta>
    python tools/observar.py revalidar --plan <plan.json> --registro <registro.json>

Oracle no tiene sensores y no va a tenerlos: un sensor vive en el consumidor, que es el único que
sabe leer su dominio. Lo que sí faltaba —y es lo que hace este archivo— es el **recorrido alrededor
de una corrida**: ejecutarla, conservar su salida íntegra, negarse a llamar observación a una
lectura vacía o inestable, comparar la expectativa DECLARADA contra el resultado, y dejar un
registro que después se pueda volver a revisar sin reescribir el pasado.

## Tres cosas distintas que acá no se confunden

- **observación histórica** — lo que una corrida devolvió, con fecha. Ya ocurrió y no vuelve a
  ocurrir; `revalidar` la lee, nunca la corrige.
- **frescura** — si los referentes que se declararon leídos conservan HOY la misma huella. Es una
  comparación de declaraciones, y la hace una medida del lenguaje, no un `if` de acá.
- **autenticidad** — si esa corrida ocurrió de verdad. **No se comprueba acá, y ninguna huella la
  comprueba**: dos declaraciones falsas iguales pasan la frescura igual que dos verdaderas. Por eso
  cada registro lleva `autenticidad.comprobada: false` escrito, en vez de un campo que insinúe lo
  contrario.

## Por qué el plan es relativo, y por qué la expectativa se declara antes

Una observación con las rutas de una máquina adentro no es reutilizable: es un souvenir. Todo lo
que el plan declara es relativo a su raíz, y una ruta absoluta se rechaza al leerlo.

Y la expectativa —qué etiqueta le corresponde al caso, y si se quiere, qué valor debe dar la
medida— se escribe en el plan ANTES de correr. Si se dedujera del veredicto, el caso diría siempre
lo que salió y nunca podría discrepar: el corpus quedaría lleno de casos que no pueden fallar.
Acá una discrepancia detiene la captura y no escribe nada; una corrida distinta se revisa a mano.

## El plan

```json
{
  "esquema": "oracle.observacion/v1",
  "raiz": "../..",
  "sensor": ["{python}", "-B", "tools/mide_lo_que_sea.py", "--salida", "{salida}"],
  "referentes": ["tools/mide_lo_que_sea.py", "docs/inventario.json"],
  "presencia": [{"relacion": "clip", "campos": ["fbx"]}],
  "exige_filas": ["clip"],
  "medida": "medidas/catalogos/dominio/dominio.lo_que_falta.json",
  "espera": {"valor": 12},
  "caso": {
    "id": "017-lo-que-falto-en-la-corrida",
    "titulo": "…", "etiqueta": "falso_verde", "como_se_detecto": "observacion",
    "sintoma": "…", "leccion": "…"
  }
}
```

`{salida}` aparece exactamente una vez y es por donde el sensor recibe dónde escribir; `{python}`
es opcional y evita clavar un intérprete. `presencia` deriva un referente del propio resultado
—rutas y `es_archivo`, **no** los bytes de esos archivos— para que el estado del mundo entre a la
comparación de frescura y no sólo el código que lo leyó, y su relación queda exigida no vacía:
derivar presencia de cero filas produce una huella de `[]` que sale «estable» sin haber mirado una
sola ruta. `espera.valor` es opcional a propósito: el número que dio una corrida es de esa corrida,
no un contrato del recorrido.

La medida entra como referente aunque el plan no la declare, y su huella es la de la lectura con la
que se cargó: quien dicta el veredicto no puede cambiar entre que se evalúa y que se registra.

## Lo que NO es una observación

`SIN EVIDENCIA` no es un rojo. Cuando una medida declara `requiere` una relación y esa relación
viene vacía, el núcleo devuelve `sin_evidencia` en vez de un veredicto: dice «no hay con qué
mirar», no «el mundo está mal». Un caso observado no se construye sobre eso, y por eso `capturar`
se planta. `exige_filas` no alcanzaba: mira las relaciones que el PLAN eligió, y la medida puede
requerir otra.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.algebra import ErrorDeAlgebra, separar_clave  # noqa: E402
from nucleo.caso import DETECCIONES, ETIQUETAS, opciones  # noqa: E402
from nucleo import caso as caso_sintaxis  # noqa: E402
from nucleo.marco import hechos_de_casos  # noqa: E402
from nucleo.medida import Veredicto, cargar  # noqa: E402
from nucleo.referente import Referente, ReferenteMalDeclarado, hechos_de_frescura  # noqa: E402
from nucleo.version import VERSION_DISTRIBUCION  # noqa: E402
from tools.corpus import revisar_evidencia  # noqa: E402

ESQUEMA_PLAN = "oracle.observacion/v1"
ESQUEMA_REGISTRO = "oracle.observacion.registro/v1"
ESQUEMA_REVALIDACION = "oracle.observacion.revalidacion/v1"
MARCA_SALIDA = "{salida}"
MARCA_PYTHON = "{python}"
MEDIDA_FRESCURA = "meta.ninguna_evidencia_se_juzga_con_referente_vencido"
MEDIDA_POLARIDAD = "meta.el_caso_se_pone_como_debe"
NOMBRE_EVIDENCIA = "evidencia.json"
NOMBRE_REGISTRO = "registro.json"

LIMITE_AUTENTICIDAD = (
    "las huellas comparan una declaración contra una relectura; dos declaraciones falsas iguales "
    "pasan igual que dos verdaderas. Nada de lo que hay acá prueba que el sensor haya corrido, ni "
    "que una huella corresponda a lo que se leyó. Que este registro exista es una afirmación sobre "
    "el pasado, y Oracle no puede verificarla")

LIMITE_OBSERVACION = (
    "una observación dice qué devolvió el sensor en ese momento, sobre lo que el sensor mira. No "
    "dice que el dominio esté bien, ni que siga igual, ni nada sobre lo que el sensor no leyó")


class ObservacionInvalida(ValueError):
    """No hay observación que conservar. Ninguna de estas se arregla insistiendo."""


class PlanInvalido(ObservacionInvalida):
    pass


class SensorFallido(ObservacionInvalida):
    pass


class LecturaVacia(ObservacionInvalida):
    pass


class LecturaInestable(ObservacionInvalida):
    pass


class ReferenteVencido(ObservacionInvalida):
    pass


class Discordancia(ObservacionInvalida):
    pass


class DestinoOcupado(ObservacionInvalida):
    pass


def huella(datos: bytes) -> str:
    return "sha256:" + hashlib.sha256(datos).hexdigest()


def _canonico(valor) -> bytes:
    return json.dumps(valor, sort_keys=True, ensure_ascii=False).encode("utf-8")


def instante() -> str:
    return datetime.now(timezone.utc).isoformat()


def _relativa(valor, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise PlanInvalido(f"`{campo}` tiene que ser una ruta no vacía")
    if valor.startswith("~"):
        raise PlanInvalido(
            f"`{campo}` empieza con «~»: una observación se declara relativa a su raíz, no al "
            f"hogar de una máquina — «{valor}»")
    if PurePosixPath(valor).is_absolute():
        raise PlanInvalido(
            f"`{campo}` es una ruta absoluta y no se puede reusar en otra máquina: «{valor}»")
    return valor


def _lista_de_rutas(datos: dict, campo: str, *, minimo: int) -> tuple[str, ...]:
    valor = datos.get(campo, [])
    if not isinstance(valor, list):
        raise PlanInvalido(f"`{campo}` tiene que ser una lista de rutas relativas")
    if len(valor) < minimo:
        raise PlanInvalido(f"`{campo}` necesita al menos {minimo} ruta(s) declarada(s)")
    rutas = tuple(_relativa(v, f"{campo}[{i}]") for i, v in enumerate(valor))
    if len(set(rutas)) != len(rutas):
        raise PlanInvalido(f"`{campo}` repite una ruta; cada referente se declara una vez")
    return rutas


def _nombres(datos: dict, campo: str, *, minimo: int) -> tuple[str, ...]:
    valor = datos.get(campo, [])
    if not isinstance(valor, list):
        raise PlanInvalido(f"`{campo}` tiene que ser una lista de nombres de relación")
    if len(valor) < minimo:
        raise PlanInvalido(f"`{campo}` necesita al menos {minimo} relación declarada")
    for i, nombre in enumerate(valor):
        if not isinstance(nombre, str) or not nombre.strip():
            raise PlanInvalido(f"`{campo}[{i}]` tiene que ser el nombre de una relación")
    if len(set(valor)) != len(valor):
        raise PlanInvalido(f"`{campo}` repite una relación")
    return tuple(valor)


def _presencia(datos: dict) -> tuple[dict, ...]:
    valor = datos.get("presencia", [])
    if not isinstance(valor, list):
        raise PlanInvalido("`presencia` tiene que ser una lista de {relacion, campos}")
    salida = []
    for i, entrada in enumerate(valor):
        if not isinstance(entrada, dict):
            raise PlanInvalido(f"`presencia[{i}]` tiene que ser un objeto {{relacion, campos}}")
        relacion = entrada.get("relacion")
        if not isinstance(relacion, str) or not relacion.strip():
            raise PlanInvalido(f"`presencia[{i}].relacion` tiene que ser el nombre de una relación")
        campos = _nombres(entrada, "campos", minimo=1)
        salida.append({"relacion": relacion, "campos": campos})
    nombres = [e["relacion"] for e in salida]
    if len(set(nombres)) != len(nombres):
        raise PlanInvalido("`presencia` declara dos veces la misma relación")
    return tuple(salida)


def _sensor(datos: dict) -> tuple[str, ...]:
    valor = datos.get("sensor", [])
    if not isinstance(valor, list) or not valor:
        raise PlanInvalido("`sensor` tiene que ser la lista de argumentos del comando a ejecutar")
    for i, trozo in enumerate(valor):
        if not isinstance(trozo, str) or not trozo:
            raise PlanInvalido(f"`sensor[{i}]` tiene que ser texto no vacío")
    marcas = sum(trozo.count(MARCA_SALIDA) for trozo in valor)
    if marcas != 1:
        raise PlanInvalido(
            f"`sensor` tiene que traer «{MARCA_SALIDA}» exactamente una vez —es por donde el "
            f"recorrido le dice al sensor dónde escribir— y trae {marcas}")
    return tuple(valor)


def _valor_esperado(datos: dict):
    espera = datos.get("espera", {})
    if not isinstance(espera, dict):
        raise PlanInvalido("`espera` tiene que ser un objeto; hoy sólo admite `valor`")
    sobran = sorted(set(espera) - {"valor"})
    if sobran:
        raise PlanInvalido(
            f"`espera` sólo admite `valor`; la polaridad la declara `caso.etiqueta`. Sobra: {sobran}")
    if "valor" not in espera:
        return None
    valor = espera["valor"]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise PlanInvalido("`espera.valor` tiene que ser un número")
    return valor


def _caso_declarado(datos: dict) -> dict:
    caso = datos.get("caso")
    if not isinstance(caso, dict):
        raise PlanInvalido("`caso` tiene que ser el objeto con la prosa del caso a emitir")
    for campo in ("id", "titulo", "sintoma", "leccion"):
        valor = caso.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            raise PlanInvalido(f"`caso.{campo}` tiene que ser texto no vacío")
    etiqueta = caso.get("etiqueta")
    if etiqueta not in ETIQUETAS:
        raise PlanInvalido(
            f"`caso.etiqueta` es «{etiqueta}» y tiene que ser una etiqueta declarada. La etiqueta "
            f"se decide antes de correr, no se deduce del resultado.\n{opciones(ETIQUETAS)}")
    deteccion = caso.get("como_se_detecto")
    if deteccion not in DETECCIONES:
        raise PlanInvalido(
            f"`caso.como_se_detecto` es «{deteccion}» y tiene que ser uno declarado.\n"
            f"{opciones(DETECCIONES)}")
    origen = caso.get("origen", {})
    if not isinstance(origen, dict):
        raise PlanInvalido("`caso.origen` tiene que ser un objeto de campos extra para el origen")
    if not all(isinstance(v, (str, int, float, bool)) for v in origen.values()):
        raise PlanInvalido("`caso.origen` sólo admite campos escalares")
    return caso


@dataclass(frozen=True)
class Plan:
    archivo: Path
    raiz: Path
    sensor: tuple[str, ...]
    referentes: tuple[str, ...]
    presencia: tuple[dict, ...]
    exige_filas: tuple[str, ...]
    medida: str
    valor_esperado: float | None
    caso: dict
    crudo: bytes


def leer_plan(ruta) -> Plan:
    ruta = Path(ruta).resolve()
    try:
        crudo = ruta.read_bytes()
    except OSError as e:
        raise PlanInvalido(f"no se pudo leer el plan {ruta}: {e}") from e
    try:
        datos = json.loads(crudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise PlanInvalido(f"el plan {ruta.name} no es JSON legible: {e}") from e
    if not isinstance(datos, dict):
        raise PlanInvalido(f"el plan {ruta.name} tiene que ser un objeto JSON")
    if datos.get("esquema") != ESQUEMA_PLAN:
        raise PlanInvalido(
            f"el plan declara el esquema «{datos.get('esquema')}» y este recorrido lee "
            f"«{ESQUEMA_PLAN}»")
    raiz_declarada = datos.get("raiz", ".")
    raiz = (ruta.parent / _relativa(raiz_declarada, "raiz")).resolve()
    if not raiz.is_dir():
        raise PlanInvalido(f"`raiz` no es un directorio: {raiz}")
    return Plan(
        archivo=ruta,
        raiz=raiz,
        sensor=_sensor(datos),
        referentes=_lista_de_rutas(datos, "referentes", minimo=1),
        presencia=_presencia(datos),
        exige_filas=_nombres(datos, "exige_filas", minimo=1),
        medida=_relativa(datos.get("medida"), "medida"),
        valor_esperado=_valor_esperado(datos),
        caso=_caso_declarado(datos),
        crudo=crudo,
    )


def medida_meta(mid: str):
    return cargar(RAIZ / "catalogos" / "meta" / f"{mid}.oracle")


def comando(plan: Plan, salida: Path) -> list[str]:
    return [sys.executable if trozo == MARCA_PYTHON else trozo.replace(MARCA_SALIDA, str(salida))
            for trozo in plan.sensor]


def correr_sensor(plan: Plan, salida: Path) -> tuple[list[str], str, bytes]:
    """Ejecuta el sensor del consumidor como otro proceso: acá no se importa su código."""
    argv = comando(plan, salida)
    entorno = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        proceso = subprocess.run(argv, cwd=plan.raiz, env=entorno,
                                 capture_output=True, text=True)
    except OSError as e:
        raise SensorFallido(f"no se pudo ejecutar el sensor {argv[0]!r}: {e}") from e
    if proceso.returncode != 0:
        detalle = (proceso.stderr or proceso.stdout).strip()
        raise SensorFallido(
            f"el sensor salió {proceso.returncode} y una corrida fallida no es una observación: "
            f"{detalle[-400:]}")
    if not salida.is_file():
        raise SensorFallido(
            f"el sensor salió 0 y no escribió evidencia en {salida.name}; un éxito sin salida no "
            f"es una lectura")
    return argv, proceso.stdout, salida.read_bytes()


def evidencia_de(crudo: bytes) -> dict:
    try:
        datos = json.loads(crudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise SensorFallido(f"la evidencia emitida no es JSON legible: {e}") from e
    if not isinstance(datos, dict):
        raise SensorFallido("la evidencia tiene que ser un mapa de relación → filas")
    fallas = revisar_evidencia("evidencia", datos)
    if fallas:
        raise SensorFallido("la evidencia emitida no cumple L0: " + "; ".join(fallas[:3]))
    return datos


def filas_de(evidencia: dict, relacion: str) -> list[dict]:
    if relacion not in evidencia:
        raise LecturaVacia(
            f"la relación «{relacion}» que el plan declara no está en la evidencia emitida; "
            f"vinieron {sorted(evidencia)}")
    try:
        _clave, filas = separar_clave(evidencia[relacion])
    except ErrorDeAlgebra as e:
        raise SensorFallido(f"la relación «{relacion}» declara mal su clave: {e}") from e
    return filas


def relaciones_exigidas(plan: Plan) -> tuple[str, ...]:
    """Las que el plan nombró, MÁS las que `presencia` recorre.

    Una `presencia` sobre una relación vacía no recorre ninguna fila y aun así emite su referente:
    la huella del canónico de `[]`. Dos lecturas que no miraron una sola ruta salen «estables», y
    el registro deja escrito que el estado del mundo no cambió sin haberlo consultado nunca. Si el
    plan dice que de esa relación salen rutas, esa relación tiene que traer filas.
    """
    return tuple(dict.fromkeys([*plan.exige_filas, *(e["relacion"] for e in plan.presencia)]))


def comprobar_no_vacia(plan: Plan, evidencia: dict) -> dict[str, int]:
    """Una lectura vacía se pone verde sola: no es una observación, es la falta de una."""
    conteo = {}
    for relacion in relaciones_exigidas(plan):
        filas = filas_de(evidencia, relacion)
        if not filas:
            raise LecturaVacia(
                f"la relación «{relacion}» vino sin filas: una lectura vacía no es una "
                f"observación, y sobre cero filas cualquier medida de ausencia da verde")
        conteo[relacion] = len(filas)
    return conteo


def referente_de_medida(plan: Plan, cuando: str) -> Referente:
    """La medida es un referente aunque el plan no la declare: es quien dicta el veredicto.

    Sin esto, un sensor que reescriba su propia medida entre que se carga y que se registra deja un
    registro cuya huella identifica una medida DISTINTA de la que produjo el número. Se leyó una y
    se guardó el nombre de otra, y nada lo notaba.
    """
    ruta = plan.raiz / plan.medida
    try:
        return Referente(plan.medida, huella(ruta.read_bytes()), cuando)
    except OSError as e:
        raise ReferenteVencido(f"no se pudo leer la medida «{plan.medida}»: {e}") from e


def leer_referentes(plan: Plan, evidencia: dict, cuando: str,
                    *, medida: Referente | None = None) -> list[Referente]:
    """Las fuentes declaradas, la medida, y el estado del mundo que el propio resultado nombra.

    `medida` permite pasar la lectura hecha al CARGARLA, que es anterior a la corrida del sensor:
    así la comparación de frescura cubre también la ventana entre que se cargó y que se evaluó.
    """
    salida = [medida if medida is not None else referente_de_medida(plan, cuando)]
    for relativa in plan.referentes:
        if relativa == plan.medida:
            # Ya entró arriba, y con la lectura que corresponde. Declararla en `referentes` sigue
            # siendo válido —los planes viejos lo hacen— pero no la duplica.
            continue
        ruta = plan.raiz / relativa
        try:
            crudo = ruta.read_bytes()
        except OSError as e:
            raise ReferenteVencido(f"no se pudo leer el referente «{relativa}»: {e}") from e
        salida.append(Referente(relativa, huella(crudo), cuando))
    for entrada in plan.presencia:
        relacion, campos = entrada["relacion"], entrada["campos"]
        vistos = []
        for i, fila in enumerate(filas_de(evidencia, relacion)):
            for campo in campos:
                if campo not in fila:
                    raise SensorFallido(
                        f"«{relacion}»[{i}] no trae el campo «{campo}» que el plan declara como "
                        f"ruta; un campo ausente daría «no está» sin haber mirado")
                ruta = str(fila[campo])
                # Contra la raíz del plan, no contra el directorio desde el que se invocó esto: una
                # ruta relativa resuelta contra un cwd cualquiera da «no está» sin haber mirado.
                vistos.append({"ruta": ruta, "es_archivo": (plan.raiz / ruta).is_file()})
        salida.append(Referente(f"presencia:{relacion}:{'+'.join(campos)}",
                                huella(_canonico(vistos)), cuando))
    return salida


def juzgar(medida, evidencia: dict) -> Veredicto:
    """Un error del álgebra acá dice que la evidencia no le sirve a la medida, no que el mundo esté
    mal. Se distingue, porque un rojo y un «no hay con qué mirar» no son lo mismo."""
    try:
        return medida.evaluar(evidencia)
    except ErrorDeAlgebra as e:
        raise SensorFallido(
            f"la medida «{medida.id}» no pudo juzgar la evidencia emitida: {e}") from e


def exigir_que_se_haya_medido(veredicto: Veredicto) -> None:
    """`SIN EVIDENCIA` no es un rojo, y un caso observado no puede nacer de uno.

    El núcleo separa las dos cosas a propósito —`Veredicto.sin_evidencia` existe para eso— y dice
    por qué: «un rojo dice "el mundo está mal", y esto dice "no hay con qué mirar". `ok` sigue en
    False porque lo único inaceptable es que salga verde». Mirar sólo `.ok` colapsa esa distinción,
    y el caso que sale afirma que se observó un defecto donde no se observó nada. Lo encontró una
    revisión de falsación el 2026-09-07: `exige_filas` mira las relaciones que el PLAN eligió y la
    medida puede requerir otra.
    """
    if veredicto.sin_evidencia:
        raise LecturaVacia(
            f"la medida «{veredicto.id}» declara que necesita la relación "
            f"«{veredicto.sin_evidencia}» y vino vacía: salió SIN EVIDENCIA, que no es un rojo "
            f"sino «no hay con qué mirar». Una observación no se construye sobre una medida que "
            f"no llegó a medir")


def comparar_frescura(leidos, actuales) -> tuple[dict, Veredicto]:
    hechos = hechos_de_frescura(leidos, actuales)
    return hechos, medida_meta(MEDIDA_FRESCURA).evaluar(hechos)


def armar_caso(plan: Plan, evidencia: dict, mid: str, origen: dict) -> dict:
    """La prosa y la etiqueta vienen del plan; la evidencia entra íntegra, sin transcribir."""
    declarado = plan.caso
    return {
        "id": declarado["id"],
        "fecha": origen["cuando_utc"][:10],
        "origen": {**declarado.get("origen", {}), **origen},
        "procedencia": "observada",
        "titulo": declarado["titulo"],
        "etiqueta": declarado["etiqueta"],
        "sintoma": declarado["sintoma"],
        "como_se_detecto": declarado["como_se_detecto"],
        "medida": mid,
        "evidencia": evidencia,
        "leccion": declarado["leccion"],
    }


def concuerda_con_la_etiqueta(caso: dict, medida) -> Veredicto:
    """La polaridad la dictamina la medida del marco, no una copia de su regla acá."""
    return medida_meta(MEDIDA_POLARIDAD).evaluar(hechos_de_casos({medida.id: medida}, [caso]))


def _git(raiz: Path, *args: str) -> str:
    try:
        salida = subprocess.run(["git", "-C", str(raiz), *args],
                                capture_output=True, text=True)
    except OSError:
        return ""
    return salida.stdout if salida.returncode == 0 else ""


def estado_del_arbol(raiz: Path) -> dict:
    commit = _git(raiz, "rev-parse", "HEAD").strip()
    if not commit:
        return {"versionado": False,
                "porque": "la raíz no está en un repositorio git legible, o no tiene commits"}
    estado = _git(raiz, "status", "--short")
    return {"versionado": True, "commit": commit, "sucio": bool(estado.strip()),
            "estado": estado}


def _relativo_a(ruta: Path, raiz: Path) -> str:
    return os.path.relpath(ruta, raiz).replace(os.sep, "/")


def capturar(plan: Plan, destino: Path, trabajo: Path) -> dict:
    """Corre dos veces, exige que las dos digan lo mismo y conserva la segunda tal cual salió."""
    destino = Path(destino)
    ocupados = [n for n in (NOMBRE_EVIDENCIA, NOMBRE_REGISTRO) if (destino / n).exists()]
    if ocupados:
        raise DestinoOcupado(
            f"{destino} ya conserva una observación ({', '.join(ocupados)}); una observación no se "
            f"pisa con otra, se guarda al lado")

    # La huella se toma de la MISMA lectura con la que se carga, y antes de que el sensor corra:
    # el registro tiene que identificar la medida que produjo el número, no la que quedó después.
    medida_al_cargar = referente_de_medida(plan, instante())
    medida = cargar(plan.raiz / plan.medida)

    primera = evidencia_de(correr_sensor(plan, trabajo / "descubrimiento.json")[2])
    comprobar_no_vacia(plan, primera)
    antes = leer_referentes(plan, primera, instante(), medida=medida_al_cargar)

    inicio = instante()
    argv, texto, crudo = correr_sensor(plan, trabajo / NOMBRE_EVIDENCIA)
    fin = instante()
    evidencia = evidencia_de(crudo)
    conteo = comprobar_no_vacia(plan, evidencia)
    despues = leer_referentes(plan, evidencia, fin)

    # En FORMA CANÓNICA, no con `==` sobre lo parseado. En Python `True == 1` y `1 == 1.0`, así que
    # un sensor que emite `true` en una corrida y `1` en la otra pasaba el control: los bytes eran
    # distintos, el tipo era distinto, y la comparación decía que no había cambiado nada. Se
    # conservaba la segunda lectura como observación de un sensor que no se puede repetir.
    # Tampoco se comparan los bytes: reordenar las claves de un objeto no es un cambio del mundo, y
    # las dos corridas escriben en rutas distintas, que un sensor podría incluir en su salida.
    if _canonico(primera) != _canonico(evidencia):
        raise LecturaInestable(
            "dos lecturas seguidas del mismo sensor dieron evidencias distintas —comparadas por "
            "valor y tipo, no por bytes—; una observación que no se puede repetir en el acto no "
            "fija nada")
    comparacion, v_frescura = comparar_frescura(antes, despues)
    if not v_frescura.ok:
        cambiados = sorted({fila["r"]["que"] for fila in v_frescura.testigos})
        raise ReferenteVencido(
            f"cambió un referente mientras corría el sensor: {cambiados}; lo que se leyó al "
            f"empezar ya no es lo que hay")

    veredicto = juzgar(medida, evidencia)
    exigir_que_se_haya_medido(veredicto)
    if plan.valor_esperado is not None and veredicto.valor != plan.valor_esperado:
        raise Discordancia(
            f"el plan espera valor {plan.valor_esperado} y la corrida dio {veredicto.valor}; una "
            f"corrida distinta se revisa, no se fuerza para que encaje en el caso")

    origen = {
        "cuando_utc": inicio,
        "comando": " ".join(plan.sensor),
        "registro": _relativo_a(destino / NOMBRE_REGISTRO, plan.raiz),
        "evidencia_sha256": huella(crudo),
        "estado": "árbol de trabajo; las fuentes QUE EL PLAN DECLARA están identificadas por SHA-256 en el registro, y el plan puede no declararlas todas",
    }
    caso = armar_caso(plan, evidencia, medida.id, origen)
    v_polaridad = concuerda_con_la_etiqueta(caso, medida)
    if not v_polaridad.ok:
        raise Discordancia(
            f"el plan declara la etiqueta «{caso['etiqueta']}» y la corrida dio "
            f"{'verde' if veredicto.ok else 'rojo'} con valor {veredicto.valor}; la etiqueta se "
            f"decidió antes y no se reescribe con el resultado ({MEDIDA_POLARIDAD})")

    registro = {
        "esquema": ESQUEMA_REGISTRO,
        "inicio_utc": inicio,
        "fin_utc": fin,
        "plan": {"archivo": _relativo_a(plan.archivo, plan.raiz), "sha256": huella(plan.crudo)},
        "herramienta": {"archivo": "tools/observar.py",
                        "sha256": huella(Path(__file__).read_bytes()),
                        "distribucion": VERSION_DISTRIBUCION},
        "comando_declarado": list(plan.sensor),
        "salida_estandar": texto,
        "evidencia": {"archivo": NOMBRE_EVIDENCIA, "sha256": huella(crudo),
                      "relaciones": sorted(evidencia), "filas_exigidas": conteo},
        "medida": {"id": medida.id, "archivo": plan.medida,
                   "sha256": medida_al_cargar.huella},
        "expectativa": {"etiqueta": plan.caso["etiqueta"], "valor": plan.valor_esperado,
                        "juzgada_por": MEDIDA_POLARIDAD},
        "resultado": {"ok": veredicto.ok, "valor": veredicto.valor,
                      "testigos": len(veredicto.testigos), "umbral": veredicto.umbral,
                      "sin_evidencia": veredicto.sin_evidencia},
        "caso": {"archivo": f"{caso['id']}.caso", "id": caso["id"]},
        "referentes_al_leer": [r.a_datos() for r in antes],
        "referentes_despues": [r.a_datos() for r in despues],
        "comparacion": comparacion,
        "arbol_git": estado_del_arbol(plan.raiz),
        "maquina": {"raiz": str(plan.raiz), "python": sys.version,
                    "comando_ejecutado": argv,
                    "porque": "dónde ocurrió esta corrida; no es parte del plan ni se usa al revalidar"},
        "autenticidad": {"comprobada": False, "porque": LIMITE_AUTENTICIDAD},
        "alcance": LIMITE_OBSERVACION,
    }

    destino.mkdir(parents=True, exist_ok=True)
    (destino / NOMBRE_EVIDENCIA).write_bytes(crudo)
    (destino / NOMBRE_REGISTRO).write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destino / f"{caso['id']}.caso").write_text(
        _caso_escrito(caso), encoding="utf-8")
    return registro


def _caso_escrito(caso: dict) -> str:
    """El caso en la superficie `.caso`. Un caso capturado se lee después, y lo lee una persona.

    Emitirlo en JSON lo dejaba en el formato del que el proyecto se estaba yendo —los casos se
    escriben en `.caso` desde el 2026-08-25— y hacía que observar barato costara legibilidad.

    SIN reserva a JSON, y se probó a quitarla: la escribí primero y la mutación mostró que ningún
    test la ejercía, porque no se encontró ninguna forma que el impresor rechace. Una reserva que
    nadie puede provocar es un constructo, y además el peor: cambiar de formato en silencio esconde
    que el impresor se rompió. Si algún día pasa, `capturar` falla acá y en voz alta — la evidencia
    y el registro ya están escritos en el disco, así que lo que se pierde es una corrida, no la
    observación.
    """
    return caso_sintaxis.imprimir(caso)


def evidencia_guardada(registro_ruta: Path, registro: dict):
    """La salida que se conservó al lado del registro, parseada; `None` si no se puede leer.

    Se compara contra ELLA y no contra su huella porque la igualdad que cuenta es por valor y tipo.
    Si el archivo no está —alguien movió el registro solo—, queda la huella, que es más estricta y
    lo dice: sin la salida guardada no se puede distinguir un cambio de presentación de uno real.
    """
    nombre = registro.get("evidencia", {}).get("archivo", NOMBRE_EVIDENCIA)
    if not isinstance(nombre, str) or "/" in nombre or nombre in ("", ".", ".."):
        return None
    try:
        return json.loads((Path(registro_ruta).parent / nombre).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def revalidar(plan: Plan, registro_ruta: Path, trabajo: Path) -> dict:
    """Vuelve a leer HOY y compara contra lo registrado. No toca la observación guardada."""
    ruta = Path(registro_ruta)
    try:
        registro = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ObservacionInvalida(f"no se pudo leer el registro {ruta}: {e}") from e
    if not isinstance(registro, dict) or registro.get("esquema") != ESQUEMA_REGISTRO:
        raise ObservacionInvalida(
            f"el registro no declara el esquema «{ESQUEMA_REGISTRO}»; no hay observación que "
            f"revalidar")

    medida_al_cargar = referente_de_medida(plan, instante())
    medida = cargar(plan.raiz / plan.medida)
    _argv, texto, crudo = correr_sensor(plan, trabajo / NOMBRE_EVIDENCIA)
    evidencia = evidencia_de(crudo)
    ahora = instante()
    actuales = leer_referentes(plan, evidencia, ahora, medida=medida_al_cargar)
    veredicto = juzgar(medida, evidencia)

    try:
        historicos = [Referente.de_datos(d) for d in registro.get("referentes_despues", [])]
        comparacion, v_frescura = comparar_frescura(historicos, actuales)
        frescura = {
            "comparable": True,
            "estables": v_frescura.ok,
            "cambiados": sorted({fila["r"]["que"] for fila in v_frescura.testigos}),
            "referente_comparado": comparacion["referente_comparado"],
        }
    except ReferenteMalDeclarado as e:
        frescura = {"comparable": False, "estables": False, "cambiados": [], "porque": str(e)}

    historico = registro.get("resultado", {})
    # El MISMO criterio que usa `capturar`: forma canónica, no bytes. Comparar bytes acá hacía que
    # un sensor que sólo cambió su sangría informara «CAMBIÓ», mientras la captura declara —y con
    # razón— que reordenar claves no es un cambio del mundo. Dos verbos del mismo recorrido no
    # pueden discrepar sobre qué es un cambio. Los bytes se informan aparte, porque conservar la
    # salida íntegra sí importa: si cambiaron, la evidencia guardada ya no se reproduce igual.
    guardada = evidencia_guardada(ruta, registro)
    evidencia_igual = (_canonico(evidencia) == _canonico(guardada) if guardada is not None
                       else huella(crudo) == registro.get("evidencia", {}).get("sha256"))
    medida_igual = medida_al_cargar.huella == registro.get("medida", {}).get("sha256")
    igual = (evidencia_igual
             and medida_igual
             and bool(frescura["estables"])
             and veredicto.ok == historico.get("ok")
             and veredicto.valor == historico.get("valor")
             and veredicto.sin_evidencia == historico.get("sin_evidencia", ""))
    return {
        "esquema": ESQUEMA_REVALIDACION,
        "cuando_utc": ahora,
        "registro": str(ruta),
        "plan_sin_cambios": huella(plan.crudo) == registro.get("plan", {}).get("sha256"),
        "medida": {
            "sin_cambios": medida_igual,
            "sha256_historico": registro.get("medida", {}).get("sha256"),
            "sha256_actual": medida_al_cargar.huella,
            "porque": "quien dicta el veredicto es la medida: si cambió, dos números iguales no "
                      "dicen lo mismo y dos distintos no prueban que cambió el mundo",
        },
        "evidencia": {
            "igual_por_valor": evidencia_igual,
            "mismos_bytes": huella(crudo) == registro.get("evidencia", {}).get("sha256"),
            "porque": "la igualdad que cuenta es por valor y tipo, como en la captura; que cambien "
                      "los bytes sin cambiar el valor es presentación, y se informa aparte",
        },
        "observacion_historica": {
            "inicio_utc": registro.get("inicio_utc"),
            "evidencia_sha256": registro.get("evidencia", {}).get("sha256"),
            "resultado": historico,
            "caso": registro.get("caso", {}),
            "porque": "lo que devolvió aquella corrida; esto no se corrige ni se vuelve a medir",
        },
        "lectura_actual": {
            "evidencia_sha256": huella(crudo),
            "resultado": {"ok": veredicto.ok, "valor": veredicto.valor,
                          "testigos": len(veredicto.testigos), "umbral": veredicto.umbral,
                          "sin_evidencia": veredicto.sin_evidencia},
            "salida_estandar": texto,
        },
        "frescura": frescura,
        "sin_cambios": igual,
        "autenticidad": {"comprobada": False, "porque": LIMITE_AUTENTICIDAD},
        "alcance": LIMITE_OBSERVACION,
    }


def _imprimir_captura(registro: dict, destino: Path) -> None:
    evidencia = registro["evidencia"]
    filas = ", ".join(f"{n}×{r}" for r, n in evidencia["filas_exigidas"].items())
    resultado = registro["resultado"]
    marca = "✓" if resultado["ok"] else "✗"
    print(f"OBSERVACIÓN CAPTURADA — {destino}")
    print(f"  sensor:       {' '.join(registro['comando_declarado'])}")
    print(f"  evidencia:    {evidencia['sha256']}  ({filas})")
    print(f"  {marca} {registro['medida']['id']:<44} {resultado['valor']:>8} "
          f"({resultado['umbral']})")
    print(f"  expectativa:  etiqueta «{registro['expectativa']['etiqueta']}» declarada antes de "
          f"correr, juzgada por {registro['expectativa']['juzgada_por']}")
    print(f"  frescura:     {len(registro['comparacion']['referente_comparado'])} referentes "
          f"estables entre las dos lecturas")
    print(f"  autenticidad: NO comprobada — {LIMITE_AUTENTICIDAD}")


def _imprimir_revalidacion(informe: dict) -> None:
    historica, actual = informe["observacion_historica"], informe["lectura_actual"]
    print(f"REVALIDACIÓN — {'sin cambios' if informe['sin_cambios'] else 'CAMBIÓ'}")
    print(f"  histórica:    {historica['inicio_utc']}  valor {historica['resultado'].get('valor')} "
          f"· {historica['evidencia_sha256']}")
    print(f"  actual:       {informe['cuando_utc']}  valor {actual['resultado']['valor']} "
          f"· {actual['evidencia_sha256']}")
    if informe["frescura"]["comparable"]:
        cambiados = informe["frescura"]["cambiados"]
        print(f"  frescura:     {'estables' if not cambiados else 'cambiaron ' + str(cambiados)}")
    else:
        print(f"  frescura:     no comparable — {informe['frescura']['porque']}")
    if not informe["medida"]["sin_cambios"]:
        print("  medida:       CAMBIÓ desde la captura; dos números iguales ya no dicen lo mismo")
    if not informe["evidencia"]["igual_por_valor"]:
        print("  evidencia:    distinta por valor")
    elif not informe["evidencia"]["mismos_bytes"]:
        print("  evidencia:    misma por valor, otros bytes (presentación, no el mundo)")
    if not informe["plan_sin_cambios"]:
        print("  aviso:        el plan cambió desde la captura; se revalidó con el plan de HOY")
    print(f"  autenticidad: NO comprobada — {LIMITE_AUTENTICIDAD}")
    print(f"  la observación histórica queda como estaba: {informe['registro']}")


def argumentos(argv: list[str]):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    verbos = p.add_subparsers(dest="verbo", required=True)
    capturar_p = verbos.add_parser("capturar", help="correr el sensor y conservar la observación")
    capturar_p.add_argument("--plan", type=Path, required=True)
    capturar_p.add_argument("--destino", type=Path, required=True,
                            help="carpeta donde se conserva evidencia, registro y caso")
    revalidar_p = verbos.add_parser("revalidar", help="volver a leer hoy y comparar con lo guardado")
    revalidar_p.add_argument("--plan", type=Path, required=True)
    revalidar_p.add_argument("--registro", type=Path, required=True)
    revalidar_p.add_argument("--informe", type=Path,
                             help="además de imprimir, guardar el informe JSON en esta ruta")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = argumentos(sys.argv[1:] if argv is None else argv)
    trabajo = Path(tempfile.mkdtemp(prefix="oracle-observar-"))
    try:
        plan = leer_plan(args.plan)
        if args.verbo == "capturar":
            registro = capturar(plan, args.destino, trabajo)
            _imprimir_captura(registro, args.destino)
        else:
            informe = revalidar(plan, args.registro, trabajo)
            if args.informe:
                args.informe.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
            _imprimir_revalidacion(informe)
            if not informe["sin_cambios"]:
                shutil.rmtree(trabajo)
                return 1
    except ObservacionInvalida as e:
        print(f"OBSERVACIÓN RECHAZADA — {e}")
        # La lectura rechazada NO se borra: es lo único que hay para entender por qué se rechazó, y
        # borrarla obliga a repetir una corrida que quizá ya no da lo mismo.
        if any(trabajo.iterdir()):
            print(f"  la lectura rechazada quedó en {trabajo}")
        else:
            shutil.rmtree(trabajo)
        return 1
    shutil.rmtree(trabajo)
    return 0


_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    raise SystemExit(_entrada_directa())
