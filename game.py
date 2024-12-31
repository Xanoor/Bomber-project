from tkiteasy import ouvrirFenetre
from map import load_map, initialize_objects
import random

LARGEUR = 1000
HAUTEUR = 800

objects = {}
cases = {"bloquantes": {"M", "C", "E", "P", "F"}, "non-bloquantes": {"U", "B"}}

COLORS = {"C": "textures/colonne.png", "M": "textures/mur0.png", "E": "textures/ethernet.png", "F": "textures/fantome.png"}

# Classe créer pour toutes cases vides (ou objet non répertorié)
class NullObject:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

# Classe du joueur
class Player:
    def __init__(self, x, y):
        self.pv = 20
        self.x = None
        self.y = None
        self.id = None
        self.bombes = 0
        self.object = self.createPlayer(x, y)

    def createPlayer(self, x, y):
        """
        Permet de créer le joueur.
        Args:
            x (int) : position x du joueur
            y (int) : position y du joueur
        Return:
            None
        """
        player_obj = g.afficherImage(x, y, (SIZE.__round__(), SIZE.__round__()), "textures/player.png")
        self.x = player_obj.x
        self.y = player_obj.y
        self.id = player_obj.id
        return player_obj
         
    def damage(self):
        print("-1")
        self.pv -= 1
        if self.pv <= 0:
            print("dead")

    def move(self, x, y):
        g.deplacer(self.object, x, y)
        self.x = self.object.x
        self.y = self.object.y


# Classe des fantomes
class Fantome:
    def __init__(self, x, y):
        self.id = None
        self.x = None
        self.y = None
        self.lastPos = None
        self.createFantom(x, y)
        
    def createFantom(self, x, y):
        """
        Fonction permettant de créer un fantome, le fantome apparait a coté d'une prise éthernet.
        Args:
            x (int) : position x du fantome
            y (int) : position y du fantome
        Return:
            None
        """
        pos = checkNeightbor(x, y)
        if len(pos) > 1: # Si la prise n'est pas bloquée:
            pos = random.choice(pos)
            self.type = "F"
            self.x = pos[0]
            self.y = pos[1]
            self.obj = g.afficherImage(pos[0], pos[1], (SIZE.__round__(), SIZE.__round__()), COLORS["F"])
            self.id = self.obj.id
            objects[(self.x, self.y, self.id)] = self

        
    def isPlayerNeighbor(self, neightbor):
        """
        Fonction qui vérifie si le joueur est voisin ou non.
        Args:
            neightbor (list) : Liste des positions voisines au fantome
        Return
            bolléen (bool) : Renvoie si le joueur est voisin ou non.
        """
        for n in neightbor:
            if n[0] == player.object.x and n[1] == player.object.y:
                return True
        return False
    
    def update(self):
        """
        Fonction appelée a chaque étape de jeu, sert a bouger le fantome.
        """
        if self.x is None or self.y is None or (self.x, self.y, self.id) not in objects: #correction de bug: parfois x et y sont null, ce qui fait crash !
            print("euh stop")
            return

        pos = checkNeightbor(self.x, self.y)

        if len(pos) == 0:
            return

        if self.isPlayerNeighbor(pos): #Si le joueur est voisin, le fantome ne bouge pas et attaque (ordre donnée)
            return player.damage()

        if len(pos) > 1:
            if self.lastPos in pos:
                pos = [p for p in pos if (p[0], p[1]) != self.lastPos]

        self.lastPos = (self.x, self.y)
        pos = random.choice(pos)

        g.deplacer(self.obj, pos[0]-self.x, pos[1]-self.y)
        self.x = pos[0]
        self.y = pos[1]

        del objects[(self.lastPos[0], self.lastPos[1], self.id)] # On supprime l'ancienne position des objets pour la rajouter apres
        objects[(self.x, self.y, self.id)] = self



def getCase(x, y):
    """
    Permet de récupérer la case sur laquelle nous avons cliqué, on met la priorité sur les fantomes (plus important qu'une prise ethernet par exemple)
    Args:
        x (int) : position x du clic
        y (int) : position y du clic
    Return:
        objet (tuple) : Objet a retourné / objet null
    """
    objectInCase = []
    case = (x-(x%SIZE), y-(y%SIZE))

    for key in objects:
        if key[:2] == case:
            objectInCase.append(objects[key])
            
    return objectInCase if len(objectInCase) > 0 else [NullObject(case[0], case[1], None)]


def getNeightborPosition(x, y, dirx=1, diry=0, s=0):
    """
    Récupère les positions autour d'une position donnée.
    Args:
        x (int) : position x de l'objet
        y (int) : position y de l'objet
        dirx (int) : direction x a vérifier
        diry (int) : direction y a vérifier
        s (int) : nombre de direction vérifiées
    Return:
        positions (list) : retourne quatres positions (les quatres positions voisines)
    """
    data = (x+(SIZE*dirx), y+(SIZE*diry))
    if s==4:
        return []
    return [data]+getNeightborPosition(x, y, -diry, dirx, s+1)

def checkNeightbor(x, y):
    """
    Fonction récursive qui vérifie et renvoie les voisons a une position.
    Args:
        x (int) : position x de l'objet
        y (int) : position y de l'objet
    Return:
        voisins (list) : retourne une liste des positions voisines non bloquantes
    """
    pos_list = getNeightborPosition(x, y)

    for pos in pos_list.copy(): # On créer une copie, sinon la liste va sauter des éléments !
        for obj in getCase(pos[0], pos[1]):
            if obj.type in cases['bloquantes']:
                if pos in pos_list:
                    pos_list.remove(pos)
                else:
                    print("non.")

    return pos_list


# Programme BomberBUT

g = ouvrirFenetre(LARGEUR, HAUTEUR)
gameMap, timer, timerfantome, SIZE = load_map("map0.txt", LARGEUR, HAUTEUR) #récupère la carte, le timer, le timerfantome et la taille des cellules
TIMERFANTOME = timerfantome # constante temps d'apparaitions fantomes
objects, player = initialize_objects(gameMap, g, SIZE, COLORS) # Retourne les objets par défauts et les coordonnées du joueur
player = Player(player[0], player[1]) #Créer de la classe du joueur

keys_dirs = {"z": (0, -1), "s": (0, 1), "q": (-1, 0), "d": (1, 0)}
key = None
while key != "Space":
    key = g.attendreTouche()

    if key in keys_dirs and player.object:
        pos = (player.x+SIZE*keys_dirs[key][0], player.y+SIZE*keys_dirs[key][1])
        case = getCase(pos[0], pos[1])

        if len(checkNeightbor(player.x, player.y)) < 1 and player.bombes == 0: #Le joueur est bloqué ! -> Game Over
            print("STOP")

        for obj in case:
            if obj.type in cases["bloquantes"]:
                case = False
                continue

        if not case: # Si la case n'est pas disponible, on reprend au début
            continue

        player.move(SIZE*keys_dirs[key][0], SIZE*keys_dirs[key][1])

        for obj in objects.copy():
            if hasattr(objects[obj], "update"):
                objects[obj].update()


        if timerfantome == 0:
            timerfantome = TIMERFANTOME
            for k, v in objects.copy().items():
                if v.type == "E":
                    Fantome(v.x-(v.x%SIZE), v.y-(v.y%SIZE))
        timer-=1
        timerfantome-=1   