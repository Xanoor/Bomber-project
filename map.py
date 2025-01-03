
def load_map(file_path, LARGEUR, HAUTEUR):
    """
    Charge la carte ainsi que les variables timer et timerfantome depuis un fichier.
    Args:
        file_path (str): Chemin vers le fichier de la carte.
        LARGEUR (int): Largeur de la fenêtre.
        HAUTEUR (int): Hauteur de la fenêtre.
    Returns:
        gameMap (list) : liste contenant les lignes de la carte
        int(timer) (int) : entier représentant le timer du jeu
        int(timerFantome) (int) : entier représentant le temps entre chaque apparitions de fantomes
        SIZE (int) : taille des cases du jeu
        margin_x (int) : Marge sur le bord gauche de la fenêtre
        margin_y (int) : Marge sur le bord haut de la fenêtre
    """
    gameMap = [[]]*2 #On créer deux lignes vide pour mettre les stats !
    timer = None
    timerfantome = None
    maxLength = ""

    with open(file_path, 'r') as f:
        for line in f.readlines():
            maxLength = line if len(maxLength) < len(line) else maxLength
            line = line.strip()
            if len(line) < 2:
                continue

            if line.startswith('timerfantome'):
                timerfantome = int(line.split(' ')[-1])
            elif line.startswith('timer'):
                timer = int(line.split(' ')[-1])
            else:
                gameMap.append(list(line))

    SIZE = min(LARGEUR // len(maxLength)+1, HAUTEUR // len(gameMap)) #Permet de définir la taille d'une cellule en fonction de la taille de l'écran et des la carte.

    map_width = len(maxLength) * SIZE  # Largeur de la carte jouable en pixels
    map_height = len(gameMap) * SIZE  # Hauteur de la carte jouable en pixels

    margin_x = (LARGEUR - map_width) // 2  # Marge à gauche
    margin_y = (HAUTEUR - map_height) // 2  # Marge en haut

    # Ajustement des marges pour qu'elles soient alignées à la grille (cela risque de décaller un peu le centrage...)
    margin_x -= margin_x % SIZE
    margin_y -= margin_y % SIZE

    return gameMap, int(timer), int(timerfantome), SIZE, margin_x, margin_y


def initialize_objects(gameMap, g, SIZE, COLORS, margin_x, margin_y):
    """
    Initialise les objets de la carte.
    Args:
        gameMap (list) : La carte du jeu sous forme de liste 2D.
        g (Tk) : Instance de la fenêtre.
        SIZE (int) : Taille des cases.
        COLORS (dict) : Dictionnaire des couleurs associées aux types d'objets.
        margin_x (int) : Marge x de la fenêtre
        margin_y (int) : Marge y de la fenêtre
    Returns:
        objects (dict) : Dictionnaire des objets créés.
        player(tuple) : Tuple des coordonnées du bomber
        upgrades (list) : Liste contenant des tuples des coordonées des upgrades
    """
    objects = {}
    upgrades = []
    player = None
    for y in range(len(gameMap)):
        for x in range(len(gameMap[y])):
            if gameMap[y][x] == "U":
                upgrades.append((SIZE*x, SIZE*y))
            elif gameMap[y][x] in COLORS:
                obj = g.afficherImage(SIZE * x+margin_x, SIZE * y+margin_y, (SIZE, SIZE), COLORS[gameMap[y][x]])
                obj.type = gameMap[y][x]
                objects[(SIZE * x+margin_x, SIZE * y+margin_y, obj.id)] = obj
            elif gameMap[y][x] == "P":
                player = (SIZE*x+margin_x, SIZE*y+margin_y)
    return objects, player, upgrades