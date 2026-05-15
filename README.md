# Linear Programming Solver — Simplex / Graphical Method

A desktop Python application with a modern interface (blue/black theme) that solves
**Linear Programming** problems using the **Simplex Method** and the **Graphical Method**.

---

## Features

- Modern UI built with **CustomTkinter** (dark theme, blue palette).
- **Simplex Method** solver powered by `scipy.optimize.linprog` (HiGHS engine).
- **Graphical Method** with visualization of:
  - Constraint lines.
  - Shaded feasible region.
  - Vertices labeled with their Z value.
  - Optimal point marked with a star.
  - Iso-Z dashed line (when a target Z is provided).
- **Maximize / Minimize** selector.
- Free-form objective function with any number of variables (Simplex) or 2 variables (Graphical).
- Dynamic constraints: add, remove, and clear.
- Supported operators: `<=`, `>=`, `=`.
- **"Use defined Z value"** option: compares a target Z against the optimum and
  reports whether it is reachable inside the feasible region.
- **Export results** to PDF or Excel (`.xlsx`) from the main panel.

---

## Requirements

- **Python 3.10+** (tested on 3.13).
- Libraries:
  - `customtkinter`
  - `scipy`
  - `matplotlib`
  - `numpy`
  - `reportlab` (PDF export)
  - `openpyxl` (Excel export)

### Install dependencies

```bash
pip install customtkinter scipy matplotlib numpy reportlab openpyxl
```

---

## Run

From the project folder:

```bash
python main.py
```

Or with the absolute path:

```bash
python C:\path\to\simplex\main.py
```

---

## Project structure

```
simplex/
├── main.py             # Entry point
├── app.py              # Graphical interface (CustomTkinter)
├── solver.py           # Simplex and graphical method logic
├── simplex_tabular.py  # Tabular Simplex / Big M / Two-Phase implementations
├── parser.py           # Expression and constraint parser
├── exporter.py         # PDF / Excel export of results
└── README.md
```

---

## Usage

### 1. Define the problem

1. Select **Maximize** or **Minimize**.
2. Enter the **objective function**, e.g.:
   ```
   3x + 5y
   ```
3. Add the **constraints**, e.g.:
   ```
   2x + 3y <= 18
   2x + y  <= 10
   x + 3y  <= 12
   ```
   (non-negativity constraints `x, y >= 0` are applied automatically).

### 2. Solve

- **Solve with Simplex** — accepts any number of variables. Shows the optimal
  values and Z in the *Results* tab.
- **Solve graphically** — requires exactly 2 variables. Plots the feasible
  region, vertices, and optimum in the *Graph* tab.

### 3. Export results

After solving, the results can be exported to:

- **PDF** — generates a printable report with the objective function, constraints
  and full result text (uses `reportlab`).
- **Excel (`.xlsx`)** — writes the same information into a spreadsheet (uses
  `openpyxl`).

A "Save as…" dialog lets you choose the destination file.

### 4. Defined Z (optional)

Tick the **"Use defined Z value"** checkbox and enter a Z value. The app will:

- Tell you whether that Z is **reachable** inside the feasible region.
- Draw the iso-Z dashed line on the graph.
- Compare the target Z against the optimal Z and report the difference.

---

## Input syntax

| Element                 | Example               | Notes                                  |
|-------------------------|-----------------------|----------------------------------------|
| Variables               | `x`, `y`, `x1`, `z2`  | Any alphanumeric identifier            |
| Coefficients            | `3x`, `-2.5y`, `0.5x` | Decimals allowed                       |
| Arithmetic operators    | `+`, `-`              | Implicit multiplication: `3x = 3*x`    |
| Relational operators    | `<=`, `>=`, `=`       | `<` and `>` are also accepted          |

### Valid examples

```
Z  = 3x + 5y
Z  = 4x1 + 2x2 + x3
constraint: 2x + 3y <= 18
constraint: x - y >= -2
constraint: x + y = 10
```

---

## Full example

**Problem:**

```
Maximize  Z = 3x + 5y
Subject to:
   2x + 3y <= 18
   2x +  y <= 10
    x + 3y <= 12
   x, y >= 0
```

**Expected result:**

- `x = 3.6`, `y = 2.8`
- `Z* = 24.8`
- Feasible vertices: `(0, 0)`, `(5, 0)`, `(3.6, 2.8)`, `(0, 4)`

---

## Tech stack

| Library                   | Purpose                                 |
|---------------------------|-----------------------------------------|
| `customtkinter`           | Modern dark-themed UI                   |
| `scipy.optimize.linprog`  | Simplex Method (HiGHS engine)           |
| `matplotlib`              | Graphical method rendering              |
| `numpy`                   | Intersection and vertex computations    |
| `reportlab`               | PDF report export                       |
| `openpyxl`                | Excel (`.xlsx`) export                  |

---

## License

Free to use for educational purposes.
