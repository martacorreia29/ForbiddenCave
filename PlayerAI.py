import random
import math

class PlayerAI:
    def __init__(self, player, map):
        self.player = player
        self.map = map
        
    def random():
        action = random.randint(0, 10)
        if(action > 8):
            player.jump = random.randint(-5, 5)
        else:
            player.xmove = random.randint(-1, 1)

    def findGem(self, gemGroup):
        # Foe all gems calculate aStar
        playerPos = (self.player.rect.centerx, self.player.rect.centery)
        for gem in gemGroup:
            goal = (gem.rect.x, gem.rect.y)
            path = aStar(playerPos, goal, self.map)

            #print(gem.rect.x, gem.rect.y)


# Node for aStar
class Node():
    def __init__(self, point, parent, cost, heuristicCost):
        self.point = point
        self.parent = parent
        self.cost = cost
        self.heuristicCost = heuristicCost

    def __str__(self):
        return "( " + str(self.point) + " -> " + str(self.heuristicCost) + " )"
    def __repr__(self):
        return "( " + str(self.point) + " -> " + str(self.heuristicCost) + " )"

## Heuristics
def heuristic(p1,p2):
    return distance_euclidian(p1, p2)
    #return distance_manhattan(p1, p2)

# Calculates the manhattan distace between 2 points
def distance_manhattan(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Calculates the euclidian distace between 2 points
def distance_euclidian(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt(pow(abs(x1 - x2),2) + pow(abs(y1 - y2),2))

# Calculates the best path between two points using an version of the A * algorithm
def aStar(point, goal, map):
    priorityQueue = []
    visited = []
    path = []
    searching = True

    # convert to txt coords
    point = screen_to_map(point)
    goal = screen_to_map(goal)

    if point == goal:
        searching == False
        path.append(point)

    h = heuristic(point, goal)
    starNode = Node(point, None, 0, h)
    ## place the start node on the queue
    priorityQueue.append(starNode)

    while(len(priorityQueue) > 0 and searching):
        # sort queue by heuristic cost
        priorityQueue = sortQueue(priorityQueue)

        # pop the first node on the queue to be visited
        node = priorityQueue[0]
        priorityQueue.remove(node)
        hex = node.hex

        ## Path discovery visualization
        #drawCircle(hex)
        ###

        if hex == goal:
            # we found the goal
            searching = False
            step = node
            while step:
                # Build path
                path.append(step.hex)
                step = step.parent

        ## check neighbors
        for hdg in range(4):
            nbr = neighbor(hex,hdg)
            # if on the map and not a wall
            if map.onmap(nbr) and nbr not in visited and terr[nbr[0]][nbr[1]] < 100:
                # get distance
                h = heuristic(nbr, goal)
                # get cost
                c = node.cost + terr[nbr[0]][nbr[1]]

                nbrNode = Node(nbr, node, c, h + c)

                # do we need to update this node on the queue
                inQueue = False
                for x in priorityQueue:
                    if x.hex == nbrNode.hex:
                        inQueue = True
                        if(x.cost > nbrNode.cost):
                            priorityQueue.remove(x)
                            priorityQueue.append(nbrNode)
                            break
                
                if(not inQueue):
                    priorityQueue.append(nbrNode)

        visited.append(node.hex)   
    return path

# selection sort
def sortQueue(queue):
    for i in range(len(queue)):
        # We assume that the first item of the unsorted segment is the smallest
        lowest_value_index = i
        # This loop iterates over the unsorted items
        for j in range(i + 1, len(queue)):
            if queue[j].heuristicCost < queue[lowest_value_index].heuristicCost:
                lowest_value_index = j
        # Swap values of the lowest unsorted element with the first unsorted
        # element
        queue[i], queue[lowest_value_index] = queue[lowest_value_index], queue[i]
    
    return queue

def neighbor(point, theta):
    (x,y) = screen_to_map(point)
    if theta == 0: # left
        x = x - 1
    elif theta == 1: # botton
        y = y + 1
    elif theta == 2: # right
        x = x + 1
    elif theta == 3: # top
        y = y - 1
    return map_to_screen(x,y)

# Map
screenSize = (1040, 680)
mapSize = (26, 16)

def screen_to_map(point):
    x, y = point
    x = x * mapSize[0] / screenSize[0]
    y = y * mapSize[1] / screenSize[1]
    return (x, y)

def map_to_screen(point):
    x, y = point
    x = x * screenSize[0] / mapSize[0]
    y = y * screenSize[1] / mapSize[1]
    return (x, y)
