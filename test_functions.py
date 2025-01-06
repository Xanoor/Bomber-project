from FunctionsToTest import *

def test_getNeightborPosition():
    """
    test de la fonction getNeightborPosition (du fichier game.py)
    """
    assert getNeightborPosition(0, 0) == [(75, 0), (0, 75), (-75, 0), (0, -75)], "Les voisins sont incorrects"
    assert len(getNeightborPosition(0, 0)) == 4, "Une position ne peut pas avoir plus ou moins de 4 voisins"
    assert getNeightborPosition(0, "0") == [], "y n'est pas un entier : la fonction doit renvoyé une liste vide"
    assert getNeightborPosition("0", 0) == [], "x n'est pas un entier : la fonction doit renvoyé une liste vide"

test_getNeightborPosition()


def test_endGameOptions():
    """
    test de la fonction endGameOptions (du fichier UI.py)
    """
    result_endGameOptions = endGameOptions(g)
    assert result_endGameOptions == "quit" or result_endGameOptions == "play again" or result_endGameOptions == "change mode", "Ce choix n'est pas possible"

test_endGameOptions()


def test_isPlayerNeighbor():
    """
    test de la fonction isPlayerNeighbor (du fichier game_objects.py)
    """
    assert isPlayerNeighbor([(100, 101),(100, 99),(99, 100),(101, 100)], (100, 101)) == True, "Le joueur est voisin mais n'est pas detecté comme tel"
    assert isPlayerNeighbor([(100, 101),(100, 99),(99, 100),(101, 100)], (101, 101)) == False, "Le joueur n'est pas voisin mais est detecté comme tel"

test_isPlayerNeighbor()


def test_load_map():
    """
    test de la fonction load_map (du fichier map.py)
    """
    assert load_map(map) == ([[], [], ['C', 'C', 'C'],
                              ['C', ' ', 'C'], 
                              ['C', 'C', 'C']], 
                              50, 10, 75, 225, 75), "Le fichier de la carte ne correspond pas aux données enregistrés"
    
test_load_map()
