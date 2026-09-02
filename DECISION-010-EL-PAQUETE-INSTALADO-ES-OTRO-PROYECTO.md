# Decisión 010 — el paquete instalado es otro proyecto, y hay que medirlo como tal

**Fecha:** 2026-09-02 · **Ampliada:** 2026-09-02 (segundo defecto) · **Estado:** vigente
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

## El segundo defecto de la misma clase: la fachada ocupaba nombres del consumidor

Lo encontró el mismo camino, un día después. Importar `oracle_metalenguaje` registraba en
`sys.modules` cuatro nombres de NIVEL SUPERIOR —`nucleo`, `catalogos`, `perfiles` y `tools`— para
que los imports absolutos del propio núcleo funcionen en los dos layouts.

`tools` es el nombre de paquete más común que hay en un repositorio. Un consumidor con su propio
`tools/` lo perdía **por importar la biblioteca**: murió con
`ModuleNotFoundError: No module named 'tools.referencias'` sobre un paquete suyo que existía y no se
había movido.

Y el verificador afirmaba lo contrario:

```python
for nombre in ("nucleo", "catalogos", "perfiles", "tools"):
    assert importlib.util.find_spec(nombre) is None, nombre
```

Eso mira el DISCO y corre **antes** de importar nada. Era verdad y decía una mentira: el wheel no
ocupa esos nombres como archivos, los ocupa al importarse. Segundo verificador que pasa mientras la
cosa está rota, en dos días.

### Lo que se decidió

El alias de `tools` **se mudó de la fachada al propio paquete `tools/`**. Los módulos de `tools/` se
importan entre sí por nombre absoluto, y eso ocurre cuando corre un entry point de Oracle —su propio
proceso, donde ocupar el nombre no le saca nada a nadie—. Un consumidor que sólo usa `Motor` o
`escalar` ya no lo ve.

El verificador ahora comprueba lo que hay que comprobar: crea un consumidor con su propio `tools/`,
importa la biblioteca, y exige que el paquete siga siendo el suyo. Se probó poniendo el defecto de
vuelta: falla con el `ModuleNotFoundError` exacto.

### El riesgo que queda, dicho

`nucleo`, `catalogos` y `perfiles` **se siguen ocupando**, porque el núcleo se importa a sí mismo por
nombre absoluto y sacarlos es reescribir todos sus imports. Son palabras en español y la colisión es
menos probable, pero no imposible. Es `setdefault`, así que un consumidor que ya cargó el suyo lo
conserva —y entonces se rompe Oracle, no él—. La salida de fondo es que el núcleo deje de importarse
por nombre absoluto; no está hecha y este documento no dice que lo esté.

Lo que sí queda fijado: **ningún módulo de `nucleo/` importa `tools`**, que es la condición que hace
seguro haberlo sacado. Hay un test que se rompe si mañana alguno lo hace.

## Lo que esto NO arregla

El verificador prueba dos layouts porque son los dos que hoy se sabe que alguien usa. Un tercero
—un zip importable, un intérprete con `sys.path` armado a mano de otra forma— seguiría sin estar
cubierto, y este documento no promete lo contrario.

Y hay una cosa más, que salió al arreglar el segundo defecto: **`objetivos_disponibles()` excluye
todo `__init__.py`**, así que la fachada —`oracle_metalenguaje/__init__.py`, que es exactamente
donde estaba el defecto— **no la muta nadie**. Lo mismo `tools/__init__.py`, donde vive ahora el
alias.

La exclusión existe por una razón buena: casi todos los `__init__.py` del proyecto están vacíos y
mutarlos sería denominador sin señal. Pero esos dos no están vacíos, y la consecuencia es que su
comportamiento lo fijan tests que leen el CÓDIGO FUENTE como texto, no mutantes. Es más débil y hay
que saberlo. Levantarlo entero es una decisión aparte: hoy sumaría decenas de archivos vacíos al
denominador.
