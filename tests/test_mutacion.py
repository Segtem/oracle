"""Tests del sensor de mutación. Un sensor sin tests es evidencia sin garantía."""

from __future__ import annotations

import importlib
import sys
from unittest import mock
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo import mutacion
from nucleo.medida import Medida

BASE = ["medida", "d.prueba",
        ["desde", ["de", "cosa", "c"], ["donde", ["==", ["campo", "c", "mal"], True]]],
        ["resumen", "contar", 1],
        ["umbral", "<=", 0, "una razón"],
        ["alcance", "NO ve nada más"]]

COMPLEJA = ["medida", "d.compleja",
            ["desde", ["unir", ["de", "izquierda", "a"], ["de", "derecha", "b"]],
             ["donde", ["y", [">", ["campo", "a", "x"], ["campo", "a", "limite"]],
                         ["==", ["campo", "b", "activo"], True]]],
             ["agrupar", [["grupo", ["campo", "a", "grupo"]]],
              [["mayor", "max", ["campo", "a", "x"]],
               ["total", "suma", ["campo", "a", "limite"]]]]],
            ["resumen", "promedio", ["col", "mayor"]],
            ["umbral", "<=", 10, "una razón"],
            ["alcance", "NO ve nada más"]]

CON_NO = ["medida", "d.con_no",
          ["desde", ["de", "cosa", "c"],
           ["donde", ["no", ["==", ["campo", "c", "mal"], True]]]],
          ["resumen", "contar", 1],
          ["umbral", "<=", 0, "una razón"],
          ["alcance", "NO ve nada más"]]

CON_CONTEO_AGRUPADO = ["medida", "d.conteo_agrupado",
                       ["desde", ["de", "cosa", "c"],
                        ["agrupar", [["grupo", ["campo", "c", "grupo"]]],
                         [["cantidad", "contar", 1]]]],
                       ["resumen", "suma", ["col", "cantidad"]],
                       ["umbral", "<=", 0, "una razón"],
                       ["alcance", "NO ve nada más"]]

# una fila que ofende y otra que no: es lo que permite que el filtro se pueda fijar
EV_ROJO = {"cosa": [{"id": "x", "mal": True}, {"id": "y", "mal": False}]}
EV_VERDE = {"cosa": [{"id": "y", "mal": False}, {"id": "z", "mal": False}]}

CASO_ROJO = {"id": "c-rojo", "etiqueta": "falso_verde", "medida": "d.prueba", "evidencia": EV_ROJO}
CASO_VERDE = {"id": "c-verde", "etiqueta": "verde_correcto", "medida": "d.prueba",
              "evidencia": EV_VERDE}

# Dos campos de TIPOS distintos en el mismo alias: sustituir uno por el otro produce una
# comparación incomparable, y el mutante muere sin que ningún caso lo haya discriminado. Es el
# mecanismo exacto de los mutantes que mueren sólo por excepción en el catálogo real.
TIPOS = ["medida", "d.tipos",
         ["desde", ["de", "cosa", "c"],
          ["donde", ["y", ["==", ["campo", "c", "n"], 1],
                     ["==", ["campo", "c", "s"], "x"]]]],
         ["resumen", "contar", 1],
         ["umbral", "<=", 0, "una razón"],
         ["alcance", "NO ve nada más"]]

CASO_TIPOS_ROJO = {"id": "c-tipos-rojo", "etiqueta": "falso_verde", "medida": "d.tipos",
                   "evidencia": {"cosa": [{"n": 1, "s": "x"}, {"n": 1, "s": "z"}]}}
CASO_TIPOS_VERDE = {"id": "c-tipos-verde", "etiqueta": "verde_correcto", "medida": "d.tipos",
                    "evidencia": {"cosa": [{"n": 9, "s": "z"}]}}


def setUpModule() -> None:
    """Registra las escalares del catálogo base DENTRO de la suite, no al importar el módulo.

    Como `import catalogos.escalares` al tope, el decorador `@escalar` corría durante el
    descubrimiento: un mutante en `escalar()`, `_registro()` o `_contrato_de_escalar()` rompía la
    importación del archivo de test y el arnés lo reportaba como «error» en vez de «muerte». Once
    mutantes de `nucleo/algebra.py` quedaban sin veredicto por esto. Acá el fallo es del test.
    """
    importlib.import_module("catalogos.escalares")


class LosMutadoresTienenAutorTests(unittest.TestCase):
    """El conjunto que corre no es sólo el propio, y eso tiene que ser comprobable.

    Un mutador que nadie escribió no puede producir un sobreviviente, así que «todos muertos» sobre
    un conjunto de autoría propia acota menos de lo que parece. Si los ajenos dejaran de cargarse,
    el número volvería a subir a 100% sin que nada lo dijera — que es justo el modo de fallar que
    estos tests existen para atrapar.
    """

    def test_corren_los_propios_y_los_ajenos(self) -> None:
        from nucleo.mutacion import MUTADORES, MUTADORES_PROPIOS

        self.assertTrue(set(MUTADORES_PROPIOS) <= set(MUTADORES))
        ajenos = set(MUTADORES) - set(MUTADORES_PROPIOS)
        self.assertGreater(len(ajenos), 15, "los mutadores del segundo autor no se cargaron")

    def test_el_equivalente_declarado_queda_afuera(self) -> None:
        """`convertir_conteo_en_existencia` cambia `contar` por `max(1)`. Con `umbral <= 0` —el de
        las 54 medidas del catálogo— «contar al menos una» y «existe alguna» son la misma
        afirmación: no debilita nada y ninguna evidencia puede distinguirlo. Está excluido a
        propósito, no por olvido."""
        from nucleo.mutacion import MUTADORES

        self.assertNotIn("convertir_conteo_en_existencia", MUTADORES)

    def test_sin_el_directorio_de_ajenos_devuelve_un_mapa_vacio_y_no_None(self) -> None:
        """Un consumidor instala el núcleo, no este repositorio: si `mutadores/` no está, la ronda
        mide con los propios en vez de romperse.

        Se exige `{}` y NO `None` a propósito. El llamador hace `or {}`, así que devolver `None`
        se comporta igual y el mutante que lo cambia es indistinguible por conducta: el arnés cae a
        correr la suite entera para confirmarlo y se pasa de tiempo. Fijar el tipo de retorno acá lo
        mata en los tests prioritarios, que es donde tiene que morir.
        """
        from nucleo import mutacion

        with mock.patch.dict(sys.modules, {"mutadores": None, "mutadores.segundo_autor": None}):
            devuelto = mutacion._mutadores_ajenos()
        self.assertEqual(devuelto, {})
        self.assertIsNotNone(devuelto)

    def test_sin_los_ajenos_el_arnes_sigue_midiendo(self) -> None:
        """Un consumidor instala el núcleo, no este repositorio: si el directorio de mutadores
        ajenos no está, la ronda mide con los propios en vez de romperse."""
        from nucleo import mutacion

        with mock.patch.object(mutacion, "_mutadores_ajenos", return_value={}):
            solo_propios = {**mutacion.MUTADORES_PROPIOS, **(mutacion._mutadores_ajenos() or {})}
        self.assertEqual(set(solo_propios), set(mutacion.MUTADORES_PROPIOS))


class MutadoresTests(unittest.TestCase):
    IDS_ESTRUCTURALES_COMPLEJA = [
        "fuente:2.1.1.1:izquierda→derecha",
        "fuente:2.1.2.1:derecha→izquierda",
        "expresion:logico@2.2.1:y→o",
        "expresion:comparador@2.2.1.1:>→<=",
        "expresion:comparador@2.2.1.2:==→!=",
        "expresion:booleano@2.2.1.2.2",
        "agregado:3.1:promedio→suma",
        "agregado:2.3.2.0.1:max→min",
        "agregado:2.3.2.1.1:suma→promedio",
        "campo:2.2.1.1.1.2:x→grupo",
        "campo:2.2.1.1.1.2:x→limite",
        "campo:2.2.1.1.2.2:limite→grupo",
        "campo:2.2.1.1.2.2:limite→x",
        "campo:2.3.1.0.1.2:grupo→limite",
        "campo:2.3.1.0.1.2:grupo→x",
        "campo:2.3.2.0.2.2:x→grupo",
        "campo:2.3.2.0.2.2:x→limite",
        "campo:2.3.2.1.2.2:limite→grupo",
        "campo:2.3.2.1.2.2:limite→x",
        "campo:3.2.1:mayor→grupo",
        "campo:3.2.1:mayor→total",
    ]

    def test_todo_mutante_sigue_siendo_una_medida_valida(self) -> None:
        for medida in (BASE, COMPLEJA):
            for nombre, datos in mutacion.mutantes(medida):
                with self.subTest(medida=medida[1], mutador=nombre):
                    Medida.de_datos(datos)   # no debe levantar

    def test_no_toca_la_medida_original(self) -> None:
        antes = str(BASE)
        mutacion.mutantes(BASE)
        self.assertEqual(str(BASE), antes)

    def test_el_denominador_cubre_fuentes_expresiones_agregados_y_campos(self) -> None:
        nombres = [nombre for nombre, _datos in mutacion.mutantes(COMPLEJA)]
        for categoria in ("fuente:", "expresion:", "agregado:", "campo:"):
            with self.subTest(categoria=categoria):
                self.assertTrue(any(nombre.startswith(categoria) for nombre in nombres), nombres)
        self.assertEqual(len(nombres), len(set(nombres)))

    def test_los_ids_estructurales_son_estables_y_exhaustivos(self) -> None:
        estructurales = [nombre for nombre, _datos in mutacion.mutantes(COMPLEJA)
                         if ":" in nombre]
        self.assertEqual(estructurales, self.IDS_ESTRUCTURALES_COMPLEJA)

    def test_cada_id_estructural_senala_el_unico_escalar_que_cambia(self) -> None:
        def diferencias(a, b, ruta=()):
            if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
                return [diferencia for i, (x, y) in enumerate(zip(a, b))
                        for diferencia in diferencias(x, y, (*ruta, i))]
            return [] if a == b else [ruta]

        for nombre, datos in mutacion.mutantes(COMPLEJA):
            if ":" not in nombre:
                continue
            if nombre.startswith("expresion:"):
                tipo, resto = nombre.split("@", 1)
                ruta = tuple(map(int, resto.split(":", 1)[0].split(".")))
                if tipo != "expresion:booleano":
                    ruta = (*ruta, 0)
            else:
                ruta = tuple(map(int, nombre.split(":", 2)[1].split(".")))
            with self.subTest(mutante=nombre):
                self.assertEqual(diferencias(COMPLEJA, datos), [ruta])

    def test_quitar_no_reemplaza_exactamente_el_nodo_por_su_operando(self) -> None:
        nombre, datos = next(
            (nombre, datos) for nombre, datos in mutacion.mutantes(CON_NO)
            if nombre.startswith("expresion:quitar_no@"))
        self.assertEqual(nombre, "expresion:quitar_no@2.2.1")
        self.assertEqual(datos[2][2][1], ["==", ["campo", "c", "mal"], True])

    def test_contar_agrupado_se_vuelve_suma_cero_en_el_mismo_agregado(self) -> None:
        nombre, datos = next(
            (nombre, datos) for nombre, datos in mutacion.mutantes(CON_CONTEO_AGRUPADO)
            if "contar→suma(0)" in nombre and nombre.startswith("agregado:2."))
        self.assertEqual(nombre, "agregado:2.2.2.0.1:contar→suma(0)")
        self.assertEqual(datos[2][2][2][0], ["cantidad", "suma", 0])

    def test_aflojar_umbral_mueve_el_limite_un_paso_sin_escala_magica(self) -> None:
        d = mutacion.aflojar_umbral(BASE)
        self.assertEqual(d[4][2], 1)
        self.assertTrue(Medida.de_datos(d).evaluar(EV_ROJO).ok)

    def test_aflojar_umbral_respeta_magnitudes_mayores_y_menores_que_1e12(self) -> None:
        for op, limite, esperado in (
                ("<=", 10**15, 10**15 + 1),
                ("<", 10**9, 10**9 + 1),
                (">=", -10**15, -10**15 - 1),
                (">", -10**9, -10**9 - 1)):
            with self.subTest(op=op, limite=limite):
                datos = [*BASE[:4], ["umbral", op, limite, "x"], BASE[5]]
                self.assertEqual(mutacion.aflojar_umbral(datos)[4][2], esperado)

    def test_aflojar_un_flotante_usa_el_siguiente_representable(self) -> None:
        datos = [*BASE[:4], ["umbral", "<=", 1e20, "x"], BASE[5]]
        nuevo = mutacion.aflojar_umbral(datos)[4][2]
        self.assertGreater(nuevo, 1e20)
        self.assertLess(nuevo, float("inf"))

    def test_aflojar_umbral_no_aplica_a_igualdad(self) -> None:
        d = [*BASE[:4], ["umbral", "==", 0, "x"], BASE[5]]
        self.assertIsNone(mutacion.aflojar_umbral(d))

    def test_aflojar_umbral_rechaza_booleanos_y_no_numeros(self) -> None:
        for limite in (True, "1", None):
            with self.subTest(limite=limite):
                d = [*BASE[:4], ["umbral", "<=", limite, "x"], BASE[5]]
                self.assertIsNone(mutacion.aflojar_umbral(d))

    def test_invertir_comparador(self) -> None:
        self.assertEqual(mutacion.invertir_comparador(BASE)[4][1], ">")

    def test_quitar_filtro_cuenta_la_relacion_entera(self) -> None:
        d = mutacion.quitar_filtro(BASE)
        self.assertEqual(Medida.de_datos(d).evaluar(EV_VERDE).valor, 2)

    def test_quitar_y_negar_filtro_no_aplican_sin_donde(self) -> None:
        d = [*BASE[:2], ["desde", ["de", "cosa", "c"]], *BASE[3:]]
        self.assertIsNone(mutacion.quitar_filtro(d))
        self.assertIsNone(mutacion.negar_filtro(d))

    def test_quitar_requiere_remueve_el_nodo_conservando_el_resto(self) -> None:
        con_req = ["medida", "d.req",
                   ["desde", ["de", "cosa", "c"]],
                   ["resumen", "contar", 1],
                   ["umbral", "<=", 0, "una razón"],
                   ["requiere", "cosa"],
                   ["alcance", "NO ve nada más"]]
        sin_req = mutacion.quitar_requiere(con_req)
        self.assertEqual(len(sin_req), 6)
        self.assertEqual(sin_req, [
            "medida", "d.req",
            ["desde", ["de", "cosa", "c"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "una razón"],
            ["alcance", "NO ve nada más"]])
        self.assertIsNone(mutacion.quitar_requiere(BASE))
        nombres = [nombre for nombre, _ in mutacion.mutantes(con_req)]
        self.assertIn("quitar_requiere", nombres)

    def test_negar_filtro_invierte_el_predicado(self) -> None:
        d = mutacion.negar_filtro(BASE)
        self.assertEqual(Medida.de_datos(d).evaluar(EV_ROJO).valor, 1)   # la fila «y»


class CorrerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalogo = {"d.prueba": Medida.de_datos(BASE)}

    def test_produce_hechos_y_no_veredictos(self) -> None:
        ev = mutacion.correr(self.catalogo, [CASO_ROJO, CASO_VERDE])
        self.assertEqual(sorted(ev), ["corrida_mutacion_medidas", "deteccion", "mutante"])
        self.assertNotIn("resultado_confiable", ev["corrida_mutacion_medidas"][0])
        for fila in ev["mutante"]:
            self.assertEqual(sorted(fila),
                             ["apunta_a", "cambio", "detecciones_conductuales", "id",
                              "rechazos_del_algebra"])

    def test_morir_por_excepcion_no_es_morir_por_conducta(self) -> None:
        """Un mutante que el álgebra rechaza no lo discriminó ningún caso: contarlo como muerte
        conductual publica una capacidad de detección que el corpus no tiene."""
        ev = mutacion.correr({"d.tipos": Medida.de_datos(TIPOS)},
                             [CASO_TIPOS_ROJO, CASO_TIPOS_VERDE])
        por_excepcion = [m for m in ev["mutante"]
                         if m["rechazos_del_algebra"] and not m["detecciones_conductuales"]]
        self.assertEqual(sorted(m["cambio"] for m in por_excepcion),
                         ["campo:2.2.1.1.1.2:n→s", "campo:2.2.1.2.1.2:s→n"])
        for m in por_excepcion:
            self.assertEqual(m["rechazos_del_algebra"], 2)
        # y la razón registrada es una excepción, no una inversión de veredicto
        del_mutante = [d for d in ev["deteccion"]
                       if d["mutante"].endswith("campo:2.2.1.1.1.2:n→s")]
        self.assertTrue(all(d["rechazado_por_el_algebra"] for d in del_mutante))
        self.assertFalse(any(d["invirtio_el_veredicto"] or d["cambio_los_testigos"]
                             or d["cambio_el_valor"] for d in del_mutante))
        # el resto sí murió por conducta: la distinción separa, no marca todo igual
        self.assertTrue(all(m["detecciones_conductuales"] for m in ev["mutante"]
                            if not m["cambio"].startswith("campo:")))

    def test_un_mutante_muere_si_ALGUN_caso_lo_detecta(self) -> None:
        ev = mutacion.correr(self.catalogo, [CASO_ROJO, CASO_VERDE])
        quitar = next(m for m in ev["mutante"] if m["cambio"] == "quitar_filtro")
        # el conteo, no un booleano: los DOS casos lo notaron, y eso es lo que el hecho publica
        self.assertEqual(quitar["detecciones_conductuales"], 2)
        self.assertEqual(quitar["rechazos_del_algebra"], 0)

    def test_quitar_el_filtro_se_detecta_por_los_TESTIGOS_no_por_el_veredicto(self) -> None:
        """En el caso rojo, contar sin filtro sigue dando >0: el veredicto no se mueve. Lo que
        cambia es QUIÉNES son los testigos, y el informe también es contrato."""
        ev = mutacion.correr(self.catalogo, [CASO_ROJO])
        d = next(x for x in ev["deteccion"] if x["mutante"].endswith("quitar_filtro"))
        self.assertTrue(d["cambio_los_testigos"])
        self.assertFalse(d["invirtio_el_veredicto"])

    def test_un_agregado_que_cambia_el_VALOR_mata_al_mutante_aunque_siga_rojo(self) -> None:
        datos = ["medida", "d.valor",
                 ["desde", ["de", "cosa", "c"]],
                 ["resumen", "max", ["campo", "c", "valor"]],
                 ["umbral", "<=", 0, "una razón"],
                 ["alcance", "NO ve nada más"]]
        caso = {"id": "c-valor", "etiqueta": "falso_verde", "medida": "d.valor",
                "evidencia": {"cosa": [{"valor": 2}, {"valor": 8}]}}

        ev = mutacion.correr({"d.valor": Medida.de_datos(datos)}, [caso])

        d = next(x for x in ev["deteccion"] if x["mutante"].endswith("max→min"))
        self.assertTrue(d["cambio_el_valor"])
        self.assertFalse(d["invirtio_el_veredicto"])

    def test_aflojar_el_umbral_se_detecta_por_el_VEREDICTO(self) -> None:
        ev = mutacion.correr(self.catalogo, [CASO_ROJO])
        d = next(x for x in ev["deteccion"] if x["mutante"].endswith("aflojar_umbral"))
        self.assertTrue(d["invirtio_el_veredicto"])

    def test_aflojar_umbral_sigue_necesitando_un_caso_ROJO(self) -> None:
        """Aflojar un umbral no mueve un verde ni le cambia los testigos: hace falta un caso ROJO.
        Es al revés de lo que yo suponía cuando agregué los casos verdes."""
        solo_verde = mutacion.correr(self.catalogo, [CASO_VERDE])
        self.assertFalse(next(m for m in solo_verde["mutante"]
                              if m["cambio"] == "aflojar_umbral")["detecciones_conductuales"])
        solo_rojo = mutacion.correr(self.catalogo, [CASO_ROJO])
        self.assertTrue(next(m for m in solo_rojo["mutante"]
                             if m["cambio"] == "aflojar_umbral")["detecciones_conductuales"])

    def test_un_caso_que_no_esta_en_su_estado_esperado_se_saltea(self) -> None:
        # etiquetado verde pero su evidencia da rojo: no fija nada y no debe contaminar
        mentiroso = {**CASO_ROJO, "etiqueta": "verde_correcto", "id": "c-mal"}
        self.assertEqual(mutacion.correr(self.catalogo, [mentiroso])["deteccion"], [])

    def test_una_medida_que_no_esta_en_el_catalogo_se_ignora(self) -> None:
        ajeno = {**CASO_ROJO, "medida": "d.fantasma"}
        self.assertEqual(mutacion.correr(self.catalogo, [ajeno])["mutante"], [])

    def test_la_mutacion_en_memoria_no_declara_estado_de_bytecode(self) -> None:
        # Este sensor no ejecuta código mutado ni toca archivos: el estado del bytecode no aplica.
        # Publicar `True` sólo para compartir forma con otro sensor sería una confianza ornamental.
        ev = mutacion.correr(self.catalogo, [CASO_ROJO])
        self.assertNotIn("bytecode_frio", ev["corrida_mutacion_medidas"][0])

    def test_un_mutante_que_revienta_cuenta_como_muerto_y_no_como_hallazgo(self) -> None:
        malo = [*BASE[:2],
                ["desde", ["de", "cosa", "c"], ["donde", ["==", ["campo", "c", "no_existe"], True]]],
                *BASE[3:]]
        catalogo = {"d.prueba": Medida.de_datos(BASE)}
        original = mutacion.MUTADORES["negar_filtro"]
        try:
            mutacion.MUTADORES["negar_filtro"] = lambda d: malo
            ev = mutacion.correr(catalogo, [CASO_ROJO])
            d = next(x for x in ev["deteccion"] if x["mutante"].endswith("negar_filtro"))
            self.assertTrue(d["rechazado_por_el_algebra"])
        finally:
            mutacion.MUTADORES["negar_filtro"] = original


if __name__ == "__main__":
    unittest.main()
