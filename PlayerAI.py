from typing import TYPE_CHECKING
import pygame
import random
import math

from pygame import draw
import ForbiddenCave
from enum import Enum
from queue import PriorityQueue

# Contains player AI logic
class PlayerAI:
    def __init__(self, player, map, screen):
        self.player = player
        self.map = map
        self.screen = screen
        self.state = State.SEARCHING
        self.isJumping = False
        self.moves = 0
        self.onElevator = None
        self.wantedPosition = None
        self.direction = None
        
    def random(self):
        action = random.randint(0, 10)
        if(action > 8):
            player.jump = random.randint(-5, 5)
        else:
            player.xmove = random.randint(-1, 1)

    def updateBehaviour(self,gemGroup,doorGroup,firegroup, wallgroup, monstergroup, elevatorgroup):
        if self.state == State.SEARCHING:
            if(len(gemGroup) < 1):
                return self.iaMoving(self.findDoor(doorGroup),firegroup, monstergroup, elevatorgroup)
            else:
                return  self.iaMoving(self.findGem(gemGroup),firegroup, monstergroup, elevatorgroup)

        elif self.state == State.JUMPING:
            playerPos = screen_to_map((self.player.rect.centerx, self.player.rect.centery))
            print("state : Jumping ")
            if not self.isJumping:
                self.jump()
                self.isJumping= True

            elif self.player.jump == 0:
                self.isJumping = False
                self.state = State.SEARCHING
                self.player.update_ia_frame = 10

        elif self.state == State.ADJUST:
            print("state : Adjusting") 
            self.adjust(wallgroup)

        elif self.state == State.ON_ELEVATOR:
            self.player.update_ia_frame = 10
            canExit = self.checkToExitElevator()
            if canExit:
                self.player.xmove = 1
                self.jump()
                self.state == State.SEARCHING
            else:
                self.player.xmove = 0

        elif self.state == State.DELAY_BEFORE_JUMP:
            self.moves -= 1
            if self.moves == 0:
                self.jump()

        elif self.state == State.DELAY_MONSTER:
            if self.wantedPosition == screen_to_map(self.player.rect.center):
                self.player.xmove == direction
                self.state == State.SEARCHING

    def delayJump(self, moves, speed):
        self.moves = moves
        self.player.update_ia_frame = speed
        self.state = State.DELAY_BEFORE_JUMP
    
    def delayMonster(self, position, direction, speed):
        self.direction = direction
        self.player.xmove == -1 * direction
        self.wantedPosition = position
        self.player.update_ia_frame = 10
        self.state = State.DELAY_MONSTER

    def adjust(self, wallgroup):
        playerPos = (self.player.rect.x, self.player.rect.y)  
        xP, yP = screen_to_map(playerPos) 

        for wall in wallgroup:                    
            xS, yS = wall.rect.centerx, wall.rect.centery
            xW, yW = screen_to_map((xS, yS))
            # wall under player
            if xW == xP and yW == yP+1:   
                # adjust position for perfect jump
                if self.player.xmove == 1:
                    self.player.rect.centerx, self.player.rect.centery = xS + 10, yS - 40
                else:
                    self.player.rect.centerx, self.player.rect.centery = xS - 10, yS - 40

        self.state = State.JUMPING

    def jump(self):
        if (self.player.jump == 0 and self.player.ymove == 0) or self.player.doElevator == True:
            #TODO self.player.jumpSound.play()
            self.player.jump = -5.2
            self.player.climbMove = 0
            self.player.doClimb = False
            self.player.doElevator = False
            self.player.elevator = None
            print("jump")
          
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
            path = aStar(playerPos, goal, self.map, self.screen)
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

        # calculate the best path for the door
        door = list(doorGroup)[0]
        goal = (door.rect.x, door.rect.y)
        path = aStar(playerPos, goal, self.map, self.screen)
        drawPath(path, self.screen)
        return path

    def iaMoving(self, path, firegroup, monstergroup, elevatorgroup): 
        nextMove = path.nodes[len(path.nodes)-2]
        nextNextMove = path.nodes[len(path.nodes)-3]
        playerPos = (self.player.rect.x, self.player.rect.y)
        index = len(path.nodes)-2 

        continueChecks = True

        # elevators
        continueChecks = self.checkElevators(playerPos, nextMove, elevatorgroup)
        if not continueChecks: return      
        
        # monsters
        continueChecks = self.checkMonsters(nextMove, monstergroup)
        if not continueChecks: return

        # fires
        continueChecks = self.checkFires(playerPos, nextMove, nextNextMove, firegroup)
        if not continueChecks: return

        # jump
        continueChecks = self.checkJumpBetweenPlataforms(playerPos, nextMove, path, index, monstergroup)
        if not continueChecks: return

        # normal movements
        continueChecks = self.movePlayer(playerPos, nextMove, index, path, monstergroup)

    def checkElevators(self, playerPos, nextMove, elevatorgroup):
        x, y = screen_to_map(nextMove)
        playerPos = self.player.rect.center
        drawCircle_noOffset(playerPos, self.screen, (0,0,255))
        xP, yP = screen_to_map(playerPos) 
        xS, yS = playerPos

        goingRight = x > xP # if next move is on the right then its going right

        if onMap((xP,yP+1), self.map):
            cHorizontal1 = self.map[yP+1][xP+1] if goingRight else self.map[yP+1][xP-1]
            cHorizontal2 = self.map[yP+1][xP+2] if goingRight else self.map[yP+1][xP-2]
            cVertical1 = self.map[yP][xP+1] if goingRight else self.map[yP][xP-1]
            cVertical2 = self.map[yP][xP+2] if goingRight else self.map[yP][xP-2]

            # check if there is an elevator path
            cHorizontal1_isFloor = cHorizontal1 == 'a' or cHorizontal1 == 'b'
            foundHorizontalElevator = cHorizontal1 == 'o' or cHorizontal1 == 'O'
            foundHorizontalElevatorWithGap =  (cHorizontal2 == 'o' or cHorizontal2 == 'O') and not foundHorizontalElevator and not cHorizontal1_isFloor
            foundVerticalElevator = cVertical1 == 'o' or cVertical1 == 'O' or cVertical2 == 'o' or cVertical2 == 'O'

            playerOnFloor = self.isFloor((xP,yP+1))

            # check if elevator is in bording zone
            if foundHorizontalElevatorWithGap and playerOnFloor:
                # Elevator path start
                elPSx , elPSy = map_to_screen((xP + 1, yP + 1)) if goingRight else map_to_screen((xP - 1, yP + 1))

                print(abs(elPSx - xS))
                if not goingRight and abs(elPSx - xS) > 45:
                    return False
                elif goingRight and abs(elPSx - xS) > 20:
                    return False

                # drawCircle_noOffset((elPSx+40, elPSy), self.screen, (0,0,255))
                # drawCircle_noOffset((elPSx+80, elPSy), self.screen, (0,0,255))
                # drawCircle_noOffset((elPSx, elPSy-40), self.screen, (0,255,0))
                # drawCircle_noOffset((elPSx, elPSy+40), self.screen, (0,255,0))


                for elevator in elevatorgroup:
                    elx, ely = elevator.rect.center
                    elevatorGoingRight = elevator.xmove > 0
                    inBordingZone = elPSx+80 < elx < elPSx + 120 if goingRight else elPSx-80 < elx < elPSx-40
                    inBordingZone = inBordingZone and elPSy - 40 < ely < elPSy + 40

                    canGo = not elevatorGoingRight and goingRight or elevatorGoingRight and not goingRight

                    if inBordingZone and canGo:
                        #self.player.rect = self.player.rect.move(-40, 0)
                        self.jump()
                        self.state = State.ON_ELEVATOR
                        self.onElevator = elevator
                        self.player.update_ia_frame = 100 if goingRight else 100 # move forward time
                        return True
                self.player.xmove = 0     
                return False

            elif foundHorizontalElevator and playerOnFloor:
                # Elevator path start
                elPSx , elPSy = map_to_screen((xP + 1, yP + 1)) if goingRight else map_to_screen((xP - 1, yP + 1))

                drawCircle_noOffset((elPSx+40, elPSy), self.screen, (0,0,255))
                drawCircle_noOffset((elPSx+80, elPSy), self.screen, (0,0,255))
                drawCircle_noOffset((elPSx, elPSy-40), self.screen, (0,255,0))
                drawCircle_noOffset((elPSx, elPSy+40), self.screen, (0,255,0))


                for elevator in elevatorgroup:
                    elx, ely = elevator.rect.center
                    drawCircle((elx, ely), self.screen, (0,255,0))
                    elevatorGoingRight = elevator.xmove > 0
                    inBordingZone = elPSx+40 < elx < elPSx + 80 if goingRight else elPSx-40 < elx < elPSx
                    inBordingZone = inBordingZone and elPSy - 40 < ely < elPSy + 40

                    canGo = not elevatorGoingRight and goingRight or elevatorGoingRight and not goingRight

                    if inBordingZone and canGo:
                        self.state = State.ON_ELEVATOR
                        self.onElevator = elevator
                        self.player.update_ia_frame = 60 if goingRight else 60 # move forward time
                        return True
                self.player.xmove = 0     
                return False

            elif foundVerticalElevator and playerOnFloor:
                #TODO: Test and fix
                # Elevator path start
                elPSx , elPSy = map_to_screen((xP + 1, yP + 1)) if goingRight else map_to_screen((xP - 1, yP + 1))

                for elevator in elevatorgroup:
                    elx, ely = elevator.rect.center
                    elevatorGoingDown = elevator.ymove > 0
                    inBordingZone = elPSx < elx < elPSx + 80 if goingRight else elPSx-40 < elx < elPSx +40
                    inBordingZone = inBordingZone and elPSy - 40 < ely < elPSy + 40

                    if inBordingZone and elevatorGoingDown:
                        self.state = State.ON_ELEVATOR
                        self.onElevator = elevator
                        self.player.update_ia_frame = 50 if goingRight else 100 # move forward time
                        self.player.update_ia_frame = 100 if elevatorGoingDown else self.player.update_ia_frame # move forward time
                        return True
                self.player.xmove = 0     
                return False
        return True

    def checkToExitElevator(self):
        xE, yE = screen_to_map(self.onElevator.rect.center)
        return self.map[yE][xE+1] != 'o'and self.map[yE][xE+1] != 'O'

    def checkMonsters(self, nextMove, monstergroup):
        x, y = screen_to_map(nextMove)
        xPS, yPS = (self.player.rect.centerx, self.player.rect.centery)
        xP, yP = screen_to_map((xPS, yPS)) 

        self.player.xmove == 1 if xP < x else -1

        # uses sensors to detect monsters
        leftSensor = (self.player.rect.centerx - 40, self.player.rect.centery)
        rightSensor = (self.player.rect.centerx + 40, self.player.rect.centery)
        for monster in monstergroup:
            jump = False
            # <0 <i
            if monster.xmove < 0 and monster.rect.centerx < xP and self.player.xmove == -1 and \
            abs(monster.rect.centerx - leftSensor[0]) < 5 and abs(monster.rect.centery - leftSensor[1]) < 5:
                jump = True
            
            # i 0>
            if monster.xmove > 0 and monster.rect.centerx > xP and self.player.xmove == 1 and \
            abs(monster.rect.centerx - rightSensor[0]) < 20 and abs(monster.rect.centery - rightSensor[1]) < 5:
                jump = True

            # i <0 
            if monster.xmove < 0 and monster.rect.centerx > xP and self.player.xmove == 1 and \
            abs(monster.rect.centerx - rightSensor[0]) < 40 and abs(monster.rect.centery - rightSensor[1]) < 5:
                jump = True            

            # 0> i
            if monster.xmove > 0 and monster.rect.centerx < xP and self.player.xmove == -1 and \
            abs(monster.rect.centerx - leftSensor[0]) < 40 and abs(monster.rect.centery - leftSensor[1]) < 5:
                jump = True

            # checks for floor afer jump
            if self.player.xmove == 1:
                xFS, yFS = xPS+100, yPS+40
                xF, yF = screen_to_map((xFS, yFS)) 
                if jump and onMap((xF, yF), self.map) and not self.isFloor((xF,yF)):
                    print("here")
                    #self.delayMonster((xPS - 40, yPS), self.player.xmove, 1)
                    self.player.rect.centerx, self.player.rect.centery = xPS - 40, yPS
                    self.player.xmove == 0
                    return True
            else:
                xFS, yFS = xP-100, yP+40
                xF, yF = screen_to_map((xFS, yFS)) 
                if jump and onMap((xF, yF), self.map) and not self.isFloor((xF,yF)):
                    self.player.rect.centerx, self.player.rect.centery = xPS + 20, yPS
                    self.player.xmove == 0
                    return True

            if jump: 
                print("sensor monster")
                self.player.update_ia_frame = 10
                self.state = State.JUMPING
                self.player.doClimb = False
                self.player.climbMove = 0
                return False
        return True

    # uses sensors to detect fire
    def checkFires(self, playerPos, nextMove, nextNextMove, firegroup):
        x, y = screen_to_map(nextMove)
        xN, yN = screen_to_map(nextNextMove)
        xP, yP = screen_to_map(playerPos) 

        # uses sensors to detect fire
        leftSensor = (self.player.rect.centerx - 40, self.player.rect.centery)
        rightSensor = (self.player.rect.centerx + 40, self.player.rect.centery)

        # if its going up or down a letter, doesnt need to check for fire
        if self.map[int(yN)][int(xN)] != 'l':
            for fire in firegroup:
                if ((abs(fire.rect.centerx - leftSensor[0]) < 10 and abs(fire.rect.centery - leftSensor[1]) < 5 and self.player.xmove == -1) or \
                (abs(fire.rect.centerx - rightSensor[0]) < 20 and abs(fire.rect.centery - rightSensor[1]) < 5 and self.player.xmove == 1)): 
                    print("sensor fire")
                    self.player.update_ia_frame = 10
                    self.state = State.JUMPING
                    self.player.doClimb = False
                    self.player.climbMove = 0
                    return False
        
            if (((onMap((xP-1,yP),self.map)and self.map[int(yP)][int(xP - 1)] == 'f' and self.player.xmove == -1 ) \
                or (onMap((xP+1,yP),self.map) and self.map[int(yP)][int(xP + 1)] == 'f' and self.player.xmove == 1))) \
                or (onMap((xP,yP),self.map)and self.map[int(yP)][int(xP)] == 'f' and (self.player.xmove == -1 or self.player.xmove == 1)):
                    print("firee")
                    return False
                        
            # fire on diagonal
            if (onMap((xP,yP+1),self.map)and self.map[int(yP+1)][int(xP)] == 'f' and self.player.xmove == -1 ) \
                or (onMap((xP,y+1),self.map) and self.map[int(yP+1)][int(xP)] == 'f' and self.player.xmove == 1):
                    print("diagonal fire")
                    self.state = State.JUMPING
                    self.player.doClimb = False
                    self.player.climbMove = 0
                    return False
        return True

    # verifies if is the end of platform and goes through path to see if path leads to another 
    # platform at the same level so it can jump      
    def checkJumpBetweenPlataforms(self, playerPos, nextMove, path, index, monstergroup):
        x, y = screen_to_map(nextMove)
        xP, yP = screen_to_map(playerPos)      
       
        if onMap((x,y+1), self.map) and self.isVoid((x, y+1)) and \
            onMap((xP,yP+1), self.map) and self.isFloor((xP,yP+1)) and x != xP:
            while index >  0:
                nextMove1 = path.nodes[index]
                xx, yy = screen_to_map(nextMove1)
                if self.map[int(yy+1)][int(xx)] == 'a' and 4 > abs(xx - xP) and (yy == yP or yy + 1 == yP or yy - 1 == yP):
                    # check for monsters
                    if(self.checkMonstersBeforeJump(playerPos, monstergroup, nextMove1)):
                        self.player.xmove = 1 if xP < x else -1
                        self.state = State.ADJUST
                        print("adjust")
                        self.player.doClimb = False
                        self.player.climbMove = 0
                    else:
                        self.player.xmove = 0
                    return False
                if xx >= xP + 3:
                    break
                index -= 1
        return True

    def checkMonstersBeforeJump(self, playerPos, monstergroup, plataformEdge):
            xP, yP = screen_to_map(playerPos)
            xEM, yEM = screen_to_map(plataformEdge)

            # find safety zone
            goingRight = xEM > xP   
            safetyDistance = 2 if goingRight else 1 # blocks
            xES, yES = map_to_screen((xEM + safetyDistance, yEM)) if goingRight else map_to_screen((xEM - safetyDistance, yEM))
            
            drawCircle((xES,yES), self.screen, (0, 255, 0))
            for monster in monstergroup:  
                xMS, yMS = screen_to_map(monster.rect.topleft)        
                xM, yM = monster.rect.center
                onSaveDistance = plataformEdge[0] < xM < xES if goingRight else xES < xM < plataformEdge[0] + 40
                print(onSaveDistance, xEM, yEM, xMS, yMS, screen_to_map((xES, yES)))
                if onSaveDistance and yMS == yEM:
                    return False

            print("Monster jump")
            #self.player.xmove = 1 if goingRight else -1
            return True

    def movePlayer(self, playerPos, nextMove, index, path, monstergroup):
        x, y = screen_to_map(nextMove)
        xP, yP = screen_to_map(playerPos)  
        # player center
        playerPos2 = (self.player.rect.centerx, self.player.rect.centery) 
        # jump
        if playerPos[1] > nextMove[1]:
            willJump = False
            # verifies if next 4 movements are fires
            while index >  0:
                nextMove1 = path.nodes[index]
                xx, yy = screen_to_map(nextMove1)    

                if self.map[int(yy+1)][int(xx)] == 'f':
                    willJump = True

                if xx >= xP + 4:
                    break
                index -= 1

            if not willJump and ((self.player.jump == 0 and self.player.ymove == 0) or self.player.doElevator == True):
                if(self.checkMonstersBeforeJump(playerPos, monstergroup, map_to_screen((xP+1, yP-2)))):
                    #self.jumpSound.play()
                    self.player.jump = -5.2
                    self.player.climbMove = 0
                    self.player.doClimb = False
                    self.player.doElevator = False
                    self.player.elevator = None
                    print("salto astar")
                else:
                    self.player.xmove = 0
                    return False
                
        # left 
        elif playerPos[0] > nextMove[0]:
            self.player.xmove = -1
            print("esquerda")

        # right
        elif playerPos[0] < nextMove[0]: 
            self.player.xmove = 1
            print("direita")
            
        # climb down
        if playerPos[1] < nextMove[1] :
            if self.player.canClimb:
                self.player.doClimb = True
                self.player.climbMove = 1
                print("descer escada")

        # climb up
        if playerPos[1] > nextMove[1]:
            if self.player.canClimb:
                self.player.doClimb = True
                self.player.climbMove = -1
                '''if self.map[int(y)][int(x)] == 'l':
                    xM, yM = screen_to_map(playerPos2)
                    xS, yS = map_to_screen((xM, yM))
                    self.player.rect.centerx, self.player.rect.centery = xS + 15, yS'''
                print("escalar") 
          
    def isFloor(self, point):
        x, y = point
        if onMap(point, self.map):
            c = self.map[int(y)][int(x)]
            return c == 'b' or c == 'a' or c == 'l'
        else:
            return False         

    def isVoid(self, point):
        x, y = point
        if onMap(point, self.map):
            c = self.map[int(y)][int(x)]
            return c == '.' or c == 'x'
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
def aStar(point, goal, textmap, screen):
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

# Auxiliary function to draw a circle o the node being visited
def drawCircle_noOffset(point, screen, color = (255,255,255)):
    (x,y) = point
    pygame.draw.circle(screen, color,(x,y),5,0)
    pygame.display.flip()
    #clock.tick(3)

class State(Enum):
    SEARCHING = 1
    JUMPING = 2
    ADJUST = 3
    ON_ELEVATOR = 4
    DELAY_BEFORE_JUMP = 5
    DELAY_MONSTER = 6
    #LADDER = 3