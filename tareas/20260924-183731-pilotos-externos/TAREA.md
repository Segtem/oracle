# Oracle no tiene ningún usuario que no sea su autor, y nadie midió cuánto tarda alguien de afuera en llegar a un rojo real

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, validacion


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.2: los consumidores son Jam, LyraGASP y commander, todos del autor. El único experimento de
afuera, la batalla naval hecha por agy, terminó en un verde que no medía nada.

## Qué hacer

1. Un protocolo de piloto: a quién, en qué dominio (al menos uno que no sea de juegos), qué se le da,
   qué se mide (el tiempo hasta la primera medida roja real, dónde se trabó, qué entendió mal) y cómo
   se registra sin guiarlo.
2. Dos o tres pilotos. Cada traba es una tarea.

**Quién:** agy (el borrador del protocolo); Brian (conseguir a las personas).

## Avance

- 2026-09-24:
  - Se analizó el contexto del encargo en [TAREA.md](TAREA.md), la auditoría (§2.2 y §2.3 en [tareas/20260924-174258-auditoria/AUDITORIA.md](../../tareas/20260924-174258-auditoria/AUDITORIA.md)), el postmortem del experimento previo de batalla naval ([vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md)) junto a sus salidas ([vault-kb/postmortems/naval-pm/oracle-resultados.txt](../../vault-kb/postmortems/naval-pm/oracle-resultados.txt)), y la ruta canónica de primer valor ([docs/13-primer-valor.md](../../docs/13-primer-valor.md)).
  - Se redactó el borrador completo del protocolo en [PROTOCOLO.md](PROTOCOLO.md) dentro de la carpeta de la tarea, documentando cada afirmación con `archivo:línea`.
  - El protocolo detalla:
    1. Diagnóstico de fallas previas: ausencia de sensor/medidas de dominio, confusión entre `oracle test` y certificación del producto, distracción en el ritual documental de tareas y pérdida histórica de logs.
    2. Población y roles: participantes externos ajenos al autor de Oracle; Brian a cargo del reclutamiento (punto 1 y asignación en TAREA.md).
    3. Dominios de prueba: 3 opciones ajenas a juegos (facturación/ventas, servicio de usuarios/auth, configuración de infraestructura/devops) para garantizar al menos un dominio no recreativo.
    4. Material provisto: acceso al CLI, producto ejecutable y enlace único a `docs/13-primer-valor.md`, excluyendo explícitamente tutoriales extensos y el tracker documental.
    5. Métricas observables: definición rigurosa del primer rojo real (`oracle juzgar` exit 1 con testigo infractor sobre hechos L0 del producto vivo vs falsos verdes o rojos estáticos de mutación/corpus), marcas temporales ($T_0$, $T_{\text{sensor}}$, $T_{\text{medida}}$, $T_{\text{corpus}}$, $T_{\text{rojo}}$), y categorización de trabas y confusiones semánticas.
    6. Observación sin guiar: principio estricto de no-intervención del observador, respuestas estandarizadas, tiempo límite de 90 minutos y preservación íntegra de grabaciones/transcripts y workspaces.
    7. Derivación de hallazgos: procedimiento para que cada traba detectada se registre como una tarea individual en Oracle.
  - *Nota de verificación*: No se ejecutaron comandos en shell ni se realizaron commits, en estricto cumplimiento de la instrucción recibida.

## Próximo paso

Brian: revisar el borrador en [PROTOCOLO.md](PROTOCOLO.md) y conseguir a las personas (o preparar los agentes/operadores externos) para llevar adelante los 2 o 3 pilotos en los dominios no lúdicos propuestos; luego coordinar la ejecución del primer piloto bajo el protocolo de observación no guiada.

