# Plan de Implementación: Corte 1 de un Aura Propio con Jam y Oracle

**Fecha:** 2026-09-21  
**Autor:** agy  
**Estado:** Plan de implementación concreto para la tarea `20260921-212821-aura-corte`  
**Lecturas previas requeridas:** `estudios/AURA-Y-ORACLE.md`, `estudios/MCP-CONTRATO.md`, `~/CLAUDE.md`, `~/Dev/jam/AGENTS.md` y `~/Dev/jam/RELEVO.md`.

---

## 1. El Ciclo de Verificación y Corrección

El bucle cerrado del agente operando sobre el motor de juego bajo la compuerta determinista de Oracle se estructura en siete pasos sucesivos:

```
    [1. Pedido del usuario]
               │
               ▼
    [2. Agente planifica y coloca] ──► Invoca herramientas de Jam en Unreal (tag `jam:preview`)
               │
               ▼
    [3. Sonda en JamPlayground]    ──► Headless (-RenderOffScreen -ExecCmds="py ...,QUIT_EDITOR")
               │
               ▼
    [4. Emisión de hechos L0]      ──► `Saved/Oracle/escena.json` (bolsas: pieza, vecina, objetivo)
               │
               ▼
    [5. Juicio por Oracle]         ──► `oracle juzgar` / `oracle_juzgar` (MCP)
               │
         ┌─────┴────────────────┐
         │ ¿Veredicto de Oracle?│
         └─────┬────────────────┘
               │
        ROJO   ▼                        VERDE ▼
   [6. Corrección por testigos]        [7. Confirmación del cambio]
   - Lee delta y piezas exactas         - Retira tag `jam:preview`
   - Ajusta posición / snap             - Piezas consolidadas en escena
   - Vuelve al paso 3                   - Reporte al usuario con alcance
```

### Detalle de cada paso:

1. **Pedido del usuario:** El usuario expresa una intención de diseño en lenguaje natural (ej. *"Colocá dos cajas de 100 cm apoyadas en el piso y alineadas al ras del muro norte, una al lado de la otra sin interpenetrarse"*).
2. **El agente planifica y coloca:** Claude Code o Codex (en la terminal host) calcula los parámetros de transformación iniciales y llama a la API de colocación de Jam (`jam.place.colocar` y `jam.snap`). Los actores se instancian en el mapa de trabajo marcados con la etiqueta `jam:preview`, asegurando aislamiento transaccional frente a la escena consolidada.
3. **Sonda del sensor en JamPlayground:** El agente dispara la ejecución desatendida del sensor sobre el proyecto host ligero (`JamPlayground`, arranque en ~15 s, evitando el costo de BotOO):
   ```bash
   ~/Dev/engines/UnrealEngine_5.8/Engine/Binaries/Linux/UnrealEditor \
     ~/Dev/games/JamPlayground/JamPlayground.uproject -RenderOffScreen -unattended -nosplash \
     -ExecCmds="py ~/Dev/jam/tools/experiments/sonda_colocacion_aura.py,QUIT_EDITOR"
   ```
   *Reglas de ejecución:* separar comandos con coma (no punto y coma) y nunca usar `-run=pythonscript` (los commandlets no tickean el render thread y hacen que `spawn_actor_from_object` devuelva `None`).
4. **Hechos JSON (Nivel L0):** La sonda dentro del editor extrae las geometrías de las piezas transitorias y sus vecinas mediante el adaptador `jam.ue`, volcando la evidencia estructurada a `Saved/Oracle/escena.json` con bolsas nombradas planas (`pieza`, `vecina`, `asentamiento`).
5. **Evaluación determinista:** El agente invoca `oracle juzgar --con Saved/Oracle/escena.json --proyecto ~/Dev/jam/medidas --confiar-escalares` (o la herramienta MCP `oracle_juzgar`). Oracle evalúa el catálogo efectivo aplicable sin tolerar acuerdos negociados.
6. **Bucle de corrección ante ROJO:** Si alguna medida falla (`ok: false`), Oracle no emite prosa probabilística: devuelve el id de la medida violada, el umbral contractual y los **testigos exactos** (por ejemplo: `Caja_B interpenetra 19.0 cm en Caja_A`). El agente toma esa cifra concreta, calcula el desplazamiento correctivo o invoca `jam.snap.al_ras` sobre el eje infractor, y reinicia desde el paso 3.
7. **Confirmación ante VERDE:** Si todas las medidas aplicables dan `ok: true`, se confirma el lote: se retiran los tags `jam:preview`, los actores quedan como parte de la escena persistente, y el agente concluye informando al usuario el veredicto positivo acompañado del alcance explícito declarado por las medidas (*qué NO se miró*).

---

## 2. Qué ya existe y qué falta (Archivo por archivo)

La inspección de la base de código de Jam y sus medidas revela una arquitectura avanzada pero con asperezas específicas para la automatización externa:

### 2.1 En el cerebro y adaptador de Jam (`~/Dev/jam/Content/Python/jam/`)

| Archivo | Estado actual (Qué ya existe) | Qué falta para el Corte 1 |
|---|---|---|
| `jam/place.py` | `colocar(asset, location, rotation, scale, surface, base, anchor, align, physics, view)` existe y es robusto. Maneja anclajes de pivote (`jam.pivot`), raycast vertical y soporte de assets. | Falta admitir ejecución no interactiva con persistencia en nivel sin depender del bucle de Slate de la UI de Jam. |
| `jam/snap.py` | `a_grilla(actor, grilla, snap_yaw, paso_yaw)` y `al_ras(actor, objetivo, eje, tol)` existen como funciones puras de traslación rígida y cuadratura. | Nada; sirve tal cual para los pasos de auto-corrección geométrica guiada por testigos. |
| `jam/ue.py` | Es el adaptador único a Unreal. Contiene `pieza()`, `piezas()`, `aabb()`, `raycast()`, `vecinos_en_zona()`, y el filtro de aislamiento `actores_de_jam()`. | Falta una función `volcar_hechos_escena(ruta_json, actores_sujeto, radio_vecinos)` que serialice directamente las relaciones L0 `pieza`, `vecina` y `asentamiento` a disco. |
| `jam/geometry.py` | Cerebro matemático puro sin `unreal`. Define `AABB`, `Pieza`, `Vec3`, `penetracion()`, `volumen()`, `es_fondo()` y constante `TOL_CM = 1.0`. | Completo para blockout rectangular; no contempla polígonos cóncavos ni mallas triangulares arbitrarias. |
| `jam/library.py` | `buscar()`, `cargar_placeable()`, `cargar_malla()`. Carga assets StaticMesh desde Content. | Completo para ubicar assets en disco. |
| `jam/oracle_placement.py` y `jam/oracle_snap.py` | Oráculos puros de referencia histórica en Python que calculan bounds, interpenetración, grilla y caras compartidas en memoria. | Sirven como oráculos de control para la prueba diferencial; el juicio operativo lo asume Oracle. |
| `jam/oracle_shadow.py` | Adaptador puro que traduce instancias de `Pieza` a hechos planos y evalúa contra `Motor.desde_proyecto("medidas")`. | Es el modelo canónico a seguir para la sonda headless que escribirá el JSON. |
| `jam/menu.py` | Contiene los selftests headless que prueban colocar, snap, scatter y physics en corridas sin GUI (`selftest_colocar()`, `selftest_snap()`). | Falta desacoplar el ciclo de prueba: hoy `selftest_colocar` destruye los actores inmediatamente al terminar; el agente necesita que queden en el mapa para inspección o confirmación. |

### 2.2 En sondas y experimentos (`~/Dev/jam/tools/experiments/`)

| Archivo | Estado actual | Qué falta |
|---|---|---|
| `tools/experiments/verifica_oracle_shadow.py` | Sonda de referencia para correr en editor completo (`UnrealEditor ... -ExecCmds="py ...,QUIT_EDITOR"`). Verifica que el puente con Oracle esté vivo. | Corre selftests fijos en memoria, no un escenario configurable alimentado por un agente. |
| `tools/experiments/verifica_physics_paint_58.py` | Demuestra spawn de actores reales en nivel (`spawn_actor_from_class`) y medición de apilado físico sobre suelo. | Específico para apilado vertical; no emite JSON a disco. |
| **FALTA: `tools/experiments/sonda_colocacion_aura.py`** | **No existe.** | Se debe crear esta sonda dedicada que: (1) lea una orden de colocación desde un archivo transitorio `Saved/Oracle/orden.json` o tome los actores `jam:preview` presentes en el nivel; (2) extraiga sus hechos geométricos L0; y (3) los guarde en `Saved/Oracle/escena.json` antes de salir. |

### 2.3 En el catálogo y relaciones de medidas (`~/Dev/jam/medidas/`)

El proyecto `medidas/` de Jam cuenta con catálogos funcionales divididos por carpetas de dominio:

#### Medidas de Jam que sirven de juez tal como están:
1. `catalogos/geometria/colocacion.interpenetracion.json`:  
   Juzga que la penetración efectiva entre `pieza` y `vecina` (descontando escenografía de fondo con `es_fondo`) sea `<= 0`. Tolerancia de 1.0 cm ya absorbida en la escalar `penetracion`.
2. `catalogos/geometria/colocacion.bounds.json`:  
   Exige que ninguna pieza tenga volumen degenerado `<= 0.001 cm³` (detecta mallas rotas o sin colisión).
3. `catalogos/geometria/snap.al_ras.json`:  
   Verifica que la distancia entre caras sobre el eje solicitado sea `<= 1.0 cm` (evita tanto huecos como penetraciones).
4. `catalogos/geometria/snap.comparte_cara.json`:  
   Exige que el solape lateral entre las dos piezas que se tocan sea `> 1.0 cm`, impidiendo falsos contactos donde las piezas sólo se tocan por una arista o vértice diagonal.
5. `catalogos/geometria/snap.grilla.json` y `snap.yaw.json`:  
   Controlan que el pivote y la rotación no presenten derivas espaciales arbitrarias (desvíos menores a 1.0 cm y 0.5°).
6. `catalogos/physics/physics.tiene_suelo.json` y `physics.apoyado.json`:  
   Comprueban que toda pieza colocada cuente con soporte físico debajo y que su base descanse sobre la cota superior del soporte (`gap <= 1.0 cm`), detectando objetos flotando o hundidos.

#### Medidas que faltan para un juicio completo de colocación:
1. `colocacion.tanda_sin_interpenetracion`:  
   `colocacion.interpenetracion` hoy asume que la evidencia entrega un sujeto en `pieza` y sus vecinos en `vecina`. Cuando un agente coloca un lote de $N$ actores en un solo turno, hace falta una medida que juzgue todos los pares $(a, b)$ de la tanda entre sí dentro de la misma relación.
2. `colocacion.asentada_en_terreno`:  
   `physics.apoyado` evalúa AABB contra AABB. En Jam quedó documentada la trampa crítica de que el AABB de un landscape cubre el mapa entero (hasta la loma más alta), dejando las piezas flotando a metros de altura. Falta una medida que evalúe la evidencia emitida por raycast vertical (`ue.raycast`) directo a la superficie real del terreno.
3. `colocacion.zona_permitida`:  
   Medida que valide contención: que ninguna pieza del lote caiga fuera del volumen o área designada en el encargo del usuario.
4. **Relaciones formales (`medidas/relaciones/`):**  
   Jam no tiene creada la carpeta `medidas/relaciones/`. En `medidas/oracle.json` arrastra en sombra la medida `meta.toda_cantidad_comparada_tiene_unidad_derivable` con cota 54 justamente por no haber formalizado los esquemas JSON de `pieza`, `vecina` y `asentamiento`. Declarar estos esquemas es indispensable para cerrar la deuda.

### 2.4 En el tracker de Jam (`~/Dev/jam/tareas/`)

El tracker propio de Jam fue inicializado el 2026-09-19 (tarea `20260919-140704-tracker`, commit `c40fc74`). Contiene 57 tareas abiertas que administran los pendientes reales del plugin. Al momento de implementar este corte, las tareas concretas derivadas deben asentarse en este tracker.

---

## 3. El Primer Escenario de Prueba (Mínimo y Medible)

Para validar el ciclo sin dispersión, el escenario 1 debe usar activos estándar del motor (`/Engine/BasicShapes/Cube.Cube`), dimensiones conocidas y umbrales ya contrastados.

### 3.1 Qué pide el usuario
> *"Colocá dos cajas de madera (`Caja_A` y `Caja_B`, cubos de 100×100×100 cm) sobre el suelo (`Z=0`), alineadas al ras de la cara frontal del `Muro_Norte` (ubicado en `(0, 0, 100)` con dimensiones 400×20×200 cm), una al lado de la otra en X sin interpenetrarse entre sí ni penetrar el muro."*

### 3.2 Paso inicial con fallo inyectado (ROJO)
El agente ejecuta su primer intento cometiendo dos errores típicos de síntesis geométrica:
- Ubica `Caja_A` en `( -60, 50, 50 )`: como la cara del muro llega hasta $Y = 10$, y la caja centrada en $Y = 50$ con semi-extensión $50$ extiende su cara trasera hasta $Y = 0$, `Caja_A` penetra **10 cm** dentro del muro.
- Ubica `Caja_B` en `( -30, 70, 50 )`: como ambas tienen ancho 100 cm (semi-extensión 50), la distancia entre centros en X es de 30 cm cuando la suma de semi-extensiones es 100 cm. `Caja_B` penetra **70 cm** dentro de `Caja_A`.

### 3.3 Hechos JSON L0 emitidos por la sonda (`Saved/Oracle/escena.json`)
```json
{
  "pieza": [
    {
      "id": "Caja_A", "ox": -60.0, "oy": 50.0, "oz": 50.0,
      "ex": 50.0, "ey": 50.0, "ez": 50.0,
      "lx": -60.0, "ly": 50.0, "lz": 50.0, "yaw": 0.0
    },
    {
      "id": "Caja_B", "ox": -30.0, "oy": 70.0, "oz": 50.0,
      "ex": 50.0, "ey": 50.0, "ez": 50.0,
      "lx": -30.0, "ly": 70.0, "lz": 50.0, "yaw": 0.0
    }
  ],
  "vecina": [
    {
      "id": "Muro_Norte", "ox": 0.0, "oy": 0.0, "oz": 100.0,
      "ex": 200.0, "ey": 10.0, "ez": 100.0,
      "lx": 0.0, "ly": 0.0, "lz": 100.0, "yaw": 0.0
    },
    {
      "id": "Caja_A", "ox": -60.0, "oy": 50.0, "oz": 50.0,
      "ex": 50.0, "ey": 50.0, "ez": 50.0,
      "lx": -60.0, "ly": 50.0, "lz": 50.0, "yaw": 0.0
    }
  ],
  "objetivo": [
    {
      "id": "Muro_Norte", "ox": 0.0, "oy": 0.0, "oz": 100.0,
      "ex": 200.0, "ey": 10.0, "ez": 100.0,
      "lx": 0.0, "ly": 0.0, "lz": 100.0, "yaw": 0.0,
      "eje": "y"
    }
  ]
}
```

### 3.4 Dictamen del Juez (ROJO)
Al evaluar este JSON, Oracle emite veredicto reprobatorio:
1. `colocacion.interpenetracion`: **ROJO**  
   - Testigo 1: `(Caja_A, Muro_Norte) -> penetracion = 9.0 cm` (descontada la tolerancia de 1 cm sobre los 10 cm de solape).  
   - Testigo 2: `(Caja_B, Caja_A) -> penetracion = 69.0 cm`.
2. `snap.al_ras`: **ROJO**  
   - Testigo: `(Caja_A, Muro_Norte, eje Y) -> desvio_de_contacto = 10.0 cm > 1.0 cm`.

### 3.5 Corrección guiada por testigos y paso VERDE
El agente no necesita "re-imaginar" la escena:
- Corrige la penetración en Y aplicando `snap.al_ras("Caja_A", "Muro_Norte", "y")`: el centro en Y se traslada a `60.0 cm` ($10 + 50$).
- Corrige la penetración en X trasladando `Caja_B` a $X = 40.0 \text{ cm}$ (dejando las caras en contacto a $X = -10$ y $X = -10$) o a $X = 50.0 \text{ cm}$ (dejando 10 cm de luz), y cuadrando su Y a `60.0 cm`.
- Al volver a correr la sonda:
  - `colocacion.interpenetracion`: **VERDE** (0 pares con penetración > 0).
  - `colocacion.bounds`: **VERDE** (volumen de ambas es $1.000.000 \text{ cm}^3 > 0.001$).
  - `snap.al_ras`: **VERDE** (desvío de contacto en Y es $0.0 \text{ cm} \le 1.0$).
  - `snap.comparte_cara`: **VERDE** (solape lateral en X es $100.0 \text{ cm} > 1.0$).
  - `Informe final`: VERDE en 4 medidas. **SIN MIRAR:** visibilidad de mallas, solape de triángulos cóncavos ni oclusión.

---

## 4. Quién es el Agente en el Corte 1

Para mantener el diseño austero y libre de abstracciones prematuras:
1. **El agente no es un orquestador nuevo:** No se desarrollará un daemon en Python ni una arquitectura de subagentes en cascada. El agente ejecutor es **Claude Code** o **Codex** operando directamente en el entorno de desarrollo.
2. **Protocolo:**
   - Consume **Oracle** a través de su servidor MCP oficial (`oracle-mcp`) usando la herramienta `oracle_juzgar`, o invocando `oracle juzgar` por shell.
   - Consume **Jam / Unreal** a través de un comando de automatización.
3. **La herramienta que le falta del lado de Unreal:**
   - Actualmente, Jam expone sus capacidades mediante botones y gestos en C++ Slate (`JamEditor`) o mediante scripts unitarios hardcodeados. El viejo receptor `conductor/receptors/unreal-mcp/` fue dado de baja.
   - **Herramienta faltante:** Un script CLI headless parametrizable en Jam:
     ```bash
     python tools/jam_comando.py colocar --asset "/Engine/BasicShapes/Cube.Cube" \
       --loc "0,60,50" --tag "jam:preview" --salida-hechos "Saved/Oracle/escena.json"
     ```
     que invoque `UnrealEditor JamPlayground.uproject -RenderOffScreen ...` ejecutando la acción solicitada y emitiendo la evidencia sin requerir intervención manual en la GUI.

---

## 5. Riesgos y lo que queda fuera

### 5.1 Riesgos técnicos y mitigaciones

1. **Latencia del arranque de Unreal Engine:**  
   *Riesgo:* Aunque JamPlayground arranca en ~15 s (contra 3 minutos de BotOO), un ciclo de 4 iteraciones de corrección sumaría 1 minuto completo de reloj.  
   *Mitigación:* Para corridas batch o CI, 1 minuto es plenamente admisible. Para desarrollo interactivo diario, el agente puede comunicarse con una sesión de Unreal Editor que permanezca abierta mediante un puerto local o pipe de comandos, reduciendo la recolección de evidencia a ~200 ms.
2. **Goodhart de segundo orden (El agente adultera el sensor):**  
   *Riesgo:* Si se le pide al LLM *"hacé que la colocación dé verde"* y se le concede acceso de escritura a todo el repo, el agente podría optar por modificar `medidas/catalogos/` o vaciar la emisión de `jam/ue.py`.  
   *Mitigación:* Custodia y permisos estrictos: durante la tarea de nivel, el directorio `medidas/` y los archivos de sensor en `Content/Python/jam/` deben permanecer bajo acceso de sólo lectura.
3. **Falsos verdes por evidencia vacía (Goodhart de primer orden):**  
   *Riesgo:* Si el comando de colocación falla catastróficamente y el sensor emite una lista `pieza: []`, las medidas de conteo de defectos reportarán cero infracciones y saldrán en verde sin haber colocado nada.  
   *Mitigación:* Exigir que todas las medidas de colocación declaren la cláusula `requiere` para sus fuentes, asegurando que Oracle aborte con `SIN EVIDENCIA` si no se detectan los actores colocados.
4. **Falsos rojos por aproximación AABB en mallas no convexas:**  
   *Riesgo:* Dos piezas en forma de L encajadas correctamente tienen cajas envolventes (AABB) que solapan fuertemente.  
   *Mitigación:* Delimitar el alcance: el Corte 1 aplica a blockout con volúmenes ortogonales y cajas de colisión convexas, documentando explícitamente en el `alcance` que la geometría fina interior no es observada.

### 5.2 Lo que queda fuera (Godot y Unity)

- **Fuera del Corte 1:** Queda totalmente excluida cualquier línea de código o script para Unity o Godot. Intentar abordar múltiples motores en el primer paso multiplicaría las incógnitas de integración.
- **Cuándo entran:**  
  Entrarán una vez que el bucle en Unreal sobre `JamPlayground` esté cerrado, documentado y verificado en verde en CI.
- **Con qué sensores entrarán:**  
  - **Godot:** Se implementará un script ligero en GDScript (`addons/oracle_sensor/sensor.gd`) que recorra el árbol de nodos de la escena (`Node3D`) en modo `--headless` (arranca en ~300 ms) y serialice los `Transform3D` y `AABB` de los `CollisionShape3D` a las mismas bolsas `pieza` y `vecina`.
  - **Unity:** Se implementará una rutina C# Editor (`Packages/JamOracle/Editor/SceneSensor.cs`) que recorra los `GameObject` activos y serialice los `Collider.bounds` a JSON.
  - **El Juez no cambia:** El catálogo `.oracle` de colocación, las tolerancias de contacto y el álgebra de Oracle no se modificarán; sólo cambiará el emisor de los hechos.

---
