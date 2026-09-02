# Procedencia de `segundo_autor.py`

**Autor:** Codex CLI, invocado el 2026-09-02 desde `~/Dev/tmp/mutadores-segundo-autor`, un
directorio con **exactamente dos archivos**: `ESPECIFICACION.md` y `CONTRATO.md` (los dos están
copiados acá al lado).

**Lo que NO vio:** este repositorio entero. Ni `nucleo/mutacion.py` y sus mutadores, ni el catálogo,
ni un solo caso del corpus, ni los tests.

**Una redacción, declarada.** A la copia de `ESPECIFICACION.md` que leyó se le quitó UN párrafo: el
que enumera qué sitios de una medida muta la implementación existente. Leerlo lo habría llevado a
proponer lo mismo. El lugar del párrafo lleva una nota que dice que se quitó y por qué. Es el único
cambio, y sacaba una enumeración de coberturas, no una definición.

**Verificación del aislamiento.** No se le creyó la declaración: se auditó su registro de comandos.
Ejecutó tres, los tres con ese directorio como raíz —dos `sed` sobre los archivos que debía leer y un
`ast.parse` sobre su propio código—, y no aparece ninguna ruta hacia afuera. Su declaración coincide
con el registro.

## Lo que declaró él

Leí completos, y únicamente dentro de este directorio:

- `ESPECIFICACION.md`, sus 504 líneas;
- `CONTRATO.md`, sus 66 líneas;
- `mutadores.py`, indirectamente al hacer que `pathlib.Path.read_text()` entregara su contenido al
  analizador sintáctico de Python.

No leí el contenido de ningún otro archivo. `PROCEDENCIA.md` fue creado como parte de esta misma
declaración.

## Comandos ejecutados

Todos se ejecutaron con este directorio como directorio de trabajo:

```sh
wc -l ESPECIFICACION.md CONTRATO.md && sed -n '1,240p' ESPECIFICACION.md && sed -n '1,260p' CONTRATO.md
sed -n '241,504p' ESPECIFICACION.md
python3 -c "import ast, pathlib; ast.parse(pathlib.Path('mutadores.py').read_text())"
```

Además usé la herramienta de aplicación de parches para crear `mutadores.py` y
`PROCEDENCIA.md`; no ejecuta una búsqueda ni una lectura de otros archivos.

## Acceso fuera del directorio

No miré, leí, busqué, listé ni abrí nada fuera de este directorio. No consulté otros repositorios,
implementaciones, ejemplos, documentación en línea ni Internet. Tampoco ejecuté `ls`, `find`,
`grep` o `rg`.
