from tkiteasy import ouvrirFenetre
from map import load_map, initialize_objects, create_background
from game_objects import Bomber, Fantome, Bombe, Upgrade, NullObject, Nappe
from UI import statistiques, showGameResult, defaultUIIcons
import config
import os #module built-in, pas besoins de l'installer
import random

LARGEUR = config.LARGEUR
HAUTEUR = config.HAUTEUR

class Game:
    """
    Class représentant l'exécution du jeu.
    """
    def __init__(self, custom=config.customMode):
        """
        Initialise la class Game.

        Args:
            custom (bool) : Définit si le jeu est lancé en mode custom ou non.
        """
        self.custom = custom
        self.gameover = False
        self.objects = {}
        self.timer_obj = None
        self.stats_obj = None
        self.explosions = []
        self.cases = {"bloquantes": {"M", "C", "E", "P", "F", "T"}, "non-bloquantes": {"U", "B", "N"}}
        self.timer = None
        self.timerfantome = None
        self.player = None
        self.SIZE = None
        self.margin_x = None
        self.margin_y = None
        self.initialize_game()
        self.run()

    def initialize_game(self) -> None:
        """
        Permet de créer le jeu de manière graphique.
        """
        #Si la classe Game n'a pas l'attribut g, on ne fait rien.
        if not hasattr(self, "g"):
            self.g = ouvrirFenetre(LARGEUR, HAUTEUR)

        self.verifyTextures()

        # Si la taille de la fenêtre est trop petite, on affiche une erreur !
        if LARGEUR < 400 or HAUTEUR < 400:
            raise ValueError(f"La taille de la fenêtre ({LARGEUR}x{HAUTEUR}) est trop petite. Minimum requis : 400x400.")
        try:
            customOrVanilla = "custom" if self.custom else "vanilla"
            map_file = random.choice(config.map[customOrVanilla])
            gameMap, self.timer, self.timerfantome, self.SIZE, self.margin_x, self.margin_y = load_map("maps/"+ customOrVanilla + "/" + map_file)
            self.TIMERFANTOME = self.timerfantome
            create_background(self.g, self.SIZE)

            # Récupération des objets, la position du joueur et des upgrades
            self.objects, player_pos, upgrades, self.pos_puddle, self.pos_portal  = initialize_objects(
                gameMap, self.g, self.SIZE, 
                self.margin_x, self.margin_y
            )

            if player_pos is None:
                print("Le joueur n'est pas présent sur carte lors de l'initialization !")
                exit()

            # Création du joueur (player)
            self.player = Bomber(player_pos[0], player_pos[1], self)
            
            # Création des upgrades
            for upgrade in upgrades:
                Upgrade(upgrade[0], upgrade[1], self)
            
            defaultUIIcons(self.g, self.SIZE)
            self.timer_obj, self.stats_obj = statistiques(
                self.g, self.timer_obj, self.stats_obj, self.timer, 
                self.player.pv, self.player.points, self.player.level, 
                self.SIZE
            )
        except Exception as e: #Si une erreur survient lors du lancement du jeu, quitter le jeu.
            raise Exception (f"Erreur lors de l'initialisation du jeu ! \n{e}")

        

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
        Fonction récursive qui vérifie et renvoie les voisins à une position.
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
        """
        Fonction appelée à chaque tour afin de mettre à jour les variables et appeler les autres classes
        """
        #On supprime chaque image d'explosion sur la carte.
        if len(self.explosions) > 0:
            for explosion in self.explosions:
                self.g.supprimer(explosion)

        # Mise à jour des fantomes et des updates
        self.callUpdate({"F", "U"}) # La consigne oblige de faire d'abord déplacer les fantomes, puis mettre à jour les bombes
                                    # il y aura donc deux appels de cette fonction pour la fonction callUpdate, une pour les fantomes et les upgrades et une pour les bombes

        # Faire apparaitre les nouveaux fantomes si le timerfantome == 0
        if self.timerfantome == 0:
            self.timerfantome = self.TIMERFANTOME
            for k, v in self.objects.copy().items():
                if v.type == "E":
                    Fantome(v.x-(v.x%self.SIZE), v.y-(v.y%self.SIZE), self)

        self.callUpdate({"B"}) # La consigne oblige de faire d'abord déplacer les fantomes, puis faire mettre à jour les bombes
                               # il y aura donc deux appels de cette fonction pour la fonction callUpdate, une pour les fantomes et les upgrades et une pour les bombes

        if self.custom: # Si l'on joue à la version custom                     
            Nappe(self.pos_puddle, self)
            
        # Mise à jour des timers
        self.timer -= 1
        self.timerfantome -= 1

        if self.timer <= 0:
            self.gameover = True
            
        # Mise à jour des statistique (UI)
        self.timer_obj, self.stats_obj = statistiques(
            self.g, self.timer_obj, self.stats_obj, self.timer, 
            self.player.pv, self.player.points, self.player.level, 
            self.SIZE
        )
        
        if self.gameover: #Si le jeu est fini, on affiche du texte.
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
        player_choice = showGameResult(self.g, self.player.points)
        self.g.supprimer("all")

        if player_choice == "play again": #Si le joueur veut rejouer, on relance
            self.__init__(self.custom)
        elif player_choice == "change mode": #Si le joueur veut rejouer dans l'autre mode, on le lance
            self.__init__(not self.custom)
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
                "play again": "space",
                "change mode": "m"
            }
        
    def verifyTextures(self) -> None:
        """
        Fonction permettant de vérifier si toutes les textures (images et couleurs) dans config.Textures et config.colors existent.
        Si ce n'est pas le cas, une erreur est créer.
        """
        texturesToCheck = {"P", "U", "F", "B", "M", "E", "C"}
        texturesHUDToCheck = {"coeur", "timer"}
        colorsToCheck = {"inside", "outside", "hud"}
        missing_textures = []
        for texture in texturesToCheck:
            if texture not in config.Textures or not os.path.isfile(config.Textures[texture]):
                missing_textures.append(texture)

        for textureHUD in texturesHUDToCheck:
            if textureHUD not in config.Textures_HUD or not os.path.isfile(config.Textures_HUD[textureHUD]):
                missing_textures.append(textureHUD)

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
                        if obj.type in self.cases["bloquantes"] and not obj.type == "T":   # Une exception est créer pour les types "T"
                            case = False                                                   # En effet, il s'agit du seul type qui doit être bloquant pour les fantomes SEULEMENT
                            continue

                    if not case: # Si la case n'est pas disponible, on reprend au début
                        continue

                    self.player.move(self.SIZE * keys_dirs[key][0], self.SIZE * keys_dirs[key][1])
                    self.player.on_portal(self.pos_portal)
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
        