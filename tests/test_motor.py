import json
import re
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from nucleo.algebra import ESCALARES, ErrorDeAlgebra, LimitesAlgebra
from nucleo.medida import Medida
from nucleo.proyecto import EscalaresNoConfiables

RAIZ = Path(__file__).resolve().parents[1]

def setUpModule() -> None:
    """Importa la fachada pública DENTRO de la suite, no al descubrirla.

    `oracle_metalenguaje/__init__.py` alinea los nombres del checkout con los del wheel vía
    `cargar_interno`, y eso importa `catalogos`, que corre `@escalar`. Con el import al tope, un
    mutante en `escalar()`, `_registro()` o `_contrato_de_escalar()` rompía el **descubrimiento** de
    la suite entera y el arnés lo daba por «error» en vez de «muerte»: eran los últimos once
    mutantes sin veredicto de toda la ronda.

    Se inyectan en `globals()` en vez de reescribir cuarenta usos. La alternativa —volver perezoso el
    `cargar_interno` del paquete— tocaba la capa de compatibilidad del wheel, cuyo trabajo es
    justamente ocurrir al importar; el arreglo correcto estaba del lado del test.
    """
    global ErrorDeMotor, EscalaresInvalidas, Motor, SinMedidasAplicables
    global escalar, registro_base, _compat
    from oracle_metalenguaje import (ErrorDeMotor, EscalaresInvalidas, Motor,  # noqa: F811
                                     SinMedidasAplicables, escalar, registro_base)
    from oracle_metalenguaje import _compat  # noqa: F811


def _medida(mid="demo.valor", *, escalar=None):
    expresion = ["campo", "i", "valor"]
    if escalar:
        expresion = [escalar, expresion]
    return [
        "medida", mid,
        ["desde", ["de", "item", "i"]],
        ["resumen", "max", expresion],
        ["umbral", "<=", 10, "el límite es parte del ejemplo verificable"],
        ["alcance", "NO comprueba propiedades ajenas a `valor`"],
    ]


def _proyecto(raiz: Path, incremento: int) -> None:
    catalogo = raiz / "catalogos" / "demo"
    catalogo.mkdir(parents=True)
    (catalogo / "demo.valor.json").write_text(
        json.dumps(_medida(escalar="ajustar_motor_aislado")), encoding="utf-8")
    (raiz / "oracle.json").write_text(json.dumps({
        "esquema": "oracle.proyecto/v1",
        "perfiles": [],
        "catalogo_base": False,
    }), encoding="utf-8")
    (raiz / "escalares.py").write_text(
        "from oracle_metalenguaje import escalar\n\n"
        "@escalar('ajustar_motor_aislado')\n"
        "def ajustar(valor):\n"
        f"    return valor + {incremento}\n",
        encoding="utf-8",
    )


class LaFachadaNoSeApropiaDeNombresDelConsumidorTests(unittest.TestCase):
    """Importar la biblioteca no puede borrarle un paquete a quien la importa.

    Hasta 0.3.2 sí podía: la fachada registraba `tools` como nombre de nivel superior, y `tools/` es
    el nombre de paquete más común que hay en un repositorio. Un consumidor real murió con
    `ModuleNotFoundError: No module named 'tools.referencias'` sobre un paquete suyo que existía.
    """

    def test_la_fachada_no_registra_tools(self) -> None:
        """Se lee del código y no del `sys.modules` de esta corrida: en el checkout `tools` ya está
        importado por los propios tests, así que mirar `sys.modules` no distinguiría nada."""
        fuente = (RAIZ / "oracle_metalenguaje" / "__init__.py").read_text(encoding="utf-8")
        registrados = re.findall(r'cargar_interno\("(\w+)"', fuente)
        self.assertEqual(registrados, ["nucleo", "catalogos", "perfiles"])
        self.assertNotIn("tools", registrados)

    def test_el_alias_de_tools_lo_pone_el_propio_paquete(self) -> None:
        """No desaparece: se mudó a donde se necesita. Los módulos de `tools/` se importan entre sí
        por nombre absoluto, y eso pasa cuando corre un entry point —proceso de Oracle, donde
        ocupar el nombre no le saca nada a nadie."""
        fuente = (RAIZ / "tools" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn('sys.modules.setdefault("tools"', fuente)

    def test_el_alias_usa_setdefault_y_no_asignacion(self) -> None:
        """Con asignación, el que llega segundo pisa al primero. Con `setdefault`, un consumidor que
        ya cargó su `tools` conserva el suyo."""
        for archivo in (RAIZ / "tools" / "__init__.py",
                        RAIZ / "oracle_metalenguaje" / "_compat.py"):
            fuente = archivo.read_text(encoding="utf-8")
            with self.subTest(archivo=archivo.name):
                self.assertNotIn('sys.modules["tools"] =', fuente)
                self.assertNotIn("sys.modules['tools'] =", fuente)

    def test_los_tres_que_quedan_son_los_que_el_nucleo_necesita(self) -> None:
        """`nucleo`, `catalogos` y `perfiles` se siguen registrando porque el núcleo se importa a sí
        mismo por nombre absoluto. NINGÚN módulo de `nucleo/` importa `tools`, que es lo que hace
        que sacarlo sea seguro — si mañana uno lo hiciera, esto se rompe y hay que pensarlo."""
        ofensores = []
        for ruta in (RAIZ / "nucleo").rglob("*.py"):
            for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
                if re.match(r"\s*(from tools[. ]|import tools\b)", linea):
                    ofensores.append(f"{ruta.relative_to(RAIZ)}:{n}")
        self.assertEqual(ofensores, [])


class TestMotor(unittest.TestCase):
    def test_la_distribucion_productiva_no_nombra_consumidores_conocidos(self):
        raiz = Path(__file__).resolve().parents[1]
        productivos = (
            raiz / "nucleo",
            raiz / "oracle_metalenguaje",
            raiz / "catalogos",
            raiz / "perfiles",
            raiz / "tools",
        )
        particulares = re.compile(
            r"\b(?:jam|unreal|botoo|placement|snap|kitbash|grilla|al_ras)\b",
            re.IGNORECASE,
        )
        acoplamientos = []
        for directorio in productivos:
            for archivo in sorted(directorio.rglob("*")):
                if archivo.suffix not in {".py", ".json"}:
                    continue
                for numero, linea in enumerate(
                        archivo.read_text(encoding="utf-8").splitlines(), 1):
                    if particulares.search(linea):
                        acoplamientos.append(
                            f"{archivo.relative_to(raiz)}:{numero}: {linea.strip()}")

        self.assertEqual(
            acoplamientos, [],
            "la distribución productiva volvió a conocer un consumidor particular:\n"
            + "\n".join(acoplamientos),
        )

    def test_un_proyecto_sin_configuracion_solo_carga_sus_medidas(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            catalogo = raiz / "catalogos" / "demo"
            catalogo.mkdir(parents=True)
            (catalogo / "demo.valor.json").write_text(
                json.dumps(_medida()), encoding="utf-8")

            motor = Motor.desde_proyecto(raiz)

            self.assertEqual([medida.id for medida in motor.medidas], ["demo.valor"])
            self.assertFalse(any(
                medida.id.startswith(("meta.", "proceso.", "simulacion."))
                for medida in motor.medidas))

    def test_el_puente_namespaced_aliasa_paquete_y_submodulos_sin_duplicarlos(self):
        legado = "_oracle_legado_de_prueba"
        namespaced = "_oracle_paquete_de_prueba." + legado
        modulo = SimpleNamespace(__name__=namespaced)
        hijo = object()
        sys.modules[namespaced + ".hijo"] = hijo
        try:
            with (mock.patch.object(_compat.importlib.util, "find_spec", return_value=object()),
                  mock.patch.object(_compat.importlib, "import_module", return_value=modulo) as importar):
                resultado = _compat.cargar_interno(legado, "_oracle_paquete_de_prueba")

            self.assertIs(resultado, modulo)
            importar.assert_called_once_with("_oracle_paquete_de_prueba." + legado)
            self.assertIs(sys.modules[legado], modulo)
            self.assertIs(sys.modules[legado + ".hijo"], hijo)
        finally:
            for nombre in (namespaced + ".hijo", legado, legado + ".hijo"):
                sys.modules.pop(nombre, None)

    def test_el_puente_solo_retrocede_si_falta_el_paquete_namespaced(self):
        legado, paquete = "_oracle_legado_fallback", "_oracle_paquete_fallback"
        namespaced = paquete + "." + legado
        modulo = SimpleNamespace(__name__=legado)
        ausente = ModuleNotFoundError("ausente", name=namespaced)
        dependencia = ModuleNotFoundError("dependencia", name="otra_dependencia")
        try:
            with (mock.patch.object(_compat.importlib.util, "find_spec", return_value=object()),
                  mock.patch.object(
                      _compat.importlib, "import_module", side_effect=(ausente, modulo)) as importar):
                self.assertIs(_compat.cargar_interno(legado, paquete), modulo)
            self.assertEqual(
                [llamada.args[0] for llamada in importar.call_args_list], [namespaced, legado])

            with (mock.patch.object(_compat.importlib.util, "find_spec", return_value=object()),
                  mock.patch.object(
                      _compat.importlib, "import_module", side_effect=dependencia) as importar):
                with self.assertRaises(ModuleNotFoundError) as capturada:
                    _compat.cargar_interno(legado, paquete)
            self.assertIs(capturada.exception, dependencia)
            importar.assert_called_once_with(namespaced)
        finally:
            sys.modules.pop(legado, None)

    def test_construccion_publica_es_inmutable_y_valida_su_configuracion(self):
        motor = Motor.desde_datos([_medida()])

        self.assertEqual([medida.id for medida in motor.medidas], ["demo.valor"])
        self.assertIsInstance(motor.medidas, tuple)
        self.assertIn("mas", motor.escalares)
        self.assertEqual(motor.limites, LimitesAlgebra())
        self.assertIsNone(motor.proyecto)
        with self.assertRaises(ErrorDeMotor):
            Motor()
        with self.assertRaises(AttributeError):
            motor.limites = LimitesAlgebra(filas_por_relacion=2)

        with self.assertRaisesRegex(ErrorDeMotor, "instancias de Medida"):
            Motor.desde_medidas([object()])
        repetida = Medida.de_datos(_medida())
        with self.assertRaisesRegex(ErrorDeMotor, "repetidos"):
            Motor.desde_medidas([repetida, repetida])
        with self.assertRaisesRegex(ErrorDeMotor, "RegistroEscalares"):
            Motor.desde_medidas([repetida], registro={})
        with self.assertRaisesRegex(ErrorDeAlgebra, "LimitesAlgebra"):
            Motor.desde_medidas([repetida], limites=object())

    def test_un_registro_entregado_se_copia_y_no_contamina_la_base(self):
        registro = registro_base()

        @escalar("triplicar_motor_aislado", registro=registro)
        def triplicar(valor):
            return valor * 3

        motor = Motor.desde_datos(
            [_medida(escalar="triplicar_motor_aislado")], registro=registro)
        del registro["triplicar_motor_aislado"]

        self.assertIn("triplicar_motor_aislado", motor.escalares)
        self.assertEqual(
            motor.evaluar({"item": [{"valor": 2}]}).veredictos[0].valor, 6)
        otra_base = registro_base()
        del otra_base["mas"]
        self.assertIn("mas", registro_base())

    def test_evalua_medidas_en_memoria_y_respeta_limites(self):
        medida = Medida.de_datos(_medida())
        motor = Motor.desde_medidas(
            [medida],
            limites=LimitesAlgebra(filas_por_relacion=1),
        )

        medida.tuberia.append(["donde", False])
        motor.medidas[0].tuberia.append(["donde", False])

        informe = motor.evaluar({"item": [{"valor": 3}]})
        self.assertTrue(informe.ok)
        self.assertEqual(informe.veredictos[0].valor, 3)
        with self.assertRaisesRegex(ErrorDeAlgebra, "supera el límite"):
            motor.evaluar({"item": [{"valor": 3}, {"valor": 4}]})

    def test_falla_cerrado_si_no_hay_medidas_aplicables(self):
        motor = Motor.desde_medidas([Medida.de_datos(_medida())])

        with self.assertRaisesRegex(SinMedidasAplicables, "ninguna medida"):
            motor.evaluar({"otra_relacion": []})

    def test_dos_proyectos_pueden_declarar_la_misma_udf_sin_contaminarse(self):
        nombre = "ajustar_motor_aislado"
        self.assertNotIn(nombre, ESCALARES)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            _proyecto(Path(a), 1)
            _proyecto(Path(b), 100)

            with self.assertRaises(EscalaresNoConfiables):
                Motor.desde_proyecto(a)
            with ThreadPoolExecutor(max_workers=2) as ejecutor:
                futuro_a = ejecutor.submit(
                    Motor.desde_proyecto, a, confiar_escalares=True)
                futuro_b = ejecutor.submit(
                    Motor.desde_proyecto, b, confiar_escalares=True)
                motor_a, motor_b = futuro_a.result(), futuro_b.result()

            evidencia = {"item": [{"valor": 1}]}
            self.assertEqual(motor_a.proyecto, Path(a).resolve())
            self.assertEqual({medida.id for medida in motor_a.medidas}, {"demo.valor"})
            self.assertIn(nombre, motor_a.escalares)
            with ThreadPoolExecutor(max_workers=4) as ejecutor:
                futuros = [
                    ejecutor.submit(motor.evaluar, evidencia)
                    for motor in (motor_a, motor_b, motor_a, motor_b) * 10
                ]
            resultados = [futuro.result().ok for futuro in futuros]
            self.assertEqual(resultados, [True, False, True, False] * 10)

        self.assertNotIn(nombre, ESCALARES)

    def test_un_proyecto_no_puede_escribir_fuera_del_registro_del_motor(self):
        nombre = "intrusa_global_del_motor"
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "escalares.py").write_text(
                "from nucleo.algebra import ESCALARES\n"
                f"ESCALARES[{nombre!r}] = lambda valor: valor\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(EscalaresInvalidas, "registro global"):
                Motor.desde_proyecto(raiz, confiar_escalares=True)

        self.assertNotIn(nombre, ESCALARES)

    def test_un_perfil_externo_se_compone_desde_una_raiz_del_host(self):
        with tempfile.TemporaryDirectory() as td_proyecto, tempfile.TemporaryDirectory() as td_fuente:
            proyecto, fuente = Path(td_proyecto), Path(td_fuente)
            (proyecto / "catalogos").mkdir()
            (proyecto / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1",
                "perfiles": ["perfil_externo"],
                "catalogo_base": False,
            }), encoding="utf-8")
            catalogo = fuente / "perfil_externo" / "catalogos"
            catalogo.mkdir(parents=True)
            (catalogo / "perfil.externo.json").write_text(
                json.dumps(_medida("perfil.externo")), encoding="utf-8")

            motor = Motor.desde_proyecto(
                proyecto, raices_perfiles=(fuente,))

            self.assertEqual([medida.id for medida in motor.medidas], ["perfil.externo"])
            self.assertEqual(
                motor.evaluar({"item": [{"valor": 4}]}).veredictos[0].valor, 4)


if __name__ == "__main__":
    unittest.main()
