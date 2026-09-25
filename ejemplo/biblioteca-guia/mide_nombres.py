"""El ADAPTADOR: habla con el disco y emite evidencia. No decide nada."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sensores.nombres import sigue_convencion

carpeta = Path(sys.argv[1])
print("documento: nombre, sigue_convencion")
for p in sorted(carpeta.glob("*.md")):
    print(f'    {json.dumps(p.name, ensure_ascii=False)}, '
          f'{"true" if sigue_convencion(p.name) else "false"}')
