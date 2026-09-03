# Plan 0.5.0 — el ámbito de una medida

**Fecha:** 2026-09-03 · **Estado:** en curso

## El hueco

Oracle contesta hoy dos preguntas y cree que contesta tres:

| pregunta | quién la contesta |
|---|---|
| ¿de dónde vino la medida? | el catálogo base, los perfiles, las bibliotecas |
| **¿para qué proyecto obliga?** | **nadie** |
| ¿hay hechos para calcularla? | `medidas_aplicables` |

«Universal» significa hoy una sola cosa: vivir en el directorio del paquete. Eso es **procedencia**,
no **ámbito**. Coincidieron hasta ahora porque todo lo que Oracle empaquetaba obligaba a todos.

Dejó de coincidir el 2026-09-03, cuando
`meta.ninguna_exclusion_de_mutador_se_apoya_en_una_premisa_falsa` —una medida sobre
`EXCLUSIONES_DE_MUTADORES`, configuración del repositorio de Oracle— puso a **Jam en rojo**, y fue
el único rojo duro que Jam tenía. Jam no tiene ningún remedio disponible en su propio repositorio:
la exclusión vive en `nucleo/mutacion.py`. El criterio ya estaba escrito en `DECISION-009`: **un
rojo sobre el que el receptor no puede actuar enseña a ignorar la herramienta.**

Poder calcular un veredicto no vuelve pertinente ese veredicto. Ése es el hueco.

## Lo que se agrega

Una declaración más en la medida, relativa al **origen** y no a Oracle:

```text
ambito universal    obliga a todo proyecto que seleccione el catálogo y aporte la evidencia
ambito del_origen   obliga sólo cuando el proyecto evaluado es el dueño de la medida
```

En una medida del catálogo base, `del_origen` significa de Oracle. En una medida escrita dentro de
Jam significa de Jam, y se satisface sola. En una biblioteca publicada significa de su publicador,
no de quien la instale. Oracle no gana un privilegio nominal en el lenguaje.

**Sin valor por omisión creíble.** Suponer `universal` reproduce la fuga que abre este plan; suponer
`del_origen` apaga en silencio las guardas que hoy sí deben viajar. La migración reifica
`sin_declarar` —como hizo `segun`— y una medida lo pone en rojo.

## Lo que NO es

- **No es un nivel nuevo.** Verificado el 2026-09-03: el catálogo tiene 55 medidas, la relación
  `medida` tiene 55 filas, y `meta.ninguna_medida_sin_alcance` está entre las filas que juzga. L2 es
  un punto fijo. El ámbito entra como **campo** de una representación que ya existe, al lado de
  `alcance`, `segun` y `umbral_op`. Un nivel existe cuando hay una representación nueva de la que
  hablar; el ámbito no la trae. `DECISION-005` ya lo había resuelto en general: «colapsa, no falta».
- **No es visibilidad.** `private` es un nombre engañoso acá: en un lenguaje la visibilidad controla
  quién puede nombrar o llamar una pieza, y Oracle no tiene composición de medidas por
  `DECISION-002`. No hay llamadas que prohibir, ni jerarquía que justifique un `protected`. La
  analogía correcta es la **jurisdicción de una regla**: todos pueden leerla, sólo dicta veredicto
  donde hay responsabilidad para responderlo.
- **No es ocultamiento.** Una medida `del_origen` sigue en el manual, sigue reificada, sigue
  mutando y sigue teniendo corpus. Lo único que no hace es obligar a un tercero.

## El orden de las preguntas

```text
selección del catálogo  →  ámbito  →  aplicabilidad por relaciones  →  evaluación
qué acepté                 dónde obliga    si puede calcularse            qué dio
```

La identidad de origen tiene que ser **lógica** —proyecto, id de biblioteca, perfil, catálogo base—
y no igualdad de rutas: en el repositorio y en el paquete instalado el mismo origen tiene layouts
distintos (`DECISION-010`). La ruta sirve para diagnosticar un archivo repetido; no define
jurisdicción.

## Las tres capas

### Capa 1 — lenguaje

- `ambito` como vocabulario cerrado en `nucleo/vocabulario.py`, cada opción con su sentido.
- Campo `ambito` en `Medida`, con `AMBITO_SIN_DECLARAR` como estado de migración.
- Las **dos** superficies: la infija (`.oracle`) y la posicional (`.json`), leer y escribir.
- Reificación: `como_hechos` emite `ambito` en la relación `medida`.

### Capa 2 — carga

- `cargar_catalogo` conserva la **procedencia** de cada medida en vez de reducirla a `dict[id, Medida]`.
- Una medida `del_origen` entra al catálogo efectivo sólo cuando origen y destino coinciden.
- `catalogo_universal()` deja de llamar universal a todo lo que carga del directorio empaquetado:
  enumera como universales sólo las que lo declaran.
- Las **relaciones** también declaran ámbito — la cota de la capa 3 necesita saber que
  `mutador_excluido` es del origen. Toca `hechos_de_relaciones`, no la numeración de niveles.

### Capa 3 — política

- `meta.toda_medida_declara_su_ambito` — la de presencia, espejo de `meta.todo_umbral_declara_de_donde_sale`.
- `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias` — la cota comprobable.
  Necesita reificar `dependencia_de_medida(medida, relacion, clase)`, con `clase` en `fuente` o
  `requiere`, en vez de dos políticas casi iguales. Eso no compone medidas: es reificación mecánica
  de la declaración, el camino que `DECISION-002` conserva para L2.
  Su `alcance` tiene que decir algo incómodo y exacto: **detecta una declaración más amplia que una
  dependencia conocida; no demuestra que toda medida universal sea realmente universal**, y sobre
  todo no demuestra que el receptor tenga un remedio disponible.
- Casos de corpus de las dos polaridades para cada una.
- Migrar las 55 medidas del catálogo base declarando su ámbito.
- `DECISION-012`.

## La asimetría, y por qué se acepta

Mentir hacia lo amplio perjudica al consumidor y debe fallar ante toda contradicción derivable.
Declarar un ámbito demasiado estrecho pierde cobertura, pero no impone un rojo sin remedio; se
discute con evidencia externa y revisión humana. Oracle vuelve falsable la declaración; no la
convierte en verdad.

## Deuda que este plan NO cierra

Queda anotada acá para que no se pierda, documentada en `estudios/EL-UMBRAL-MAYOR-QUE-CERO.md`:

- **La exclusión de mutadores se aplica en tiempo de importación, incondicionalmente**
  (`nucleo/mutacion.py:177`). Aunque `premisa_vale` sea falso, el mutador sigue desactivado. La
  alarma se pone roja y el arnés sigue haciendo lo incorrecto. Se arregla excluyendo **por medida**,
  no por catálogo.
- **El catálogo base de Oracle nunca ejerció un umbral > 0**: 55 de 55 son `<= 0`, incluida la única
  que usa la macro `peor`, con tolerancia 0. El camino está vivo en Jam (`snap.al_ras <= 1.0`,
  `snap.grilla <= 1.0`, `snap.yaw <= 0.5`) y en la biblioteca de ejemplo
  (`meta.segtem.todo_umbral_declara_origen`, `<= 5`), pero no en el catálogo que Oracle publica.
  Que el único ejemplo con umbral > 0 del repositorio viva en `ejemplo/` es justamente lo que
  permitió que la exclusión global pasara inadvertida: el catálogo base no la contradecía nunca.
- **El generador fabrica un `falso_verde` con una sola fila ofensora** (`nucleo/generador.py:504`),
  asumiendo que `count=1` rompe el umbral. Con un umbral permisivo el caso sale verde en vez de
  rojo, sin avisar.
