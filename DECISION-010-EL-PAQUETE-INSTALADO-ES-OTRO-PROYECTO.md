# Decisión 010 — el paquete instalado es otro proyecto, y hay que medirlo como tal

**Fecha:** 2026-09-02 · **Estado:** vigente
**Origen:** un consumidor migrando de subtree a PyPI, bloqueado por un defecto de 0.3.1.

## El hecho

`nucleo/aislamiento/escalares.py` lanza el subproceso que ejecuta las UDF de un proyecto con el
entorno **reemplazado**, y le pasaba `PYTHONPATH = RAIZ_ORACLE`. En el repo eso es la raíz, que
contiene `oracle_metalenguaje/`, así que la fachada importa. En el wheel, `RAIZ_ORACLE` **es el
directorio del propio paquete**, y quien lo hace importable es su padre.

Consecuencia: el `escalares.py` de un consumidor que hace `from oracle_metalenguaje import escalar`
—que es lo que la documentación le pide hacer— moría con `ModuleNotFoundError`.

## Por qué no lo vio nadie durante dos releases

Porque **sólo se rompe cuando el paquete no está en `site-packages`**. En un venv, `site.py` agrega
ese directorio por su cuenta y tapa la falta. `tools/verificar_instalacion.py` probaba exactamente
ese caso: construía el wheel, lo instalaba en un venv, corría un proyecto con `escalares.py` que
importa la fachada, y salía `WHEEL OK`.

Era un verde que no significaba nada, en la herramienta que existe para decir que el paquete está
bien. Es el defecto que este repositorio cataloga 90 veces, cometido en su propio arnés.

## La decisión

**El paquete instalado no es «el repo, movido». Es un layout distinto, y hay que ejercerlo como un
proyecto aparte.** Concretamente:

1. `tools/verificar_instalacion.py` prueba **dos** layouts, no uno: el venv y el vendorizado con
   `pip install --target`. El segundo es el que usa un consumidor cuyo intérprete es de otro —uno
   embebido dentro de una aplicación anfitriona—, que no puede crear un venv.
2. Cualquier ruta que se derive de `__file__` para encontrar **la fachada** se le pregunta al
   importador (`importlib.util.find_spec`), no se calcula. Las que buscan `catalogos/` o `nucleo/`
   sí pueden derivarse: en los dos layouts cuelgan del mismo lugar.
3. Se auditaron los demás usos y **el del aislamiento es el único** que necesitaba la fachada desde
   un subproceso con el entorno reemplazado. La otra llamada a `subprocess` con `env` explícito
   —la del arnés de mutación— copia `os.environ` en vez de reemplazarlo.

## Lo que se descartó, y por qué

- **`RAIZ_ORACLE.parent`**, que era lo obvio y lo que propuso quien encontró el defecto. En el repo
  eso es el directorio que CONTIENE a Oracle —`~/Dev` en la máquina donde apareció— y meterlo en el
  camino de un subproceso que existe para **confinar** una UDF ajena es exactamente lo contrario de
  lo que ese módulo hace. Con `find_spec`, en el repo no se agrega ninguna entrada.
- **Derivarlo de `__package__`.** Parecía preciso y está mal por una razón que no se ve leyendo el
  archivo: `oracle_metalenguaje/__init__.py` aliasa `nucleo` como paquete de nivel superior, así que
  ese mismo archivo termina importado **dos veces bajo dos nombres, como dos objetos distintos**. El
  que usa `nucleo/proyecto.py` se llama `nucleo.aislamiento.escalares`, y desde ese nombre el layout
  del wheel es invisible. El cálculo daba el valor correcto en la copia equivocada.

## Cómo sabemos que el arreglo mide algo

Se puso el defecto **de vuelta a propósito** y se corrió el verificador: sale 1, con el
`ModuleNotFoundError` exacto. Un chequeo que pasa con y sin el defecto no comprueba nada.

## Lo que esto NO arregla

El verificador prueba dos layouts porque son los dos que hoy se sabe que alguien usa. Un tercero
—un zip importable, un intérprete con `sys.path` armado a mano de otra forma— seguiría sin estar
cubierto, y este documento no promete lo contrario.
