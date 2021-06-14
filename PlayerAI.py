import pygame
import random
import math
from queue import PriorityQueue

class PlayerAI:
    def __init__(self, player, map, screen):
        self.player = player
        self.map = map
        self.screen = screen
        
    def random():
        action = random.randint(0, 10)
        if(action > 8):
            player.jump = random.randint(-5, 5)
        else:
            player.xmove = random.randint(-1, 1)

    def findGem(self, gemGroup):
        if(len(gemGroup) < 1):
            return []

        # Foe all gems calculate aStar
        playerPos = (self.player.rect.centerx, self.player.rect.centery)

        paths = []
        for gem in gemGroup:
            goal = (gem.rect.x, gem.rect.y)
            path = aStar(playerPos, goal, self.map)
            paths.append(path)

        closestGemPath = paths[0]
        for path in paths:
            if len(path) < len(closestGemPath):
                closestGemPath = path

        drawPath(closestGemPath, self.screen)

        return closestGemPath


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

# Calculates the best path between two points using an version of the A * algorithm
def aStar(point, goal, textmap):
    priorityQueue = []
    visited = []
    path = []
    searching = True

    if point == goal:
        searching == False
        path.append(point)

    # convert to txt map coords
    point = screen_to_map(point)
    goal = screen_to_map(goal)

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
        currentTile = node.point

        ## Path discovery visualization
        #drawCircle(currentTile, screen)
        ###

        if currentTile == goal:
            # we found the goal
            searching = False
            step = node
            while step:
                # Build path
                path.append(map_to_screen(step.point))
                step = step.parent

        ## check neighbors
        for hdg in range(4):
            nbr = neighbor(currentTile, hdg)
            # if on the map and not a wall
            if onMap(nbr, textmap) and nbr not in visited and not isWall(nbr, textmap):
                # get distance
                h = heuristic(nbr, goal)
                # get cost
                c = node.cost #TODO: We could add a cost to each tile

                nbrNode = Node(nbr, node, c, h + c)

                # do we need to update this node on the queue
                inQueue = False
                for x in priorityQueue:
                    if x.point == nbrNode.point:
                        inQueue = True
                        if(x.cost > nbrNode.cost):
                            priorityQueue.remove(x)
                            priorityQueue.append(nbrNode)
                            break
                
                if(not inQueue):
                    priorityQueue.append(nbrNode)

        visited.append(node.point)   
    return path

def onMap(point, textmap):
    x, y = point
    width =  len(textmap[0])
    height = len(textmap)
    return x > 0 and x < width and y > 0 and y < height

def isWall(point, textmap):
    x, y = point
    c = textmap[y][x]
    return c == 'b' or c == 'a' or c == 'f' or c == 'O'

def neighbor(point, theta):
    (x,y) = point
    if theta == 0: # left
        x = x - 1
    elif theta == 1: # botton
        y = y + 1
    elif theta == 2: # right
        x = x + 1
    elif theta == 3: # top
        y = y - 1
    return (x,y)

## Heuristics
def heuristic(p1,p2):
    return distance_euclidian(p1, p2)
    #return distance_manhattan(p1, p2)

# Calculates the manhattan distace between 2 points
def distance_manhattan(p1, p2):
    x1, y1 = map_to_screen(p1)
    x2, y2 = map_to_screen(p2)
    return abs(x1 - x2) + abs(y1 - y2)

# Calculates the euclidian distace between 2 points
def distance_euclidian(p1, p2):
    x1, y1 = map_to_screen(p1)
    x2, y2 = map_to_screen(p2)
    return math.sqrt(pow(abs(x1 - x2),2) + pow(abs(y1 - y2),2))

# Map
screenSize = (1040, 680)
mapSize = (26, 17) # it has to be 17 becouse the first line is the bonus score

def screen_to_map(point):
    x, y = point
    x = x * mapSize[0] // screenSize[0]
    y = y * mapSize[1] // screenSize[1]
    return (x, y-1) # becouse the first line is the bonus score

def map_to_screen(point):
    x, y = point
    x = x * screenSize[0] / mapSize[0]
    y = (y + 1) * screenSize[1] / mapSize[1] # becouse the first line is the bonus score
    return (x, y)

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

clock = pygame.time.Clock()

def drawPath(path, screen):
    for node in path:
        drawCircle(node, screen)

# Auxiliary function to draw a circle o the node being visited
def drawCircle(point, screen, color = (255,255,255)):
    (x,y) = point
    (x,y) = (x+20, y+20) # center
    pygame.draw.circle(screen, color,(x,y),5,0)
    pygame.display.flip()
    #clock.tick(10)