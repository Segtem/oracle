"""Tests unitarios para nucleo/relacion.py (Nivel L−1)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from nucleo.relacion import (
    Campo,
    Relacion,
    RelacionMalDeclarada,
    cargar,
    cargar_fuente_relacion,
    cargar_relaciones,
    como_hechos,
    hechos_de_relaciones,
    rutas_de_relaciones,
)


class RelacionTests(unittest.TestCase):
    def _datos_base(self):
        return [
            "relacion",
            "pieza",
            [
                "campos",
                ["campo", "id", "texto", "sin_unidad"],
                ["campo", "ox", "flotante", "cm"],
            ],
            ["alcance", "no ve la malla real"],
        ]

    def test_inmutabilidad_dataclasses(self) -> None:
        c = Campo("id", "texto", "sin_unidad")
        with self.assertRaises(FrozenInstanceError):
            c.nombre = "otro"  # type: ignore

        r = Relacion.de_datos(self._datos_base())
        with self.assertRaises(FrozenInstanceError):
            r.nombre = "otro"  # type: ignore

    def test_construccion_canonica_y_a_datos(self) -> None:
        datos = self._datos_base()
        r = Relacion.de_datos(datos)
        self.assertEqual(r.nombre, "pieza")
        self.assertEqual(r.alcance, "no ve la malla real")
        self.assertEqual(len(r.campos), 2)

        c0, c1 = r.campos
        self.assertEqual(c0.nombre, "id")
        self.assertEqual(c0.tipo, "texto")
        self.assertEqual(c0.unidad, "sin_unidad")
        self.assertTrue(c0.es_sin_unidad)
        self.assertFalse(c0.es_magnitud)
        self.assertEqual(c0.a_datos(), ["campo", "id", "texto", "sin_unidad"])

        self.assertEqual(c1.nombre, "ox")
        self.assertEqual(c1.tipo, "flotante")
        self.assertEqual(c1.unidad, "cm")
        self.assertFalse(c1.es_sin_unidad)
        self.assertTrue(c1.es_magnitud)
        self.assertEqual(c1.a_datos(), ["campo", "ox", "flotante", "cm"])

        self.assertEqual(r.a_datos(), datos)

    def test_rechaza_forma_no_lista_o_longitud_incorrecta(self) -> None:
        invalidas = [
            "no es lista",
            123,
            ["relacion", "pieza"],
            ["relacion", "pieza", ["campos"], ["alcance", "x"], "sobra"],
            ["otra_cosa", "pieza", ["campos", ["campo", "a", "texto", "sin_unidad"]], ["alcance", "x"]],
        ]
        for d in invalidas:
            with self.subTest(datos=d), self.assertRaises(RelacionMalDeclarada):
                Relacion.de_datos(d)

    def test_rechaza_nombre_de_relacion_invalido(self) -> None:
        nombres = ["", "   ", "Pieza", "pieza-1", "pieza.a", "1pieza", None, 42]
        for n in nombres:
            d = ["relacion", n, ["campos", ["campo", "id", "texto", "sin_unidad"]], ["alcance", "x"]]
            with self.subTest(nombre=n), self.assertRaises(RelacionMalDeclarada):
                Relacion.de_datos(d)

    def test_rechaza_nodo_campos_invalido(self) -> None:
        invalidos = [
            "no es lista",
            [],
            ["otro_nodo"],
            ["campos"],  # sin campos declarados
        ]
        for c in invalidos:
            d = ["relacion", "pieza", c, ["alcance", "x"]]
            with self.subTest(campos=c):
                with self.assertRaises(RelacionMalDeclarada) as cm:
                    Relacion.de_datos(d)
                if c == []:
                    self.assertIn("campos", str(cm.exception))

    def test_rechaza_item_campo_malformado(self) -> None:
        items = [
            "no_es_lista",
            ["campo", "id", "texto"],  # falta unidad
            ["campo", "id", "texto", "sin_unidad", "sobra"],
            ["otro_tag", "id", "texto", "sin_unidad"],
            ["campo", "ID_MAYUS", "texto", "sin_unidad"],  # nombre inválido
            ["campo", "", "texto", "sin_unidad"],
            ["campo", 123, "texto", "sin_unidad"],
            ["campo", "id", "tipo_inexistente", "sin_unidad"],  # tipo inválido
            ["campo", "id", 999, "sin_unidad"],
            ["campo", "id", "texto", ""],  # unidad vacía
            ["campo", "id", "texto", "   "],  # unidad espacios
            ["campo", "id", "texto", None],  # unidad None
        ]
        for item in items:
            d = ["relacion", "pieza", ["campos", item], ["alcance", "x"]]
            with self.subTest(item=item):
                with self.assertRaises(RelacionMalDeclarada) as cm:
                    Relacion.de_datos(d)
                if not (isinstance(item, list) and len(item) == 4 and item[0] == "campo"):
                    self.assertIn("pieza.campo[1]:", str(cm.exception))

    def test_rechaza_campos_duplicados(self) -> None:
        d = [
            "relacion",
            "pieza",
            [
                "campos",
                ["campo", "id", "texto", "sin_unidad"],
                ["campo", "id", "flotante", "cm"],
            ],
            ["alcance", "x"],
        ]
        with self.assertRaises(RelacionMalDeclarada) as cm:
            Relacion.de_datos(d)
        self.assertIn("repetido", str(cm.exception))

    def test_rechaza_alcance_invalido(self) -> None:
        alcances = [
            "no es lista",
            ["alcance"],
            ["alcance", ""],
            ["alcance", "   "],
            ["alcance", 123],
            ["otro_tag", "texto"],
            ["alcance", "texto", "sobra"],
        ]
        for a in alcances:
            d = ["relacion", "pieza", ["campos", ["campo", "id", "texto", "sin_unidad"]], a]
            with self.subTest(alcance=a), self.assertRaises(RelacionMalDeclarada):
                Relacion.de_datos(d)

    def test_carga_fuente_y_archivo(self) -> None:
        datos = self._datos_base()
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            p_json = raiz / "pieza.json"
            p_json.write_text(json.dumps(datos), encoding="utf-8")

            cargado = cargar(p_json)
            self.assertEqual(cargado.nombre, "pieza")
            self.assertEqual(cargar_fuente_relacion(p_json), datos)

            p_invalido = raiz / "invalido.json"
            p_invalido.write_text("{no es json}", encoding="utf-8")
            with self.assertRaises(RelacionMalDeclarada):
                cargar_fuente_relacion(p_invalido)

            p_txt = raiz / "pieza.txt"
            p_txt.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaises(RelacionMalDeclarada):
                cargar_fuente_relacion(p_txt)

            with self.assertRaises(RelacionMalDeclarada):
                cargar_fuente_relacion(raiz / "no_existe.json")

    def test_rutas_de_relaciones_y_cargar_relaciones(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            dir_a = raiz / "dir_a"
            dir_a.mkdir()
            (dir_a / "pieza.json").write_text(json.dumps(self._datos_base()), encoding="utf-8")

            d_evento = [
                "relacion", "evento",
                ["campos", ["campo", "t", "entero", "pasos"]],
                ["alcance", "traza"],
            ]
            dir_b = raiz / "dir_b"
            dir_b.mkdir()
            (dir_b / "evento.json").write_text(json.dumps(d_evento), encoding="utf-8")

            rutas = rutas_de_relaciones(dir_a, dir_b)
            self.assertEqual(len(rutas), 2)

            rels = cargar_relaciones(dir_a, dir_b)
            self.assertEqual(sorted(rels.keys()), ["evento", "pieza"])

            # Colección como argumento único
            rutas_col = rutas_de_relaciones([dir_a, dir_b])
            self.assertEqual(rutas, rutas_col)

            # Directorio inexistente devuelve vacío
            self.assertEqual(rutas_de_relaciones(raiz / "inexistente"), [])

    def test_rechaza_directorios_y_archivos_no_fisicos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            dir_real = raiz / "real"
            dir_real.mkdir()
            (dir_real / "pieza.json").write_text(json.dumps(self._datos_base()), encoding="utf-8")

            sym_dir = raiz / "sym_dir"
            os.symlink(dir_real, sym_dir)
            with self.assertRaises(RelacionMalDeclarada):
                rutas_de_relaciones(sym_dir)

            archivo_como_dir = dir_real / "pieza.json"
            with self.assertRaises(RelacionMalDeclarada):
                rutas_de_relaciones(archivo_como_dir)

            sym_file = dir_real / "sym_pieza.json"
            os.symlink(dir_real / "pieza.json", sym_file)
            with self.assertRaises(RelacionMalDeclarada):
                rutas_de_relaciones(dir_real)

    def test_cargar_relaciones_rechaza_duplicados(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            dir1 = raiz / "d1"
            dir2 = raiz / "d2"
            dir1.mkdir()
            dir2.mkdir()
            (dir1 / "p1.json").write_text(json.dumps(self._datos_base()), encoding="utf-8")
            (dir2 / "p2.json").write_text(json.dumps(self._datos_base()), encoding="utf-8")

            with self.assertRaises(RelacionMalDeclarada) as cm:
                cargar_relaciones(dir1, dir2)
            self.assertIn("dos veces", str(cm.exception))

    def test_reificacion_a_hechos(self) -> None:
        r = Relacion.de_datos(self._datos_base())
        hechos = hechos_de_relaciones([r])

        self.assertIn("relacion_declarada", hechos)
        self.assertIn("campo_declarado", hechos)

        rels = hechos["relacion_declarada"]
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0], {
            "relacion": "pieza",
            "campos": 2,
            "alcance": "no ve la malla real",
            "tiene_alcance": True,
        })

        campos = hechos["campo_declarado"]
        self.assertEqual(len(campos), 2)
        self.assertEqual(campos[0], {
            "relacion": "pieza",
            "campo": "id",
            "tipo": "texto",
            "unidad": "sin_unidad",
            "tiene_unidad": True,
            "es_magnitud": False,
            "es_sin_unidad": True,
        })
        self.assertEqual(campos[1], {
            "relacion": "pieza",
            "campo": "ox",
            "tipo": "flotante",
            "unidad": "cm",
            "tiene_unidad": True,
            "es_magnitud": True,
            "es_sin_unidad": False,
        })

        self.assertEqual(como_hechos([r]), hechos)

        with self.assertRaises(RelacionMalDeclarada):
            hechos_de_relaciones(["no es Relacion"])


if __name__ == "__main__":
    unittest.main()
