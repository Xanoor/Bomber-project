from tkiteasy import ouvrirFenetre
from map import *
from config import LARGEUR, HAUTEUR, keys
from game_objects import *

g = ouvrirFenetre(LARGEUR, HAUTEUR)
map = "maps/map_test.txt"
gameMap, timer, timerfantome, SIZE, margin_x, margin_y = load_map(map)
objects, player_pos, upgrades, pos_puddle, pos_portal  = initialize_objects(gameMap, g, SIZE, margin_x, margin_y)


def getNeightborPosition(x: int, y: int, dirx: int=1, diry: int=0, s: int=0) -> list:
    """
    Récupère les positions autour d'une position donnée.
    Args:
        x (int) : position x de l'objet
        y (int) : position y de l'objet
        dirx (int) : direction x a vérifier, par défaut sur 1
        diry (int) : direction y a vérifier, par défaut sur 0
        s (int) : nombre de direction vérifiées, par défaut sur 0
    Return:
        positions (list) : retourne quatres positions (les quatres positions voisines)
    """
    if type(x) != int or type(y) != int:
        return []
    
    data = (x+(SIZE*dirx), y+(SIZE*diry))
    if s == 4:
        return []
    return [data] + getNeightborPosition(x, y, -diry, dirx, s+1)


def endGameOptions(g: object) -> str:
    """
    Fonction permettant de recommencer ou d'arrêter la partie.

    Args :
        g (object) : Notre fenêtre.
    Return :
        choice[key] (str) : choix de fin de jeu retourné par la fonction endGameOptions.
    """

    g.afficherTexte("FERMER ? (Espace, Echap, M)", LARGEUR/2, HAUTEUR/1.35, "white", 20)
    key = None
    choice = {keys["play again"]: "play again", keys["quit"]: "quit", keys["change mode"]: "change mode"}
    while True:
        key = g.attendreTouche().lower()
        if key in choice:
            return choice[key]


def isPlayerNeighbor(neightbor: list, player_pos: tuple): # Ajout du paramètre player_pos pour adapter la fonction à un fonctionnement seul
    """
    Fonction qui vérifie si le joueur est voisin ou non.
    Args:
        neightbor (list) : Liste des positions voisines au fantome
        player_pos (tuple) : position (x, y) du joueur
    Return
        booléen (bool) : Renvoie si le joueur est voisin ou non.
    """
    for n in neightbor:
        # Modification des variables de la position du joueur pour adapter la fonction à un fonctionnement seul
        if n[0] == player_pos[0] and n[1] == player_pos[1]: 
            return True
    return False


def load_map(file_path: str):
    """
    Charge la carte ainsi que les variables timer et timerfantome depuis un fichier.
    Args:
        file_path (str): Chemin vers le fichier de la carte.
    Returns:
        gameMap (list) : liste contenant les lignes de la carte
        int(timer) (int) : entier représentant le timer du jeu
        int(timerFantome) (int) : entier représentant le temps entre chaque apparitions de fantomes
        SIZE (int) : taille des cases du jeu
        margin_x (int) : Marge sur le bord gauche de la fenêtre
        margin_y (int) : Marge sur le bord haut de la fenêtre
    """

    if type(file_path) != str or not os.path.isfile(file_path):
        print("Erreur, ce ne sont pas les bons paramètres ou le chemin vers la carte n'existe pas !")
        exit()

    gameMap = [[]]*2 #On créer deux lignes vide pour mettre les stats !
    timer = None
    timerfantome = None
    maxLength = ""

    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) < 2:
                continue

            if line.startswith('timerfantome'):
                timerfantome = int(line.split(' ')[-1])
            elif line.startswith('timer'):
                timer = int(line.split(' ')[-1])
            else:
                maxLength = line if len(maxLength) < len(line) else maxLength
                gameMap.append(list(line))

    if timerfantome == None or timer == None:
        print("Erreur, les variables timer et/ou timerfantome ne sont pas présente dans le fichier de configuration")
        exit()

    SIZE = min(LARGEUR // len(maxLength)+1, HAUTEUR // len(gameMap)) #Permet de définir la taille d'une cellule en fonction de la taille de l'écran et des la carte.
    if SIZE > 75: SIZE=75 # On évite que chaque cases soit énorme (ultra zommé)

    map_width = len(maxLength) * SIZE  # Largeur de la carte jouable en pixels
    map_height = len(gameMap) * SIZE  # Hauteur de la carte jouable en pixels

    margin_x = (LARGEUR - map_width) // 2  # Marge à gauche
    margin_y = (HAUTEUR - map_height) // 2  # Marge en haut

    # Ajustement des marges pour qu'elles soient alignées à la grille (cela risque de décaller un peu le centrage...)
    margin_x -= margin_x % SIZE
    margin_y -= margin_y % SIZE
    
    return gameMap, int(timer), int(timerfantome), SIZE, abs(margin_x), abs(margin_y)
