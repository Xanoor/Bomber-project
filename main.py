from tkiteasy import ouvrirFenetre
from map import load_map, initialize_objects
from UI import statistiques
import random

LARGEUR = 800
HAUTEUR = 600

class Game:
    def __init__(self):
        self.gameover = False
        self.objects = {}
        self.stats_obj = None
        self.explosions = []
        self.cases = {"bloquantes": {"M", "C", "E", "P", "F"}, "non-bloquantes": {"U", "B"}}
        self.timer = None
        self.timerfantome = None
        self.IMAGES = {"C": "textures/colonne.png", "M": "textures/mur0.png", "E": "textures/ethernet.png", "F": "textures/fantome.png", "B": "textures/bombe.png", "U": "textures/upgrade.png"}

game = Game()

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
        self.level = 0
        self.explosionDist = 10
        self.points = 0
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
        player_obj = g.afficherImage(x, y, (SIZE, SIZE), "textures/player.png")
        self.x = player_obj.x
        self.y = player_obj.y
        self.id = player_obj.id
        return player_obj
         
    def damage(self):
        """
        Fonction appelée lorsque le joueur est touché par une bombe ou attaqué par un fantome.
        """

        self.pv -= 1
        if self.pv <= 0:
            game.gameover = True
        

    def move(self, x, y):
        """
        Fonction appelée afin de faire bouger le joueur.
        """
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
            self.obj = g.afficherImage(pos[0], pos[1], (SIZE, SIZE), game.IMAGES["F"])
            self.id = self.obj.id
            game.objects[(self.x, self.y, self.id)] = self

        
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
    
    def hitByBomb(self):
        """
        Fonction qui se déclanche lorsque le fantome est touché par une bombe.
        Le fantome est supprimé et laisse place a une upgrade.
        """
        del game.objects[(self.x, self.y, self.id)]
        g.supprimer(self.obj)
        Upgrade(self.x, self.y)
    
    def update(self):
        """
        Fonction appelée a chaque étape de jeu, sert a bouger le fantome.
        """
        if self.x is None or self.y is None or (self.x, self.y, self.id) not in game.objects: #correction de bug: parfois x et y sont null, ce qui fait crash !
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

        if self.isPlayerNeighbor(checkNeightbor(self.x, self.y)):
            player.damage()

        del game.objects[(self.lastPos[0], self.lastPos[1], self.id)] # On supprime l'ancienne position des objets pour la rajouter apres
        game.objects[(self.x, self.y, self.id)] = self

class Bombe:
    def __init__(self, x, y):
        self.id = None
        self.x = x
        self.y = y
        self.type = "B"
        self.cooldown = 5
        self.createBomb(x, y)

    def createBomb(self, x, y):
        """
        Fonction permettant de créer une bombe. Elle créer l'objets graphique, les données et enregistre tout dans le dictionnaire objects.
        Params:
            x (int) : Position x de la bombe.
            y (int) : Position y de la bombe.
        Return:
            None
        """
        self.obj = g.afficherImage(x, y, (SIZE, SIZE), game.IMAGES["B"])
        self.id = self.obj.id
        game.objects[(self.x, self.y, self.id)] = self

    def getExplosionPattern(self, x, y, dirx=1, diry=0, dist=1, s=0):
        """
        Fonction récursive permettant d'obtenir le patterne de l'explosion (position)
        """
        pattern = []
        if s == 4:
            return [(x, y)] # on ajoute la position actuelle de la bombe
        for i in range(1, dist+1):
            position = (x + (SIZE * dirx * i), y + (SIZE * diry * i))
            # La fonction any retourne True si la condition est vérifiée au moins une fois, sinon False
            hasTypeC = any(element.type == "C" or element.type == "E" for element in getCase(position[0], position[1])) # Vérification si un des types est une colonne
            if hasTypeC: break #Si la position contient une colonne ou une prise ethernet, on s'arrete et n'ajoutons pas la position.
            pattern.append(position)

        return pattern + self.getExplosionPattern(x, y, -diry, dirx, dist, s+1)

    def explosion(self):
        """
        Fonction appelée afin de faire exploser la bombe.
        """
        for pos in self.getExplosionPattern(self.x, self.y, dist=player.explosionDist):
            playerIsHit = False
            for obj in getCase(pos[0], pos[1]):
                if obj == self: #Ne fais rien afin de ne pas s'auto exploser à l'infini
                    continue
                elif hasattr(obj, "hitByBomb"): #Si l'objet dispose d'une fonction hitByBomb, on la déclanche
                    obj.hitByBomb()
                elif obj.type == "M": #Si l'objet est un mur
                    g.supprimer(obj)
                    del game.objects[(obj.x, obj.y, obj.id)]
                    player.points += 1
                if player.x == obj.x and player.y == obj.y and not playerIsHit: #Si l'objet est le joueur et qu'il n'a pas déja été touché par cette bombe
                    playerIsHit = True
                    player.damage()
            #Pour chaque position, créer une image d'explosion 
            game.explosions.append(g.afficherImage(pos[0], pos[1], (SIZE, SIZE), "textures/explosion.png"))



    def hitByBomb(self):
        """
        Fonction qui se déclanche lorsque la bombe est touché par une autre bombe.
        Le cooldown est mit à 0 et le fonction update est appelée (celle-ci fera exploser la bombe).
        """
        if self.cooldown is not None:
            self.cooldown = 0
            self.update()

    def update(self):
        """
        Fonction appellée à chaque étape du jeu (chaque déplacement du joueur).
        """
        if self.cooldown is not None:
            self.cooldown -= 1
            
            if self.cooldown <= 0:
                self.cooldown = None
                del game.objects[(self.x, self.y, self.id)]
                g.supprimer(self.obj)
              
                self.explosion()

        

class Upgrade:
    def __init__(self, x, y):
        self.id = None
        self.x = x
        self.y = y
        self.type = "U"
        self.createUpgrade(x, y)

    def createUpgrade(self, x, y):
        """
        Fonction permettant de créer une upgrade. Elle créer l'objets graphique, les données et enregistre tout dans le dictionnaire objects.
        Params:
            x (int) : Position x de l'upgrade.
            y (int) : Position y de l'upgrade.
        Return:
            None
        """
        self.obj = g.afficherImage(x, y, (SIZE, SIZE), game.IMAGES["U"])
        self.id = self.obj.id
        game.objects[(self.x, self.y, self.id)] = self

    def hitByBomb(self):
        """
        Fonction qui se déclanche lorsque l'upgrade est touchée par une bombe.
        L'upgrade est supprimé.
        """
        del game.objects[(self.x, self.y, self.id)]
        g.supprimer(self.obj)

    def update(self):
        if self.x == player.x and self.y == player.y:
            if player.level%2 == 0:
                player.explosionDist += 1
            else:
                player.pv += 1
            player.level += 1
            player.points += 1

            del game.objects[(self.x, self.y, self.id)]
            g.supprimer(self.obj)


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

    for key in game.objects:
        if key[:2] == case:
            objectInCase.append(game.objects[key])
            
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
            if obj.type in game.cases['bloquantes']:
                if pos in pos_list:
                    pos_list.remove(pos)

    return pos_list

# Programme BomberBUT

g = ouvrirFenetre(LARGEUR, HAUTEUR)
gameMap, game.timer, game.timerfantome, SIZE, game.margin_x, game.margin_y = load_map("map0.txt", LARGEUR, HAUTEUR) #récupère la carte, le timer, le timerfantome et la taille des cellules
TIMERFANTOME = game.timerfantome # constante temps d'apparaitions fantomes
game.objects, player, upgrades = initialize_objects(gameMap, g, SIZE, game.IMAGES, game.margin_x, game.margin_y) # Retourne les objets par défauts et les coordonnées du joueur
player = Player(player[0], player[1]) #Créer de la classe du joueur, n'est pas dans le dict objets !

# On créer toutes les upgrades
for u in upgrades:
    Upgrade(u[0], u[1])

game.stats_obj = statistiques(g, game.stats_obj, game.timer, player.pv, player.points, player.level, SIZE, SIZE+SIZE//2)

keys_dirs = {"z": (0, -1), "s": (0, 1), "q": (-1, 0), "d": (1, 0), "Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
binded_keys = {"e", "z", "s", "q", "d", "Up", "Right", "Down", "Left"} #Liste des touches autorisées
key = None

while True:
    key = g.attendreTouche()
    if key in binded_keys and not game.gameover:
        if len(game.explosions) > 0:
            for explosion in game.explosions:
                g.supprimer(explosion)

        if key in keys_dirs and player.object:
            pos = (player.x+SIZE*keys_dirs[key][0], player.y+SIZE*keys_dirs[key][1])
            case = getCase(pos[0], pos[1])

            if len(checkNeightbor(player.x, player.y)) < 1: #Le joueur est bloqué ! -> Game Over (on continue ou non ?)
                game.gameover = True

            for obj in case:
                if obj.type in game.cases["bloquantes"]:
                    case = False
                    continue

            if not case: # Si la case n'est pas disponible, on reprend au début
                continue

            player.move(SIZE*keys_dirs[key][0], SIZE*keys_dirs[key][1])
        elif key == "e" and not game.gameover:
            Bombe(player.x, player.y)

        for obj in game.objects.copy(): # La consigne oblige de faire déja déplacer les fantomes, puis faire mettre a jour les bombes
            try:                   # il y aura donc deux boucles pour la fonction udpate, une pour fantomes et upgrades et une pour bombes
                if hasattr(game.objects[obj], "update") and game.objects[obj].type == "F" or game.objects[obj].type == "U":
                    game.objects[obj].update()
            except: #Erreur lors de la récupération de l'objet (supprimé par exemple)
                continue

        if game.timerfantome == 0:
            game.timerfantome = TIMERFANTOME
            for k, v in game.objects.copy().items():
                if v.type == "E":
                    Fantome(v.x-(v.x%SIZE), v.y-(v.y%SIZE))

        for obj in game.objects.copy(): # La consigne oblige de faire déja déplacer les fantomes, puis faire mettre a jour les bombes
            try:                   # il y aura donc deux boucles pour la fonction udpate, une pour fantomes et upgrades et une pour bombes
                if hasattr(game.objects[obj], "update") and game.objects[obj].type == "B":
                    game.objects[obj].update()
            except: #Erreur lors de la récupération de l'objet (supprimé par exemple)
                continue
            
        game.timer-=1
        game.timerfantome-=1   

        if game.timer <= 0:
            game.gameover = True
        statistiques(g, game.stats_obj, game.timer, player.pv, player.points, player.level, SIZE, SIZE+SIZE//2)
