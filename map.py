from config import HAUTEUR, LARGEUR, colors, Textures
import os

def load_map(file_path: str) -> tuple[list, int, int, int, int, int]:
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
        raise BaseException("Erreur, ce ne sont pas les bons paramètres ou le chemin vers la carte n'existe pas !")

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
        raise ValueError("Erreur, les variables timer et/ou timerfantome ne sont pas présente dans le fichier de configuration")

    SIZE = min(LARGEUR // len(maxLength)-1, HAUTEUR // len(gameMap)) #Permet de définir la taille d'une cellule en fonction de la taille de l'écran et des la carte.
    if SIZE > 75: SIZE=75 # On évite que chaque cases soit énorme (ultra zommé)

    map_width = len(maxLength) * SIZE  # Largeur de la carte jouable en pixels
    map_height = len(gameMap) * SIZE  # Hauteur de la carte jouable en pixels

    margin_x = (LARGEUR - map_width) // 2  # Marge à gauche
    margin_y = (HAUTEUR - map_height) // 2  # Marge en haut

    # Ajustement des marges pour qu'elles soient alignées à la grille (cela risque de décaller un peu le centrage...)
    margin_x -= margin_x % SIZE
    margin_y -= margin_y % SIZE
    
    if margin_x < 0: margin_x=0 #Si la marge est négative, on la désactive
    if margin_y < 0: margin_y=0 #Si la marge est négative, on la désactive

    return gameMap, int(timer), int(timerfantome), SIZE, margin_x, margin_y


def create_background(g: object, SIZE: int) -> None:
    """
    Fonction servant a créer le background (fond) du jeu.
    On créer un premier rectangle servant de fond pour le HUD (UI).
    Puis un second pour le reste (la carte entière).
    Nous faisons +10 à la taille de la fenêter car parfois, un petit jour apparait.
    Args:
        g (object) : Instance de la fenêtre (tkiteasy).
        SIZE (int) : Taille d'une cellule.
    Return:
        None
    """
    # Si une des valeurs est absente, nous ne créons pas de fond.
    if not isinstance(g, object) or type(SIZE) != int:
        return

    g.dessinerRectangle(0, 0, LARGEUR+10, SIZE*2, colors["hud"])
    g.dessinerRectangle(0, SIZE*2, LARGEUR+10, HAUTEUR-(SIZE*2), colors["outside"], "background")


def initialize_objects(gameMap, g: object, SIZE: int, margin_x: int, margin_y: int) -> tuple[dict, tuple, list, list, list]:
    """
    Initialise les objets de la carte.
    Args:
        gameMap (list) : La carte du jeu sous forme de liste 2D.
        g (object) : Instance de la fenêtre (tkiteasy).
        SIZE (int) : Taille des cases.
        margin_x (int) : Marge x de la fenêtre
        margin_y (int) : Marge y de la fenêtre
    Returns:
        objects (dict) : Dictionnaire des objets créés.
        player(tuple) : Tuple des coordonnées du bomber
        upgrades (list) : Liste contenant des tuples des coordonées des upgrades
    """
    objects = {}
    upgrades, pos_puddle, pos_portal = [], [], []
    player = None
    for y in range(len(gameMap)):
        emptyLine = 0
        for x in range(len(gameMap[y])):
            if gameMap[y][x] == "-":
                emptyLine+=1
            elif gameMap[y][x] == "U":
                upgrades.append((SIZE*x, SIZE*y))
            elif gameMap[y][x] == "P":
                player = (SIZE*x+margin_x, SIZE*y+margin_y)
            elif gameMap[y][x] in Textures:
                obj = g.afficherImage(SIZE * x+margin_x, SIZE * y+margin_y, (SIZE, SIZE), Textures[gameMap[y][x]])
                obj.type = gameMap[y][x]
                if gameMap[y][x] == "N":
                    pos_puddle += [(SIZE*x+margin_x, SIZE*y+margin_y)]
                elif gameMap[y][x] == "T":
                    pos_portal += [(SIZE*x+margin_x, SIZE*y+margin_y)]                
                objects[(SIZE * x+margin_x, SIZE * y+margin_y, obj.id)] = obj
        if y > 2:
            # Si les deux cases du HUD sont passées, créer pour chaque "ligne", un fond de la couleur de l'intérieur
            BG_X = margin_x+(emptyLine*SIZE)
            BG_Y = (y*SIZE)+margin_y
            WIDTH = (len(gameMap[y])-1)*SIZE-(emptyLine*SIZE)
            g.dessinerRectangle(BG_X, BG_Y, WIDTH, SIZE, colors["inside"], "background")

    return objects, player, upgrades, pos_puddle, pos_portal