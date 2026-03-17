import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Import des modules personnalisés (supposés existants)
try:
    from spline_core import QuadraticSpline
    from data_io import load_data, save_coeffs, save_curve
except ImportError:
    # Fallback pour démonstration si modules manquants
    class QuadraticSpline:
        def __init__(self, points, m0): self.points = points; self.m0 = m0
        def evaluate(self, x): return np.interp(x, self.points[:,0], self.points[:,1])
        @staticmethod
        def approximate(p, k, m0): return QuadraticSpline(p, m0)

class SplineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyseur de Splines Quadratiques C1 - Mr. DAGO DADJÉ ALEXANDRE")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # État des données
        self.points = np.array([[0.0, 0.0], [2.0, 3.0], [5.0, 2.0], [8.0, 5.0]])
        self.spline = None
        
        self.setup_styles()
        self.setup_ui()
        self.init_plot()
        self.update_listbox()
        self.compute_spline() # Premier calcul auto

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("Action.TButton", font=('Helvetica', 10, 'bold'))
        self.style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))

    def setup_ui(self):
        # PanedWindow pour séparer contrôles et graphique
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # --- FRAME GAUCHE (CONTRÔLES) ---
        self.left_panel = ttk.Frame(self.paned, padding="10")
        self.paned.add(self.left_panel, weight=1)

        # Section Données
        ttk.Label(self.left_panel, text="Points de contrôle (x, y)", style="Header.TLabel").pack(fill=tk.X, pady=5)
        
        list_frame = ttk.Frame(self.left_panel)
        list_frame.pack(fill=tk.BOTH, expand=False)
        
        self.points_listbox = tk.Listbox(list_frame, height=10, font=("Consolas", 10))
        self.points_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.points_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.points_listbox.config(yscrollcommand=scrollbar.set)

        btn_grid = ttk.Frame(self.left_panel)
        btn_grid.pack(fill=tk.X, pady=5)
        ttk.Button(btn_grid, text="Ajouter", command=self.add_point_dialog).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(btn_grid, text="Modifier", command=self.edit_point_dialog).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(btn_grid, text="Suppr.", command=self.del_point).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(self.left_panel, text="📂 Charger Fichier (CSV/TXT)", command=self.load_file).pack(fill=tk.X, pady=2)

        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=15)

        # Section Paramètres
        ttk.Label(self.left_panel, text="Configuration", style="Header.TLabel").pack(fill=tk.X, pady=5)
        
        # Mode
        mode_frame = ttk.LabelFrame(self.left_panel, text="Mode de calcul", padding=5)
        mode_frame.pack(fill=tk.X, pady=5)
        self.mode_var = tk.StringVar(value="interp")
        ttk.Radiobutton(mode_frame, text="Interpolation", variable=self.mode_var, value="interp", command=self.on_param_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Approximation", variable=self.mode_var, value="approx", command=self.on_param_change).pack(side=tk.LEFT)

        # Slider m0 (Interactivité Live)
        ttk.Label(self.left_panel, text="Pente initiale (m0) :").pack(anchor=tk.W, pady=(10, 0))
        self.m0_var = tk.DoubleVar(value=0.0)
        self.m0_scale = ttk.Scale(self.left_panel, from_=-10.0, to=10.0, orient=tk.HORIZONTAL, 
                                 variable=self.m0_var, command=lambda _: self.compute_spline())
        self.m0_scale.pack(fill=tk.X, pady=5)
        ttk.Label(self.left_panel, textvariable=self.m0_var).pack(anchor=tk.E)

        # Paramètres Approximation
        self.approx_frame = ttk.LabelFrame(self.left_panel, text="Paramètres Approx.", padding=5)
        # On ne l'affiche que si mode == approx
        self.knots_var = tk.IntVar(value=5)
        ttk.Label(self.approx_frame, text="Nb Noeuds:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.approx_frame, textvariable=self.knots_var, width=8).grid(row=0, column=1, padx=5)

        # Section Export
        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=15)
        ttk.Button(self.left_panel, text="💾 Exporter Coefficients", command=self.export_coeffs).pack(fill=tk.X, pady=2)
        ttk.Button(self.left_panel, text="📊 Exporter Courbe (CSV)", command=self.export_curve).pack(fill=tk.X, pady=2)

        # --- FRAME DROITE (PLOT) ---
        self.right_panel = ttk.Frame(self.paned, padding="10")
        self.paned.add(self.right_panel, weight=4)
        
    def init_plot(self):
        """Initialise la figure Matplotlib une seule fois."""
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Barre d'outils
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.right_panel)
        self.toolbar.update()
        
        # Objets graphiques vides
        self.line_spline, = self.ax.plot([], [], 'b-', lw=2, label="Spline Q.")
        self.line_points, = self.ax.plot([], [], 'ro', markersize=6, label="Points")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()

    def update_listbox(self):
        self.points_listbox.delete(0, tk.END)
        for i, p in enumerate(self.points):
            self.points_listbox.insert(tk.END, f"{i:02d} | x: {p[0]:.3f} | y: {p[1]:.3f}")

    def on_param_change(self):
        """Gère l'affichage dynamique des options selon le mode."""
        if self.mode_var.get() == "approx":
            self.approx_frame.pack(fill=tk.X, pady=5)
        else:
            self.approx_frame.pack_forget()
        self.compute_spline()

    def compute_spline(self):
        """Recalcule la spline et rafraîchit le graphique sans reconstruire l'objet Canvas."""
        if len(self.points) < 3:
            return

        try:
            m0 = self.m0_var.get()
            # Calcul de la spline
            if self.mode_var.get() == "interp":
                self.spline = QuadraticSpline(self.points, m0)
            else:
                self.spline = QuadraticSpline.approximate(self.points, self.knots_var.get(), m0)

            # Préparation des données pour le plot (domaine valide uniquement)
            x_min, x_max = self.points[:, 0].min(), self.points[:, 0].max()
            x_eval = np.linspace(x_min, x_max, 200)
            y_eval = self.spline.evaluate(x_eval)

            # Mise à jour rapide des lignes
            self.line_spline.set_data(x_eval, y_eval)
            self.line_points.set_data(self.points[:, 0], self.points[:, 1])
            
            # Ajustement auto des axes
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Erreur calcul: {e}")

    # --- DIALOGUES ---
    def add_point_dialog(self):
        self._point_window("Ajouter un point", lambda x, y: self._add_point_logic(x, y))

    def edit_point_dialog(self):
        sel = self.points_listbox.curselection()
        if not sel: return
        idx = sel[0]
        px, py = self.points[idx]
        self._point_window("Modifier point", lambda x, y: self._edit_point_logic(idx, x, y), px, py)

    def _point_window(self, title, callback, def_x=0.0, def_y=0.0):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("250x150")
        win.transient(self.root)
        win.grab_set()

        content = ttk.Frame(win, padding=10)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="X:").grid(row=0, column=0, pady=5)
        ex = ttk.Entry(content); ex.insert(0, str(def_x)); ex.grid(row=0, column=1)
        
        ttk.Label(content, text="Y:").grid(row=1, column=0, pady=5)
        ey = ttk.Entry(content); ey.insert(0, str(def_y)); ey.grid(row=1, column=1)

        def validate():
            try:
                callback(float(ex.get()), float(ey.get()))
                win.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Entrez des nombres valides")

        ttk.Button(content, text="Valider", command=validate).grid(row=2, column=0, columnspan=2, pady=10)

    def _add_point_logic(self, x, y):
        new_points = np.vstack([self.points, [x, y]])
        self.points = new_points[np.argsort(new_points[:, 0])]
        self.update_listbox()
        self.compute_spline()

    def _edit_point_logic(self, idx, x, y):
        self.points[idx] = [x, y]
        self.points = self.points[np.argsort(self.points[:, 0])]
        self.update_listbox()
        self.compute_spline()

    def del_point(self):
        sel = self.points_listbox.curselection()
        if sel and len(self.points) > 3:
            self.points = np.delete(self.points, sel[0], axis=0)
            self.update_listbox()
            self.compute_spline()
        else:
            messagebox.showwarning("Attention", "Il faut au moins 3 points.")

    # --- I/O ---
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Data files", "*.txt *.csv")])
        if path:
            try:
                # data_io.load_data doit renvoyer un np.array
                self.points = load_data(path)
                self.update_listbox()
                self.compute_spline()
            except Exception as e:
                messagebox.showerror("Erreur de chargement", str(e))

    def export_coeffs(self):
        if self.spline:
            path = filedialog.asksaveasfilename(defaultextension=".txt")
            if path: save_coeffs(self.spline, path)

    def export_curve(self):
        if self.spline:
            path = filedialog.asksaveasfilename(defaultextension=".csv")
            if path:
                x = np.linspace(self.points[:,0].min(), self.points[:,0].max(), 500)
                save_curve(self.spline, x, path)

if __name__ == "__main__":
    root = tk.Tk()
    app = SplineGUI(root)
    root.mainloop()