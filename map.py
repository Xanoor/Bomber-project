from tkiteasy import ouvrirFenetre
f = open('map0.txt', 'r')

LARGEUR = 1000
HAUTEUR = 800
TIMERFANTOME = None
timer = None
timerfantome = None

gameMap = []

objects = {}
fantomes = {}

cases = {"bloquantes": {"M", "C", "E", "P", "F"}, "non-bloquantes": {"U", "B"}}

for x in f.readlines():
    x = x.strip()
    if len(x) < 2:
        continue

    if x.startswith('timerfantome'):
        timerfantome = 1#int(x.split(' ')[-1])
        TIMERFANTOME = 1#int(x.split(' ')[-1])
    elif x.startswith('timer'):
        timer = int(x.split(' ')[-1])
    else:
        gameMap.append(list(x))


g = ouvrirFenetre(LARGEUR, HAUTEUR)

COLORS = {"C": "textures/colonne.png", "M": "textures/mur0.png", "E": "textures/ethernet.png", "F": "textures/mur2.png"}
SIZE = min(LARGEUR//len(gameMap[0]), HAUTEUR//len(gameMap))

player = None
def createPlayer(x, y):
    global player
    if player is None:
        player = g.afficherImage(x, y, (SIZE.__round__(), SIZE.__round__()), "textures/mur3.png")

for y in range(0, len(gameMap)):
    for x in range(0, len(gameMap[y])):
        if gameMap[y][x] in COLORS:
            obj = g.afficherImage(SIZE*x, SIZE*y, (SIZE.__round__(), SIZE.__round__()), COLORS[gameMap[y][x]])
            obj.type = gameMap[y][x]
            objects[(SIZE*x, SIZE*y)] = obj
        
        if gameMap[y][x] == "P":
            createPlayer(SIZE*x, SIZE*y)


class nullObject:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

def getCase(x, y):
    case = (x-(x%SIZE), y-(y%SIZE))
    return (objects|fantomes)[case] if case in objects|fantomes else nullObject(case[0], case[1], None) #dict1 | dict2 remplace les doublons par dict2 (on garde les fantomes)

def createFantom(x, y):
    obj = g.afficherImage(x, y, (SIZE.__round__(), SIZE.__round__()), COLORS["F"])
    obj.type = "F"
    fantomes[(x, y)] = obj

while g.recupererClic() is None:
    clic = g.attendreClic()
    case = getCase(clic.x, clic.y)

    if player:
        if abs(player.x//SIZE-case.x//SIZE) in {0, 1} and abs(player.y//SIZE-case.y//SIZE) in {0, 1}:
            if case.type == None or case.type in cases['non-bloquantes']:
                g.deplacer(player, (case.x//SIZE-player.x//SIZE)*SIZE, (case.y//SIZE-player.y//SIZE)*SIZE)
                timer-=1
                timerfantome-=1
            else:
                print(case.type)
                print(fantomes)

        if timerfantome == 0:
            timerfantome = TIMERFANTOME
            for k, v in objects.items():
                if v.type == "E":
                    createFantom(v.x, v.y)
            
