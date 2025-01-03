import random

# Classe créer pour toutes cases vides (ou objet non répertorié)
class NullObject:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

# Classe du joueur
class Player:
    def __init__(self, x, y, game):
        self.game = game
        self.pv = 20
        self.x = None
        self.y = None
        self.id = None
        self.level = 0
        self.explosionDist = 1
        self.points = 0
        self.object = self.createPlayer(x, y)

    def createPlayer(self, x, y):
        """
        Permet de créer le joueur.
        Args:
            x (int) : position x du joueur
            y (int) : position y du joueur
        Return:
            player_obj (ObjetGraphique) : affichage sur la carte du joueur
        """
        player_obj = self.game.g.afficherImage(x, y, (self.game.SIZE, self.game.SIZE), "textures/player.png")
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
            self.game.gameover = True

    def move(self, x, y):
        """
        Fonction appelée afin de faire bouger le joueur.
        Args:
            x (int) : coordonnées x de la nouvelle position du joueur
            y (int) : coordonnées y de la nouvelle position du joueur
        """
        self.game.g.deplacer(self.object, x, y)
        self.x = self.object.x
        self.y = self.object.y


# Classe des fantomes
class Fantome:
    def __init__(self, x, y, game):
        self.game = game
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
        pos = self.game.checkNeightbor(x, y)
        if len(pos) > 1: # Si la prise n'est pas bloquée:
            pos = random.choice(pos)
            self.type = "F"
            self.x = pos[0]
            self.y = pos[1]
            self.obj = self.game.g.afficherImage(pos[0], pos[1], (self.game.SIZE, self.game.SIZE), self.game.IMAGES["F"])
            self.id = self.obj.id
            self.game.objects[(self.x, self.y, self.id)] = self

    def isPlayerNeighbor(self, neightbor):
        """
        Fonction qui vérifie si le joueur est voisin ou non.
        Args:
            neightbor (list) : Liste des positions voisines au fantome
        Return
            bolléen (bool) : Renvoie si le joueur est voisin ou non.
        """
        for n in neightbor:
            if n[0] == self.game.player.object.x and n[1] == self.game.player.object.y:
                return True
        return False
    
    def hitByBomb(self):
        """
        Fonction qui se déclanche lorsque le fantome est touché par une bombe.
        Le fantome est supprimé et laisse place a une upgrade.
        """
        del self.game.objects[(self.x, self.y, self.id)]
        self.game.g.supprimer(self.obj)
        Upgrade(self.x, self.y, self.game)
    
    def update(self):
        """
        Fonction appelée a chaque étape de jeu, sert a bouger le fantome.
        """
        if self.x is None or self.y is None or (self.x, self.y, self.id) not in self.game.objects:
            return

        pos = self.game.checkNeightbor(self.x, self.y)

        if len(pos) == 0:
            return

        if self.isPlayerNeighbor(pos):  #Si le joueur est voisin, le fantome ne bouge pas et attaque (ordre donnée)
            return self.game.player.damage()

        if len(pos) > 1:
            if self.lastPos in pos:
                pos = [p for p in pos if (p[0], p[1]) != self.lastPos]

        self.lastPos = (self.x, self.y)
        pos = random.choice(pos)

        self.game.g.deplacer(self.obj, pos[0]-self.x, pos[1]-self.y)
        self.x = pos[0]
        self.y = pos[1]

        if self.isPlayerNeighbor(self.game.checkNeightbor(self.x, self.y)):
            self.game.player.damage()

        del self.game.objects[(self.lastPos[0], self.lastPos[1], self.id)] # On supprime l'ancienne position des objets pour la rajouter apres
        self.game.objects[(self.x, self.y, self.id)] = self

class Bombe:
    def __init__(self, x, y, game):
        self.game = game
        self.id = None
        self.x = x
        self.y = y
        self.type = "B"
        self.cooldown = 6 # 5-1 car on met direct a jour le tour (ce qui retire un au cooldown)
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
        self.obj = self.game.g.afficherImage(x, y, (self.game.SIZE, self.game.SIZE), self.game.IMAGES["B"])
        self.id = self.obj.id
        self.game.objects[(self.x, self.y, self.id)] = self

    def getExplosionPattern(self, x, y, dirx=1, diry=0, dist=1, s=0):
        """
        Fonction récursive permettant d'obtenir le patterne de l'explosion (position)
        Args:
            x (int) : position x de la bombe
            y (int) : position y de la bombe
            dirx (int) : direction x de l'explosion (haut, bas, gauche, droite), par défaut sur 1
            diry (int) : direction y de l'explosion, par défaut sur 0
            dist (int) : distance de l'explosion par rapport à la bombe, par défaut sur 1
            s (int) : nombre de direction testé par la bombe, par défaut sur 0
        Return:
            pattern (list) : liste contenant tout les coordonées (x, y) des cases touchés par l'explosion
        """
        pattern = []
        if s == 4:
            return [(x, y)] # on ajoute la position actuelle de la bombe
        for i in range(1, dist+1):
            position = (x + (self.game.SIZE * dirx * i), y + (self.game.SIZE * diry * i))
            # La fonction any retourne True si la condition est vérifiée au moins une fois, sinon False
            hasTypeC = any(element.type == "C" or element.type == "E" for element in self.game.getCase(position[0], position[1]))
            if hasTypeC: break #Si la position contient une colonne ou une prise ethernet, on s'arrete et n'ajoutons pas la position.

            pattern.append(position)

        return pattern + self.getExplosionPattern(x, y, -diry, dirx, dist, s+1)

    def explosion(self):
        """
        Fonction appelée afin de faire exploser la bombe.
        """
        for pos in self.getExplosionPattern(self.x, self.y, dist=self.game.player.explosionDist):
            playerIsHit = False
            for obj in self.game.getCase(pos[0], pos[1]):
                if obj == self: #Ne fais rien afin de ne pas s'auto exploser à l'infini
                    continue
                elif hasattr(obj, "hitByBomb"):
                    obj.hitByBomb()
                elif obj.type == "M": #Si l'objet est un mur
                    self.game.g.supprimer(obj)
                    del self.game.objects[(obj.x, obj.y, obj.id)]
                    self.game.player.points += 1
                if (self.game.player.x == obj.x and self.game.player.y == obj.y 
                    and not playerIsHit): #Si l'objet est le joueur et qu'il n'a pas déja été touché par cette bombe
                    playerIsHit = True
                    self.game.player.damage()
            
            #Pour chaque position, créer une image d'explosion 
            self.game.explosions.append(self.game.g.afficherImage(pos[0], pos[1], 
                                        (self.game.SIZE, self.game.SIZE), 
                                        "textures/explosion.png"))

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
                del self.game.objects[(self.x, self.y, self.id)]
                self.game.g.supprimer(self.obj)
                self.explosion()

# Classe pour les améliorations (upgrades)
class Upgrade:
    def __init__(self, x, y, game):
        self.game = game
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
        self.obj = self.game.g.afficherImage(x, y, (self.game.SIZE, self.game.SIZE), self.game.IMAGES["U"])
        self.id = self.obj.id
        self.game.objects[(self.x, self.y, self.id)] = self

    def hitByBomb(self):
        """
        Fonction qui se déclanche lorsque l'upgrade est touchée par une bombe.
        L'upgrade est supprimé.
        """
        del self.game.objects[(self.x, self.y, self.id)]
        self.game.g.supprimer(self.obj)

    def update(self):
        """
        Fonction appellée à chaque étape du jeu (chaque déplacement du joueur).
        """
        if self.x == self.game.player.x and self.y == self.game.player.y:
            if self.game.player.level%2 == 0:
                self.game.player.explosionDist += 1
            else:
                self.game.player.pv += 1
            self.game.player.level += 1
            self.game.player.points += 1

            del self.game.objects[(self.x, self.y, self.id)]
            self.game.g.supprimer(self.obj)