
#Taille de la fenêtre
LARGEUR = 1500
HAUTEUR = 1000

# Nom du fichier de la carte.
map = {"vanilla": [
           "map0.txt", "map1.txt", "map2.txt"
        ],
       
        "custom": [
           ""
        ]
}

#Attribution des touches
keys = {
    #Touches de déplacement
    "up": "z",
    "down": "s",
    "right": "d",
    "left": "q",

    #Touche poser une bombe
    "place_bomb": "e",

    #Touches pour quitter ou rejouer
    "quit": "escape",
    "play again": "space"
}

#Textures utilisées
Textures = {
            "C": "textures/colonne.png",
            "M": "textures/mur0.png",
            "E": "textures/ethernet.png",
            "F": "textures/fantome.png",
            "B": "textures/bombe.png",
            "U": "textures/upgrade.png",
            "P": "textures/player2.png"
}

#Couleurs utilisées
colors = {
    "inside" : "#707070",
    "outside": "green",
    "hud": "#505050"
}