/**
 * Cat-straints CSP Engine
 * Handles Constraint Satisfaction, Backtracking search, Hill Climbing (Min-Conflicts),
 * Conflict detection, and real-time laser vector generation.
 */

class CSPEngine {
  constructor(N = 8) {
    this.N = N;
  }

  setN(newN) {
    this.N = parseInt(newN, 10);
  }

  /**
   * Evaluates conflicts for an arbitrary list of placed cats [{row, col}, ...]
   */
  evaluatePlacements(placements) {
    const conflictPairs = [];
    const conflictingCells = new Set();
    const len = placements.length;

    for (let i = 0; i < len; i++) {
      for (let j = i + 1; j < len; j++) {
        const c1 = placements[i];
        const c2 = placements[j];

        const sameRow = c1.row === c2.row;
        const sameCol = c1.col === c2.col;
        const sameDiag = Math.abs(c1.row - c2.row) === Math.abs(c1.col - c2.col);

        if (sameRow || sameCol || sameDiag) {
          let type = 'diag';
          if (sameRow) type = 'row';
          else if (sameCol) type = 'col';

          conflictPairs.push({
            p1: { row: c1.row, col: c1.col },
            p2: { row: c2.row, col: c2.col },
            type
          });

          conflictingCells.add(`${c1.row},${c1.col}`);
          conflictingCells.add(`${c2.row},${c2.col}`);
        }
      }
    }

    const isSolved = placements.length === this.N && conflictPairs.length === 0;

    return {
      conflictPairs,
      conflictingCells,
      totalConflicts: conflictPairs.length,
      isSolved,
      catsPlaced: placements.length,
      targetCats: this.N
    };
  }

  /**
   * Fast check if a placement (row, col) is safe given already placed queens in rows 0..row-1
   * Used in systematic backtracking search.
   */
  isSafe(board, row, col) {
    for (let r = 0; r < row; r++) {
      const c = board[r];
      if (c === col || Math.abs(r - row) === Math.abs(c - col)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Generator for step-by-step backtracking animation.
   * Yields state objects for interactive visualizer.
   */
  *backtrackingGenerator() {
    const N = this.N;
    const board = new Array(N).fill(-1);
    const stats = {
      nodesExplored: 0,
      backtracks: 0,
      currentDepth: 0,
      maxDepthReached: 0
    };

    function* solveRow(row) {
      if (row === N) {
        yield {
          type: 'solution',
          board: [...board],
          row: N - 1,
          col: board[N - 1],
          stats: { ...stats }
        };
        return true;
      }

      for (let col = 0; col < N; col++) {
        stats.nodesExplored++;
        stats.currentDepth = row;
        if (row > stats.maxDepthReached) stats.maxDepthReached = row;

        board[row] = col;

        // Check if current position conflicts with previous rows
        let safe = true;
        let conflictWith = -1;
        for (let r = 0; r < row; r++) {
          const c = board[r];
          if (c === col || Math.abs(r - row) === Math.abs(c - col)) {
            safe = false;
            conflictWith = r;
            break;
          }
        }

        if (safe) {
          yield {
            type: 'place_valid',
            board: [...board],
            row,
            col,
            stats: { ...stats }
          };

          const solved = yield* solveRow(row + 1);
          if (solved) return true;
        } else {
          yield {
            type: 'conflict_try',
            board: [...board],
            row,
            col,
            conflictRow: conflictWith,
            conflictCol: board[conflictWith],
            stats: { ...stats }
          };
        }

        // Backtrack
        stats.backtracks++;
        board[row] = -1;
        yield {
          type: 'backtrack',
          board: [...board],
          row,
          col,
          stats: { ...stats }
        };
      }

      return false;
    }

    const solved = yield* solveRow(0);
    yield {
      type: solved ? 'done_success' : 'done_impossible',
      board: [...board],
      stats: { ...stats }
    };
  }

  /**
   * Synchronous quick solver to get a solution or hint instantly
   */
  getInstantSolution() {
    const N = this.N;
    const board = new Array(N).fill(-1);

    const solve = (row) => {
      if (row === N) return true;
      // Shuffle columns for non-deterministic fun hints
      const cols = Array.from({ length: N }, (_, i) => i).sort(() => Math.random() - 0.5);
      for (const col of cols) {
        if (this.isSafe(board, row, col)) {
          board[row] = col;
          if (solve(row + 1)) return true;
          board[row] = -1;
        }
      }
      return false;
    };

    if (solve(0)) {
      return board.map((col, row) => ({ row, col }));
    }
    return null;
  }

  /**
   * Calculate heuristic h(n) = number of attacking pairs on a board where each row has 1 cat
   */
  calculateBoardConflicts(board) {
    let conflicts = 0;
    const N = board.length;
    for (let i = 0; i < N; i++) {
      if (board[i] === -1) continue;
      for (let j = i + 1; j < N; j++) {
        if (board[j] === -1) continue;
        if (board[i] === board[j] || Math.abs(i - j) === Math.abs(board[i] - board[j])) {
          conflicts++;
        }
      }
    }
    return conflicts;
  }

  /**
   * Count conflicts if row has queen at column col
   */
  countConflictsForSquare(board, row, col) {
    let count = 0;
    const N = board.length;
    for (let r = 0; r < N; r++) {
      if (r === row || board[r] === -1) continue;
      const c = board[r];
      if (c === col || Math.abs(r - row) === Math.abs(c - col)) {
        count++;
      }
    }
    return count;
  }

  /**
   * Generator for Hill Climbing / Min-Conflicts search.
   * Yields step-by-step local search progression, showing heuristic landscape, plateaus, and restarts.
   */
  *hillClimbingGenerator(maxSteps = 600, maxRestarts = 20) {
    const N = this.N;
    let stats = {
      steps: 0,
      restarts: 0,
      evaluations: 0,
      conflicts: 0
    };

    for (let restart = 0; restart < maxRestarts; restart++) {
      stats.restarts = restart;

      // Random initial configuration (1 queen per row)
      const board = Array.from({ length: N }, () => Math.floor(Math.random() * N));
      let currentConflicts = this.calculateBoardConflicts(board);
      stats.conflicts = currentConflicts;

      yield {
        type: restart === 0 ? 'hc_init' : 'hc_restart',
        board: [...board],
        conflicts: currentConflicts,
        stats: { ...stats }
      };

      if (currentConflicts === 0) {
        yield {
          type: 'hc_success',
          board: [...board],
          conflicts: 0,
          stats: { ...stats }
        };
        return;
      }

      let consecutiveNoImprovement = 0;

      for (let step = 0; step < maxSteps; step++) {
        stats.steps++;
        stats.conflicts = currentConflicts;

        // Find all rows that have conflicts
        const conflictingRows = [];
        for (let r = 0; r < N; r++) {
          if (this.countConflictsForSquare(board, r, board[r]) > 0) {
            conflictingRows.push(r);
          }
        }

        if (conflictingRows.length === 0) {
          // Solved!
          yield {
            type: 'hc_success',
            board: [...board],
            conflicts: 0,
            stats: { ...stats }
          };
          return;
        }

        // Pick a random conflicted variable (row)
        const chosenRow = conflictingRows[Math.floor(Math.random() * conflictingRows.length)];
        const oldCol = board[chosenRow];

        // Evaluate min-conflicts for all columns in this row
        let minConflictVal = Infinity;
        let bestCols = [];
        const conflictMap = [];

        for (let col = 0; col < N; col++) {
          stats.evaluations++;
          const conf = this.countConflictsForSquare(board, chosenRow, col);
          conflictMap.push(conf);

          if (conf < minConflictVal) {
            minConflictVal = conf;
            bestCols = [col];
          } else if (conf === minConflictVal) {
            bestCols.push(col);
          }
        }

        // Pick a best column (breaking ties randomly)
        const newCol = bestCols[Math.floor(Math.random() * bestCols.length)];
        const previousCol = board[chosenRow];
        board[chosenRow] = newCol;

        const newConflicts = this.calculateBoardConflicts(board);

        if (newConflicts >= currentConflicts) {
          consecutiveNoImprovement++;
        } else {
          consecutiveNoImprovement = 0;
        }
        currentConflicts = newConflicts;

        yield {
          type: 'hc_move',
          board: [...board],
          chosenRow,
          oldCol: previousCol,
          newCol,
          conflictMap,
          conflicts: currentConflicts,
          stats: { ...stats }
        };

        if (currentConflicts === 0) {
          yield {
            type: 'hc_success',
            board: [...board],
            conflicts: 0,
            stats: { ...stats }
          };
          return;
        }

        // If trapped in a local minimum/plateau for too long, trigger restart
        if (consecutiveNoImprovement > N * 2) {
          yield {
            type: 'hc_local_minima',
            board: [...board],
            conflicts: currentConflicts,
            stats: { ...stats }
          };
          break; // break out of steps loop and do next restart
        }
      }
    }

    yield {
      type: 'hc_fail',
      conflicts: stats.conflicts,
      stats: { ...stats }
    };
  }

  /**
   * Run a competitive benchmark race between Backtracking and Hill Climbing
   */
  runBenchmark() {
    const N = this.N;

    // 1. Benchmark Backtracking
    const t0 = performance.now();
    let btExplored = 0;
    let btBacktracks = 0;
    const btBoard = new Array(N).fill(-1);

    const btSolve = (r) => {
      if (r === N) return true;
      for (let c = 0; c < N; c++) {
        btExplored++;
        if (this.isSafe(btBoard, r, c)) {
          btBoard[r] = c;
          if (btSolve(r + 1)) return true;
          btBoard[r] = -1;
          btBacktracks++;
        }
      }
      return false;
    };

    const btSuccess = btSolve(0);
    const btTime = Math.max(0.01, performance.now() - t0);

    // 2. Benchmark Hill Climbing (Min-Conflicts with random restarts)
    const t1 = performance.now();
    let hcSteps = 0;
    let hcRestarts = 0;
    let hcSolved = false;
    let hcFinalBoard = [];

    for (let restart = 0; restart < 40; restart++) {
      hcRestarts = restart;
      const board = Array.from({ length: N }, () => Math.floor(Math.random() * N));
      let conflicts = this.calculateBoardConflicts(board);
      if (conflicts === 0) {
        hcSolved = true;
        hcFinalBoard = board;
        break;
      }

      let stuckCount = 0;
      for (let s = 0; s < 500; s++) {
        hcSteps++;
        const conflictedRows = [];
        for (let r = 0; r < N; r++) {
          if (this.countConflictsForSquare(board, r, board[r]) > 0) conflictedRows.push(r);
        }
        if (conflictedRows.length === 0) {
          hcSolved = true;
          hcFinalBoard = board;
          break;
        }

        const r = conflictedRows[Math.floor(Math.random() * conflictedRows.length)];
        let minC = Infinity;
        let candidates = [];
        for (let c = 0; c < N; c++) {
          const val = this.countConflictsForSquare(board, r, c);
          if (val < minC) {
            minC = val;
            candidates = [c];
          } else if (val === minC) {
            candidates.push(c);
          }
        }
        const nextC = candidates[Math.floor(Math.random() * candidates.length)];
        const prevC = board[r];
        board[r] = nextC;
        const newConflicts = this.calculateBoardConflicts(board);
        if (newConflicts >= conflicts) stuckCount++;
        else stuckCount = 0;
        conflicts = newConflicts;

        if (conflicts === 0) {
          hcSolved = true;
          hcFinalBoard = board;
          break;
        }
        if (stuckCount > N * 2) break;
      }
      if (hcSolved) break;
    }

    const hcTime = Math.max(0.01, performance.now() - t1);

    return {
      N,
      backtracking: {
        success: btSuccess,
        nodesExplored: btExplored,
        backtracks: btBacktracks,
        timeMs: btTime.toFixed(2),
        solution: btBoard
      },
      hillClimbing: {
        success: hcSolved,
        steps: hcSteps,
        restarts: hcRestarts,
        timeMs: hcTime.toFixed(2),
        solution: hcFinalBoard
      }
    };
  }
}

if (typeof window !== 'undefined') {
  window.CSPEngine = CSPEngine;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CSPEngine;
}
