"""`--con` repetible en `oracle juzgar` y `oracle cobertura`: un candidato integrado tiene un sensor por frente.

Cada relación la aporta un solo archivo: si dos traen la misma, es un solapamiento de interfaz entre frentes que
Git no ve (la medida de uno contaría filas del otro), y se rechaza en vez de combinarlas.
"""

from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import unittest

from tests.test_juzgar import POLITICA_LECTURA, POLITICA_REFERENCIAS, BaseJuzgarTest, _fila_referencia
from tests import test_requisito as _requisito  # el módulo, no la clase: sus pruebas no se corren dos veces

LECTURA = {"esquema": "oracle.tareas.hechos/v1", "completa": True, "git": "no_solicitado", "head": ""}


class JuzgarVarios(BaseJuzgarTest):
    def juzgar(self, *rutas: Path) -> tuple[int, str, str]:
        argv = ["juzgar"]
        for ruta in rutas:
            argv += ["--con", str(ruta)]
        return self.correr_cli(*argv, "--proyecto", str(self.proyecto),
                               "--medida", POLITICA_REFERENCIAS, "--medida", POLITICA_LECTURA)

    def test_dos_archivos_con_relaciones_distintas_juzgan_como_uno(self) -> None:
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia("ausente", "falta.png")]}, "a.json")
        b = self.escribir_evidencia({"lectura_seguimiento": [LECTURA]}, "b.json")
        juntos = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia("ausente", "falta.png")],
                                          "lectura_seguimiento": [LECTURA]}, "juntos.json")
        esperado = self.juzgar(juntos)
        self.assertEqual(esperado[0], 1, esperado)  # rojo por la referencia ausente: el combinado se evalúa de verdad
        self.assertEqual(self.juzgar(a, b), esperado)
        self.assertEqual(self.juzgar(b, a), esperado)  # el orden de los archivos no cambia el veredicto

    def test_la_misma_relacion_en_dos_archivos_se_rechaza(self) -> None:
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]}, "a.json")
        b = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()],
                                     "lectura_seguimiento": [LECTURA]}, "b.json")
        rc, out, err = self.juzgar(a, b)
        self.assertEqual(rc, 2, out + err)
        self.assertIn(f"la relación «referencia_seguimiento» viene en «{a}» y en «{b}»", err)
        self.assertIn("dos sensores emiten la misma relación", err)
        self.assertEqual(out, "")

    def test_el_mismo_archivo_dos_veces_se_rechaza(self) -> None:
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]}, "a.json")
        (self.temporal / "sub").mkdir()  # «sub/../a.json» es el mismo archivo con otro nombre
        rc, out, err = self.correr_cli("juzgar", "--con", str(a), "--con", str(self.temporal / "sub" / ".." / "a.json"),
                                       "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2, out + err)
        self.assertIn("está dos veces en `--con`", err)

    def test_un_enlace_duro_al_mismo_archivo_tambien_es_el_mismo(self) -> None:
        for contenido in ({}, {"referencia_seguimiento": [_fila_referencia()]}):
            with self.subTest(contenido=contenido):
                a = self.escribir_evidencia(contenido, "a.json")
                duro = self.temporal / "duro.json"
                duro.unlink(missing_ok=True)
                os.link(a, duro)
                rc, out, err = self.correr_cli("juzgar", "--con", str(a), "--con", str(duro),
                                               "--proyecto", str(self.proyecto))
                self.assertEqual(rc, 2, out + err)
                self.assertIn(f"el archivo «{duro}» está dos veces en `--con` (también como «{a}»)", err)

    def test_un_enlace_simbolico_al_mismo_archivo_tambien_es_el_mismo(self) -> None:
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]}, "a.json")
        simbolico = self.temporal / "simbolico.json"
        simbolico.symlink_to(a)
        rc, out, err = self.correr_cli("juzgar", "--con", str(a), "--con", str(simbolico),
                                       "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2, out + err)
        self.assertIn(f"el archivo «{simbolico}» está dos veces en `--con` (también como «{a}»)", err)

    def test_una_relacion_rota_que_ninguna_medida_usa_da_lo_mismo_que_un_archivo(self) -> None:
        # Sin medidas aplicables, un archivo con un null no se valida; varios archivos tampoco (agy H01).
        a = self.escribir_evidencia({"otra": [{"x": 1}]}, "a.json")
        b = self.escribir_evidencia({"accesoria": [{"x": None}]}, "b.json")
        juntos = self.escribir_evidencia({"otra": [{"x": 1}], "accesoria": [{"x": None}]}, "juntos.json")
        def sin_rutas(r):
            return r[0], r[1], r[2].replace(str(self.temporal), "T")
        esperado = sin_rutas(self.correr_cli("juzgar", "--con", str(juntos), "--proyecto", str(self.proyecto)))
        self.assertEqual(esperado[0], 1, esperado)
        self.assertEqual(sin_rutas(self.correr_cli("juzgar", "--con", str(a), "--con", str(b), "--proyecto",
                                                   str(self.proyecto))), esperado)

    def test_el_solapamiento_se_ve_aunque_un_archivo_traiga_una_cabecera_rota(self) -> None:
        # codex-1: la relación repetida se nombra antes que el error de la cabecera del segundo archivo.
        a = self.escribir_evidencia({"r": [["clave", ["id"]], {"id": "a"}]}, "a.json")
        b = self.escribir_evidencia({"r": [["clave", ["id", "id"]], {"id": "b"}]}, "b.json")
        rc, out, err = self.correr_cli("juzgar", "--con", str(a), "--con", str(b), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2, out + err)
        self.assertIn(f"la relación «r» viene en «{a}» y en «{b}»", err)

    def test_un_error_de_la_evidencia_entre_varios_nombra_el_archivo(self) -> None:
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]}, "a.json")
        b = self.escribir_evidencia({"lectura_seguimiento": [{**LECTURA, "head": None}]}, "b.json")
        rc, out, err = self.juzgar(a, b)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("ERROR AL EVALUAR", err)
        self.assertIn("null explícito", err)
        self.assertIn(f"(en «{b}»)", err)
        # Con un solo archivo el mensaje es el de siempre.
        rc, out, err = self.correr_cli("juzgar", "--con", str(b), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2, out + err)
        self.assertIn("ERROR AL EVALUAR", err)
        self.assertNotIn("(en «", err)

    def test_un_error_que_no_es_de_ningun_archivo_no_nombra_ninguno(self) -> None:
        from unittest.mock import patch
        from nucleo.algebra import ErrorDeAlgebra
        from tools import juzgar
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]}, "a.json")
        b = self.escribir_evidencia({"lectura_seguimiento": [LECTURA]}, "b.json")
        with patch.object(juzgar, "juzgar_evidencia", side_effect=ErrorDeAlgebra("falla del núcleo")):
            rc, out, err = self.juzgar(a, b)
        self.assertEqual((rc, err), (2, "ERROR AL EVALUAR — falla del núcleo\n"))

    def test_un_archivo_invalido_entre_varios_se_nombra(self) -> None:
        a = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]}, "a.json")
        b = self.escribir_evidencia("{roto", "b.json")
        rc, out, err = self.juzgar(a, b)
        self.assertEqual(rc, 2, out + err)
        self.assertIn(f"JSON inválido en «{b}»", err)


class CoberturaVarios(unittest.TestCase):
    _proyecto = _requisito.CoberturaTests._proyecto

    def cobertura(self, raiz: Path, *evidencias: dict) -> tuple[int, str]:
        from tools import cli
        argv = ["cobertura"]
        for i, evidencia in enumerate(evidencias):
            ruta = raiz / f"hechos-{i}.json"
            ruta.write_text(json.dumps(evidencia), encoding="utf-8")
            argv += ["--con", str(ruta)]
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(argv + ["--proyecto", str(raiz)])
        return codigo, salida.getvalue().replace(str(raiz), "RAIZ")

    def test_cobertura_con_varios_archivos(self) -> None:
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": _requisito.MEDIDO.replace(", openspec.b", "")})
        esperado = self.cobertura(raiz, {"corrida": [{"codigo": 1}], "otra": []})
        self.assertEqual(esperado[0], 1, esperado)  # no se cumple: la fila de corrida llegó desde el primer archivo
        self.assertEqual(self.cobertura(raiz, {"corrida": [{"codigo": 1}]}, {"otra": []}), esperado)
        codigo, texto = self.cobertura(raiz, {"corrida": [{"codigo": 0}]}, {"corrida": [{"codigo": 1}]})
        self.assertEqual(codigo, 1)
        self.assertIn("la relación «corrida» viene en «RAIZ/hechos-0.json» y en «RAIZ/hechos-1.json»", texto)

    def test_cobertura_rechaza_lo_mismo_que_juzgar(self) -> None:
        from nucleo.proyecto import Proyecto
        from tools import cli, cobertura
        raiz = self._proyecto({"cli_validate.rutas_de_archivo.requisito": _requisito.MEDIDO.replace(", openspec.b", "")})
        a = raiz / "a.json"
        a.write_text(json.dumps({"corrida": [{"codigo": 0}]}), encoding="utf-8")
        (raiz / "sub").mkdir()
        roto = raiz / "roto.json"
        roto.write_text("{roto", encoding="utf-8")
        for rutas, esperado in (([a, raiz / "sub" / ".." / "a.json"], "está dos veces en `--con`"),
                                ([a, roto], f"JSON inválido en «{roto}»")):
            with self.subTest(esperado=esperado), redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(cobertura.main(Proyecto(raiz), con=[str(r) for r in rutas]), 1)
            self.assertIn(esperado, salida.getvalue())
        # Una bandera donde va la ruta, también con una cantidad par de argumentos.
        with redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(cli.main(["cobertura", "--con", "--rara", "--proyecto", str(raiz)]), 1)
        self.assertIn("uso: oracle cobertura [--con <hechos.json>]...", salida.getvalue())
        # Un null en uno de varios archivos: la medida no juzga, y se dice de qué archivo vino.
        nulo = raiz / "nulo.json"
        nulo.write_text(json.dumps({"corrida": [{"codigo": None}]}), encoding="utf-8")
        otro = raiz / "otro.json"
        otro.write_text(json.dumps({"otra": []}), encoding="utf-8")
        with redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(cobertura.main(Proyecto(raiz), con=[str(otro), str(nulo)]), 1)
        self.assertIn(f"null explícito en la fila 0, campo «codigo» (en «{nulo}»)", salida.getvalue())
        # Una lista vacía es «sin evidencia», no evidencia vacía.
        with redirect_stdout(io.StringIO()) as sin:
            cobertura.main(Proyecto(raiz))
        with redirect_stdout(io.StringIO()) as vacia:
            cobertura.main(Proyecto(raiz), con=[])
        self.assertEqual(vacia.getvalue(), sin.getvalue())


if __name__ == "__main__":
    unittest.main()
