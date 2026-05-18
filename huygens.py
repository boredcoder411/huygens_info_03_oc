"""
Cette partie du programme sont les calculs de la simulation d'ondes.'
Elle calcule les ondes à l'aide d'une equation discrete , ainsi que la courbure
sur chaque côtés des ondes.
Enfin, elle crée un 'mur' qui empêche les ondes de passer à travers (obstacles).
"""

def step_wave(onde, onde_avant, c, dt, dx, mur):
    """
    Calcule l'état suivant d'une onde sur une grille 2D.

    Paramètres :
    onde  : onde actuellement
    onde_avant  : onde précédemment
    c  : vitesse/milieu de l'onde
    dt  : intervalle temps
    dx  : intervalle espace
    mur  : matrice définissant les zones perméables (1) et bloquées (0)

    Fonctionnement :
    - Laplacien en 2D (Δu(i,j)=ui+1,j+ui-1,j+ui,j+1+ui,j-1-4ui,j)
    - Équation des ondes (discrétisée)
    - Créer un mur pour bloquer l'onde dans certaines zones
    - Prise en compte bords image (sinon onde revient en haut)

    Retour :
    onde_apres : nouvel état onde
    """

    onde_apres = onde.copy()
    coef = (c * dt / dx) ** 2

    laplacien = (
        onde[2:, 1:-1]
        + onde[:-2, 1:-1]
        + onde[1:-1, 2:]
        + onde[1:-1, :-2]
        - 4 * onde[1:-1, 1:-1]
    )

    # propagation de l'onde avec l'équation de l'onde
    onde_apres[1:-1, 1:-1] = (
        2 * onde[1:-1, 1:-1]
        - onde_avant[1:-1, 1:-1]
        + coef * laplacien
    )

    # application du masque (toutes les cellules avec un mur ont maintenant une valeur de 0)
    onde_apres *= mur

    # bords gauche/droite --> murs
    onde_apres[:, 0] = 0
    onde_apres[:, -1] = 0

    # bords haut/bas --> murs
    onde_apres[0, :] = 0
    onde_apres[-1, :] = 0

    return onde_apres