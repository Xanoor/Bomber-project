from tkiteasy import ouvrirFenetre
from map import load_map, initialize_objects
from game_objects import Player, Fantome, Bombe, Upgrade, NullObject
from UI import statistiques
import config

LARGEUR = config.LARGEUR
HAUTEUR = config.HAUTEUR

class Game:
    def __init__(self):
        self.g = None
        self.gameover = False
        self.win = False
        self.objects = {}
        self.stats_obj = None
        self.explosions = []
        self.cases = {"bloquantes": {"M", "C", "E", "P", "F"}, "non-bloquantes": {"U", "B"}}
        self.timer = None
        self.timerfantome = None
        self.IMAGES = {
            "C": "textures/colonne.png",
            "M": "textures/mur0.png",
            "E": "textures/ethernet.png",
            "F": "textures/fantome.png",
            "B": "textures/bombe.png",
            "U": "textures/upgrade.png"
        }
        self.player = None
        self.SIZE = None
        self.margin_x = None
        self.margin_y = None
        self.initialize_game()
        self.run()

    def initialize_game(self):
        try:
            self.g = ouvrirFenetre(LARGEUR, HAUTEUR)
            gameMap, self.timer, self.timerfantome, self.SIZE, self.margin_x, self.margin_y = load_map("map0.txt", LARGEUR, HAUTEUR)
            self.TIMERFANTOME = self.timerfantome
            
            # Récupération des objets, la position du joueur et des upgrades
            self.objects, player_pos, upgrades = initialize_objects(
                gameMap, self.g, self.SIZE, self.IMAGES, 
                self.margin_x, self.margin_y
            )
            
            # Creation du joueur (player)
            self.player = Player(player_pos[0], player_pos[1], self)
            
            # Creation des upgrades
            for u in upgrades:
                Upgrade(u[0], u[1], self)
                
            self.stats_obj = statistiques(
                self.g, self.stats_obj, self.timer, 
                self.player.pv, self.player.points, self.player.level, 
                self.SIZE, self.SIZE + self.SIZE//2
            )
        except Exception as e: #Si une erreur survient lors du lancement du jeu, quitter le jeu.
            print(f"Erreur lors de l'initialisation du jeu ! \n{e}")
            exit()
        

    def getCase(self, x: int, y: int) -> list:
        """
        Permet de récupérer la case que nous vérifions, on met la priorité sur les fantomes (plus important qu'une prise ethernet par exemple)
        Args:
            x (int) : position x à vérifier
            y (int) : position y à vérifier
        Return:
            objectInCase (list) : Objet à retourner / objet null
        """
        if type(x) != int or type(y) != int:
            return [NullObject(x-(x%self.SIZE), y-(y%self.SIZE), None)]
            
        objectInCase = []
        case = (x-(x%self.SIZE), y-(y%self.SIZE))

        for key in self.objects:
            if key[:2] == case:
                objectInCase.append(self.objects[key])
                
        return objectInCase if len(objectInCase) > 0 else [NullObject(case[0], case[1], None)]

    def getNeightborPosition(self, x: int, y: int, dirx: int=1, diry: int=0, s: int=0) -> list:
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
        
        data = (x+(self.SIZE*dirx), y+(self.SIZE*diry))
        if s == 4:
            return []
        return [data] + self.getNeightborPosition(x, y, -diry, dirx, s+1)

    def checkNeightbor(self, x: int, y: int) -> list:
        """
        Fonction récursive qui vérifie et renvoie les voisons a une position.
        Args:
            x (int) : position x de l'objet
            y (int) : position y de l'objet
        Return:
            voisins (list) : retourne une liste des positions voisines non bloquantes
        """
        if type(x) != int or type(y) != int:
            return []
            
        pos_list = self.getNeightborPosition(x, y)

        for pos in pos_list.copy():
            for obj in self.getCase(pos[0], pos[1]):
                if obj.type in self.cases['bloquantes']:
                    if pos in pos_list:
                        pos_list.remove(pos)

        return pos_list

    def update(self):
        """Fonction appelée a chaque tours afin de mettre a jour les variables et appeler les autres classes"""

        for obj in self.objects.copy(): # La consigne oblige de faire déja déplacer les fantomes, puis faire mettre a jour les bombes
            try:                        # il y aura donc deux boucles pour la fonction udpate, une pour fantomes et upgrades et une pour bombes
                if (hasattr(self.objects[obj], "update") and 
                    (self.objects[obj].type == "F" or self.objects[obj].type == "U")):
                    self.objects[obj].update()
            except: #Erreur lors de la récupération de l'objet (supprimé par exemple)
                continue

        # Faire apparaitre les nouveaux fantomes si le timerfantome == 0
        if self.timerfantome == 0:
            self.timerfantome = self.TIMERFANTOME
            for k, v in self.objects.copy().items():
                if v.type == "E":
                    Fantome(v.x-(v.x%self.SIZE), v.y-(v.y%self.SIZE), self)

        # Mise a jour des bombes
        for obj in self.objects.copy(): # La consigne oblige de faire déja déplacer les fantomes, puis faire mettre a jour les bombes
            try:                        # il y aura donc deux boucles pour la fonction udpate, une pour fantomes et upgrades et une pour bombes
                if hasattr(self.objects[obj], "update") and self.objects[obj].type == "B":
                    self.objects[obj].update()
            except: #Erreur lors de la récupération de l'objet (supprimé par exemple)
                continue

        # Mise a jour des timers
        self.timer -= 1
        self.timerfantome -= 1

        if self.timer <= 0:
            self.gameover = True
            
            

        # Mise a jour des statistique (UI)
        statistiques(
            self.g, self.stats_obj, self.timer, 
            self.player.pv, self.player.points, self.player.level, 
            self.SIZE, self.SIZE + self.SIZE//2
        )

        #On vérifie s'il reste des murs, si non : le jeu est gagné, on l'arrête.
        compteur_M = 0
        for i in range(len(list(self.objects.values()))):
            if list(self.objects.values())[i].type == 'M':
                compteur_M += 1
        if compteur_M == 0:
            self.win = True

        if self.gameover:
            self.win_or_lose()
        if self.win:
            self.win_or_lose()

    def win_or_lose(self):
        if self.gameover:
            final_message = "GAME OVER"
        else:
            final_message = "YOU WIN"
        size_text = 40
        longueur_rect, largeur_rect = size_text * len(final_message), size_text
        x_rect = LARGEUR/2 - (longueur_rect/2)
        y_rect = HAUTEUR/2 - (largeur_rect / 2)
        rect_gameover = self.g.dessinerRectangle(x_rect, y_rect, longueur_rect, largeur_rect, "gray")
        text_gameover = self.g.afficherTexte(final_message, LARGEUR/2, HAUTEUR/2, "white", size_text)
        self.end()
        

    def end(self):
        self.g.afficherTexte("RECOMMENCER ? (Espace)", LARGEUR/4, HAUTEUR/1.5, "white", 20)
        self.g.afficherTexte("ARRÊTER ? (Echap)", LARGEUR/1.25, HAUTEUR/1.5, "white", 20)
        touche_fin = None
        while touche_fin not in {"space", "Espace"}: # On oblige que la touche soit espace ou échap.
            touche_fin = self.g.attendreTouche()
            if touche_fin == "space":
                self.g.fermerFenetre()
                Game()
            elif touche_fin == "Escape":
                self.g.fermerFenetre()
                exit()
    

    def run(self):
        """Fonction permettant de tourner le jeu"""

        keys_dirs = {
            "z": (0, -1), "s": (0, 1), "q": (-1, 0), "d": (1, 0),
            "Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)
        }
        binded_keys = {"e", "z", "s", "q", "d", "Up", "Right", "Down", "Left", "space"}

        while True:
            key = self.g.attendreTouche()
            if key in binded_keys and not self.gameover and not self.win:
                if len(self.explosions) > 0:
                    for explosion in self.explosions:
                        self.g.supprimer(explosion)

                if key in keys_dirs and self.player.object:
                    pos = (
                        self.player.x + self.SIZE * keys_dirs[key][0],
                        self.player.y + self.SIZE * keys_dirs[key][1]
                    )
                    case = self.getCase(pos[0], pos[1])

                    if len(self.checkNeightbor(self.player.x, self.player.y)) < 1: #Le joueur est bloqué ! -> Game Over (on continue ou non ?)
                        self.gameover = True
                        self.win_or_lose()

                    for obj in case:
                        if obj.type in self.cases["bloquantes"]:
                            case = False
                            continue

                    if not case: # Si la case n'est pas disponible, on reprend au début
                        continue

                    self.player.move(self.SIZE * keys_dirs[key][0], self.SIZE * keys_dirs[key][1])
                elif (key == "space") and not self.gameover and not self.win:
                    Bombe(self.player.x, self.player.y, self)

                self.update()