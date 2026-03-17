import numpy as np
import os

def load_data(source):
    """
    Charge des points (xi, yi) depuis un fichier, une liste ou un array.
    Supporte CSV, TXT (délimiteurs: , ; tab ou espace).
    
    Returns:
        np.ndarray: Tableau (n, 2) trié par x croissant.
    """
    # 1. Gestion des entrées de type conteneur (List ou Array)
    if isinstance(source, (list, np.ndarray)):
        data = np.array(source)
    
    # 2. Gestion des fichiers
    elif isinstance(source, str):
        if not os.path.exists(source):
            raise FileNotFoundError(f"Le fichier '{source}' n'existe pas.")
        
        data = None
        # On teste d'abord avec genfromtxt qui est très flexible
        # autostrip=True et names=True permettent de gérer bcp de formats
        for d in [None, ',', ';', '\t']:
            try:
                # invalid_raise=False permet de sauter les lignes de texte (headers)
                data = np.genfromtxt(source, delimiter=d, invalid_raise=False)
                # Si on a chargé une seule colonne ou rien, on continue
                if data is not None and data.ndim == 2 and data.shape[1] >= 2:
                    break
            except Exception:
                continue
        
        if data is None or data.ndim < 2:
            raise ValueError("Format de fichier non reconnu ou colonnes insuffisantes (X, Y requis).")
    else:
        raise TypeError("La source doit être un chemin de fichier (str) ou une liste de points.")

    # 3. Nettoyage et Validation
    # On ne garde que les 2 premières colonnes au cas où il y en a plus
    points = data[:, :2]
    
    # Supprimer les lignes contenant des NaN (fréquent si header mal géré)
    points = points[~np.isnan(points).any(axis=1)]
    
    if len(points) < 2:
        raise ValueError("Le jeu de données doit contenir au moins 2 points valides.")

    # Tri par X croissant (indispensable pour les splines)
    points = points[np.argsort(points[:, 0])]
    
    # Vérification des doublons sur X (provoque une division par zéro en calcul de pente)
    if np.any(np.diff(points[:, 0]) <= 0):
        raise ValueError("Données invalides : deux points ont la même valeur X ou ne sont pas strictement croissants.")

    return points

def save_coeffs(spline, filename):
    """
    Sauvegarde les coefficients des polynômes quadratiques par intervalle.
    Format : [x_i, x_i+1] | ai*x^2 + bi*x + ci
    """
    try:
        coeffs = spline.get_coeffs() # Supposé retourner une liste de tuples (a, b, c)
        nodes = spline.x_nodes       # Les nœuds xi
    except AttributeError:
        raise ValueError("L'objet spline ne possède pas les attributs nécessaires (get_coeffs, x_nodes).")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{'Intervalle [x_i, x_i+1]':^25} | {'a':^12} | {'b':^12} | {'c':^12}\n")
        f.write("-" * 70 + "\n")
        
        for i in range(len(coeffs)):
            a, b, c = coeffs[i]
            x_start = nodes[i]
            x_end = nodes[i+1]
            interval = f"[{x_start:g}, {x_end:g}]"
            f.write(f"{interval:<25} | {a:12.6e} | {b:12.6e} | {c:12.6e}\n")
            
    print(f"✅ Coefficients exportés avec succès : {filename}")

def save_curve(spline, x_eval, filename):
    """
    Exporte la courbe calculée en format CSV standard.
    """
    try:
        y_eval = spline.evaluate(x_eval)
        # Empilement horizontal x et y
        output = np.column_stack((x_eval, y_eval))
        
        header = "x,y_spline"
        np.savetxt(filename, output, delimiter=',', header=header, fmt='%.8f', comments='')
        print(f"✅ Courbe exportée ({len(x_eval)} points) : {filename}")
    except Exception as e:
        raise IOError(f"Erreur lors de l'export de la courbe : {e}")

# --- Zone de test rapide ---
if __name__ == "__main__":
    # Test chargement manuel
    test_pts = [[0, 0], [2, 4], [1, 1]] # Désordonné
    print("Test Tri Manuel:", load_data(test_pts))