"""Module principal pour le calcul de splines quadratiques de classe C1.
Algo exact pseudo-code: recurrence β, eval directe formule S_i sans stock coeffs inutiles.
Objectif pédagogique: m0 influence."""

import numpy as np

class QuadraticSpline:
    def __init__(self, points, m0=0.0):
        """
        Construit spline C1.
        :param points: np.array (n,2) [x,y] croissant
        :param m0: β0 = S'(x0)
        Stocke x_nodes, beta pour eval directe.
        """
        self.x_nodes = points[:,0]
        self.y_nodes = points[:,1]
        self.m0 = m0
        n = len(self.x_nodes) - 1
        h = np.diff(self.x_nodes)
        
        # Vérifier que h[i] != 0
        if np.any(h == 0):
            raise ValueError("Points x consécutifs identiques détectés.")

        # Étape 3: pentes beta
        self.beta = np.zeros(n+1)
        self.beta[0] = float(m0)
        for i in range(n):
            dy_h = (self.y_nodes[i+1] - self.y_nodes[i]) / h[i]
            self.beta[i+1] = 2 * dy_h - self.beta[i]

    def evaluate(self, x_eval):
        """
        S(x) directe sans coeffs intermédiaires.
        Étape 6: trouve i, S_i(x) = y_i + β_i dx + [(β_{i+1}-β_i)/(2 h_i)] dx^2
        """
        y_eval = np.zeros_like(x_eval)
        for j, xx in enumerate(x_eval):
            i = np.searchsorted(self.x_nodes, xx) - 1
            if i < 0:
                if xx < self.x_nodes[0]:
                    raise ValueError(f"x={xx} hors [{self.x_nodes[0]:.3f},{self.x_nodes[-1]:.3f}]")
                i = 0
            if i >= len(self.x_nodes)-1:
                if xx > self.x_nodes[-1]:
                    raise ValueError(f"x={xx} hors [{self.x_nodes[0]:.3f},{self.x_nodes[-1]:.3f}]")
                i = len(self.x_nodes)-2
            hi = self.x_nodes[i+1] - self.x_nodes[i]
            dx = xx - self.x_nodes[i]
            ci = (self.beta[i+1] - self.beta[i]) / (2 * hi)
            y_eval[j] = (self.y_nodes[i] 
                         + self.beta[i] * dx 
                         + ci * dx**2)
        return y_eval

    def derivative(self, x_eval):
        """S'(x) analogue."""
        y_prime = np.zeros_like(x_eval)
        for j, xx in enumerate(x_eval):
            i = np.searchsorted(self.x_nodes, xx) - 1
            if i < 0:
                if xx < self.x_nodes[0]: continue
                i = 0
            if i >= len(self.x_nodes)-1:
                if xx > self.x_nodes[-1]: continue
                i = len(self.x_nodes)-2
            hi = self.x_nodes[i+1] - self.x_nodes[i]
            dx = xx - self.x_nodes[i]
            ci = (self.beta[i+1] - self.beta[i]) / (2 * hi)
            y_prime[j] = self.beta[i] + 2 * ci * dx
        return y_prime

    def get_coeffs(self):
        """Optionnel coeffs [y_i, β_i, c_i]"""
        n = len(self.x_nodes) - 1
        h = np.diff(self.x_nodes)
        coeffs = []
        for i in range(n):
            hi = h[i]
            ci = (self.beta[i+1] - self.beta[i]) / (2 * hi)
            coeffs.append([self.y_nodes[i], self.beta[i], ci])
        return coeffs

    @classmethod
    def approximate(cls, points, num_knots=None, m0=0.0, lambda_smooth=0.1):
        """Stub approx."""
        if num_knots is None:
            num_knots = max(3, len(points)//3)
        idx = np.linspace(0, len(points)-1, num_knots, dtype=int)
        return cls(points[idx], m0)

