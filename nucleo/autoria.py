"""Archivos de autoría propios del proyecto, reificados para las políticas meta."""

from .caso import rutas_de_corpus
from .medida import rutas_de_catalogo
from .relacion import rutas_de_relaciones

RELACIONES_DE_AUTORIA = frozenset({"archivo_de_autoria"})
AMBITOS_DE_RELACIONES = {"archivo_de_autoria": "universal"}
CAMPOS_DE_RELACIONES = {"archivo_de_autoria": ("tipo", "ruta", "formato")}


def hechos_de_autoria(proy) -> dict[str, list[dict]]:
    """Una fila por archivo cargable propio; las bibliotecas responden por su corpus."""
    fuentes = (
        ("medida", rutas_de_catalogo(proy.catalogos)),
        ("caso", rutas_de_corpus(proy.corpus)),
        ("relacion", rutas_de_relaciones(proy.raiz / "relaciones")),
    )
    return {"archivo_de_autoria": [
        {"tipo": tipo, "ruta": ruta.relative_to(proy.raiz).as_posix(),
         "formato": ruta.suffix.lstrip(".")}
        for tipo, rutas in fuentes for ruta in rutas
    ]}
