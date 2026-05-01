import re


def parse_expression(expr):
    """Parsea 'a*x + b*y - c' a un dict {var: coef, '__const__': k}."""
    if not expr or not expr.strip():
        raise ValueError("Expresión vacía.")
    s = expr.replace(" ", "").replace("\t", "")
    s = s.replace("-", "+-")
    if s.startswith("+"):
        s = s[1:]
    terms = [t for t in s.split("+") if t]
    coefs = {"__const__": 0.0}
    pat = re.compile(r"^([+-]?\d*\.?\d*)\*?([a-zA-Z_][a-zA-Z0-9_]*)?$")
    for term in terms:
        m = pat.match(term)
        if not m:
            raise ValueError(f"Término inválido: '{term}'")
        coef_str, var = m.groups()
        if coef_str in ("", "+", None):
            coef = 1.0
        elif coef_str == "-":
            coef = -1.0
        else:
            coef = float(coef_str)
        if var is None:
            coefs["__const__"] += coef
        else:
            coefs[var] = coefs.get(var, 0.0) + coef
    return coefs


def parse_constraint(line):
    """Parsea '2x + y <= 10' devolviendo (lhs_coefs, op, rhs)."""
    line = line.strip()
    for op in ("<=", ">=", "==", "=", "<", ">"):
        idx = line.find(op)
        if idx >= 0:
            lhs, rhs = line[:idx], line[idx + len(op):]
            lhs_coefs = parse_expression(lhs)
            rhs_coefs = parse_expression(rhs)
            const_lhs = lhs_coefs.pop("__const__", 0.0)
            const_rhs = rhs_coefs.pop("__const__", 0.0)
            for v, c in rhs_coefs.items():
                lhs_coefs[v] = lhs_coefs.get(v, 0.0) - c
            rhs_val = const_rhs - const_lhs
            normalized = "<=" if op in ("<=", "<") else (">=" if op in (">=", ">") else "=")
            return lhs_coefs, normalized, rhs_val
    raise ValueError(f"Restricción sin operador (<=, >=, =): '{line}'")
