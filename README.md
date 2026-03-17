# Documentation Algorithme Spline Quadratique C1

## Pseudo-code Exact Implémenté

L'algorithme dans `spline_core.py.interpolate()` suit *exactement* cette logique:

```
Début

// Étape 1 : calcul des intervalles
Pour i = 0 à n-1 faire
    h_i = x_{i+1} - x_i
Fin

// Étape 2 : initialisation
β_0 ← m0  // donné par user (slider GUI)

// Étape 3 : calcul des pentes β_i = S'(x_i)
Pour i = 0 à n-1 faire
    β_{i+1} = 2 * ((y_{i+1} - y_i) / h_i) - β_i
Fin

// Étape 4 : définition directe S_i(x) = y_i + β_i (x-x_i) + [(β_{i+1}-β_i)/(2 h_i)] (x-x_i)^2 (stock [y_i, β_i, c_i])

Pour i = 0 à n-1 faire
    c_i = (β_{i+1} - β_i) / (2 * h_i)
Fin  // direct no a b vars

// Fonction globale S(x): trouve i puis formule Étape 4
S(x) = S_i(x) si x ∈ [x_i, x_{i+1}]

Fin
```

## Preuves (exemple (0,0),(1,1),(2,0) m0=0)
- h=[1,1]
- β=[0, 2, -4]
- i=0: a=0 b=0 c=1 → x^2
- i=1: a=1 b=2 c=-3 → vérifié C1@1


**App 100% conforme**. `python main.py` pour tester.
