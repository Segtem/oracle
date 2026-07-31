"""Contrato del adaptador de proyecto: selección, perfiles y confinamiento."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from nucleo import algebra, proyecto as modulo
from nucleo.proyecto import (ConfiguracionProyecto, EscalaresInvalidas,
                             EscalaresNoConfiables, Proyecto, ProyectoInvalido,
                             catalogos_a_cargar, catalogos_base_a_cargar,
                             configuracion, escalares_del_proyecto,
                             perfiles_incluidos, presentar_ruta, problemas_estructura,
                             resolver, ruta_de_medida_nueva)


class ProyectoTests(unittest.TestCase):
    def _raiz(self, base: str, *, catalogos: bool = True) -> Path:
        raiz = Path(base)
        if catalogos:
            (raiz / "catalogos").mkdir()
        return raiz

    def _configurar(self, raiz: Path, datos) -> None:
        (raiz / "oracle.json").write_text(json.dumps(datos), encoding="utf-8")

    def test_los_objetos_de_configuracion_y_proyecto_son_inmutables(self) -> None:
        configuracion_vacia = ConfiguracionProyecto()
        proy = Proyecto(Path("/proyecto"))

        with self.assertRaises(FrozenInstanceError):
            configuracion_vacia.perfiles = ("python",)
        with self.assertRaises(FrozenInstanceError):
            configuracion_vacia.catalogo_base = False
        with self.assertRaises(FrozenInstanceError):
            proy.raiz = Path("/otro")

    def test_sin_oracle_json_la_configuracion_es_vacia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(configuracion(Proyecto(self._raiz(td))), ConfiguracionProyecto())

    def test_oracle_json_valido_preserva_el_orden_de_perfiles(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "perfiles": ["python"],
            })
            self.assertEqual(configuracion(Proyecto(raiz)).perfiles, ("python",))

    def test_un_proyecto_nuevo_no_recibe_politicas_base_implicitamente(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            proy = Proyecto(raiz)
            self.assertFalse(configuracion(proy).catalogo_base)
            self.assertEqual(catalogos_base_a_cargar(proy), [])
            self.assertEqual(catalogos_a_cargar(proy), [proy.catalogos])

            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "perfiles": [],
                "catalogo_base": True,
            })
            self.assertTrue(configuracion(proy).catalogo_base)
            self.assertEqual(
                catalogos_base_a_cargar(proy), [modulo.RAIZ_ORACLE / "catalogos"])
            self.assertEqual(
                catalogos_a_cargar(proy),
                [modulo.RAIZ_ORACLE / "catalogos", proy.catalogos],
            )

    def test_oracle_json_roto_o_no_fisico_falla_cerrado(self) -> None:
        casos = (
            [],
            {"esquema": "oracle.proyecto/v0"},
            {"esquema": modulo.ESQUEMA_PROYECTO, "perfiles": "python"},
            {"esquema": modulo.ESQUEMA_PROYECTO, "perfiles": [1]},
            {"esquema": modulo.ESQUEMA_PROYECTO, "perfiles": [{"python": True}]},
            {"esquema": modulo.ESQUEMA_PROYECTO, "perfiles": [""]},
            {"esquema": modulo.ESQUEMA_PROYECTO, "perfiles": ["python", "python"]},
            {"esquema": modulo.ESQUEMA_PROYECTO, "catalogo_base": None},
            {"esquema": modulo.ESQUEMA_PROYECTO, "catalogo_base": 0},
            {"esquema": modulo.ESQUEMA_PROYECTO, "catalogo_base": "no"},
        )
        for datos in casos:
            with self.subTest(datos=datos), tempfile.TemporaryDirectory() as td:
                raiz = self._raiz(td)
                self._configurar(raiz, datos)
                with self.assertRaises(ProyectoInvalido):
                    configuracion(Proyecto(raiz))

        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            real = raiz / "configuracion-real.json"
            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO, "perfiles": ["python"],
            })
            (raiz / "oracle.json").replace(real)
            (raiz / "oracle.json").symlink_to(real)
            with self.assertRaisesRegex(ProyectoInvalido, "archivo físico"):
                configuracion(Proyecto(raiz))

        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            (raiz / "oracle.json").symlink_to(raiz / "ausente.json")
            with self.assertRaises(ProyectoInvalido):
                configuracion(Proyecto(raiz))

    def test_propiedades_presentacion_y_catalogos_son_exactos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            proy = Proyecto(raiz)
            self.assertEqual(proy.catalogos, raiz / "catalogos")
            self.assertEqual(proy.corpus, raiz / "corpus")
            self.assertEqual(proy.diferencial, raiz / "diferencial")
            self.assertFalse(proy.es_el_propio_oracle)
            self.assertEqual(str(proy), str(raiz))

            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO, "perfiles": ["python"],
            })
            esperadas = [
                perfiles_incluidos()["python"],
            ]
            self.assertEqual(catalogos_base_a_cargar(proy), esperadas)
            self.assertEqual(catalogos_a_cargar(proy), [*esperadas, proy.catalogos])

        propio = Proyecto(modulo.RAIZ_ORACLE)
        self.assertTrue(propio.es_el_propio_oracle)
        self.assertEqual(str(propio), "oracle (sí mismo)")
        self.assertEqual(catalogos_a_cargar(propio), catalogos_base_a_cargar(propio))

    def test_una_instalacion_sin_autocertificacion_exige_proyecto_explicito(self) -> None:
        with tempfile.TemporaryDirectory() as td_instalacion, tempfile.TemporaryDirectory() as td_cwd:
            instalacion, cwd = Path(td_instalacion), Path(td_cwd)
            (instalacion / "catalogos").mkdir()
            with (mock.patch.object(modulo, "RAIZ_ORACLE", instalacion),
                  mock.patch.object(Path, "cwd", return_value=cwd),
                  mock.patch.dict(os.environ, {}, clear=True)):
                with self.assertRaisesRegex(ProyectoInvalido, "--proyecto"):
                    resolver([])

    def test_los_perfiles_se_descubren_sin_registro_de_nombres_en_el_nucleo(self) -> None:
        with tempfile.TemporaryDirectory() as td_oracle, tempfile.TemporaryDirectory() as td_proyecto:
            raiz_oracle = Path(td_oracle)
            (raiz_oracle / "catalogos").mkdir()
            catalogo_perfil = raiz_oracle / "perfiles" / "lenguaje_nuevo" / "catalogos"
            catalogo_perfil.mkdir(parents=True)
            raiz_proyecto = self._raiz(td_proyecto)
            self._configurar(raiz_proyecto, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "perfiles": ["lenguaje_nuevo"],
            })

            with mock.patch.object(modulo, "RAIZ_ORACLE", raiz_oracle):
                self.assertEqual(perfiles_incluidos(), {"lenguaje_nuevo": catalogo_perfil})
                self.assertEqual(
                    catalogos_base_a_cargar(Proyecto(raiz_proyecto)),
                    [catalogo_perfil],
                )

    def test_un_host_puede_aportar_raices_de_perfiles_sin_modificar_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as td_proyecto, tempfile.TemporaryDirectory() as td_fuente:
            raiz_proyecto = self._raiz(td_proyecto)
            fuente = Path(td_fuente)
            catalogo = fuente / "dominio_externo" / "catalogos"
            catalogo.mkdir(parents=True)
            self._configurar(raiz_proyecto, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "perfiles": ["dominio_externo"],
                "catalogo_base": False,
            })
            proy = Proyecto(raiz_proyecto)

            with self.assertRaisesRegex(ProyectoInvalido, "desconocidos"):
                catalogos_a_cargar(proy)
            self.assertEqual(perfiles_incluidos((fuente,))["dominio_externo"], catalogo)
            self.assertEqual(
                catalogos_base_a_cargar(proy, raices_perfiles=(fuente,)), [catalogo])
            self.assertEqual(
                catalogos_a_cargar(proy, raices_perfiles=(fuente,)),
                [catalogo, proy.catalogos],
            )

    def test_raices_externas_rechazan_ambiguedad_y_rutas_no_fisicas(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            raiz_a, raiz_b = Path(a), Path(b)
            (raiz_a / "repetido" / "catalogos").mkdir(parents=True)
            (raiz_b / "repetido" / "catalogos").mkdir(parents=True)
            with self.assertRaisesRegex(ProyectoInvalido, "repetido"):
                perfiles_incluidos((raiz_a, raiz_b))

            enlace = raiz_a / "enlace-a-raiz"
            enlace.symlink_to(raiz_b, target_is_directory=True)
            with self.assertRaisesRegex(ProyectoInvalido, "raíz de perfiles"):
                perfiles_incluidos((enlace,))

            ausente = raiz_a / "ausente"
            with self.assertRaisesRegex(ProyectoInvalido, "raíz de perfiles"):
                perfiles_incluidos((ausente,))

    def test_descubrir_perfiles_falla_cerrado_ante_raices_y_entradas_no_fisicas(self) -> None:
        with tempfile.TemporaryDirectory() as td_oracle, tempfile.TemporaryDirectory() as td_fuera:
            raiz_oracle = Path(td_oracle)
            with mock.patch.object(modulo, "RAIZ_ORACLE", raiz_oracle):
                self.assertEqual(perfiles_incluidos(), {})

            (raiz_oracle / "perfiles").mkdir()
            with (mock.patch.object(modulo, "RAIZ_ORACLE", raiz_oracle),
                  mock.patch.object(Path, "resolve", side_effect=OSError("sin acceso"))):
                self.assertEqual(perfiles_incluidos(), {})

            perfiles = raiz_oracle / "perfiles"
            (perfiles / "NombreInvalido" / "catalogos").mkdir(parents=True)
            perfil_externo = Path(td_fuera) / "externo"
            (perfil_externo / "catalogos").mkdir(parents=True)
            (perfiles / "enlace").symlink_to(perfil_externo, target_is_directory=True)
            with mock.patch.object(modulo, "RAIZ_ORACLE", raiz_oracle):
                self.assertEqual(perfiles_incluidos(), {})

            perfiles.rename(raiz_oracle / "perfiles-reales")
            (raiz_oracle / "perfiles").symlink_to(
                raiz_oracle / "perfiles-reales", target_is_directory=True)
            with mock.patch.object(modulo, "RAIZ_ORACLE", raiz_oracle):
                self.assertEqual(perfiles_incluidos(), {})

    def test_escalares_externas_son_opt_in_incluso_al_omitir_la_bandera(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            marca = raiz / "ejecutada"
            (raiz / "escalares.py").write_text(
                f"from pathlib import Path\nPath({str(marca)!r}).write_text('sí')\n",
                encoding="utf-8")

            with self.assertRaises(EscalaresNoConfiables):
                with escalares_del_proyecto(Proyecto(raiz)):
                    pass
            self.assertFalse(marca.exists())

    def test_un_registro_de_instancia_revierte_si_falla_el_cuerpo_del_contexto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            (raiz / "escalares.py").write_text(
                "from nucleo.algebra import escalar\n"
                "@escalar('udf_transaccional')\n"
                "def udf(valor): return valor\n",
                encoding="utf-8",
            )
            registro = algebra.RegistroEscalares()

            with self.assertRaisesRegex(RuntimeError, "fallo posterior"):
                with escalares_del_proyecto(
                        Proyecto(raiz), confiar=True, registro=registro):
                    self.assertIn("udf_transaccional", registro)
                    raise RuntimeError("fallo posterior")

            self.assertEqual(registro, {})

    def test_escalares_rechaza_symlink_aun_si_apunta_dentro_del_proyecto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            real = raiz / "escalares-reales.py"
            real.write_text("", encoding="utf-8")
            (raiz / "escalares.py").symlink_to(real)
            with self.assertRaisesRegex(EscalaresInvalidas, "archivo físico"):
                with escalares_del_proyecto(Proyecto(raiz), confiar=True):
                    pass

    def test_escalares_rechaza_un_spec_incompleto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            (raiz / "escalares.py").write_text("", encoding="utf-8")
            for spec in (None, SimpleNamespace(loader=None)):
                with self.subTest(spec=spec), mock.patch(
                        "importlib.util.spec_from_file_location", return_value=spec):
                    with self.assertRaisesRegex(EscalaresInvalidas, "preparar"):
                        with escalares_del_proyecto(Proyecto(raiz), confiar=True):
                            pass

    def test_estructura_rechaza_componentes_desconocidos_y_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            proy = Proyecto(raiz)
            with self.assertRaisesRegex(ValueError, "desconocidos"):
                problemas_estructura(proy, ("plugins",))
            self.assertEqual(
                problemas_estructura(proy, ("catalogos", "corpus")),
                ["falta `corpus/`"])

            real = raiz / "corpus-real"
            real.mkdir()
            (raiz / "corpus").symlink_to(real, target_is_directory=True)
            self.assertEqual(
                problemas_estructura(proy, ("corpus",)),
                ["`corpus/` no puede ser un symlink"])

    def test_ruta_de_medida_valida_es_exacta_y_los_ids_invalidos_se_rechazan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            proy = Proyecto(raiz)
            self.assertEqual(
                ruta_de_medida_nueva(proy, "dominio.nombre_compuesto"),
                raiz / "catalogos" / "dominio" / "dominio.nombre_compuesto.json")
            for mid in (None, 1, "Dominio.nombre", "dominio", "dominio..nombre"):
                with self.subTest(mid=mid), self.assertRaises(ProyectoInvalido):
                    ruta_de_medida_nueva(proy, mid)

    def test_presentar_ruta_distingue_rutas_internas_y_externas_aun_si_no_existen(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as otro:
            raiz = self._raiz(td)
            proy = Proyecto(raiz)
            self.assertEqual(presentar_ruta(proy, raiz / "futura.json"), "futura.json")
            externa = Path(otro) / "futura.json"
            self.assertEqual(presentar_ruta(proy, externa), str(externa.resolve()))

    def test_resolver_respeta_precedencia_y_valida_cada_origen(self) -> None:
        with (tempfile.TemporaryDirectory() as explicito,
              tempfile.TemporaryDirectory() as entorno,
              tempfile.TemporaryDirectory() as actual,
              tempfile.TemporaryDirectory() as invalido):
            ruta_explicita = self._raiz(explicito)
            ruta_entorno = self._raiz(entorno)
            ruta_actual = self._raiz(actual)
            ruta_invalida = Path(invalido)

            with (mock.patch.dict(os.environ, {"ORACLE_PROYECTO": str(ruta_entorno)}),
                  mock.patch.object(modulo.Path, "cwd", return_value=ruta_actual)):
                self.assertEqual(
                    resolver(["--proyecto", str(ruta_explicita)]), Proyecto(ruta_explicita))
                self.assertEqual(resolver([]), Proyecto(ruta_entorno))

            with (mock.patch.dict(os.environ, {}, clear=True),
                  mock.patch.object(modulo.Path, "cwd", return_value=ruta_actual)):
                self.assertEqual(resolver([]), Proyecto(ruta_actual))

            with (mock.patch.dict(os.environ, {}, clear=True),
                  mock.patch.object(modulo.Path, "cwd", return_value=ruta_invalida)):
                self.assertEqual(resolver([]), Proyecto(modulo.RAIZ_ORACLE))

            with self.assertRaisesRegex(ProyectoInvalido, "necesita una ruta"):
                resolver(["--proyecto"])
            with self.assertRaisesRegex(ProyectoInvalido, "falta `catalogos/`"):
                resolver(["--proyecto", str(ruta_invalida)])
            with (mock.patch.dict(os.environ, {"ORACLE_PROYECTO": str(ruta_invalida)}),
                  self.assertRaisesRegex(ProyectoInvalido, "ORACLE_PROYECTO")):
                resolver([])

    def test_helpers_de_argumentos_preservan_lo_ajeno(self) -> None:
        argv = ["--proyecto", "/tmp/proyecto", "--hechos", "--confiar-escalares"]
        self.assertTrue(modulo.confiar_escalares(argv))
        self.assertFalse(modulo.confiar_escalares(["--hechos"]))
        self.assertEqual(modulo.sin_bandera(argv), ["--hechos", "--confiar-escalares"])
        self.assertEqual(modulo.sin_banderas_comunes(argv), ["--hechos"])


if __name__ == "__main__":
    unittest.main()
