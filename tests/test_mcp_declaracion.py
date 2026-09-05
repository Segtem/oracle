"""Contrato de la declaración de la herramienta MCP: anotaciones, esquemas y límites."""

from __future__ import annotations

import io
import unittest

from tools import mcp


class AnotacionesHerramientaTests(unittest.TestCase):
    """Las anotaciones declaran al anfitrión las garantías de seguridad y ejecución."""

    def test_read_only_hint_promete_que_la_herramienta_no_modifica_el_proyecto(self) -> None:
        """Un cliente MCP decide si requerir confirmación interactiva según readOnlyHint.

        Si fuera False, el servidor declararía que puede modificar el proyecto o escribir en
        disco, degradando la autonomía del agente; si fuera False en una herramienta de consulta,
        quebraría la promesa fundacional de sólo lectura del plan 0.6.0.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["annotations"]["readOnlyHint"], True)

    def test_destructive_hint_promete_ausencia_de_mutacion_destructiva(self) -> None:
        """Los clientes imponen salvaguardas críticas ante herramientas declaradas destructivas.

        Si fuera True, el cliente trataría la consulta del catálogo como una operación peligrosa
        (semejante a un borrado), exigiendo confirmación explícita del usuario y bloqueando
        la inspección automatizada.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["annotations"]["destructiveHint"], False)

    def test_idempotent_hint_garantiza_que_consultas_repetidas_son_seguras(self) -> None:
        """El anfitrión sólo puede reintentar llamadas seguras si conoce su idempotencia.

        Si fuera False, el cliente asumiría que invocar la herramienta dos veces consecutivas
        con los mismos parámetros produce efectos colaterales o resultados acumulativos.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["annotations"]["idempotentHint"], True)

    def test_open_world_hint_declara_que_el_dominio_es_el_arbol_local_cerrado(self) -> None:
        """La herramienta opera exclusivamente sobre el árbol confinado del proyecto.

        Si fuera True, el cliente asumiría que la herramienta interactúa con servicios externos
        o la red global, perdiendo la garantía de reproducibilidad sobre el estado local.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["annotations"]["openWorldHint"], False)

    def test_anotaciones_completas_preservan_el_perfil_de_seguridad_declarado(self) -> None:
        """El conjunto de anotaciones define la política de confianza del servidor frente al cliente.

        Si cualquiera de las cuatro banderas discrepara de su valor exacto, el anfitrión
        clasificaría erróneamente el nivel de aislamiento y riesgo de la herramienta.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["annotations"], {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        })


class EsquemaEntradaTests(unittest.TestCase):
    """El esquema de entrada cierra las propiedades aceptadas para evitar errores inadvertidos."""

    def test_input_schema_rechaza_propiedades_adicionales_para_cerrar_la_superficie(self) -> None:
        """Una propiedad adicional no prevista debe fallar la validación y no ignorarse.

        Si additionalProperties fuera True, el esquema aceptaría argumentos mal escritos
        o inventados sin advertir al agente que su pedido contiene parámetros no reconocidos.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["inputSchema"]["additionalProperties"], False)

    def test_ids_exige_al_menos_un_identificador_para_no_crear_un_modo_vacio_ambiguo(self) -> None:
        """La consulta puntual de una única medida es el caso de uso central con ids.

        Si minItems fuera 2 en lugar de 1, un agente que solicite el detalle de una sola
        medida (por ejemplo {"ids": ["demo.alfa"]}) sería rechazado por esquema.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["inputSchema"]["properties"]["ids"]["minItems"], 1)

    def test_ids_exige_identificadores_unicos_para_impedir_duplicados_en_la_consulta(self) -> None:
        """La lista de medidas solicitadas no debe admitir identificadores redundantes.

        Si uniqueItems fuera False, el esquema permitiría que un cliente envíe listas con ids
        repetidos, abriendo ambigüedades en la correspondencia entre pedido y respuesta.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["inputSchema"]["properties"]["ids"]["uniqueItems"], True)

    def test_input_schema_completo_coincide_con_el_contrato_normativo(self) -> None:
        """El esquema completo publicado a los clientes debe fijar estructura y tipos exactos.

        Cualquier mutación en los tipos, límites o expresiones regulares altera la validación
        previa que el cliente MCP ejecuta antes de transmitir la llamada.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["inputSchema"], {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ids": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {
                        "type": "string",
                        "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+$",
                    },
                    "description": "Ids efectivos cuyo detalle se pide. Omitir para listar todos.",
                },
            },
        })


class EsquemaSalidaTests(unittest.TestCase):
    """El esquema de salida fija los límites estructurales de la respuesta."""

    def test_output_schema_rechaza_propiedades_adicionales_en_la_raiz(self) -> None:
        """La respuesta de catálogo efectivo debe cumplir el contrato estricto de la versión 1.

        Si additionalProperties fuera True, el servidor podría devolver campos adicionales
        no estandarizados sin que los esquemas de los clientes detecten la divergencia.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["outputSchema"]["additionalProperties"], False)

    def test_total_permite_cero_para_proyectos_sin_medidas_efectivas(self) -> None:
        """Un proyecto nuevo o sin políticas aplicables tiene legítimamente cero medidas.

        Si minimum fuera 1 en lugar de 0, una respuesta con total 0 violaría el esquema
        declarado y sería rechazada como inválida por validadores estrictos del cliente.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["outputSchema"]["properties"]["total"]["minimum"], 0)

    def test_medidas_items_rechaza_propiedades_adicionales_en_las_filas(self) -> None:
        """Cada fila de medida tiene un formato definido y no debe admitir campos espurios.

        Si additionalProperties fuera True en los items de medidas, se permitiría la presencia
        de claves no acordadas en la lista de medidas devuelta al agente.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["outputSchema"]["properties"]["medidas"]["items"][
                "additionalProperties"
            ],
            False,
        )

    def test_relaciones_exige_elementos_unicos_para_preservar_la_semantica_de_conjunto(self) -> None:
        """Las relaciones de una medida son un conjunto sin elementos repetidos.

        Si uniqueItems fuera False, el esquema toleraría listas con relaciones duplicadas,
        afectando a clientes que construyen grafos o cuentan dependencias de la medida.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["outputSchema"]["properties"]["medidas"]["items"][
                "properties"
            ]["relaciones"]["uniqueItems"],
            True,
        )

    def test_requiere_exige_elementos_unicos_para_impedir_requisitos_repetidos(self) -> None:
        """Los requerimientos previos de una medida no pueden duplicarse en la respuesta.

        Si uniqueItems fuera False, el esquema permitiría redundancia en la lista de requisitos,
        desvirtuando el cálculo de dependencias y el orden de evaluación.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["outputSchema"]["properties"]["medidas"]["items"][
                "properties"
            ]["requiere"]["uniqueItems"],
            True,
        )

    def test_umbral_rechaza_propiedades_adicionales_en_la_cota(self) -> None:
        """El umbral debe restringirse a operador, valor, segun y porque.

        Si additionalProperties fuera True, se admitirían propiedades arbitrarias en el
        objeto umbral, debilitando la transparencia y rigor del criterio de juicio.
        """
        self.assertEqual(
            mcp.HERRAMIENTA_CATALOGO["outputSchema"]["properties"]["medidas"]["items"][
                "properties"
            ]["umbral"]["additionalProperties"],
            False,
        )

    def test_output_schema_completo_fija_el_contrato_estructural_de_respuesta(self) -> None:
        """El esquema de salida completo debe coincidir exactamente con el contrato normativo.

        Cualquier deriva en nombres requeridos, tipos o enumeraciones permitidas
        invalida las garantías de interoperabilidad con clientes del protocolo MCP.
        """
        self.assertEqual(mcp.HERRAMIENTA_CATALOGO["outputSchema"], {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "esquema", "oracle_version", "proyecto", "huella_proyecto", "detalle",
                "total", "medidas",
            ],
            "properties": {
                "esquema": {"const": "oracle.mcp/catalogo-efectivo/v1"},
                "oracle_version": {"type": "string"},
                "proyecto": {"type": "string"},
                "huella_proyecto": {
                    "type": "string", "pattern": "^[0-9a-f]{64}$",
                },
                "detalle": {"type": "boolean"},
                "total": {"type": "integer", "minimum": 0},
                "medidas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id", "origen", "fijacion"],
                        "properties": {
                            "id": {"type": "string"},
                            "origen": {"type": "string"},
                            "relaciones": {
                                "type": "array", "items": {"type": "string"},
                                "uniqueItems": True,
                            },
                            "fijacion": {
                                "enum": ["evidencia", "arnes", "heredada", "sin_fijar"],
                            },
                            "ambito": {
                                "enum": ["universal", "del_origen", "sin_declarar"],
                            },
                            "requiere": {
                                "type": "array", "items": {"type": "string"},
                                "uniqueItems": True,
                            },
                            "umbral": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["operador", "valor", "segun", "porque"],
                                "properties": {
                                    "operador": {"type": "string"},
                                    "valor": {"type": ["string", "number", "boolean"]},
                                    "segun": {"type": "string"},
                                    "porque": {"type": "string"},
                                },
                            },
                            "alcance": {"type": "string"},
                            "fuente": {"type": "string"},
                            "fuente_sha256": {
                                "type": "string", "pattern": "^[0-9a-f]{64}$",
                            },
                        },
                    },
                },
            },
        })


class SerializacionYTransporteTests(unittest.TestCase):
    """La serialización compacta debe ser determinista y UTF-8 nativa sin escapes ASCII."""

    def test_json_compacto_preserva_caracteres_utf8_sin_escapar_a_ascii(self) -> None:
        """Los caracteres no ASCII deben permanecer legibles en UTF-8 y no como escapes Unicode.

        Si ensure_ascii fuera True, caracteres como la tilde se codificarían como secuencias
        \\u00e1, inflando el tamaño del JSON e introduciendo opacidad innecesaria para el modelo.
        """
        self.assertEqual(
            mcp._json_compacto({"termino": "ámbito"}),
            '{"termino":"ámbito"}',
        )

    def test_json_compacto_ordena_las_claves_para_producir_huellas_reproducibles(self) -> None:
        """La serialización canónica se usa para calcular huellas estables de error y estado.

        Si sort_keys fuera False, el orden de claves dependería del orden de inserción,
        provocando que dos estados semánticamente idénticos generen huellas SHA-256 distintas.
        """
        self.assertEqual(
            mcp._json_compacto({"zeta": 1, "alfa": 2}),
            '{"alfa":2,"zeta":1}',
        )

    def test_enviar_emite_bytes_utf8_directos_sin_secuencias_de_escape_ascii(self) -> None:
        """El transporte sobre stdout debe emitir bytes UTF-8 reales seguidos de un solo LF.

        Si ensure_ascii fuera True, el delimitador y los caracteres con tildes se transformarían
        en secuencias de escape ASCII, violando el estándar de transporte directo de MCP.
        """
        salida = io.BytesIO()
        salida.flush = lambda: None
        mensaje = {"jurisdicción": "catálogo efectivo"}
        mcp._enviar(salida, mensaje)
        self.assertEqual(
            salida.getvalue(),
            '{"jurisdicción":"catálogo efectivo"}\n'.encode("utf-8"),
        )
