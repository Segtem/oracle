"""Tests de la superficie infija de autoría."""

from __future__ import annotations

import json
import pathlib
import unittest
from pathlib import Path

from nucleo import caso as sintaxis_caso
from nucleo.caso import CasoMalDeclarado
from nucleo.medida import rutas_de_catalogo
from nucleo.macro import EXTENSIONES_DE_MACRO
from nucleo.medida import cargar_fuente_medida, ruta_de_medida
from tools import sintaxis

RAIZ = Path(__file__).resolve().parents[1]


class SintaxisInfijaTests(unittest.TestCase):
    def test_todas_las_medidas_del_catalogo_vuelven_exactas(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        # Contado, no escrito: un 29 a mano vence con cada medida nueva y el test empieza a
        # medir cuántas hay en vez de que todas vuelvan exactas, que es lo que dice medir.
        del_catalogo = len(rutas_de_catalogo(
            RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        self.assertEqual(informe["medidas"], del_catalogo)
        self.assertGreater(del_catalogo, 0)
        del_corpus = len(sintaxis_caso.rutas_de_corpus(RAIZ / "corpus"))
        self.assertEqual(informe["casos"], del_corpus)
        self.assertGreater(del_corpus, 0)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])
        self.assertLess(informe["puntuacion_superficie"], informe["puntuacion_json"])
        self.assertTrue(any(p.suffix == ".oracle" for p in sintaxis._rutas_catalogo(RAIZ)))

    def test_los_inventarios_de_catalogo_no_vuelven_a_rglob_json_a_mano(self) -> None:
        def bloque(ruta: Path, inicio: str, fin: str) -> str:
            texto = ruta.read_text(encoding="utf-8")
            return texto.split(inicio, 1)[1].split(fin, 1)[0]

        revisados = (
            (RAIZ / "nucleo" / "medida.py", "def rutas_de_catalogo", "def cargar_fuente_medida"),
            (RAIZ / "tools" / "sintaxis.py", "def _rutas_catalogo", "def _puntuacion"),
            (RAIZ / "tools" / "cifras.py", "def _medidas_universales", "def _lineas"),
            (RAIZ / "tools" / "estudio.py", "def catalogo_en_prosa", "def corpus_en_prosa"),
            (RAIZ / "tools" / "estudio.py", "def numeros", "    casos = "),
        )
        for ruta, inicio, fin in revisados:
            with self.subTest(ruta=ruta.name, inicio=inicio):
                codigo = bloque(ruta, inicio, fin)
                self.assertNotIn('rglob("*.json")', codigo)
                self.assertNotIn('glob("*/*.json")', codigo)

    def test_una_macro_se_relee_como_macro_y_no_como_expansion(self) -> None:
        # Por el LECTOR común, no por `json.loads`: la medida está guardada en la superficie y el
        # test habla de la superficie, no del formato en que quedó el archivo.
        datos = cargar_fuente_medida(ruta_de_medida("meta.donde_compone", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        superficie = sintaxis.imprimir(datos)

        self.assertTrue(superficie.startswith("ninguno meta.donde_compone:"))
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_una_medida_canonica_preserva_requiere_y_agrupar(self) -> None:
        datos = cargar_fuente_medida(
            ruta_de_medida("proceso.modulo_con_consumidor", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        releida = sintaxis.leer(sintaxis.imprimir(datos))

        self.assertEqual(releida, datos)
        self.assertEqual(releida[5], ["requiere", "importa"])
        self.assertEqual(releida[2][2][0], "agrupar")

    def test_imprimir_leer_es_idempotente_sobre_la_superficie_generada(self) -> None:
        datos = ["ninguno", "d.prueba", "pieza", "p",
                 ["y", ["==", ["campo", "p", "mal"], True],
                  [">", ["campo", "p", "n"], 2]],
                 "una razón", "NO ve otros campos"]
        texto = sintaxis.imprimir(datos)

        self.assertEqual(sintaxis.imprimir(sintaxis.leer(texto)), texto)

    def test_un_error_de_expresion_trae_posicion_y_esperado(self) -> None:
        texto = "\n".join([
            "ninguno d.rota:",
            "    de pieza p",
            "    donde p.mal ==",
            "    umbral <= 0 porque \"razón\"",
            "    alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 3)
        self.assertIn("se esperaba expresión", str(e.exception))

    def test_una_ruta_de_error_se_traduce_a_linea_columna_y_fragmento(self) -> None:
        from nucleo import algebra

        texto = "\n".join([
            "medida d.rota:",
            "    de pieza p",
            "    donde p.x > 0 y p.typo == 2",
            "    resumen contar(1)",
            "    umbral <= 0 porque \"razón\"",
            "    alcance \"NO ve otros campos\"",
        ])
        lectura = sintaxis.leer_con_mapa(texto)

        with self.assertRaises(algebra.ErrorDeAlgebra) as e:
            algebra.desde(lectura.datos[2], {"pieza": [{"x": 1}]})

        self.assertEqual(e.exception.ruta, "2.2.1.2")
        ubicacion = lectura.ubicacion(e.exception.ruta)
        self.assertEqual((ubicacion.linea, ubicacion.columna), (3, 28))

        fragmento = sintaxis.fragmento_de_error(e.exception, texto)
        self.assertIn("en `2.2.1.2`", fragmento)
        self.assertIn("   3 |     donde p.x > 0 y p.typo == 2", fragmento)
        self.assertTrue(fragmento.endswith("^"))

    def test_la_metamorfica_de_sintaxis_juzga_todo_el_catalogo(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_ida_y_vuelta(Proyecto(RAIZ))
        del_catalogo = len(rutas_de_catalogo(
            RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        self.assertEqual(len(filas), del_catalogo)
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        # La jueza se busca en el CATÁLOGO, no en el código de la herramienta: estuvo un rato
        # declarada adentro de `metamorficas.py` —consecuencia de una restricción de la tarea que
        # la escribió— y una medida que vive en Python no entra a la mutación ni al inventario de
        # puntos ciegos, que es justo lo que este proyecto le exige a todas las demás.
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_ida_y_vuelta", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        from nucleo.proyecto import macros_del_proyecto
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)

    def test_la_metamorfica_de_sintaxis_cubre_algebra(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto, macros_del_proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_cubre_algebra()
        self.assertGreater(len(filas), 0)
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_cubre_algebra", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)


class SintaxisDeCasosTests(unittest.TestCase):
    def _caso_base(self, evidencia=None) -> dict:
        return {
            "id": "999-caso-de-prueba",
            "fecha": "2026-08-25",
            "origen": {"repo": "test", "commit": "local"},
            "titulo": "Caso de prueba",
            "etiqueta": "verde_correcto",
            "sintoma": "Prosa con `backticks`, comillas \"dobles\" y coma, sin escapar.",
            "como_se_detecto": "observacion",
            "medida": "demo.mide",
            "evidencia": evidencia or {"hecho": [{"id": "a", "ok": True}]},
            "leccion": "La prosa vuelve igual.",
        }

    def test_todo_el_corpus_vuelve_exacto_en_la_superficie_de_casos(self) -> None:
        rutas = sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")
        self.assertGreater(len(rutas), 0)
        for ruta in rutas:
            with self.subTest(caso=ruta.relative_to(RAIZ)):
                datos = sintaxis_caso.cargar_fuente_caso(ruta)
                superficie = sintaxis_caso.imprimir(datos)
                releido = sintaxis_caso.leer(superficie)
                self.assertEqual(releido, datos)
                self.assertEqual(sintaxis_caso.imprimir(releido), superficie)

    def test_el_corpus_real_ejercita_los_dos_lectores(self) -> None:
        rutas = sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")
        self.assertEqual({r.suffix for r in rutas}, {".caso", ".json"})
        self.assertEqual(sum(1 for r in rutas if r.suffix == ".json"), 2)
        self.assertEqual(sum(1 for r in rutas if r.suffix == ".caso"), len(rutas) - 2)

    def test_la_metamorfica_de_casos_juzga_todo_el_corpus(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto, macros_del_proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_casos_ida_y_vuelta(Proyecto(RAIZ))
        self.assertEqual(len(filas), len(sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")))
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_casos_ida_y_vuelta", RAIZ / "catalogos",
                           *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)

    def test_la_metamorfica_de_casos_cubre_la_forma_del_caso(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto, macros_del_proyecto
        from tools import metamorficas

        candidatos = metamorficas._generar_casos_candidatos()
        self.assertGreaterEqual(len(candidatos), 5)
        self.assertTrue(any("vacia" in c["evidencia"] and c["evidencia"]["vacia"] == []
                            for c in candidatos))
        self.assertTrue(any(len(c["evidencia"]) == 3 for c in candidatos))
        self.assertTrue(any(c["medida"] is None and c["estado_sin_medida"] == "abierto"
                            for c in candidatos))
        self.assertTrue(any(any(isinstance(f, list) and f[0] == "clave"
                                for filas in c["evidencia"].values() for f in filas)
                            for c in candidatos))
        filas = metamorficas._sintaxis_casos_cubre_casos()
        self.assertEqual(len(filas), len(candidatos))
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_casos_cubre_casos", RAIZ / "catalogos",
                           *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)

    def test_una_relacion_heterogenea_usa_la_salida_de_escape(self) -> None:
        datos = self._caso_base({"rel": [{"a": 1}, {"b": "dos", "c": False}]})
        superficie = sintaxis_caso.imprimir(datos)

        self.assertIn("\n        rel:\n", superficie)
        self.assertIn('            fila {"a": 1}\n', superficie)
        self.assertIn('            fila {"b": "dos", "c": false}\n', superficie)
        self.assertEqual(sintaxis_caso.leer(superficie), datos)

    def test_una_relacion_presente_y_vacia_no_es_una_relacion_ausente(self) -> None:
        datos = self._caso_base({"presente": []})
        releido = sintaxis_caso.leer(sintaxis_caso.imprimir(datos))

        self.assertIn("presente", releido["evidencia"])
        self.assertEqual(releido["evidencia"]["presente"], [])
        self.assertNotIn("ausente", releido["evidencia"])

    def test_una_relacion_vacia_puede_conservar_clave_declarada(self) -> None:
        datos = self._caso_base({"pieza": [["clave", ["id"]]]})
        releido = sintaxis_caso.leer(sintaxis_caso.imprimir(datos))

        self.assertEqual(releido["evidencia"]["pieza"], [["clave", ["id"]]])

    def test_el_mismo_id_en_json_y_caso_es_error(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "corpus").mkdir()
            datos = self._caso_base()
            (raiz / "corpus" / "uno.json").write_text(
                json.dumps(datos, ensure_ascii=False), encoding="utf-8")
            (raiz / "corpus" / "dos.caso").write_text(
                sintaxis_caso.imprimir(datos), encoding="utf-8")

            with self.assertRaises(CasoMalDeclarado) as cm:
                sintaxis_caso.cargar_casos(raiz / "corpus")

        mensaje = str(cm.exception)
        self.assertIn("999-caso-de-prueba", mensaje)
        self.assertIn("uno.json", mensaje)
        self.assertIn("dos.caso", mensaje)

    def test_un_caso_mal_formado_denuncia_archivo_linea_columna_y_fragmento(self) -> None:
        import tempfile
        texto = "\n".join([
            "caso 999-roto:",
            '    fecha: "2026-08-25"',
            "    origen:",
            '        repo: "test"',
            '        commit: "local"',
            '    titulo: "Roto"',
            "    etiqueta: verde_correcto",
            "    sintoma:",
            "        falla",
            "    como_se_detecto: observacion",
            "    medida: demo.mide",
            "    evidencia:",
            "        hecho: id, ok",
            '            "a" true',
            "    leccion:",
            "        falla",
        ]) + "\n"
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "roto.caso"
            ruta.write_text(texto, encoding="utf-8")
            with self.assertRaises(CasoMalDeclarado) as cm:
                sintaxis_caso.cargar_fuente_caso(ruta)

        mensaje = str(cm.exception)
        self.assertIn("roto.caso", mensaje)
        self.assertIn("línea 14, columna", mensaje)
        self.assertIn("  14 |", mensaje)
        self.assertIn("^", mensaje)

    def test_las_herramientas_no_vuelven_a_rglob_json_sobre_corpus(self) -> None:
        revisadas = (
            RAIZ / "tools" / "aceptacion.py",
            RAIZ / "tools" / "cifras.py",
            RAIZ / "tools" / "corpus.py",
            RAIZ / "tools" / "estudio.py",
            RAIZ / "tools" / "medida.py",
            RAIZ / "tools" / "metamorficas.py",
            RAIZ / "tools" / "mutar.py",
            RAIZ / "tools" / "trazar.py",
        )
        for ruta in revisadas:
            with self.subTest(ruta=ruta.name):
                codigo = ruta.read_text(encoding="utf-8")
                self.assertNotIn('rglob("*.json")', codigo)
                self.assertNotIn('glob("*/*.json")', codigo)


class GramaticaDelIdTests(unittest.TestCase):
    """Un id es un nombre de archivo, y la gramática es UNA SOLA.

    Antes había dos: `ID_MEDIDA_RE` gobernaba la creación (`--nueva`) y la superficie aceptaba
    `\\S+`, cualquier cosa sin espacios. Así `tareas.vencida_sin_dueño` se leía sin una queja pero
    la herramienta se negaba a crearlo, y el catálogo podía guardar ids que el proyecto no sabe
    escribir. La razón del ASCII —dos nombres idénticos en pantalla con bytes distintos, NFC contra
    NFD— está escrita al lado de `ID_MEDIDA_RE`.
    """

    CUERPO = ('\n    de tarea t'
              '\n    donde t.vencida == true'
              '\n    umbral <= 0 porque "una tarea vencida sin dueño no la hace nadie"'
              '\n    alcance "ve el par vencida+sin-dueño. NO ve si quien la tiene puede resolverla"\n')

    def test_la_superficie_acepta_un_id_de_la_gramatica(self) -> None:
        datos = sintaxis.leer("ninguno tareas.vencida_sin_dueno:" + self.CUERPO)
        self.assertEqual(datos[1], "tareas.vencida_sin_dueno")

    def test_la_superficie_rechaza_un_id_fuera_de_la_gramatica(self) -> None:
        for malo in ("tareas.vencida_sin_dueño", "Tareas.mide", "sin_punto", "tareas..mide",
                     "tareas.mide-guion", "1tareas.mide"):
            with self.subTest(malo=malo):
                with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
                    sintaxis.leer(f"ninguno {malo}:" + self.CUERPO)
                self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_el_almacenamiento_no_puede_contrabandear_un_id_que_la_superficie_rechaza(self) -> None:
        """Si sólo lo comprobara la superficie, escribir el JSON a mano saltearía la gramática."""
        from nucleo.medida import Medida, MedidaMalDeclarada
        datos = ["medida", "tareas.vencida_sin_dueño",
                 ["desde", ["de", "tarea", "t"], ["donde", ["==", ["campo", "t", "v"], True]]],
                 ["resumen", "contar", 1],
                 ["umbral", "<=", 0, "una tarea vencida sin dueño no la hace nadie"],
                 ["alcance", "ve el par vencida+sin-dueño"]]
        with self.assertRaises(MedidaMalDeclarada) as cm:
            Medida.de_datos(datos)
        self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_dos_ids_que_se_dibujan_iguales_son_ids_distintos(self) -> None:
        """El peligro concreto que cierra la gramática, demostrado y no afirmado."""
        import unicodedata
        nfc, nfd = "dueño", unicodedata.normalize("NFD", "dueño")
        self.assertNotEqual(nfc, nfd)
        self.assertNotEqual(nfc.encode("utf-8"), nfd.encode("utf-8"))
        from nucleo.proyecto import ID_MEDIDA_RE
        for forma in (nfc, nfd):
            self.assertIsNone(ID_MEDIDA_RE.fullmatch(f"tareas.vencida_sin_{forma}"))


class GramaticaDelIdDeCasoTests(unittest.TestCase):
    def _texto(self, cid: str) -> str:
        datos = {
            "id": "999-caso-valido",
            "fecha": "2026-08-25",
            "origen": {"repo": "test", "commit": "local"},
            "titulo": "Caso valido",
            "etiqueta": "verde_correcto",
            "sintoma": "Prueba",
            "como_se_detecto": "observacion",
            "medida": "demo.mide",
            "evidencia": {"hecho": [{"id": "a"}]},
            "leccion": "Prueba",
        }
        datos["id"] = cid
        return sintaxis_caso.imprimir(datos)

    def test_la_superficie_acepta_un_id_de_caso_de_la_gramatica(self) -> None:
        self.assertEqual(sintaxis_caso.leer(self._texto("999-caso-valido"))["id"],
                         "999-caso-valido")

    def test_la_superficie_rechaza_un_id_de_caso_fuera_de_la_gramatica(self) -> None:
        cuerpo = self._texto("999-caso-valido").replace("999-caso-valido", "999-caso-con-dueno")
        for malo in ("999-caso-con-dueño", "99-corto", "999_Caso", "999-", "abc-caso"):
            with self.subTest(malo=malo):
                texto = cuerpo.replace("999-caso-con-dueno", malo)
                with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
                    sintaxis_caso.leer(texto)
                self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_el_json_no_puede_contrabandear_un_id_de_caso_invalido(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "999-caso-con-dueno.json"
            ruta.write_text(json.dumps({"id": "999-caso-con-dueño"}, ensure_ascii=False),
                            encoding="utf-8")
            with self.assertRaises(CasoMalDeclarado) as cm:
                sintaxis_caso.cargar_fuente_caso(ruta)
        self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_la_gramatica_vive_junto_a_la_de_medida(self) -> None:
        from nucleo.proyecto import ID_CASO_RE, ID_MEDIDA_RE
        self.assertIsNotNone(ID_MEDIDA_RE.fullmatch("dominio.nombre"))
        self.assertIsNotNone(ID_CASO_RE.fullmatch("999-caso-valido"))
        self.assertIsNone(ID_CASO_RE.fullmatch("999-caso-con-dueño"))


class MedidaNuevaNaceEnLaSuperficieTests(unittest.TestCase):
    def test_el_destino_de_una_medida_nueva_es_la_superficie(self) -> None:
        """El formato en el que se autoriza a alguien a escribir es el primer mensaje del lenguaje."""
        import tempfile
        from nucleo.proyecto import EXTENSION_DE_AUTORIA, Proyecto, ruta_de_medida_nueva
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "catalogos").mkdir()
            destino = ruta_de_medida_nueva(Proyecto(raiz), "tareas.mide")
            self.assertEqual(destino.suffix, EXTENSION_DE_AUTORIA)

    def test_la_plantilla_que_se_entrega_se_lee_y_carga(self) -> None:
        """Una plantilla que no parsea manda a la primera persona que la usa contra la pared."""
        from nucleo.medida import Medida
        from tools.medida import PLANTILLA
        datos = sintaxis.leer(PLANTILLA.format(mid="tareas.mide"))
        self.assertEqual(Medida.de_datos(datos).id, "tareas.mide")


class CasoNuevoNaceEnLaSuperficieTests(unittest.TestCase):
    def test_la_plantilla_de_caso_que_se_entrega_se_lee_y_carga(self) -> None:
        import tempfile
        from tools.corpus import PLANTILLA

        texto = PLANTILLA.format(cid="999-caso-nuevo")
        self.assertEqual(sintaxis_caso.leer(texto)["id"], "999-caso-nuevo")
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "999-caso-nuevo.caso"
            ruta.write_text(texto, encoding="utf-8")
            self.assertEqual(sintaxis_caso.cargar_fuente_caso(ruta)["id"], "999-caso-nuevo")

    def test_el_andamio_crea_un_caso_en_superficie(self) -> None:
        import io
        import tempfile
        from contextlib import redirect_stdout
        from nucleo.proyecto import Proyecto
        from tools import corpus

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "catalogos").mkdir()
            (raiz / "corpus").mkdir()
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = corpus.main(["--proyecto", str(raiz), "--nuevo", "meta/999-caso-nuevo"])
            destino = raiz / "corpus" / "meta" / "999-caso-nuevo.caso"

            self.assertEqual(codigo, 0, salida.getvalue())
            self.assertTrue(destino.exists())
            self.assertEqual(corpus.ruta_de_caso_nuevo(Proyecto(raiz), "meta/999-caso-nuevo"),
                             destino)
            self.assertEqual(sintaxis_caso.cargar_fuente_caso(destino)["id"],
                             "999-caso-nuevo")


class DocumentacionVerificadaTests(unittest.TestCase):
    """El tutorial afirma que sus ejemplos están verificados contra el código vigente.

    Hasta hoy esa afirmación la sostenía la palabra de quien escribió el documento. Un ejemplo que
    no compila es una afirmación no ejercitada, que es justo lo que el repositorio no acepta en
    ningún otro lado.
    """

    def test_todo_bloque_oracle_de_la_documentacion_lee_y_vuelve_canonico(self) -> None:
        informe = sintaxis.verificar_documentos(RAIZ)
        self.assertEqual(informe["fallas"], [])
        self.assertGreater(informe["ejecutables"], 0)

    def test_un_documento_declarado_que_no_esta_es_un_error(self) -> None:
        """Si faltara en silencio, sacar un documento de la verificación sería renombrarlo."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            informe = sintaxis.verificar_documentos(Path(d))
            self.assertEqual(len(informe["fallas"]), len(sintaxis.DOCUMENTOS_CON_SUPERFICIE))

    def test_un_bloque_roto_se_denuncia_con_documento_y_linea(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
                (raiz / nombre).write_text("texto\n\n```oracle\nmedida x:\n    de\n```\n",
                                           encoding="utf-8")
            informe = sintaxis.verificar_documentos(raiz)
            self.assertEqual(len(informe["fallas"]), len(sintaxis.DOCUMENTOS_CON_SUPERFICIE))
            self.assertIn(":3:", informe["fallas"][0])

    def test_un_bloque_que_lee_pero_no_es_canonico_tambien_falla(self) -> None:
        """Parsear no alcanza: el documento tiene que mostrar lo que la herramienta imprime."""
        import tempfile
        # `t.vencida==true` sin espacios alrededor del comparador: lee perfecto, pero el impresor
        # pone los espacios. Un documento así enseña una forma que la herramienta no produce.
        cuerpo = ("ninguno tareas.mide:\n"
                  "    de tarea t\n"
                  "    donde t.vencida==true\n"
                  '    umbral <= 0 porque "una tarea vencida sin dueño no la hace nadie"\n'
                  '    alcance "ve el par vencida+sin-dueño"\n')
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
                (raiz / nombre).write_text(f"```oracle\n{cuerpo}```\n", encoding="utf-8")
            fallas = sintaxis.verificar_documentos(raiz)["fallas"]
            self.assertTrue(fallas)
            self.assertIn("canónica", fallas[0])


class DefmacroSurfaceTests(unittest.TestCase):
    """La superficie cubre la otra mitad del lenguaje: las macros, no sólo las medidas."""

    def test_las_tres_macros_del_nucleo_vuelven_exactas(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        del_macros = len([p for p in (RAIZ / "nucleo" / "macros").iterdir()
                          if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()])
        self.assertEqual(informe["macros"], del_macros)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])

    def test_cada_macro_del_nucleo_se_lee_igual_al_archivo(self) -> None:
        for ruta in sorted(p for p in (RAIZ / "nucleo" / "macros").iterdir()
                           if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()):
            with self.subTest(macro=ruta.stem):
                texto = ruta.read_text(encoding="utf-8")
                datos = (sintaxis.leer(texto) if ruta.suffix == ".oracle"
                         else json.loads(texto))
                superficie = sintaxis.imprimir(datos)
                self.assertTrue(superficie.startswith(f"defmacro {ruta.stem}("))
                self.assertEqual(sintaxis.leer(superficie), datos)
                self.assertEqual(sintaxis.imprimir(sintaxis.leer(superficie)), superficie)

    def test_una_macro_con_huecos_se_imprime_como_defmacro(self) -> None:
        datos = ["defmacro", "todos-cumplen",
                 ["id", "relacion", "alias", "predicado", "porque", "alcance"],
                 [],
                 ["medida", ["$", "id"],
                  ["desde", ["de", ["$", "relacion"], ["$", "alias"]],
                   ["donde", ["no", ["$", "predicado"]]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, ["$", "porque"]],
                  ["alcance", ["$", "alcance"]]]]
        superficie = sintaxis.imprimir(datos)

        self.assertTrue(superficie.startswith(
            "defmacro todos-cumplen(id, relacion, alias, predicado, porque, alcance):"))
        self.assertIn("\n    medida $id:\n", superficie)
        self.assertIn("\n        de $relacion $alias\n", superficie)
        self.assertIn("\n        donde no $predicado\n", superficie)
        self.assertIn("\n        umbral <= 0 porque $porque\n", superficie)
        self.assertIn("\n        alcance $alcance\n", superficie)
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_una_macro_con_guarda_vuelve_exacta(self) -> None:
        datos = ["defmacro", "propia",
                 ["id", "otro"],
                 [["guarda", ["!=", ["$", "id"], ["$", "otro"]], "distintos"]],
                 ["medida", ["$", "id"],
                  ["desde", ["de", "rel", ["$", "otro"]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, ["$", "id"]],
                  ["alcance", ["$", "otro"]]]]
        superficie = sintaxis.imprimir(datos)

        self.assertIn("\n    guarda $id != $otro \"distintos\"\n", superficie)
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_la_aridad_de_defmacro_es_cinco(self) -> None:
        for datos in (["defmacro", "p", ["id"], []],
                      ["defmacro", "p", ["id"], [], ["medida"], "de+"],
                      ["no-defmacro", "p", ["id"], [], ["medida"]]):
            with self.subTest(datos=datos):
                with self.assertRaises(ValueError):
                    sintaxis.imprimir(datos)

    def test_una_guarda_mal_formada_trae_linea_y_columna(self) -> None:
        texto = "\n".join([
            "defmacro mala(id):",
            "    guarda $id != 1",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == true",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 2)
        self.assertIn("mensaje de la guarda", str(e.exception))

    def test_un_parametro_que_la_plantilla_nunca_usa_no_carga(self) -> None:
        texto = "\n".join([
            "defmacro propia(id, sobra):",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == true",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 1)
        self.assertIn("nunca lo usa", str(e.exception))

    def test_un_hueco_de_parametro_no_declarado_no_carga(self) -> None:
        texto = "\n".join([
            "defmacro propia(id):",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == $inventado",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 4)
        self.assertIn("no es un parámetro", str(e.exception))

    def test_un_hueco_dentro_de_una_cadena_no_cuenta_como_hueco(self) -> None:
        """Un `$x` adentro del mensaje de una guarda es texto, no un hueco: no se lo exige como
        parámetro ni se lo cuenta como usado."""
        texto = "\n".join([
            "defmacro propia(id):",
            "    guarda $id != 1 \"usá $otro si querés\"",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == true",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])
        datos = sintaxis.leer(texto)
        self.assertEqual(datos[2], ["id"])
        self.assertEqual(datos[3][0][2], "usá $otro si querés")


class MacrosEnLaSuperficieTests(unittest.TestCase):
    """La biblioteca estándar del lenguaje también se guarda en la superficie."""

    def test_la_biblioteca_estandar_esta_escrita_en_la_superficie(self) -> None:
        from nucleo.macro import macros_base
        base = pathlib.Path(RAIZ / "nucleo" / "macros")
        self.assertTrue(any(p.suffix == ".oracle" for p in base.iterdir()))
        self.assertEqual(sorted(macros_base()), ["ninguno", "ninguno-par", "peor"])

    def test_el_mismo_nombre_en_los_dos_formatos_es_un_error(self) -> None:
        """No gana ninguno: un ganador silencioso es una divergencia esperando."""
        import tempfile
        from nucleo.macro import MacroMalDeclarada, cargar_macros
        cuerpo = (RAIZ / "nucleo" / "macros" / "ninguno.oracle").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:
            raiz = pathlib.Path(d)
            (raiz / "ninguno.oracle").write_text(cuerpo, encoding="utf-8")
            (raiz / "ninguno.json").write_text(
                json.dumps(sintaxis.leer(cuerpo), ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(MacroMalDeclarada):
                cargar_macros(raiz)

    def test_el_numerador_no_pierde_las_macros_al_cambiarles_el_formato(self) -> None:
        """Bajar la proporción renombrando archivos es sastreo con otra ropa.

        Cuando las tres macros base pasaron a `.oracle`, el `glob("*.json")` a mano de `cifras.py`
        las dejó caer del numerador sin una queja. El inventario de formatos es UNO.
        """
        from nucleo.macro import EXTENSIONES_DE_MACRO
        from tools import cifras
        contadas = [p for p in cifras._lenguaje() if p.parent.name == "macros"]
        en_disco = [p for p in (RAIZ / "nucleo" / "macros").iterdir()
                    if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()]
        self.assertEqual(len(contadas), len(en_disco))
        self.assertGreater(len(contadas), 0)


class ElCatalogoRealEjercitaLosDosLectoresTests(unittest.TestCase):
    """Un lector que sólo ejercitan los tests es un lector a medio probar.

    El catálogo universal está escrito en la superficie —es la forma en que se autoriza a escribir
    y tiene que ser la forma en que está escrito lo que se publica— pero DOS medidas se dejan a
    propósito en `.json`. Si todas migraran, el camino `.json` de `cargar_catalogo` dejaría de
    correrse en el catálogo real y sólo lo tocarían los temporales de esta suite; el día que se
    rompiera, se enteraría un consumidor —Jam y LyraGASP guardan sus medidas en `.json`— y no acá.
    """

    def _rutas(self):
        from nucleo.medida import rutas_de_catalogo
        return rutas_de_catalogo(RAIZ / "catalogos",
                                 *sorted((RAIZ / "perfiles").glob("*/catalogos")))

    def test_el_catalogo_publica_medidas_en_los_dos_formatos(self) -> None:
        sufijos = {r.suffix for r in self._rutas()}
        self.assertEqual(sufijos, {".oracle", ".json"})

    def test_la_superficie_es_la_forma_dominante_y_no_una_excepcion(self) -> None:
        """Si quedara una sola en superficie, la afirmación «el catálogo está escrito en el
        lenguaje» sería falsa y nada la contradiría."""
        rutas = self._rutas()
        en_superficie = [r for r in rutas if r.suffix == ".oracle"]
        self.assertGreater(len(en_superficie), len(rutas) // 2)

    def test_las_dos_que_quedan_en_json_cargan_por_el_mismo_camino(self) -> None:
        from nucleo.medida import cargar_fuente_medida
        for ruta in (r for r in self._rutas() if r.suffix == ".json"):
            with self.subTest(medida=ruta.stem):
                self.assertEqual(cargar_fuente_medida(ruta)[1], ruta.stem)


class VersionDeLaSuperficieTests(unittest.TestCase):
    """La superficie declara contra qué sintaxis se escribió, y cargarla es fail-closed.

    Es el hueco que el álgebra ya cerró, abierto un nivel más arriba: un `.oracle` es un formato
    GUARDADO, y hasta hoy nada le decía a nadie si un archivo escrito ayer sigue significando lo
    mismo. La regla de qué sube cada parte del número está en `ESPECIFICACION.md` §0.
    """

    CUERPO = (
        'ninguno d.prueba:\n'
        '    de pieza p\n'
        '    donde p.x == true\n'
        '    umbral <= 0 porque "razón"\n'
        '    alcance "NO ve otros campos"\n'
    )

    def test_sin_declarar_no_hay_version(self) -> None:
        self.assertIsNone(sintaxis.leer_con_mapa(self.CUERPO).version)

    def test_el_lector_devuelve_la_version_declarada(self) -> None:
        lectura = sintaxis.leer_con_mapa("sintaxis 0.1\n" + self.CUERPO)
        self.assertEqual(lectura.version, "0.1")
        self.assertEqual(lectura.datos, sintaxis.leer(self.CUERPO))

    def test_la_version_es_superficie_no_un_comentario_pegado_arriba(self) -> None:
        comentado = sintaxis.leer_con_mapa("# sintaxis 0.1\n" + self.CUERPO)
        self.assertIsNone(comentado.version)
        declarado = sintaxis.leer_con_mapa("sintaxis 0.1\n" + self.CUERPO)
        self.assertEqual(declarado.version, "0.1")

    def test_una_version_mal_formada_falla_cerrado(self) -> None:
        for mala in ("basura", "0", "0.3.1", "a.b", "01.2", "-1.0"):
            with self.subTest(mala=mala):
                with self.assertRaises(sintaxis.ErrorSintaxis) as e:
                    sintaxis.leer(f"sintaxis {mala}\n" + self.CUERPO)
                self.assertIn("MAYOR.MENOR", str(e.exception))

    def _cargar(self, declarada):
        import tempfile
        from nucleo.medida import cargar
        prefijo = f"sintaxis {declarada}\n" if declarada is not None else ""
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "d.prueba.oracle"
            ruta.write_text(prefijo + self.CUERPO, encoding="utf-8")
            return cargar(ruta)

    def test_sin_declarar_la_misma_y_una_menor_vieja_cargan(self) -> None:
        self.assertEqual(self._cargar(None).id, "d.prueba")
        self.assertEqual(self._cargar("0.1").id, "d.prueba")
        self.assertEqual(self._cargar("0.0").id, "d.prueba")

    def test_una_menor_futura_y_una_mayor_no_cargan_diciendo_las_dos(self) -> None:
        import tempfile
        from nucleo.medida import MedidaMalDeclarada, cargar
        for declarada in ("0.2", "1.0"):
            with self.subTest(declarada=declarada), tempfile.TemporaryDirectory() as d:
                ruta = Path(d) / "d.prueba.oracle"
                ruta.write_text(f"sintaxis {declarada}\n" + self.CUERPO, encoding="utf-8")
                with self.assertRaises(MedidaMalDeclarada) as ctx:
                    cargar(ruta)
                self.assertIn(declarada, str(ctx.exception))
                self.assertIn("0.1", str(ctx.exception))

    def test_ningun_archivo_existente_tuvo_que_declarar_version(self) -> None:
        """Poner versión a la superficie no puede obligar a tocar un archivo ya escrito.

        Contado, no escrito: la versión anterior de este test fijaba «34» a mano y se cayó con la
        primera medida nueva —por el conteo, no por lo que dice medir—. Es el mismo error que tenía
        `--verificar` con su `== 29`, y en este repositorio ya tiene nombre.
        """
        from nucleo.macro import cargar_macros

        en_superficie = [r for r in sintaxis._rutas_catalogo(RAIZ) if r.suffix == ".oracle"]
        self.assertTrue(en_superficie)
        sin_declarar = 0
        for ruta in en_superficie + sintaxis._rutas_macros(RAIZ):
            texto = ruta.read_text(encoding="utf-8")
            if not texto.startswith("sintaxis "):
                sin_declarar += 1
                cargar_fuente_medida(ruta) if ruta in en_superficie else None
        self.assertEqual(sin_declarar, len(en_superficie) + len(sintaxis._rutas_macros(RAIZ)),
                         "algún archivo del árbol quedó obligado a declarar versión")
        self.assertEqual(len(cargar_macros(RAIZ / "nucleo" / "macros")),
                         len(sintaxis._rutas_macros(RAIZ)))

    def test_el_verificador_sigue_en_verde_sobre_todo_lo_que_hay(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        docs = sintaxis.verificar_documentos(RAIZ)
        self.assertEqual(informe["medidas"], len(sintaxis._rutas_catalogo(RAIZ)))
        self.assertEqual(informe["macros"], len(sintaxis._rutas_macros(RAIZ)))
        self.assertEqual(informe["casos"], len(sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")))
        self.assertGreater(docs["ejecutables"], 0)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])
        self.assertEqual(docs["fallas"], [])


class NingunaEntradaEsFailOpenTests(unittest.TestCase):
    """Todas las puertas juzgan la versión, no sólo las que cargan un catálogo.

    `leer()` es puro y no juzga —es la decisión correcta y está defendida en su docstring—, pero
    `tools/sintaxis.py --leer` también carga un archivo, y traducía en silencio, con exit 0, una
    superficie escrita contra una sintaxis que este núcleo no implementa. Una salida fail-open al
    lado de dos fail-closed es peor que no tener ninguna: enseña a confiar.
    """

    FUTURO = ('sintaxis 9.0\n'
              'ninguno tareas.mide:\n'
              '    de tarea t\n'
              '    donde t.vencida == true\n'
              '    umbral <= 0 porque "una tarea vencida sin dueño no la hace nadie"\n'
              '    alcance "ve el par vencida+sin-dueño y nada más"\n')

    def _archivo(self, d, nombre="m.oracle"):
        ruta = pathlib.Path(d) / nombre
        ruta.write_text(self.FUTURO, encoding="utf-8")
        return ruta

    def test_el_cli_leer_rechaza_una_sintaxis_que_este_nucleo_no_implementa(self) -> None:
        import io
        import tempfile
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = sintaxis.main(["--leer", str(self._archivo(d))])
            self.assertEqual(codigo, 1)
            self.assertIn("9.0", salida.getvalue())
            self.assertNotIn('"ninguno"', salida.getvalue())

    def test_las_tres_puertas_coinciden(self) -> None:
        """El catálogo, las macros y el CLI dan el mismo veredicto sobre el mismo archivo."""
        import io
        import tempfile
        from contextlib import redirect_stdout

        from nucleo.macro import MacroMalDeclarada, cargar_macros
        from nucleo.medida import MedidaMalDeclarada, cargar_fuente_medida
        with tempfile.TemporaryDirectory() as d:
            ruta = self._archivo(d)
            with self.assertRaises(MedidaMalDeclarada):
                cargar_fuente_medida(ruta)
            with self.assertRaises(MacroMalDeclarada):
                cargar_macros(pathlib.Path(d))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(sintaxis.main(["--leer", str(ruta)]), 1)


class LosBloquesDeCasoDeLaDocumentacionTambienSeVerificanTests(unittest.TestCase):
    """Cuando entró la superficie de casos, sus ejemplos quedaron fuera del verificador.

    `verificar_documentos` miraba dos documentos y una sola superficie. Los ejemplos de `.caso`
    aparecieron en cuatro documentos y ninguno pasaba por el lector: volvían a ser una afirmación
    sostenida por la palabra de quien la escribió, que es lo que este mecanismo vino a terminar.
    """

    def test_se_verifican_las_dos_superficies(self) -> None:
        import re
        de_caso = 0
        for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
            texto = (RAIZ / nombre).read_text(encoding="utf-8")
            de_caso += sum(1 for m in sintaxis.BLOQUE_RE.finditer(texto)
                           if m.group(1) == "caso" and not m.group(2))
        self.assertGreater(de_caso, 0, "ningún documento muestra un caso ejecutable")
        self.assertEqual(sintaxis.verificar_documentos(RAIZ)["fallas"], [])

    def test_un_bloque_de_caso_roto_se_denuncia(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
                (raiz / nombre).write_text("```caso\ncaso 999-roto:\n    fecha\n```\n",
                                           encoding="utf-8")
            fallas = sintaxis.verificar_documentos(raiz)["fallas"]
            self.assertEqual(len(fallas), len(sintaxis.DOCUMENTOS_CON_SUPERFICIE))
            self.assertIn("no lee", fallas[0])


class ElErrorDelLenguajeSeManipulaComoUnErrorTests(unittest.TestCase):
    """`ErrorSintaxis` es un `dataclass(frozen=True)`, y eso congelaba de más.

    Un dataclass congelado reemplaza `__setattr__` por uno que rechaza TODO, incluidos los dunder
    que el intérprete y las herramientas de traza escriben sobre cualquier excepción. CPython los
    escribe por la API de C al levantar —por eso un `raise` simple andaba— pero cualquier código
    Python que re-lance o encadene el error se estrellaba con `FrozenInstanceError`.

    Lo encontró la mutación de código, no una persona: **51 de 193 mutantes** de `nucleo/caso.py` no
    salieron ni muertos ni vivos, salieron `error_arnes` con
    `FrozenInstanceError: cannot assign to field '__traceback__'`. Un error del arnés no es una
    muerte —caso `017` del corpus—, así que esos 51 no medían nada y la ronda quedaba inconclusa.
    """

    def test_se_le_puede_escribir_la_maquinaria_de_excepciones(self) -> None:
        for atributo in ("__traceback__", "__cause__", "__context__"):
            with self.subTest(atributo=atributo):
                e = sintaxis.ErrorSintaxis(1, 1, "x")
                setattr(e, atributo, None)
                self.assertIsNone(getattr(e, atributo))

    def test_los_campos_del_error_siguen_congelados(self) -> None:
        """La inmutabilidad que se quiere es la de línea, columna y qué se esperaba."""
        import dataclasses
        e = sintaxis.ErrorSintaxis(1, 1, "x")
        for campo in ("linea", "columna", "esperado"):
            with self.subTest(campo=campo):
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    setattr(e, campo, 99)

    def test_se_puede_encadenar_y_relanzar_desde_python(self) -> None:
        """El camino exacto que el arnés rompía: atrapar, encadenar y volver a levantar."""
        import traceback
        try:
            try:
                raise sintaxis.ErrorSintaxis(3, 7, "adentro")
            except sintaxis.ErrorSintaxis as interno:
                raise sintaxis.ErrorSintaxis(1, 1, "afuera") from interno
        except sintaxis.ErrorSintaxis as e:
            texto = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.assertIn("adentro", texto)
            self.assertIn("afuera", texto)


if __name__ == "__main__":
    unittest.main()
