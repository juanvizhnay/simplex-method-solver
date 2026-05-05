import customtkinter as ctk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from solver import LPSolver

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_DARK = "#0a1929"
BG_PANEL = "#0f2540"
BG_INPUT = "#0c1c33"
ACCENT = "#1976d2"
ACCENT_HOVER = "#2196f3"
ACCENT_DEEP = "#0d47a1"
TEXT = "#e3f2fd"
TEXT_MUTED = "#90caf9"
DANGER = "#b71c1c"
DANGER_HOVER = "#e53935"


class SimplexApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Solver de Programación Lineal — Simplex / Gráfico")
        self.geometry("1280x820")
        self.minsize(1080, 700)
        self.configure(fg_color=BG_DARK)
        self.solver = LPSolver()
        self.constraint_entries = []
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="◆  PROGRAMACIÓN LINEAL",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT,
        ).pack(side="left", padx=24, pady=18)
        ctk.CTkLabel(
            header, text="Método Simplex  ·  Método Gráfico",
            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED,
        ).pack(side="left", padx=10)

        body = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        left = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=14, width=460)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)
        self._build_input_panel(left)

        right = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=14)
        right.pack(side="right", fill="both", expand=True)
        self._build_output_panel(right)

    def _build_input_panel(self, parent):
        ctk.CTkLabel(
            parent, text="Datos del problema",
            font=ctk.CTkFont(size=17, weight="bold"), text_color=TEXT,
        ).pack(pady=(18, 10), anchor="w", padx=22)

        sense_frame = ctk.CTkFrame(parent, fg_color="transparent")
        sense_frame.pack(fill="x", padx=22, pady=4)
        ctk.CTkLabel(sense_frame, text="Tipo:", text_color=TEXT, width=70, anchor="w").pack(side="left")
        self.sense_var = ctk.StringVar(value="Maximizar")
        ctk.CTkOptionMenu(
            sense_frame, values=["Maximizar", "Minimizar"], variable=self.sense_var,
            fg_color=ACCENT, button_color=ACCENT_DEEP, button_hover_color=ACCENT_HOVER,
            text_color=TEXT, width=180,
        ).pack(side="left", padx=8)

        method_frame = ctk.CTkFrame(parent, fg_color="transparent")
        method_frame.pack(fill="x", padx=22, pady=(8, 0))
        ctk.CTkLabel(method_frame, text="Método:", text_color=TEXT, width=70, anchor="w").pack(side="left")
        self.method_var = ctk.StringVar(value="Simplex estándar (tabular)")
        ctk.CTkOptionMenu(
            method_frame,
            values=[
                "Auto (HiGHS)",
                "Simplex estándar (tabular)",
                "M Grande (tabular)",
                "Dos Fases (tabular)",
            ],
            variable=self.method_var,
            fg_color=ACCENT, button_color=ACCENT_DEEP, button_hover_color=ACCENT_HOVER,
            text_color=TEXT, width=240,
        ).pack(side="left", padx=8)

        ctk.CTkLabel(parent, text="Función objetivo   Z =", text_color=TEXT).pack(
            anchor="w", padx=22, pady=(14, 2)
        )
        self.obj_entry = ctk.CTkEntry(
            parent, placeholder_text="ej:  3x + 5y",
            fg_color=BG_INPUT, border_color=ACCENT, text_color=TEXT, height=36,
        )
        self.obj_entry.pack(fill="x", padx=22, pady=2)
        self.obj_entry.insert(0, "3x + 5y")

        z_frame = ctk.CTkFrame(parent, fg_color="transparent")
        z_frame.pack(fill="x", padx=22, pady=(12, 4))
        self.use_z_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            z_frame, text="Usar valor de Z definido", variable=self.use_z_var,
            text_color=TEXT, fg_color=ACCENT, hover_color=ACCENT_HOVER, border_color=ACCENT,
        ).pack(side="left")
        self.z_entry = ctk.CTkEntry(
            z_frame, placeholder_text="Z =", width=110,
            fg_color=BG_INPUT, border_color=ACCENT, text_color=TEXT,
        )
        self.z_entry.pack(side="right")

        ctk.CTkLabel(
            parent, text="Restricciones",
            text_color=TEXT, font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(16, 2))
        ctk.CTkLabel(
            parent, text="(operadores válidos:  <=    >=    = )",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=22)

        self.cons_frame = ctk.CTkScrollableFrame(
            parent, fg_color=BG_INPUT, corner_radius=10, height=220,
            scrollbar_button_color=ACCENT, scrollbar_button_hover_color=ACCENT_HOVER,
        )
        self.cons_frame.pack(fill="both", expand=False, padx=22, pady=10)

        self._add_constraint("2x + 3y <= 18")
        self._add_constraint("2x + y <= 10")
        self._add_constraint("x + 3y <= 12")

        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", padx=22, pady=4)
        ctk.CTkButton(
            btn_row, text="+  Añadir restricción", command=lambda: self._add_constraint(""),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT,
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(
            btn_row, text="Limpiar", command=self._clear_constraints,
            fg_color="#37474f", hover_color="#546e7a", text_color=TEXT,
        ).pack(side="right", expand=True, fill="x", padx=(4, 0))

        ctk.CTkLabel(parent, text="").pack()
        ctk.CTkButton(
            parent, text="▶   Resolver con Simplex", height=46,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT,
            command=self.solve_simplex,
        ).pack(fill="x", padx=22, pady=(6, 4))
        ctk.CTkButton(
            parent, text="📈   Resolver gráficamente", height=46,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT_DEEP, hover_color=ACCENT, text_color=TEXT,
            command=self.solve_graphical,
        ).pack(fill="x", padx=22, pady=4)

    def _add_constraint(self, default=""):
        row = ctk.CTkFrame(self.cons_frame, fg_color="transparent")
        row.pack(fill="x", pady=4)
        entry = ctk.CTkEntry(
            row, placeholder_text="ej:  2x + y <= 10",
            fg_color=BG_PANEL, border_color=ACCENT, text_color=TEXT, height=32,
        )
        entry.pack(side="left", fill="x", expand=True)
        if default:
            entry.insert(0, default)
        ctk.CTkButton(
            row, text="✕", width=32, height=32,
            fg_color=DANGER, hover_color=DANGER_HOVER, text_color=TEXT,
            command=lambda: self._remove_constraint(row, entry),
        ).pack(side="right", padx=(8, 0))
        self.constraint_entries.append(entry)

    def _remove_constraint(self, row, entry):
        if entry in self.constraint_entries:
            self.constraint_entries.remove(entry)
        row.destroy()

    def _clear_constraints(self):
        for e in list(self.constraint_entries):
            e.master.destroy()
        self.constraint_entries.clear()

    def _build_output_panel(self, parent):
        self.tabs = ctk.CTkTabview(
            parent, fg_color=BG_DARK,
            segmented_button_fg_color=BG_PANEL,
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color=BG_PANEL,
            segmented_button_unselected_hover_color=ACCENT_DEEP,
            text_color=TEXT,
        )
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)
        self.tabs.add("Resultados")
        self.tabs.add("Gráfico")

        self.result_text = ctk.CTkTextbox(
            self.tabs.tab("Resultados"), fg_color=BG_PANEL, text_color=TEXT,
            font=ctk.CTkFont(family="Consolas", size=13),
            scrollbar_button_color=ACCENT,
        )
        self.result_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.result_text.insert(
            "1.0",
            "Ingrese una función objetivo, marque maximizar o minimizar,\n"
            "añada las restricciones y pulse «Resolver con Simplex»\n"
            "o «Resolver gráficamente» (solo 2 variables).\n",
        )

        self.graph_frame = ctk.CTkFrame(self.tabs.tab("Gráfico"), fg_color=BG_PANEL)
        self.graph_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas = None

    def _collect(self):
        self.solver.objective = self.obj_entry.get().strip()
        self.solver.constraints = [e.get() for e in self.constraint_entries if e.get().strip()]
        self.solver.sense = "max" if self.sense_var.get() == "Maximizar" else "min"
        if self.use_z_var.get() and self.z_entry.get().strip():
            try:
                self.solver.target_z = float(self.z_entry.get())
            except ValueError:
                self.solver.target_z = None
        else:
            self.solver.target_z = None

    def solve_simplex(self):
        try:
            self._collect()
            if not self.solver.objective:
                messagebox.showerror("Error", "Ingrese una función objetivo.")
                return
            if not self.solver.constraints:
                messagebox.showerror("Error", "Añada al menos una restricción.")
                return
            choice = self.method_var.get()
            method_map = {
                "Auto (HiGHS)": None,
                "Simplex estándar (tabular)": "simplex",
                "M Grande (tabular)": "bigM",
                "Dos Fases (tabular)": "twophase",
            }
            tab_method = method_map.get(choice)
            if tab_method is None:
                res = self.solver.solve_simplex()
                self._render_result(res, method="HiGHS (linprog)")
            else:
                res = self.solver.solve_tabular(tab_method)
                label = {"simplex": "Simplex estándar",
                         "bigM": "M Grande",
                         "twophase": "Dos Fases"}[tab_method]
                self._render_result(res, method=label, tabular=True)
            self.tabs.set("Resultados")
        except Exception as e:
            messagebox.showerror("Error de entrada", str(e))

    def solve_graphical(self):
        try:
            self._collect()
            if not self.solver.objective:
                messagebox.showerror("Error", "Ingrese una función objetivo.")
                return
            if not self.solver.constraints:
                messagebox.showerror("Error", "Añada al menos una restricción.")
                return
            verts, data = self.solver.vertices_2d()
            if verts is None:
                messagebox.showerror(
                    "Método gráfico",
                    f"Requiere exactamente 2 variables. Detectadas: {len(data['variables'])}",
                )
                return
            res = self.solver.solve_simplex()
            self._render_result(res, method="Gráfico", verts=verts, data=data)
            self._draw_graph(verts, data, res)
            self.tabs.set("Gráfico")
        except Exception as e:
            messagebox.showerror("Error de entrada", str(e))

    def _render_result(self, res, method, verts=None, data=None, tabular=False):
        self.result_text.delete("1.0", "end")
        out = []
        out.append(f"═══════ MÉTODO {method.upper()} ═══════\n")
        out.append(f"Tipo de problema: {self.sense_var.get()}")
        out.append(f"Z = {self.solver.objective}")
        out.append("Sujeto a:")
        for c in self.solver.constraints:
            out.append(f"   {c}")
        out.append("   x_i >= 0")
        out.append("")

        if verts is not None and data is not None:
            variables = data["variables"]
            c = data["c"]
            out.append("─── Vértices de la región factible ───")
            if not verts:
                out.append("   (no hay región factible)")
            else:
                for p in verts:
                    zv = c[0] * p[0] + c[1] * p[1]
                    out.append(
                        f"   ({variables[0]}={p[0]:.4f}, {variables[1]}={p[1]:.4f})   →   Z = {zv:.4f}"
                    )
            out.append("")

        if tabular and res.get("tableau_text"):
            out.append("─── DESARROLLO PASO A PASO ───")
            out.append(res["tableau_text"])
            out.append("")
            if "phase1_W" in res:
                out.append(f"   Fase 1 finaliza con W = {res['phase1_W']:.4f}")
                out.append("")

        if not res["ok"]:
            out.append(f"❌ No se encontró solución óptima.")
            out.append(f"   Motivo: {res['msg']}")
        else:
            out.append("─────────  SOLUCIÓN ÓPTIMA  ─────────")
            for v, val in res["values"].items():
                out.append(f"   {v} = {val:.4f}")
            out.append("")
            out.append(f"   Z* = {res['z']:.4f}")

            if self.solver.target_z is not None:
                out.append("")
                out.append("─── Comparación con Z definido ───")
                out.append(f"   Z objetivo  = {self.solver.target_z}")
                out.append(f"   Z óptimo    = {res['z']:.4f}")
                diff = res["z"] - self.solver.target_z
                out.append(f"   Diferencia  = {diff:+.4f}")
                if self.solver.sense == "max" and self.solver.target_z > res["z"] + 1e-6:
                    out.append("   ⚠ El Z objetivo es INALCANZABLE (mayor que el óptimo).")
                elif self.solver.sense == "min" and self.solver.target_z < res["z"] - 1e-6:
                    out.append("   ⚠ El Z objetivo es INALCANZABLE (menor que el óptimo).")
                else:
                    out.append("   ✓ El Z objetivo es alcanzable dentro de la región factible.")

        self.result_text.insert("1.0", "\n".join(out))

    def _draw_graph(self, verts, data, res):
        for w in self.graph_frame.winfo_children():
            w.destroy()

        variables = data["variables"]
        cons_parsed = data["cons_parsed"]
        c = data["c"]

        fig = Figure(figsize=(7, 5), facecolor=BG_PANEL)
        ax = fig.add_subplot(111, facecolor=BG_DARK)
        ax.tick_params(colors=TEXT)
        for spine in ax.spines.values():
            spine.set_color(TEXT_MUTED)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)

        if verts:
            xs = [p[0] for p in verts]
            ys = [p[1] for p in verts]
            xmax = max(xs + [1.0]) * 1.4 + 1
            ymax = max(ys + [1.0]) * 1.4 + 1
        else:
            xmax = ymax = 10.0
        x = np.linspace(0, xmax, 400)

        palette = ["#42a5f5", "#26c6da", "#66bb6a", "#ef5350",
                   "#ab47bc", "#ffa726", "#ec407a", "#7e57c2"]
        for i, (lhs, op, rhs) in enumerate(cons_parsed):
            a = lhs.get(variables[0], 0.0)
            b = lhs.get(variables[1], 0.0)
            label = f"{a:g}{variables[0]} + {b:g}{variables[1]} {op} {rhs:g}"
            col = palette[i % len(palette)]
            if abs(b) > 1e-9:
                y = (rhs - a * x) / b
                ax.plot(x, y, color=col, label=label, linewidth=2)
            elif abs(a) > 1e-9:
                ax.axvline(rhs / a, color=col, label=label, linewidth=2)

        if verts and len(verts) >= 3:
            poly_x = [p[0] for p in verts] + [verts[0][0]]
            poly_y = [p[1] for p in verts] + [verts[0][1]]
            ax.fill(poly_x, poly_y, color=ACCENT, alpha=0.28, label="Región factible")

        for p in verts:
            ax.plot(p[0], p[1], "o", color="#fff176", markersize=7)
            zv = c[0] * p[0] + c[1] * p[1]
            ax.annotate(
                f"({p[0]:.2f}, {p[1]:.2f})\nZ={zv:.2f}",
                (p[0], p[1]), textcoords="offset points", xytext=(8, 8),
                fontsize=8, color=TEXT,
            )

        if res["ok"] and len(variables) == 2:
            ox = res["values"][variables[0]]
            oy = res["values"][variables[1]]
            ax.plot(ox, oy, "*", color="#ff5722", markersize=22,
                    label=f"Óptimo  Z*={res['z']:.2f}")

        if self.solver.target_z is not None and abs(c[1]) > 1e-9:
            yz = (self.solver.target_z - c[0] * x) / c[1]
            ax.plot(x, yz, "--", color="#fff176", linewidth=1.8,
                    label=f"Z = {self.solver.target_z}")

        ax.set_xlim(0, xmax)
        ax.set_ylim(0, ymax)
        ax.set_xlabel(variables[0])
        ax.set_ylabel(variables[1])
        ax.set_title("Método Gráfico — Región Factible")
        ax.grid(True, alpha=0.2, color=TEXT_MUTED)
        leg = ax.legend(
            loc="upper right", fontsize=8,
            facecolor=BG_PANEL, edgecolor=TEXT_MUTED, labelcolor=TEXT,
        )
        if leg:
            leg.get_frame().set_alpha(0.9)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas = canvas
