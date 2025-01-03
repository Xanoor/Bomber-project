
def statistiques(g, stats_obj, timer: int, pv: int, points: int, level: int, SIZE: int, hauteur_stats: int):
    """
    Permet de créer des stats
    
    Args :
        stats_x (int) : Coordonées x de la zone de texte
        stats_y (int) : Cordonnées y de la zone de texte
        taille_stats (int) : Taille de la police d'écriture
    Return :
        None
    """
    #Message de statistique
    stats = f"⌚{timer} ❤️: {pv} Points: {points} Niveau: {level}"

    largeur_stats = (len(stats)*SIZE)/3

    if stats_obj is not None:
        g.changerTexte(stats_obj, stats)
    else:
        stats_obj = g.afficherTexte(stats, largeur_stats, hauteur_stats, 'white', SIZE)
    return stats_obj
