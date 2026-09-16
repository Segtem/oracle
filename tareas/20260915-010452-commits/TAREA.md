# Los commits como hechos del tracker

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: oracle, idea

Como en tatr, cada commit empieza con el ID de su tarea. `oracle tarea hechos --git` debería emitir una relación de commits (sha, asunto, ID nombrado, si la tarea existe y su estado en ese commit) para escribir en el lenguaje reglas como «ningún commit nombra una tarea inexistente» o «toda CERRADA tiene su commit», y juzgarlas en CI con `oracle juzgar`.

El experimento es ver cuáles se pueden definir sin tocar `nucleo/`: ordenar por tiempo dentro de una tarea o clasificar el asunto de un commit quizás no entren, y eso sería un límite medido. Depende de [20260915-010206-juzgar](../20260915-010206-juzgar/TAREA.md).
