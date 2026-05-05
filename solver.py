import numpy as np
from itertools import combinations
from scipy.optimize import linprog

from parser import parse_expression, parse_constraint
from simplex_tabular import solve_with_method, format_iterations


class LPSolver:
    def __init__(self):
        self.objective = ""
        self.constraints = []
        self.sense = "max"
        self.target_z = None

    def _build_arrays(self):
        obj_coefs = parse_expression(self.objective)
        obj_coefs.pop("__const__", None)
        cons_parsed = [parse_constraint(c) for c in self.constraints if c.strip()]

        all_vars = set(obj_coefs.keys())
        for lhs, _, _ in cons_parsed:
            all_vars.update(lhs.keys())
        variables = sorted(all_vars)

        c = np.array([obj_coefs.get(v, 0.0) for v in variables], dtype=float)
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for lhs, op, rhs in cons_parsed:
            row = [lhs.get(v, 0.0) for v in variables]
            if op == "<=":
                A_ub.append(row); b_ub.append(rhs)
            elif op == ">=":
                A_ub.append([-x for x in row]); b_ub.append(-rhs)
            else:
                A_eq.append(row); b_eq.append(rhs)
        return {
            "variables": variables,
            "c": c,
            "A_ub": np.array(A_ub, dtype=float) if A_ub else None,
            "b_ub": np.array(b_ub, dtype=float) if b_ub else None,
            "A_eq": np.array(A_eq, dtype=float) if A_eq else None,
            "b_eq": np.array(b_eq, dtype=float) if b_eq else None,
            "cons_parsed": cons_parsed,
        }

    def solve_simplex(self):
        data = self._build_arrays()
        c = data["c"]
        c_lp = -c if self.sense == "max" else c
        bounds = [(0, None) for _ in data["variables"]]
        res = linprog(
            c_lp,
            A_ub=data["A_ub"], b_ub=data["b_ub"],
            A_eq=data["A_eq"], b_eq=data["b_eq"],
            bounds=bounds, method="highs",
        )
        if not res.success:
            return {"ok": False, "msg": res.message, "variables": data["variables"]}
        z_val = -res.fun if self.sense == "max" else res.fun
        return {
            "ok": True,
            "variables": data["variables"],
            "values": dict(zip(data["variables"], res.x)),
            "z": z_val,
            "msg": res.message,
        }

    def solve_tabular(self, method):
        """Resuelve usando Simplex tabular: 'simplex' | 'bigM' | 'twophase'."""
        data = self._build_arrays()
        A_ub = data["A_ub"].tolist() if data["A_ub"] is not None else None
        b_ub = data["b_ub"].tolist() if data["b_ub"] is not None else None
        A_eq = data["A_eq"].tolist() if data["A_eq"] is not None else None
        b_eq = data["b_eq"].tolist() if data["b_eq"] is not None else None
        c = data["c"].tolist()
        result = solve_with_method(
            c, A_ub, b_ub, A_eq, b_eq, data["variables"], self.sense, method
        )
        style = "gauss" if method == "simplex" else "simplex"
        result["tableau_text"] = format_iterations(
            result.get("iterations", []), self.sense, style=style,
        )
        return result

    def vertices_2d(self):
        """Calcula los vértices factibles para problemas de 2 variables."""
        data = self._build_arrays()
        variables = data["variables"]
        if len(variables) != 2:
            return None, data
        cons = list(data["cons_parsed"])
        lines = []
        for lhs, op, rhs in cons:
            row = [lhs.get(variables[0], 0.0), lhs.get(variables[1], 0.0)]
            lines.append((row, rhs, op))
        lines.append(([1.0, 0.0], 0.0, ">="))
        lines.append(([0.0, 1.0], 0.0, ">="))

        pts = []
        n = len(lines)
        for i, j in combinations(range(n), 2):
            a1, b1, _ = lines[i]; a2, b2, _ = lines[j]
            M = np.array([a1, a2], dtype=float)
            v = np.array([b1, b2], dtype=float)
            if abs(np.linalg.det(M)) < 1e-9:
                continue
            try:
                p = np.linalg.solve(M, v)
            except np.linalg.LinAlgError:
                continue
            feasible = True
            for a, b, op in lines:
                val = a[0] * p[0] + a[1] * p[1]
                if op == "<=" and val > b + 1e-6:
                    feasible = False; break
                if op == ">=" and val < b - 1e-6:
                    feasible = False; break
                if op == "=" and abs(val - b) > 1e-6:
                    feasible = False; break
            if feasible:
                pts.append((float(p[0]), float(p[1])))

        unique = []
        for p in pts:
            if not any(abs(p[0] - q[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6 for q in unique):
                unique.append(p)
        if unique:
            cx = sum(p[0] for p in unique) / len(unique)
            cy = sum(p[1] for p in unique) / len(unique)
            unique.sort(key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))
        return unique, data
