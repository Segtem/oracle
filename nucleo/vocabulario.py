"""Los vocabularios cerrados del lenguaje, cada opción con lo que significa.

Un vocabulario cerrado —las cinco etiquetas de un caso, los cuatro orígenes de un umbral— es la
parte del lenguaje que más se equivoca quien recién llega, porque los nombres se parecen entre sí
y el archivo no dice cuál es cuál. Durante meses ese significado vivió en prosa suelta:
`PLAN-LENGUAJE.md`, `corpus/README.md`, el tutorial y `docs/07-conectar-a-un-proyecto-propio.md`
decían cada uno una parte, y ninguno era la fuente.

Acá la declaración ES la fuente: el nombre y su sentido viajan juntos en la misma estructura. De
ahí salen las dos cosas que importan — el error que ve quien se equivoca, en el momento exacto en
que se equivoca, y el manual, que no es un documento aparte sino una vista de esto mismo.

Este módulo no importa nada de `nucleo`: lo usan tanto `caso` como `medida`, que no se conocen
entre sí, y una dependencia hacia adentro los ataría sin motivo.
"""


def opciones(vocabulario: dict[str, str]) -> str:
    """Las opciones de un vocabulario cerrado, en líneas indentadas, cada una con su sentido.

    Antes el error decía sólo la lista de nombres. A quien escribió `falso_rojo` donde iba
    `falso_verde` no le falta saber que hay cinco: le falta saber cuál es cuál, y el momento en que
    le hace falta es exactamente ése.
    """
    return "\n".join(f"        {nombre}: {sentido}"
                     for nombre, sentido in sorted(vocabulario.items()))


# ---- de dónde salió el número de un umbral -----------------------------------------
#
# `segun` es obligatorio y es la pregunta más incómoda de una medida: un umbral sin origen es un
# número que alguien tipeó. Las cuatro opciones no son grados de calidad sino orígenes distintos,
# y `tanteo` es una respuesta legítima mientras esté escrita.

ORIGENES_DE_UMBRAL: dict[str, str] = {
    "medicion": "el número salió de medir la cosa real con un instrumento que se puede nombrar. "
                "Es el origen más fuerte, porque otro puede repetir la medición y discutirlo",
    "contrato": "el número lo fija algo externo que no se negocia: una especificación, el formato "
                "de un archivo, una norma, la API de un tercero",
    "convencion": "el número lo eligió el equipo y vale porque está escrito, no porque se haya "
                  "medido. Cambiarlo es una decisión, no la corrección de un error",
    "tanteo": "el número es provisorio: se puso para arrancar y todavía nadie lo justificó. "
              "Declararlo así es honesto; dejarlo así mucho tiempo, no",
}


# ---- dónde obliga una medida -------------------------------------------------------
#
# La carpeta dice de dónde vino una medida, no a quién puede imponerle un veredicto. Este
# vocabulario separa esas dos preguntas sin darle a Oracle un nombre privilegiado: el origen puede
# ser el catálogo base, un perfil, una biblioteca o el propio proyecto.

AMBITO_SIN_DECLARAR = "sin_declarar"

AMBITOS: dict[str, str] = {
    "universal": "la medida obliga a todo proyecto que seleccione el catálogo y aporte la "
                 "evidencia necesaria para evaluarla",
    "del_origen": "la medida obliga sólo cuando el proyecto evaluado es dueño de su origen; un "
                  "consumidor ajeno puede leerla, pero no recibe su veredicto",
}


# ---- los operadores de la tubería --------------------------------------------------
#
# El álgebra los despacha por literal, repartidos entre `_validar` y `_evaluar`; acá se los nombra
# en un solo lugar, con lo que hace cada uno. Que esta lista no se despegue de la implementación no
# se confía a la buena voluntad: la mide `meta.todo_operador_del_manual_lo_reconoce_el_algebra`.

OPERADORES: dict[str, str] = {
    "desde": "encabeza toda tubería. No es un paso: es la marca de que lo que sigue es una tubería "
             "y no otra cosa",
    "de": "nombra la relación de evidencia de la que salen las filas. Es el único operador que "
          "trae datos; todos los demás transforman lo que «de» trajo",
    "donde": "se queda con las filas que cumplen la condición. Sin él un rojo entrega como testigos "
             "todas las filas, también las que no ofendieron, y hay que leerlas a mano",
    "unir": "cruza dos relaciones fila contra fila. Los alias de los dos lados conviven en la fila "
            "resultante, así que la condición puede hablar de ambos",
    "agrupar": "junta las filas por una o más claves y calcula un agregado por grupo. Devuelve una "
               "fila por grupo, no una por fila: cambia de qué habla la tubería",
    "resumen": "cierra la tubería en un solo escalar, que es lo que el umbral compara. «contar» no "
               "evalúa la expresión: cuenta filas",
}


# ---- las relaciones que el lenguaje emite sobre sí mismo ---------------------------
#
# Están acá y no leyéndose de `ESPECIFICACION.md` por una razón concreta: la especificación no
# viaja dentro del paquete instalado, así que un manual que la parsee queda vacío justo para quien
# instaló Oracle desde PyPI —que es casi todo el mundo—. Que estas claves sean exactamente las de
# `RELACIONES_DEL_LENGUAJE` lo fija un test; que cada una esté además nombrada en la especificación
# lo mide `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`.

RELACIONES_EXPLICADAS: dict[str, str] = {
    "caso": "cada caso del corpus: su polaridad, su procedencia, si la medida que reclama existe, "
            "y si es propio o heredado de una biblioteca",
    "medida_en_uso": "cuántos casos evalúan cada medida y cuántos mutantes le sobreviven; es la "
                     "relación con la que Oracle mide si una medida está ejercitada o es adorno",
    "sombra": "qué medidas heredadas se miden y se informan pero todavía no tumban la corrida, "
              "desde cuándo, con qué razón escrita y hace cuántos días — que es lo que permite "
              "envejecerlas y distinguir una transición de un estado permanente",
    "relacion_documentada": "si cada relación del lenguaje está nombrada en la especificación; "
                            "existe para que una relación nueva no quede sin documentar en silencio",
    "verbo_del_cli": "cada verbo que el comando acepta y si la ayuda lo nombra; un verbo fuera de "
                     "la ayuda es trabajo terminado que nadie va a encontrar",
    "mutador_excluido": "cada mutador que el arnés no corre, con la premisa declarada y si sigue "
                        "disponible en el registro del arnés; ninguna exclusión debe aplicarse "
                        "globalmente para que el denominador de mutación no baje en silencio",
    "opcion_del_vocabulario": "cada opción de un vocabulario cerrado, con cuántas palabras la "
                              "explican y si el manual la alcanza",
}
