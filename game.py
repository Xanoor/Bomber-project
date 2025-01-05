from tkiteasy import ouvrirFenetre
from map import load_map, initialize_objects, create_background
from game_objects import Player, Fantome, Bombe, Upgrade, NullObject
from UI import statistiques, show_game_result
import config
import os #module built-in, pas besoins de l'installer
import random

LARGEUR = config.LARGEUR
HAUTEUR = config.HAUTEUR

class Game:
    def __init__(self):
        self.g = None
        self.gameover = False
        self.objects = {}
        self.stats_obj = None
        self.explosions = []
        self.cases = {"bloquantes": {"M", "C", "E", "P", "F"}, "non-bloquantes": {"U", "B"}}
        self.timer = None
        self.timerfantome = None
        self.player = None
        self.SIZE = None
        self.margin_x = None
        self.margin_y = None
        self.custom = False
        self.initialize_game()
        self.run()

    def initialize_game(self) -> None:
        self.verifyTextures()
        try:
            self.g = ouvrirFenetre(LARGEUR, HAUTEUR)
            map_file = random.choice(config.map["custom" if self.custom else "vanilla"])
            gameMap, self.timer, self.timerfantome, self.SIZE, self.margin_x, self.margin_y = load_map("maps/"+map_file)
            self.TIMERFANTOME = self.timerfantome
            create_background(self.g, self.SIZE)
            
            # Récupération des objets, la position du joueur et des upgrades
            self.objects, player_pos, upgrades = initialize_objects(
                gameMap, self.g, self.SIZE, 
                self.margin_x, self.margin_y
            )
            
            # Creation du joueur (player)
            self.player = Player(player_pos[0], player_pos[1], self)
            
            # Creation des upgrades
            for upgrade in upgrades:
                Upgrade(upgrade[0], upgrade[1], self)
                
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
        #On supprime chaque image d'explosion sur la carte.
        if len(self.explosions) > 0:
            for explosion in self.explosions:
                self.g.supprimer(explosion)

        # Mise à jour des fantomes et des updates
        self.callUpdate({"F", "U"}) # La consigne oblige de faire déja déplacer les fantomes, puis faire mettre a jour les bombes
                                    # il y aura donc deux appels de cette fonction pour la fonction callUpdate, une pour fantomes et upgrades et une pour bombes

        # Faire apparaitre les nouveaux fantomes si le timerfantome == 0
        if self.timerfantome == 0:
            self.timerfantome = self.TIMERFANTOME
            for k, v in self.objects.copy().items():
                if v.type == "E":
                    Fantome(v.x-(v.x%self.SIZE), v.y-(v.y%self.SIZE), self)

        self.callUpdate({"B"}) # La consigne oblige de faire déja déplacer les fantomes, puis faire mettre a jour les bombes
                               # il y aura donc deux appels de cette fonction pour la fonction callUpdate, une pour fantomes et upgrades et une pour bombes

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
        
        if self.gameover: #Si le joueur à gagné ou perdu, on affiche du texte.
            self.displayUI()

    def callUpdate(self, type_obj: set) -> None:
        """
        Fonctions mettant à jour soit les fantomes et les updates soit les bombes

        Args:
            type_obj (set) : Set contenant le (ou les) type(s) d'objet que l'on souhaite update
        """

        for obj in self.objects.copy(): 
            try:
                if (hasattr(self.objects[obj], "update") and self.objects[obj].type in type_obj):
                    self.objects[obj].update()
            except: #Erreur lors de la récupération de l'objet (supprimé par exemple)
                continue

    def displayUI(self) -> None:
        """
        Fonction permettant d'afficher du texte et de recommencer le jeu OU de l'arrêter.
        """
        player_choice = show_game_result(self.g, self.player.points)

        if player_choice == "play again": #Si le joueur veut rejouer, on relance
            Game()
        else:                             #Sinon, on quitte
            exit()

    def verifyKeyBinding(self) -> None:
        """
        Fonction permettant de vérifier si toutes les touches du jeu sont attribués et existent.
        Si ce n'est pas le cas, les touches sont remises par défaut.
        """
        keysToCheck = {"up", "down", "left", "right", "play again", "quit", "place_bomb"}
        if not all(key in config.keys for key in keysToCheck):
            config.keys = {
                "up": "z",
                "down": "s",
                "right": "d",
                "left": "q",
                "place_bomb": "e",
                "quit": "escape",
                "play again": "space"
            }
        
    def verifyTextures(self) -> None:
        """
        Fonction permettant de vérifier si toutes les textures (images et couleurs) dans config.Textures et config.colors existent.
        Si ce n'est pas le cas, une erreur est créer.
        """
        texturesToCheck = {"P", "U", "F", "B", "M", "E", "C"}
        colorsToCheck = {"inside", "outside", "hud"}
        missing_textures = []
        for texture in texturesToCheck:
            if texture not in config.Textures or not os.path.isfile(config.Textures[texture]):
                missing_textures.append(texture)

        for color in colorsToCheck:
            if color not in config.colors:
                missing_textures.append(color)

        if missing_textures:
            raise FileNotFoundError(f"Les textures ou couleurs suivantes sont manquantes ou n'existent pas : {', '.join(missing_textures)}")


    def run(self) -> None:
        """Fonction permettant de tourner le jeu"""
        self.verifyKeyBinding()
        
        keys_dirs = {
            config.keys["up"]: (0, -1), config.keys["down"]: (0, 1), config.keys["left"]: (-1, 0), config.keys["right"]: (1, 0),
            "up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0) #Touches additionnels (directionnelles)
        }
        binded_keys = set(config.keys.values()) | keys_dirs.keys() #On joint les touches dans config et celles dans keys_dirs (left, right, up, down)
        key = None
        while key != config.keys["quit"]:
            key = self.g.attendreTouche().lower() # On transforme la touche en minuscule au cas ou le joueur a activé CAPSLOCK
            if key in binded_keys and not self.gameover:
                if key in keys_dirs and self.player.object:
                    pos = (
                        self.player.x + self.SIZE * keys_dirs[key][0],
                        self.player.y + self.SIZE * keys_dirs[key][1]
                    )
                    case = self.getCase(pos[0], pos[1])

                    if len(self.checkNeightbor(self.player.x, self.player.y)) < 1: #Le joueur est bloqué -> Game Over
                        self.gameover = True
                        self.displayUI()

                    for obj in case:
                        if obj.type in self.cases["bloquantes"]:
                            case = False
                            continue

                    if not case: # Si la case n'est pas disponible, on reprend au début
                        continue

                    self.player.move(self.SIZE * keys_dirs[key][0], self.SIZE * keys_dirs[key][1])
                    self.update()
                elif key == config.keys["place_bomb"] and not self.gameover:
                    # On verifie si la case est déja un bombe ou non.
                    caseAlreadyABomb = False
                    for obj in self.getCase(self.player.x, self.player.y):
                        if obj.type == "B":
                            caseAlreadyABomb = True
                            break
                    if not caseAlreadyABomb:
                        Bombe(self.player.x, self.player.y, self) 
                        self.update()

        self.g.fermerFenetre()
        