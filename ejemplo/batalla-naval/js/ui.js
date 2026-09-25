/**
 * ui.js - Interfaz de Usuario y Controlador de Eventos de Batalla Naval
 */

document.addEventListener('DOMContentLoaded', () => {
  const trace = new TraceRecorder();
  const game = new NavalGame(trace);

  // Elementos DOM
  const playerGridEl = document.getElementById('playerGrid');
  const enemyGridEl = document.getElementById('enemyGrid');
  const statusIndicator = document.getElementById('statusIndicator');
  const statusTitle = document.getElementById('statusTitle');
  const statusSubtitle = document.getElementById('statusSubtitle');
  const metricTurns = document.getElementById('metricTurns');
  const metricHits = document.getElementById('metricHits');
  const metricAccuracy = document.getElementById('metricAccuracy');
  const combatLog = document.getElementById('combatLog');

  // Herramientas de colocación
  const placementTools = document.getElementById('placementTools');
  const shipsDock = document.getElementById('shipsDock');
  const btnRotate = document.getElementById('btnRotate');
  const btnAutoPlace = document.getElementById('btnAutoPlace');
  const btnClearPlacement = document.getElementById('btnClearPlacement');
  const btnStartBattle = document.getElementById('btnStartBattle');
  const orientationBadge = document.getElementById('orientationBadge');

  // Rastreador de barcos
  const playerRoster = document.getElementById('playerRoster');
  const cpuRoster = document.getElementById('cpuRoster');

  // Modales
  const auditModal = document.getElementById('auditModal');
  const gameOverModal = document.getElementById('gameOverModal');
  const btnOpenAudit = document.getElementById('btnOpenAudit');
  const btnCloseAudit = document.getElementById('btnCloseAudit');
  const btnCloseGameOver = document.getElementById('btnCloseGameOver');
  const btnDownloadJson = document.getElementById('btnDownloadJson');
  const btnCopyJson = document.getElementById('btnCopyJson');
  const btnNewGame = document.getElementById('btnNewGame');
  const btnRestart = document.getElementById('btnRestart');
  const btnToggleSound = document.getElementById('btnToggleSound');
  const btnVerifyFromGameOver = document.getElementById('btnVerifyFromGameOver');

  // Tabs del modal de auditoría
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const rulesListEl = document.getElementById('rulesList');
  const jsonViewerEl = document.getElementById('jsonViewer');

  // Estado local de UI para fase de colocación
  let currentPlacementOrientation = 'horizontal'; // 'horizontal' | 'vertical'
  let selectedShipConfig = null;
  let playerPlacedShips = [];

  const ROW_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];

  // Inicializar
  initGame();

  function initGame() {
    game.newGame();
    playerPlacedShips = [];
    selectedShipConfig = SHIPS_CONFIG[0];
    currentPlacementOrientation = 'horizontal';

    renderEmptyGrid(playerGridEl, 'player');
    renderEmptyGrid(enemyGridEl, 'enemy');
    renderDock();
    renderRosters();
    updateHUD();
    updateStatus('Fase de Despliegue', 'Ubicá tus 5 buques en el tablero o pulsá "Auto-Desplegar"', 'waiting');
    clearCombatLog();
    addLogEntry('Sistema listo. Desplegá tu flota de combate para iniciar las operaciones.', 'sunk-event');

    placementTools.style.display = 'flex';
    btnStartBattle.disabled = true;
  }

  // Renderizar Grilla con etiquetas A-J y 1-10
  function renderEmptyGrid(tableEl, type) {
    tableEl.innerHTML = '';

    // Fila de encabezado numérico (1-10)
    const headerRow = document.createElement('tr');
    const cornerCell = document.createElement('th');
    cornerCell.className = 'grid-label';
    headerRow.appendChild(cornerCell);

    for (let c = 1; c <= GRID_SIZE; c++) {
      const th = document.createElement('th');
      th.className = 'grid-label';
      th.textContent = c;
      headerRow.appendChild(th);
    }
    tableEl.appendChild(headerRow);

    // Filas A-J con casillas
    for (let r = 0; r < GRID_SIZE; r++) {
      const tr = document.createElement('tr');
      const rowLabel = document.createElement('th');
      rowLabel.className = 'grid-label-row';
      rowLabel.textContent = ROW_LABELS[r];
      tr.appendChild(rowLabel);

      for (let c = 0; c < GRID_SIZE; c++) {
        const td = document.createElement('td');
        td.className = 'grid-cell';
        td.dataset.row = r;
        td.dataset.col = c;
        td.dataset.grid = type;

        if (type === 'player') {
          td.addEventListener('mouseenter', handlePlayerCellHover);
          td.addEventListener('mouseleave', handlePlayerCellLeave);
          td.addEventListener('click', handlePlayerCellClick);
        } else {
          td.addEventListener('click', handleEnemyCellClick);
        }

        tr.appendChild(td);
      }
      tableEl.appendChild(tr);
    }
  }

  // Renderizar el Dock de selección de barcos para colocar
  function renderDock() {
    shipsDock.innerHTML = '';
    const placedIds = playerPlacedShips.map(s => s.id);

    SHIPS_CONFIG.forEach(cfg => {
      const isPlaced = placedIds.includes(cfg.id);
      const isSelected = selectedShipConfig && selectedShipConfig.id === cfg.id;

      const item = document.createElement('div');
      item.className = `ship-dock-item ${isPlaced ? 'placed' : ''} ${isSelected ? 'selected' : ''}`;
      item.dataset.shipId = cfg.id;

      const nameRow = document.createElement('div');
      nameRow.className = 'ship-dock-name';
      nameRow.innerHTML = `${cfg.name} <span>${cfg.length}</span>`;
      item.appendChild(nameRow);

      const blocks = document.createElement('div');
      blocks.className = 'ship-preview-blocks';
      for (let i = 0; i < cfg.length; i++) {
        const b = document.createElement('div');
        b.className = 'preview-block';
        blocks.appendChild(b);
      }
      item.appendChild(blocks);

      if (!isPlaced) {
        item.addEventListener('click', () => {
          selectedShipConfig = cfg;
          renderDock();
        });
      }

      shipsDock.appendChild(item);
    });

    orientationBadge.textContent = currentPlacementOrientation === 'horizontal' ? 'HORIZONTAL' : 'VERTICAL';
  }

  // Manejo de eventos de colocación en el tablero propio
  function handlePlayerCellHover(e) {
    if (game.phase !== 'placement' || !selectedShipConfig) return;
    const row = parseInt(e.target.dataset.row, 10);
    const col = parseInt(e.target.dataset.col, 10);

    clearPlacementHover();
    const canPlace = game.playerBoard.canPlaceShip(
      selectedShipConfig.id,
      selectedShipConfig.length,
      row,
      col,
      currentPlacementOrientation
    );

    for (let i = 0; i < selectedShipConfig.length; i++) {
      const r = currentPlacementOrientation === 'horizontal' ? row : row + i;
      const c = currentPlacementOrientation === 'horizontal' ? col + i : col;
      if (r < GRID_SIZE && c < GRID_SIZE) {
        const cell = playerGridEl.querySelector(`[data-row="${r}"][data-col="${c}"]`);
        if (cell) {
          cell.classList.add(canPlace ? 'placement-valid' : 'placement-invalid');
        }
      }
    }
  }

  function handlePlayerCellLeave() {
    clearPlacementHover();
  }

  function clearPlacementHover() {
    playerGridEl.querySelectorAll('.placement-valid, .placement-invalid').forEach(el => {
      el.classList.remove('placement-valid', 'placement-invalid');
    });
  }

  function handlePlayerCellClick(e) {
    if (game.phase !== 'placement' || !selectedShipConfig) return;
    const row = parseInt(e.target.dataset.row, 10);
    const col = parseInt(e.target.dataset.col, 10);

    if (game.playerBoard.canPlaceShip(selectedShipConfig.id, selectedShipConfig.length, row, col, currentPlacementOrientation)) {
      const ship = new Ship(selectedShipConfig);
      ship.place(row, col, currentPlacementOrientation);
      game.playerBoard.placeShip(ship);
      playerPlacedShips.push(ship);

      window.soundFX.playSonarPing();
      renderPlayerShips();

      // Seleccionar siguiente barco no colocado
      const placedIds = playerPlacedShips.map(s => s.id);
      selectedShipConfig = SHIPS_CONFIG.find(c => !placedIds.includes(c.id)) || null;
      renderDock();

      if (playerPlacedShips.length === SHIPS_CONFIG.length) {
        btnStartBattle.disabled = false;
        updateStatus('Flota Completa', 'Pulsá "Iniciar Batalla" para trabar combate.', 'waiting');
      }
    } else {
      window.soundFX.playMiss();
    }
  }

  function renderPlayerShips() {
    // Limpiar celdas previas de barco
    playerGridEl.querySelectorAll('.grid-cell').forEach(c => c.classList.remove('ship-present'));
    for (const ship of game.playerBoard.ships) {
      for (const coord of ship.coordinates) {
        const cell = playerGridEl.querySelector(`[data-row="${coord.row}"][data-col="${coord.col}"]`);
        if (cell) cell.classList.add('ship-present');
      }
    }
  }

  // Rotar orientación
  btnRotate.addEventListener('click', toggleOrientation);
  window.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
      toggleOrientation();
    }
  });

  function toggleOrientation() {
    currentPlacementOrientation = currentPlacementOrientation === 'horizontal' ? 'vertical' : 'horizontal';
    orientationBadge.textContent = currentPlacementOrientation === 'horizontal' ? 'HORIZONTAL' : 'VERTICAL';
    window.soundFX.playSonarPing();
  }

  // Auto-despliegue
  btnAutoPlace.addEventListener('click', () => {
    game.playerBoard.autoPlaceFleet();
    playerPlacedShips = [...game.playerBoard.ships];
    selectedShipConfig = null;
    renderPlayerShips();
    renderDock();
    btnStartBattle.disabled = false;
    window.soundFX.playSonarPing();
    updateStatus('Flota Desplegada Automáticamente', 'Todos los buques en posición. Pulsá "Iniciar Batalla"', 'waiting');
  });

  // Limpiar colocación
  btnClearPlacement.addEventListener('click', () => {
    game.playerBoard.reset();
    playerPlacedShips = [];
    selectedShipConfig = SHIPS_CONFIG[0];
    renderPlayerShips();
    renderDock();
    btnStartBattle.disabled = true;
    updateStatus('Tablero Limpio', 'Seleccioná un barco y colocalo en la cuadrícula.', 'waiting');
  });

  // Iniciar Batalla
  btnStartBattle.addEventListener('click', () => {
    try {
      game.startBattle();
      placementTools.style.display = 'none';
      document.querySelector('.enemy-card').classList.add('active-target');
      window.soundFX.playSonarPing();
      updateStatus('¡Combate Iniciado!', 'Tu turno: hacé clic en las coordenadas del radar enemigo.', 'player');
      addLogEntry('¡Bafles abiertos! Batalla iniciada. Fuego a discreción.', 'sunk-event');
      updateHUD();
      renderRosters();
    } catch (err) {
      alert(err.message);
    }
  });

  // Disparo del Jugador
  function handleEnemyCellClick(e) {
    if (game.phase !== 'battle') return;
    if (game.currentTurn !== 'jugador') return;

    const row = parseInt(e.target.dataset.row, 10);
    const col = parseInt(e.target.dataset.col, 10);
    const cellEl = e.target;

    if (cellEl.classList.contains('shot')) return;

    window.soundFX.playShot();
    const result = game.firePlayerShot(row, col);
    if (!result.valid) return;

    // Pintar celda
    cellEl.classList.add('shot');
    const coordName = `${ROW_LABELS[row]}${col + 1}`;

    if (result.hit) {
      cellEl.classList.add('hit');
      if (result.sunk) {
        window.soundFX.playSunk();
        markShipAsSunkOnGrid(enemyGridEl, result.ship);
        addLogEntry(`[T-${game.turnNumber - 1}] ¡HUNDIDO! Has destruido el ${result.ship.name} enemigo en ${coordName}!`, 'sunk-event');
      } else {
        window.soundFX.playHit();
        addLogEntry(`[T-${game.turnNumber - 1}] Jugador disparó a ${coordName}: ¡IMPACTO!`, 'player-shot');
      }
    } else {
      cellEl.classList.add('miss');
      window.soundFX.playMiss();
      addLogEntry(`[T-${game.turnNumber - 1}] Jugador disparó a ${coordName}: Agua.`, 'player-shot');
    }

    updateHUD();
    renderRosters();

    if (result.gameOver) {
      handleGameOver(result.winner);
      return;
    }

    // Turno de la CPU
    updateStatus('Turno Enemigo', 'El comandante enemigo está calculando vector de ataque...', 'cpu');
    setTimeout(() => {
      runCpuTurn();
    }, 650);
  }

  // Turno de la CPU
  function runCpuTurn() {
    if (game.phase !== 'battle' || game.currentTurn !== 'cpu') return;

    window.soundFX.playShot();
    const cpuResult = game.executeCpuTurn();
    if (!cpuResult) return;

    const { row, col } = cpuResult.coords;
    const playerCell = playerGridEl.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    const coordName = `${ROW_LABELS[row]}${col + 1}`;

    playerCell.classList.add('shot');

    if (cpuResult.hit) {
      playerCell.classList.add('hit');
      if (cpuResult.sunk) {
        window.soundFX.playSunk();
        markShipAsSunkOnGrid(playerGridEl, cpuResult.ship);
        addLogEntry(`[T-${game.turnNumber - 1}] ¡ALERTA! El enemigo hundió nuestro ${cpuResult.ship.name}!`, 'sunk-event');
      } else {
        window.soundFX.playHit();
        addLogEntry(`[T-${game.turnNumber - 1}] CPU disparó a ${coordName}: ¡Impacto en nuestro casco!`, 'cpu-shot');
      }
    } else {
      playerCell.classList.add('miss');
      window.soundFX.playMiss();
      addLogEntry(`[T-${game.turnNumber - 1}] CPU disparó a ${coordName}: Agua.`, 'cpu-shot');
    }

    updateHUD();
    renderRosters();

    if (cpuResult.gameOver) {
      handleGameOver(cpuResult.winner);
      return;
    }

    updateStatus('Tu Turno', 'Elegí una coordenada en el radar enemigo para abrir fuego.', 'player');
  }

  function markShipAsSunkOnGrid(gridEl, ship) {
    for (const coord of ship.coordinates) {
      const cell = gridEl.querySelector(`[data-row="${coord.row}"][data-col="${coord.col}"]`);
      if (cell) cell.classList.add('sunk');
    }
  }

  // Fin de Juego
  function handleGameOver(winner) {
    const isPlayerWin = winner === 'jugador';
    if (isPlayerWin) {
      window.soundFX.playVictory();
      updateStatus('¡VICTORIA NAVAL!', 'Toda la flota enemiga ha sido destruida.', 'player');
      addLogEntry('¡VICTORIA TOTAL! Todos los barcos hostiles han sido enviados al fondo del mar.', 'sunk-event');
    } else {
      window.soundFX.playDefeat();
      updateStatus('DERROTA NAVAL', 'Nuestra flota ha sido completamente aniquilada.', 'cpu');
      addLogEntry('DERROTA: Hemos perdido todos nuestros navíos. Fin de las operaciones.', 'sunk-event');
    }

    document.getElementById('gameOverTitle').textContent = isPlayerWin ? '¡VICTORIA NAVAL!' : 'FLOTA HUNDIDA';
    document.getElementById('gameOverTitle').className = `gameover-title ${isPlayerWin ? 'win' : 'loss'}`;
    document.getElementById('goTurns').textContent = game.turnNumber;
    document.getElementById('goAccuracy').textContent = `${calcAccuracy(game.stats.playerHits, game.stats.playerShots)}%`;
    document.getElementById('goWinner').textContent = isPlayerWin ? 'JUGADOR' : 'CPU';

    gameOverModal.classList.add('open');
  }

  // HUD y Métricas
  function updateHUD() {
    metricTurns.textContent = game.turnNumber;
    metricHits.textContent = `${game.stats.playerHits} / 17`;
    metricAccuracy.textContent = `${calcAccuracy(game.stats.playerHits, game.stats.playerShots)}%`;
  }

  function calcAccuracy(hits, shots) {
    if (!shots || shots === 0) return 0;
    return Math.round((hits / shots) * 100);
  }

  function updateStatus(title, sub, type) {
    statusTitle.textContent = title;
    statusSubtitle.textContent = sub;
    statusIndicator.className = 'status-indicator';
    if (type === 'waiting') statusIndicator.classList.add('waiting');
    else if (type === 'cpu') statusIndicator.classList.add('cpu');
  }

  // Rosters de buques
  function renderRosters() {
    renderRosterList(playerRoster, game.playerBoard.ships, 'jugador');
    renderRosterList(cpuRoster, game.cpuBoard.ships, 'cpu');
  }

  function renderRosterList(container, ships, owner) {
    container.innerHTML = '';
    const configToDisplay = SHIPS_CONFIG;

    configToDisplay.forEach(cfg => {
      const ship = ships.find(s => s.id === cfg.id);
      const isSunk = ship ? ship.isSunk() : false;
      const hits = ship ? ship.hits : 0;

      const item = document.createElement('div');
      item.className = `roster-item ${isSunk ? 'sunk' : ''}`;

      const nameSpan = document.createElement('span');
      nameSpan.textContent = cfg.name;
      item.appendChild(nameSpan);

      const blocks = document.createElement('div');
      blocks.className = 'roster-blocks';
      for (let i = 0; i < cfg.length; i++) {
        const b = document.createElement('div');
        b.className = `roster-block ${i < hits ? 'hit' : ''}`;
        blocks.appendChild(b);
      }
      item.appendChild(blocks);
      container.appendChild(item);
    });
  }

  // Bitácora de combate
  function clearCombatLog() {
    combatLog.innerHTML = '';
  }

  function addLogEntry(msg, type = '') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = msg;
    combatLog.appendChild(entry);
    combatLog.scrollTop = combatLog.scrollHeight;
  }

  // Modal de Auditoría y Verificación
  btnOpenAudit.addEventListener('click', openAuditModal);
  btnCloseAudit.addEventListener('click', () => auditModal.classList.remove('open'));
  btnVerifyFromGameOver.addEventListener('click', () => {
    gameOverModal.classList.remove('open');
    openAuditModal();
  });

  function openAuditModal() {
    renderAuditData();
    auditModal.classList.add('open');
  }

  function renderAuditData() {
    // 1. Evaluar las 11 medidas formalmente
    const rules = trace.evaluateRules();
    rulesListEl.innerHTML = '';

    rules.forEach(r => {
      const item = document.createElement('div');
      item.className = `rule-item ${r.passed ? 'passed' : 'failed'}`;

      const header = document.createElement('div');
      header.className = 'rule-header';

      const left = document.createElement('div');
      left.innerHTML = `<div class="rule-title">${r.name}</div><div class="rule-id">${r.id}</div>`;

      const badge = document.createElement('div');
      badge.className = `rule-status ${r.passed ? 'green' : 'red'}`;
      badge.textContent = r.passed ? 'VERDE ✓' : `ROJO ✗ (${r.value})`;

      header.appendChild(left);
      header.appendChild(badge);
      item.appendChild(header);

      const desc = document.createElement('div');
      desc.className = 'rule-desc';
      desc.textContent = r.reason;
      item.appendChild(desc);

      if (!r.passed && r.witnesses.length > 0) {
        const witnessEl = document.createElement('div');
        witnessEl.style.fontSize = '0.72rem';
        witnessEl.style.color = '#ff6b8b';
        witnessEl.style.fontFamily = 'monospace';
        witnessEl.textContent = `Testigo del defecto: ${JSON.stringify(r.witnesses[0])}`;
        item.appendChild(witnessEl);
      }

      rulesListEl.appendChild(item);
    });

    // 2. Traza JSON
    jsonViewerEl.textContent = trace.toJSON(2);
  }

  // Tabs
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add('active');
    });
  });

  // Descarga y Copia de JSON
  btnDownloadJson.addEventListener('click', () => {
    trace.downloadJSON('hechos_partida.json');
  });

  btnCopyJson.addEventListener('click', () => {
    navigator.clipboard.writeText(trace.toJSON(2)).then(() => {
      btnCopyJson.textContent = '¡Copiado!';
      setTimeout(() => { btnCopyJson.textContent = 'Copiar JSON'; }, 2000);
    });
  });

  // Reiniciar / Nueva Partida
  btnNewGame.addEventListener('click', () => {
    if (confirm('¿Reiniciar y comenzar una nueva partida?')) {
      initGame();
    }
  });

  btnRestart.addEventListener('click', () => {
    gameOverModal.classList.remove('open');
    initGame();
  });

  btnCloseGameOver.addEventListener('click', () => {
    gameOverModal.classList.remove('open');
  });

  // Mute Sonido
  btnToggleSound.addEventListener('click', () => {
    const isEnabled = window.soundFX.toggleSound();
    btnToggleSound.textContent = isEnabled ? '🔊 Sonido' : '🔇 Mute';
  });
});
