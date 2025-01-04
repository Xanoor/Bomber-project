from config import LARGEUR, HAUTEUR, keys

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

def show_game_result(g: object, gameover: bool) -> str:
        if gameover:
            final_message = "GAME OVER"
        else:
            final_message = "YOU WIN"
        size_text = 40
        longueur_rect, largeur_rect = size_text * len(final_message), size_text
        x_rect = LARGEUR/2 - (longueur_rect/2)
        y_rect = HAUTEUR/2 - (largeur_rect / 2)
        g.dessinerRectangle(x_rect, y_rect, longueur_rect, largeur_rect, "gray")
        g.afficherTexte(final_message, LARGEUR/2, HAUTEUR/2, "white", size_text)
        return endGameOptions(g)


def endGameOptions(g: object) -> str:
    g.afficherTexte("RECOMMENCER ? (Espace)", LARGEUR/4, HAUTEUR/1.5, "white", 20)
    g.afficherTexte("ARRÊTER ? (Echap)", LARGEUR/1.25, HAUTEUR/1.5, "white", 20)
    key = None
    choice = {keys["play_again"]: "play_again", keys["quit"]: "quit"}
    while True:
        key = g.attendreTouche().lower()
        if key in choice: 
            g.fermerFenetre()
            return choice[key]