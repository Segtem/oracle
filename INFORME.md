# Informe de tarea: Reemplazo de invocaciones por ruta hacia el comando `oracle`

## Qué cambié, archivo por archivo, y por qué

### `ORACLE-TUTORIAL-PRACTICO.md`
- **Línea 111**: Se reemplazó `python tools/medida.py --nueva dominio.regla` por `oracle nueva dominio.regla`. Crea el andamio de la medida directamente en superficie infija (`.oracle`) usando el CLI unificado.
- **Línea 272**: Se reemplazó `python tools/medida.py --expandir <archivo>` por `oracle expandir <archivo>`. Muestra la expansión de la macro a su forma canónica.
- **Línea 474**: Se reemplazó `python tools/medida.py --escalares` por `oracle escalares`. Muestra el inventario de funciones escalares, comparadores, operadores y agregados.
- **Líneas 708–717 (Sección 8.6)**: Se reemplazaron las tres invocaciones que exigían conocer `<ruta-a-oracle>` (`python <ruta-a-oracle>/tools/medida.py --proyecto . --relaciones`, `python <ruta-a-oracle>/tools/aceptacion.py --proyecto .`, `python <ruta-a-oracle>/tools/mutar.py --proyecto .`) por `oracle relaciones` y `oracle test`. Se actualizó la prosa posterior para referenciar `oracle test` y la mutación en lugar de los scripts sueltos `aceptacion.py` y `mutar.py`.

### `corpus/README.md`
- **Línea 63**: Se reemplazó `python tools/corpus.py --nuevo <grupo/NNN-descripcion>` por `oracle caso <grupo/NNN-descripcion>`. Crea el andamio del caso directamente en superficie (`.caso`).

### `ORACLE-PARA-NOTEBOOKLM.md` y directorio `estudio/`
- Se regeneraron con `python tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md` y `python tools/estudio.py --destino estudio` para mantener sincronizada la documentación plana y el árbol de estudio tras las modificaciones.

---

## Comandos nuevos corridos (salidas reales)

### `oracle nueva dominio.regla`
```
creada: catalogos/dominio/dominio.regla.oracle

Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:
  oracle revisar catalogos/dominio/dominio.regla.oracle
```

### `oracle expandir catalogos/proceso/proceso.test_con_mutante_que_lo_mata.oracle`
```
[
 "medida",
 "proceso.test_con_mutante_que_lo_mata",
 [
  "desde",
  [
   "de",
   "mutante",
   "m"
  ],
  [
   "donde",
   [
    "y",
    [
     "==",
     [
      "campo",
      "m",
      "detecciones_conductuales"
     ],
     0
    ],
    [
     "==",
     [
      "campo",
      "m",
      "rechazos_del_algebra"
     ],
     0
    ]
   ]
  ]
 ],
 [
  "resumen",
  "contar",
  1
 ],
 [
  "umbral",
  "<=",
  0,
  "un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada. Cuenta como detección cualquiera de las tres formas en que un caso puede notarlo —invertir el veredicto, cambiar los testigos o cambiar el valor— porque las tres son contrato: los testigos son lo que una persona LEE para actuar, y el valor explica cuánto y no sólo de qué lado cayó. Un rechazo del álgebra tampoco deja al mutante vivo, pero es otra cosa y por eso se cuenta aparte: ahí ningún caso discriminó nada, el mutante ni siquiera llegó a evaluar"
 ],
 [
  "alcance",
  "cuenta mutantes que ningún caso observó, de ninguna de las cuatro maneras. NO ve los mutantes que nadie generó: una medida sin ningún mutador aplicable da cero y sale verde. Tampoco distingue un mutante equivalente —imposible de matar— de uno que el corpus todavía no fija; esa diferencia hay que declararla a mano"
 ]
]
```

### `oracle escalares`
```
FUNCIONES ESCALARES declaradas (el mecanismo de UDF):

  cerca/2
      Distancia absoluta entre dos cantidades. Es el reemplazo de la igualdad exacta.
  contiene/2
      ¿`aguja` aparece en `texto`? Sensible a mayúsculas a propósito: se usa para exigir que un
  mas/2
      Suma. Es aritmética sobre cantidades medidas, y eso no es de ningún dominio.
  menos/2
      
  por/2
      Producto. Aritmética sobre cantidades medidas, igual que `mas`: no es de ningún dominio.

COMPARADORES: == != < <= > >=
LÓGICOS: y  o  no
AGREGADOS: contar max min promedio suma
ACCESORES: ["campo", alias, nombre] · ["hecho", alias] · ["col", nombre]
OPERADORES: de · donde · unir · resumen   (con y agrupar todavía no tienen usuario)
```

### `oracle caso proceso/099-ejemplo`
```
creado: corpus/proceso/099-ejemplo.caso

Reemplazá los marcadores en MAYÚSCULAS. Después:
  oracle test
```

### `oracle relaciones`
```
RELACIONES que se pueden medir hoy:

  afirmacion
      alcance                      str
      comando                      str
      id                           str
      texto                        str
      · aparece en: 001-verde-acumulativo, 020-una-afirmacion-sin-alcance-alcanza, 104-afirmacion-con-alcance

  alcanzable
      desde                        str
      hasta                        str
      saltos                       int
      · aparece en: 015-racimo-inalcanzable, 024-una-variante-no-vacia-inalcanzable, 044-sin-grafo-de-alcance-sale-verde

  archivo
      ruta                         str
      sintaxis_valida              bool
      · aparece en: 010-sed-desindenta, 107-reruteo-sin-romper-sintaxis

  cambio
      archivo                      str
      commiteado                   bool
      es_codigo_vivo               bool
      · aparece en: 007-relevo-verde-arbol-sucio, 021-un-cambio-vivo-invalida-la-verificacion, 102-verificacion-vigente

  conclusion
      causa_atribuida              str
      causa_real                   str
      medicion                     str
      texto                        str
      · aparece en: 011-conclusion-errada-desvan

  corrida
      determinista                 bool
      escenario                    str
      falto                        int
      id                           str
      pasos                        int
      presupuesto_agotado          bool
      razon                        str
      semilla                      int
      sobro                        int
      · aparece en: 200-corrida-sin-ninguna-corrida, 201-presupuesto-sin-ninguna-corrida, 301-simulador-que-ignora-la-semilla

  corrida_mutacion
      baseline_verde               bool
      bytecode_frio                bool
      errores_arnes                int
      id                           str
      mutantes                     int
      resultado_confiable          bool
      rondas_cache_verificadas     int
      tests_fallaron               int
      timeouts                     int
      · aparece en: 006-arnes-bytecode-viejo, 013-comparadores-del-algebra-sin-ejercitar, 016-timeout-contado-como-mutante-muerto

  declaracion
      coinciden                    bool
      condicion_repetida           bool
      medida                       str
      mide                         str
      testigos                     str
      umbral_declarado             float
      umbral_en_filtro             float
      · aparece en: 004-testigos-duplicados, 012-umbral-duplicado-en-filtro-y-umbral

  desvio_yaw_generado
      grados                       float
      · aparece en: 005-mutante-yaw-sin-franja

  edicion_masiva
      archivos                     int
      herramienta                  str
      verifico_sintaxis_despues    bool
      · aparece en: 010-sed-desindenta, 107-reruteo-sin-romper-sintaxis

  equivalencia
      caso                         str
      error                        str
      evaluo                       bool
      mismo_valor                  bool
      mismo_veredicto              bool
      mismos_testigos              bool
      origen                       str
      propiedad                    str
      · aparece en: 100-donde-no-compone, 101-donde-compone-bien, 102-unir-no-conmuta

  evento
      actor                        str
      corrida                      str
      falta                        int
      que                          str
      t                            int
      · aparece en: 202-traza-sin-ningun-evento, 301-simulador-que-ignora-la-semilla, 305-traza-con-hueco

  generador
      cubre_caso_fondo             bool
      cubre_franja_0.5_a_5_grados  bool
      id                           str
      produce                      str
      · aparece en: 003-mutante-fondo-nunca-ejercitado, 005-mutante-yaw-sin-franja

  hallazgo
      era_real                     bool
      objetivo                     str
      verificador                  str
      · aparece en: 008-vault-falso-rojo, 022-un-falso-rojo-ya-rompe-el-verificador, 103-vault-sin-falsos-rojos

  importa
      a                            str
      b                            str
      es_test                      bool
      · aparece en: 009-modulo-sin-consumidor, 015-racimo-inalcanzable, 023-un-import-ajeno-no-es-consumidor

  medida
      alcance                      str
      comparador                   str
      id                           str
      porque                       str
      umbral_es_flotante           bool
      · aparece en: 061-ausencia-sin-requiere, 062-ausencia-cubierta-o-no-aplica, 063-ausencia-sin-terminos-no-concluye

  modulo
      alcanzable                   bool
      es_paquete_vacio             bool
      es_test                      bool
      importable                   bool
      importadores                 int
      lineas                       int
      nombre                       str
      tests                        int
      · aparece en: 009-modulo-sin-consumidor, 011-conclusion-errada-desvan, 015-racimo-inalcanzable

  mutante
      apunta_a                     str
      cambio                       str
      codigo_salida                int
      detecciones_conductuales     int
      equivalente_declarado        bool
      error_arnes                  bool
      estado                       str
      id                           str
      murio                        bool
      razon_equivalente            str
      rechazos_del_algebra         int
      tests_fallaron               bool
      timeout                      bool
      · aparece en: 002-mutante-firma-por-id, 003-mutante-fondo-nunca-ejercitado, 005-mutante-yaw-sin-franja

  nodo
      cabeza                       str
      declarados                   int
      evaluados                    int
      · aparece en: 055-logico-cortocircuito, 056-logico-evalua-todo, 057-un-solo-cortocircuito

  paso
      filas_antes                  int
      filas_despues                int
      operador                     str
      t                            int
      · aparece en: 049-donde-agrego-filas, 050-donde-filtra-como-debe, 051-agrupar-invento-un-grupo

  producto
      derecha                      int
      izquierda                    int
      salida                       int
      · aparece en: 053-unir-perdio-un-par, 054-unir-materializa-el-producto

  termino
      cabeza                       str
      medida                       str
      · aparece en: 061-ausencia-sin-requiere, 062-ausencia-cubierta-o-no-aplica, 063-ausencia-sin-terminos-no-concluye

  test
      archivo                      str
      cubre                        str
      id                           str
      · aparece en: 002-mutante-firma-por-id, 014-mutador-dejo-un-archivo-mutado-al-ser-matado

  verificacion
      camino                       str
      commit                       str
      que                          str
      · aparece en: 007-relevo-verde-arbol-sucio, 102-verificacion-vigente

Un hecho nuevo se agrega desde su SENSOR, no acá: el sensor produce, el álgebra juzga.
```

---

## Qué NO hice y por qué

Se ejecutó `grep -rn "python tools/" --include='*.md' . | grep -v ORACLE-PARA-NOTEBOOKLM | grep -v estudio/ | grep -v TAREA.md | grep -v DOCTRINA.md` y quedaron exactamente las siguientes 7 invocaciones justificadas:

1. `corpus/README.md:12` — `python tools/corpus.py --resumen`:
   - **Por qué no se tocó**: Es una herramienta de resumen estadístico del corpus (desglosa casos por etiqueta, forma de detección, estados abiertos/resueltos y medidas reclamadas) para la sección «Lo que dicen los números». `oracle` no implementa un subcomando `resumen` ni bandera `--resumen`.
2. `README.md:392` — `python tools/cifras.py`:
   - **Por qué no se tocó**: Es una herramienta de mantenimiento interno del repositorio Oracle (inspecciona y refresca las cifras publicadas en README y DOCTRINA). No forma parte del recorrido de un autor de medidas y no existe `oracle cifras`.
3. `README.md:393` — `python tools/verificar_instalacion.py`:
   - **Por qué no se tocó**: Es una verificación interna de empaquetado (wheel) e instalación limpia del binario, ejecutada en CI. No tiene equivalente en el comando `oracle`.
4. `ORACLE-TUTORIAL-PRACTICO.md:110` — `python tools/sintaxis.py --imprimir catalogos/proceso/...`:
   - **Por qué no se tocó**: Muestra la traducción de una medida guardada en JSON a su representación en superficie infija. El comando `oracle` no tiene subcomando `imprimir` ni `traducir`.
5. `ORACLE-TUTORIAL-PRACTICO.md:112` — `python tools/sintaxis.py --leer medida.oracle`:
   - **Por qué no se tocó**: Muestra la traducción inversa de superficie infija a JSON. El comando `oracle` no implementa `oracle leer`.
6. `ESCRIBIR-UNA-MEDIDA.md:77` — `python tools/sintaxis.py --imprimir <archivo.json>`:
   - **Por qué no se tocó**: Mismo motivo: traducción manual de JSON a superficie infija para medidas legadas, sin equivalente en `oracle`.
7. `ESCRIBIR-UNA-MEDIDA.md:78` — `python tools/sintaxis.py --leer <archivo.oracle>`:
   - **Por qué no se tocó**: Mismo motivo: traducción manual de superficie a JSON, sin equivalente en `oracle`.

Tampoco se tocaron archivos `.py`, `.json`, `.oracle`, `.caso`, `PLAN-LENGUAJE.md`, `ESPECIFICACION.md` ni los `DECISION-*.md`.

---

## Lo que descubrí que no me pediste

1. **Sección 8.6 del tutorial práctico (`ORACLE-TUTORIAL-PRACTICO.md`)**:
   En la sección «8.6 Correr todo», el tutorial guiaba al lector a ejecutar `python <ruta-a-oracle>/tools/medida.py --proyecto . --relaciones`, `python <ruta-a-oracle>/tools/aceptacion.py ...` y `python <ruta-a-oracle>/tools/mutar.py ...`. No coincidía con el grep literal de `python tools/` debido al prefijo `<ruta-a-oracle>/`, pero sufría exactamente del problema planteado en la tarea: obligaba a tener el checkout de Oracle a mano y a invocar scripts individuales en lugar del comando unificado `oracle relaciones` y `oracle test`. Se actualizó a los comandos `oracle` correspondientes y se sincronizó la prosa explicativa.

2. **Resolución de proyectos en `oracle test` vs paquetes instalados**:
   Al ejecutar `oracle test` o `oracle revisar` desde un worktree de desarrollo donde `oracle.json` declara `"catalogo_base": true`, si el comando `oracle` en el PATH proviene de una instalación previa en `site-packages` distinta del árbol local, `nucleo/proyecto.py` detecta que la raíz no es `RAIZ_ORACLE` del paquete y carga el catálogo base del paquete más el del worktree actual, generando duplicación de IDs de catálogo (`meta.*`). Para invocaciones dentro del propio repositorio de Oracle en desarrollo, el `sys.path` de `tools/cli.py` resuelve la raíz del repositorio local de forma unívoca.

---

## Salidas reales de las nueve verificaciones de DOCTRINA.md

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 605 tests in 12.542s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 605 tests · 547/547 mutantes de medida · **2413 sitios de mutación de código** (2208 + 205 del motor Python).
  escala: **5721 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,4 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5721 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 3. `python tools/corpus.py`
```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 4. `python tools/aceptacion.py`
```
  ROJO  108-donde-compone-un-campo-por-vez     meta.donde_compone  (valor 3)
  ROJO  109-unir-conmuta-un-campo-por-vez      meta.unir_conmuta  (valor 3)
  ROJO  110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez meta.agrupar_sin_claves_es_el_resumen_global  (valor 2)
  ROJO  111-una-macro-equivale-a-su-expansion-un-campo-por-vez meta.una_macro_equivale_a_su_expansion  (valor 3)
  ROJO  120-sintaxis-no-vuelve-igual           meta.sintaxis_ida_y_vuelta  (valor 1)
  verde 121-sintaxis-vuelve-exacta             meta.sintaxis_ida_y_vuelta  (valor 0)
  ROJO  122-sintaxis-revienta-al-leer          meta.sintaxis_ida_y_vuelta  (valor 1)
  ROJO  123-sintaxis-un-campo-por-vez          meta.sintaxis_ida_y_vuelta  (valor 3)
  ROJO  124-sintaxis-cubre-algebra-no-vuelve-igual meta.sintaxis_cubre_algebra  (valor 1)
  verde 125-sintaxis-cubre-algebra-vuelve-exacta meta.sintaxis_cubre_algebra  (valor 0)
  ROJO  126-sintaxis-cubre-algebra-un-campo-por-vez meta.sintaxis_cubre_algebra  (valor 4)
  ROJO  127-sintaxis-casos-no-vuelve-igual     meta.sintaxis_casos_ida_y_vuelta  (valor 1)
  verde 128-sintaxis-casos-vuelve-exacta       meta.sintaxis_casos_ida_y_vuelta  (valor 0)
  ROJO  129-sintaxis-casos-generados-no-vuelve-igual meta.sintaxis_casos_cubre_casos  (valor 1)
  verde 130-sintaxis-casos-generados-vuelve-exacta meta.sintaxis_casos_cubre_casos  (valor 0)
  ROJO  131-sintaxis-casos-un-campo-por-vez    meta.sintaxis_casos_ida_y_vuelta  (valor 4)
  ROJO  132-sintaxis-casos-generados-un-campo-por-vez meta.sintaxis_casos_cubre_casos  (valor 4)
  ROJO  400-umbral-flotante-de-igualdad        meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  ROJO  401-umbral-flotante-de-desigualdad     meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  verde 402-umbral-flotante-de-orden-y-entero  meta.ningun_umbral_flotante_de_igualdad  (valor 0)
  ROJO  403-umbral-sin-defensa                 meta.ningun_umbral_sin_defensa  (valor 1)
  verde 404-umbral-con-defensa                 meta.ningun_umbral_sin_defensa  (valor 0)
  ROJO  405-medida-sin-alcance                 meta.ninguna_medida_sin_alcance  (valor 1)
  verde 406-medida-con-alcance                 meta.ninguna_medida_sin_alcance  (valor 0)
  ROJO  001-verde-acumulativo                  proceso.afirmacion_declara_alcance  (valor 3)
  ROJO  002-mutante-firma-por-id               proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  003-mutante-fondo-nunca-ejercitado     proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  005-mutante-yaw-sin-franja             proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  006-arnes-bytecode-viejo               proceso.arnes_con_bytecode_frio  (valor 1)
  ROJO  007-relevo-verde-arbol-sucio           proceso.verificacion_vigente  (valor 2)
  ROJO  008-vault-falso-rojo                   proceso.verificador_sin_falsos_rojos  (valor 2)
  ROJO  009-modulo-sin-consumidor              proceso.modulo_con_consumidor  (valor 3)
  ROJO  010-sed-desindenta                     proceso.sintaxis_valida_tras_edicion_masiva  (valor 1)
  ROJO  013-comparadores-del-algebra-sin-ejercitar proceso.test_con_mutante_que_lo_mata  (valor 6)
  ROJO  014-mutador-dejo-un-archivo-mutado-al-ser-matado proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  015-racimo-inalcanzable                proceso.modulo_alcanzable  (valor 12)
  ROJO  016-timeout-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  017-error-de-arnes-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  018-mutante-de-cache-borro-la-copia-del-proyecto proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  019-ronda-sin-mutantes-declarada-verde proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  020-una-afirmacion-sin-alcance-alcanza proceso.afirmacion_declara_alcance  (valor 1)
  ROJO  021-un-cambio-vivo-invalida-la-verificacion proceso.verificacion_vigente  (valor 1)
  ROJO  022-un-falso-rojo-ya-rompe-el-verificador proceso.verificador_sin_falsos_rojos  (valor 1)
  ROJO  023-un-import-ajeno-no-es-consumidor   proceso.modulo_con_consumidor  (valor 1)
  ROJO  024-una-variante-no-vacia-inalcanzable proceso.modulo_alcanzable  (valor 1)
  ROJO  025-mutante-de-codigo-sobreviviente    proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  027-ronda-de-codigo-sin-mutantes-no-concluye proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  ROJO  043-ausencia-total-sale-verde          proceso.modulo_con_consumidor  (valor 0)
  ROJO  044-sin-grafo-de-alcance-sale-verde    proceso.modulo_alcanzable  (valor 0)
  verde 058-rechazo-del-algebra-no-es-deteccion proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 059-clave-declarada-en-un-caso         proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 101-mutantes-todos-muertos             proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 102-verificacion-vigente               proceso.verificacion_vigente  (valor 0)
  verde 103-vault-sin-falsos-rojos             proceso.verificador_sin_falsos_rojos  (valor 0)
  verde 104-afirmacion-con-alcance             proceso.afirmacion_declara_alcance  (valor 0)
  verde 105-arnes-con-cache-frio               proceso.arnes_con_bytecode_frio  (valor 0)
  verde 106-modulos-con-consumidor             proceso.modulo_con_consumidor  (valor 0)
  verde 107-reruteo-sin-romper-sintaxis        proceso.sintaxis_valida_tras_edicion_masiva  (valor 0)
  verde 108-ronda-mutacion-concluyente         proceso.ronda_mutacion_concluyente  (valor 0)
  verde 109-mutantes-de-codigo-todos-muertos   proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  verde 110-mutante-de-codigo-equivalente-declarado-verde proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  verde 116-todo-el-nucleo-es-alcanzable       proceso.modulo_alcanzable  (valor 0)
  ROJO  200-corrida-sin-ninguna-corrida        simulacion.corrida_reproducible  (valor 0)
  ROJO  201-presupuesto-sin-ninguna-corrida    simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  202-traza-sin-ningun-evento            simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  301-simulador-que-ignora-la-semilla    simulacion.corrida_reproducible  (valor 2)
  verde 302-corridas-reproducibles             simulacion.corrida_reproducible  (valor 0)
  ROJO  303-el-presupuesto-no-alcanzo          simulacion.no_se_agoto_el_presupuesto  (valor 3)
  verde 304-el-presupuesto-alcanzo             simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  305-traza-con-hueco                    simulacion.la_traza_no_tiene_huecos  (valor 2)
  verde 306-traza-completa                     simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  307-una-corrida-no-reproducible-alcanza simulacion.corrida_reproducible  (valor 1)
  ROJO  308-una-corrida-agota-el-presupuesto   simulacion.no_se_agoto_el_presupuesto  (valor 1)
  ROJO  309-una-traza-con-un-hueco             simulacion.la_traza_no_tiene_huecos  (valor 1)

defectos que se pusieron rojos: 67 · verdes correctos: 34 · huecos declarados: 0
  resuelto       004-testigos-duplicados
  resuelto       012-umbral-duplicado-en-filtro-y-umbral
  limite_humano  011-conclusion-errada-desvan

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ningun_umbral_sin_defensa                      0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)

ACEPTACIÓN ✓ — 67 defectos en rojo, 34 verdes correctos, 0 huecos declarados sin tapar
```

### 5. `python tools/diferencial.py`
```
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### 6. `python tools/trazar.py`
```
evaluaciones trazadas: 92
hechos: 182 pasos · 339 nodos lógicos · 11 productos

el álgebra, juzgada por medidas escritas en el álgebra:
  ✓ meta.agrupar_no_agranda_la_relacion                 0 (<= 0)
  ✓ meta.donde_nunca_agrega_filas                       0 (<= 0)
  ✓ meta.los_logicos_evaluan_todos_sus_operandos        0 (<= 0)
  ✓ meta.unir_materializa_el_producto                   0 (<= 0)

contrastado con la implementación independiente: 4 propiedades, 0 desacuerdos

  · meta.agrupar_no_agranda_la_relacion: compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción
  · meta.donde_nunca_agrega_filas: compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción
  · meta.los_logicos_evaluan_todos_sus_operandos: cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción
  · meta.unir_materializa_el_producto: compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción
```

### 7. `python tools/metamorficas.py`
```
equivalencias comprobadas: 331
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_casos_cubre_casos                     5 (5 construidas, 0 del catálogo)
  sintaxis_casos_ida_y_vuelta                  104 (0 construidas, 104 del catálogo)
  sintaxis_cubre_algebra                        94 (94 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         37 (0 construidas, 37 del catálogo)
  una_macro_equivale_a_su_expansion             69 (0 construidas, 69 del catálogo)
  unir_conmuta                                  16 (1 construidas, 15 del catálogo)

juzgado por las medidas aplicables:
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_casos_cubre_casos                     0 (<= 0)
  ✓ meta.sintaxis_casos_ida_y_vuelta                    0 (<= 0)
  ✓ meta.sintaxis_cubre_algebra                         0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

### 8. `python tools/sintaxis.py --verificar`
```
medidas convertidas: 37
macros convertidas: 3
casos convertidos: 104
ida JSON: OK
vuelta texto: OK
caracteres: JSON 142369 · superficie 139406
puntuación: JSON 25487 (17,9%) · superficie 10489 (7,5%)
bloques de documentación: 21 verificados · 8 declarados como gramática o fragmento
```

### 9. `python tools/mutar.py`
```
mutantes de medida (medida × mutador): 547 · murieron 547 · sobrevivieron 0
  de los muertos: 422 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 125 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1924

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.codigo_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'estado'], 'pasaron'] en `2.2.1.1`
```
