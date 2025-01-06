from config import LARGEUR, HAUTEUR, keys, Textures_HUD

def defaultUIIcons(g:object, SIZE:int):
    """
    Permet d'afficher des images pour le HUD, tel que l'image pour la vie, pour le timer...
    Args:
        g (object) : Fenêtre tkinter.
        SIZE (int) : Taille d'une case
    """
    if not isinstance(g, object) or type(SIZE) != int:
         raise TypeError("defaultUIIcons : La variable g ou SIZE n'est pas dans le bon format !")
    Y_POS = SIZE-(SIZE//2)

    g.afficherImage(SIZE, Y_POS, (SIZE, SIZE), Textures_HUD["timer"])
    g.afficherImage(SIZE*6, Y_POS, (SIZE, SIZE), Textures_HUD["coeur"])

def statistiques(g: object, timer_obj: object|None, stats_obj: object|None, timer: int, pv: int, points: int, level: int, SIZE: int) -> tuple[object, object]:
    """
    Met à jour ou crée les objets d'affichage des statistiques du jeu.

    Cette fonction gère l'affichage des statistiques du jeu (temps, points, points de vie, niveau) 
    sur l'interface graphique. 
    Si les objets `timer_obj` et `stats_obj` existent déjà, leurs textes sont mis à jour. 
    Sinon, de nouveaux objets graphiques sont créés.

    Args:
        g (object) : Instance de fenêtre tkinter.
        timer_obj (object | None): Objet graphique existant pour afficher le temps, ou None s'il doit être créé.
        stats_obj (object | None): Objet graphique existant pour afficher les statistiques, ou None s'il doit être créé.
        timer (int): Temps restant.
        pv (int): Points de vie du joueur.
        points (int): Score actuel du joueur.
        level (int): Niveau actuel du joueur.
        SIZE (int): Taille de base pour les éléments graphiques (utilisée pour les positions et la taille du texte).
    Returns:
        tuple[object, object]: Les objets graphiques mis à jour ou nouvellement créés pour le temps et les statistiques.
    """

    if not isinstance(g, object) or type(SIZE) != int:
         raise TypeError("defaultUIIcons : La variable g ou SIZE n'est pas dans le bon format !")

    #Message de statistique
    stats = f"{pv}      Points: {points}      Niveau: {level}"
    Y_POS = SIZE-(SIZE//2)
    FONT_SIZE = SIZE-(SIZE//3)

    if stats_obj is not None and timer_obj is not None:
        g.changerTexte(timer_obj, timer)
        g.changerTexte(stats_obj, stats)
    else:
        timer_obj = g.afficherTexte(timer, SIZE*2, Y_POS, 'white', FONT_SIZE, ancre="nw")   #Création du texte du timer SIZE*2 permet de créer une marge
        stats_obj = g.afficherTexte(stats, SIZE*7.2, Y_POS, 'white', FONT_SIZE, ancre="nw") #Création du texte des stats SIZE*7.2 permet de créer une marge

    return timer_obj, stats_obj

def showGameResult(g: object, points: int) -> str:
        """
        Affiche le score final et termine le jeu.

        Cette fonction affiche un écran de fin de jeu avec le message "GAME OVER" 
        et le score du joueur, puis propose des options de fin de partie.
        Args :
            g (object) : Instance de fenêtre tkinter.
            points (int) : Points du joueur à la fin de la partie.
        Return :
            str: Le choix de fin de jeu retourné par la fonction endGameOptions.
        """
        MESSAGE = "GAME OVER"
        FONT_SIZE = 40
        SIZE_X, SIZE_Y = FONT_SIZE * len(MESSAGE), FONT_SIZE * 3
        X_RECT, Y_RECT = LARGEUR/2 - (SIZE_X/2), HAUTEUR/2 - (SIZE_Y / 2)

        g.dessinerRectangle(X_RECT, Y_RECT, SIZE_X, SIZE_Y, "gray")
        g.afficherTexte(MESSAGE + "\nScore : " + str(points), LARGEUR/2, HAUTEUR/2, "white", FONT_SIZE, "center")
        return endGameOptions(g)


def endGameOptions(g: object) -> str:
    """
    Affiche les options de fin de partie et attend la sélection de l'utilisateur.

    Cette fonction affiche trois options à l'écran : recommencer, arrêter ou changer de mode, 
    puis attend que l'utilisateur fasse un choix via une touche du clavier. Le choix est 
    retourné sous forme d'une chaîne de caractères.

    Args:
        g (object) : Instance de fenêtre tkinter.
    Returns:
        str: Le choix de l'utilisateur parmi "play again", "quit" ou "change mode", en fonction de la touche appuyée.
    """
    g.afficherTexte("RECOMMENCER ? (Espace)", LARGEUR/2, HAUTEUR/1.35, "white", 20)
    g.afficherTexte("ARRÊTER ? (Echap)", LARGEUR/2, HAUTEUR/1.5, "white", 20)
    g.afficherTexte("CHANGER DE MODE ? (M)", LARGEUR/2, HAUTEUR/1.2, "white", 20)

    key = None
    choice = {keys["play again"]: "play again", keys["quit"]: "quit", keys["change mode"]: "change mode"}
    while True:
        key = g.attendreTouche().lower()
        if key in choice: 
            # g.fermerFenetre()
            return choice[key]