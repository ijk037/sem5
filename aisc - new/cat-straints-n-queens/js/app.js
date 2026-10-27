/**
 * Cat-straints Main Application Controller
 */

class CatstraintsApp {
  constructor() {
    this.csp = new CSPEngine(8);
    this.placements = []; // Array of {row, col}
    this.mode = 'manual'; // 'manual' | 'backtracking' | 'hillclimbing'
    this.activeTab = 'play'; // 'play' | 'compare'

    // Visualizer state
    this.animInterval = null;
    this.isPlaying = false;
    this.speed = 180; // ms per step
    this.btGenerator = null;
    this.hcGenerator = null;
    this.history = [];
    this.historyIndex = -1;

    // Showdown comparison state
    this.showdownRunning = false;
    this.showdownInterval = null;

    // DOM Elements
    this.boardEl = null;
    this.laserCanvas = null;
    this.laserCtx = null;

    // Bind event handlers
    window.addEventListener('DOMContentLoaded', () => this.init());
  }

  init() {
    this.boardEl = document.getElementById('chessboard');
    this.laserCanvas = document.getElementById('laserCanvas');
    if (this.laserCanvas) {
      this.laserCtx = this.laserCanvas.getContext('2d');
    }

    // Init fireworks
    const fireworksCanvas = document.getElementById('fireworksCanvas');
    if (fireworksCanvas) {
      window.fireworks.init(fireworksCanvas);
    }

    this.bindEvents();
    this.renderBoard();
    this.updateStats();

    // Auto resize listener for lasers
    window.addEventListener('resize', () => {
      this.drawLasers();
      if (this.activeTab === 'compare') {
        this.drawShowdownLasers();
      }
    });
  }

  bindEvents() {
    // Tab switching
    document.querySelectorAll('[data-tab-target]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.currentTarget.getAttribute('data-tab-target');
        this.switchTab(target);
      });
    });

    // Board Size Slider
    const sizeSlider = document.getElementById('boardSizeSlider');
    const sizeVal = document.getElementById('boardSizeVal');
    if (sizeSlider) {
      sizeSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        if (sizeVal) sizeVal.textContent = `${val} × ${val}`;
        this.setBoardSize(val);
      });
    }

    // Quick size buttons (4, 6, 8, 10, 12)
    document.querySelectorAll('[data-quick-size]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const sz = parseInt(e.currentTarget.getAttribute('data-quick-size'), 10);
        if (sizeSlider) sizeSlider.value = sz;
        if (sizeVal) sizeVal.textContent = `${sz} × ${sz}`;
        this.setBoardSize(sz);
      });
    });

    // Solver Mode Selector Buttons
    document.querySelectorAll('[data-mode-btn]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const m = e.currentTarget.getAttribute('data-mode-btn');
        this.setMode(m);
      });
    });

    // Play / Pause / Step Controls
    const playPauseBtn = document.getElementById('btnPlayPause');
    if (playPauseBtn) {
      playPauseBtn.addEventListener('click', () => this.togglePlayPause());
    }

    const stepForwardBtn = document.getElementById('btnStepForward');
    if (stepForwardBtn) {
      stepForwardBtn.addEventListener('click', () => this.stepForward());
    }

    const stepBackwardBtn = document.getElementById('btnStepBackward');
    if (stepBackwardBtn) {
      stepBackwardBtn.addEventListener('click', () => this.stepBackward());
    }

    const resetBtn = document.getElementById('btnReset');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => this.resetSolver());
    }

    // Speed Slider
    const speedSlider = document.getElementById('animSpeedSlider');
    if (speedSlider) {
      speedSlider.addEventListener('input', (e) => {
        // Slider value 1 (slow) to 100 (fast) -> 500ms down to 10ms
        const val = parseInt(e.target.value, 10);
        this.speed = Math.max(10, Math.round(520 - (val * 5)));
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    }

    // Action buttons: Clear, Randomize, Hint, Instant Solve
    const clearBtn = document.getElementById('btnClear');
    if (clearBtn) clearBtn.addEventListener('click', () => this.clearBoard());

    const randomBtn = document.getElementById('btnRandomize');
    if (randomBtn) randomBtn.addEventListener('click', () => this.randomizeBoard());

    const hintBtn = document.getElementById('btnHint');
    if (hintBtn) hintBtn.addEventListener('click', () => this.giveHint());

    const autoSolveBtn = document.getElementById('btnAutoSolve');
    if (autoSolveBtn) autoSolveBtn.addEventListener('click', () => this.instantSolve());

    const launchFireworksBtn = document.getElementById('btnLaunchFireworks');
    if (launchFireworksBtn) {
      launchFireworksBtn.addEventListener('click', () => {
        window.fireworks.launch(3500);
        window.cuteAudio.playVictory();
      });
    }

    // Sound Toggle Button
    const soundBtn = document.getElementById('btnToggleSound');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        const muted = window.cuteAudio.toggleMute();
        soundBtn.innerHTML = muted ? '🔇 Sound: Off' : '🔊 Sound: On';
        soundBtn.classList.toggle('opacity-60', muted);
      });
    }

    // Benchmark Run Button
    const runBenchBtn = document.getElementById('btnRunBenchmark');
    if (runBenchBtn) {
      runBenchBtn.addEventListener('click', () => this.runShowdownRace());
    }

    // Victory Modal close
    const victoryCloseBtn = document.getElementById('btnVictoryClose');
    if (victoryCloseBtn) {
      victoryCloseBtn.addEventListener('click', () => {
        document.getElementById('victoryModal').classList.add('hidden');
      });
    }

    const victoryNextBtn = document.getElementById('btnVictoryNext');
    if (victoryNextBtn) {
      victoryNextBtn.addEventListener('click', () => {
        document.getElementById('victoryModal').classList.add('hidden');
        if (this.csp.N < 12) {
          const nextN = this.csp.N + 1;
          const sl = document.getElementById('boardSizeSlider');
          if (sl) sl.value = nextN;
          const sv = document.getElementById('boardSizeVal');
          if (sv) sv.textContent = `${nextN} × ${nextN}`;
          this.setBoardSize(nextN);
        } else {
          this.clearBoard();
        }
      });
    }
  }

  switchTab(tabId) {
    this.activeTab = tabId;
    this.pause();

    // Toggle nav pills
    document.querySelectorAll('[data-tab-target]').forEach(btn => {
      const match = btn.getAttribute('data-tab-target') === tabId;
      btn.classList.toggle('cute-tab-active', match);
      btn.classList.toggle('bg-white', !match);
      btn.classList.toggle('text-pink-600', !match);
    });

    // Toggle tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.add('hidden');
    });

    const activePanel = document.getElementById(`tab-${tabId}`);
    if (activePanel) activePanel.classList.remove('hidden');

    if (tabId === 'compare') {
      this.initShowdownBoards();
    } else if (tabId === 'play') {
      setTimeout(() => {
        this.renderBoard();
        this.drawLasers();
      }, 50);
    }
  }

  setBoardSize(n) {
    this.pause();
    this.csp.setN(n);
    this.placements = [];
    this.history = [];
    this.historyIndex = -1;
    this.btGenerator = null;
    this.hcGenerator = null;
    this.renderBoard();
    this.updateStats();
    window.cuteAudio.playPlop();
  }

  setMode(mode) {
    this.pause();
    this.mode = mode;

    // Update mode pill buttons
    document.querySelectorAll('[data-mode-btn]').forEach(btn => {
      const isCurrent = btn.getAttribute('data-mode-btn') === mode;
      btn.classList.toggle('cute-tab-active', isCurrent);
      btn.classList.toggle('bg-pink-50', !isCurrent);
      btn.classList.toggle('text-pink-700', !isCurrent);
    });

    // Update solver control panel visibility
    const controlsPanel = document.getElementById('animControls');
    const manualInstructions = document.getElementById('manualInstructions');
    const visualizerHelp = document.getElementById('visualizerHelp');

    if (mode === 'manual') {
      if (controlsPanel) controlsPanel.classList.add('hidden');
      if (manualInstructions) manualInstructions.classList.remove('hidden');
      if (visualizerHelp) visualizerHelp.classList.add('hidden');
    } else {
      if (controlsPanel) controlsPanel.classList.remove('hidden');
      if (manualInstructions) manualInstructions.classList.add('hidden');
      if (visualizerHelp) visualizerHelp.classList.remove('hidden');
      this.resetSolver();
      this.play();
    }

    this.renderBoard();
    this.updateStats();
  }

  renderBoard() {
    if (!this.boardEl) return;
    const N = this.csp.N;

    // Setup CSS Grid
    this.boardEl.style.gridTemplateColumns = `repeat(${N}, minmax(0, 1fr))`;
    this.boardEl.innerHTML = '';

    // Evaluate placements for conflicts
    const evalResult = this.csp.evaluatePlacements(this.placements);
    const conflictSet = evalResult.conflictingCells;

    // Create a 2D map for quick lookup
    const catMap = new Map();
    this.placements.forEach(p => catMap.set(`${p.row},${p.col}`, p));

    // Render N x N squares
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        const tile = document.createElement('div');
        const isDark = (r + c) % 2 === 1;
        const cellKey = `${r},${c}`;
        const hasCat = catMap.has(cellKey);
        const isConflicted = conflictSet.has(cellKey);

        tile.className = `board-tile aspect-square rounded-lg flex items-center justify-center relative overflow-hidden transition-all ${
          isDark ? 'dark-tile' : 'light-tile'
        }`;
        tile.dataset.row = r;
        tile.dataset.col = c;

        if (isConflicted) {
          tile.classList.add('is-conflicted');
        }

        // Click handler for manual placement
        tile.addEventListener('click', () => this.handleTileClick(r, c));

        // If cat placed, insert cute SVG
        if (hasCat) {
          const wrapper = document.createElement('div');
          wrapper.className = 'cat-wrapper w-full h-full flex items-center justify-center p-1';

          let state = isConflicted ? 'conflict' : 'happy';
          if (evalResult.isSolved) state = 'crowned';

          // Adapt SVG size to board scale
          const svgSize = Math.max(28, Math.min(68, Math.floor(480 / N)));
          wrapper.innerHTML = window.CuteCats.getCatSvg(r, c, state, svgSize);

          tile.appendChild(wrapper);

          // Add cute conflict badge if conflicted
          if (isConflicted) {
            const badge = document.createElement('span');
            badge.className = 'absolute top-1 right-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-md pointer-events-none badge-bounce';
            badge.textContent = '!';
            tile.appendChild(badge);
          }
        }

        this.boardEl.appendChild(tile);
      }
    }

    // Sync laser canvas size & redraw lasers
    requestAnimationFrame(() => this.drawLasers());
  }

  handleTileClick(r, c) {
    if (this.mode !== 'manual') {
      this.setMode('manual');
    }

    // Check if a cat is already on this square
    const idx = this.placements.findIndex(p => p.row === r && p.col === c);
    if (idx !== -1) {
      // Remove cat
      this.placements.splice(idx, 1);
      window.cuteAudio.playRemove();
    } else {
      // Freeform placement: allow user to place cat anywhere to test conflicts freely
      this.placements.push({ row: r, col: c });
      window.cuteAudio.playPlop();
    }

    this.renderBoard();
    this.updateStats();
    this.checkVictory();
  }

  drawLasers() {
    if (!this.laserCanvas || !this.laserCtx || !this.boardEl) return;

    const wrapper = document.getElementById('boardWrapper') || this.boardEl;
    const w = wrapper.clientWidth;
    const h = wrapper.clientHeight;

    this.laserCanvas.width = w;
    this.laserCanvas.height = h;
    this.laserCtx.clearRect(0, 0, w, h);

    const evalResult = this.csp.evaluatePlacements(this.placements);
    if (evalResult.conflictPairs.length === 0) return;

    // Draw glowing red conflict laser beams between exact tile centers
    this.laserCtx.save();
    evalResult.conflictPairs.forEach(pair => {
      const tile1 = this.boardEl.querySelector(`[data-row="${pair.p1.row}"][data-col="${pair.p1.col}"]`);
      const tile2 = this.boardEl.querySelector(`[data-row="${pair.p2.row}"][data-col="${pair.p2.col}"]`);

      if (!tile1 || !tile2) return;

      const x1 = tile1.offsetLeft + tile1.offsetWidth / 2;
      const y1 = tile1.offsetTop + tile1.offsetHeight / 2;
      const x2 = tile2.offsetLeft + tile2.offsetWidth / 2;
      const y2 = tile2.offsetTop + tile2.offsetHeight / 2;

      // Outer Red Glow
      this.laserCtx.beginPath();
      this.laserCtx.moveTo(x1, y1);
      this.laserCtx.lineTo(x2, y2);
      this.laserCtx.strokeStyle = 'rgba(235, 77, 75, 0.45)';
      this.laserCtx.lineWidth = 8;
      this.laserCtx.lineCap = 'round';
      this.laserCtx.stroke();

      // Middle Vibrant Beam
      this.laserCtx.beginPath();
      this.laserCtx.moveTo(x1, y1);
      this.laserCtx.lineTo(x2, y2);
      this.laserCtx.strokeStyle = 'rgba(255, 71, 87, 0.9)';
      this.laserCtx.lineWidth = 3.5;
      this.laserCtx.lineCap = 'round';
      this.laserCtx.stroke();

      // Hot White Core Laser
      this.laserCtx.beginPath();
      this.laserCtx.moveTo(x1, y1);
      this.laserCtx.lineTo(x2, y2);
      this.laserCtx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
      this.laserCtx.lineWidth = 1.2;
      this.laserCtx.stroke();

      // Warning Sparkles at both ends
      this.drawWarningPuff(x1, y1);
      this.drawWarningPuff(x2, y2);
    });
    this.laserCtx.restore();
  }

  drawWarningPuff(x, y) {
    this.laserCtx.beginPath();
    this.laserCtx.arc(x, y, 6, 0, Math.PI * 2);
    this.laserCtx.fillStyle = 'rgba(255, 71, 87, 0.8)';
    this.laserCtx.fill();
  }

  updateStats(customStats = null) {
    const evalResult = this.csp.evaluatePlacements(this.placements);

    // Update Badges
    const placedEl = document.getElementById('statPlaced');
    if (placedEl) {
      placedEl.textContent = `${this.placements.length} / ${this.csp.N}`;
    }

    const conflictsEl = document.getElementById('statConflicts');
    if (conflictsEl) {
      conflictsEl.textContent = evalResult.totalConflicts;
      conflictsEl.className = evalResult.totalConflicts > 0
        ? 'font-bold text-red-500 animate-pulse'
        : 'font-bold text-emerald-600';
    }

    const statusPill = document.getElementById('boardStatusPill');
    if (statusPill) {
      if (evalResult.isSolved) {
        statusPill.innerHTML = '🎉 Purr-fect Solved!';
        statusPill.className = 'px-3 py-1 bg-emerald-100 text-emerald-800 text-sm font-bold rounded-full shadow-sm';
      } else if (this.placements.length === this.csp.N && evalResult.totalConflicts > 0) {
        statusPill.innerHTML = `⚠️ ${evalResult.totalConflicts} Conflicts!`;
        statusPill.className = 'px-3 py-1 bg-red-100 text-red-700 text-sm font-bold rounded-full shadow-sm';
      } else {
        const remaining = this.csp.N - this.placements.length;
        statusPill.innerHTML = remaining > 0 ? `🐾 Place ${remaining} more kitties` : '🐾 Ready';
        statusPill.className = 'px-3 py-1 bg-pink-100 text-pink-700 text-sm font-medium rounded-full shadow-sm';
      }
    }

    // Visualizer specific stats
    if (customStats) {
      const liveStat1 = document.getElementById('visualizerStat1');
      const liveStat2 = document.getElementById('visualizerStat2');
      if (liveStat1) liveStat1.textContent = customStats.label1 || '-';
      if (liveStat2) liveStat2.textContent = customStats.label2 || '-';
    }
  }

  checkVictory() {
    const evalResult = this.csp.evaluatePlacements(this.placements);
    if (evalResult.isSolved) {
      window.cuteAudio.playVictory();
      window.fireworks.launch(4500);

      const victoryModal = document.getElementById('victoryModal');
      const victoryDesc = document.getElementById('victoryDesc');
      if (victoryDesc) {
        victoryDesc.textContent = `You placed all ${this.csp.N} kitties safely with ZERO conflicts! Every kitty has their cozy personal space! 🐾`;
      }
      if (victoryModal) {
        victoryModal.classList.remove('hidden');
      }
    }
  }

  clearBoard() {
    this.pause();
    this.placements = [];
    this.history = [];
    this.historyIndex = -1;
    this.renderBoard();
    this.updateStats();
    window.cuteAudio.playRemove();
  }

  randomizeBoard() {
    this.pause();
    const N = this.csp.N;
    this.placements = [];
    for (let r = 0; r < N; r++) {
      this.placements.push({ row: r, col: Math.floor(Math.random() * N) });
    }
    this.renderBoard();
    this.updateStats();
    window.cuteAudio.playPlop();
    this.checkVictory();
  }

  giveHint() {
    this.pause();
    const solution = this.csp.getInstantSolution();
    if (!solution) return;

    // If board is empty, place first queen
    if (this.placements.length === 0) {
      this.placements.push(solution[0]);
    } else {
      // Find row not yet placed, or correct a wrong row
      let placedRows = new Set(this.placements.map(p => p.row));
      let missingRow = -1;
      for (let r = 0; r < this.csp.N; r++) {
        if (!placedRows.has(r)) {
          missingRow = r;
          break;
        }
      }

      if (missingRow !== -1) {
        const hintCat = solution.find(p => p.row === missingRow);
        if (hintCat) this.placements.push(hintCat);
      } else {
        // Overwrite full board with solution
        this.placements = [...solution];
      }
    }

    this.renderBoard();
    this.updateStats();
    window.cuteAudio.playPlop();
    this.checkVictory();
  }

  instantSolve() {
    this.pause();
    const solution = this.csp.getInstantSolution();
    if (solution) {
      this.placements = solution;
      this.renderBoard();
      this.updateStats();
      this.checkVictory();
    }
  }

  // --- SOLVER ANIMATION & VISUALIZER ---

  resetSolver() {
    this.pause();
    this.placements = [];
    this.history = [];
    this.historyIndex = -1;

    if (this.mode === 'backtracking') {
      this.btGenerator = this.csp.backtrackingGenerator();
    } else if (this.mode === 'hillclimbing') {
      this.hcGenerator = this.csp.hillClimbingGenerator();
      const firstStep = this.hcGenerator.next().value;
      if (firstStep) {
        this.applyHillClimbingStep(firstStep);
        this.history.push(firstStep);
        this.historyIndex = 0;
      }
    }

    this.renderBoard();
    this.updateStats({
      label1: 'Ready to search',
      label2: 'Nodes: 0'
    });
  }

  togglePlayPause() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    if (this.mode === 'manual') return;
    this.isPlaying = true;
    const playBtn = document.getElementById('btnPlayPause');
    if (playBtn) playBtn.innerHTML = '⏸️ Pause';

    if (this.mode === 'backtracking' && !this.btGenerator) {
      this.resetSolver();
    } else if (this.mode === 'hillclimbing' && !this.hcGenerator) {
      this.resetSolver();
    }

    if (this.animInterval) {
      clearInterval(this.animInterval);
      this.animInterval = null;
    }
    this.animInterval = setInterval(() => {
      const hasMore = this.stepForward();
      if (!hasMore) {
        this.pause();
      }
    }, this.speed);
  }

  pause() {
    this.isPlaying = false;
    if (this.animInterval) {
      clearInterval(this.animInterval);
      this.animInterval = null;
    }
    const playBtn = document.getElementById('btnPlayPause');
    if (playBtn) playBtn.innerHTML = '▶️ Play';
  }

  stepForward() {
    if (this.mode === 'backtracking') {
      if (!this.btGenerator) this.btGenerator = this.csp.backtrackingGenerator();
      const nextVal = this.btGenerator.next();

      if (nextVal.done || !nextVal.value) {
        this.pause();
        return false;
      }

      const step = nextVal.value;
      this.applyBacktrackingStep(step);
      this.history.push(step);
      this.historyIndex = this.history.length - 1;
      return true;
    } else if (this.mode === 'hillclimbing') {
      if (!this.hcGenerator) this.hcGenerator = this.csp.hillClimbingGenerator();
      const nextVal = this.hcGenerator.next();

      if (nextVal.done || !nextVal.value) {
        this.pause();
        return false;
      }

      const step = nextVal.value;
      this.applyHillClimbingStep(step);
      this.history.push(step);
      this.historyIndex = this.history.length - 1;
      return true;
    }
    return false;
  }

  stepBackward() {
    if (this.historyIndex > 0) {
      this.pause();
      this.historyIndex--;
      const step = this.history[this.historyIndex];
      if (this.mode === 'backtracking') {
        this.applyBacktrackingStep(step);
      } else {
        this.applyHillClimbingStep(step);
      }
    }
  }

  applyBacktrackingStep(step) {
    // Map board array to placements
    this.placements = [];
    if (step.board) {
      step.board.forEach((col, r) => {
        if (col !== -1) {
          this.placements.push({ row: r, col });
        }
      });
    }

    this.renderBoard();

    // Sound feedback
    if (step.type === 'place_valid') {
      window.cuteAudio.playStep(true);
    } else if (step.type === 'conflict_try') {
      window.cuteAudio.playStep(false);
    } else if (step.type === 'backtrack') {
      window.cuteAudio.playBacktrack();
    } else if (step.type === 'solution') {
      this.pause();
      this.checkVictory();
    }

    // Update stats bar
    this.updateStats({
      label1: `Explored: ${step.stats.nodesExplored} nodes`,
      label2: `Backtracks: ${step.stats.backtracks}`
    });
  }

  applyHillClimbingStep(step) {
    this.placements = [];
    if (step.board) {
      step.board.forEach((col, r) => {
        if (col !== -1) {
          this.placements.push({ row: r, col });
        }
      });
    }

    this.renderBoard();

    if (step.type === 'hc_move') {
      window.cuteAudio.playStep(true);
    } else if (step.type === 'hc_restart') {
      window.cuteAudio.playBacktrack();
    } else if (step.type === 'hc_success') {
      this.pause();
      this.checkVictory();
    }

    this.updateStats({
      label1: `Steps: ${step.stats.steps} | Restarts: ${step.stats.restarts}`,
      label2: `Conflicts: ${step.conflicts}`
    });
  }

  // --- ALGORITHM SHOWDOWN COMPARISON ---

  initShowdownBoards() {
    this.renderShowdownBoard('boardBacktracking', 8);
    this.renderShowdownBoard('boardHillClimbing', 8);
  }

  renderShowdownBoard(elementId, N, placements = []) {
    const el = document.getElementById(elementId);
    if (!el) return;

    el.style.gridTemplateColumns = `repeat(${N}, minmax(0, 1fr))`;
    el.innerHTML = '';

    const catMap = new Map();
    placements.forEach(p => catMap.set(`${p.row},${p.col}`, p));

    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        const tile = document.createElement('div');
        const isDark = (r + c) % 2 === 1;
        tile.className = `aspect-square rounded flex items-center justify-center relative overflow-hidden ${
          isDark ? 'bg-amber-100' : 'bg-orange-50'
        }`;

        if (catMap.has(`${r},${c}`)) {
          const wrapper = document.createElement('div');
          wrapper.className = 'w-full h-full flex items-center justify-center p-0.5';
          const sz = Math.max(20, Math.min(38, Math.floor(260 / N)));
          wrapper.innerHTML = window.CuteCats.getCatSvg(r, c, 'happy', sz);
          tile.appendChild(wrapper);
        }

        el.appendChild(tile);
      }
    }
  }

  runShowdownRace() {
    const benchResult = this.csp.runBenchmark();

    // Render results in the metric cards
    const btTimeEl = document.getElementById('benchBtTime');
    const btNodesEl = document.getElementById('benchBtNodes');
    const btBacktracksEl = document.getElementById('benchBtBacktracks');

    if (btTimeEl) btTimeEl.textContent = `${benchResult.backtracking.timeMs} ms`;
    if (btNodesEl) btNodesEl.textContent = `${benchResult.backtracking.nodesExplored}`;
    if (btBacktracksEl) btBacktracksEl.textContent = `${benchResult.backtracking.backtracks}`;

    const hcTimeEl = document.getElementById('benchHcTime');
    const hcStepsEl = document.getElementById('benchHcSteps');
    const hcRestartsEl = document.getElementById('benchHcRestarts');

    if (hcTimeEl) hcTimeEl.textContent = `${benchResult.hillClimbing.timeMs} ms`;
    if (hcStepsEl) hcStepsEl.textContent = `${benchResult.hillClimbing.steps}`;
    if (hcRestartsEl) hcRestartsEl.textContent = `${benchResult.hillClimbing.restarts}`;

    // Render final boards
    const btPlacements = benchResult.backtracking.solution.map((col, r) => ({ row: r, col }));
    const hcPlacements = benchResult.hillClimbing.solution.map((col, r) => ({ row: r, col }));

    this.renderShowdownBoard('boardBacktracking', this.csp.N, btPlacements);
    this.renderShowdownBoard('boardHillClimbing', this.csp.N, hcPlacements);

    // Audio cue
    window.cuteAudio.playVictory();
  }
}

// Global App instance
window.catstraintsApp = new CatstraintsApp();
