"""Lector único y fail-closed de fixtures diferenciales versionados.

Los consumidores no deben conocer la forma física del fixture. Este módulo valida las dos formas
de ``oracle.diferencial/v1`` y las proyecta como evidencias o casos asociados a una medida. Así
``medida --relaciones``, la revisión, el diferencial y la mutación leen exactamente el mismo dato.
La frescura usa el mismo camino: reifica las huellas leída y actual como `referente_comparado` y
delega el veredicto a una medida `.oracle`; no conserva un comparador propio.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

from nucleo.algebra import ErrorDeAlgebra, separar_clave, validar_unicidad
from nucleo.diferencial import (ALGORITMO_HUELLA, ESQUEMA_DIFERENCIAL, HUELLA_RE,
                                ProcedenciaInvalida, huella_archivos, huella_catalogo,
                                huella_datos, ids_de_medidas)
from nucleo.proyecto import ID_MEDIDA_RE
from nucleo.referente import Referente, hechos_de_frescura


ESCALARES_L0 = (str, int, float, bool, type(None))
ID_MEDIDA_FRESCURA = "meta.ninguna_evidencia_se_juzga_con_referente_vencido"


@dataclass(frozen=True)
class Fixture:
    ruta: Path
    datos: dict


def id_medida_valido(valor: Any) -> bool:
    """Gramática portable de ids; excluye rutas, espacios y nombres ambiguos."""
    return isinstance(valor, str) and ID_MEDIDA_RE.fullmatch(valor) is not None


def _id_escenario_valido(valor: Any) -> bool:
    return isinstance(valor, str) and bool(valor) and not any(c.isspace() for c in valor)


def _validar_evidencia(evidencia: Any, contexto: str) -> list[str]:
    if not isinstance(evidencia, dict) or not evidencia:
        return [f"{contexto}: `evidencia` debe ser un mapa no vacío de relación → filas"]

    fallas = []
    for relacion, filas in evidencia.items():
        if not isinstance(relacion, str) or not relacion.strip():
            fallas.append(f"{contexto}: nombre de relación inválido: {relacion!r}")
            continue
        if not isinstance(filas, list):
            fallas.append(f"{contexto}: la relación «{relacion}» debe ser una lista de filas")
            continue
        try:
            clave, hechos = separar_clave(filas)
        except ErrorDeAlgebra as e:
            fallas.append(f"{contexto}: {relacion}: {e}")
            continue
        bien_formados = True
        for i, fila in enumerate(hechos):
            if not isinstance(fila, dict):
                bien_formados = False
                fallas.append(f"{contexto}: {relacion}[{i}] no es una fila")
                continue
            for campo, valor in fila.items():
                if not isinstance(campo, str) or not campo:
                    fallas.append(f"{contexto}: {relacion}[{i}] tiene un campo inválido")
                if not isinstance(valor, ESCALARES_L0):
                    fallas.append(
                        f"{contexto}: {relacion}[{i}].{campo} no es escalar "
                        f"({type(valor).__name__})")
        if clave and bien_formados:
            try:
                validar_unicidad(relacion, clave, hechos)
            except ErrorDeAlgebra as e:
                fallas.append(f"{contexto}: {relacion}: {e}")
    return fallas


def _validar_comunes(datos: Any, nombre: str) -> list[str]:
    if not isinstance(datos, dict):
        return [f"{nombre}: la raíz del fixture debe ser un objeto JSON"]

    fallas = []
    if datos.get("esquema") != ESQUEMA_DIFERENCIAL:
        fallas.append(
            f"{nombre}: esquema ausente o desconocido; se requiere {ESQUEMA_DIFERENCIAL!r}")
    if not isinstance(datos.get("origen"), str) or not datos.get("origen", "").strip():
        fallas.append(f"{nombre}: falta `origen` no vacío")
    if type(datos.get("mundos")) is not int or datos.get("mundos") <= 0:
        fallas.append(f"{nombre}: `mundos` debe ser un entero positivo")
    frescura = datos.get("frescura")
    if not isinstance(frescura, dict):
        fallas.append(f"{nombre}: falta `frescura` versionada")
        return fallas
    if frescura.get("algoritmo") != ALGORITMO_HUELLA:
        fallas.append(f"{nombre}: `frescura.algoritmo` debe ser {ALGORITMO_HUELLA!r}")
    if frescura.get("raiz_fuentes") not in (".", ".."):
        fallas.append(f"{nombre}: `frescura.raiz_fuentes` sólo admite '.' o '..'")
    fuentes = frescura.get("fuentes")
    if not isinstance(fuentes, dict):
        fallas.append(f"{nombre}: `frescura.fuentes` debe ser un mapa")
    else:
        for clase in ("emisor", "referencia"):
            rutas = fuentes.get(clase)
            if not isinstance(rutas, list) or not rutas or any(
                    not isinstance(r, str) or not r.strip() or Path(r).is_absolute()
                    or ".." in Path(r).parts for r in (rutas or [])):
                fallas.append(
                    f"{nombre}: `frescura.fuentes.{clase}` requiere rutas relativas válidas")
    if not isinstance(frescura.get("configuracion"), dict):
        fallas.append(f"{nombre}: `frescura.configuracion` debe ser un mapa")
    huellas = frescura.get("huellas")
    requeridas = {"emisor", "referencia", "catalogo", "configuracion"}
    if not isinstance(huellas, dict) or set(huellas) != requeridas:
        fallas.append(f"{nombre}: `frescura.huellas` debe contener {sorted(requeridas)}")
    elif any(not isinstance(h, str) or not HUELLA_RE.fullmatch(h) for h in huellas.values()):
        fallas.append(f"{nombre}: cada huella debe ser SHA-256 hexadecimal")
    return fallas


SIN_EVIDENCIA_EN_FIXTURE = "SIN EVIDENCIA"


def registro_de_veredicto(medida, evidencia) -> dict:
    """Cómo salió una medida en un escenario, en la forma que el fixture guarda.

    Lo escriben el emisor y lo recalcula el verificador, y por eso vive acá y no en cada uno: dos
    copias de esta forma se separan, y el día que se separen el fixture y quien lo revisa van a
    estar comparando cosas distintas sin decirlo.
    """
    try:
        v = medida.evaluar(evidencia)
    except ErrorDeAlgebra:
        # Qué mensaje da el error no entra: dos implementaciones independientes redactan distinto,
        # y exigir la misma frase convertiría la redacción en contrato.
        return {"ok": False, "levanta": True}
    if v.sin_evidencia:
        return {"ok": False, "valor": SIN_EVIDENCIA_EN_FIXTURE}
    return {"ok": bool(v.ok), "valor": valor_comparable(v.valor)}


def valor_comparable(valor):
    """Un entero escrito `3.0` y escrito `3` es el mismo número; guardar uno u otro según qué
    implementación lo produjo convertiría en desacuerdo algo que no lo es."""
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    return valor


def ok_guardado(registro) -> bool | None:
    """El `ok` de un veredicto guardado, venga en la forma corta (un booleano) o en la larga."""
    if type(registro) is bool:
        return registro
    if isinstance(registro, dict) and type(registro.get("ok")) is bool:
        return registro["ok"]
    return None


def mismo_veredicto(guardado, ahora: dict) -> bool:
    """Compara lo guardado contra lo que sale hoy, sin exigirle a un fixture viejo lo que no trae.

    Un fixture de la forma corta sólo afirmó el `ok`; reclamarle el valor sería inventar una
    afirmación que nadie hizo.
    """
    if type(guardado) is bool:
        return guardado == ahora["ok"]
    if not isinstance(guardado, dict):
        return False
    return all(guardado.get(campo) == ahora.get(campo)
               for campo in ("ok", "valor", "levanta"))


def _veredicto_guardado(valor: Any, contexto: str) -> tuple[bool | None, list[str]]:
    """El veredicto de una medida en un escenario: un booleano, o el registro que además dice con
    qué valor salió y si la evaluación levantó.

    Las dos formas conviven a propósito. La corta es la que emitieron todos los fixtures hasta
    0.23.0 —y la que siguen emitiendo los consumidores—; exigir la larga los invalidaría a todos de
    golpe, que es un rojo sin remedio del lado de quien actualiza. La larga es la que distingue un
    rojo de un SIN EVIDENCIA y de un error, que en un booleano se ven iguales.
    """
    if type(valor) is bool:
        return valor, []
    if not isinstance(valor, dict):
        return None, [f"{contexto}: un veredicto es un booleano o un mapa con `ok`"]
    fallas = []
    ok = valor.get("ok")
    if type(ok) is not bool:
        fallas.append(f"{contexto}: `ok` debe ser booleano")
        ok = None
    levanta = valor.get("levanta", False)
    if type(levanta) is not bool:
        # Se vuelve con lo que hay: sin un `levanta` legible, las coherencias que dependen de él
        # —que no esté en verde, que no traiga valor— no se pueden juzgar, y elegirle un valor sería
        # juzgarlas contra algo que el fixture no dijo.
        return ok, [*fallas, f"{contexto}: `levanta` debe ser booleano"]
    sobrantes = set(valor) - {"ok", "valor", "levanta"}
    if sobrantes:
        fallas.append(f"{contexto}: campos desconocidos {sorted(sobrantes)}")
    if levanta:
        # Una evaluación que levantó no tiene valor ni puede estar en verde: si lo tuviera, el
        # fixture estaría afirmando dos cosas incompatibles y nadie las compararía nunca.
        if ok:
            fallas.append(f"{contexto}: `levanta` con `ok` en verdadero")
        if "valor" in valor:
            fallas.append(f"{contexto}: `levanta` no lleva `valor`")
    elif "valor" in valor:
        v = valor["valor"]
        if not (isinstance(v, (int, float)) and type(v) is not bool
                or v == SIN_EVIDENCIA_EN_FIXTURE):
            fallas.append(
                f"{contexto}: `valor` debe ser un número o {SIN_EVIDENCIA_EN_FIXTURE!r}")
        elif v == SIN_EVIDENCIA_EN_FIXTURE and ok:
            fallas.append(f"{contexto}: SIN EVIDENCIA nunca sale en verde")
    return ok, fallas


def _validar_medidas_declaradas(datos: dict, medidas: Any, nombre: str) -> list[str]:
    """Las medidas que el fixture trae escritas, porque no están en ningún catálogo.

    Sin esto, un fixture sólo puede contrastar medidas publicadas, y hay formas del álgebra que
    ninguna medida del catálogo usa: quedarían sin contraste hasta que alguien escriba una medida
    real que las use, que es esperar por la razón equivocada.
    """
    declaradas = datos.get("medidas_declaradas")
    if declaradas is None:
        return []
    if not isinstance(declaradas, dict) or not declaradas:
        return [f"{nombre}: `medidas_declaradas` debe ser un mapa no vacío"]
    fallas = []
    for mid, canonica in declaradas.items():
        if isinstance(medidas, list) and mid not in medidas:
            fallas.append(f"{nombre}: `medidas_declaradas` trae «{mid}», que no está en `medidas`")
        if (not isinstance(canonica, list) or len(canonica) < 6 or canonica[0] != "medida"
                or canonica[1] != mid):
            fallas.append(
                f"{nombre}: `medidas_declaradas[{mid}]` debe ser la forma canónica de esa medida")
    return fallas


def _validar_dominio(datos: dict, nombre: str) -> list[str]:
    fallas = []
    medidas, escenarios = datos.get("medidas"), datos.get("escenarios")
    if not isinstance(medidas, list) or not medidas:
        fallas.append(f"{nombre}: el formato Dominio requiere `medidas` no vacías")
    elif any(not id_medida_valido(m) for m in medidas) or len(set(medidas)) != len(medidas):
        fallas.append(f"{nombre}: `medidas` debe contener ids válidos y únicos")

    if not isinstance(escenarios, list) or not escenarios:
        fallas.append(f"{nombre}: el formato Dominio requiere `escenarios` no vacíos")
        return fallas
    fallas += _validar_medidas_declaradas(datos, medidas, nombre)
    if type(datos.get("mundos")) is int and datos["mundos"] != len(escenarios):
        fallas.append(
            f"{nombre}: `mundos` dice {datos['mundos']} pero hay {len(escenarios)} escenarios")

    ids, polaridades = set(), set()
    individuales = {mid: set() for mid in medidas} if isinstance(medidas, list) else {}
    for i, escenario in enumerate(escenarios):
        contexto = f"{nombre}: escenario[{i}]"
        if not isinstance(escenario, dict):
            fallas.append(f"{contexto} debe ser un objeto")
            continue
        eid = escenario.get("id")
        if not _id_escenario_valido(eid):
            fallas.append(f"{contexto}: `id` debe ser un texto no vacío y sin espacios")
        elif eid in ids:
            fallas.append(f"{contexto}: id duplicado «{eid}»")
        else:
            ids.add(eid)
        if type(escenario.get("referencia_ok")) is not bool:
            fallas.append(f"{contexto}: `referencia_ok` debe ser booleano")
        else:
            polaridades.add(escenario["referencia_ok"])
        guardado = escenario.get("oracle_al_generar")
        if not isinstance(guardado, dict):
            fallas.append(f"{contexto}: falta `oracle_al_generar`")
        else:
            global_ok, por_medida = guardado.get("global_ok"), guardado.get("por_medida")
            if type(global_ok) is not bool:
                fallas.append(f"{contexto}: `oracle_al_generar.global_ok` debe ser booleano")
            if not isinstance(por_medida, dict) or set(por_medida) != set(medidas or []):
                fallas.append(
                    f"{contexto}: `oracle_al_generar.por_medida` debe cubrir exactamente `medidas`")
            else:
                oks = {}
                for mid, guardado_medida in por_medida.items():
                    ok, suyas = _veredicto_guardado(guardado_medida, f"{contexto}: {mid}")
                    fallas += suyas
                    if ok is not None:
                        oks[mid] = ok
                        if mid in individuales:
                            individuales[mid].add(ok)
                completos = len(oks) == len(por_medida)
                if completos and type(global_ok) is bool and global_ok != all(oks.values()):
                    fallas.append(f"{contexto}: `global_ok` no es el AND de `por_medida`")
                if (completos and type(global_ok) is bool
                        and type(escenario.get("referencia_ok")) is bool
                        and global_ok != escenario["referencia_ok"]):
                    fallas.append(f"{contexto}: Oracle y la referencia ya discrepaban al generar")
        fallas += _validar_evidencia(escenario.get("evidencia"), contexto)
    if polaridades != {False, True}:
        fallas.append(f"{nombre}: los escenarios deben contener ambas polaridades globales")
    flojas = [mid for mid, vistos in individuales.items() if vistos != {False, True}]
    if flojas:
        fallas.append(f"{nombre}: faltan ambas polaridades individuales para {flojas}")
    return fallas


def _validar_grupos(datos: dict, nombre: str) -> list[str]:
    grupos = datos.get("grupos")
    if not isinstance(grupos, dict) or not grupos:
        return [f"{nombre}: el formato `grupos` requiere grupos no vacíos"]
    fallas, mundos = [], datos.get("mundos")
    for mid, casos in grupos.items():
        contexto = f"{nombre}: grupo {mid!r}"
        if not id_medida_valido(mid):
            fallas.append(f"{nombre}: id de medida de grupo inválido: {mid!r}")
        if not isinstance(casos, list) or not casos:
            fallas.append(f"{contexto} requiere casos no vacíos")
            continue
        if type(mundos) is int and mundos != len(casos):
            fallas.append(f"{contexto}: `mundos` dice {mundos} pero el grupo tiene {len(casos)} casos")
        polaridades = set()
        for i, caso in enumerate(casos):
            caso_ctx = f"{contexto}[{i}]"
            if not isinstance(caso, dict):
                fallas.append(f"{caso_ctx} debe ser un objeto")
                continue
            if type(caso.get("esperado_ok")) is not bool:
                fallas.append(f"{caso_ctx}: `esperado_ok` debe ser booleano")
            else:
                polaridades.add(caso["esperado_ok"])
            fallas += _validar_evidencia(caso.get("evidencia"), caso_ctx)
        if polaridades != {False, True}:
            fallas.append(f"{contexto} debe contener ambas polaridades (verde y rojo)")
    return fallas


def validar_fixture(datos: Any, nombre: str = "fixture") -> list[str]:
    """Contrato fail-closed para las dos formas de ``oracle.diferencial/v1``."""
    fallas = _validar_comunes(datos, nombre)
    if not isinstance(datos, dict):
        return fallas
    if datos.get("esquema") != ESQUEMA_DIFERENCIAL or not isinstance(datos.get("frescura"), dict):
        return fallas
    tiene_escenarios, tiene_grupos = "escenarios" in datos, "grupos" in datos
    if tiene_escenarios and tiene_grupos:
        fallas.append(f"{nombre}: mezcla los formatos `escenarios` y `grupos`")
    elif tiene_escenarios:
        fallas += _validar_dominio(datos, nombre)
    elif tiene_grupos:
        fallas += _validar_grupos(datos, nombre)
    else:
        fallas.append(f"{nombre}: formato desconocido; falta `escenarios` o `grupos`")
    return fallas


def _medida_frescura():
    """Carga la política escrita en el lenguaje; no reimplementa su comparación en Python."""
    from nucleo.macro import macros_base
    from nucleo.medida import cargar

    ruta = (Path(__file__).resolve().parents[1] / "catalogos" / "meta"
            / f"{ID_MEDIDA_FRESCURA}.oracle")
    return cargar(ruta, macros=macros_base())


def referentes_de_fixture(datos: dict) -> list[Referente]:
    """Lo que un fixture declara haber leído: el referente de cada fuente, con su huella.

    Estos referentes YA se calculaban —`revisar_frescura` los arma para comparar contra el estado
    de hoy—, pero morían adentro de esa función. Exponerlos es lo que convierte L−2 de algo que el
    lenguaje sabe expresar en algo que este repositorio realmente emite, y es la condición que la
    DECISIÓN 004 puso para que `meta.ninguna_evidencia_declara_un_referente_sin_huella` deje de
    estar sostenida sólo por evidencia fabricada.

    El `cuando` es «al generar» porque eso es lo que la declaración afirma: el estado que el emisor
    vio en el momento de producir el fixture. Nada acá comprueba que siga siendo cierto — de eso se
    ocupa `revisar_frescura`, y la medida que consume estos hechos lo dice en su alcance.
    """
    frescura = datos.get("frescura")
    if not isinstance(frescura, dict):
        return []
    huellas = frescura.get("huellas")
    if not isinstance(huellas, dict):
        return []
    return [Referente(que, huella if isinstance(huella, str) else "", "al generar")
            for que, huella in sorted(huellas.items())]


def revisar_frescura(datos: dict, raiz: Path, catalogo: dict) -> list[str]:
    """Recalcula huellas y entrega las dos declaraciones a la medida de L−2."""
    frescura = datos["frescura"]
    raiz_fuentes = Path(raiz) / frescura["raiz_fuentes"]
    fuentes = frescura["fuentes"]
    esperadas = frescura["huellas"]
    # Las que el fixture trae escritas no entran en la huella del catálogo: firmarlas con lo que
    # el propio fixture dice sería una huella que se comprueba a sí misma. Quien las fija es la
    # huella del emisor, que es donde están escritas.
    propias = set(datos.get("medidas_declaradas") or {})
    del_catalogo = [mid for mid in ids_de_medidas(datos) if mid not in propias]
    medidas = [catalogo[mid] for mid in del_catalogo if mid in catalogo]
    faltan = [mid for mid in del_catalogo if mid not in catalogo]
    if faltan:
        return [f"fixture vencido: faltan medidas actuales para recalcular el catálogo: {faltan}"]

    actuales = {
        "catalogo": huella_catalogo(medidas),
        "configuracion": huella_datos(frescura["configuracion"]),
    }
    problemas = []
    for clase in ("emisor", "referencia"):
        try:
            actuales[clase] = huella_archivos(raiz_fuentes, fuentes[clase])
        except (OSError, ProcedenciaInvalida) as e:
            problemas.append(f"fixture vencido: no se pudo comprobar {clase}: {e}")
    if problemas:
        return problemas

    evidencia = hechos_de_frescura(
        [Referente(clase, huella, "al generar")
         for clase, huella in esperadas.items()],
        [Referente(clase, huella, "ahora")
         for clase, huella in actuales.items()],
    )

    veredicto = _medida_frescura().evaluar(evidencia)
    for testigo in veredicto.testigos:
        referente = testigo["r"]
        problemas.append(
            f"fixture vencido: cambió {referente['que']} "
            f"({referente['huella_leida'][:12]}… → {referente['huella_actual'][:12]}…)"
        )
    return problemas


def cargar_fixtures(rutas: Iterable[Path], *, raiz: Path | None = None,
                    catalogo: dict | None = None) -> tuple[list[Fixture], list[str]]:
    """Carga y valida; con raíz y catálogo también exige procedencia todavía fresca."""
    if (raiz is None) != (catalogo is None):
        raise ValueError("`raiz` y `catalogo` se pasan juntos para comprobar frescura")
    cargados, fallas = [], []
    for ruta in rutas:
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as e:
            fallas.append(f"{ruta.name}: JSON ilegible — {e}")
            continue
        problemas = validar_fixture(datos, ruta.name)
        if not problemas and raiz is not None:
            problemas = [f"{ruta.name}: {p}" for p in revisar_frescura(datos, raiz, catalogo)]
        if problemas:
            fallas += problemas
        else:
            cargados.append(Fixture(ruta, datos))
    return cargados, fallas


def evidencias(fixture: Fixture) -> Iterator[tuple[str, dict]]:
    """Evidencias únicas con un origen legible, sin obligar al consumidor a conocer el formato."""
    datos = fixture.datos
    if "escenarios" in datos:
        for escenario in datos["escenarios"]:
            yield f"{fixture.ruta.stem}/{escenario['id']}", escenario["evidencia"]
    else:
        for mid, casos in datos["grupos"].items():
            for i, caso in enumerate(casos):
                yield f"{fixture.ruta.stem}/{mid}[{i}]", caso["evidencia"]


def casos_para_mutacion(fixture: Fixture, catalogo: dict) -> Iterator[dict]:
    """Proyecta cualquiera de las dos formas al contrato corpus-like del mutador."""
    datos = fixture.datos
    if "escenarios" in datos:
        for mid in datos["medidas"]:
            if mid not in catalogo:
                continue
            for escenario in datos["escenarios"]:
                ok = catalogo[mid].evaluar(escenario["evidencia"]).ok
                yield {"id": f"{fixture.ruta.stem}/{mid}[{escenario['id']}]",
                       "etiqueta": "verde_correcto" if ok else "falso_verde",
                       "medida": mid, "evidencia": escenario["evidencia"]}
    else:
        for mid, entradas in datos["grupos"].items():
            for i, entrada in enumerate(entradas):
                yield {"id": f"{fixture.ruta.stem}/{mid}[{i}]",
                       "etiqueta": "verde_correcto" if entrada["esperado_ok"] else "falso_verde",
                       "medida": mid, "evidencia": entrada["evidencia"]}
