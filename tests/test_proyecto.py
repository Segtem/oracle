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
            configuracion_vacia.bibliotecas = ("tercero.calidad",)
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
            {"esquema": modulo.ESQUEMA_PROYECTO, "bibliotecas": "tercero.calidad"},
            {"esquema": modulo.ESQUEMA_PROYECTO, "bibliotecas": [1]},
            {"esquema": modulo.ESQUEMA_PROYECTO, "bibliotecas": ["invalida"]},
            {"esquema": modulo.ESQUEMA_PROYECTO,
             "bibliotecas": ["tercero.calidad", "tercero.calidad"]},
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

    def test_instalar_no_activa_una_biblioteca(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            proy = Proyecto(raiz)
            self._configurar(raiz, {"esquema": modulo.ESQUEMA_PROYECTO})
            with mock.patch(
                    "nucleo.biblioteca.descubrir_bibliotecas",
                    side_effect=AssertionError("no se debe descubrir lo no seleccionado")):
                self.assertEqual(catalogos_a_cargar(proy), [proy.catalogos])

    def test_selecciona_catalogos_relaciones_y_macros_de_una_biblioteca(self) -> None:
        macro = ["defmacro", "externa", ["id"], [],
                 ["medida", ["$", "id"],
                  ["desde", ["de", "item", "i"]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, "contrato", "porque"],
                  ["alcance", "NO ve nada fuera de item"]]]
        relacion = ["relacion", "item",
                    ["campos", ["campo", "id", "texto", "sin_unidad"]],
                    ["alcance", "NO dice de dónde vino el item"]]
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            biblioteca = raiz / "instalada"
            catalogos = biblioteca / "catalogos"
            relaciones = biblioteca / "relaciones"
            macros = biblioteca / "macros"
            corpus = biblioteca / "corpus"
            for directorio in (catalogos, relaciones, macros, corpus):
                directorio.mkdir(parents=True)
            (relaciones / "item.json").write_text(json.dumps(relacion), encoding="utf-8")
            (macros / "externa.json").write_text(json.dumps(macro), encoding="utf-8")
            manifiesto = SimpleNamespace(
                id="tercero.calidad", catalogos=(catalogos,), relaciones=(relaciones,),
                macros=(macros,), corpus=(corpus,))
            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "bibliotecas": ["tercero.calidad"],
            })
            proy = Proyecto(raiz)

            with mock.patch(
                    "nucleo.biblioteca.descubrir_bibliotecas",
                    return_value={"tercero.calidad": manifiesto}):
                config = configuracion(proy)
                self.assertEqual(config.bibliotecas, ("tercero.calidad",))
                self.assertEqual(catalogos_base_a_cargar(proy), [catalogos])
                self.assertEqual(catalogos_a_cargar(proy), [catalogos, proy.catalogos])
                self.assertEqual(set(modulo.relaciones_del_proyecto(proy)), {"item"})
                self.assertIn("externa", modulo.macros_del_proyecto(proy))

    def test_una_biblioteca_seleccionada_tiene_que_estar_instalada(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "bibliotecas": ["tercero.ausente"],
            })
            with (mock.patch("nucleo.biblioteca.descubrir_bibliotecas", return_value={}),
                  self.assertRaisesRegex(ProyectoInvalido, "bibliotecas no instaladas")):
                catalogos_a_cargar(Proyecto(raiz))

    def test_oracle_no_carga_sus_relaciones_dos_veces_como_base_y_proyecto(self) -> None:
        relacion = ["relacion", "item",
                    ["campos", ["campo", "id", "texto", "sin_unidad"]],
                    ["alcance", "NO dice de dónde vino el item"]]
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            (raiz / "relaciones").mkdir()
            (raiz / "relaciones" / "item.json").write_text(
                json.dumps(relacion), encoding="utf-8")
            self._configurar(raiz, {
                "esquema": modulo.ESQUEMA_PROYECTO,
                "catalogo_base": True,
            })
            with mock.patch.object(modulo, "RAIZ_ORACLE", raiz):
                relaciones = modulo.relaciones_del_proyecto(Proyecto(raiz))
        self.assertEqual(set(relaciones), {"item"})

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

    def test_un_registro_de_instancia_no_deja_sucio_el_registro_global(self) -> None:
        nombre = "udf_global_sucia_temporal"
        self.assertNotIn(nombre, algebra.ESCALARES)
        self.addCleanup(algebra.ESCALARES.pop, nombre, None)

        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            (raiz / "escalares.py").write_text("", encoding="utf-8")
            registro = algebra.RegistroEscalares()

            with escalares_del_proyecto(Proyecto(raiz), confiar=True, registro=registro):
                algebra.ESCALARES[nombre] = lambda: "sucia"
                self.assertIn(nombre, algebra.ESCALARES)

            self.assertEqual(registro, {})
            self.assertNotIn(nombre, algebra.ESCALARES)

    def test_los_metadatos_se_filtran_y_esta_declarado(self) -> None:
        """Fija el límite REAL del confinamiento, incluida la fuga. No es un test que celebra.

        El hook de auditoría niega leer el CONTENIDO de archivos de afuera, escribir afuera, red y
        procesos —eso lo fija el test de abajo—. Lo que NO detiene son los METADATOS: `os.stat`,
        `os.path.exists`, `os.access` y todo lo que se apoya en ellos funcionan sobre cualquier ruta.
        Una UDF hostil puede averiguar si existe `~/.ssh/id_rsa`, leer tamaños, permisos y fechas, y
        devolverlo como resultado por el canal JSON.

        **No es un descuido: `os.stat` no emite ningún evento auditable en CPython.** PEP 578 cubre
        `open`, `os.listdir`, `os.scandir`, los que mutan el árbol, los procesos y los sockets, pero
        no la consulta de metadatos. Un `sys.addaudithook` no puede interceptar lo que nadie anuncia.

        Este test existe para que el límite no envejezca en silencio en ninguna de las dos
        direcciones: si algún día la fuga se cierra de verdad, ESTE TEST FALLA y obliga a actualizar
        la declaración del módulo, en vez de dejarla diciendo de menos.
        """
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            raiz = self._raiz(td)
            exterior = Path(afuera)
            centinela = exterior / "centinela.txt"
            centinela.write_text("secreto", encoding="utf-8")
            (raiz / "escalares.py").write_text(
                "import os\n"
                "from nucleo.algebra import escalar\n"
                "estado = {}\n"
                f"ruta = {str(centinela)!r}\n"
                "for nombre, fn in ((\'existe\', lambda: os.path.exists(ruta)),\n"
                "                   (\'tamano\', lambda: os.stat(ruta).st_size),\n"
                "                   (\'contenido\', lambda: open(ruta).read())):\n"
                "    try:\n"
                "        estado[nombre] = fn()\n"
                "    except BaseException as e:\n"
                "        estado[nombre] = type(e).__name__\n"
                "@escalar(\'sonda_limite\')\n"
                "def sonda_limite():\n"
                "    return estado\n",
                encoding="utf-8",
            )
            with escalares_del_proyecto(Proyecto(raiz), confiar=True):
                estado = algebra.ESCALARES["sonda_limite"]()

        # Lo que el confinamiento SÍ detiene: el contenido.
        self.assertEqual(estado["contenido"], "PermissionError")
        # Lo que NO detiene, y queda fijado como límite conocido:
        self.assertIs(estado["existe"], True,
                      "si esto falla, la fuga de metadatos se cerró: actualizá el docstring de "
                      "nucleo/aislamiento/escalares.py y este test")
        self.assertEqual(estado["tamano"], len("secreto"),
                         "si esto falla, `os.stat` dejó de pasar: actualizá la declaración")

    def test_escalares_confiadas_no_leen_ni_escriben_afuera_ni_crean_procesos(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            raiz = self._raiz(td)
            exterior = Path(afuera)
            centinela = exterior / "centinela.txt"
            escritura = exterior / "escritura.txt"
            pid = raiz / "proceso.pid"
            centinela.write_text("secreto", encoding="utf-8")
            (raiz / "escalares.py").write_text(
                "from pathlib import Path\n"
                "import subprocess\n"
                "import sys\n"
                "from nucleo.algebra import escalar\n"
                "estado = {}\n"
                f"centinela = Path({str(centinela)!r})\n"
                f"escritura = Path({str(escritura)!r})\n"
                f"pid = Path({str(pid)!r})\n"
                "try:\n"
                "    estado['lectura'] = centinela.read_text(encoding='utf-8')\n"
                "except BaseException as e:\n"
                "    estado['lectura'] = type(e).__name__\n"
                "try:\n"
                "    escritura.write_text('afuera', encoding='utf-8')\n"
                "    estado['escritura'] = 'escribió'\n"
                "except BaseException as e:\n"
                "    estado['escritura'] = type(e).__name__\n"
                "try:\n"
                "    p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
                "    pid.write_text(str(p.pid), encoding='utf-8')\n"
                "    estado['proceso'] = 'creado'\n"
                "except BaseException as e:\n"
                "    estado['proceso'] = type(e).__name__\n"
                "@escalar('estado_aislamiento')\n"
                "def estado_aislamiento():\n"
                "    return estado\n",
                encoding="utf-8",
            )

            with escalares_del_proyecto(Proyecto(raiz), confiar=True):
                estado = algebra.ESCALARES["estado_aislamiento"]()

            self.assertEqual(estado["lectura"], "PermissionError")
            self.assertEqual(estado["escritura"], "PermissionError")
            self.assertEqual(estado["proceso"], "PermissionError")
            self.assertFalse(escritura.exists())
            self.assertFalse(pid.exists())

    def test_escalares_rechaza_symlink_aun_si_apunta_dentro_del_proyecto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            real = raiz / "escalares-reales.py"
            real.write_text("", encoding="utf-8")
            (raiz / "escalares.py").symlink_to(real)
            with self.assertRaisesRegex(EscalaresInvalidas, "archivo físico"):
                with escalares_del_proyecto(Proyecto(raiz), confiar=True):
                    pass

    def test_escalares_rechaza_un_modulo_con_error_de_sintaxis(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            (raiz / "escalares.py").write_text("def rota(:\n", encoding="utf-8")
            with self.assertRaisesRegex(EscalaresInvalidas, "SyntaxError"):
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
                raiz / "catalogos" / "dominio" / "dominio.nombre_compuesto.oracle")
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


class SombraDeclarada(unittest.TestCase):
    """`sombra` en `oracle.json`: qué medidas se miden pero todavía no obligan."""

    def _leer(self, valor):
        from nucleo.proyecto import _sombra_declarada
        return _sombra_declarada({"sombra": valor})

    def test_sin_sombra_la_lista_viene_vacia(self) -> None:
        from nucleo.proyecto import _sombra_declarada
        self.assertEqual(_sombra_declarada({}), ())

    def test_lee_fecha_y_motivo_y_ordena_por_id(self) -> None:
        """El orden estable evita que dos corridas del mismo proyecto se lean distinto."""
        entradas = self._leer({"m.b": {"desde": "2026-01-02", "porque": "x"},
                               "m.a": {"desde": "2026-01-01", "porque": "y"}})
        self.assertEqual([e.medida for e in entradas], ["m.a", "m.b"])
        self.assertEqual(entradas[0].porque, "y")

    def test_los_espacios_se_recortan(self) -> None:
        entrada, = self._leer({"m.a": {"desde": "  2026-01-01 ", "porque": "  x  "}})
        self.assertEqual((entrada.desde, entrada.porque), ("2026-01-01", "x"))

    def test_una_entrada_sin_campos_se_acepta_y_la_juzga_una_medida(self) -> None:
        """El lector NO exige `desde` ni `porque`: eso lo exige
        `meta.toda_sombra_declara_desde_y_porque`. Escribir la regla en los dos lados haría que
        una de las dos envejeciera."""
        entrada, = self._leer({"m.a": {}})
        self.assertEqual((entrada.desde, entrada.porque), ("", ""))

    def test_falla_cerrado_ante_formas_que_no_entiende(self) -> None:
        from nucleo.proyecto import ProyectoInvalido
        for valor in (["m.a"], "m.a", {"m.a": "porque sí"}, {"m.a": ["x"]},
                      {"": {}}, {"   ": {}}, {"m.a": {"desde": 3}},
                      {"m.a": {"porque": None}}):
            with self.subTest(valor=valor), self.assertRaises(ProyectoInvalido):
                self._leer(valor)

    def test_una_entrada_de_sombra_no_se_puede_modificar_despues(self) -> None:
        """Es lo que el proyecto DECLARÓ. Si un consumidor pudiera reescribir la fecha o el
        motivo en memoria, la antigüedad que se imprime dejaría de ser la declarada."""
        import dataclasses
        from nucleo.proyecto import EnSombra
        entrada = EnSombra("m.a", "2026-09-01", "x")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            entrada.desde = "2020-01-01"

    def test_la_configuracion_del_proyecto_la_expone(self) -> None:
        import json
        from nucleo.proyecto import Proyecto, configuracion
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1",
                "sombra": {"meta.x": {"desde": "2026-09-01", "porque": "en transición"}},
            }), encoding="utf-8")
            config = configuracion(Proyecto(raiz))
        self.assertEqual([e.medida for e in config.sombra], ["meta.x"])
        self.assertEqual(config.sombra[0].porque, "en transición")
