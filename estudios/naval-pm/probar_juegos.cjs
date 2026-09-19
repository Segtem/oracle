// Arnés de lógica: DOM/audio simulados, temporizadores en cola, IIFE expuesta sólo en memoria.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = process.argv[2] || '/home/workstation/Dev/lab/batalla_naval_test';
function load(name, expose) {
  const nodes = new Map(), timers = [];
  function node(id = '') {
    if (nodes.has(id)) return nodes.get(id);
    const n = {style:{}, dataset:{}, listeners:{}, classList:{add(){},remove(){},toggle(){}},
      addEventListener(k,f){(this.listeners[k] ||= []).push(f)}, appendChild(){},
      querySelector(){return node('cell')}, querySelectorAll(){return []}, innerHTML:'', textContent:''};
    nodes.set(id,n); return n;
  }
  const document = {getElementById:node, createElement:()=>node(Symbol()), querySelectorAll:()=>[], addEventListener(){}};
  let seed = 19;
  const math = Object.create(Math);
  math.random = () => ((seed = (1664525 * seed + 1013904223) >>> 0) / 2**32);
  const ctx = {document, window:{addEventListener(){},soundFX:new Proxy({}, {get:()=>()=>{}})},
    setTimeout:f=>timers.push(f), requestAnimationFrame(){}, Math:math, assert, console};
  vm.createContext(ctx);
  const source = fs.readFileSync(path.join(root, name, 'game.js'), 'utf8');
  assert(source.trimEnd().endsWith('})();'));
  vm.runInContext(source.replace(/\}\)\(\);\s*$/, expose + '\n})();'), ctx);
  return {ctx,nodes,timers,run:s=>vm.runInContext(s,ctx)};
}
const con = load('batalla_naval_con_oracle', `
  renderCoordinates=renderGrids=renderDock=renderFleetStatus=updatePlayerBoardUI=updateEnemyBoardUI=logMessage=()=>{};
  globalThis.api={initGame,setupEventListeners,createEmptyBoard,canPlaceShip,placeShip,placeShipsRandomly,
    handleEnemyCellClick,enemyTurn,GAME_STATE,SHIPS_CONFIG,
    get pb(){return playerBoard},get eb(){return enemyBoard},get ps(){return playerShips},get es(){return enemyShips}};
`);
con.run(`
  const a=api; a.initGame();
  for(let i=0;i<100;i++) {
    const b=a.createEmptyBoard(), s=[]; a.placeShipsRandomly(b,s);
    assert.equal(s.length,5); assert.equal(b.flat().filter(c=>c.shipId!==null).length,17);
    assert.deepEqual(s.map(x=>x.coordinates.length),[5,4,3,3,2]);
  }
  let b=a.createEmptyBoard();
  assert(!a.canPlaceShip(b,9,9,2,'H')); assert(!a.canPlaceShip(b,9,9,2,'V'));
  a.placeShip(b,[],a.SHIPS_CONFIG[4],0,0,'H');
  assert(!a.canPlaceShip(b,0,0,2,'V')); assert(a.canPlaceShip(b,1,0,2,'H'));
  a.GAME_STATE.PHASE='PLAYING';
  const first=a.es[0].coordinates[0];
  a.handleEnemyCellClick(first.r,first.c); assert.equal(a.GAME_STATE.currentTurn,'ENEMY');
  const shots=a.GAME_STATE.stats.shots; a.handleEnemyCellClick(9,9); assert.equal(a.GAME_STATE.stats.shots,shots);
  a.GAME_STATE.currentTurn='PLAYER'; a.handleEnemyCellClick(first.r,first.c); assert.equal(a.GAME_STATE.stats.shots,shots);
  assert(!a.es[0].sunk);
  for(const s of a.es) for(const p of s.coordinates) {a.GAME_STATE.currentTurn='PLAYER';a.handleEnemyCellClick(p.r,p.c)}
  assert.equal(a.GAME_STATE.stats.hits,17); assert.equal(a.GAME_STATE.stats.enemySunk,5); assert.equal(a.GAME_STATE.PHASE,'GAME_OVER');
  a.initGame(); a.placeShipsRandomly(a.pb,a.ps); a.GAME_STATE.PHASE='PLAYING';
  for(let i=0;i<100 && a.GAME_STATE.PHASE==='PLAYING';i++) {
    const before=a.pb.flat().filter(c=>c.hit||c.miss).length; a.enemyTurn();
    assert.equal(a.pb.flat().filter(c=>c.hit||c.miss).length,before+1);
  }
  assert.equal(a.GAME_STATE.PHASE,'GAME_OVER');assert.equal(a.GAME_STATE.stats.playerSunk,5);
`);
console.log('CON: 100 flotas de 17 celdas; límites H/V, colisión, adyacencia permitida, bloqueo de turno, repetición, hundimiento, victoria y derrota: OK');
const sin = load('batalla_naval_sin_oracle', `
  renderGrids=renderShipDock=renderFleetStatusHUD=initRadarAnimation=logMessage=()=>{};
  globalThis.api={initGame,resetState,canPlaceShip,getShipCoordinates,placeShipOnGrid,randomizeFleet,
    handleEnemyCellClick,cpuTurn,state,STATES,FLEET_CONFIG};
`);
sin.run(`
 const a=api; a.resetState();
 for(let i=0;i<100;i++) {
   a.resetState(); a.randomizeFleet(a.state.cpuShips,a.state.cpuGrid);
   assert.equal(a.state.cpuGrid.flat().filter(Boolean).length,17);
   assert.deepEqual(a.state.cpuShips.map(s=>s.positions.length),[5,4,3,3,2]);
 }
 a.resetState(); const b=a.state.playerGrid;
 assert(!a.canPlaceShip(b,a.getShipCoordinates(9,9,2,'H')));assert(!a.canPlaceShip(b,a.getShipCoordinates(9,9,2,'V')));
 a.placeShipOnGrid(b,a.state.playerShips[4],a.getShipCoordinates(0,0,2,'H'));
 assert(!a.canPlaceShip(b,a.getShipCoordinates(0,0,2,'V')));assert(a.canPlaceShip(b,a.getShipCoordinates(1,0,2,'H')));
 a.randomizeFleet(a.state.cpuShips,a.state.cpuGrid);
 const click=(r,c)=>a.handleEnemyCellClick({currentTarget:{dataset:{row:r,col:c},classList:{add(){},remove(){}}}});
 a.state.phase='PLAYER_TURN'; const p=a.state.cpuShips[0].positions[0]; click(p.r,p.c);
 assert.equal(a.state.phase,'CPU_TURN');const shots=a.state.playerStats.shots;
 click(9,9);assert.equal(a.state.playerStats.shots,shots);
 a.state.phase='PLAYER_TURN';click(p.r,p.c);assert.equal(a.state.playerStats.shots,shots);assert(!a.state.cpuShips[0].sunk);
 for(const s of a.state.cpuShips)for(const p of s.positions){a.state.phase='PLAYER_TURN';click(p.r,p.c)}
 assert.equal(a.state.playerStats.hits,17);assert(a.state.cpuShips.every(s=>s.sunk));assert.equal(a.state.phase,'GAME_OVER');
 a.resetState();a.randomizeFleet(a.state.playerShips,a.state.playerGrid);
 for(let i=0;i<100 && a.state.phase!=='GAME_OVER';i++){
  a.state.phase='CPU_TURN'; const before=a.state.playerShots.flat().filter(Boolean).length;a.cpuTurn();
  assert.equal(a.state.playerShots.flat().filter(Boolean).length,before+1);
 }
 assert.equal(a.state.phase,'GAME_OVER');assert(a.state.playerShips.every(s=>s.sunk));
 a.initGame();a.initGame();
`);
console.log('SIN: mismos controles de lógica: OK');
const rotations = sin.nodes.get('btn-rotate').listeners.click;
sin.run("api.state.orientation='H'");
rotations.forEach(f=>f());
assert.equal(rotations.length, 2);
assert.equal(sin.ctx.api.state.orientation,'H');
console.log('SIN: defecto reproducido tras 2 initGame: 2 listeners de rotación; un clic rota dos veces y queda H.');
// Un callback viejo del enemigo puede entrar en una partida nueva en la variante CON.
con.run("api.initGame();api.placeShipsRandomly(api.pb,api.ps);api.GAME_STATE.PHASE='PLAYING';api.GAME_STATE.currentTurn='PLAYER'");
con.timers[0]();
assert.equal(con.ctx.api.pb.flat().filter(c=>c.hit||c.miss).length,1);
console.log('CON: callback enemigo pendiente de partida anterior dispara en nueva partida durante turno PLAYER.');
