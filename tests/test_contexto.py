"""`oracle contexto` es una vista, no un documento: todo lo que dice sale de otra fuente."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.proyecto import Proyecto  # noqa: E402
from nucleo.vocabulario import OPERADORES, ORIGENES_DE_UMBRAL  # noqa: E402
from tools import contexto  # noqa: E402


def _proyecto_vacio(td: str) -> Proyecto:
    raiz = Path(td)
    (raiz / "catalogos").mkdir()
    (raiz / "corpus").mkdir()
    (raiz / "oracle.json").write_text(
        json.dumps({"esquema": "oracle.proyecto/v1"}), encoding="utf-8")
    return Proyecto(raiz)


def _texto_controlado(*, campos=None, dondes=None, catalogo=None, falla="",
                      perfiles=(), catalogo_base=False, compacto=False) -> str:
    proyecto = SimpleNamespace(raiz=Path("/tmp/proyecto-controlado"))
    cfg = SimpleNamespace(sombra=[], perfiles=list(perfiles), catalogo_base=catalogo_base)
    with (mock.patch.object(contexto, "_relaciones", return_value=(campos or {}, dondes or {})),
          mock.patch.object(contexto, "_medidas", return_value=(catalogo or [], falla)),
          mock.patch.object(contexto, "configuracion", return_value=cfg)):
        return contexto.texto(proyecto, compacto=compacto)


class ContieneLoQueHaceFaltaTests(unittest.TestCase):

    def setUp(self) -> None:
        self.propio = contexto.texto(Proyecto(RAIZ))

    def test_dice_lo_que_toda_medida_declara(self) -> None:
        """Es lo único que no se puede deducir mirando el proyecto: hay que saberlo de antemano."""
        for exigido in ("umbral", "segun", "alcance", "porque"):
            self.assertIn(exigido, self.propio)

    def test_los_origenes_del_umbral_salen_del_vocabulario(self) -> None:
        """No copiados: si mañana entra un quinto origen, aparece acá solo."""
        for origen in ORIGENES_DE_UMBRAL:
            self.assertIn(origen, self.propio)

    def test_los_operadores_salen_del_vocabulario(self) -> None:
        for operador in OPERADORES:
            self.assertIn(operador, self.propio)

    def test_las_relaciones_salen_de_la_evidencia_real(self) -> None:
        """Del mismo inventario que usa `oracle relaciones`, no de una lista escrita al lado."""
        from tools.medida import inventario_de_relaciones

        campos, _ = inventario_de_relaciones(Proyecto(RAIZ))
        self.assertTrue(campos, "el proyecto propio tiene que tener evidencia")
        for relacion in list(campos)[:5]:
            self.assertIn(relacion, self.propio)

    def test_nombra_las_medidas_que_ya_existen(self) -> None:
        """Para no proponer una que ya está. Sin esto, el que escribe no tiene cómo saberlo."""
        self.assertIn("meta.toda_medida_esta_fijada", self.propio)

    def test_dice_que_el_caso_va_antes_que_la_medida(self) -> None:
        """Es el error que ninguna validación automática atrapa: una medida escrita primero hace
        que el caso la describa en vez de probarla."""
        self.assertIn("CASO", self.propio)
        self.assertIn("antes", self.propio)


class ElCompactoDiceLoMismoConMenosTests(unittest.TestCase):

    def setUp(self) -> None:
        proy = Proyecto(RAIZ)
        self.normal = contexto.texto(proy)
        self.compacto = contexto.texto(proy, compacto=True)

    def test_ahorra_de_verdad(self) -> None:
        """El destinatario probable es un agente con una ventana de contexto. Si ahorrara poco, la
        bandera sería una complicación sin motivo."""
        self.assertLess(len(self.compacto) * 2, len(self.normal))

    def test_no_pierde_ninguna_relacion(self) -> None:
        """Apretar no es recortar: lo que se va son renglones en blanco y prosa, no información."""
        from tools.medida import inventario_de_relaciones

        campos, _ = inventario_de_relaciones(Proyecto(RAIZ))
        for relacion in campos:
            self.assertIn(relacion, self.compacto)

    def test_no_pierde_ninguna_medida(self) -> None:
        catalogo, falla = contexto._medidas(Proyecto(RAIZ))
        self.assertEqual(falla, "")
        for mid, _ in catalogo:
            self.assertIn(mid, self.compacto)

    def test_no_deja_renglones_vacios(self) -> None:
        self.assertNotIn("\n\n", self.compacto)


class UnProyectoSinNadaNoRompeTests(unittest.TestCase):
    """Un proyecto recién inicializado es el caso donde MÁS falta este comando, y es justo donde
    no hay evidencia ni medidas de las que derivar nada."""

    def test_sin_evidencia_lo_dice_en_vez_de_fallar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            salida = contexto.texto(_proyecto_vacio(td))
        self.assertIn("ninguna", salida)
        self.assertIn("umbral", salida)

    def test_sin_medidas_tambien(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            salida = contexto.texto(_proyecto_vacio(td))
        self.assertIn("0 MEDIDAS", salida.upper())


class ElContextoNoMienteCuandoNoPuedeLeerTests(unittest.TestCase):
    """Un cero por falla es indistinguible de un cero real, y quien lee esto no tiene con qué dudar.

    Medido el 2026-09-04: los dos consumidores conocidos tienen catálogo —41 y 9 medidas— y este
    texto decía «LAS 0 MEDIDAS QUE YA EXISTEN», porque un `except Exception: return []` se tragaba
    el fallo de cargar las escalares del proyecto. Sobre esa base, un agente escribe la primera
    medida de un catálogo que ya tiene cuarenta y una.
    """

    def _proyecto_con_escalares(self, td: str):
        raiz = Path(td)
        (raiz / "catalogos").mkdir()
        (raiz / "escalares.py").write_text(
            "# código del proyecto: ejecutarlo necesita autorización\n", encoding="utf-8")
        return Proyecto(raiz)

    def test_sin_autorizacion_dice_que_falta_y_no_cuenta_cero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto_con_escalares(td)
            catalogo, falla = contexto._medidas(proy, confiar=False)

            self.assertEqual(catalogo, [])
            self.assertIn("--confiar-escalares", falla)

    def test_el_texto_no_afirma_un_numero_que_no_pudo_averiguar(self) -> None:
        """Lo que se lee es la afirmación, no el valor de retorno: es lo único que ve un agente."""
        with tempfile.TemporaryDirectory() as td:
            salida = contexto.texto(self._proyecto_con_escalares(td))

        self.assertIn("NO SE PUDIERON LEER", salida)
        self.assertNotIn("LAS 0 MEDIDAS QUE YA EXISTEN", salida)

    def test_un_catalogo_vacio_de_verdad_si_dice_cero(self) -> None:
        """El otro lado: sin escalares que autorizar, cero es cero y hay que decirlo."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            catalogo, falla = contexto._medidas(Proyecto(raiz))

            self.assertEqual(falla, "")
            self.assertEqual(catalogo, [])
            self.assertIn("LAS 0 MEDIDAS QUE YA EXISTEN", contexto.texto(Proyecto(raiz)))


class CadaDecisionDelContextoQuedaFijadaTests(unittest.TestCase):

    def test_la_raiz_es_la_del_repositorio_y_no_su_directorio_padre(self) -> None:
        """La entrada es este módulo real porque su raíz decide qué proyecto e imports inspecciona."""
        self.assertEqual(contexto.RAIZ, RAIZ)

    def test_no_autorizar_es_el_default_de_la_carga_de_medidas(self) -> None:
        """Omitir la autorización importa: código propio jamás debe ejecutarse por accidente."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "escalares.py").write_text(
                "# código del proyecto que requiere autorización\n", encoding="utf-8")

            resultado = contexto._medidas(Proyecto(raiz))

        self.assertEqual(resultado, (
            [],
            "el catálogo usa escalares declaradas por el proyecto y nadie autorizó "
            "ejecutarlas: repetí con `--confiar-escalares`",
        ))

    def test_un_error_inesperado_conserva_su_tipo_y_mensaje(self) -> None:
        """El error con texto propio importa porque diagnostica una causa distinta de autorización."""
        with mock.patch.object(
                contexto, "escalares_del_proyecto", side_effect=ValueError("catálogo inválido")):
            resultado = contexto._medidas(SimpleNamespace())

        self.assertEqual(resultado, (
            [], "no se pudo cargar el catálogo — ValueError: catálogo inválido"))

    def test_una_relacion_ilegible_se_convierte_en_dos_inventarios_vacios(self) -> None:
        """La excepción importa porque la vista debe seguir siendo utilizable sin evidencia legible."""
        with mock.patch.object(
                contexto, "inventario_de_relaciones", side_effect=ValueError("evidencia rota")):
            resultado = contexto._relaciones(SimpleNamespace())

        self.assertEqual(resultado, ({}, {}))

    def test_un_perfil_vacio_se_nombra_como_ninguno(self) -> None:
        """La lista vacía deja falso el nombre unido y verdadero el reemplazo que informa ausencia."""
        salida = _texto_controlado(perfiles=())
        lineas = [linea for linea in salida.splitlines() if linea.startswith("perfiles:")]

        self.assertEqual(lineas, ["perfiles: ninguno · catálogo base: no"])

    def test_la_vista_normal_explica_cada_origen_del_umbral(self) -> None:
        """El modo no compacto importa porque debe elegir la explicación, no sólo los nombres."""
        origenes = {"medicion": "se obtuvo observando el sistema real"}
        with mock.patch.object(contexto, "ORIGENES_DE_UMBRAL", origenes):
            salida = _texto_controlado(compacto=False)

        fragmento = salida.split("Los orígenes del umbral son cerrados:\n", 1)[1].split(
            "\n\n## RELACIONES QUE HAY HOY, CON SUS CAMPOS", 1)[0]
        self.assertEqual(
            fragmento, "        medicion: se obtuvo observando el sistema real")

    def test_un_inventario_vacio_lo_dice_en_la_seccion_de_relaciones(self) -> None:
        """Los campos vacíos importan porque otros «ninguna» no deben ocultar esta advertencia."""
        salida = _texto_controlado(campos={}, dondes={})
        seccion = salida.split("## RELACIONES QUE HAY HOY, CON SUS CAMPOS", 1)[1].split(
            "## CON QUÉ SE ESCRIBE", 1)[0]

        self.assertEqual(
            seccion,
            "\n\n  (ninguna: sin evidencia no hay nada que medir todavía)\n"
            "Un hecho nuevo se agrega desde su SENSOR, no acá.\n\n",
        )

    def test_una_relacion_con_cuatro_fuentes_muestra_solo_tres(self) -> None:
        """Cuatro apariciones importan porque hacen observable el límite prometido de tres ejemplos."""
        salida = _texto_controlado(
            campos={"uso": {"nombre": {"texto"}}},
            dondes={"uso": {"cuarta", "primera", "segunda", "tercera"}},
        )
        lineas = [linea for linea in salida.splitlines() if "· aparece en:" in linea]

        self.assertEqual(lineas, ["      · aparece en: cuarta, primera, segunda"])

    def test_las_aridades_distinguen_sin_tope_de_tope_exacto(self) -> None:
        """Un tope nulo y otro igual al mínimo importan porque recorren las dos decisiones de formato."""
        def exacta():
            pass

        def variable():
            pass

        exacta.aridad_min = 2
        exacta.aridad_max = 2
        variable.aridad_min = 3
        variable.aridad_max = None
        with mock.patch.dict(
                contexto.ESCALARES, {"exacta": exacta, "variable": variable}, clear=True):
            salida = _texto_controlado()

        seccion = salida.split("  escalares:\n", 1)[1].split(
            "\n\n## LAS 0 MEDIDAS QUE YA EXISTEN", 1)[0]
        self.assertEqual(seccion.splitlines(), ["    exacta/2", "    variable/3+"])

    def test_un_catalogo_realmente_vacio_lo_declara_debajo_del_cero(self) -> None:
        """El catálogo vacío importa porque es el único caso donde «ninguna» es una afirmación cierta."""
        salida = _texto_controlado(catalogo=[])
        seccion = salida.split("## LAS", 1)[1].split("## EL ORDEN QUE IMPORTA", 1)[0]

        self.assertEqual(
            seccion, " 0 MEDIDAS QUE YA EXISTEN\n\n  (ninguna todavía)\n\n")

    def test_un_alcance_no_vacio_se_resume_hasta_el_primer_punto(self) -> None:
        """El texto verdadero y el reemplazo vacío importan porque sólo el primero informa el límite."""
        medida = SimpleNamespace(alcance="Sólo ve Python. No ve otros lenguajes.")
        salida = _texto_controlado(catalogo=[("calidad.una", medida)])
        lineas = [linea for linea in salida.splitlines()
                  if linea.startswith("  calidad.") or linea.startswith("      NO ve:")]

        self.assertEqual(lineas, ["  calidad.una", "      NO ve: Sólo ve Python"])


class LaEntradaDirectaPropagaSusDecisionesTests(unittest.TestCase):

    @staticmethod
    def _texto_que_revela_banderas(
            proyecto, *, compacto=False, confiar_escalares=False) -> str:
        return f"compacto={compacto}; confiar_escalares={confiar_escalares}"

    def test_confiar_escalares_si_autoriza_al_texto(self) -> None:
        """La bandera sola importa porque era aceptada pero se perdía justo antes de cargar el catálogo."""
        salida = io.StringIO()
        with (mock.patch.object(contexto, "resolver_cli", return_value=SimpleNamespace()),
              mock.patch.object(contexto, "texto", side_effect=self._texto_que_revela_banderas),
              redirect_stdout(salida)):
            codigo = contexto.main(["--confiar-escalares"])

        self.assertEqual(
            (codigo, salida.getvalue()),
            (0, "compacto=False; confiar_escalares=True\n"),
        )

    def test_argv_del_proceso_conserva_su_primera_bandera(self) -> None:
        """Dos argumentos importan porque cortar desde el segundo perdería la primera decisión real."""
        salida = io.StringIO()
        argv = ["contexto.py", "--compacto", "argumento-desconocido"]
        with (mock.patch.object(contexto.sys, "argv", argv),
              mock.patch.object(contexto, "resolver_cli", return_value=SimpleNamespace()),
              mock.patch.object(contexto, "texto", side_effect=self._texto_que_revela_banderas),
              redirect_stdout(salida)):
            codigo = contexto.main(None)

        self.assertEqual(
            (codigo, salida.getvalue()),
            (0, "compacto=True; confiar_escalares=False\n"),
        )

    def test_confiar_y_compacto_llegan_como_decisiones_independientes(self) -> None:
        """Una bandera común y otra propia importan porque el parseo debe quitar sólo la primera."""
        salida = io.StringIO()
        with (mock.patch.object(contexto, "resolver_cli", return_value=SimpleNamespace()),
              mock.patch.object(contexto, "texto", side_effect=self._texto_que_revela_banderas),
              redirect_stdout(salida)):
            codigo = contexto.main(["--confiar-escalares", "--compacto"])

        self.assertEqual(
            (codigo, salida.getvalue()),
            (0, "compacto=True; confiar_escalares=True\n"),
        )

    def test_un_proyecto_que_no_resuelve_devuelve_dos(self) -> None:
        """La ausencia importa porque debe distinguir un proyecto inválido de una ejecución exitosa."""
        with mock.patch.object(contexto, "resolver_cli", return_value=None):
            codigo = contexto.main([])

        self.assertEqual(codigo, 2)


if __name__ == "__main__":
    unittest.main()
