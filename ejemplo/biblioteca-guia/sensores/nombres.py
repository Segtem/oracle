"""El SENSOR: puro. Decide si un nombre sigue la convención, y nada más."""
import re

CONVENCION = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Z]+-[A-Za-z0-9-]+-v\d+\.\d+\.md$")


def sigue_convencion(nombre: str) -> bool:
    return CONVENCION.fullmatch(nombre) is not None
