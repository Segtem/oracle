/**
 * engine.js - Lógica pura del juego de Batalla Naval
 * Diseñado para ejecutarse tanto en el navegador como en Node.js para testing y auditoría formal.
 */

const GRID_SIZE = 10;

const SHIPS_CONFIG = [
  { id: 'portaaviones', name: 'Portaaviones', length: 5 },
  { id: 'acorazado', name: 'Acorazado', length: 4 },
  { id: 'crucero', name: 'Crucero', length: 3 },
  { id: 'submarino', name: 'Submarino', length: 3 },
  { id: 'destructor', name: 'Destructor', length: 2 }
];

const TOTAL_FLEET_CELLS = SHIPS_CONFIG.reduce((acc, s) => acc + s.length, 0); // 17

class Ship {
  constructor(config) {
    this.id = config.id;
    this.name = config.name;
    this.length = config.length;
    this.row = null;
    this.col = null;
    this.orientation = 'horizontal'; // 'horizontal' | 'vertical'
    this.coordinates = [];
    this.hits = 0;
  }

  place(row, col, orientation) {
    this.row = row;
    this.col = col;
    this.orientation = orientation;
    this.coordinates = [];
    for (let i = 0; i < this.length; i++) {
      if (orientation === 'horizontal') {
        this.coordinates.push({ row: row, col: col + i });
      } else {
        this.coordinates.push({ row: row + i, col: col });
      }
    }
  }

  isSunk() {
    return this.hits >= this.length;
  }
}

class Board {
  constructor(owner) {
    this.owner = owner; // 'jugador' | 'cpu'
    this.grid = Array.from({ length: GRID_SIZE }, () =>
      Array.from({ length: GRID_SIZE }, () => ({
        ship: null,
        shot: false,
        hit: false
      }))
    );
    this.ships = [];
  }

  reset() {
    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        this.grid[r][c] = { ship: null, shot: false, hit: false };
      }
    }
    this.ships = [];
  }

  canPlaceShip(shipId, length, row, col, orientation) {
    for (let i = 0; i < length; i++) {
      const r = orientation === 'horizontal' ? row : row + i;
      const c = orientation === 'horizontal' ? col + i : col;

      // Fuera de límites
      if (r < 0 || r >= GRID_SIZE || c < 0 || c >= GRID_SIZE) {
        return false;
      }
      // Solapamiento
      if (this.grid[r][c].ship !== null) {
        return false;
      }
    }
    return true;
  }

  placeShip(ship) {
    if (!this.canPlaceShip(ship.id, ship.length, ship.row, ship.col, ship.orientation)) {
      throw new Error(`Posición inválida para ${ship.name} en (${ship.row}, ${ship.col})`);
    }

    for (const coord of ship.coordinates) {
      this.grid[coord.row][coord.col].ship = ship;
    }
    this.ships.push(ship);
    return true;
  }

  receiveShot(row, col) {
    if (row < 0 || row >= GRID_SIZE || col < 0 || col >= GRID_SIZE) {
      throw new Error(`Coordenadas de disparo (${row}, ${col}) fuera de rango`);
    }

    const cell = this.grid[row][col];
    if (cell.shot) {
      return { alreadyShot: true, hit: false, sunk: false, ship: null };
    }

    cell.shot = true;
    if (cell.ship !== null) {
      cell.hit = true;
      cell.ship.hits += 1;
      const sunk = cell.ship.isSunk();
      return {
        alreadyShot: false,
        hit: true,
        sunk: sunk,
        ship: cell.ship
      };
    } else {
      return {
        alreadyShot: false,
        hit: false,
        sunk: false,
        ship: null
      };
    }
  }

  isAllSunk() {
    return this.ships.length === SHIPS_CONFIG.length && this.ships.every(s => s.isSunk());
  }

  totalHitsReceived() {
    return this.ships.reduce((acc, s) => acc + s.hits, 0);
  }

  autoPlaceFleet() {
    this.reset();
    for (const cfg of SHIPS_CONFIG) {
      const ship = new Ship(cfg);
      let placed = false;
      let attempts = 0;
      while (!placed && attempts < 500) {
        attempts++;
        const orientation = Math.random() < 0.5 ? 'horizontal' : 'vertical';
        const maxR = orientation === 'horizontal' ? GRID_SIZE : GRID_SIZE - ship.length;
        const maxC = orientation === 'horizontal' ? GRID_SIZE - ship.length : GRID_SIZE;
        const r = Math.floor(Math.random() * maxR);
        const c = Math.floor(Math.random() * maxC);

        if (this.canPlaceShip(ship.id, ship.length, r, c, orientation)) {
          ship.place(r, c, orientation);
          this.placeShip(ship);
          placed = true;
        }
      }
      if (!placed) {
        throw new Error(`No se pudo colocar automáticamente el barco ${ship.name}`);
      }
    }
  }
}

/**
 * Inteligencia Artificial para el CPU
 * Estrategia de Caza y Blanco (Hunt and Target) con paridad matemática.
 */
class NavalAI {
  constructor() {
    this.reset();
  }

  reset() {
    this.targetQueue = []; // Cola de celdas adyacentes a impactos no hundidos
    this.currentShipHits = []; // Coordenadas de impactos del barco actual bajo ataque
  }

  getNextShot(opponentBoard) {
    // 1. Modo Blanco: si tenemos celdas candidatas prioritarias en la cola
    while (this.targetQueue.length > 0) {
      const candidate = this.targetQueue.shift();
      if (!opponentBoard.grid[candidate.row][candidate.col].shot) {
        return candidate;
      }
    }

    // 2. Modo Caza: búsqueda probabilística con paridad (celdas de tablero de ajedrez)
    // Ya que el barco más chico mide 2 casillas, alcanza con disparar a (r + c) % 2 === 0
    const parityCandidates = [];
    const otherCandidates = [];

    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        if (!opponentBoard.grid[r][c].shot) {
          if ((r + c) % 2 === 0) {
            parityCandidates.push({ row: r, col: c });
          } else {
            otherCandidates.push({ row: r, col: c });
          }
        }
      }
    }

    const pool = parityCandidates.length > 0 ? parityCandidates : otherCandidates;
    const chosenIndex = Math.floor(Math.random() * pool.length);
    return pool[chosenIndex];
  }

  recordShotResult(row, col, hit, sunk) {
    if (hit) {
      this.currentShipHits.push({ row, col });

      if (sunk) {
        // Barco destruido: limpiar objetivos del barco y volver a cazar
        this.currentShipHits = [];
        this.targetQueue = [];
      } else {
        // Agregar vecinos ortogonales válidos
        const neighbors = [
          { row: row - 1, col: col },
          { row: row + 1, col: col },
          { row: row, col: col - 1 },
          { row: row, col: col + 1 }
        ].filter(p => p.row >= 0 && p.row < GRID_SIZE && p.col >= 0 && p.col < GRID_SIZE);

        if (this.currentShipHits.length >= 2) {
          // Ya sabemos si el barco es horizontal o vertical
          const isHorizontal = this.currentShipHits[0].row === this.currentShipHits[1].row;
          const alignedNeighbors = neighbors.filter(n =>
            isHorizontal ? n.row === this.currentShipHits[0].row : n.col === this.currentShipHits[0].col
          );
          // Poner los alineados al frente de la cola
          this.targetQueue.unshift(...alignedNeighbors);
        } else {
          this.targetQueue.push(...neighbors);
        }
      }
    }
  }
}

/**
 * Gestor de la partida (GameManager)
 */
class NavalGame {
  constructor(traceRecorder) {
    this.trace = traceRecorder;
    this.playerBoard = new Board('jugador');
    this.cpuBoard = new Board('cpu');
    this.ai = new NavalAI();
    this.phase = 'placement'; // 'placement' | 'battle' | 'game_over'
    this.currentTurn = 'jugador';
    this.turnNumber = 0;
    this.winner = null;
    this.stats = {
      playerShots: 0,
      playerHits: 0,
      cpuShots: 0,
      cpuHits: 0
    };
  }

  newGame() {
    this.trace.reset();
    this.playerBoard.reset();
    this.cpuBoard.reset();
    this.ai.reset();
    this.phase = 'placement';
    this.currentTurn = 'jugador';
    this.turnNumber = 0;
    this.winner = null;
    this.stats = {
      playerShots: 0,
      playerHits: 0,
      cpuShots: 0,
      cpuHits: 0
    };

    // La CPU siempre coloca su flota automáticamente
    this.cpuBoard.autoPlaceFleet();
    this.trace.recordFleet('cpu', this.cpuBoard.ships);
  }

  startBattle() {
    if (this.playerBoard.ships.length !== SHIPS_CONFIG.length) {
      throw new Error('Debés colocar los 5 barcos antes de iniciar la batalla.');
    }
    this.trace.recordFleet('jugador', this.playerBoard.ships);
    this.phase = 'battle';
    this.currentTurn = 'jugador';
    this.turnNumber = 0;
  }

  firePlayerShot(row, col) {
    if (this.phase !== 'battle') {
      throw new Error('La partida no está en fase de batalla.');
    }
    if (this.currentTurn !== 'jugador') {
      throw new Error('No es el turno del jugador.');
    }

    const shotResult = this.cpuBoard.receiveShot(row, col);
    if (shotResult.alreadyShot) {
      return { valid: false, message: 'Casilla ya atacada previamente.' };
    }

    this.stats.playerShots++;
    if (shotResult.hit) this.stats.playerHits++;

    this.trace.recordShot(
      this.turnNumber,
      'jugador',
      'cpu',
      row,
      col,
      shotResult.hit,
      shotResult.sunk,
      shotResult.sunk ? shotResult.ship.id : 'ninguno'
    );

    this.turnNumber++;

    if (this.cpuBoard.isAllSunk()) {
      this.endGame('jugador');
      return {
        valid: true,
        hit: shotResult.hit,
        sunk: shotResult.sunk,
        ship: shotResult.ship,
        gameOver: true,
        winner: 'jugador'
      };
    }

    // Pasa turno a la CPU
    this.currentTurn = 'cpu';
    return {
      valid: true,
      hit: shotResult.hit,
      sunk: shotResult.sunk,
      ship: shotResult.ship,
      gameOver: false
    };
  }

  executeCpuTurn() {
    if (this.phase !== 'battle' || this.currentTurn !== 'cpu') {
      return null;
    }

    const shotCoords = this.ai.getNextShot(this.playerBoard);
    const shotResult = this.playerBoard.receiveShot(shotCoords.row, shotCoords.col);

    this.stats.cpuShots++;
    if (shotResult.hit) this.stats.cpuHits++;

    this.ai.recordShotResult(shotCoords.row, shotCoords.col, shotResult.hit, shotResult.sunk);

    this.trace.recordShot(
      this.turnNumber,
      'cpu',
      'jugador',
      shotCoords.row,
      shotCoords.col,
      shotResult.hit,
      shotResult.sunk,
      shotResult.sunk ? shotResult.ship.id : 'ninguno'
    );

    this.turnNumber++;

    if (this.playerBoard.isAllSunk()) {
      this.endGame('cpu');
      return {
        coords: shotCoords,
        hit: shotResult.hit,
        sunk: shotResult.sunk,
        ship: shotResult.ship,
        gameOver: true,
        winner: 'cpu'
      };
    }

    this.currentTurn = 'jugador';
    return {
      coords: shotCoords,
      hit: shotResult.hit,
      sunk: shotResult.sunk,
      ship: shotResult.ship,
      gameOver: false
    };
  }

  endGame(winner) {
    this.phase = 'game_over';
    this.winner = winner;
    const loser = winner === 'jugador' ? 'cpu' : 'jugador';
    const hitsWinner = winner === 'jugador' ? this.stats.playerHits : this.stats.cpuHits;
    const hitsLoser = winner === 'jugador' ? this.stats.cpuHits : this.stats.playerHits;

    this.trace.recordGameOver(winner, loser, hitsWinner, hitsLoser);
  }
}

// Exportable para Node y Browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    GRID_SIZE,
    SHIPS_CONFIG,
    TOTAL_FLEET_CELLS,
    Ship,
    Board,
    NavalAI,
    NavalGame
  };
} else {
  window.GRID_SIZE = GRID_SIZE;
  window.SHIPS_CONFIG = SHIPS_CONFIG;
  window.TOTAL_FLEET_CELLS = TOTAL_FLEET_CELLS;
  window.Ship = Ship;
  window.Board = Board;
  window.NavalAI = NavalAI;
  window.NavalGame = NavalGame;
}
