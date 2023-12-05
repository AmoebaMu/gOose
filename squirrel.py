# Original Code with group member comments*****
# rb - Rukia Beduni, ak - Amy Kusnandar, np - Nashrah Purnita

# Squirrel Eat Squirrel (a 2D Katamari Damacy clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = (24, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90     # how far from the center the squirrel moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30    # how high the player bounces
STARTSIZE = 25       # how big the player starts off
WINSIZE = 300        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with

NUMGRASS = 80        # number of grass objects in the active area
NUMSQUIRRELS = 30    # number of squirrels in the active area
SQUIRRELMINSPEED = 3 # slowest squirrel speed
SQUIRRELMAXSPEED = 7 # fastest squirrel speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

"""
This program has three data structures to represent the player, enemy squirrels, and grass background objects. The data structures are dictionaries with the following keys:

Keys used by all three data structures:
    'x' - the left edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'y' - the top edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'rect' - the pygame.Rect object representing where on the screen the object is located.
Player data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'facing' - either set to LEFT or RIGHT, stores which direction the player is facing.
    'size' - the width and height of the player in pixels. (The width & height are always the same.)
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'health' - an integer showing how many more times the player can be hit by a larger squirrel before dying.
Enemy Squirrel data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'movex' - how many pixels per frame the squirrel moves horizontally. A negative integer is moving to the left, a positive to the right.
    'movey' - how many pixels per frame the squirrel moves vertically. A negative integer is moving up, a positive moving down.
    'width' - the width of the squirrel's image, in pixels
    'height' - the height of the squirrel's image, in pixels
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'bouncerate' - how quickly the squirrel bounces. A lower number means a quicker bounce.
    'bounceheight' - how high (in pixels) the squirrel bounces
Grass data structure keys:
    'grassImage' - an integer that refers to the index of the pygame.Surface object in GRASSIMAGES used for this grass object
"""

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))  #rb - pygame function that sets the icon on the windows title bar 
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT)) #rb - is a small image ideal 32 x 32 pixels on a surface object used as a windows icon. If not the ideal size, the image will be compressed. 
    pygame.display.set_caption('Squirrel Eat Squirrel')         
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)         #rb - sets the font which the game will be viewed in 

    # load the image files
    L_SQUIR_IMG = pygame.image.load('squirrel.png') #rb- This line is where the enemy and player squirrel images facing left are loaded, its noted to put png file in the same folder as gooseatgoose, failure to do so will result in a error.
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False) #rb- #image of squirrel facing left, using the transform.flip function it faces to the right. Function contains three parameters to flip, the image to flip, boolean value for horizontal, and another for vertical. If true for second parameter and false for third, it returns the image facing it's right. 
    GRASSIMAGES = []
    for i in range(1, 5):
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))

    while True:
        runGame() #rb- function rungame is called allowing game to begin


def runGame():
    # set up variables for the start of a new game
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    winMode = False           # if the player has won

    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You have achieved OMEGA SQUIRREL!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30) #rb- from line 93-103 are variables that appear on screen after after game ends. If won, text "You have achieved OMEGA SQUIRREL!" appears, when lost "press 'R' to restart".

    # camerax and cameray are the top left of where the camera view is
    camerax = 0 #rb- the 2D world which is where the game is played. Camerax represents the x-axis of the world. The further the world is located the smaller the x values. The value 0 represents the origin of the world, where the squirrel is originally located. This value is a limited portion of an infinite 2d space, since its impossible to fit it on screen.
    cameray = 0 #rb- represents the same idea as cameras, however in the y-axis. Depending on our camera x and y values, this created an area in which viewed by the player, areas outside these values can't be seen by the player.

    grassObjs = []    #rb- stores all the grass objects in the game, as new grass objects are created or removed, the list is updated.
    squirrelObjs = [] #rb- stores all the non-player squirrel objects, as new squirrel objects are created or removed, the list is updated.
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)), #rb- this variable is a dictionary value
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': MAXHEALTH}

    moveLeft  = False #ak- makes sure that the player isn't moving by itself when game first starts, until keys are pressed
    moveRight = False
    moveUp    = False
    moveDown  = False #rb- lines 120 to 123 are move variables that track which arrow/WASD keys are being used/held down

    # start off with some random grass images on the screen
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray)) #rb- the function makenewgrass creates grass object, this process takes place in an area not visible to the player. The function then returns the grass object on an area visible to the player. 
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT) #ak- assigns a random x and y coordinate for the grass to appear within the window height and width

    while True: # main game loop #rb- updates the game state, draw everything to the screen, and handles event.
        # Check if we should turn off invulnerability
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME: #rb- this is when the player gets hit by an enemy squirrel and doesn't die, instead the player becomes invulnerabe for a few seconds (the INVULNTIME constant determines the time). At this time the player's squirrel will start to flash and not take any damage from other squirrels. 
            invulnerableMode = False #rb- once the invulnerability mode time is over, then the invulnerableMode is set to false

        # move all the squirrels
        for sObj in squirrelObjs:
            # move the squirrel, and adjust for their bounce. #rb- The movex and movey keys help the enemy squirels move up and down. If the values are positive then, they'll move right or down, if negative, they'll move left or up. The larger the values, the faster they'll move.
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # reset bounce amount

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                if sObj['movex'] > 0: # faces right
                    sObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sObj['width'], sObj['height']))
                else: # faces left
                    sObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sObj['width'], sObj['height']))


        # go through all the objects and see if any need to be deleted.
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(squirrelObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, squirrelObjs[i]):
                del squirrelObjs[i]

        # add more grass & squirrels if we don't have enough.
        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray))
        while len(squirrelObjs) < NUMSQUIRRELS:
            squirrelObjs.append(makeNewSquirrel(camerax, cameray))

        # adjust camerax and cameray if beyond the "camera slack" (ak- the camera slack is the number of pixels the player can move before the camera/screen is updated)
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2) #ak- defines sort of the boundaries of where the camera displays the character, makes sure that the screen moves with the character
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2) #ak- the y coordinates of the border that the character needs to be in
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK: #ak- makes sure that the character is still within the screen/camera, x coordinates, helps make the character centered on screen
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH #ak- if the difference between the center and the character's x coordinate is bigger than the camera slack, which is the limit/border, the camera will move accordingly
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK: #ak- for the left direction, if statement above was for x coordinate being too far right
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH #ak- changes the camera position and not the characters
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK: #ak- same thing as above but for y coordinates of character and camera
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT #ak- for going up
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT #ak- for going down

        # draw the green background
        DISPLAYSURF.fill(GRASSCOLOR) #ak- colour was defined using rgb values at the beginning of the code, this colour fills the surface

        # draw all the grass objects on the screen
        for gObj in grassObjs: #ak- goes through the grass image files
            gRect = pygame.Rect( (gObj['x'] - camerax, #ak- creates a rectangular object with the parameters
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect) #ak- brings the grass images and displays it on the surface, blit copies the image surface and draws it onto the display surface


        # draw the other squirrels
        for sObj in squirrelObjs: #ak- similar to the grass image files, this does the same thing but for the squirrel file
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']), #ak- for the movement of the enemy squirrels, function below
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface'], sObj['rect']) #ak- displays the image onto the surface


        # draw the player squirrel
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1 #ak- flash for when the player squirrel is attacked by a larger squirrel and loses health, flashes the character and sort of erases the drawing of the squirrel
            #ak- to flash the character, it will be drawn and erased every tenth of a second and repeats/flashes for two seconds
            #to do so it grabs the current run time, rounds it to one decimal point and multiplies it by 10. The function checks if number is even or odd, if it is even then the function will be set to False (0==1)
            #since time is constantly moving, the function will switch between True and False, drawing and erasing the squirrel 
        if not gameOverMode and not (invulnerableMode and flashIsOn): #ak- if the game is running and the squirrel is not in its in invulnerable state when it is attacked
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax, #ak- same as with the objects above, displays the player squirrel onto the surface
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # draw the health meter
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT: #ak- event loop runs all the tasks and callbacks for the code to run
                terminate() #ak- if the QUIT event is running, then the code should terminate and stop
            #ak- below is the code for the keys that allow the player to move on the screen (using WASD directions)
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w): #ak- if W is pressed, the player should move up, which is why move down is false; sets the respective movement variables to either True or False
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change player image #ak- changes the player image to face the correct direction that it is going, this line checks that it's facing left
                        playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size'])) #ak- applies a transformation on the image to face left
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif winMode and event.key == K_r: #ak- for when the player wins the game, player presses r to run the game again, stops the old one and starts a new game
                    return

            elif event.type == KEYUP: #ak- for when the key is not pressed anymore, which is why it's called keyup, the key is up and not pressed down; makes sure that the player does not continue to move after key is pressed
                # stop moving the player's squirrel
                if event.key in (K_LEFT, K_a):
                    moveLeft = False #ak- sets the movement variable to false to stop the player from going in that direction
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE: #ak- if escape key is pressed, then the code will stop running, the game will stop
                    terminate()

        if not gameOverMode: #ak- only allows movement when the game is still running/not over
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE #ak- actually moves the player, changes the x values so that the position on the screen is changed according to the keys pressed from earlier
            if moveRight:
                playerObj['x'] += MOVERATE #ak - moverate is how fast the player is moving
            if moveUp:
                playerObj['y'] -= MOVERATE #ak- changes the y value coordinate of the player according to the keys that are pressed
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0: #ak- the playerObj['bounce'] part is what point of bouncing the player is, the bounce value 
                playerObj['bounce'] += 1 #ak- if the player stops moving but the bounce hasn't finished, makes sure that the bounce still finishes

            if playerObj['bounce'] > BOUNCERATE: #ak- makes sure that the bounce does not become larger than the bouncerate, keeps the bounce constant to the current rate
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any squirrels
            for i in range(len(squirrelObjs)-1, -1, -1): #ak- takes the list of squirrelObjs and starts at the last index, since a squirrel may or may not disappear when collisions happen
                sqObj = squirrelObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):
                    # a player/squirrel collision has occurred

                    if sqObj['width'] * sqObj['height'] <= playerObj['size']**2: #ak- checks and compares the sizes of the player and the collided squirrel
                        # player is larger and eats the squirrel
                        playerObj['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1 #ak- increases the size of the player squirrel based on the smaller squirrel collided
                        del squirrelObjs[i]

                        if playerObj['facing'] == LEFT: #ak- updates the size of the player image using the transform function in pygame, also accounts for direction facing
                            playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True # turn on "win mode"

                    elif not invulnerableMode:
                        # player is smaller and takes damage
                        invulnerableMode = True
                        invulnerableStartTime = time.time() #ak- starts the time for a short period of invulnerability 
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect) #ak- displays the game over text onto the surface created by the code
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game #ak- after a certain period of time, the game will restart and continue running the code

        # check if the player has won.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update() #ak- only updates a portion of the screen
        FPSCLOCK.tick(FPS) #ak- tracks the time to update the screen



def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars #np- the for loop on line 317 draws the filled-in red rectangle for the amount of health the player has
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10)) #np- display red rectangle on surface
    for i in range(MAXHEALTH): # draw the white outlines #np- the for loop on line 319 draws an unfilled white rectangle for all of the possible health the player could have 
        #np- (which is the integer value stored in the MAXHEALTH constant)
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate(): # finishes the game, exit #np- the python exit function # built-in method used to terminate a python script
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    #np- Returns the number of pixels to offset based on the bounce.
    #np- Larger bounceRate means a slower bounce.
    #np- Larger bounceHeight means a higher bounce.
    #np- currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity(): #np- randomly determine how fast an enemy squirrel will move - 50/50 chance that speed will be positive or negative, speed is either negative or positive
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH)) #np- creating rectangle of camera view
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT)) #np- creating rectangle of camera view
        #np- create a Rect object with the random coordinates and use colliderect()
        #np- to make sure the right edge isn't in the camera view.
        #np- check if the random XY coordinates would collide with the camera view’s Rect object
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewSquirrel(camerax, cameray):
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width']  = (generalSize + random.randint(0, 10)) * multiplier #np- width and height are set to random sizes to have variety
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = getRandomVelocity()
    sq['movey'] = getRandomVelocity()
    if sq['movex'] < 0: # squirrel is facing left
        sq['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sq['width'], sq['height']))
    else: # squirrel is facing right # it is larger than 0
        sq['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def makeNewGrass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width']  = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()
