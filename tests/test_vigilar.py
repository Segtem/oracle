"""Contrato pequeño y prioritario del bucle vivo de `oracle medida probar`."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from nucleo.proyecto import Proyecto
from nucleo.medida import MedidaMalDeclarada
from nucleo.proyecto import EscalaresInvalidas, EscalaresNoConfiables
from tools import cli, medida


class _SalidaDiferida(io.StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.visible = ""

    def flush(self) -> None:
        self.visible = self.getvalue()
        super().flush()


def _proyecto(raiz: Path) -> tuple[Proyecto, Path]:
    for nombre in ("catalogos", "corpus", "diferencial"):
        (raiz / nombre).mkdir()
    (raiz / "oracle.json").write_text(json.dumps({
        "esquema": "oracle.proyecto/v1",
        "catalogo_base": True,
        "perfiles": [],
    }), encoding="utf-8")
    ruta = raiz / "catalogos" / "demo" / "demo.alto.oracle"
    ruta.parent.mkdir()
    ruta.write_text(
        "ninguno demo.alto:\n"
        "    de pieza p\n"
        "    donde p.alto > 400.0\n"
        '    umbral <= 0 segun contrato porque "cuatro metros es el techo"\n'
        '    ambito universal\n'
        '    alcance "mira el alto declarado. NO mira la malla"\n',
        encoding="utf-8",
    )
    return Proyecto(raiz), ruta


class MedidaMutantesDePresentacionTests(unittest.TestCase):
    """Fija bordes del CLI porque un diagnóstico impreciso induce una reparación equivocada."""

    @staticmethod
    def _callado(fn, *args, **kwargs):
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = fn(*args, **kwargs)
        return rc, salida.getvalue()

    @staticmethod
    def _veredicto(ok: bool, nombre: str = "caso"):
        return SimpleNamespace(
            ok=ok,
            linea=lambda: f"resultado de {nombre}",
            valor=1,
            umbral="<= 0",
            sin_evidencia=None,
            testigos=[],
            alcance="sólo mira la evidencia declarada",
        )

    def test_relaciones_propaga_el_error_y_limita_los_origenes(self) -> None:
        """El inventario no debe aparentar éxito ante evidencia ilegible ni convertir una muestra
        de tres orígenes en una lista potencialmente enorme."""
        with mock.patch.object(medida, "inventario_de_relaciones", side_effect=ValueError("rota")):
            rc, salida = self._callado(medida.relaciones, object())
        self.assertEqual(rc, 1)
        self.assertIn("no se pudo inventariar", salida)

        campos = {"pieza": {"alto": {"float"}}}
        dondes = {"pieza": {"d", "c", "b", "a"}}
        with mock.patch.object(medida, "inventario_de_relaciones", return_value=(campos, dondes)):
            rc, salida = self._callado(medida.relaciones, object())
        self.assertEqual(rc, 0)
        self.assertIn("aparece en: a, b, c", salida)
        self.assertNotIn("a, b, c, d", salida)

    def test_escalares_distingue_aridades_y_no_inventa_omisiones(self) -> None:
        """Una firma incorrecta enseña a escribir llamadas inválidas; el aviso de código externo
        sólo corresponde cuando realmente se decidió no ejecutarlo."""
        def variadica():
            """Acepta argumentos desde uno."""

        def fija():
            """Acepta exactamente dos argumentos."""

        variadica.aridad_min = 1
        variadica.aridad_max = None
        variadica.unidad = ""
        fija.aridad_min = fija.aridad_max = 2
        fija.unidad = "cm"
        proy = SimpleNamespace(raiz=Path("/proyecto"))
        with mock.patch.object(medida, "ESCALARES", {"variadica": variadica, "fija": fija}):
            rc, salida = self._callado(medida.escalares, proy)
        self.assertEqual(rc, 0)
        self.assertIn("variadica/1+", salida)
        self.assertIn("fija/2 → cm", salida)
        self.assertNotIn("no se ejecutó", salida)

    def test_nueva_crea_padres_y_tolera_un_directorio_existente(self) -> None:
        """Crear una medida debe funcionar tanto en un dominio nuevo como en uno ya abierto; son
        los dos sentidos independientes de `parents` y `exist_ok`."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            nueva = base / "grupo-nuevo" / "dominio-nuevo" / "demo.uno.oracle"
            with mock.patch.object(medida, "ruta_de_medida_nueva", return_value=nueva):
                rc_nueva, _ = self._callado(medida.nueva, SimpleNamespace(raiz=base), "demo.uno")
            self.assertEqual(rc_nueva, 0)
            self.assertTrue(nueva.is_file())

            existente = base / "dominio-existente" / "demo.dos.oracle"
            existente.parent.mkdir()
            with mock.patch.object(medida, "ruta_de_medida_nueva", return_value=existente):
                rc_existente, _ = self._callado(
                    medida.nueva, SimpleNamespace(raiz=base), "demo.dos")
            self.assertEqual(rc_existente, 0)
            self.assertTrue(existente.is_file())

    def test_nueva_rechaza_id_y_destino_repetido_con_uno(self) -> None:
        """Los dos rechazos son fallos del comando; devolver éxito haría que un script continúe
        después de no haber creado el archivo solicitado."""
        with mock.patch.object(
                medida, "ruta_de_medida_nueva", side_effect=medida.ProyectoInvalido("mal id")):
            rc_id, _ = self._callado(medida.nueva, object(), "mal")
        self.assertEqual(rc_id, 1)

        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "repetida.oracle"
            destino.write_text("ya estaba", encoding="utf-8")
            with mock.patch.object(medida, "ruta_de_medida_nueva", return_value=destino):
                rc_repetida, _ = self._callado(
                    medida.nueva, SimpleNamespace(raiz=Path(td)), "demo.repetida")
        self.assertEqual(rc_repetida, 1)

    def test_expandir_distingue_macro_y_forma_canonica(self) -> None:
        """Llamar canónica a una macro confunde la representación editable con la expansión que
        se está mostrando; una lista mínima además debe diagnosticarse sin acceder fuera de ella."""
        falsa = mock.Mock()
        falsa.a_datos.return_value = ["medida", "á.demo"]
        for datos, es_macro, esperado, ausente in (
                (["medida"], False, "«?» ya está", None),
                (["medida", "demo.id"], False, "«demo.id» ya está", None),
                (["ninguno", "demo.id"], True, '"medida"', "ya está en forma canónica")):
            with (self.subTest(datos=datos),
                  mock.patch.object(medida, "cargar_fuente_medida", return_value=datos),
                  mock.patch("nucleo.macro.es_macro", return_value=es_macro),
                  mock.patch.object(medida.Medida, "de_datos", return_value=falsa)):
                rc, salida = self._callado(medida.expandir_archivo, Path("medida.oracle"))
            self.assertEqual(rc, 0)
            self.assertIn(esperado, salida)
            if ausente:
                self.assertNotIn(ausente, salida)
        self.assertIn("á.demo", salida)
        self.assertNotIn("\\u00e1", salida)
        self.assertIn('\n "á.demo"\n', salida)

    def _revisar_con(self, resultados):
        m = mock.Mock(id="demo.m", op="<=", limite=0, segun="contrato",
                      porque="defensa", alcance="no mira otras relaciones")
        m.evaluar.side_effect = resultados
        datos = ["medida", "demo.m"]
        evidencias = [(f"origen-{i}", {}) for i in range(len(resultados))]
        parches = (
            mock.patch.object(medida, "macros_del_proyecto", return_value={}),
            mock.patch.object(medida, "cargar_fuente_medida", return_value=datos),
            mock.patch.object(medida.Medida, "de_datos", return_value=m),
            mock.patch.object(medida, "alcance_derivado", return_value=[]),
            mock.patch.object(medida, "_evidencias", return_value=evidencias),
        )
        with parches[0], parches[1], parches[2], parches[3], parches[4] as cargar:
            rc, salida = self._callado(medida.revisar, object(), Path("demo.oracle"))
        return rc, salida, cargar

    def test_revisar_cuenta_polaridades_errores_y_dos_ejemplos(self) -> None:
        """La revisión orienta con conteos y con una muestra acotada: perder una unidad, el primer
        error o el límite de dos cambia el diagnóstico que recibe quien escribió la medida."""
        resultados = [
            self._veredicto(False, "rojo-0"),
            self._veredicto(False, "rojo-1"),
            self._veredicto(False, "rojo-2"),
            self._veredicto(True, "verde"),
            ValueError("primero"),
            TypeError("segundo"),
        ]
        rc, salida, cargar = self._revisar_con(resultados)
        self.assertEqual(rc, 0)
        cargar.assert_called_once_with(mock.ANY, comprobar_frescura=True)
        self.assertIn("1 verde · 3 rojo · 2 error", salida)
        self.assertIn("origen-4: ValueError: primero", salida)
        self.assertNotIn("TypeError: segundo", salida)
        self.assertIn("origen-0", salida)
        self.assertIn("origen-1", salida)
        self.assertNotIn("se pone roja con «origen-2»", salida)

    def test_revisar_distingue_ausencia_de_rojos_y_de_verdes(self) -> None:
        """Ambas polaridades son necesarias para discriminar; confundir sus límites acepta una
        regla constante o rechaza una que sí tiene un ejemplo de cada lado."""
        rc_sin_rojos, salida_sin_rojos, _ = self._revisar_con([self._veredicto(True)])
        rc_sin_verdes, salida_sin_verdes, _ = self._revisar_con([self._veredicto(False)])
        rc_uno_y_uno, _, _ = self._revisar_con([
            self._veredicto(False), self._veredicto(True)])
        self.assertEqual(rc_sin_rojos, 1)
        self.assertIn("nunca se pone roja", salida_sin_rojos)
        self.assertEqual(rc_sin_verdes, 1)
        self.assertIn("nunca se pone verde", salida_sin_verdes)
        self.assertEqual(rc_uno_y_uno, 0)

    def test_revisar_propaga_cada_fallo_de_carga_con_uno(self) -> None:
        """Una fuente ilegible, una expansión inválida y un corpus roto son fallos distintos, pero
        ninguno puede convertirse en un éxito apto para automatización."""
        with (mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_fuente_medida",
                                side_effect=MedidaMalDeclarada("fuente rota"))):
            rc_fuente, _ = self._callado(medida.revisar, object(), Path("m.oracle"))
        self.assertEqual(rc_fuente, 1)

        with (mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_fuente_medida", return_value=["medida", "m"]),
              mock.patch.object(medida.Medida, "de_datos",
                                side_effect=MedidaMalDeclarada("expansión rota"))):
            rc_medida, _ = self._callado(medida.revisar, object(), Path("m.oracle"))
        self.assertEqual(rc_medida, 1)

        m = mock.Mock(id="d.m", op="<=", limite=0, segun="contrato",
                      porque="defensa", alcance="límite")
        with (mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_fuente_medida", return_value=["medida", "d.m"]),
              mock.patch.object(medida.Medida, "de_datos", return_value=m),
              mock.patch.object(medida, "alcance_derivado", return_value=[]),
              mock.patch.object(medida, "_evidencias", side_effect=ValueError("corpus roto"))):
            rc_corpus, _ = self._callado(medida.revisar, object(), Path("m.oracle"))
        self.assertEqual(rc_corpus, 1)

    def test_revisar_nombra_la_forma_macro_y_la_canonica(self) -> None:
        """La forma declarada decide dónde corregir: en la invocación de la macro o en la tubería
        canónica; invertir la pertenencia manda a editar la capa equivocada."""
        m = mock.Mock(id="d.m", op="<=", limite=0, segun="contrato",
                      porque="defensa", alcance="límite")
        m.evaluar.side_effect = [self._veredicto(False), self._veredicto(True)]
        for datos, macros, forma in (
                (["atajo", "d.m"], {"atajo": object()}, "forma: atajo"),
                (["medida", "d.m"], {}, "forma: canónica")):
            m.evaluar.side_effect = [self._veredicto(False), self._veredicto(True)]
            with (mock.patch.object(medida, "macros_del_proyecto", return_value=macros),
                  mock.patch.object(medida, "cargar_fuente_medida", return_value=datos),
                  mock.patch.object(medida.Medida, "de_datos", return_value=m),
                  mock.patch.object(medida, "alcance_derivado", return_value=[]),
                  mock.patch.object(medida, "_evidencias", return_value=[("r", {}), ("v", {})])):
                rc, salida = self._callado(medida.revisar, object(), Path("m.oracle"))
            self.assertEqual(rc, 0)
            self.assertIn(forma, salida)

    def test_relaciones_por_alias_tolera_hojas_y_recorre_ambos_lados(self) -> None:
        """Una tubería contiene hojas ajenas a las fuentes y un `unir` necesita conservar las dos;
        caer en una hoja o visitar dos veces la derecha pierde relaciones válidas."""
        datos = ["medida", "d.m", ["desde", ["unir", ["de", "izq", "i"],
                                                   ["de", "der", "d"]]]]
        self.assertEqual(medida.relaciones_por_alias(datos), {"i": "izq", "d": "der"})
        for hoja in ([], "texto"):
            medida.relaciones_por_alias(["medida", "d.m", ["desde", hoja]])

    def test_alcance_sin_declaraciones_y_cruce_entre_relaciones(self) -> None:
        """No poder cargar declaraciones significa desconocimiento, no error; al cruzarlas, un
        campo leído en otra relación jamás debe denunciarse como campo fantasma de ésta."""
        m = mock.Mock()
        with mock.patch("nucleo.relacion.cargar_relaciones", side_effect=ValueError("ausentes")):
            self.assertEqual(medida.alcance_derivado(SimpleNamespace(raiz=Path("/p")), m), [])

        m.a_datos.return_value = [
            "medida", "d.m", ["desde", ["de", "r1", "a"]],
            ["campos", ["campo", "a", "x"], ["campo", "b", "y"]],
        ]
        declaraciones = {
            "r1": SimpleNamespace(campos=[SimpleNamespace(nombre="x")]),
            "r2": SimpleNamespace(campos=[SimpleNamespace(nombre="y")]),
        }
        with (mock.patch("nucleo.relacion.cargar_relaciones", return_value=declaraciones),
              mock.patch.object(medida, "relaciones_por_alias",
                                return_value={"a": "r1", "b": "r2"})):
            lineas = medida.alcance_derivado(SimpleNamespace(raiz=Path("/p")), m)
        self.assertEqual(lineas, [
            "    de `r1` lee todos los campos declarados",
            "    de `r2` lee todos los campos declarados",
        ])

    def test_evaluadas_aparte_incluye_el_limite_de_subconjunto(self) -> None:
        """Consumir exactamente todas las relaciones del lenguaje sigue siendo consumir sólo
        lenguaje; excluir la igualdad marca como sin fijar una medida que sí ejercita el arnés."""
        m = SimpleNamespace(id="meta.limite")
        with (mock.patch("nucleo.medida.relaciones_del_lenguaje_declaradas",
                         return_value={"medida", "caso"}),
              mock.patch("nucleo.medida.relaciones_de_medida",
                         return_value={"medida", "caso"})):
            aparte = medida._evaluadas_aparte(object(), {m.id: m})
        self.assertEqual(aparte, {m.id})

    def _probar_simulado(self, *, texto="item: malo\n    true", veredicto=None,
                         error_lectura=None, error_evaluacion=None):
        m = mock.Mock(id="d.m")
        if error_evaluacion:
            m.evaluar.side_effect = error_evaluacion
        else:
            m.evaluar.return_value = veredicto or self._veredicto(True)
        leer = mock.patch.object(
            medida, "leer_caso", side_effect=error_lectura) if error_lectura else \
            mock.patch.object(medida, "leer_caso", return_value={"evidencia": {}})
        with (mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_fuente_medida", return_value=["medida", "d.m"]),
              mock.patch.object(medida.Medida, "de_datos", return_value=m),
              mock.patch.object(medida, "alcance_derivado", return_value=[]), leer):
            return self._callado(medida.probar, object(), Path("m.oracle"), texto)

    def test_probar_rechaza_medida_evidencia_vacia_y_evaluacion_rota(self) -> None:
        """Explorar no autoriza a ocultar tres ausencias de resultado: medida inválida, entrada
        vacía y evaluación imposible deben detener el script con código de fallo."""
        with (mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_fuente_medida",
                                side_effect=MedidaMalDeclarada("rota"))):
            rc_medida, _ = self._callado(medida.probar, object(), Path("m"), "item: x")
        self.assertEqual(rc_medida, 1)
        rc_vacia, salida_vacia = self._probar_simulado(texto=" \n\t")
        self.assertEqual(rc_vacia, 1)
        self.assertIn("no llegó evidencia", salida_vacia)
        rc_eval, salida_eval = self._probar_simulado(error_evaluacion=TypeError("campo ausente"))
        self.assertEqual(rc_eval, 1)
        self.assertIn("TypeError: campo ausente", salida_eval)

    def test_probar_propaga_error_de_caso_y_sin_evidencia_es_neutro(self) -> None:
        """Una evidencia mal declarada sí invalida la prueba, mientras una relación requerida vacía
        es un resultado neutro explícito y no un rojo inventado."""
        rc_caso, _ = self._probar_simulado(
            error_lectura=medida.CasoMalDeclarado("columnas inválidas"))
        self.assertEqual(rc_caso, 1)
        v = self._veredicto(True)
        v.sin_evidencia = "pieza"
        rc_neutro, salida = self._probar_simulado(veredicto=v)
        self.assertEqual(rc_neutro, 0)
        self.assertIn("SIN EVIDENCIA", salida)

    def test_probar_traduce_coordenadas_al_fragmento_visible(self) -> None:
        """Las coordenadas pertenecen al texto que ve la persona, no al caso envoltorio oculto;
        los mínimos, la sangría y el detalle posterior al primer separador son parte del contrato."""
        class ErrorVisible(Exception):
            pass

        error = ErrorVisible("interno: detalle: conservado")
        error.linea = 13
        error.columna = 9
        with mock.patch.object(medida, "ErrorSintaxis", ErrorVisible):
            rc, salida = self._probar_simulado(error_lectura=error)
        self.assertEqual(rc, 1)
        self.assertIn("línea 1, columna 1: detalle: conservado", salida)

        sin_coordenadas = ErrorVisible("interno: otro")
        with mock.patch.object(medida, "ErrorSintaxis", ErrorVisible):
            rc, salida = self._probar_simulado(
                texto="         item: malo", error_lectura=sin_coordenadas)
        self.assertEqual(rc, 1)
        self.assertIn("columna 2: otro", salida)

        error.columna = 10
        with mock.patch.object(medida, "ErrorSintaxis", ErrorVisible):
            rc, salida = self._probar_simulado(
                texto="         item: malo", error_lectura=error)
        self.assertEqual(rc, 1)
        self.assertIn("columna 11", salida)

    def test_probar_limita_testigos_y_explica_el_excedente(self) -> None:
        """Cinco filas mantienen legible el diagnóstico; con seis debe verse sólo cinco y saberse
        que falta exactamente una, sin anunciar un excedente cero en el borde."""
        cinco = self._veredicto(False)
        cinco.testigos = [f"fila-{i}" for i in range(5)]
        rc_cinco, salida_cinco = self._probar_simulado(veredicto=cinco)
        self.assertEqual(rc_cinco, 0)
        self.assertNotIn("… y", salida_cinco)

        seis = self._veredicto(False)
        seis.testigos = [f"fila-{i}" for i in range(6)]
        rc_seis, salida_seis = self._probar_simulado(veredicto=seis)
        self.assertEqual(rc_seis, 0)
        self.assertIn("fila-4", salida_seis)
        self.assertNotIn("fila-5", salida_seis)
        self.assertIn("… y 1 más", salida_seis)


class MedidaMutantesDeListadoYDespachoTests(unittest.TestCase):
    """Fija el protocolo de salida y retorno que consumen personas y scripts."""

    @staticmethod
    def _callado(fn, *args, **kwargs):
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = fn(*args, **kwargs)
        return rc, salida.getvalue()

    @staticmethod
    def _m(mid: str, alcance: str = "límite declarado"):
        return SimpleNamespace(
            id=mid, op="<=", limite=0, segun="contrato", alcance=alcance)

    def _listar_con(self, catalogo, propias, ejercicio, argv=None):
        contexto = mock.MagicMock()
        contexto.__enter__.return_value = None
        contexto.__exit__.return_value = False
        proy = SimpleNamespace(catalogos=Path("/proyecto/catalogos"), raiz=Path("/proyecto"))
        with (mock.patch.object(medida, "problemas_estructura", return_value=[]),
              mock.patch.object(medida, "confiar_escalares", return_value=False),
              mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
              mock.patch.object(medida, "catalogos_a_cargar", return_value=[]),
              mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_catalogo", side_effect=[catalogo, propias]),
              mock.patch.object(medida, "ejercicio_del_catalogo", return_value=ejercicio)):
            return self._callado(medida.listar, proy, argv)

    @staticmethod
    def _ejercicio(*, sin=(), casos=None, heredadas=(), aparte=(), completa=True,
                   hubo_jueza=True):
        return medida.Ejercicio(
            frozenset(sin), casos or {}, {}, frozenset(heredadas), frozenset(aparte),
            completa, hubo_jueza)

    def test_listar_propaga_estructura_y_cargas_invalidas(self) -> None:
        """Un listado parcial parece una auditoría completa; cualquier estructura, UDF o catálogo
        ilegible debe impedir que el llamador lo tome por válido."""
        proy = SimpleNamespace(catalogos=Path("/p/catalogos"), raiz=Path("/p"))
        with mock.patch.object(medida, "problemas_estructura", return_value=["falta catalogos"]):
            rc_estructura, _ = self._callado(medida.listar, proy)
        self.assertEqual(rc_estructura, 1)

        contexto = mock.MagicMock()
        contexto.__enter__.return_value = None
        contexto.__exit__.return_value = False
        bases = (
            EscalaresNoConfiables("sin permiso"),
            EscalaresInvalidas("archivo roto"),
            ValueError("catálogo roto"),
        )
        for error in bases:
            with (self.subTest(error=type(error).__name__),
                  mock.patch.object(medida, "problemas_estructura", return_value=[]),
                  mock.patch.object(medida, "confiar_escalares", return_value=False),
                  mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
                  mock.patch.object(medida, "catalogos_a_cargar", return_value=[]),
                  mock.patch.object(medida, "macros_del_proyecto", return_value={}),
                  mock.patch.object(medida, "cargar_catalogo", side_effect=error)):
                rc, _ = self._callado(medida.listar, proy)
            self.assertEqual(rc, 1)

    def test_listar_normaliza_argv_ausente_y_catalogo_vacio(self) -> None:
        """La ausencia de banderas equivale a una lista vacía y un catálogo genuinamente vacío es
        un resultado exitoso, no un valor implícito ambiguo."""
        contexto = mock.MagicMock()
        contexto.__enter__.return_value = None
        contexto.__exit__.return_value = False
        proy = SimpleNamespace(catalogos=Path("/p/catalogos"), raiz=Path("/p"))
        with (mock.patch.object(medida, "problemas_estructura", return_value=[]),
              mock.patch.object(medida, "confiar_escalares", return_value=False) as confiar,
              mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
              mock.patch.object(medida, "catalogos_a_cargar", return_value=[]),
              mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "cargar_catalogo", side_effect=[{}, {}])):
            rc, salida = self._callado(medida.listar, proy)
        self.assertEqual(rc, 0)
        confiar.assert_called_once_with([])
        self.assertIn("0 medidas", salida)

    def test_listar_usa_singular_para_una_medida_y_una_heredada(self) -> None:
        """Los singulares son parte de una salida destinada a lectura; sus bordes además revelan
        si el conteo usado para presentar coincide con el conjunto realmente recorrido."""
        propia = self._m("d.unica")
        ejercicio = self._ejercicio()
        rc, salida = self._listar_con({propia.id: propia}, {propia.id: propia}, ejercicio)
        self.assertEqual(rc, 0)
        self.assertIn("CATÁLOGO (1 medida · todas fijadas)", salida)

        heredada = self._m("base.unica")
        ejercicio = self._ejercicio(heredadas={heredada.id})
        rc, salida = self._listar_con({heredada.id: heredada}, {}, ejercicio)
        self.assertEqual(rc, 0)
        self.assertIn("1 MEDIDA HEREDADA", salida)

    def test_listar_separa_fijadas_y_sin_fijar_en_el_encabezado(self) -> None:
        """El resumen es la alarma de auditoría: invertir cualquiera de los conjuntos puede dejar
        una medida sin evidencia escondida bajo “todas fijadas”."""
        catalogo = {mid: self._m(mid) for mid in ("d.fija", "d.suelta1", "d.suelta2")}
        ejercicio = self._ejercicio(sin={"d.suelta1", "d.suelta2"})
        rc, salida = self._listar_con(catalogo, catalogo, ejercicio)
        self.assertEqual(rc, 0)
        self.assertIn("3 medidas · 1 fijada · 2 sin fijar", salida)

    def test_listar_conserva_todas_las_lineas_del_alcance(self) -> None:
        """El alcance enumera lo que una medida no ve; perder una línea al formatearlo exagera la
        cobertura y es peor que un simple cambio cosmético."""
        m = self._m("d.multilinea", "primera\nsegunda\ntercera")
        rc, salida = self._listar_con({m.id: m}, {m.id: m}, self._ejercicio())
        self.assertEqual(rc, 0)
        self.assertIn("alcance:  primera", salida)
        self.assertIn("segunda", salida)
        self.assertIn("tercera", salida)

        dos = self._m("d.dos_lineas", "primera\nsegunda")
        rc_dos, salida_dos = self._listar_con(
            {dos.id: dos}, {dos.id: dos}, self._ejercicio())
        self.assertEqual(rc_dos, 0)
        self.assertIn("alcance:  primera", salida_dos)
        self.assertIn("segunda", salida_dos)

    def _main_con(self, args, *, proy=None, estructura=(), argv=None):
        proy = proy or SimpleNamespace(
            raiz=Path("/proyecto"), es_el_propio_oracle=False)
        argv = list(args if argv is None else argv)
        with (mock.patch.object(medida, "sin_banderas_comunes", return_value=list(args)),
              mock.patch.object(medida, "resolver_cli", return_value=proy),
              mock.patch.object(medida, "problemas_estructura", return_value=list(estructura))):
            return self._callado(medida.main, argv)

    def test_main_propaga_resolucion_estructura_y_listado(self) -> None:
        """El despachador no debe borrar códigos de fallo: son la única señal fiable para quien
        encadena el comando desde un script."""
        with (mock.patch.object(medida, "sin_banderas_comunes", return_value=["--listar"]),
              mock.patch.object(medida, "resolver_cli", return_value=None)):
            rc_sin_proyecto, _ = self._callado(medida.main, ["--listar"])
        self.assertEqual(rc_sin_proyecto, 1)

        rc_estructura, _ = self._main_con(["--listar"], estructura=["falta catálogo"])
        self.assertEqual(rc_estructura, 1)

        with mock.patch.object(medida, "listar", return_value=7):
            rc_listar, _ = self._main_con(["--listar"])
        self.assertEqual(rc_listar, 7)

    def test_main_escalares_distingue_oracle_confianza_y_excepciones(self) -> None:
        """El Oracle propio no es código externo y la confianza explícita debe ejecutarlo; mezclar
        los booleanos muestra advertencias falsas o ignora una autorización deliberada."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "escalares.py").write_text("# existe", encoding="utf-8")
            propio = SimpleNamespace(raiz=raiz, es_el_propio_oracle=True)
            with mock.patch.object(medida, "escalares", return_value=5) as escalares:
                rc_propio, _ = self._main_con(["--escalares"], proy=propio)
            self.assertEqual(rc_propio, 5)
            escalares.assert_called_once_with(propio)

            externo = SimpleNamespace(raiz=raiz, es_el_propio_oracle=False)
            contexto = mock.MagicMock()
            contexto.__enter__.return_value = None
            contexto.__exit__.return_value = False
            with (mock.patch.object(medida, "confiar_escalares", return_value=True),
                  mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
                  mock.patch.object(medida, "escalares", return_value=6) as escalares):
                rc_confiado, _ = self._main_con(["--escalares"], proy=externo)
            self.assertEqual(rc_confiado, 6)
            escalares.assert_called_once_with(externo)

            contexto.__enter__.side_effect = EscalaresNoConfiables("bloqueado")
            with (mock.patch.object(medida, "confiar_escalares", return_value=True),
                  mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto)):
                rc_error, _ = self._main_con(["--escalares"], proy=externo)
            self.assertEqual(rc_error, 1)

    def test_main_expandir_valida_borde_argumento_ruta_y_retorno(self) -> None:
        """Dos argumentos son suficientes y el primero es el archivo; desplazar el borde o el índice
        puede expandir otra ruta mientras el comando aparenta haber obedecido."""
        contexto = mock.MagicMock()
        contexto.__enter__.return_value = None
        contexto.__exit__.return_value = False
        proy = SimpleNamespace(raiz=Path("/proyecto"), es_el_propio_oracle=False)

        with (mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
              mock.patch.object(medida, "confiar_escalares", return_value=False),
              mock.patch.object(medida, "macros_del_proyecto", return_value={}),
              mock.patch.object(medida, "expandir_archivo", return_value=8) as expandir):
            rc_borde, _ = self._main_con(["--expandir", "uno.oracle"], proy=proy)
            rc_indice, _ = self._main_con(
                ["--expandir", "uno.oracle", "dos.oracle"], proy=proy)
        self.assertEqual((rc_borde, rc_indice), (8, 8))
        self.assertEqual(expandir.call_args.args[0], proy.raiz / "uno.oracle")

        rc_falta, salida = self._main_con(["--expandir"], proy=proy)
        self.assertEqual(rc_falta, 1)
        self.assertIn("falta el archivo", salida)

    def test_main_nueva_valida_borde_argumento_y_retorno(self) -> None:
        """El id único completa el comando; exigir uno extra o descartar el retorno rompe tanto el
        uso interactivo como la composición desde otros comandos."""
        with mock.patch.object(medida, "nueva", return_value=9) as nueva:
            rc, _ = self._main_con(["--nueva", "d.id"])
        self.assertEqual(rc, 9)
        nueva.assert_called_once_with(mock.ANY, "d.id")

        rc_falta, salida = self._main_con(["--nueva"])
        self.assertEqual(rc_falta, 1)
        self.assertIn("falta el id", salida)

    def test_main_ruta_directa_y_relativa_no_se_confunden(self) -> None:
        """Una ruta existente conserva su identidad; sólo una ausente se resuelve contra la raíz
        del proyecto, y el mensaje final debe nombrar el argumento que escribió la persona."""
        contexto = mock.MagicMock()
        contexto.__enter__.return_value = None
        contexto.__exit__.return_value = False
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            directa = base / "directa.oracle"
            directa.write_text("x", encoding="utf-8")
            proy = SimpleNamespace(raiz=base / "proyecto", es_el_propio_oracle=False)
            proy.raiz.mkdir()
            relativa = proy.raiz / "relativa.oracle"
            relativa.write_text("x", encoding="utf-8")
            with (mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
                  mock.patch.object(medida, "confiar_escalares", return_value=False),
                  mock.patch.object(medida, "revisar", return_value=4) as revisar):
                rc_directa, _ = self._main_con([str(directa)], proy=proy)
                self.assertEqual(revisar.call_args.args[1], directa)
                rc_relativa, _ = self._main_con(["relativa.oracle", "señuelo"], proy=proy)
                self.assertEqual(revisar.call_args.args[1], relativa)
            self.assertEqual((rc_directa, rc_relativa), (4, 4))

            rc_ausente, salida = self._main_con(["ausente.oracle", "señuelo"], proy=proy)
        self.assertEqual(rc_ausente, 1)
        self.assertIn("no existe: ausente.oracle", salida)

    def test_main_error_de_escalares_en_accion_devuelve_uno(self) -> None:
        """La carga diferida de UDF también puede fallar al revisar o expandir; el despachador debe
        convertir ese rechazo en el mismo código inequívoco que usa el inventario."""
        contexto = mock.MagicMock()
        contexto.__enter__.side_effect = EscalaresInvalidas("rota")
        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "m.oracle"
            ruta.write_text("x", encoding="utf-8")
            proy = SimpleNamespace(raiz=Path(td), es_el_propio_oracle=False)
            with (mock.patch.object(medida, "escalares_del_proyecto", return_value=contexto),
                  mock.patch.object(medida, "confiar_escalares", return_value=False)):
                rc, salida = self._main_con([str(ruta)], proy=proy)
        self.assertEqual(rc, 1)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", salida)


class VigilarTests(unittest.TestCase):
    def test_firma_detecta_reemplazo_y_archivo_ausente(self) -> None:
        estado = mock.Mock(st_mtime_ns=11, st_size=22, st_ino=33)
        ruta = mock.Mock()
        ruta.stat.return_value = estado
        self.assertEqual(medida._firma_de_archivo(ruta), (11, 22, 33))

        ruta.stat.return_value = mock.Mock(st_mtime_ns=12, st_size=22, st_ino=33)
        self.assertNotEqual(medida._firma_de_archivo(ruta), (11, 22, 33))

        ruta.stat.side_effect = FileNotFoundError("guardado atómico")
        self.assertIsNone(medida._firma_de_archivo(ruta))

    def test_reevalua_al_guardar_y_sobrevive_a_un_reemplazo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            firmas = [(1, 10, 100), None, (2, 11, 101)]
            salida = _SalidaDiferida()
            vueltas = 0
            evaluaciones = 0

            def evaluar(_proy, _ruta, _texto) -> int:
                nonlocal evaluaciones
                if evaluaciones == 0:
                    self.assertIn("VIGILANDO", salida.visible)
                rc = (1, 0)[evaluaciones]
                evaluaciones += 1
                return rc

            def dormir(_intervalo: float) -> None:
                nonlocal vueltas
                vueltas += 1
                if vueltas == 2:
                    self.assertIn("esperando que vuelva a aparecer", salida.visible)
                if vueltas == 3:
                    raise KeyboardInterrupt

            with (mock.patch.object(medida, "_firma_de_archivo", side_effect=firmas),
                  mock.patch.object(medida, "probar", side_effect=evaluar) as probar,
                  mock.patch.object(medida.time, "sleep", side_effect=dormir) as esperar,
                  redirect_stdout(salida)):
                rc = medida.vigilar(
                    proy, ruta, 'pieza: id, alto\n    "columna", 450.0')

        self.assertEqual(rc, 0)
        self.assertEqual(probar.call_count, 2)
        self.assertEqual(esperar.call_args_list, [mock.call(0.25)] * 3)
        self.assertIn("VIGILANDO", salida.getvalue())
        self.assertIn("esperando que vuelva a aparecer", salida.getvalue())
        self.assertIn("Vigilancia terminada", salida.getvalue())

    def test_un_error_real_de_parseo_no_mata_la_vigilancia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            valido = ruta.read_text(encoding="utf-8")
            ruta.write_text("ninguno demo.alto:\n    de", encoding="utf-8")
            vueltas = 0

            def guardar_y_terminar(_intervalo: float) -> None:
                nonlocal vueltas
                vueltas += 1
                if vueltas == 1:
                    ruta.write_text(valido, encoding="utf-8")
                else:
                    raise KeyboardInterrupt

            salida = io.StringIO()
            with (mock.patch.object(medida.time, "sleep", side_effect=guardar_y_terminar),
                  redirect_stdout(salida)):
                rc = medida.vigilar(
                    proy, ruta, 'pieza: id, alto\n    "columna", 450.0')

        self.assertEqual(rc, 0)
        self.assertIn("✗", salida.getvalue())
        self.assertIn("ROJO", salida.getvalue())
        self.assertIn("Vigilancia terminada", salida.getvalue())

    def test_cli_despacha_vigilar_y_valida_el_valor_de_con(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            evidencia = 'pieza: id, alto\n    "columna", 450.0'
            argv_vigilar = [
                "medida", "probar", str(ruta), "--con", evidencia, "--vigilar",
                "--proyecto", str(proy.raiz)]
            with mock.patch.object(medida, "vigilar", return_value=7) as vigilar:
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.main(argv_vigilar)
            self.assertEqual(rc, 7)
            vigilar.assert_called_once_with(proy, ruta, evidencia)

            argv_una = [
                "medida", "probar", str(ruta), "--proyecto", str(proy.raiz),
                "--con", evidencia]
            with mock.patch.object(cli, "cmd_probar", return_value=5) as probar:
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.main(argv_una)
            self.assertEqual(rc, 5)
            probar.assert_called_once_with(
                proy, str(ruta), evidencia, argv=argv_una, vigilar=False)

            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main([
                    "medida", "probar", str(ruta), "--proyecto", str(proy.raiz), "--con"])
            self.assertEqual(rc, 1)
            self.assertIn("falta la evidencia", salida.getvalue())

            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main([
                    "medida", "probar", str(ruta), "--con", "--vigilar",
                    "--proyecto", str(proy.raiz)])
            self.assertEqual(rc, 1)
            self.assertIn("falta la evidencia", salida.getvalue())

    def test_wrapper_elige_una_sola_modalidad_y_propaga_el_codigo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            with (mock.patch.object(medida, "probar", return_value=3) as una,
                  mock.patch.object(medida, "vigilar", return_value=4) as viva):
                self.assertEqual(cli.cmd_probar(proy, str(ruta), "filas"), 3)
                self.assertEqual(cli.cmd_probar(
                    proy, str(ruta), "filas", vigilar=True), 4)
            una.assert_called_once_with(proy, ruta, "filas")
            viva.assert_called_once_with(proy, ruta, "filas")

    def test_wrapper_respeta_confianza_de_escalares_y_falla_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            contexto = mock.MagicMock()
            contexto.__enter__.return_value = None
            contexto.__exit__.return_value = False
            with (mock.patch.object(cli, "escalares_del_proyecto", return_value=contexto) as abrir,
                  mock.patch.object(cli, "confiar_escalares", return_value=True),
                  mock.patch.object(medida, "probar", return_value=0)):
                self.assertEqual(cli.cmd_probar(
                    proy, str(ruta), "filas", argv=["--confiar-escalares"]), 0)
            abrir.assert_called_once_with(proy, confiar=True)

            contexto.__enter__.side_effect = cli.EscalaresNoConfiables("falta confianza")
            salida = io.StringIO()
            with (mock.patch.object(cli, "escalares_del_proyecto", return_value=contexto),
                  redirect_stdout(salida)):
                self.assertEqual(cli.cmd_probar(proy, str(ruta), "filas"), 1)
            self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", salida.getvalue())
