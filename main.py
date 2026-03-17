"""
================================================================wide
Application Spline Quadratique C1 - Point d'entrée
================================================================
Auteur: DAGO DADJE ALEXANDRE

Description: Ce script lance l'interface graphique (GUI) permettant 
             de manipuler et visualiser des splines quadratiques 
             avec contrôle de la pente initiale (m0).

Modules requis :
- spline_core.py : Moteur de calcul mathématique.
- data_io.py     : Gestion de l'import/export (CSV, TXT).
- gui.py         : Interface utilisateur Tkinter & Matplotlib.
================================================================
"""

import tkinter as tk
import sys
from gui import SplineGUI

def main():
    try:
        # 1. Initialisation de la fenêtre racine
        root = tk.Tk()
        
        # 2. Configuration optionnelle de l'apparence au niveau OS
        # (Permet d'avoir une icône ou un titre par défaut avant le chargement du GUI)
        root.title("Analyseur de Splines Quadratiques")
        
        # 3. Lancement de l'interface
        # L'instance SplineGUI prend le contrôle de la fenêtre root
        app = SplineGUI(root)
        
        # 4. Boucle d'événements principale
        root.mainloop()
        
    except ImportError as e:
        print(f"Erreur : Dépendance manquante. {e}")
        print("Assurez-vous d'avoir installé : numpy et matplotlib.")
        sys.exit(1)
    except Exception as e:
        print(f"Une erreur inattendue est survenue au lancement : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()