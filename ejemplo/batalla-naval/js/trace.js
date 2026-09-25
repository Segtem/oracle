/**
 * trace.js - Recolector de evidencia relacional formal y auditor de reglas
 * Emite la traza de la partida en formato de hechos (JSON) compatible con oracle-metalenguaje.
 */

class TraceRecorder {
  constructor() {
    this.reset();
  }

  reset() {
    this.celdaBarco = [];
    this.tiros = [];
    this.partida = [];
    this._nextSegmentId = 0;
  }

  recordFleet(jugador, ships) {
    for (const ship of ships) {
      ship.coordinates.forEach((coord, idx) => {
        this.celdaBarco.push({
          id: this._nextSegmentId++,
          jugador: jugador,
          barco_id: ship.id,
          segmento_idx: idx,
          fila: coord.row,
          columna: coord.col
        });
      });
    }
  }

  recordShot(turno, tirador, receptor, fila, columna, esImpacto, hundioBarco, barcoHundido) {
    this.tiros.push({
      turno: turno,
      tirador: tirador,
      receptor: receptor,
      fila: fila,
      columna: columna,
      es_impacto: Boolean(esImpacto),
      hundio_barco: Boolean(hundioBarco),
      barco_hundido: barcoHundido || 'ninguno'
    });
  }

  recordGameOver(ganador, perdedor, impactosGanador, impactosPerdedor) {
    const finalTurn = this.tiros.length > 0 ? this.tiros[this.tiros.length - 1].turno : 0;
    this.partida = [{
      estado: 'terminada',
      ganador: ganador,
      perdedor: perdedor,
      turno_final: finalTurn,
      total_tiros: this.tiros.length,
      impactos_ganador: impactosGanador,
      impactos_perdedor: impactosPerdedor
    }];
  }

  toFactsObject() {
    return {
      celda_barco: this.celdaBarco,
      tiro: this.tiros,
      partida: this.partida.length > 0 ? this.partida : [{
        estado: 'en_curso',
        ganador: 'ninguno',
        perdedor: 'ninguno',
        turno_final: this.tiros.length > 0 ? this.tiros[this.tiros.length - 1].turno : 0,
        total_tiros: this.tiros.length,
        impactos_ganador: 0,
        impactos_perdedor: 0
      }]
    };
  }

  toJSON(indent = 2) {
    return JSON.stringify(this.toFactsObject(), null, indent);
  }

  downloadJSON(filename = 'hechos_partida.json') {
    const jsonStr = this.toJSON(2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Auditoría espejo de las 11 medidas de Oracle evaluadas directamente en JavaScript.
   * Permite al usuario ver el veredicto formal dentro de la interfaz web además del CLI.
   */
  evaluateRules() {
    const facts = this.toFactsObject();
    const celdas = facts.celda_barco;
    const tiros = facts.tiro;
    const partida = facts.partida[0] || {};

    const results = [];

    // 1. naval.tiros_dentro_del_tablero
    const invalidShots = tiros.filter(t => t.fila < 0 || t.fila > 9 || t.columna < 0 || t.columna > 9);
    results.push({
      id: 'naval.tiros_dentro_del_tablero',
      name: 'Tiros dentro del tablero [0..9]',
      passed: invalidShots.length === 0,
      value: invalidShots.length,
      threshold: '<= 0',
      reason: 'El tablero reglamentario es de 10x10; cualquier disparo fuera de [0, 9] es inválido.',
      witnesses: invalidShots
    });

    // 2. naval.tiros_sin_repeticion
    const dupShots = [];
    for (let i = 0; i < tiros.length; i++) {
      for (let j = i + 1; j < tiros.length; j++) {
        if (tiros[i].tirador === tiros[j].tirador &&
            tiros[i].fila === tiros[j].fila &&
            tiros[i].columna === tiros[j].columna) {
          dupShots.push({ original: tiros[i], duplicado: tiros[j] });
        }
      }
    }
    results.push({
      id: 'naval.tiros_sin_repeticion',
      name: 'Sin disparos duplicados a la misma casilla',
      passed: dupShots.length === 0,
      value: dupShots.length,
      threshold: '<= 0',
      reason: 'Ningún jugador puede disparar dos veces a la misma casilla en una partida.',
      witnesses: dupShots
    });

    // 3. naval.alternancia_turnos
    const nonAlternating = [];
    for (let i = 0; i < tiros.length - 1; i++) {
      if (tiros[i + 1].turno === tiros[i].turno + 1 && tiros[i + 1].tirador === tiros[i].tirador) {
        nonAlternating.push({ turno1: tiros[i], turno2: tiros[i + 1] });
      }
    }
    results.push({
      id: 'naval.alternancia_turnos',
      name: 'Alternancia estricta de turnos',
      passed: nonAlternating.length === 0,
      value: nonAlternating.length,
      threshold: '<= 0',
      reason: 'Los turnos deben alternar estrictamente entre ambos jugadores en turnos consecutivos.',
      witnesses: nonAlternating
    });

    // 4. naval.turnos_sin_huecos
    let turnGaps = 0;
    if (tiros.length > 0) {
      const maxTurn = Math.max(...tiros.map(t => t.turno));
      if (tiros.length !== maxTurn + 1) {
        turnGaps = Math.abs(tiros.length - (maxTurn + 1));
      }
    }
    results.push({
      id: 'naval.turnos_sin_huecos',
      name: 'Turnos continuos sin huecos ni saltos',
      passed: turnGaps === 0,
      value: turnGaps,
      threshold: '<= 0',
      reason: 'La secuencia de turnos debe ser continua, arrancando en 0 y avanzando de a 1.',
      witnesses: turnGaps > 0 ? [{ tirosRegistrados: tiros.length }] : []
    });

    // 5. naval.barcos_dentro_del_tablero
    const invalidCells = celdas.filter(c => c.fila < 0 || c.fila > 9 || c.columna < 0 || c.columna > 9);
    results.push({
      id: 'naval.barcos_dentro_del_tablero',
      name: 'Barcos dentro de la cuadrícula [0..9]',
      passed: invalidCells.length === 0,
      value: invalidCells.length,
      threshold: '<= 0',
      reason: 'Todas las celdas ocupadas por barcos deben ubicarse dentro de 10x10.',
      witnesses: invalidCells
    });

    // 6. naval.barcos_sin_solapamiento
    const overlapping = [];
    for (let i = 0; i < celdas.length; i++) {
      for (let j = i + 1; j < celdas.length; j++) {
        if (celdas[i].jugador === celdas[j].jugador &&
            celdas[i].fila === celdas[j].fila &&
            celdas[i].columna === celdas[j].columna) {
          overlapping.push({ c1: celdas[i], c2: celdas[j] });
        }
      }
    }
    results.push({
      id: 'naval.barcos_sin_solapamiento',
      name: 'Barcos sin solapamiento entre sí',
      passed: overlapping.length === 0,
      value: overlapping.length,
      threshold: '<= 0',
      reason: 'Dos casillas de barco del mismo jugador no pueden coincidir en la misma celda.',
      witnesses: overlapping
    });

    // 7. naval.flota_reglamentaria
    const jugadorCeldas = celdas.filter(c => c.jugador === 'jugador').length;
    const cpuCeldas = celdas.filter(c => c.jugador === 'cpu').length;
    const flotaFlaws = [];
    if (jugadorCeldas !== 17) flotaFlaws.push({ jugador: 'jugador', celdas: jugadorCeldas, esperado: 17 });
    if (cpuCeldas !== 17) flotaFlaws.push({ jugador: 'cpu', celdas: cpuCeldas, esperado: 17 });
    results.push({
      id: 'naval.flota_reglamentaria',
      name: 'Flota reglamentaria de 17 casillas por bando',
      passed: flotaFlaws.length === 0,
      value: flotaFlaws.length,
      threshold: '<= 0',
      reason: 'Cada bando debe tener exactamente 17 casillas (5+4+3+3+2).',
      witnesses: flotaFlaws
    });

    // 8. naval.veracidad_impacto_positivo (Falso impacto / fantasma)
    const ghostHits = [];
    for (const t of tiros) {
      if (t.es_impacto) {
        const match = celdas.find(c => c.jugador === t.receptor && c.fila === t.fila && c.columna === t.columna);
        if (!match) {
          ghostHits.push(t);
        }
      }
    }
    results.push({
      id: 'naval.veracidad_impacto_positivo',
      name: 'Veracidad de impacto: ningún impacto fantasma',
      passed: ghostHits.length === 0,
      value: ghostHits.length,
      threshold: '<= 0',
      reason: 'Un disparo no puede declararse impacto si no había un segmento de barco rival.',
      witnesses: ghostHits
    });

    // 9. naval.veracidad_impacto_negativo (Agua falsa / impacto omitido)
    const falseMisses = [];
    for (const t of tiros) {
      if (!t.es_impacto) {
        const match = celdas.find(c => c.jugador === t.receptor && c.fila === t.fila && c.columna === t.columna);
        if (match) {
          falseMisses.push({ tiro: t, celdaReal: match });
        }
      }
    }
    results.push({
      id: 'naval.veracidad_impacto_negativo',
      name: 'Veracidad de agua: ningún impacto omitido',
      passed: falseMisses.length === 0,
      value: falseMisses.length,
      threshold: '<= 0',
      reason: 'Un disparo en una casilla con barco no puede ser reportado como agua.',
      witnesses: falseMisses
    });

    // 10. naval.fin_de_juego_sin_tiros_posteriores
    const postGameShots = [];
    if (partida.estado === 'terminada') {
      const finalTurn = partida.turno_final;
      for (const t of tiros) {
        if (t.turno > finalTurn) {
          postGameShots.push(t);
        }
      }
    }
    results.push({
      id: 'naval.fin_de_juego_sin_tiros_posteriores',
      name: 'Fin de partida: sin disparos posteriores',
      passed: postGameShots.length === 0,
      value: postGameShots.length,
      threshold: '<= 0',
      reason: 'Una vez finalizada la partida no se permiten más disparos.',
      witnesses: postGameShots
    });

    // 11. naval.ganador_legitimo
    let winnerValid = true;
    const winnerWitnesses = [];
    if (partida.estado === 'terminada') {
      if (partida.impactos_ganador !== 17) {
        winnerValid = false;
        winnerWitnesses.push(partida);
      }
    }
    results.push({
      id: 'naval.ganador_legitimo',
      name: 'Ganador legítimo: exactamente 17 impactos',
      passed: winnerValid,
      value: winnerValid ? 0 : 1,
      threshold: '<= 0',
      reason: 'El ganador debe haber destruido la totalidad de las 17 casillas enemigas.',
      witnesses: winnerWitnesses
    });

    return results;
  }
}

// Exportable para browser y Node
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TraceRecorder };
} else {
  window.TraceRecorder = TraceRecorder;
}
