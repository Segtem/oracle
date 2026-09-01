"""Contratos pequeños de medida, cargados sin importar el módulo durante descubrimiento.

Esto es intencional: si una mutación rompe la construcción de la clasificación base, la excepción
ocurre dentro de un test y demuestra discriminación; no se confunde con un runner roto.
"""

from __future__ import annotations

import importlib
import json
import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace


def modulo_medida():
    return importlib.import_module("nucleo.medida")


class ContratoMedidaTests(unittest.TestCase):
    def test_clasificacion_meta_valida_forma_y_contenido(self) -> None:
        m = modulo_medida()
        base = m.ClasificacionMeta()
        self.assertEqual(base.relaciones_del_lenguaje,
                         frozenset({"ancestro", "medida", "caso", "medida_en_uso",
                                    "paso", "nodo", "producto", "equivalencia",
                                    "paso_de_medida", "fuente", "termino", "requiere",
                                    "campo_declarado", "relacion_declarada",
                                    "referente_declarado", "referente_comparado",
                                    "cantidad_comparada", "sombra"}))
        self.assertEqual(base.prefijos_meta, ("meta.",))

        invalidas = (
            {"relaciones_del_lenguaje": {"medida"}},
            {"relaciones_del_lenguaje": frozenset({1})},
            {"relaciones_del_lenguaje": frozenset({""})},
            {"prefijos_meta": ["meta."]},
            {"prefijos_meta": ()},
            {"prefijos_meta": (1,)},
            {"prefijos_meta": ("",)},
        )
        for kwargs in invalidas:
            with self.subTest(kwargs=kwargs), self.assertRaises(m.MedidaMalDeclarada):
                m.ClasificacionMeta(**kwargs)

    def test_los_cuatro_datos_publicos_son_inmutables(self) -> None:
        m = modulo_medida()
        objetos_y_campo = (
            (m.ClasificacionMeta(), "prefijos_meta"),
            (m.Veredicto("d.m", 0, True, "<= 0", "razón", "alcance", ()), "ok"),
            (m.Medida("d.m", [], [], "<=", 0, "razón", "alcance"), "limite"),
            (m.Informe(()), "veredictos"),
        )
        for objeto, campo in objetos_y_campo:
            with self.subTest(tipo=type(objeto).__name__), self.assertRaises(FrozenInstanceError):
                setattr(objeto, campo, None)

    def test_linea_roja_sin_testigos_no_inventa_una_flecha(self) -> None:
        m = modulo_medida()
        v = m.Veredicto("d.m", 1, False, "<= 0", "razón", "alcance", ())
        self.assertNotIn("→", v.linea())

    def test_exactamente_cuatro_testigos_muestra_tres_y_un_restante(self) -> None:
        m = modulo_medida()
        testigos = tuple({"x": {"id": str(i)}} for i in range(4))
        linea = m.Veredicto("d.m", 4, False, "<= 0", "razón", "alcance", testigos).linea()
        self.assertEqual(linea.count("x="), 3)
        self.assertIn("+1", linea)

    def test_json_del_informe_conserva_unicode_legible(self) -> None:
        m = modulo_medida()
        veredicto = m.Veredicto("dominio.señal", 0, True, "<= 0", "razón", "qué no ve", ())
        texto = m.Informe((veredicto,)).a_json()
        self.assertIn("señal", texto)
        self.assertNotIn("\\u00f1", texto)
        self.assertEqual(json.loads(texto)["medidas"][0]["id"], "dominio.señal")

    def test_relacion_vacia_directa_y_compuesta_se_derivan_sin_convenciones(self) -> None:
        m = modulo_medida()

        def medida(mid, tuberia):
            return SimpleNamespace(
                id=mid, tuberia=tuberia, op="<=", limite=0,
                porque="razón", alcance="qué no ve")

        casos = (
            (medida("d.vacia", ["desde"]), ""),
            (medida("d.directa", ["desde", ["de", "pieza", "p"]]), "pieza"),
            (medida("d.compuesta", [
                "desde",
                ["unir", ["de", "primera", "a"], ["de", "segunda", "b"]],
            ]), "primera"),
        )
        self.assertEqual([m.relaciones_de_medida(objeto)[0] if m.relaciones_de_medida(objeto)
                          else "" for objeto, _esperada in casos],
                         [esperada for _objeto, esperada in casos])

    def test_como_hechos_sigue_siendo_lista_y_cuelga_relaciones_estructurales(self) -> None:
        m = modulo_medida()
        medida = m.Medida.de_datos([
            "medida", "d.con_requiere",
            ["desde", ["unir", ["de", "pieza", "p"], ["de", "marca", "q"]],
             ["donde", ["==", ["campo", "p", "id"], ["campo", "q", "pieza"]]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "una razón"],
            ["requiere", "marca"],
            ["alcance", "NO ve otro dominio"],
        ])
        hechos = m.como_hechos([medida])

        self.assertIsInstance(hechos, list)
        self.assertEqual(hechos[0]["agregado"], "contar")
        self.assertEqual(hechos[0]["comparador"], "<=")
        self.assertEqual(hechos[0]["pasos"], 2)
        self.assertTrue(hechos[0]["declara_requiere"])
        self.assertEqual(hechos.por_relacion["requiere"],
                         [{"medida": "d.con_requiere", "indice": 0, "relacion": "marca"}])
        self.assertEqual(
            sorted((f["relacion"], f["alias"]) for f in hechos.por_relacion["fuente"]),
            [("marca", "q"), ("pieza", "p")])
        self.assertTrue(any(t["cabeza"] == "requiere"
                            for t in hechos.por_relacion["termino"]))

    def test_como_hechos_marca_si_el_umbral_es_flotante(self) -> None:
        m = modulo_medida()
        con_flotante = m.Medida.de_datos([
            "medida", "d.flotante",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0.5, "una razón"],
            ["alcance", "NO ve"],
        ])
        con_entero = m.Medida.de_datos([
            "medida", "d.entero",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "una razón"],
            ["alcance", "NO ve"],
        ])
        hechos = {h["id"]: h for h in m.como_hechos([con_flotante, con_entero])}
        self.assertTrue(hechos["d.flotante"]["umbral_es_flotante"])
        self.assertFalse(hechos["d.entero"]["umbral_es_flotante"])

    def test_el_umbral_de_igualdad_sobre_flotante_carga_y_lo_juzga_la_medida(self) -> None:
        m = modulo_medida()
        medida = m.Medida.de_datos([
            "medida", "d.igual_flotante",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "==", 0.3, "una razón"],
            ["alcance", "NO ve"],
        ])
        hechos = m.como_hechos([medida])
        self.assertTrue(hechos[0]["umbral_es_flotante"])
        self.assertEqual(hechos[0]["comparador"], "==")

    def test_evaluar_y_aplicables_despliegan_relaciones_derivadas(self) -> None:
        m = modulo_medida()
        fuente = m.Medida.de_datos([
            "medida", "d.con_requiere",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "una razón"],
            ["requiere", "pieza"],
            ["alcance", "NO ve otra cosa"],
        ])
        jueza = m.Medida.de_datos([
            "medida", "meta.ve_terminos",
            ["desde", ["de", "termino", "t"],
             ["donde", ["==", ["campo", "t", "cabeza"], "requiere"]]],
            ["resumen", "contar", 1],
            ["umbral", ">=", 1, "una razón"],
            ["requiere", "termino"],
            ["alcance", "NO ve semántica del requisito"],
        ])
        evidencia = {"medida": m.como_hechos([fuente])}

        self.assertEqual(m.medidas_aplicables([jueza], evidencia), [jueza])
        self.assertTrue(jueza.evaluar(evidencia).ok)

    def test_las_juezas_se_seleccionan_por_relaciones_y_no_por_ids_conocidos(self) -> None:
        m = modulo_medida()
        self.assertEqual(m.relaciones_de_fuente(None), ())
        self.assertEqual(m.relaciones_de_fuente(["fuente_desconocida"]), ())

        def medida(mid, fuente):
            return SimpleNamespace(id=mid, tuberia=["desde", fuente])

        una = medida("cualquier.nombre", ["de", "a", "x"])
        dos = medida("otro.nombre", ["unir", ["de", "a", "x"], ["de", "b", "y"]])
        self.assertEqual(m.relaciones_de_medida(dos), ("a", "b"))
        self.assertEqual(m.medidas_aplicables([una, dos], {"a": []}), [una])
        self.assertEqual(m.medidas_aplicables([una, dos], {"a": [], "b": []}), [una, dos])

    def test_evidencia_con_derivadas_permite_iguales_y_falla_con_distintos(self) -> None:
        m = modulo_medida()
        medida = m.Medida.de_datos([
            "medida", "d.simple",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["alcance", "NO ve"],
        ])
        hechos = m.como_hechos([medida])
        fuente_igual = list(hechos.por_relacion["fuente"])
        fuente_distinta = [{"medida": "d.otra", "ruta": "2.1", "relacion": "otra", "alias": "o"}]

        # Si ya existía con contenido idéntico, no debe fallar
        evidencia_ok = {"medida": hechos, "fuente": fuente_igual}
        desplegada = m.evidencia_con_derivadas(evidencia_ok)
        self.assertEqual(desplegada["fuente"], fuente_igual)

        # Si ya existía con contenido distinto, debe fallar
        evidencia_choque = {"medida": hechos, "fuente": fuente_distinta}
        with self.assertRaisesRegex(ValueError, "dos veces con contenidos distintos"):
            m.evidencia_con_derivadas(evidencia_choque)

    def test_evaluar_sin_evidencia_devuelve_veredicto_con_valor_cero(self) -> None:
        m = modulo_medida()
        medida = m.Medida.de_datos([
            "medida", "d.requiere_algo",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["requiere", "pieza"],
            ["alcance", "NO ve"],
        ])
        v = medida.evaluar({})
        self.assertEqual(v.valor, 0)
        self.assertFalse(v.ok)
        self.assertEqual(v.sin_evidencia, "pieza")

    def test_rutas_en_catalogo_valida_directorio_existente_y_fisico(self) -> None:
        m = modulo_medida()
        # Normalización de argumentos de directorio
        self.assertEqual(m._normalizar_directorios(["a", "b"]), ("a", "b"))
        self.assertEqual(m._normalizar_directorios([["a", "b"]]), ("a", "b"))
        self.assertEqual(m._normalizar_directorios([("a", "b")]), ("a", "b"))
        self.assertEqual(m._normalizar_directorios(["un_solo_str"]), ("un_solo_str",))
        self.assertEqual(m._normalizar_directorios([m.Path("un_solo_path")]), (m.Path("un_solo_path"),))

        # Directorio inexistente devuelve lista vacía
        self.assertEqual(m._rutas_en_catalogo(m.Path("inexistente_xyz_123")), [])
        self.assertEqual(m.rutas_de_catalogo(m.Path("inexistente_xyz_123")), [])

        # Archivo regular que no es directorio debe fallar
        with self.assertRaisesRegex(m.MedidaMalDeclarada, "debe ser un directorio físico"):
            m._rutas_en_catalogo(__file__)

    def test_hecho_medida_pasos_en_medida_sin_pasos(self) -> None:
        m = modulo_medida()
        obj = SimpleNamespace(
            id="d.minima", tuberia=["desde"], resumen=["resumen", "contar", 1],
            op="<=", limite=0, porque="razón", alcance="alcance", requiere=())
        hecho = m._hecho_medida(obj, m.clasificacion_meta_base())
        self.assertEqual(hecho["pasos"], 0)

    def test_ruta_formatea_indices_y_cabeza_extrae_primer_string(self) -> None:
        m = modulo_medida()
        self.assertEqual(m._ruta((2, 1, 3)), "2.1.3")
        self.assertEqual(m._ruta(()), "")

        self.assertEqual(m._cabeza(["de", "pieza", "p"]), "de")
        self.assertEqual(m._cabeza([]), "")
        self.assertEqual(m._cabeza([123]), "")
        self.assertEqual(m._cabeza("no_es_lista"), "")
        self.assertEqual(m._cabeza(None), "")

    def test_tipo_distingue_todos_los_tipos_en_orden(self) -> None:
        m = modulo_medida()
        self.assertEqual(m._tipo([]), "lista")
        self.assertEqual(m._tipo(True), "booleano")
        self.assertEqual(m._tipo(False), "booleano")
        self.assertEqual(m._tipo(0), "entero")
        self.assertEqual(m._tipo(1.5), "flotante")
        self.assertEqual(m._tipo("hola"), "texto")
        self.assertEqual(m._tipo(None), "ausente")
        self.assertEqual(m._tipo((1, 2)), "tuple")
        self.assertEqual(m._tipo(object()), "object")

        medida = m.Medida.de_datos([
            "medida", "d.tipos",
            ["desde", ["de", "pieza", "p"],
             ["donde", ["y",
                        ["==", ["campo", "p", "b"], True],
                        ["==", ["campo", "p", "n"], 42],
                        ["==", ["campo", "p", "s"], "cadena"],
                        ["==", ["campo", "p", "f"], 3.14],
                        ["==", ["campo", "p", "z"], None]]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["alcance", "NO ve"],
        ])
        hechos = m.como_hechos([medida])
        terminos = hechos.por_relacion["termino"]
        tipos = {t["tipo"] for t in terminos}
        self.assertEqual(tipos, {"lista", "booleano", "entero", "flotante", "texto", "ausente"})
        textos_por_tipo = {(t["tipo"], t["texto"]) for t in terminos if t["tipo"] != "lista"}
        self.assertIn(("booleano", "true"), textos_por_tipo)
        self.assertIn(("entero", "42"), textos_por_tipo)
        self.assertIn(("flotante", "3.14"), textos_por_tipo)
        self.assertIn(("texto", "cadena"), textos_por_tipo)
        self.assertIn(("ausente", "null"), textos_por_tipo)
        flotante = next(t for t in terminos if t["tipo"] == "flotante")
        self.assertEqual(flotante["padre"], "2.2.1.4")
        self.assertEqual(flotante["cabeza_padre"], "==")
        for t in terminos:
            if t["tipo"] != "lista":
                self.assertEqual(t["longitud"], 0)

    def test_literal_nan_no_se_reifica_como_json_no_canonico(self) -> None:
        m = modulo_medida()
        with self.assertRaises(m.MedidaMalDeclarada):
            m._texto_literal(float("nan"))

    def test_ancestros_de_medida_emite_clausura_con_cabeza(self) -> None:
        m = modulo_medida()
        medida = m.Medida.de_datos([
            "medida", "d.ancestros",
            ["desde", ["de", "pieza", "p"],
             ["donde", ["==", ["campo", "p", "f"], 3.14]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["alcance", "NO ve"],
        ])
        hechos = m.como_hechos([medida])
        ancestros = hechos.por_relacion["ancestro"]

        # Cada fila trae los atributos del NODO repetidos, no sólo la ruta del ancestro. Con eso,
        # «¿hay un flotante comparado por igualdad dentro de un filtro?» se contesta con un `de` y un
        # `donde`, sin unir dos relaciones. La forma normalizada obligaba a ese `unir`, y `unir` arma
        # el producto completo: 1917 × 4699 = 9 millones de pares para quedarse con 1917, por encima
        # del límite de un millón. La repetición cuesta memoria; el `unir` costaba 228 líneas de
        # plan indexado en `nucleo/algebra.py` con 31 mutantes de código vivos.
        def fila(ancestro, cabeza_ancestro):
            return {"medida": "d.ancestros", "ruta": "2.2.1.2",
                    "ancestro": ancestro, "cabeza_ancestro": cabeza_ancestro,
                    "tipo": "flotante", "cabeza": "", "cabeza_padre": "==", "texto": "3.14"}

        self.assertIn(fila("2.2", "donde"), ancestros)
        self.assertIn(fila("2.2.1", "=="), ancestros)
        self.assertFalse(any(a["ruta"] == "" for a in ancestros))

    def test_pasos_de_medida_recorre_todos_los_pasos_con_sus_rutas_e_indices(self) -> None:
        m = modulo_medida()
        medida = m.Medida.de_datos([
            "medida", "d.pasos",
            ["desde",
             ["de", "pieza", "p"],
             ["donde", [">", ["campo", "p", "x"], 0]],
             ["agrupar", [["g", ["campo", "p", "g"]]], [["c", "contar", 1]]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["alcance", "NO ve"],
        ])
        hechos = m.como_hechos([medida])
        pasos = hechos.por_relacion["paso_de_medida"]
        self.assertEqual(pasos, [
            {"medida": "d.pasos", "indice": 0, "ruta": "2.1", "operador": "de"},
            {"medida": "d.pasos", "indice": 1, "ruta": "2.2", "operador": "donde"},
            {"medida": "d.pasos", "indice": 2, "ruta": "2.3", "operador": "agrupar"},
        ])

    def test_fuentes_de_medida_recorre_fuentes_simples_y_compuestas_con_rutas(self) -> None:
        m = modulo_medida()
        # Fuente simple
        simple = m.Medida.de_datos([
            "medida", "d.simple",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["alcance", "NO ve"],
        ])
        hechos_s = m.como_hechos([simple])
        self.assertEqual(hechos_s.por_relacion["fuente"], [
            {"medida": "d.simple", "ruta": "2.1", "relacion": "pieza", "alias": "p"},
        ])

        # Fuente compuesta con unir
        compuesta = m.Medida.de_datos([
            "medida", "d.compuesta",
            ["desde", ["unir", ["de", "primera", "a"], ["de", "segunda", "b"]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "razón"],
            ["alcance", "NO ve"],
        ])
        hechos_c = m.como_hechos([compuesta])
        self.assertEqual(hechos_c.por_relacion["fuente"], [
            {"medida": "d.compuesta", "ruta": "2.1.1", "relacion": "primera", "alias": "a"},
            {"medida": "d.compuesta", "ruta": "2.1.2", "relacion": "segunda", "alias": "b"},
        ])

        # Casos borde de _fuentes
        self.assertEqual(list(m._fuentes("d.m", [], (2, 1))), [])
        self.assertEqual(list(m._fuentes("d.m", "no_es_lista", (2, 1))), [])
        self.assertEqual(list(m._fuentes("d.m", None, (2, 1))), [])

    def test_derivacion_descubre_emisores_nuevos_sin_editar_listas(self) -> None:
        import tempfile
        from pathlib import Path
        m = modulo_medida()

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "nucleo").mkdir()
            (raiz / "tools").mkdir()
            (raiz / "nucleo" / "marco.py").write_text(
                'RELACIONES_DEL_LENGUAJE = frozenset({"caso", "medida_en_uso"})\n',
                encoding="utf-8")
            (raiz / "tools" / "nuevo.py").write_text(
                'RELACIONES_DEL_LENGUAJE = frozenset({"relacion_nueva"})\n',
                encoding="utf-8")

            relaciones = m.relaciones_del_lenguaje_declaradas(raiz=raiz)
            self.assertEqual(relaciones, frozenset({"caso", "medida_en_uso", "relacion_nueva"}))

    def test_derivacion_falla_cerrado_ante_declaraciones_invalidas(self) -> None:
        import tempfile
        from pathlib import Path
        m = modulo_medida()

        invalidas = (
            'RELACIONES_DEL_LENGUAJE = frozenset({1})\n',
            'RELACIONES_DEL_LENGUAJE = frozenset({""})\n',
            'RELACIONES_DEL_LENGUAJE = frozenset({"   "})\n',
            'RELACIONES_DEL_LENGUAJE = 42\n',
            'RELACIONES_DEL_LENGUAJE = fn_desconocida({"a"})\n',
            # Roto Y declarando: el archivo dice ser un emisor, así que no poder leerlo es un error.
            'RELACIONES_DEL_LENGUAJE = frozenset({"a"})\ndef broken(:\n',
        )
        for codigo in invalidas:
            with tempfile.TemporaryDirectory() as d:
                raiz = Path(d)
                (raiz / "tools").mkdir()
                (raiz / "tools" / "invalido.py").write_text(codigo, encoding="utf-8")
                with self.subTest(codigo=codigo), self.assertRaises(m.MedidaMalDeclarada):
                    m.relaciones_del_lenguaje_declaradas(raiz=raiz)

    def test_un_archivo_roto_que_no_declara_nada_no_es_asunto_del_lenguaje(self) -> None:
        """Un script a medio escribir en `tools/` no puede romper «¿esta medida es meta?».

        Sin el filtro previo, cualquier archivo con un error de sintaxis hacía fallar la derivación
        entera. El fallo ni siquiera se veía: quien hace la pregunta lo envolvía en un `except` y se
        quedaba con el conjunto vacío, y de ahí salían seis medidas L2 marcadas «SIN FIJAR».
        """
        import tempfile
        from pathlib import Path
        m = modulo_medida()

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "tools").mkdir()
            (raiz / "tools" / "emisor.py").write_text(
                'RELACIONES_DEL_LENGUAJE = frozenset({"buena"})\n', encoding="utf-8")
            (raiz / "tools" / "borrador_a_medio_escribir.py").write_text(
                'def sin_terminar(:\n', encoding="utf-8")
            self.assertEqual(m.relaciones_del_lenguaje_declaradas(raiz=raiz), frozenset({"buena"}))

    def test_derivacion_no_sigue_directorios_ni_archivos_symlink(self) -> None:
        import tempfile
        from pathlib import Path
        m = modulo_medida()

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            destino = raiz / "externo"
            destino.mkdir()
            (destino / "emisor.py").write_text(
                'RELACIONES_DEL_LENGUAJE = frozenset({"externa"})\n', encoding="utf-8")
            (raiz / "nucleo").symlink_to(destino, target_is_directory=True)
            (raiz / "tools").mkdir()

            self.assertEqual(m.relaciones_del_lenguaje_declaradas(raiz=raiz), frozenset())

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "tools").mkdir()
            destino = raiz / "emisor.py"
            destino.write_text(
                'RELACIONES_DEL_LENGUAJE = frozenset({"externa"})\n', encoding="utf-8")
            (raiz / "tools" / "emisor.py").symlink_to(destino)

            self.assertEqual(m.relaciones_del_lenguaje_declaradas(raiz=raiz), frozenset())

    def test_derivacion_soporta_anotaciones_de_tipo_y_operaciones(self) -> None:
        import tempfile
        from pathlib import Path
        m = modulo_medida()

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "tools").mkdir()
            (raiz / "tools" / "tipado.py").write_text(
                'RELACIONES_DEL_LENGUAJE: frozenset[str] = frozenset({"r1"}) | {"r2", "r3"}\n'
                'RELACIONES_DE_EXTRA = ["r4"]\n',
                encoding="utf-8")
            relaciones = m.relaciones_del_lenguaje_declaradas(raiz=raiz)
            self.assertEqual(relaciones, frozenset({"r1", "r2", "r3", "r4"}))


if __name__ == "__main__":
    unittest.main()
