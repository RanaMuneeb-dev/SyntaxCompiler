# 🚀 SyntaxCompiler: Bilingual Visual Compiler & IR Optimizer

> **Syntax Summit '26 Hackathon Project**  
> An interactive bilingual compiler (English & Roman Urdu) featuring a 6-stage visual pipeline, AST constant-folding optimizer, and safe VM executor designed for next-generation Computer Science education.

---

## 🌟 Key Features

* **🌐 Native Bilingual Syntax:** First-class support for Roman Urdu (`rakho`, `jabtak`, `agar`, `warna`, `dikhao`, `aur`, `ya`, `nahi`) and standard English (`let`, `while`, `if`, `else`, `print`, `&&`, `||`, `!`).
* **🔍 6-Stage Visual Inspection Pipeline:**
  1. **Phase 01 — Lexer:** Token table with categories, line tracking, and live filter chips.
  2. **Phase 02 — LL(1) Parser:** Interactive collapsible Abstract Syntax Tree (AST).
  3. **Phase 03 — Semantic Analyzer:** Static type inference (`number`, `string`, `bool`) and scope resolution.
  4. **Phase 04 — Three-Address Code (TAC):** Quadruple intermediate representation with jump and label backpatching.
  5. **Phase 04.5 — Compiler Optimizer:** AST-level Constant Folding ($10 + 20 \times 2 \to 50$) and Dead-Branch Pruning with a side-by-side Raw vs Optimized TAC diff panel (slashing redundant instructions by up to 40%).
  6. **Phase 05 — Virtual Machine:** In-memory execution sandbox with $S_{\max} = 50{,}000$ cycle infinite-loop protection and terminal output.
* **🌓 Cyber Dark & Day Light Mode:** Fluid animated theme switcher.
* **⚡ Zero External Backend Dependencies:** Native Python 3 standard library architecture.

---

## 🛠️ Quick Start Guide

### Prerequisites
* Python 3.10+
* Node.js 18+ & npm

### 1. Start Backend Compiler Engine
```bash
# From repository root
python backend/main.py
# Server runs at http://localhost:8000
```

### 2. Start Frontend IDE Visualizer
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173 in your browser
```

---

## 📖 Bilingual Syntax Cheatsheet

| Category | Roman Urdu | English Equivalent | Example |
| :--- | :--- | :--- | :--- |
| **Variable Declaration** | `rakho` / `banao` | `let` | `rakho x = 10;` |
| **Conditional If** | `agar (cond) { }` | `if (cond) { }` | `agar (x > 5) { }` |
| **Conditional Else** | `warna { }` | `else { }` | `warna { dikhao "No"; }` |
| **While Loop** | `jabtak (cond) { }` | `while (cond) { }` | `jabtak (n > 1) { n = n - 1; }` |
| **Standard Output** | `dikhao` / `bolo` / `likho` | `print` | `dikhao "Factorial: ";` |
| **Logical AND** | `aur` | `&&` | `agar (x > 0 aur x < 10)` |
| **Logical OR** | `ya` | `\|\|` | `agar (x == 1 ya x == 2)` |
| **Logical NOT** | `nahi` | `!` | `agar (nahi (x == 0))` |
| **Modulo Operator** | `%` | `%` | `rakho rem = n % 2;` |
| **Comments** | `//` and `/* */` | `//` and `/* */` | `// Roman Urdu Comment` |

---

## 📂 Repository Architecture

```text
SyntaxCompiler/
├── backend/                       # Pure Python Compiler Pipeline
│   ├── lexer.py                   # Tokenizer & comment stripper
│   ├── ast_nodes.py               # Typed AST node definitions
│   ├── parser.py                  # LL(1) Recursive Descent Parser
│   ├── semantic.py                # Symbol Table & Type Checker
│   ├── tac.py                     # Three-Address Code Quadruples Generator
│   ├── optimizer.py               # AST Constant-Folding & Dead-Code Optimizer
│   ├── vm.py                      # Stack-safe Virtual Machine Executor
│   ├── main.py                    # Standard library HTTP Server
│   └── test_suite.py              # Automated regression tests
├── frontend/                      # React + Vite Interactive IDE
│   ├── src/
│   │   ├── components/            # Visual panels (Tokens, AST, Symbols, TAC, Optimizer, Output)
│   │   ├── App.jsx                # Split-screen IDE workspace & Theme Switcher
│   │   └── App.module.css         # Responsive styles
│   ├── package.json
│   └── vite.config.js
├── .gitignore                     # Clean ignore rules
└── README.md                      # Comprehensive documentation
```

---

## 🧪 Testing

Run automated compiler regression tests:
```bash
python backend/test_suite.py
```
*Tests verify Roman Urdu loops, AST constant folding, logical expressions, and semantic error reporting.*
