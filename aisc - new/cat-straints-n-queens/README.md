# 🐱 Cat-straints: The N-Kittens Challenge
> **An Interactive CSP & AI Search Adventure with Cute Kittens, Real-Time Laser Eye Conflicts, Animated Backtracking, and Fireworks! 🎆**

A cozy, educational web application for exploring the classic **N-Queens Constraint Satisfaction Problem (CSP)** with an adorable twist: chess queens are replaced by cuddly kittens! 

Users can attempt to place cats manually, watch red laser conflict beams connect any attacking pairs in real time, step through an animated Depth-First Backtracking search, race Backtracking against Min-Conflicts Hill Climbing in a live algorithm showdown, and celebrate solved boards with dazzling canvas fireworks and victory audio!

---

## ✨ Features

### 1. 🐾 Cute Cat Face Avatars & Dynamic Expressions
* Chess queens are replaced with handcrafted SVG kittens in multiple breeds: **Orange Tabby**, **Calico**, **Siamese**, **Tuxedo**, **Pastel Pink**, and **Matcha Cream**.
* Expressions dynamically react to board state:
  * 😸 **Peaceful & Happy:** When safe from attack.
  * 😾 **Stressed & Laser Eyes (`>_<`):** When attacked along rows, columns, or diagonals.
  * 👑 **Royal Crown & Sparkles (`✨`):** When the puzzle is successfully solved!

### 2. ⚡ Real-Time Laser Conflict Beams
* Attacking pairs (same row, same column, or same diagonal) are highlighted in real time.
* An HTML5 overlay canvas draws vibrant red laser beams with an outer warning glow between conflicting cats.
* Live badges display individual warning pips and update the total conflict counter $\sum \text{conflicts}$ instantaneously.

### 3. 🎬 Interactive Animated Backtracking (DFS)
* Watch how the AI systematically navigates the search tree.
* Step-by-step visualizer with:
  * **Play / Pause** auto-running search.
  * **Step Forward & Step Backward** (full historical state stack).
  * **Speed Slider** (from 10ms lightning search to 500ms educational slow-motion).
  * **Live Search Metrics:** Nodes explored, dead ends encountered, and backtrack count.

### 4. ⚔️ Algorithm Showdown (Backtracking vs. Hill Climbing)
* Compare **Systematic Search (Backtracking)** vs. **Local Optimization (Min-Conflicts Hill Climbing)** side-by-side on identical board sizes.
* Live race benchmarks:
  * Execution Time (ms)
  * Search Nodes / Steps Explored
  * Backtracks vs. Random Restarts
  * Completeness & Optimality trade-offs

### 5. 🎚️ Dynamic Board Sizing ($N = 4 \dots 12$)
* Instant board resize slider with quick preset buttons ($4\times4, 6\times6, 8\times8, 10\times10, 12\times12$).
* Dynamic grid auto-scales tiles and cat avatars responsively.

### 6. 🎆 Fullscreen Fireworks Celebration
* Solved boards trigger an explosive particle fireworks & confetti celebration canvas.
* Multi-color rockets burst with gravity, air resistance, and sparkles.
* Synthesized Web Audio API fanfare (no external mp3 files required — 100% offline & zero network lag).

### 7. 📚 Embedded CSP & Search Syllabus Hub
* Dedicated interactive guide covering:
  * **CSP Formulation:** Variables $X_i$, Domains $D_i$, Constraints $C$.
  * **State-Space Search:** Naive state space $N^N$ vs. Permutations $N!$ vs. CSP tree pruning.
  * **Systematic DFS vs. Min-Conflicts Heuristic.**
  * **Real-World Applications:** Scheduling, timetabling, circuit design, and register allocation.

---

## 🚀 Deployment & Local Usage

The application is completely self-contained (vanilla HTML5, CSS3, ES6 JavaScript, Tailwind CSS via CDN, and Web Audio API). There are **no build steps, bundlers, or server requirements**.

### Option 1: Direct Browser Open (Fastest)
Simply double-click `index.html` or drag it into any modern web browser (Chrome, Safari, Edge, Firefox).

### Option 2: Local HTTP Server
Using Python:
```bash
python3 -m http.server 8080
```
Then visit `http://localhost:8080` in your browser.

Using Node.js:
```bash
npx serve .
```

### Option 3: Deploy to GitHub Pages (1-Click)
1. Push this repository to GitHub.
2. In your repository, go to **Settings > Pages**.
3. Under **Build and deployment > Branch**, select `main` (or `master`) and folder `/ (root)`.
4. Click **Save**. Your site will be live at `https://<your-username>.github.io/<repo-name>/`!

### Option 4: Deploy to Vercel or Netlify
* **Vercel:** Drag and drop the folder into [vercel.com](https://vercel.com) or run `vercel`.
* **Netlify:** Drag and drop the folder into [app.netlify.com/drop](https://app.netlify.com/drop).

---

## 📖 Syllabus & Conceptual Reference

### 1. Constraint Satisfaction Problem (CSP)
A CSP is formally defined by three components $(X, D, C)$:
* **Variables ($X$):** $X = \{X_0, X_1, \dots, X_{N-1}\}$, where variable $X_i$ represents the cat placed in row $i$.
* **Domains ($D$):** For each variable $X_i$, its domain is $D_i = \{0, 1, \dots, N-1\}$, representing the column index.
* **Constraints ($C$):** For all $i \neq j$:
  1. **Column constraint:** $X_i \neq X_j$
  2. **Diagonal constraint:** $|X_i - X_j| \neq |i - j|$

### 2. State-Space Complexity
* **Naive State Space:** $N^N$ possible configurations. For $N=8$, this is $8^8 = 16,777,216$ states.
* **Permutation Formulation:** Enforcing distinct columns restricts search to $N!$ states ($8! = 40,320$ states).
* **Backtracking Search:** By pruning invalid partial assignments at depth $k < N$, backtracking searches only valid prefixes, finding the first solution to 8-Queens in only ~876 node evaluations.

### 3. Backtracking vs. Hill Climbing
| Metric | Backtracking (DFS) | Hill Climbing (Min-Conflicts) |
| :--- | :--- | :--- |
| **Search Type** | Systematic Tree Search | Local Heuristic Search |
| **State Nature** | Partial assignments ($0 \le k \le N$) | Complete assignments ($N$ cats placed) |
| **Completeness** | **Complete** (Guaranteed solution or proof of none) | **Incomplete** (Can plateau without restarts) |
| **Space Complexity** | $O(N)$ stack depth | $O(N)$ current board |
| **Scalability** | Struggles when $N > 30$ | Solves $N = 10,000+$ in near $O(N)$ time |

---

## 🎨 Project Structure

```text
busy-lavoisier/
├── index.html          # Main responsive single-page web app
├── css/
│   └── styles.css      # Pastel theme, animations, laser glow, board styling
├── js/
│   ├── audio.js        # Web Audio API synthesizer (plop, meows, victory fanfare)
│   ├── cats.js         # SVG kitten avatar generator (breeds & expressions)
│   ├── csp-engine.js   # CSP conflict logic, Backtracking & Min-Conflicts solvers
│   ├── fireworks.js    # Canvas particle fireworks & confetti engine
│   └── app.js          # Controller connecting UI, events, timers, & dual boards
└── README.md           # Documentation, syllabus notes & deployment guide
```

---

## 🐾 License
MIT License. Created with 💖 for computer science students, AI educators, and cat lovers everywhere!
