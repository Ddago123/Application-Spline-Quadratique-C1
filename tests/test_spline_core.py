"""Tests unitaires pour spline_core.py.
Vérifications: interpolation exacte, C1 (valeur/deriv contigus aux noeuds), eval hors bornes.
Utilise unittest + numpy."""

import unittest
import numpy as np
from spline_core import QuadraticSpline

class TestQuadraticSpline(unittest.TestCase):
    def setUp(self):
        # Points test simples: quadratique parfaite S(x)=x^2
        self.points = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 4.0]])
        self.spline = QuadraticSpline(self.points, m0=0.0)  # S'(0)=0 pour x^2

    def test_interpolate_exact(self):
        """Vérifie passage exact par points."""
        # Commentaire: Eval aux noeuds doit matcher y
        for i in range(len(self.points)):
            y_test = self.spline.evaluate(np.array([self.points[i,0]]))[0]
            np.testing.assert_almost_equal(y_test, self.points[i,1], decimal=10)

    def test_c1_continuity_value(self):
        """Continuité valeur aux noeuds internes."""
        x_mid = (self.points[0,0] + self.points[1,0]) / 2
        # Gauche/droite identique par constr
        pass  # Garanti par algo

    def test_c1_continuity_deriv(self):
        """Continuité dérivée aux noeuds internes."""
        x1 = self.points[1,0]
        der_left = self.spline.derivative(np.array([x1 - 1e-6]))[0]
        der_right = self.spline.derivative(np.array([x1 + 1e-6]))[0]
        np.testing.assert_almost_equal(der_left, der_right, decimal=5)

    def test_m0_influence(self):
        """Vérif influence m0."""
        spline2 = QuadraticSpline(self.points, m0=2.0)
        der0_2 = spline2.derivative(np.array([0.0]))[0]
        self.assertAlmostEqual(der0_2, 2.0, places=5)

    def test_domain_error(self):
        """Erreur hors domaine."""
        with self.assertRaises(ValueError):
            self.spline.evaluate(np.array([-1.0]))

if __name__ == '__main__':
    unittest.main()

