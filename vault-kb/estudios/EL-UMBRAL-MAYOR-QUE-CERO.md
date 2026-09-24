# El umbral mayor que cero: ciudadano del lenguaje, extranjero en el corpus

## Resumen ejecutivo

El verbo general `medida` admite cualquier comparador y cualquier valor escalar en su cláusula de
umbral. Sin embargo, en el catálogo propio de Oracle **el 100% de las medidas tienen umbral `<= 0`**.
La práctica del repositorio identificó medir con contar transgresiones, convirtiendo una posibilidad
del lenguaje en un camino casi inexplorado por sus propios tests.

Esta asimetría ya produjo una rotura concreta: en `nucleo/mutacion.py:153-159`, la exclusión del
mutador `convertir_conteo_en_existencia` se fundamentó en la premisa universal de que *todas las
medidas del catálogo tienen umbral `<= 0`*. Cuando el consumidor `Jam` corre aceptación con su medida
`snap.al_ras` (cuyo umbral es `<= 1.0`), la premisa se vuelve falsa y la regla reflexiva
`meta.ninguna_exclusion_de_mutador_se_apoya_en_una_premisa_falsa` falla con código 1.

Este estudio documenta la medición empírica en los tres repositorios conocidos, desentraña la
diferencia semántica entre poner un número en el filtro o en el umbral, inventaría cada sitio del
código de Oracle que asume silenciosamente el cero, propone una medida propia para mantener vivo el
camino en el catálogo base y define cómo vigilar este sesgo mediante medidas meta.

---

## 1. El censo real: verificación empírica de los tres catálogos

Se verificaron empíricamente los catálogos de **Oracle**, **Jam** y **LyraGASP**, distinguiendo
dos niveles de observación:
1. **Sintáctico (explícito en fuente)**: cláusulas `umbral <op> <valor>` escritas literalmente en los
   archivos `.oracle` o `.json`.
2. **Semántico (expandido en `Medida`)**: el contrato que ve el motor tras expandir macros
   (`ninguno`, `ninguno-requiere`, `peor`, etc.).

### Resultado medido

```text
=== Oracle (/home/workstation/Dev/oracle/catalogos) ===
Archivos en catálogo: 52
Umbrales explícitos en fuente: 42
  Explícitos <= 0: 42
  Explícitos distintos de <= 0: 0
Medidas expandidas: 52
  Expandidas <= 0: 52
  Expandidas distintos de <= 0: 0

=== Jam (/home/workstation/Dev/jam/medidas/catalogos) ===
Archivos en catálogo: 41
Umbrales explícitos en fuente: 8
  Explícitos <= 0: 7
  Explícitos distintos de <= 0: 1
    * snap.al_ras.json: <= 1.0
Medidas expandidas: 41
  Expandidas <= 0: 38
  Expandidas distintos de <= 0: 3
    * snap.al_ras: <= 1.0 (segun: sin_declarar)
    * snap.grilla: <= 1.0 (segun: sin_declarar)
    * snap.yaw: <= 0.5 (segun: sin_declarar)

=== LyraGASP (/home/workstation/Dev/games/unreal/LyraGASP/medidas/catalogos) ===
Archivos en catálogo: 9
Umbrales explícitos en fuente: 1
  Explícitos <= 0: 1
  Explícitos distintos de <= 0: 0
Medidas expandidas: 9
  Expandidas <= 0: 9
  Expandidas distintos de <= 0: 0
```

### Qué revelan estos números

1. **La medición previa es exacta**: en sintaxis explícita, Oracle tiene 42 cláusulas `umbral`,
   todas `<= 0`. Los otros 10 archivos de Oracle son invocaciones de macros (`ninguno-requiere` o
   JSON antiguo) que expanden invariablemente a `umbral <= 0`.
2. **Jam es el único autor que escribió umbrales distintos de cero**:
   - En forma canónica explícita escribió `snap.al_ras.json` con `umbral <= 1.0`.
   - A través de la macro `peor` (provista en `nucleo/macros/peor.oracle`), Jam escribió
     `snap.grilla.json` (tolerancia `1.0` cm) y `snap.yaw.json` (tolerancia `0.5` grados).
3. **Oracle nunca usó la macro `peor` en su propio catálogo**: la macro vive en
   `nucleo/macros/peor.oracle`, pero dentro de `catalogos/` de Oracle ninguna medida la invoca.
   Oracle diseñó el medio de abstracción para umbrales con tolerancia, pero jamás lo consumió.

---

## 2. Semántica de un umbral > 0: `snap.al_ras` frente a `scatter.cobertura`

Para comprender por qué `1.0` es un umbral legítimo y cuándo un número pertenece al filtro o al
umbral, se contrastan dos medidas reales del catálogo de Jam.

### El caso real: `snap.al_ras.json`

```json
[
  "medida",
  "snap.al_ras",
  ["desde", ["unir", ["de", "pieza", "a"], ["de", "objetivo", "b"]], ["donde", [">", ["desvio_de_contacto", ["hecho", "a"], ["hecho", "b"]], 1.0]]],
  ["resumen", "max", ["desvio_de_contacto", ["hecho", "a"], ["hecho", "b"]]],
  ["umbral", "<=", 1.0, "hasta 1 cm se considera contacto: evita rechazar ruido de bounds sin aceptar una junta visible"],
  ["requiere", "pieza", "objetivo"],
  ["alcance", "contacto de las caras sobre el eje solicitado. NO ve si las piezas comparten superficie en los otros dos ejes, ni la geometría real dentro del AABB. Si `pieza` u `objetivo` vienen vacías la medida NO concluye —lo declara en `requiere`— y sale SIN EVIDENCIA en vez de un verde que no miró nada"]
]
```

En su defensa (`porque`) dice:
> *"hasta 1 cm se considera contacto: evita rechazar ruido de bounds sin aceptar una junta visible"*

Y en su `alcance` aclara que mide el contacto de caras sobre el eje solicitado sin juzgar los otros
dos ejes ni la geometría interna.

#### Por qué 1.0 es correcto y no un margen puesto por comodidad

En modelado 3D y videojuegos bajo Unreal Engine, las cajas alineadas a los ejes (AABB) de dos mallas
adyacentes casi nunca dan una distancia de exactamente `0.000000` cm. Existen imprecisiones de coma
flotante y márgenes de tessellation. Si se exigiera `desvio == 0`, mallas perfectamente acopladas se
rechazarían como defectuosas por ruido numérico imperceptible.

Por otro lado, si la separación supera `1.0` cm, el ojo del jugador percibe una grieta (*seam*) entre
los bloques modulares, rompiendo la inmersión y la oclusión de luz. Por lo tanto:
- El número `1.0` **no es una concesión perezosa** ("permito que falle 1 vez").
- El número `1.0` **es la definición física y perceptual del concepto «al ras»**.
- La unidad del resumen es física: centímetros (`cm`). La medida no cuenta entidades; mide una
  distancia máxima: `resumen max(desvio_de_contacto)`.
- Cuando la medida falla, el veredicto no dice `✗ snap.al_ras 1 (<= 0)`: publica la magnitud del peor
  defecto observado, por ejemplo `✗ snap.al_ras 9.0 (<= 1.0)`. Quien lee el reporte sabe de inmediato
  que hay una separación de 9 cm.

### El contraste: `scatter.cobertura.json`

```json
[
  "medida",
  "scatter.cobertura",
  ["desde", ["de", "cobertura_scatter", "c"], ["donde", ["<", ["campo", "c", "fraccion"], 0.6]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "cero celdas por debajo del 60%: el contrato operativo considera amontonado un reparto que ocupa menos del 60% de una grilla 3×3, y una sola celda así ya describe un amontonamiento. El umbral es 0 y no un margen porque el número del dominio —el 0,6— ya está en el filtro; ponerlo también acá lo escribiría dos veces y nada mantendría las dos copias iguales (caso `012` del corpus)"],
  ["requiere", "cobertura_scatter"],
  ["alcance", "fracción de celdas con al menos un centro. NO ve uniformidad dentro de cada celda, distancias entre vecinos, patrones, orientación ni calidad visual. Si `cobertura_scatter` viene vacía la medida NO concluye —lo declara en `requiere`— y sale SIN EVIDENCIA en vez de verde"]
]
```

Su `porque` argumenta con precisión quirúrgica:
> *"cero celdas por debajo del 60%: el contrato operativo considera amontonado un reparto que ocupa menos del 60% de una grilla 3×3, y una sola celda así ya describe un amontonamiento. El umbral es 0 y no un margen porque el número del dominio —el 0,6— ya está en el filtro; ponerlo también acá lo escribiría dos veces y nada mantendría las dos copias iguales (caso `012` del corpus)"*

### La regla: cuándo el número va en el FILTRO y cuándo en el UMBRAL

| Dimensión | El número va en el FILTRO | El número va en el UMBRAL |
|---|---|---|
| **Tipo de medida** | Oráculo de ausencia de defectos. | Cota de magnitud continua / métrica extrema. |
| **Operación de resumen** | `contar 1` (o `suma` de indicadores booleanos). | `max(...)`, `min(...)`, `promedio(...)`. |
| **Unidad del resultado** | Cardinalidad entera: cantidad de filas transgresoras. | Magnitud del dominio: cm, grados, segundos, bytes. |
| **Función del número** | Criterio de corte para clasificar si un hecho ofende. | Cota contractual admisible para la magnitud medida. |
| **Significado del umbral** | **`<= 0`**: Ningún defecto es tolerable. | **`<= K`**: La magnitud extrema no debe exceder K. |
| **Patrón si se pusiera K > 0** | Concesión de comodidad ("tolero hasta 3 celdas rotas"). | Especificación técnica del contrato físico o métrico. |

#### Por qué `snap.al_ras` repite el 1.0 en el filtro y en el umbral

Podría preguntarse por qué `snap.al_ras` tiene `donde desvio > 1.0` si ya tiene `umbral <= 1.0`.
La razón reside en la semántica del álgebra relacional de Oracle:
1. Si no hubiera filtro `donde > 1.0`, `resumen max` calcularía el desvío sobre todas las piezas en
   contacto normal (por ejemplo, 0.2 cm). Si no hay defectos, el veredicto daría `✓ valor 0.2 (<= 1.0)`.
   Esto sería válido, pero arrastraría miles de pares como testigos en la relación.
2. Al filtrar con `donde desvio > 1.0`, los pares que cumplen la tolerancia se descartan de inmediato.
   Si todas las piezas cumplen, la tubería queda vacía; en el álgebra de Oracle, `_agregar("max", [])`
   devuelve el neutro `0`, que satisface `0 <= 1.0` (VERDE) sin testigos.
3. Si al menos una pieza se separa 2.5 cm, pasa el filtro, `max` devuelve `2.5`, y `2.5 <= 1.0` da ROJO
   con esa pieza específica como testigo.
Este patrón es exactamente el que abstrae la macro `peor`:
```oracle
defmacro peor(id, relacion, alias, expresion, tolerancia, porque, segun, alcance):
    medida $id:
        de $relacion $alias
        donde $expresion > $tolerancia
        resumen max($expresion)
        umbral <= $tolerancia segun $segun porque $porque
        alcance $alcance
```

---

## 3. Qué más en Oracle asume en silencio que el umbral es 0

Se realizó una inspección exhaustiva del código fuente de Oracle (`nucleo/`, `mutadores/`, `tools/`,
`perfiles/`). A continuación se detallan los sitios donde se asume silenciosamente que el umbral es 0,
evaluando si la suposición es inocua o una bomba de tiempo.

### 1. `nucleo/mutacion.py:145-147` y `nucleo/mutacion.py:153-159`
```python
def _todos_los_umbrales_son_menores_o_iguales_a_cero(catalogo: dict[str, Medida]) -> bool:
    """La equivalencia sólo vale para la forma exacta `umbral <= 0` de cada medida."""
    return all(medida.op == "<=" and medida.limite == 0 for medida in catalogo.values())

EXCLUSIONES_DE_MUTADORES = (
    ExclusionDeMutador(
        mutador="convertir_conteo_en_existencia",
        premisa="todas las medidas del catálogo tienen umbral <= 0",
        predicado=_todos_los_umbrales_son_menores_o_iguales_a_cero,
    ),
)
```
- **Veredicto**: **BOMBA EXPLOTADA**.
- **Por qué**: Asume que la totalidad de las medidas de cualquier catálogo evaluado tiene `umbral <= 0`.
  Al evaluar la aceptación de Jam (`python3 tools/aceptacion.py --proyecto /home/workstation/Dev/jam/medidas`),
  la premisa evalúa a `False` debido a `snap.al_ras` (`<= 1.0`), `snap.grilla` (`<= 1.0`) y `snap.yaw` (`<= 0.5`).
  La salida real del comando es:
  ```text
  ACEPTACIÓN ✗ — 1 problema(s)
    · meta.ninguna_exclusion_de_mutador_se_apoya_en_una_premisa_falsa: el marco no cumple su propia regla
        → m={'mutador': 'convertir_conteo_en_existencia', 'premisa': 'todas las medidas del catálogo tienen umbral <= 0', 'premisa_vale': False}
  ```
  La equivalencia de `convertir_conteo_en_existencia` es local a cada medida (vale para aquellas cuyo
  resumen sea `contar` y su umbral sea `<= 0`), pero se implementó como un interruptor global para todo
  el proyecto apoyado en una premisa universal falsa.

### 2. `nucleo/mutacion.py:177-179`
```python
    excluidos = {exclusion.mutador for exclusion in EXCLUSIONES_DE_MUTADORES}
    return {fn.__name__: fn for fn in segundo_autor.MUTADORES
            if fn.__name__ not in excluidos}
```
- **Veredicto**: **FALLA DE ARQUITECTURA**.
- **Por qué**: En tiempo de importación de Python, `_mutadores_ajenos()` excluye incondicionalmente
  cualquier mutador nombrado en `EXCLUSIONES_DE_MUTADORES` sin consultar si su predicado es verdadero
  o falso sobre el catálogo cargado. Incluso cuando `premisa_vale` es `False` (como en Jam), el mutador
  permanece desactivado en el arnés.

### 3. `nucleo/mutacion.py:284-289`
```python
        if agregado == "contar":
            # La expresión de `contar` no tiene semántica. Para que el mutante no sea el equivalente
            # universal contar→suma(1), lo reemplaza por el agregado nulo suma(0): «no medir».
            mutada = _reemplazar(datos, ruta_agregado, "suma")
            mutada = _reemplazar(mutada, ruta_expresion, 0)
            yield f"agregado:{_ruta(ruta_agregado)}:contar→suma(0)", mutada
```
- **Veredicto**: **BOMBA SILENCIOSA**.
- **Por qué**: Asume que `suma(0)` (cuyo valor evaluado es siempre `0`) representa "no medir" y que `0`
  es un valor intrínsecamente aprobatorio. Esto es verdad para cotas superiores positivas (`<= 0` o
  `<= 10`). Pero si una medida exige presencia mediante una cota inferior (`contar 1 >= 1`), un defecto
  de ausencia produce `0` (rojo); al mutar a `suma(0)`, el valor sigue siendo `0` (rojo). El mutante
  no muere por cambio de veredicto; sobrevive artificialmente porque el arnés asumió que `0` siempre
  apaga las alarmas.

### 4. `mutadores/segundo_autor.py:119-128`
```python
def _direccion_monotona(partes, direccion):
    _, resumen, umbral, _ = partes
    if direccion == "superior" and umbral[1] not in {"<", "<="}:
        return False
    if direccion == "inferior" and umbral[1] not in {">", ">="}:
        return False
    if resumen[1] == "contar":
        return True
    return resumen[1] == "suma" and _es_predicado(resumen[2])
```
- **Veredicto**: **BOMBA SILENCIOSA**.
- **Por qué**: Esta función gobierna mutadores estructurales clave: `alejar_limite_de_defecto`,
  `acercar_limite_de_requisito` y `eliminar_filtro_de_requisito`. Asume que los únicos resúmenes
  monótonos son `contar` y `suma`.
  Al correr sobre `snap.al_ras.json` (que usa `max` y umbral `1.0`), `_direccion_monotona` devuelve
  `False`. En consecuencia, `alejar_limite_de_defecto` (que debería mutar `desvio > 1.0` a `desvio > 2.0`
  para verificar si el corpus tiene casos en la frontera) devuelve `None`. El mutador no se genera y el
  borde de `snap.al_ras` queda ciego a esa mutación.

### 5. `mutadores/segundo_autor.py:238-248` (`vaciar_tuberia_si_cero_aprueba`)
```python
    if not _aprueba(0, umbral[1], umbral[2]):
        return None
    tuberia.append(["donde", False])
```
- **Veredicto**: **CORRECTO / SEGURO**.
- **Por qué**: Aunque explota que los agregados sobre listas vacías producen 0, no asume que el umbral
  sea `<= 0`. Consulta explícitamente `_aprueba(0, ...)`. Si el umbral fuera `>= 1.0`, se desactiva
  adecuadamente sin arrojar falsos equivalentes.

### 6. `mutadores/segundo_autor.py:251-263` (`convertir_conteo_en_existencia`)
```python
    if resumen[1] != "contar" or umbral[1] not in {"<", "<="}:
        return None
    if not (_aprueba(0, umbral[1], umbral[2]) or _aprueba(1, umbral[1], umbral[2])):
        return None
    resumen[1:] = ["max", 1]
```
- **Veredicto**: **CORRECTO EN EL MUTADOR, MUTILADO POR EL ARNÉS**.
- **Por qué**: El autor del mutador protegió la transformación verificando que 0 y 1 sean aprobados.
  El problema no está en esta función, sino en que `nucleo/mutacion.py` le impidió correr sobre
  cualquier medida bajo la presunción de que todo el catálogo es `<= 0`.

### 7. `nucleo/algebra.py:586-587`
```python
def _agregar(agregado: str, valores: list):
    """Agrega valores comprobando dominio, compatibilidad y finitud antes y después."""
    if not valores:
        return 0
```
- **Veredicto**: **DECISIÓN DE DISEÑO CON SUPOSICIÓN SEMÁNTICA**.
- **Por qué**: Para `contar` y `suma`, el neutro matemático de una lista vacía es `0`. Para `max` y
  `min`, en Python nativo levantaría excepción (`ValueError`) y en teoría matemática sería $-\infty$ o
  $+\infty$. Devolver `0` asume que "la ausencia de observaciones equivale a magnitud cero". Esto
  funciona de maravilla para medidas de desvío con `max` y cotas positivas (`<= 1.0`), pero fallaría si
  se midieran magnitudes que operan con números negativos o cotas inferiores estrictas.

### 8. `nucleo/medida.py:347-353`
```python
        # ANTES de medir: si falta con qué, no hay veredicto que dar. Medir igual produciría el
        # agregado sobre cero filas —que es 0— y un umbral `<= 0` lo leería como verde.
        faltante = next((r for r in self.requiere if not evidencia.get(r)), "")
        if faltante:
            return Veredicto(id=self.id, valor=0, ok=False, ...)
```
- **Veredicto**: **CÓDIGO CORRECTO, COMENTARIO SESGADO**.
- **Por qué**: La guarda `requiere` falla cerrado (`ok=False`), lo cual es seguro e impecable. Sin
  embargo, la prosa del comentario confiesa la inercia mental del núcleo: da por sentado que la
  evaluación normal de un agregado vacío da 0 y que el umbral es `<= 0`.

### 9. `nucleo/generador.py:504-505` y `fabricar_candidatos`
```python
rel2: ev_of.get(rel2, []),  # Solo 1 hecho en rel2 para mantener count=1
```
- **Veredicto**: **BOMBA SILENCIOSA**.
- **Por qué**: Al fabricar evidencia sintética para casos `falso_verde` (casos que deben disparar ROJO),
  el generador inyecta exactamente 1 fila ofensora asumiendo que `count=1` basta para romper el umbral.
  Si la medida tuviera un umbral permisivo (ej. `contar <= 5` o `snap.al_ras <= 1.0` con valores por
  defecto de `0.0`), el caso generado resulta VERDE en lugar de ROJO, inutilizando la generación
  automática de casos de fijación.

### 10. `tools/medida.py:57-64`
```python
PLANTILLA = """\
ninguno {mid}:
    de RELACION x
    donde x.CAMPO == false
    # segun: medicion · contrato · convencion · tanteo
    umbral <= 0 segun SEGUN porque "POR QUE ese numero y no otro. Si SEGUN es tanteo, esta explicacion es obligatoria."
    alcance "QUE NO VE esta medida. Obligatorio: un verde que no dice lo que no mira se lee como «esta bien»."
"""
```
- **Veredicto**: **SESGO EDITORIAL**.
- **Por qué**: El generador de medidas (`oracle medida nueva`) canaliza a todo usuario hacia la macro
  `ninguno` y clava `umbral <= 0`. No ofrece alternativa canónica ni menciona `peor`.

### 11. `tests/test_mutacion.py:102-106`
```python
    def test_el_equivalente_declarado_queda_afuera(self) -> None:
        """`convertir_conteo_en_existencia` cambia `contar` por `max(1)`. Con `umbral <= 0` —el de
        las 54 medidas del catálogo— «contar al menos una» y «existe alguna» son la misma
        afirmación..."""
        self.assertNotIn("convertir_conteo_en_existencia", MUTADORES)
```
- **Veredicto**: **TEST CON PREMISA VENCIDA**.
- **Por qué**: El arnés de pruebas unitarias cristalizó la exclusión global como contrato inmutable,
  asumiendo que las medidas siempre serán 54 y siempre `<= 0`.

---

## 4. La deuda de Oracle con su propio corpus: propuesta concreta

### ¿Es una deuda técnica?

**Sí, y es grave.** En la filosofía de Oracle, lo que no está ejercitado por el corpus no está
garantizado. Que el 100% de las medidas propias de Oracle tengan `umbral <= 0` significa que:
1. Oracle muta y certifica su propio código dentro de un subespacio degenerado (oráculos de conteo de
   ausencias).
2. La macro `peor.oracle` está huérfana en su propio árbol.
3. Las herramientas auxiliares (`generador.py`, `segundo_autor.py`) acumulan asunciones falsas que sólo
   estallan cuando un consumidor externo intenta usar el lenguaje en toda su riqueza.

### Propuesta concreta: `meta.antiguedad_de_sombras`

Para que el camino esté vivo en el catálogo de Oracle, debe existir una medida **propia de su dominio**
donde el umbral mayor a cero sea una necesidad semántica y no un artificio inventado para pasar un test.

Esa medida ya existe en espíritu, pero fue deformada para encajar en `ninguno`:
`meta.ninguna_sombra_envejece_sin_revisarse.oracle`.

Hoy dice:
```oracle
ninguno meta.ninguna_sombra_envejece_sin_revisarse:
    de sombra s
    donde s.dias > 90
    umbral <= 0 segun convencion porque "una sombra es una etapa de transición, y lo único que la distingue de apagar la medida es que alguien la vaya a sacar. Noventa días es un trimestre: tiempo de sobra para el arreglo que se pospuso, y poco para que el proyecto se acostumbre a no verla. El número lo eligió el equipo y no salió de medir nada — cambiarlo es una decisión, no la corrección de un error"
    alcance "cuenta días desde la fecha que la sombra declara..."
```

Al forzarla en `ninguno`, el número del dominio (`90` días) fue empujado al filtro (`donde s.dias > 90`),
resumiendo con `contar(1)` y dejando el umbral en `<= 0`.
Consecuencia: cuando falla, el reporte dice `✗ meta.ninguna_sombra_envejece_sin_revisarse 1 (<= 0)`.
Nadie sabe si la sombra tiene 91 días o 400 días.

#### La reformulación canónica con macro `peor`

Se propone incorporar o migrar hacia:

```oracle
peor meta.antiguedad_de_sombras:
    relacion sombra
    alias s
    expresion s.dias
    tolerancia 90
    umbral <= 90 segun convencion porque "una sombra es una etapa de transición, y noventa días es un trimestre: tiempo de sobra para el arreglo que se pospuso, y poco para que el proyecto se acostumbre a no verla. El número lo eligió el equipo y no salió de medir nada — cambiarlo es una decisión, no la corrección de un error"
    segun convencion
    alcance "mide la edad en días de la sombra más vieja del proyecto. NO juzga si el motivo sigue siendo válido, ni si alguien la miró en el medio, ni si el arreglo avanzó; una sombra revisada ayer y una olvidada hace un año se ven igual si la fecha no cambió. Tampoco ve una fecha que no se pueda leer o que esté en el futuro: eso da días negativos y lo mide meta.toda_sombra_declara_una_fecha_real"
```

#### Por qué esta medida es la solución óptima

1. **Dominio nativo**: Trata sobre sombras de Oracle (`oracle.json`), un concepto central de L2.
2. **Magnitud física real**: Mide tiempo en días (`dias`), una magnitud continua y monótona.
3. **Diagnóstico superior**: Al fallar, publica la edad real de la peor sombra:
   `✗ meta.antiguedad_de_sombras 142 (<= 90)` en lugar de un conteo ciego `1`.
4. **Ejercita la macro huérfana**: Pone en producción `nucleo/macros/peor.oracle` dentro del propio repo.
5. **Inmuniza el arnés**: Al existir en el catálogo base, cualquier función como
   `_todos_los_umbrales_son_menores_o_iguales_a_cero` falla inmediatamente en el CI de Oracle antes
   de llegar a romper repositorios de terceros.

---

## 5. Cómo vigilar esto automáticamente: medidas meta

Para que una asunción de "umbral 0" no vuelva a entrar por la puerta de atrás, se requieren dos
niveles de vigilancia:

### Nivel 1: Medida meta sobre las exclusiones del arnés

El arnés no debe admitir premisas que generalicen propiedades accidentales del catálogo local.
La medida `meta.ninguna_exclusion_de_mutador_se_apoya_en_una_premisa_falsa` demostró ser efectiva
al atrapar el error en Jam, pero falló en atraparlo en Oracle porque el catálogo de Oracle carecía
de contraejemplos.

Para blindar esto, se puede extender la relación `mutador_excluido` para que el emisor de hechos
(`nucleo/marco.py`) evalúe la premisa no sólo sobre el catálogo del proyecto, sino también sobre un
**catálogo sintético de referencia** que contenga medidas con umbrales diversos (`> 0`, `< 0`, `max`,
`promedio`). Si una exclusión se rompe en el catálogo de referencia, la exclusión es local y no puede
aplicarse globalmente al motor.

Adicionalmente, se puede formular la regla:
```oracle
ninguno meta.ninguna_exclusion_asume_catalogo_homogeneo:
    de mutador_excluido m
    donde m.premisa == "todas las medidas del catálogo tienen umbral <= 0"
    umbral <= 0 segun contrato porque "un mutador no puede excluirse del arnés general apoyándose en que todas las medidas del catálogo sean <= 0: la equivalencia semántica de una mutación es una propiedad de cada medida individual (su agregado y su umbral) y no una homogeneidad contingente del catálogo"
    alcance "vigila el texto de las premisas declaradas en EXCLUSIONES_DE_MUTADORES. NO juzga si mutadores individuales no declarados son equivalentes"
```

### Nivel 2: Medida meta sobre la completitud del catálogo base

Una medida que exija expresamente que el catálogo base de Oracle no sea monótono:

```oracle
medida meta.el_catalogo_base_ejercita_umbrales_positivos:
    de medida m
    donde m.umbral_valor > 0
    resumen contar(1)
    umbral >= 1 segun contrato porque "el catálogo de Oracle no puede ser monótonamente <= 0: debe contener al menos una medida con umbral mayor que cero para que el arnés de mutación, el generador de casos y las herramientas del marco ejerciten el camino no-cero de manera continua en su propio árbol"
    requiere medida
    alcance "cuenta medidas del catálogo con umbral estrictamente mayor que cero. NO juzga si los umbrales están bien justificados ni su unidad"
```

### Nivel 3: Refactor conceptual de la mutación

La verdadera solución arquitectónica a la rotura actual de `convertir_conteo_en_existencia` es que
**la equivalencia pertenece al mutador, no a una lista negra global**:

El mutador `convertir_conteo_en_existencia` en `mutadores/segundo_autor.py` ya sabe cuándo debilita
y cuándo es equivalente:
- Si `resumen == "contar"` y `umbral <= 0`: `contar(1)` y `max(1)` producen veredictos idénticos para
  cualquier entrada (0 da verde, $\ge 1$ da rojo). El mutante es idéntico por construcción.
- Si `resumen == "contar"` y `umbral <= 5`: `contar(1)` y `max(1)` divergen cuando hay 6 elementos
  (uno da rojo, el otro verde). El mutante es activo y discriminable.

Por lo tanto, la comprobación `if umbral[1] == "<=" and umbral[2] <= 0: return None` debe vivir
**adentro del propio mutador**. De esa manera, el mutador no genera mutantes equivalentes espurios
en medidas `<= 0`, genera mutantes reales en medidas con umbral $> 0$, y no requiere ninguna premisa
ni exclusión global en `nucleo/mutacion.py`.

---

## Conclusión

El umbral mayor que cero **es ciudadano de pleno derecho en la gramática y el álgebra de Oracle**,
como lo atestiguan la presencia de la macro estándar `peor.oracle` y la verificación limpia de
`snap.al_ras` en el motor de evaluación.

Sin embargo, **ha sido un extranjero en la práctica del repositorio**. Al escribir 52 medidas
exclusivamente con la forma `umbral <= 0`, los desarrolladores asumieron inconscientemente que el
mundo entero se reducía a oráculos de ausencia. Esa asunción vició el arnés de mutación, inutilizó
mutadores monótonos para medidas con `max` y cegó al generador automático de casos.

Reincorporar la cota métrica como ciudadana de primera en el catálogo propio (mediante
`meta.antiguedad_de_sombras`) y trasladar la detección de equivalencias del arnés global al mutador
individual es el paso necesario para que el lenguaje y la práctica vuelvan a coincidir.
