# Plan — el servidor LSP y qué significa «IntelliSense» en Oracle

**Estado:** diseño, sin construir (2026-08-31). Sucede a `PLAN-IDE.md`, cuyo primer punto
—`oracle medida probar --vigilar`— ya está hecho.

## Por qué acá el autocompletado no es una adivinanza

En un lenguaje dinámico, el IntelliSense **infiere**: mira el código, adivina un tipo y ofrece lo
que probablemente sirva. Se equivoca seguido y por eso se aprende a desconfiar de él.

En Oracle no hay nada que adivinar. **Todo lo que un editor querría ofrecer está declarado**, y por
eso el completado es una consulta, no una inferencia:

| dónde | qué se ofrece | de dónde sale |
|---|---|---|
| `etiqueta: ` | 5 valores | `ETIQUETAS`, conjunto cerrado |
| `procedencia: ` | 3 valores | `PROCEDENCIAS`, conjunto cerrado |
| `como_se_detecto: ` | 5 valores | `DETECCIONES`, conjunto cerrado |
| `umbral <= 0 segun ` | 4 valores | `medicion · contrato · convencion · tanteo` |
| `de ` | las relaciones declaradas | `relaciones/*.json`, con su `alcance` en el popup |
| `donde p.` | los campos de **esa** relación | la declaración, **con su unidad** |
| `medida: ` en un caso | los ids del catálogo | el catálogo cargado |
| `resumen ` | los agregados | `AGREGADOS` del álgebra |

La fila que ningún IDE del mundo muestra hoy:

```
p.ox      flotante · cm        ← la unidad, en el desplegable
p.yaw     flotante · grados
p.id      texto · sin_unidad
```

Un alumno que escribe `donde p.alto > 400` y ve `cm` al lado del campo entiende, sin que nadie se lo
diga, que 400 son centímetros. Eso es enseñar sin dar una clase.

## Las cuatro funciones, en orden de valor

### 1. Diagnósticos — está casi hecho

`ErrorSintaxis` ya trae `linea`, `columna`, `esperado` y `encontrado` como campos. Convertir eso a
un diagnóstico de LSP es una función de diez líneas. Es lo primero y lo más barato.

Y hay diagnósticos que no son de sintaxis y valen más:

- **`⚠ SIN FIJAR`** sobre una medida que ningún caso pone a prueba;
- **«nunca se pone roja»** / **«nunca se pone verde»**, que hoy da `oracle medida revisar`;
- el **`alcance` derivado**: qué campos declarados NO lee esta medida.

### 2. Completado — la tabla de arriba

Exacto, no aproximado. Y con la documentación al lado: al ofrecer una relación se muestra el
`alcance` de su sensor; al ofrecer un campo, su unidad.

### 3. Hover — lo que una medida promete y lo que no

Al pasar por un id de medida: su `umbral`, su `segun`, su `porque` y su `alcance` entero. Es el
único lugar donde `porque` —que la máquina no puede juzgar— se le pone delante a la persona en el
momento en que importa.

### 4. CodeLens — el veredicto en vivo, arriba de cada medida

Esto no lo tiene ningún otro lenguaje, porque ningún otro lenguaje sabe si un enunciado suyo está
puesto a prueba:

```
ROJO · 1 testigo · fijada por 2 casos
ninguno web.ninguna_imagen_pesada:
    de imagen i
    ...
```

y sobre una que nadie prueba:

```
⚠ SIN FIJAR — ninguna evidencia la pone a prueba
```

## La regla que no se negocia

De `PLAN-IDE.md`, y vale igual acá:

> **El servidor puede mostrar, medir y confrontar. No completa el umbral, ni el `porque`, ni el
> `alcance`.**

Ofrecer los cuatro valores de `segun` está bien: es un conjunto cerrado, elegir sigue siendo del
humano. Sugerir *cuál* elegir, no. Escribir el `porque`, menos todavía: es lo único que la máquina
no puede juzgar y por lo tanto lo único que la persona tiene que aportar.

## Dónde corre

`~/Dev/cs50-emacs` usa `lsp-mode` y `~/Dev/cs50-vscode` es VS Code: **un solo servidor cubre los dos
entornos del taller**. No se construye un IDE; se enchufa a los que ya están instalados.

## El riesgo, dicho antes de empezar

El LSP es el único de los tres trabajos de `PLAN-IDE.md` que **se acopla a la superficie**. La
superficie se movió dos veces la semana del 2026-08-25: cambió cómo se parsean las macros y el
umbral cambió de forma para aceptar `segun`. Mitigación concreta: **el servidor no parsea nada**.
Llama a `nucleo/sintaxis.py` y a `nucleo/medida.py` y traduce sus errores y sus datos a LSP. Si
duplica el parser, queda desactualizado a la primera.
