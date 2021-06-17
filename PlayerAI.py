from typing import TYPE_CHECKING
import pygame
import random
import math
import ForbiddenCave
from enum import Enum
from queue import PriorityQueue

# Contains player AI logic
class PlayerAI:
    def __init__(self, player, map, screen, costs):
        self.player = player
        self.map = map
        self.screen = screen
        self.costMap = costs
        self.state = State.SEARCHING
        self.isJumping = False
        
    def random(self):
        action = random.randint(0, 10)
        if(action > 8):
            player.jump = random.randint(-5, 5)
        else:
            player.xmove = random.randint(-1, 1)

    def updateBehaviour(self,gemGroup,doorGroup):
        if self.state == State.SEARCHING:
            if(len(gemGroup) < 1):
                return self.iaMoving(self.findDoor(doorGroup))
            else:
                return  self.iaMoving(self.findGem(gemGroup))
        elif self.state == State.JUMPING:
            print("state : Jumping") 
            if self.isJumping == False:
                self.jump()
                self.isJumping= True
            elif self.player.jump == 0:
                self.isJumping = False
                self.state = State.SEARCHING
                self.player.update_ia_frame = 10

    def jump(self):
        if (self.player.jump == 0 and self.player.ymove == 0) or self.player.doElevator == True:
            #self.player.jumpSound.play()
            self.player.jump = -5.2
            self.player.climbMove = 0
            self.player.doClimb = False
            self.player.doElevator = False
            self.player.elevator = None
            #self.player.xmove = 1
            print("salto jumppp")
        
    
    def findGem(self, gemGroup):
        playerPos = (self.player.rect.centerx, self.player.rect.centery)
        closestGems = gemGroup

        if(len(gemGroup) > 4):
            gemsDistances = {}
            # find closest gem group
            for gem in gemGroup:
                goal = (gem.rect.x, gem.rect.y)
                distance = distance_euclidian_onScreen(playerPos, goal)
                gemsDistances.update({distance:gem})            
            closestGems = [gemsDistances[k] for k in sorted(list(gemsDistances.keys()))[:4]]
        paths = []
        # for all gems calculate aStar
        for gem in closestGems:
            goal = (gem.rect.x, gem.rect.y)
            path = aStar(playerPos, goal, self.map, self.screen, self.costMap)
            paths.append(path)

        closestGemPath = paths[0]
        closestAlpha = closestGemPath.size + closestGemPath.cost
        for path in paths:
            alpha = path.size + path.cost
            if alpha < closestAlpha:
                closestGemPath = path
                closestAlpha = alpha

        drawPath(closestGemPath, self.screen)

        return closestGemPath
                    

    def findDoor(self, doorGroup):
        
        playerPos = (self.player.rect.centerx, self.player.rect.centery)
        # Calculate the best path for the door
        door = list(doorGroup)[0]
        goal = (door.rect.x, door.rect.y)
        path = aStar(playerPos, goal, self.map, self.screen, self.costMap)
        
        #print(closestGemPath.cost)
        drawPath(path, self.screen)
        return path

    def iaMoving(self,path):       
        nextMove = path.nodes[len(path.nodes)-2]
        #currentMove = path.nodes[len(path.nodes)-1]
        # center player
        #self.player.rect.centerx = path.nodes[len(path.nodes)-1][0] + 20
        #self.player.rect.centery = path.nodes[len(path.nodes)-1][1] + 20

        
        #nextNextMove = path.nodes[len(path.nodes)-3]
        playerPos = (self.player.rect.x, self.player.rect.y)

        # x, y = screen_to_map(currentMove)
        # xx, yy = screen_to_map(nextMove)
        # print(x, y)
        # drawCircle(currentMove, self.screen, (0, 0, 255))
        # if (onMap((x,y), self.map) and self.map[int(y)][int(x)] == 'l'):
           
        index = len(path.nodes)-2
        x, y = screen_to_map(nextMove)
        xP, yP = screen_to_map(playerPos)

        if (onMap((x,y+1), self.map) and (self.map[int(y+1)][int(x)] == '.' or self.map[int(y+1)][int(x)] == 'x') \
                    and  (onMap((xP,yP+1), self.map) and self.isFloor((xP,yP+1),self.map))):
            while index >  0:
                nextMove1 = path.nodes[index]
                xx, yy = screen_to_map(nextMove1)
                if self.map[int(yy+1)][int(xx)] == 'a' and 4 > abs(xx - xP) and (yy == yP or yy + 1 == yP or yy -1 == yP):
                    if yy + 1 == yP:
                        self.player.update_ia_frame = 50
                      
                    self.state = State.JUMPING
                    self.player.doClimb = False
                    self.player.climbMove = 0
    
                    #Maybe this is bad
                    print("#########################State change to jumping#########################")
                    return 
                if xx >= xP + 3:
                    break
                index -= 1
 
        if (onMap((xP-1,yP),self.map)and self.map[int(yP)][int(xP - 1)] == 'f' and self.player.xmove == -1 ) \
            or (onMap((xP+1,yP),self.map) and self.map[int(yP)][int(xP + 1)] == 'f' and self.player.xmove == 1):
                print("firee")
                self.player.update_ia_frame = 30
                self.state = State.JUMPING
                self.player.doClimb = False
                self.player.climbMove = 0
                return
        if (onMap((xP,yP),self.map)and self.map[int(yP)][int(xP)] == 'f' and (self.player.xmove == -1 or self.player.xmove == 1)):
                print("firee")
                self.player.update_ia_frame = 30
                self.state = State.JUMPING
                self.player.doClimb = False
                self.player.climbMove = 0
                return
        ## fire on diagonal rip rip rip
        if (onMap((xP,yP+1),self.map)and self.map[int(yP+1)][int(xP)] == 'f' and self.player.xmove == -1 ) \
            or (onMap((xP,yP+1),self.map) and self.map[int(yP+1)][int(xP)] == 'f' and self.player.xmove == 1):
                print("diagonal fire")
                self.state = State.JUMPING
                self.player.doClimb = False
                self.player.climbMove = 0
                return

        if playerPos[1] > nextMove[1]:
            
            if (self.player.jump == 0 and self.player.ymove == 0) or self.player.doElevator == True:
                        #self.jumpSound.play()
                self.player.jump = -5.2
                self.player.climbMove = 0
                self.player.doClimb = False
                self.player.doElevator = False
                self.player.elevator = None
                #self.player.xmove = 0

                print("salto")
                
        elif playerPos[0] > nextMove[0]: # left
            self.player.xmove = -1 #-(playerPos[0] - nextMove[0])/40
    
        elif playerPos[0] < nextMove[0]: # right
            self.player.xmove = 1 #(nextMove[0] - playerPos[0])/40
            print("direita")
            
        if playerPos[1] < nextMove[1] :
            if self.player.canClimb:
                self.player.doClimb = True
                self.player.climbMove = 1 #(nextMove[1] - playerPos[1])/20
                print("descer escada")

        if playerPos[1] > nextMove[1]:
            if self.player.canClimb:
                self.player.doClimb = True
                self.player.climbMove = -1 #(playerPos[1] - nextMove[1])/20
                print("escalar")

          
    def isFloor(self, point, textmap):
        x, y = point
        if onMap(point, textmap):
            c = textmap[y][x]
            return c == 'b' or c == 'a' or c == 'l'
        else:
            return False         


##################
## A* algorithm ##
##################
class Path():
    def __init__(self, nodes, size, cost):
        self.size = size
        self.cost = cost
        self.nodes = nodes

# Node for A*
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
def aStar(point, goal, textmap, screen, costMap):
    priorityQueue = []
    visited = []
    path = None
    searching = True

    if point == goal:
        searching == False
        path.append(Path(point, 1, 0))

    # convert to txt map coords
    point = screen_to_map(point)
    goal = screen_to_map(goal)

    h = heuristic(point, goal)
    startNode = Node(point, None, 0, h)
    # place the start node on the queue
    priorityQueue.append(startNode)

    while(len(priorityQueue) > 0 and searching):
        # sort queue by heuristic cost
        priorityQueue = sortQueue(priorityQueue)

        # pop the first node on the queue to be visited
        node = priorityQueue[0]
        priorityQueue.remove(node)
        currentTile = node.point

        ''' Path discovery visualization
        #drawCircle(currentTile, screen)'''

        if currentTile == goal:
            # we found the goal
            searching = False
            step = node
            totalCost = 0
            nodes = []
            while step:
                # Build path
                nodes.append(map_to_screen(step.point))
                totalCost += step.cost
                step = step.parent
            path = Path(nodes, len(nodes), totalCost)            

        # check neighbors
        for hdg in range(4):
            nbr = neighbor(currentTile, hdg)
            # if on the map and not a wall
            if onMap(nbr, textmap) and nbr not in visited and not isWall(nbr, textmap):
                # get distance
                h = heuristic(nbr, goal)

                # get cost
                c = node.cost + calcTileCost(currentTile, nbr, textmap, screen)#TODO: We could add a cost to each tile

                nbrNode = Node(nbr, node, c, h + c)
                c += costMap[nbr[1]][nbr[0]]

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

def calcTileCost(currentTile, point, textmap, screen):
    cx, cy = currentTile
    x, y = point
    c = textmap[y][x]
    cost = 0
    if(c == '.'):
        hasFloor = False
        for i in range(3):
            if onMap((x,y+i+1) , textmap):
                temp = textmap[y+i+1][x] == 'a' or textmap[y+i+1][x] == 'b' or textmap[y+i+1][x] == 'l'
                if cy > y:
                    temp = temp or textmap[y+i+1][x] == 'x'
                hasFloor = hasFloor or temp
            
        hasPlatform = False
        if cx >= x:
            for i in range(-2,0):
                for j in range(1, 3):
                    a = x + i
                    b = y - j

                    if onMap((a,b), textmap) and textmap[b][a] == 'a':
                        hasPlatform = True
        else: 
            for i in range(1, 3):
                for j in range(1, 3):
                    a = x + i
                    b = y - j

                    if onMap((a,b), textmap) and textmap[b][a] == 'a':
                        hasPlatform = True
        
        if hasFloor: 
            cost = 30
        # _ _
        elif ((onMap((x-1,y+1), textmap) and textmap[y+1][x-1] == 'a') or (onMap((x+1,y+1), textmap) and textmap[y+1][x+1] == 'a')):
            cost = 0

        elif hasPlatform:
            cost = 40
        else: 
            cost = 999
        #print (cost)
    return cost 
    
def onMap(point, textmap):
    x, y = point
    width =  len(textmap[0])
    height = len(textmap)
    return x > 0 and x < width and y > 0 and y < height

def isWall(point, textmap):
    x, y = point
    c = textmap[y][x]
    return c == 'b' or c == 'a' or c == 'f' or c == 'x' or c == 'o' #or c == 'O' or c == 'm' or c == 'V'

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

def distance_euclidian_onScreen(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt(pow(abs(x1 - x2),2) + pow(abs(y1 - y2),2))

## Map ##
screenSize = (1040, 680)
mapSize = (26, 17) # it has to be 17 because the first line is the bonus score

def screen_to_map(point):
    x, y = point
    x = x * mapSize[0] // screenSize[0]
    y = y * mapSize[1] // screenSize[1]
    return (x, y-1) # because the first line is the bonus score

def map_to_screen(point):
    x, y = point
    x = x * screenSize[0] / mapSize[0]
    y = (y + 1) * screenSize[1] / mapSize[1] # because the first line is the bonus score
    return (x, y)

# selection sort
def sortQueue(queue):
    for i in range(len(queue)):
        # we assume that the first item of the unsorted segment is the smallest
        lowest_value_index = i
        # this loop iterates over the unsorted items
        for j in range(i + 1, len(queue)):
            if queue[j].heuristicCost < queue[lowest_value_index].heuristicCost:
                lowest_value_index = j
        # Swap values of the lowest unsorted element with the first unsorted
        # element
        queue[i], queue[lowest_value_index] = queue[lowest_value_index], queue[i]
    
    return queue


## Debug draw ##
clock = pygame.time.Clock()

def drawPath(path, screen, color = (255,255,255)):
    for node in path.nodes:
        drawCircle(node, screen, color)

# Auxiliary function to draw a circle o the node being visited
def drawCircle(point, screen, color = (255,255,255)):
    (x,y) = point
    (x,y) = (x+20, y+20) # center
    pygame.draw.circle(screen, color,(x,y),5,0)
    pygame.display.flip()
    #clock.tick(3)

class State(Enum):
    SEARCHING = 1
    JUMPING = 2
    #LADDER = 3