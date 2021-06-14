#Import Modules
import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
import PlayerAI
from pygame.locals import *
from pygame.color import *


PATH_IMAGES = "./images/"
PATH_SOUND = "./sound/"
PATH_MAPS = "./maps/"

UPDATE_AI_FRAME = 20

# Map of level player is moving in
class LevelMap:
    
    def __init__(self, tilefile, wallfile1, wallfile2, mapfile, yoffset):
        # Tile image for wall
        self.tile = pygame.image.load(tilefile) 
        self.wall1 = pygame.image.load(wallfile1)
        self.wall2 = pygame.image.load(wallfile2)
        
        # Load text map
        file = open(mapfile, "r") 
        self.rawtextmap = file.readlines()
        file.close()
        
        # Remove carriage returns
        self.textmap = []                
        for line in self.rawtextmap:
            line = line[0:len(line)-1]
            self.textmap.append(line)
            
        # Sprite groups
        self.levelsurface = None
        self.gemgroup = None
        self.monstergroup = None
        self.laddergroup = None
        self.elevatorgroup = None
        self.firegroup = None
        self.doorgroup = None
        self.batgroup = None
        
        # Offset for tile position location
        self.xoff = 0
        self.yoff = yoffset
        
    # Calculate tile from screen coordinates
    def calcTileFromScreenPos(self, xpos, ypos):
    
        # Fetch tile height and width
        xd = self.tile.get_rect().width
        yd = self.tile.get_rect().height
        
        # Subtract offsets
        xpos = xpos - self.xoff
        ypos = ypos - self.yoff
        
        # Calculate coordinates in tile map 
        xp = xpos / xd
        yp = ypos / yd
        
        return (xp, yp)

    # Fetch tile from map for position
    def fetchTileForPosition(self, xpos, ypos, doCorrect):
        
        # Derive tile position from screen position
        tilePos = self.calcTileFromScreenPos(xpos, ypos)
        xp = tilePos[0]
        yp = tilePos[1]
        
        # Fetch tile and correct it
        result = self.textmap[int(yp)][int(xp)]        
        if doCorrect == True:
            if result == "c" or result == "m" or result == "l" or result == "y":
                result = "."
        
        return result
    
    # Fetch tile environment from map position
    def fetchTileEnvironmentForPosition(self, xpos, ypos):
  
        # Derive tile position from screen position
        tilePos = self.calcTileFromScreenPos(xpos, ypos)
        xp = tilePos[0]
        yp = tilePos[1]  
        
        # Set environment calculation deltas
        xd = [0, 1, 0, -1]
        yd = [-1, 0, 1, 0]
        
        # Retrieve tiles in neighborhood
        result = []
        for ndx in range(4):
            result.append(self.textmap[int(yp+yd[ndx])][int(xp+xd[ndx])])
        
        return result
                
    # Create an empty surface
    def createEmptySurface(self, rect):
    
        surf = pygame.Surface(rect)
        surf = surf.convert()
        surf.fill((0, 0, 0))
        return surf        
         
    # Fetch gem group from map definition
    def fetchGemgroup(self, dirty=False):     

        # Don't recreate gem group
        if self.gemgroup is not None and not dirty:
            return self.gemgroup
        
        # Fetch gem size
        size = self.tile.get_size()
        
        # Create the sprite group for the gems
        self.gemgroup = pygame.sprite.RenderPlain()
        
        # Create gem sprites and add them to the gem group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "c":
                    gem = Gem(xpos, ypos, PATH_IMAGES + "gem.png")
                    self.gemgroup.add(gem)
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.gemgroup

    # Fetch gem group from map definition
    def fetchDoorgroup(self, dirty=False):     

        # Don't recreate door group
        if self.doorgroup is not None and not dirty:
            return self.doorgroup
        
        # Fetch door size
        size = self.tile.get_size()
        
        # Create the sprite group for the door
        self.doorgroup = pygame.sprite.RenderPlain()
        
        # Create door sprites and add them to the gem group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "d":
                    door = Door(xpos, ypos, PATH_IMAGES + "door.png")
                    self.doorgroup.add(door)
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.doorgroup

    
    # Fetch fire group from map definition
    def fetchFiregroup(self, dirty=False):     

        # Don't recreate gem group
        if self.firegroup is not None and not dirty:
            return self.firegroup
        
        # Fetch gem size
        size = self.tile.get_size()
        
        # Create the sprite group for the gems
        self.firegroup = pygame.sprite.RenderUpdates()
        
        # Create gem sprites and add them to the gem group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "f":
                    fire = Fire(xpos, ypos, PATH_IMAGES + "fire.png")
                    self.firegroup.add(fire)
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.firegroup    

    # Fetch monster group from map definition
    def fetchMonstergroup(self, dirty=False):     

        # Don't recreate monster group
        if self.monstergroup is not None and not dirty:
            return self.monstergroup
        
        # Fetch monster size
        size = self.tile.get_size()
        
        # Create the sprite group for the monster
        self.monstergroup = pygame.sprite.RenderPlain()
        
        # Create monster sprites and add them to the monster group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "m":
                    monster = Monster(xpos, ypos, PATH_IMAGES + "monsterLeft.png", PATH_IMAGES + "monsterRight.png", self.levelsurface, self)
                    self.monstergroup.add(monster)
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.monstergroup
    
    # Fetch ladder group from map definition
    def fetchLaddergroup(self, dirty=False):     

        # Don't recreate ladder group
        if self.laddergroup is not None and not dirty:
            return self.laddergroup
        
        # Fetch ladder size
        size = self.tile.get_size()
        
        # Create the sprite group for the ladders
        self.laddergroup = pygame.sprite.RenderPlain()
        
        # Create monster sprites and add them to the ladder group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "L" or tile == "l" or tile == "y": 
                    ladder = Ladder(xpos, ypos , PATH_IMAGES + "ladder.png")
                    self.laddergroup.add(ladder) 
                                       
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.laddergroup   

    # Fetch elevator group from map definition
    def fetchElevatorgroup(self, dirty=False):     

        # Don't recreate elevator group
        if self.elevatorgroup is not None and not dirty:
            return self.elevatorgroup
        
        # Fetch elevator size
        size = self.tile.get_size()
        
        # Create the sprite group for the elevators
        self.elevatorgroup = pygame.sprite.RenderPlain()
        
        # Create elevator sprites and add them to the elevator group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "O": 
                    elevator = Elevator(xpos, ypos, PATH_IMAGES + "elevator.png", self)
                    self.elevatorgroup.add(elevator)                                     
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.elevatorgroup

    # Fetch elevator group from map definition
    def fetchBatgroup(self, dirty=False):     

        # Don't recreate bat group
        if self.batgroup is not None and not dirty:
            return self.batgroup
        
        # Fetch elevator size
        size = self.tile.get_size()
        
        # Create the sprite group for the bats
        self.batgroup = pygame.sprite.RenderPlain()
        
        # Create bat sprites and add them to the bat group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "V": 
                    bat = Bat(xpos, ypos, PATH_IMAGES + "bat.png", self)
                    self.batgroup.add(bat)                                      
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.batgroup

    # Create level surface from map definition
    def fetchLevelSurface(self, dirty=False):
        
        # Don't recreate level surface
        if self.levelsurface is not None and not dirty:
            return self.levelsurface
        
        # Create empty level surface
        size = self.tile.get_size()
        xwidth = len(self.textmap[0]) * size[0]
        ywidth = len(self.textmap) * size[1] + self.yoff
        self.levelsurface = self.createEmptySurface((xwidth, ywidth))
        
        # Paint walls on surface
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                # Wall
                if tile == "b" or tile == "d":
                    self.levelsurface.blit(self.tile, (xpos, ypos))
                elif tile == "a":
                    if xpos / size[0] % 2 == 1:
                        self.levelsurface.blit(self.wall1, (xpos, ypos))
                    else:
                        self.levelsurface.blit(self.wall2, (xpos, ypos))                                 
                
                xpos = xpos + size[0]
            ypos = ypos + size[1]
        
        return self.levelsurface       

# Superclass for animated sprites
class AnimatedSprite(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer    

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self.start = pygame.time.get_ticks()
        self.fps = 10
        self.delay = 1000 / self.fps
        self.last_update = 0 
        
    # Fetch images for animation
    def sliceImage(self, w, h, filename):
        images = []
        master_image = pygame.image.load(filename)
    
        master_width, master_height = master_image.get_size()
        for i in range(int(master_width/w)):
            image = master_image.subsurface(i*w,0,w,h)
            image = image.convert()
            colorkey = image.get_at((0,0))         
            image.set_colorkey(colorkey, RLEACCEL)
            images.append(image)
        return images    
        
# Player is the player
class Player(AnimatedSprite):
        
    def __init__(self, xpos, ypos, playerleft, playerright, playerclimb, playerdead, \
                 background, map):
        AnimatedSprite.__init__(self) #call Sprite initializer
        
        # Start direction
        self.xmove = 0
        self.ymove = 0
        self.jump = 0
        
        # Images and start image and first animation frame
        self.imageleft = self.sliceImage(40, 40, playerleft)
        self.imageright = self.sliceImage(40, 40, playerright)
        self.imageclimb = self.sliceImage(40, 40, playerclimb)
        self.imagedead = self.sliceImage(40, 40, playerdead)
        self.image = self.imageright[0]
        self.frame = 0    

        # Reference to background and to logical background map        
        self.background = background
        self.map = map
        
        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, 40, 40)
        
        # Flags if Player can climb and is climbing
        self.canClimb = False
        self.doClimb = False
        self.climbMove = 0
        self.jumpDead = False
        self.deadJumpCnt = 7
        
        # Flag to indicate that player is on elevator
        self.doElevator = False
        self.elevator = None 

        # Player AI
        self.ai = None


        #TODO: remove if not needed
        # sensors 
        # self.sensorImg = PATH_IMAGES + "point.png" 
        # self.leftSensor = None
        # self.rightSensor = None
        # self.downLeftSensor = None
        # self.downRightSensor = None
        # self.leftLongDistanceSensor = None
        # self.rightLongDistanceSensor = None
        # self.topLeftSensor = None
        # self.topRightSensor = None

           
    # def refresh_sensors(self, screen, display):
    #     self.leftSensor = (self.rect.centerx - self.rect.width , self.rect.centery)
    #     self.rightSensor = (self.rect.centerx  + self.rect.width , self.rect.centery)
    #     self.downLeftSensor = (self.rect.centerx - self.rect.width , self.rect.centery + self.rect.height -10)
    #     self.downRightSensor = (self.rect.centerx + self.rect.width , self.rect.centery + self.rect.height -10)
    #     #self.leftLongDistanceSensor = (self.rect.centerx - self.rect.width * 2, self.rect.centery)
    #     #self.rightLongDistanceSensor = (self.rect.centerx  + self.rect.width * 2 , self.rect.centery)
    #     self.topLeftSensor = (self.rect.centerx - self.rect.width , self.rect.centery - self.rect.height)
    #     self.topRightSensor = (self.rect.centerx + self.rect.width , self.rect.centery - self.rect.height)

    #     # print("Player: x: ", self.rect.x, "y: ", self.rect.y)
    #     # print("leftSensor: x: ", self.leftSensor[0], "y: ", self.leftSensor[1])
    #     # print("rightSensor: x: " , self.rightSensor[0], "y: ", self.rightSensor[1])
    #     # print("downLeftSensor:  x: " , self.downLeftSensor[0], "y: ", self.downLeftSensor[1])
    #     # print("downRightSensor:  x: " , self.downRightSensor[0], "y: ", self.downRightSensor[1])
    #     # print("\n")

    #     if display:
    #             screen.blit(pygame.image.load(self.sensorImg), self.leftSensor)
    #             screen.blit(pygame.image.load(self.sensorImg), self.rightSensor)
    #             screen.blit(pygame.image.load(self.sensorImg), self.downLeftSensor)
    #             screen.blit(pygame.image.load(self.sensorImg), self.downRightSensor)
    #             #screen.blit(pygame.image.load(self.sensorImg), self.leftLongDistanceSensor)
    #             #screen.blit(pygame.image.load(self.sensorImg), self.rightLongDistanceSensor)
    #             screen.blit(pygame.image.load(self.sensorImg), self.topLeftSensor)
    #             screen.blit(pygame.image.load(self.sensorImg), self.topRightSensor)

    # print( player's state
    def printState(self):
        print(("Position: " + str(self.rect.left) + ", " + str(self.rect.top)))
        print(("Direction: " + str(self.xmove) + ", " + str(self.ymove)))
        print(("Jump: " + str(self.jump)))
        print(("Can climb: " + str(self.canClimb)))
        print(("Do climb: " + str(self.doClimb)))
        print(("Climb move: " + str(self.climbMove)))
  
     # Check if player's head has collided
    def checkHeadWallCollision(self, correction):

        pix1 = self.background.get_at((self.rect.left+5, self.rect.top-1))
        pix2 = self.background.get_at((self.rect.left+35, self.rect.top-1))       
        if (pix1 != THECOLORS['black'] or \
           pix2 != THECOLORS['black']):
            self.jump = correction
            self.ymove = int(self.jump)
 
    # Determine y move direction of player if not climbing
    def setYMove(self):
           
        # Player is jumping
        if self.jump < 0: 
            self.jump = self.jump + 0.125
            self.ymove = int(self.jump)

        # Check if player is falling 
        if self.jump >= 0:       
            pix1 = self.background.get_at((self.rect.left+5, int(self.rect.top+40+self.jump)))
            pix2 = self.background.get_at((self.rect.left+35, int(self.rect.top+40+self.jump))) 
            tile1 = self.map.fetchTileForPosition(self.rect.left+5, int(self.rect.top+40+self.jump), False)  
            tile2 = self.map.fetchTileForPosition(self.rect.left+35, int(self.rect.top+40+self.jump), False)    
            if (tile1 == "l" and tile2 == "l") or (tile1 == "y" and tile2 == "y"):
                if(self.jump > self.deadJumpCnt): self.jumpDead = True
                self.jump = 0
                self.ymove = int(self.jump)
                self.canClimb = True  
            elif (tile1 == "l" or tile2 == "l") or (tile1 == "y" or tile2 == "y"):
                if(self.jump > self.deadJumpCnt): self.jumpDead = True                
                self.jump = 0
                self.ymove = int(self.jump)
                self.canClimb = False                         
            elif pix1 == THECOLORS['black'] and \
               pix2 == THECOLORS['black']:
                self.jump = self.jump + 0.125
                self.ymove = int(self.jump)
            else:
                if(self.jump > self.deadJumpCnt): self.jumpDead = True                
                self.jump = 0
                self.ymove = int(self.jump)
                
                # Correct y position if player's feet are inside wall
                pix1 = self.background.get_at((self.rect.left+5, int(self.rect.top+39)))
                pix2 = self.background.get_at((self.rect.left+35, int(self.rect.top+39))) 
                if (pix1 != THECOLORS['black'] or \
                    pix2 != THECOLORS['black']):
                    newpos = self.rect.move((self.xmove, -1))
                    self.rect = newpos  
                
        # Correct player position if his feet are still above the ground ->
        # will happen if jump > 1, don't perform correction if a ladder is
        # below player's feet
        pix1 = self.background.get_at((self.rect.left+5, int(self.rect.top+40+1)))
        pix2 = self.background.get_at((self.rect.left+35, int(self.rect.top+40+1))) 
        tile1 = self.map.fetchTileForPosition(self.rect.left+5, int(self.rect.top+40+1), False)  
        tile2 = self.map.fetchTileForPosition(self.rect.left+35, int(self.rect.top+40+1), False)           
        while pix1 == THECOLORS['black'] and \
              pix2 == THECOLORS['black'] and \
              (tile1 != "l" and tile2 != "l") and \
              (tile1 != "y" and tile2 != "y") and self.jump == 0:
            newpos = self.rect.move((self.xmove, 1))
            self.rect = newpos   
            pix1 = self.background.get_at((self.rect.left+5, int(self.rect.top+40+1)))
            pix2 = self.background.get_at((self.rect.left+35, int(self.rect.top+40+1)))
            tile1 = self.map.fetchTileForPosition(self.rect.left+5, int(self.rect.top+40+1), False)  
            tile2 = self.map.fetchTileForPosition(self.rect.left+35, int(self.rect.top+40+1), False)          
        
        # Don't allow player's head to crash into ceiling
        if self.jump < 0:
            self.checkHeadWallCollision(0)                                          

    # Correct x move direction of player if necessary
    def setXMove(self):
               
        # Determine x position of check
        if self.xmove < 0:
            xcheck = self.rect.left + 5 - 1
        elif self.xmove > 0:
            xcheck = self.rect.left + 35 + 1  
        else:
            return

        # Perform check
        pix1 = self.background.get_at((xcheck, self.rect.top+5))
        pix2 = self.background.get_at((xcheck, self.rect.top+35))    
        if pix1 != THECOLORS['black'] or pix2 != THECOLORS['black']:
            self.xmove = 0
            self.jump = 0             
    
    # Set climb y move direction
    def setClimbMove(self):       
        
        # Do only climb down if there is no wall below player
        pix1 = self.background.get_at((self.rect.left+5, int(self.rect.top+40+self.jump)))
        pix2 = self.background.get_at((self.rect.left+35, int(self.rect.top+40+self.jump)))       
        if self.climbMove > 0:
            if pix1 == THECOLORS['black'] and \
               pix2 == THECOLORS['black']:
                self.ymove = self.climbMove
            else:
                self.ymove = 0
        else:
            self.ymove = self.climbMove 
            
        # Allow player not to run over wall when going up
        if self.ymove < 0:
            self.checkHeadWallCollision(0) 
            
    # Set y move direction according to elevator
    def setElevatorMove(self):
        self.ymove = self.elevator.ymove
    
    # Update sprite on screen
    def update(self):
            
        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1                                       
           
            # Switch back to first frame of sequence if necessary
            if self.doClimb == True:
                if self.frame >= len(self.imageclimb): 
                    self.frame = 0                  
            else:
                if self.frame >= len(self.imageleft): 
                    self.frame = 0   
                    
            # Animate image
            if self.doClimb == True:
                self.image = self.imageclimb[self.frame]
            elif self.xmove < 0:
                self.image = self.imageleft[self.frame]
            elif self.xmove > 0:
                self.image = self.imageright[self.frame]
            
            self.last_update = t               
            
        # Determine x move direction
        self.setXMove()
       
        # Determine y move direction        
        if self.doClimb:
            self.setClimbMove()
        elif self.doElevator:
            self.setElevatorMove()
        else:
            self.setYMove()                
                                     
        # Adjust position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect = newpos
        
        # Correct position by elevator x movement 
        if self.doElevator:
            newpos = self.rect.move((self.elevator.xmove) , 0)
            self.rect = newpos                          

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print(">>>> removed")

    def collided(self):
        self.kill()
        print(">>>> collided")             

# Skull is shown when the player is dead
class Skull(AnimatedSprite):
        
    def __init__(self, xpos, ypos, skull, background):
        AnimatedSprite.__init__(self) #call Sprite initializer
                
        # Images and start image and first animation frame
        self.imageskull = self.sliceImage(40, 40, skull)
        self.image = self.imageskull[0]
        self.frame = 0    
        self.delay = 100

        # Reference to background and to logical background map        
        self.background = background
        
        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, 40, 40)
                                          
    # Update sprite on screen
    def update(self):
        
        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if (t - self.last_update) > self.delay:
            self.frame += 1
            if self.frame >= len(self.imageskull):
                self.frame = 0 
            self.image = self.imageskull[self.frame]
            self.last_update = t               
                            
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print( ">>>> removed")

    def collided(self):
        self.kill()
        print( ">>>> collided")             

# Fires burn the player
class Fire(AnimatedSprite):
    
    def __init__(self, xpos, ypos, imagename):
        AnimatedSprite.__init__(self) #call Sprite initialize
        
        # Images and start image
        self.fireimage = self.sliceImage(40, 40, imagename)
        self.image = self.fireimage[0]
        self.frame = 0
        self.fps = 10
        self.delay = 1000 / self.fps 

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])
                
    def update(self):
             
        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1
            self.last_update = t  
            
        if self.frame >= len(self.fireimage): 
            self.frame = 0                  
                     
        self.image = self.fireimage[self.frame]
            
    
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print( ">>>> fire removed")

    def collided(self):
        self.kill()
        print( ">>>> fire collided")

# Gems are collected by the player
class Gem(pygame.sprite.Sprite):
    
    def __init__(self, xpos, ypos, imagename):
        pygame.sprite.Sprite.__init__(self) #call Sprite initialize
        
        # Images and start image
        self.image = pygame.image.load(imagename)
        self.image.set_colorkey((0,0,0))

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])
                
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print( ">>>> gem removed")

    def collided(self):
        self.kill()
        print( ">>>> gem collided")
        
# The door leads to the next level
class Door(pygame.sprite.Sprite):
    
    def __init__(self, xpos, ypos, imagename):
        pygame.sprite.Sprite.__init__(self) #call Sprite initialize
        
        # Images and start image
        self.image = pygame.image.load(imagename)

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])
                
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print( ">>>> gem removed")

    def collided(self):
        self.kill()
        print( ">>>> gem collided")   
        
# Ladders can be climbed
class Ladder(pygame.sprite.Sprite):
    
    def __init__(self, xpos, ypos, imagename):
        pygame.sprite.Sprite.__init__(self) #call Sprite initialize
        
        # Images and start image
        self.image = pygame.image.load(imagename)

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1]) 

    def collided(self):
        self.kill()
        print( ">>>> ladder collided")

# Elevators are moving around
class Elevator(pygame.sprite.Sprite):
    
    def __init__(self, xpos, ypos, imagename, map):
        pygame.sprite.Sprite.__init__(self) #call Sprite initialize
        
        # Images and start image
        self.image = pygame.image.load(imagename)
        self.image.set_colorkey((0,0,0))

        # Map for tile requests
        self.map = map

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])
        
        # Fetch elevator tile environment tiles
        env = map.fetchTileEnvironmentForPosition(xpos, ypos)
        
        # Set elevator initial movement direction
        self.xmove = 0
        self.ymove = 0
        
        if env[0] == "o":
            self.ymove = -1
        elif env[1] == "o":
            self.xmove = 1
        elif env[2] == "o":
            self.ymove = 1
        elif env[3] == "o":
            self.xmove = -1
    
    # Update elevator position
    def update(self):
        
        # Determine if elevator direction has to be changed
        xcheck = self.rect.left + self.xmove
        ycheck = self.rect.top + self.ymove
        if self.xmove == 1:
            xcheck = xcheck + 40
        if self.ymove == 1:
            ycheck = ycheck + 40

        tile = self.map.fetchTileForPosition(xcheck, ycheck, True)
        if tile != "o" and tile != "O":
            self.xmove = -self.xmove
            self.ymove = -self.ymove
        
        # Adjust position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect = newpos 

# bats are moving around
class Bat(AnimatedSprite):
    
    def __init__(self, xpos, ypos, imagename, map):
        AnimatedSprite.__init__(self) #call Sprite initialize
        
        # Images and start image
        self.image = pygame.image.load(imagename)
        self.image.set_colorkey((0,0,0))

        # Images and start image and first animation frame
        self.batimage = self.sliceImage(40, 40, imagename)
        self.image = self.batimage[0]
        self.frame = 0  
        self.fps = 10
        self.delay = 1000 / self.fps         

        # Map for tile requests
        self.map = map

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])
        
        # Fetch bat tile environment tiles
        env = map.fetchTileEnvironmentForPosition(xpos, ypos)    
        
        # Set bat initial movement direction
        self.xmove = 0
        self.ymove = 0

        if env[1] == "v" or env[0] == "y":
            self.xmove = 1
        elif env[0] == "v" or env[0] == "y":
            self.ymove = -1            
        elif env[2] == "v" or env[0] == "y":
            self.ymove = 1
        elif env[3] == "v" or env[0] == "y":
            self.xmove = -1
     
    # Update bat position
    def update(self):
        
        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1
            self.last_update = t 
           
            if self.frame >= len(self.batimage): 
                self.frame = 0         
                    
            self.image = self.batimage[self.frame] 
        
        # Determine if bat direction has to be changed
        xcheck = self.rect.left + self.xmove
        ycheck = self.rect.top + self.ymove
        if self.xmove == 1:
            xcheck = xcheck + 40
        if self.ymove == 1:
            ycheck = ycheck + 40

        tile = self.map.fetchTileForPosition(xcheck, ycheck, False)
        if tile != "v" and tile != "V" and tile != "y":
            self.xmove = -self.xmove
            self.ymove = -self.ymove
        
        # Adjust position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect = newpos 

# Player must avoid contact with monster
class Monster(AnimatedSprite):
    
    def __init__(self, xpos, ypos, monsterleft, monsterright, background, map):
        AnimatedSprite.__init__(self) #call Sprite initialize
        
        # Init monster move direction
        self.xpos = xpos;
        self.ypos = ypos;
        self.xmove = 0.4
        
        # Images and start image and first animation frame
        self.monsterleft = self.sliceImage(40, 40, monsterleft)
        self.monsterright = self.sliceImage(40, 40, monsterright)
        self.image = self.monsterright[0]
        self.frame = 0  
        self.fps = 5
        self.delay = 1000 / self.fps         
    
        # Map for tile requests
        self.map = map
        
        # Background
        self.background = background
    
        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1]) 

    def update(self):
        
        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1
            self.last_update = t  
            
        if self.frame >= len(self.monsterleft): 
            self.frame = 0                  
                             
        # Determine x position of check
        if self.xmove < 0:
            xcheck = self.rect.left - 1
            self.image = self.monsterleft[self.frame]        
            
        elif self.xmove > 0:
            xcheck = self.rect.left + 41
            self.image = self.monsterright[self.frame]                    
        else:
            return
        
        # Perform check
        tile = self.map.fetchTileForPosition(xcheck, self.rect.top+41, 0)
        pix1 = self.background.get_at((xcheck, self.rect.top+41))       
        pix2 = self.background.get_at((xcheck, self.rect.top+20))
        if (pix1 == THECOLORS['black'] or pix2 != THECOLORS['black']) \
            and tile != "l" and tile != "y":
            self.xmove = -self.xmove 
               
        # Adjust position
        self.xpos = self.xpos + self.xmove
        self.rect = Rect(self.xpos, self.ypos, self.image.get_size()[0], self.image.get_size()[1]) 

        
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print( ">>>> monster removed")

    def collided(self):
        self.kill()
        print( ">>>> monster collided")
                
         
# Main class controlling the game
class ForbiddenCave:
    
   # Initialize game controller
   def __init__(self):     
       pygame.init() # Initialize pygame environment 
       
       self.screen = None
       self.background = None
       self.map = None
       self.yoff = 40
       
       # Game state constants
       self.GAMESTATE_DOOR = 0
       self.GAMESTATE_DEAD = 1
       self.GAMESTATE_QUIT = 2
       
       # Game state variables       
       self.gemcnt = 0
       self.lives = 5
       self.levelcnt = -1
       self.totallevelcnt = 0
       self.bonus = 0
       self.beginbonus = 3000
       self.lastBonusDecTime = 0
       self.score = 0
       self.bonusscore = 0
       self.highscore = 0

       self.frameCounter = 0 
       
       # Level maps
       self.maps = [ PATH_MAPS + "level2.txt", PATH_MAPS + "level2.txt", PATH_MAPS + "level3.txt", PATH_MAPS + "level4.txt", \
                     PATH_MAPS + "level5.txt", PATH_MAPS + "level6.txt", PATH_MAPS + "level7.txt", PATH_MAPS + "level8.txt" ] 
       
       # Sounds
       self.gemSound = self.loadSound(PATH_SOUND + "gem.wav")    
       self.jumpSound = self.loadSound(PATH_SOUND + "jump.wav")  
       self.deadSound = self.loadSound(PATH_SOUND + "dead.wav") 
       self.bonusSound = self.loadSound(PATH_SOUND + "bonus.wav")
       self.doorSound = self.loadSound(PATH_SOUND + "door.wav") 
       self.startSound = self.loadSound(PATH_SOUND + "start.wav") 
       self.doneSound = self.loadSound(PATH_SOUND + "done.wav") 
       self.overSound = self.loadSound(PATH_SOUND + "over.wav") 
    
   # load sound
   def loadSound(self, name):
        class NoneSound:
            def play(self): pass
        if not pygame.mixer or not pygame.mixer.get_init():
            return NoneSound()
        fullname = name
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error as message:
            print( 'Cannot load sound:', fullname)
            raise(SystemExit, message)
        return sound    
     
   # Initialize the game window
   def initWindow(self, width, height):
       
       self.screen = pygame.display.set_mode((width, height))
       pygame.display.set_caption('Forbidden Cave')
       pygame.mouse.set_visible(1)
        
   # Start game
   def start(self):
       self.initWindow(1040, 680)
       
       result = 0
       while result != self.GAMESTATE_QUIT:
           # Show welcome screen
           result = self.doWelcomeLoop()
           if result == self.GAMESTATE_QUIT:
               return # end game
                  
           # Start game
           self.lives = 3
           self.score = 0
           self.bonusscore = 0
           self.levelcnt = -1
           self.totallevelcnt = 0 
           while True:
               
               # Next level
               self.lastBonusDecTime = pygame.time.get_ticks()
               self.levelcnt += 1
               self.totallevelcnt += 1
               if self.levelcnt >= len(self.maps):
                   self.levelcnt = 0
                   self.beginbonus -= 500           
               self.map = LevelMap(PATH_IMAGES + "wall.png", PATH_IMAGES + "wall1.png", PATH_IMAGES + "wall2.png", self.maps[self.levelcnt], self.yoff)           
               
               # Process game
               result = self.doMainLoop()
               
               # Abort if quit or dead
               if result == self.GAMESTATE_DEAD or \
                  result == self.GAMESTATE_QUIT:               
                   break
               else:
                # Add bonus to score
                self.score += self.bonus           
                self.doLevelDoneLoop()
                
                # Check bonus life
                self.bonusscore += self.bonus
                if self.bonusscore >= 5000:
                    self.bonusscore -= 5000
                    self.lives += 1
             
           # Game over!
           if result == self.GAMESTATE_DEAD:
               self.doGameOverLoop()
    
   # Add text to provided background
   def addText(self, text, background, xpos, ypos, \
                color=(255,255,255), bgcolor=(0,0,0), size=22, center=False, rightpad=0):
    
        font=pygame.font.Font("OptaneBold.ttf", size)
        text=font.render(text, 4, color)
        textpos=text.get_rect()
        textpos.left=0
        textpos.top=0
        if center == True:
            xpos = background.get_width()/2 - textpos.width/2
        cleanrec=(xpos-1, ypos-1, textpos.width+1+rightpad, textpos.height)
        if bgcolor!=None:
            background.fill(bgcolor, cleanrec);
        background.blit(text, (xpos, ypos));    
    
   # Show welcome screen
   def doWelcomeLoop(self):
       
        # Load map for screen bounds decoration
        map = LevelMap(PATH_IMAGES + "wall.png", PATH_IMAGES + "wall1.png", PATH_IMAGES + "wall2.png", "welcome.txt", 0) 
        background = map.fetchLevelSurface() 
        
        self.addText("Forbidden Cave", background, 0, 80, (255,48,48), THECOLORS['black'], 80, True)
        self.addText("by Heiko Nolte, written May 2011", background, 0, 190, (209,209,209), THECOLORS['black'], 18, True)
        self.addText("Version 1.0", background, 0, 210, (209,209,209), THECOLORS['black'], 12, True)
        self.addText("You have dared to enter:", background, 0, 250, (255,193,37), THECOLORS['black'], 25, True)
        self.addText("Collect all gems to proceed to the next level.", background, 0, 280, (255,193,37), THECOLORS['black'], 25, True)
        self.addText("Use the arrow keys to control your movement.", background, 0, 310, (255,193,37), THECOLORS['black'], 25, True)
        self.addText("Press space to jump.", background, 0, 340, (255,193,37), THECOLORS['black'], 25, True)
        self.addText("Highscore: " + str(self.highscore), background, 0, 400, THECOLORS["cyan"], THECOLORS['black'], 30, True)
        self.addText("Press space to start game  ", background, 0, 500, (255,48,48), THECOLORS['black'], 40, True)
      
        
        # Repeat until space or quit pressed
        while True:    
           # Handle key events
           for event in pygame.event.get():
               if event.type == QUIT:
                   return self.GAMESTATE_QUIT
               if event.type == KEYDOWN:
                   if event.key == 32:
                       return
                  
           self.screen.blit(background, (0, 0)) 
           pygame.display.flip()  
       
   # Display level completed information box
   def doLevelDoneLoop(self):
        
        # Calculate info box coordinates      
        width = 400
        height = 200
        left = self.background.get_rect().width / 2 - width / 2
        top = self.background.get_rect().height / 2 - height / 2
        rect = Rect(left, top, height, width)
        
        self.doneSound.play(6)
        begin = pygame.time.get_ticks()
        tsize = 25
        timediff = 0
        lasttimediff = 0
        while timediff < 5000:
           
           timediff = pygame.time.get_ticks() - begin
                      
           # Catch QUIT key event
           for event in pygame.event.get():
               if event.type == QUIT:
                   return self.GAMESTATE_QUIT               
           
           # Create info box 
           infobox = pygame.Surface((width, height))
           infobox = infobox.convert()
           infobox.fill((135,206,250))
            
           # Add texts to infobox
           self.addText("Level " + str(self.totallevelcnt) + " completed.", infobox, 0, 30, THECOLORS["black"], (135,206,250), 25, True)      
           self.addText("Bonus: " + str(self.bonus), infobox, 0, 80, THECOLORS["black"], (135,206,250), 23, True)      
           self.addText("Get ready for next level!", infobox, 0, 130, THECOLORS["black"], (135,206,250), tsize, True)
           
           # Change ready text size
           if timediff - lasttimediff > 100:
               tsize += 1
               if tsize > 30: tsize = 25
               lasttimediff = timediff       
                          
           # Draw infobox
           self.screen.blit(infobox, (left, top))                   
           pygame.display.flip()  
           
           
   # Display game over information box
   def doGameOverLoop(self):
        
        # Calculate info box coordinates      
        width = 300
        height = 120
        left = self.background.get_rect().width / 2 - width / 2
        top = self.background.get_rect().height / 2 - height / 2
        rect = Rect(left, top, height, width)
        
        self.overSound.play()
        begin = pygame.time.get_ticks()
        tsize = 20
        timediff = 0
        lasttimediff = 0
        while timediff < 6000:
           
           timediff = pygame.time.get_ticks() - begin
                      
           # Catch QUIT key event
           for event in pygame.event.get():
               if event.type == QUIT:
                   return self.GAMESTATE_QUIT               
           
           # Create info box 
           infobox = pygame.Surface((width, height))
           infobox = infobox.convert()
           infobox.fill((255,246,143))
                      
           # Add texts to infobox
           self.addText("Game over!", infobox, 0, 18, THECOLORS["black"], (255,246,143), 25, True)      
           self.addText("Final score: " + str(self.score), infobox, 0, 55, THECOLORS["black"], (255,246,143), 23, True)      
           
           # Highscore
           if self.score > self.highscore:
               self.addText("A new highscore!", infobox, 0, 85, THECOLORS["black"], (255,246,143), 20, True)      
           
           # Change ready text size
           if timediff - lasttimediff > 50:
               tsize += 1
               if tsize > 30: tsize = 20
               lasttimediff = timediff       
                          
           # Draw infobox
           self.screen.blit(infobox, (left, top))                   
           pygame.display.flip() 
           
        # Set new highscore
        if self.score > self.highscore:
            self.highscore = self.score                             
                              
   # Main loop to control gameplay
   def doMainLoop(self):
       
       # Fetch self.background from loaded map
       self.background = self.map.fetchLevelSurface()

       ##################################################
       ### Fetch sprite groups
       ##################################################
       gemgroup = self.map.fetchGemgroup()
       self.gemcnt = len(gemgroup)
       monstergroup = self.map.fetchMonstergroup()
       laddergroup = self.map.fetchLaddergroup()
       elevatorgroup = self.map.fetchElevatorgroup()
       firegroup = self.map.fetchFiregroup()
       doorgroup = self.map.fetchDoorgroup()
       batgroup = self.map.fetchBatgroup()
       collgroup = None

       # Draw screen
       self.screen.blit(self.background, (0, 0))
       pygame.display.flip()
     
       ##################################################
       ### Main loop
       ##################################################
       clock=pygame.time.Clock()
       loopstate = 1
       doorsoundPlayed = False
       while self.lives > 0:
           
           # Create player sprite 
           self.startSound.play()
           player = Player(40, 600, PATH_IMAGES + "playerLeft.png", PATH_IMAGES + "playerRight.png", PATH_IMAGES + "playerClimb.png", PATH_IMAGES + "scull.png", \
                           self.background, self.map)
           
           playergroup = pygame.sprite.RenderPlain()
           playergroup.add(player)              
           
           self.bonus = self.beginbonus
           while loopstate == 1:
               clock.tick(100) # fps  
               
               # Decrease bonues
               time = pygame.time.get_ticks()
               if pygame.time.get_ticks() - self.lastBonusDecTime > 5000:                   
                   if self.bonus > 0:
                       self.bonusSound.play()
                       self.bonus -= 100
                       self.lastBonusDecTime = time  
               if self.bonus == 0:   
                   loopstate = 0 # Life lost           
    
               ##################################################
               ### Handle input events
               ##################################################
               
               for event in pygame.event.get():
                   if event.type == QUIT:
                       return self.GAMESTATE_QUIT
                   if event.type == KEYDOWN:
                       if event.key == K_SPACE or event.key == K_UP: # up
                           if (player.jump == 0 and player.ymove == 0) \
                                or player.doElevator == True:
                            self.jumpSound.play()
                            player.jump = -5.2
                            player.climbMove = 0
                            player.doClimb = False
                            player.doElevator = False
                            player.elevator = None
                       if event.key == K_LEFT: # left
                            player.xmove = -1 
                       if event.key == K_RIGHT: # right
                            player.xmove = 1
                       if event.key == K_UP: # up
                           if player.canClimb:
                                player.doClimb = True
                                player.climbMove = -1
                       if event.key == K_DOWN : # down                    
                           if player.canClimb:
                                player.doClimb = True
                                player.climbMove = 1                        
                   elif event.type == KEYUP:
                       if event.key == K_RIGHT and player.xmove > 0:
                           player.xmove = 0
                       if event.key == K_LEFT and player.xmove < 0:
                           player.xmove = 0
                       if event.key == K_UP or event.key == K_DOWN and player.doClimb:
                           player.climbMove = 0  
                           player.doClimb = False                  
                                              
               ##################################################
               ### Update state of sprites
               ##################################################
               
               gemgroup.update()
               monstergroup.update()
               laddergroup.update()
               elevatorgroup.update()
               batgroup.update()
               playergroup.update()
               firegroup.update()

               # Player AI
               if not player.ai:
                player.ai = PlayerAI.PlayerAI(player, self.map.textmap, self.screen)
               
               self.frameCounter += 1
               if self.frameCounter == UPDATE_AI_FRAME:
                player.ai.findGem(gemgroup)
                self.frameCounter = 0
         

               ##################################################
               ### print( game state
               ################################################## 
               
               self.addText("Bonus: " + str(self.bonus), self.background, 10, 5, THECOLORS['lightblue'], THECOLORS['black'], 22, False, 30)
               self.addText("Score: " + str(self.score), self.background, 450, 5, THECOLORS['orange'])            
               self.addText("Lives: " + str(self.lives), self.background, 950, 5, THECOLORS['green'])                
                
               ##################################################
               ### Draw self.background and sprites on screen
               ################################################## 
                      
               self.screen.blit(self.background, (0, 0)) 
               laddergroup.draw(self.screen)
               playergroup.draw(self.screen)            
               elevatorgroup.draw(self.screen)
               gemgroup.draw(self.screen)          
               firegroup.draw(self.screen)
               monstergroup.draw(self.screen)
               batgroup.draw(self.screen) 
               if(self.gemcnt == 0):
                   if not doorsoundPlayed:
                       self.doorSound.play()
                       doorsoundPlayed = True
                   doorgroup.draw(self.screen)
               #self.screen.blit(pygame.image.load(PATH_IMAGES + "gem.png"), PlayerAI.map_to_screen((26,16)))                  
               pygame.display.flip()  
               
               ##################################################
               ### Perform collision handling
               ##################################################     
        
               # Check if player has fallen too long
               if player.jumpDead == True:
                   loopstate = 0
        
               # Check player with gem collisions          
               collgroup = pygame.sprite.spritecollide(player, gemgroup, 0)
               pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
               if len(pixelgroup):
                   self.gemSound.play()
                   self.gemcnt -= 1
                   self.score += 100
                   self.bonusscore += 100
                   if self.bonusscore >= 5000:
                        self.bonusscore -= 5000
                        self.lives += 1
                   gemgroup.remove(pixelgroup[0])
    
               # Check player with fire collisions          
               collgroup = pygame.sprite.spritecollide(player, firegroup, 0)
               pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
               if len(pixelgroup):
                   print( "fire collision")
                   loopstate = 0
               
               # Check player with bat collisions          
               collgroup = pygame.sprite.spritecollide(player, batgroup, 0)
               pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
               if len(pixelgroup):
                   print( "bat collision")
                   loopstate = 0
               
               # Check player with door collisions
               if self.gemcnt == 0:          
                   collgroup = pygame.sprite.spritecollide(player, doorgroup, 0)
                   if len(collgroup):
                       print( "door collision")
                       return self.GAMESTATE_DOOR
        
               # Check player with ladder collisions
               tile1 = self.map.fetchTileForPosition(player.rect.left+5, int(player.rect.top+40+1), False)  
               tile2 = self.map.fetchTileForPosition(player.rect.left+35, int(player.rect.top+40+1), False)      
               collgroup=pygame.sprite.spritecollide(player, laddergroup, 0)
               if len(collgroup) > 0:
                    # Collision with ladder sprite
                    player.canClimb = True
               elif (tile1 == "l" and tile2 == "l") or (tile1 == "y" and tile2 == "y"):
                    # Ladder is right below player
                    player.canClimb = True
               else:
                    # No ladder
                    player.canClimb = False
                    player.doClimb = False
                    player.climbMove = 0
                
               # Check player with monster collisions          
               collgroup = pygame.sprite.spritecollide(player, monstergroup, 0)
               pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
               if len(pixelgroup) > 0:
                    print( "monster collision")
                    loopstate = 0

               # Check player with elevator collisions
               collgroup = pygame.sprite.spritecollide(player, elevatorgroup, 0)
               if len(collgroup) > 0:
                    # Calculate check coordinates
                    xcheck1 = player.rect.left + 10
                    xcheck2 = player.rect.left + player.rect.width - 10
                    ycheck = player.rect.top + player.rect.height + 1
                    
                    # Check against elevator
                    elevator = collgroup[0]
                    pix1 = self.background.get_at((xcheck1+5, int(player.rect.top+41)))
                    pix2 = self.background.get_at((xcheck2-5, int(player.rect.top+41))) 
                    if ycheck < elevator.rect.top + elevator.rect.height / 4 and  \
                       xcheck1 < elevator.rect.left + elevator.rect.width and \
                       xcheck2 > elevator.rect.left and \
                       pix1 == THECOLORS["black"] and \
                       pix2 == THECOLORS["black"]:
                        player.doElevator = True 
                        player.elevator = elevator
                        player.rect.top = elevator.rect.top - player.rect.height + 1
                        if(player.jump > player.deadJumpCnt): 
                              loopstate = 0
                        player.jump = 0 
                    else:
                        player.doElevator = False
                        player.elevator = None
               else:
                    player.doElevator = False
                    player.elevator = None
                    
           # end while loopstate = 1 loop
           self.lives -= 1 # deduct one life
           
           # Skull sprite
           self.deadSound.play()
           skull = Skull(player.rect.left, player.rect.top, PATH_IMAGES + "scull.png", self.background) 
           skullgroup = pygame.sprite.RenderPlain()  
           skullgroup.add(skull)
           
           # stop game for a certain time when player is dead
           begin = pygame.time.get_ticks()
           while 1:
               
               # Catch QUIT key event
               for event in pygame.event.get():
                   if event.type == QUIT:
                       return self.GAMESTATE_QUIT               
               
               # Check if loop will be left
               current = pygame.time.get_ticks()
               if current - begin > 2000:
                   break 
               
               ##################################################
               ### Draw Skull on screen
               ################################################## 
               skull.update()       
               skullgroup.draw(self.screen) 
               self.addText("Lives: " + str(self.lives), self.screen, 950, 5, THECOLORS['green'])                             
               pygame.display.flip()                 
           
           if self.lives > 0:
               loopstate = 1 # continue game if lives are left 
           else:
               # Game over
               return self.GAMESTATE_DEAD

# Entrypoint
def main():
    game = ForbiddenCave()
    game.start()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()