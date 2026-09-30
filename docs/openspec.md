# OpenSpec y Oracle

OpenSpec escribe lo que el código promete: requisitos con `SHALL` y escenarios con `WHEN`/`THEN`.
No dice si el código lo cumple. `/opsx:verify` se lo pregunta a un agente, que lee el código y
opina. Oracle contesta con una medida que se corre, con el corpus que la fija y con lo que no mide
escrito al lado.

El puente tiene tres pasos: importar las promesas, medirlas una por una y juzgar la evidencia.

## 1. Importar los requisitos

```bash
oracle requisito importar openspec/specs                 # muestra lo que haría
oracle requisito importar openspec/specs --escribir      # escribe requisitos/*.requisito
```

Cada `### Requirement:` de cada `openspec/specs/<capacidad>/spec.md` se vuelve un requisito
`<capacidad>.<nombre>`, con el párrafo `SHALL` como texto y la spec como fuente. `--dominio <d>`
cambia el prefijo. Con un solo `spec.md` en vez del directorio importa esa spec nada más.

```
requisito cli_validate.interactivity_controls:
    texto "The CLI SHALL respect `--no-interactive` to disable prompts. …"
    fuente "openspec/specs/cli-validate/spec.md#Interactivity controls"
    sin_medir "sin medida todavía; escenarios: «Disabling prompts via flags or environment»"
```

Nace **sin medir** a propósito. El importador no sabe qué medida prueba qué, y un enlace inventado
es peor que ninguno: se lee como cubierto. Un requisito que ya existe no se toca nunca, así que
se puede reimportar cada vez que cambia la spec y sólo entra lo nuevo.

## 2. Medir cada escenario

```bash
oracle medida nueva cli_validate.no_interactivo_no_pregunta \
    --escenario-de openspec/specs/cli-validate/spec.md "Disabling prompts via flags or environment" \
    --requisito cli_validate.interactivity_controls
```

Crea la medida con el escenario como comentario, sus casos, y la agrega al `medido_por` del
requisito. Cuando todos los escenarios de un requisito tienen medida, se reescribe su `sin_medir`
con lo que de verdad queda afuera —«que el mensaje sea claro es un juicio»— o se borra.
`oracle cobertura` dice en cualquier momento qué está medido, qué en parte y qué no.

En el experimento con la spec `cli-validate` de OpenSpec, de 31 escenarios 19 fueron medibles
enteros, 9 en parte y 3 eran prosa (`tareas/20260928-210611-openspec/experimento/`).

## 3. Juzgar: el paso de verificación

```bash
oracle cobertura --con hechos.json
```

Juzga la evidencia que emite tu sensor y marca cada requisito: ✓ se cumple, ◐ se cumple en lo
medido (con su `SIN MEDIR`), ✗ no se cumple, ? sin juicio. Sale con 1 si hay un rojo que la sombra
no perdona.

### Dentro de `/opsx:verify`

OpenSpec (1.13) inyecta el `context` y la guía de `operations.apply` de `openspec/config.yaml` en
`openspec instructions apply --json`, que es lo que `/opsx:verify` lee antes de verificar:

```yaml
operations:
  apply:
    guidance:
      - "Antes de dar por verificado un cambio, correr el sensor y `oracle cobertura --con hechos.json`, y copiar su salida en el informe. Un requisito ✗ es un CRITICAL; uno ? o ◐ se informa con su SIN MEDIR."
```

El skill de verify trata esa guía como **consejo**, no como veredicto: el agente puede correrla o
no. Por eso la garantía no está ahí sino en el código de salida, en un lugar donde nadie decide:

```bash
# .githooks/pre-push, o un paso de CI
oracle cambios --desde origin/main || exit 1      # ¿se aflojó alguna medida?
oracle cobertura --con hechos.json || exit 1      # ¿se cumple lo que la spec promete?
```

`oracle cambios` es la otra mitad: el agente que no logra cumplir la spec puede aflojar la medida,
la escalar o el sensor. Eso sale nombrado, y aflojar sin reescribir el `porque` es error.

---

Los textos citados de OpenSpec en esta página son © 2024 OpenSpec Contributors, bajo [licencia MIT](https://github.com/Fission-AI/OpenSpec/blob/main/LICENSE).
