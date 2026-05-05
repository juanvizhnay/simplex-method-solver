"""Simplex tabular con soporte simbólico para M (M grande) y método de Dos Fases."""

EPS = 1e-9
MAX_ITER = 100


class Coef:
    """Representa un coeficiente de la forma a + b*M, con M >> 0."""
    __slots__ = ("a", "b")

    def __init__(self, a=0.0, b=0.0):
        self.a = float(a)
        self.b = float(b)

    def __add__(self, other):
        if isinstance(other, Coef):
            return Coef(self.a + other.a, self.b + other.b)
        return Coef(self.a + other, self.b)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Coef):
            return Coef(self.a - other.a, self.b - other.b)
        return Coef(self.a - other, self.b)

    def __rsub__(self, other):
        return Coef(other - self.a, -self.b)

    def __mul__(self, k):
        if isinstance(k, Coef):
            if abs(k.b) < EPS:
                return Coef(self.a * k.a, self.b * k.a)
            if abs(self.b) < EPS:
                return Coef(self.a * k.a, self.a * k.b)
            raise ValueError("Producto M*M no soportado.")
        return Coef(self.a * k, self.b * k)

    def __rmul__(self, k):
        return self.__mul__(k)

    def __truediv__(self, k):
        if isinstance(k, Coef):
            if abs(k.b) > EPS:
                raise ValueError("División por expresión con M no soportada.")
            k = k.a
        return Coef(self.a / k, self.b / k)

    def __neg__(self):
        return Coef(-self.a, -self.b)

    def __lt__(self, other):
        if not isinstance(other, Coef):
            other = Coef(other)
        if abs(self.b - other.b) > EPS:
            return self.b < other.b - EPS
        return self.a < other.a - EPS

    def __le__(self, other):
        return not (other.__lt__(self) if isinstance(other, Coef) else Coef(other).__lt__(self))

    def __gt__(self, other):
        return (other if isinstance(other, Coef) else Coef(other)).__lt__(self)

    def __eq__(self, other):
        if not isinstance(other, Coef):
            other = Coef(other)
        return abs(self.a - other.a) < EPS and abs(self.b - other.b) < EPS

    def __hash__(self):
        return hash((round(self.a, 9), round(self.b, 9)))

    def is_zero(self):
        return abs(self.a) < EPS and abs(self.b) < EPS

    def fmt(self):
        a, b = self.a, self.b
        if abs(a) < EPS and abs(b) < EPS:
            return "0"
        if abs(b) < EPS:
            return f"{a:.4g}"
        if abs(a) < EPS:
            if abs(b - 1) < EPS:
                return "M"
            if abs(b + 1) < EPS:
                return "-M"
            return f"{b:.4g}M"
        bs = ""
        if abs(abs(b) - 1) > EPS:
            bs = f"{abs(b):.4g}"
        sign = "+" if b > 0 else "-"
        return f"{a:.4g}{sign}{bs}M"


def _reduced_costs(A, c, basis):
    n = len(c)
    m = len(basis)
    cB = [c[basis[i]] for i in range(m)]
    reduced = []
    for j in range(n):
        zj = Coef(0)
        for i in range(m):
            zj = zj + cB[i] * A[i][j]
        reduced.append(c[j] - zj)
    return reduced


def _pivot(A, b, basis, i_piv, j_piv):
    n = len(A[0])
    pv = A[i_piv][j_piv]
    A[i_piv] = [v / pv for v in A[i_piv]]
    b[i_piv] = b[i_piv] / pv
    for k in range(len(b)):
        if k == i_piv:
            continue
        factor = A[k][j_piv]
        if abs(factor) < EPS:
            continue
        A[k] = [A[k][p] - factor * A[i_piv][p] for p in range(n)]
        b[k] = b[k] - factor * b[i_piv]
    basis[i_piv] = j_piv


def _snapshot(A, b, c, basis, var_names, label, reduced=None,
              entering=None, leaving=None, ratios=None, pivot_row=None,
              z_value=None, gauss_ops=None, pivot_col=None, pivot_val=None):
    return {
        "label": label,
        "var_names": list(var_names),
        "basis": list(basis),
        "A": [row[:] for row in A],
        "b": b[:],
        "c": [Coef(co.a, co.b) for co in c],
        "reduced": [Coef(r.a, r.b) for r in reduced] if reduced else None,
        "entering": entering,
        "leaving": leaving,
        "ratios": ratios,
        "pivot_row": pivot_row,
        "pivot_col": pivot_col,
        "pivot_val": pivot_val,
        "z_value": z_value,
        "gauss_ops": gauss_ops,
    }


def _objective_value(c, basis, b):
    z = Coef(0)
    for i, bj in enumerate(basis):
        z = z + c[bj] * b[i]
    return z


def simplex_iterations(c, A, b, basis, var_names, label_prefix=""):
    """Simplex sobre forma estándar: min c'x s.a. Ax=b, x>=0. Captura cada tabla."""
    iterations = []
    iteration = 0
    while True:
        reduced = _reduced_costs(A, c, basis)
        j_piv = -1
        min_r = Coef(0)
        for j in range(len(c)):
            if reduced[j] < min_r:
                min_r = reduced[j]
                j_piv = j
        z_val = _objective_value(c, basis, b)
        if j_piv == -1:
            iterations.append(_snapshot(
                A, b, c, basis, var_names,
                label=f"{label_prefix}Tabla {iteration} (ÓPTIMA)",
                reduced=reduced, z_value=z_val,
            ))
            return "optimal", basis, iterations

        ratios = []
        for i in range(len(b)):
            if A[i][j_piv] > EPS:
                ratios.append(b[i] / A[i][j_piv])
            else:
                ratios.append(None)
        i_piv = -1
        min_ratio = float("inf")
        for i, r in enumerate(ratios):
            if r is not None and r < min_ratio - EPS:
                min_ratio = r
                i_piv = i
        if i_piv == -1:
            iterations.append(_snapshot(
                A, b, c, basis, var_names,
                label=f"{label_prefix}Tabla {iteration} (NO ACOTADA)",
                reduced=reduced, entering=j_piv, ratios=ratios, z_value=z_val,
            ))
            return "unbounded", basis, iterations

        leaving = basis[i_piv]
        label = f"{label_prefix}Tabla {iteration}" + (" (inicial)" if iteration == 0 else "")
        pivot_val = A[i_piv][j_piv]
        gauss_ops = [f"F{i_piv+1} ← (1/{pivot_val:.4g}) · F{i_piv+1}"]
        for k in range(len(b)):
            if k != i_piv and abs(A[k][j_piv]) > EPS:
                factor = A[k][j_piv]
                sign = "+" if factor < 0 else "−"
                gauss_ops.append(
                    f"F{k+1} ← F{k+1} {sign} ({abs(factor):.4g}) · F{i_piv+1}"
                )
        iterations.append(_snapshot(
            A, b, c, basis, var_names, label=label, reduced=reduced,
            entering=j_piv, leaving=leaving, ratios=ratios, pivot_row=i_piv,
            pivot_col=j_piv, pivot_val=pivot_val, z_value=z_val,
            gauss_ops=gauss_ops,
        ))
        _pivot(A, b, basis, i_piv, j_piv)
        iteration += 1
        if iteration > MAX_ITER:
            return "max_iter", basis, iterations


def setup_problem(c_orig, A_ub, b_ub, A_eq, b_eq, var_names_orig, sense, method):
    """Construye la forma estándar añadiendo holguras, excedentes y artificiales."""
    n_orig = len(c_orig)
    c_for_min = [-x for x in c_orig] if sense == "max" else list(c_orig)

    rows = []
    if A_ub is not None and len(A_ub) > 0:
        for i in range(len(A_ub)):
            row = list(A_ub[i])
            rhs = float(b_ub[i])
            if rhs < 0:
                row = [-v for v in row]
                rows.append((row, ">=", -rhs))
            else:
                rows.append((row, "<=", rhs))
    if A_eq is not None and len(A_eq) > 0:
        for i in range(len(A_eq)):
            row = list(A_eq[i])
            rhs = float(b_eq[i])
            if rhs < 0:
                row = [-v for v in row]
                rhs = -rhs
            rows.append((row, "=", rhs))

    m = len(rows)
    var_names = list(var_names_orig)
    c = [Coef(v) for v in c_for_min]
    A = [r[0][:] for r in rows]
    b = [r[2] for r in rows]
    basis = [None] * m
    artificial_indices = []
    s_n = 0
    e_n = 0
    a_n = 0

    for i in range(m):
        for k in range(m):
            A[k] = A[k]

    for i, (_, op, _) in enumerate(rows):
        if op == "<=":
            s_n += 1
            var_names.append(f"s{s_n}")
            c.append(Coef(0))
            for k in range(m):
                A[k].append(1.0 if k == i else 0.0)
            basis[i] = len(var_names) - 1
        elif op == ">=":
            e_n += 1
            var_names.append(f"e{e_n}")
            c.append(Coef(0))
            for k in range(m):
                A[k].append(-1.0 if k == i else 0.0)
            a_n += 1
            var_names.append(f"a{a_n}")
            c.append(Coef(0, 1) if method == "bigM" else Coef(0))
            for k in range(m):
                A[k].append(1.0 if k == i else 0.0)
            basis[i] = len(var_names) - 1
            artificial_indices.append(len(var_names) - 1)
        else:
            a_n += 1
            var_names.append(f"a{a_n}")
            c.append(Coef(0, 1) if method == "bigM" else Coef(0))
            for k in range(m):
                A[k].append(1.0 if k == i else 0.0)
            basis[i] = len(var_names) - 1
            artificial_indices.append(len(var_names) - 1)

    return {
        "c": c, "A": A, "b": b, "basis": basis,
        "var_names": var_names, "n_orig": n_orig,
        "artificial_indices": artificial_indices, "sense": sense,
        "row_ops": [r[1] for r in rows],
    }


def needs_artificials(A_ub, b_ub, A_eq, b_eq):
    if A_eq is not None and len(A_eq) > 0:
        return True
    if A_ub is not None and len(A_ub) > 0:
        for v in b_ub:
            if v < 0:
                return True
    return False


def solve_with_method(c_orig, A_ub, b_ub, A_eq, b_eq, var_names_orig, sense, method):
    """method ∈ {'simplex', 'bigM', 'twophase'}."""
    if method == "simplex":
        if needs_artificials(A_ub, b_ub, A_eq, b_eq):
            return {
                "ok": False,
                "msg": ("El Simplex estándar requiere todas las restricciones '<=' "
                        "con lado derecho >= 0.\nUse Método M Grande o Dos Fases."),
                "iterations": [],
            }
        prob = setup_problem(c_orig, A_ub, b_ub, A_eq, b_eq, var_names_orig, sense, "simplex")
        status, basis, its = simplex_iterations(
            prob["c"], prob["A"], prob["b"], prob["basis"], prob["var_names"]
        )
        return _build_result(status, basis, its, prob)

    if method == "bigM":
        prob = setup_problem(c_orig, A_ub, b_ub, A_eq, b_eq, var_names_orig, sense, "bigM")
        status, basis, its = simplex_iterations(
            prob["c"], prob["A"], prob["b"], prob["basis"], prob["var_names"],
            label_prefix="M-Grande · ",
        )
        result = _build_result(status, basis, its, prob)
        if result["ok"]:
            for i, bj in enumerate(basis):
                if bj in prob["artificial_indices"] and prob["b"][i] > 1e-6:
                    result["ok"] = False
                    result["msg"] = "Problema INFACTIBLE: variable artificial > 0 en óptimo."
                    break
        return result

    if method == "twophase":
        prob = setup_problem(c_orig, A_ub, b_ub, A_eq, b_eq, var_names_orig, sense, "twophase")
        artif = prob["artificial_indices"]

        if not artif:
            status, basis, its = simplex_iterations(
                prob["c"], prob["A"], prob["b"], prob["basis"], prob["var_names"]
            )
            return _build_result(status, basis, its, prob)

        # Fase 1: minimizar W = suma de artificiales
        c_phase1 = [Coef(0) for _ in prob["c"]]
        for j in artif:
            c_phase1[j] = Coef(1)
        A1 = [row[:] for row in prob["A"]]
        b1 = prob["b"][:]
        basis1 = prob["basis"][:]
        status1, basis1, its1 = simplex_iterations(
            c_phase1, A1, b1, basis1, prob["var_names"], label_prefix="Fase 1 · ",
        )
        w = sum(c_phase1[basis1[i]].a * b1[i] for i in range(len(b1)))
        if w > 1e-6:
            return {
                "ok": False,
                "msg": f"Problema INFACTIBLE: Fase 1 termina con W = {w:.4f} > 0",
                "iterations": its1,
                "phase1_W": w,
                "var_names": prob["var_names"],
                "n_orig": prob["n_orig"],
            }

        # Fase 2: usar c original; bloquear artificiales con coste +M para que no reentren
        c_phase2 = [Coef(co.a, co.b) for co in prob["c"]]
        for j in artif:
            c_phase2[j] = Coef(0, 1)
        status2, basis2, its2 = simplex_iterations(
            c_phase2, A1, b1, basis1, prob["var_names"], label_prefix="Fase 2 · ",
        )
        prob["A"] = A1
        prob["b"] = b1
        result = _build_result(status2, basis2, its1 + its2, prob)
        result["phase1_W"] = w
        return result

    return {"ok": False, "msg": f"Método desconocido: {method}", "iterations": []}


def _build_result(status, basis, iterations, prob):
    var_names = prob["var_names"]
    n_orig = prob["n_orig"]
    sense = prob["sense"]
    if status == "unbounded":
        return {"ok": False, "msg": "Solución NO ACOTADA.", "iterations": iterations,
                "var_names": var_names, "n_orig": n_orig}
    if status == "max_iter":
        return {"ok": False, "msg": "Se alcanzó el máximo de iteraciones.", "iterations": iterations,
                "var_names": var_names, "n_orig": n_orig}
    A = prob["A"]
    b = prob["b"]
    values = {var_names[j]: 0.0 for j in range(n_orig)}
    for i, j in enumerate(basis):
        if j < n_orig:
            values[var_names[j]] = b[i]
    c_orig = [prob["c"][j].a for j in range(n_orig)]
    z = sum(c_orig[j] * values[var_names[j]] for j in range(n_orig))
    if sense == "max":
        z = -z
    return {
        "ok": True,
        "values": values,
        "z": z,
        "iterations": iterations,
        "var_names": var_names,
        "n_orig": n_orig,
        "basis": basis,
    }


def format_iterations(iterations, sense, style="simplex"):
    """Renderiza las tablas como texto monoespaciado.
    style='simplex' → tablas con Cj/Cj-Zj y entra/sale (M Grande, Dos Fases).
    style='gauss'   → matriz + operaciones de filas tipo Gauss-Jordan.
    """
    if not iterations:
        return ""
    if style == "gauss":
        return _format_gauss(iterations, sense)
    out = []
    CW = 9   # ancho de columna
    BW = 10  # ancho cabecera de fila
    flip_default = sense == "max"  # internamente minimizamos -c, por eso negamos al mostrar

    if flip_default:
        out.append("Nota: el problema es de MAXIMIZACIÓN. Internamente se resuelve")
        out.append("min(-Z); en las tablas se muestran los valores ya negados para")
        out.append("que coincidan con el Z original (Cj y Cj-Zj con signos invertidos).")
        out.append("Excepción: la Fase 1 minimiza W (suma de artificiales) y se muestra tal cual.")

    for it in iterations:
        # Fase 1 es siempre minimizar W, sin importar el sentido del problema original
        flip = flip_default and not it["label"].startswith("Fase 1")
        var_names = it["var_names"]
        basis = it["basis"]
        A = it["A"]
        b = it["b"]
        c = it["c"]
        reduced = it["reduced"]
        ratios = it["ratios"]
        n = len(var_names)

        out.append("")
        out.append(f"┌── {it['label']} " + "─" * max(0, 60 - len(it['label'])))

        # Fila Cj (negada para mostrar al usuario en problemas de max)
        c_show = [(-c[j] if flip else c[j]) for j in range(n)]
        line = f"{'Cj':<{BW}}│"
        for j in range(n):
            line += f" {c_show[j].fmt():>{CW}}"
        line += f" │ {'b':>{CW}}"
        out.append(line)

        # Cabecera de variables
        line = f"{'Base':<{BW}}│"
        for j in range(n):
            line += f" {var_names[j]:>{CW}}"
        line += f" │ {'RHS':>{CW}}"
        if ratios is not None:
            line += f" │ {'razón':>{CW}}"
        out.append(line)

        sep = "─" * BW + "┼" + "─" * (n * (CW + 1) + 1) + "┼" + "─" * (CW + 2)
        if ratios is not None:
            sep += "┼" + "─" * (CW + 2)
        out.append(sep)

        # Filas de la base
        pivot_row = it.get("pivot_row")
        for i, bj in enumerate(basis):
            row = f"{var_names[bj]:<{BW}}│"
            for j in range(n):
                v = A[i][j]
                row += f" {v:>{CW}.4g}"
            row += f" │ {b[i]:>{CW}.4g}"
            if ratios is not None:
                if ratios[i] is None:
                    row += f" │ {'—':>{CW}}"
                else:
                    mark = " ←" if i == pivot_row else "  "
                    row += f" │ {ratios[i]:>{CW-2}.4g}{mark}"
            out.append(row)

        out.append(sep)

        # Cj - Zj  (también negado para max)
        if reduced is not None:
            line = f"{'Cj-Zj':<{BW}}│"
            for j in range(n):
                rj = -reduced[j] if flip else reduced[j]
                line += f" {rj.fmt():>{CW}}"
            zv = it.get("z_value")
            if zv is not None:
                z_show = (-zv if flip else zv).fmt()
            else:
                z_show = ""
            line += f" │ Z={z_show}"
            out.append(line)

        # Anotaciones de pivote
        if it.get("entering") is not None and it.get("leaving") is not None:
            ent = var_names[it["entering"]]
            lev = var_names[it["leaving"]]
            out.append(f"   ▸ Entra: {ent}    Sale: {lev}    "
                       f"(pivote = {A[pivot_row][it['entering']]:.4g})")
        elif it.get("entering") is not None:
            out.append(f"   ▸ Entra: {var_names[it['entering']]}   (sin variable de salida → no acotada)")

    return "\n".join(out)


def _format_gauss(iterations, sense):
    """Formato Gauss-Jordan: matriz + operaciones de filas, sin jerga simplex."""
    out = []
    out.append("Resolución por eliminación de Gauss-Jordan sobre la matriz aumentada.")
    out.append("Se elige en cada paso la columna pivote (la que mejora más Z) y la")
    out.append("fila pivote (la del menor cociente positivo b_i / a_ij), y se aplica")
    out.append("Gauss-Jordan para que esa columna quede con un 1 en el pivote y 0 en el resto.")
    out.append("")

    CW = 9
    BW = 6  # ancho cabecera de fila ("F1", "F2", ...)
    flip = sense == "max"

    for idx, it in enumerate(iterations):
        var_names = it["var_names"]
        A = it["A"]
        b = it["b"]
        n = len(var_names)
        m = len(b)

        out.append(f"┌── {it['label']} " + "─" * max(0, 60 - len(it['label'])))
        # Cabecera de columnas
        line = f"{'':<{BW}}│"
        for j in range(n):
            line += f" {var_names[j]:>{CW}}"
        line += f" │ {'b':>{CW}}"
        out.append(line)
        sep = "─" * BW + "┼" + "─" * (n * (CW + 1) + 1) + "┼" + "─" * (CW + 2)
        out.append(sep)
        # Filas
        for i in range(m):
            row = f"{'F'+str(i+1):<{BW}}│"
            for j in range(n):
                row += f" {A[i][j]:>{CW}.4g}"
            row += f" │ {b[i]:>{CW}.4g}"
            out.append(row)
        out.append(sep)

        # Valor actual de Z (con signo correcto si es max)
        zv = it.get("z_value")
        if zv is not None:
            z_disp = (-zv if flip else zv).fmt()
            out.append(f"   Z actual = {z_disp}")

        # Si hay pivote planeado, mostrar elección + operaciones de Gauss
        if it.get("pivot_col") is not None and it.get("pivot_row") is not None:
            i_p = it["pivot_row"]
            j_p = it["pivot_col"]
            pv = it["pivot_val"]
            ratios = it["ratios"]
            out.append("")
            out.append(f"   Columna pivote: «{var_names[j_p]}» (la que más reduce el valor objetivo).")
            cocientes = []
            for i in range(m):
                if ratios[i] is None:
                    cocientes.append(f"F{i+1}: a≤0")
                else:
                    mark = "  ← mínimo" if i == i_p else ""
                    cocientes.append(f"F{i+1}: {b[i]:.4g}/{A[i][j_p]:.4g} = {ratios[i]:.4g}{mark}")
            out.append(f"   Cocientes b_i / a_i,{var_names[j_p]}:")
            for c_line in cocientes:
                out.append(f"       {c_line}")
            out.append(f"   ⇒ Pivote = a[F{i_p+1}, {var_names[j_p]}] = {pv:.4g}")
            out.append("")
            out.append("   Operaciones por filas (Gauss-Jordan):")
            for op in it.get("gauss_ops") or []:
                out.append(f"       {op}")

        out.append("")

    return "\n".join(out)
