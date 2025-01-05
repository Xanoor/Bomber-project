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

def show_game_result(g: object, points: int) -> str:
        """
        Fonction de fin de jeu affichant le score final.

        Args :
            g (object) : Notre fenêtre.
            points (int) : Points du joueur à la fin de la partie.
        Return :
            choice[key] (str) : choix de fin de jeu retourné par la fonction endGameOptions.
        """
        final_message = "GAME OVER"
        size_text = 40
        longueur_rect, largeur_rect = size_text * len(final_message), size_text * 3
        x_rect, y_rect = LARGEUR/2 - (longueur_rect/2), HAUTEUR/2 - (largeur_rect / 2)
        g.dessinerRectangle(x_rect, y_rect, longueur_rect, largeur_rect, "gray")
        g.afficherTexte(final_message + "\nScore : " + str(points), LARGEUR/2, HAUTEUR/2, "white", size_text, "center")
        return endGameOptions(g)


def endGameOptions(g: object) -> str:
    """
    Fonction permettant de recommencer ou d'arrêter la partie.

    Args :
        g (object) : Notre fenêtre.
    Return :
        choice[key] (str) : choix de fin de jeu retourné par la fonction endGameOptions.
    """
    g.afficherTexte("RECOMMENCER ? (Espace)", LARGEUR/4, HAUTEUR/1.5, "white", 20)
    g.afficherTexte("ARRÊTER ? (Echap)", LARGEUR/1.25, HAUTEUR/1.5, "white", 20)
    key = None
    choice = {keys["play again"]: "play again", keys["quit"]: "quit"}
    while True:
        key = g.attendreTouche().lower()
        if key in choice: 
            g.fermerFenetre()
            return choice[key]