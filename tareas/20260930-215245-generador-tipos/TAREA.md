# el generador respeta los tipos declarados en .relacion

- ESTADO: ABIERTA
- PRIORIDAD: 58
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: el encogido de buscar_candidatos conserva el tipo de la semilla, y las reglas ponen textos (_PARES_DE_CAMPOS) donde comparan dos campos; un campo declarado entero en su .relacion puede quedar "". Oracle no valida la evidencia contra los tipos declarados. Qué: cuando la relación está declarada, semillas, vecinos y encogido respetan su tipo (entero/real/texto/bool).
