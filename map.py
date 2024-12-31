
def load_map(file_path, LARGEUR, HAUTEUR):
    """
    Charge la carte ainsi que les variables timer et timerfantome depuis un fichier.
    Args:
        file_path (str): Chemin vers le fichier de la carte.
        LARGEUR (int): Largeur de la fenêtre.
        HAUTEUR (int): Hauteur de la fenêtre.
    Returns:
        tuple: (gameMap, objects, timer, timerfantome, SIZE)
    """
    gameMap = []
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
    return gameMap, int(timer), int(timerfantome), SIZE


def initialize_objects(gameMap, g, SIZE, COLORS):
    """
    Initialise les objets de la carte.
    Args:
        gameMap (list): La carte du jeu sous forme de liste 2D.
        g (Tk): Instance de la fenêtre.
        SIZE (int): Taille des cases.
        COLORS (dict): Dictionnaire des couleurs associées aux types d'objets.
    Returns:
        dict: Dictionnaire des objets créés.
        player: Tuple des coordonnées du bomber
    """
    objects = {}
    player = None
    for y in range(len(gameMap)):
        for x in range(len(gameMap[y])):
            if gameMap[y][x] in COLORS:
                obj = g.afficherImage(SIZE * x, SIZE * y, (SIZE, SIZE), COLORS[gameMap[y][x]])
                obj.type = gameMap[y][x]
                objects[(SIZE * x, SIZE * y, obj.id)] = obj
            elif gameMap[y][x] == "P":
                player = (SIZE*x, SIZE*y)
    return objects, player