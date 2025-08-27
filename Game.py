from ast import Raise
import time
import Setup
import MapCreator
import Menus
import Dijkstra

class GameHandler(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)
        self.player = Player("Temporary", self)
        self.background = GameBackground(self)
                                        
        self.playableMap = [] # 2d list of blocks
        self.weightedAdjacencyList = Dijkstra.AdjacencyList()
        self.dijkstraGraph = None
        self.pathfindingWaypointBlocks = []

        self.blocks = Setup.pg.sprite.Group() # a group of all blocks in the map for easier drawing
        self.entities = Setup.pg.sprite.Group()

        self.blockAttributeDictionary = {0 : [False, 0, 0],
                                     1 : [True, 0, 80],
                                     2 : [True, 0, 80],
                                     3 : [True, 0, 80],
                                     4 : [True, 0, 80],
                                     5 : [True, 0, 80],
                                     6 : [True, 0, 80],
                                     7 : [True, 0, 80],
                                     8 : [False, 10, 80], # spike start
                                     9 : [False, 10, 80],
                                     10 : [False, 10, 80],
                                     11 : [False, 10, 80],
                                     12 : [False, 10, 80],
                                     13 : [False, 10, 80], # spike end
                                     14 : [False, 0, 0],
                                     15 : [False, 0, 0],
                                     16 : [False, 0, 0],
                                     17 : [False, 0, 0],
                                     18 : [False, 0, 0],
                                     19 : [False, 0, 0],
                                     20 : [False, 0, 0],
                                     43 : [False, 0, 0], # friendly character start
                                     44 : [False, 0, 0],
                                     45 : [False, 0, 0],
                                     46 : [False, 0, 0],
                                     47 : [False, 0, 0], # friendly character end
                                     }# (collision with player, damage if any, knockback when hit (is increased if player takes damage from block)

        self.CreatePlayableMap()
        self.OpenSaveFile()

    def OpenSaveFile(self):
        self.filePath = Setup.os.path.join("ASSETS", "SAVED_DATA", f"SAVE_FILE_{Setup.setup.SAVE_SLOT}.txt")
        self.saveFile = open(self.filePath, "r")

    def CreatePlayableMap(self):
        self.playableMap = []
        self.waypoints = []
        self.treasureChests = []
        self.friendlyCharacters = []

        newRow = []

        for row in MapCreator.mapDataHandler.mapGrid.blockGrid:
            for block in row:
                if block.blockNumber <= 20 or (block.blockNumber >= 43 and block.blockNumber <= 47): # a block and not an entity - friendly characters only display text so are represented as a block
                    attributes = self.blockAttributeDictionary.get(block.blockNumber)

                    if attributes:
                        mapBlock = MapBlock(block.blockNumber, block.rotation, block.originalLocationX, block.originalLocationY, block.image, attributes[0], attributes[1], attributes[2])
                        newRow.append(mapBlock)
                     
                        if block.blockNumber != 0: # self.blocks will be used to display the blocks, block 0 is a filler block for the map creator and should not be visible in game
                            self.blocks.add(mapBlock)

                        if block.blockNumber == 17 or block.blockNumber == 18: # waypoints
                            self.waypoints.append(Waypoint(mapBlock))

                        if block.blockNumber == 19: # treasure chests
                            self.treasureChests.append(TreaureChest(mapBlock, "wooden sword")) # temp reward

                        if block.blockNumber >= 43 and block.blockNumber <= 47: # friendly characters
                            self.friendlyCharacters.append(FriendlyCharacter(mapBlock, block.blockNumber - 43)) # between 0 and 4
                    else:
                        raise ValueError("block has no attributes")

                else: # entities (bosses, enemies, pathFinders)
                    if block.blockNumber == 48:    
                        self.pathfindingWaypointBlocks.append(block) 

            self.playableMap.append(newRow)
            newRow = []

        self.PopulateGraph(self.pathfindingWaypointBlocks)

    def PopulateGraph(self, blocks):
        self.blockNumberToObject = {}

        unweightedAdjacencyList = {0 : [1],
                                   1 : [0, 2, 7],
                                   2 : [1, 3],
                                   3 : [2, 4],
                                   4 : [3, 5],
                                   5 : [4, 6, 7],
                                   6 : [5],
                                   7 : [1, 5, 8],
                                   8 : [7]
                                   }
        
        for block in blocks: # populate blockNumberToObject
            if block.DoesTextExist("PATHFINDING"):
                blockNodeNumber = int(block.textList[0].text)

                if blockNodeNumber not in self.blockNumberToObject:
                    self.blockNumberToObject.update({blockNodeNumber : block})
            
        for x in range(0, list(unweightedAdjacencyList.keys())[-1] + 1): # extract neighbours and populate weightedAdjacencyList
            if x in self.blockNumberToObject:
                block = self.blockNumberToObject[x] # orders the weightedGraph - better display of the grpah when printed

                if block.DoesTextExist("PATHFINDING"):
                    blockNodeNumber = int(block.textList[0].text)

                    if blockNodeNumber in unweightedAdjacencyList:
                        blockNeighbours = unweightedAdjacencyList[blockNodeNumber]            
                        blockNeighboursObjects = []

                        for neighbour in blockNeighbours:
                            if neighbour in self.blockNumberToObject:
                                blockNeighboursObjects.append(self.blockNumberToObject[neighbour])

                        self.weightedAdjacencyList.PopulateGraph(block, blockNeighboursObjects, blockNodeNumber, blockNeighbours)   

        #for keyValuePair in self.weightedAdjacencyList.weightedGraph.items():
        #    print("\n", keyValuePair)

        self.dijkstraGraph = Dijkstra.DijkstraImplementation(self.weightedAdjacencyList.weightedGraph)

class MapBlock(Setup.pg.sprite.Sprite): 
    def __init__(self, blockNumber, rotation, originalLocationX, originalLocationY, image, hasCollision, damage, knockback):
        super().__init__()
        self.blockNumber = blockNumber
        self.rotation = rotation
        self.worldX = originalLocationX
        self.worldY = originalLocationY

        self.width = Setup.setup.BLOCK_WIDTH
        self.height = Setup.setup.BLOCK_WIDTH

        self.image = Setup.pg.transform.scale(image, (self.width, self.height)) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.worldX, self.worldY)  

        self.collision = hasCollision 
        self.damage = damage
        self.knockback = knockback

class Spell():
    def __init__(self, name, description, damage, manaCost, parentPlayer):
        self.name = name
        self.description = description
        self.damage = damage
        self.manaCost = manaCost
        self.parentPlayer = parentPlayer

        self.currentState = "NONE" # "NONE" "SPELL"
        self.tempCounter = 0 # used until spells have an actual function

    def Attack(self, currentMana):
        if currentMana >= self.manaCost:
            self.parentPlayer.mana -= self.manaCost
            self.currentState = "SPELL"

    def Update(self):
        match self.currentState:
            case "SPELL":
                self.UseSpell()

    def UseSpell(self):
        if self.tempCounter >= 120:
            self.currentState = "NONE" # after the spell is finished
            self.tempCounter = 0 

        self.tempCounter += 1

class Weapon():
    def __init__(self, name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, images, parentPlayer): # images is a list of all the different filepaths for the corresponding attacks
        self.name = name
        self.description = description
        self.abilityDescription = abilityDescription
        self.damage = damage
        self.chargedDamage = chargedDamage
        self.abilityDamage = abilityDamage
        self.abilityManaCost = abilityManaCost
        self.abilityCooldown = abilityCooldown
        self.images = images
        self.parentPlayer = parentPlayer

        self.currentState = "NONE" # "NONE" "BASIC" "CHARGED" "ABILITY"
        self.isChargingAttack = False
        self.chargingStartTime = 0
        self.mostRecentAbilityTime = 0

        self.tempCounter = 0 # TODO - used until attacks have an actual function
        self.attackStart = 0

    def Attack(self, endInputTime):
        lengthOfAttackCharge = endInputTime - self.chargingStartTime # how long left click was held
        chargeAttackThreshold = 1 # second

        if self.currentState == "NONE":
            if lengthOfAttackCharge < chargeAttackThreshold:
                self.currentState = "BASIC"
            else:
                self.currentState = "CHARGED"

    def Ability(self, currentTime):
        if self.currentState == "NONE":
            if currentTime - self.mostRecentAbilityTime >= self.abilityCooldown:
                self.mostRecentAbilityTime = currentTime
                self.currentState = "ABILITY"

    def Update(self):
        match self.currentState:
            case "BASIC":
                self.attackStart = time.time()
                self.BasicAttack()
            case "CHARGED":
                self.attackStart = time.time()
                self.ChargedAttack()
            case "ABILITY":
                self.PerformAbility()

    def BasicAttack(self):
        if self.tempCounter >= 120:
            self.currentState = "NONE" # after the attack is finished
            self.tempCounter = 0

        self.tempCounter += 1
        

    def ChargedAttack(self):
        if self.tempCounter >= 120:
            self.currentState = "NONE" # after the attack is finished
            self.tempCounter = 0

        self.tempCounter += 1

    def PerformAbility(self):
        if self.tempCounter >= 120:
            self.currentState = "NONE" # after the attack is finished
            self.tempCounter = 0

        self.tempCounter += 1

class WoodenSword(Weapon):
    def __init__(self):
        super.__init__()

        self.basicAttackLength = 2 # seconds
        self.basicAttackSheet = 0

    def BasicAttack(self):
        if self.attackStart <= self.basicAttackLength:
            pass
            #attack     

class Inventory():
    def __init__(self, player):
        self.parentPlayer = player
        self.inventoryMainMenu = Menus.menuManagement.inventoryButtonGroup

    def UpdatePlayerModelScreen(self):
        Setup.pg.draw.rect(Setup.setup.screen, Setup.setup.BLACK, (0, 0, Setup.setup.WIDTH, Setup.setup.HEIGHT)) # background
        Setup.setup.screen.blit(self.parentPlayer.currentImage, (0, 0)) # current player image

class Player(Setup.pg.sprite.Sprite):
    def __init__(self, name, gameHandler):
        super().__init__()
        self.gameHandler = gameHandler

        self.name = name
        self.width = Setup.setup.BLOCK_WIDTH
        self.height = Setup.setup.BLOCK_WIDTH
        self.worldX = Setup.setup.WIDTH / 2
        self.worldY = Setup.setup.HEIGHT / 2

        self.maxHealth = 100 # temp
        self.maxMana = 100 # temp
        self.health = 100 # temp
        self.mana = 100 # temp

        self.camera = Camera(self)
        self.miniMap = MiniMap()
        self.weapon = Weapon("Wooden sword", "weapon", "ability", 100, 200, 300, 20, 5, None, self) # temp
        self.spell = Spell("Fireball", "fire", 100, 20, self) # temp
        self.inventory = Inventory(self)
        self.mapFragments = {1 : True, 2 : True, 3 : True, 4 : False}

        self.idleFilePath = Setup.os.path.join("ASSETS", "PLAYER", "PLAYER_IDLE_SHEET")
        self.idleImageSheet = Setup.pg.image.load(self.idleFilePath + ".png").convert_alpha()
        self.idleSheet = Setup.SpriteSheet(self.idleImageSheet, self, self.width * 8)

        self.jumpFilePath = Setup.os.path.join("ASSETS", "PLAYER", "PLAYER_JUMP_SHEET")
        self.jumpImageSheet = Setup.pg.image.load(self.jumpFilePath + ".png").convert_alpha()
        self.jumpSheet = Setup.SpriteSheet(self.jumpImageSheet, self, self.width * 8)

        self.state = "IDLE"
        self.currentFrame = 0
        self.currentSheet = self.idleSheet
        self.startTime = time.time()
        self.isCrouched = False

        # movement
        self.movementSpeeds = [0, 0]
        self.keyPressVelocity = 6
        self.mostRecentDirection = None
        self.playerYFallingSpeed = 0
        self.playerXCarriedMovingSpeed = 0 # dashing etc
        self.gravity = Setup.setup.GRAVITY 

        self.UpdateCurrentImage(False)

    def UpdateCurrentImage(self, flipImage):
        self.currentSheet.Update()
        self.currentImage = self.currentSheet.GetImage(self.currentFrame, self.width, self.height, 1)
        self.currentImage = Setup.pg.transform.scale(self.currentImage, (self.width, self.height)) 
        self.currentImage = Setup.pg.transform.flip(self.currentImage, flipImage, False)

        self.mask = Setup.pg.mask.from_surface(self.currentImage) 
        self.rect = self.mask.get_rect()
        self.rect.topleft = (self.worldX, self.worldY)

    def CollideWithObject(self, mapBlocks):
        collided = []
        self.rect.topleft = (self.worldX, self.worldY)

        for block in mapBlocks:
            if block.collision: # if the block can be collided with
                block.rect.topleft = (block.worldX, block.worldY) # using original locations for both the player and block to make collision less confusing

                if self.rect.colliderect(block.rect):
                    collided.append(block)

        return collided

    def Movement(self, mapBlocks):
        collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

        # horizontal movement
        self.worldX += self.movementSpeeds[0]
        self.rect.topleft = (self.worldX, self.worldY)

        for block in self.CollideWithObject(mapBlocks):
            if self.movementSpeeds[0] > 0: # moving right so colliding with the left side of the block (right side of the player)
                self.worldX = block.worldX - self.rect.width
                collisions['right'] = True

            elif self.movementSpeeds[0] < 0: # moving left so colliding with the right side of the block (left side of the player)
                self.worldX = block.worldX + block.rect.width
                collisions['left'] = True

            self.rect.topleft = (self.worldX, self.worldY)

        # vertical movement
        self.worldY += self.movementSpeeds[1]
        self.rect.topleft = (self.worldX, self.worldY)

        for block in self.CollideWithObject(mapBlocks):
            if self.movementSpeeds[1] > 0: # moving down so colliding with the top of the block (bottom of the player)
                self.worldY = block.worldY - self.rect.height
                collisions['bottom'] = True

            elif self.movementSpeeds[1] < 0: # moving up so colliding with the bottom of the block (top of the player)
                self.worldY = block.worldY + block.rect.height
                collisions['top'] = True

            self.rect.topleft = (self.worldX, self.worldY)

        return collisions

    def Inputs(self):
        keys = Setup.pg.key.get_pressed()

        if self.miniMap.enlarged and self.miniMap.seeWaypoints: # cannot move when currently at a waypoint - can move when viewing mini map normally
            self.movementSpeeds, self.playerXCarriedMovingSpeed = [0, 0], 0
        else:           
            self.OpenCloseInventory()
            self.OpenCloseInGameMenu()
            self.MovementKeyHandler(keys)
            self.JumpHandler(keys)
            self.DashHandler(keys)
            self.CrouchHandler(keys)

    def OpenCloseInventory(self):
        if Setup.setup.pressedKey == Setup.pg.K_i:
            Menus.menuManagement.ChangeStateOfMenu(self.inventory.inventoryMainMenu, "GAME", cursor=True)

            if Menus.menuManagement.inGameMenuButtonGroup in Menus.menuManagement.gameMenus:
                Menus.menuManagement.RemoveMenu(Menus.menuManagement.inGameMenuButtonGroup, "GAME")

    def OpenCloseInGameMenu(self):
        if Setup.setup.pressedKey == Setup.pg.K_TAB and self.inventory.inventoryMainMenu not in Menus.menuManagement.gameMenus:
            Menus.menuManagement.ChangeStateOfMenu(Menus.menuManagement.inGameMenuButtonGroup, "GAME", cursor=True)

    def MovementKeyHandler(self, keys):
        if keys[Setup.pg.K_d] or keys[Setup.pg.K_RIGHT]: # d key or right arrow key
            self.movementSpeeds[0] = self.keyPressVelocity

            if self.mostRecentDirection == "LEFT": # can cancel the dash if you press the opposite movemnt key
                self.playerXCarriedMovingSpeed = 0

            self.mostRecentDirection = "RIGHT"

        elif keys[Setup.pg.K_a] or keys[Setup.pg.K_LEFT]: # a key or left arrow key
            self.movementSpeeds[0] = -self.keyPressVelocity

            if self.mostRecentDirection == "RIGHT":
                self.playerXCarriedMovingSpeed = 0

            self.mostRecentDirection = "LEFT"
        else:
            self.movementSpeeds[0] = 0
        
    def JumpHandler(self, keys):
        if keys[Setup.pg.K_SPACE]:
            if self.state != "AIR": # pressing space (jump) and has contact with the ground
                self.isCrouched = False
                self.state = "AIR"
                self.playerYFallingSpeed = -20
                self.gravity = Setup.setup.GRAVITY

            elif self.movementSpeeds[1] < 0: # if the player is holding space while still moving upwards (different to falling)
                if self.gravity >= Setup.setup.GRAVITY * 0.4:
                    self.gravity *= 0.95

            elif self.movementSpeeds[1] > 0: # if the player is holding space while falling (constant falling speed)
                self.gravity = Setup.setup.GRAVITY * 0.25
        else:
            self.gravity = Setup.setup.GRAVITY

    def DashHandler(self, keys):
        if keys[Setup.pg.K_LSHIFT] and self.playerXCarriedMovingSpeed == 0: # pressing shift (dash) and not already in a dash
            if self.mostRecentDirection == "LEFT":
                self.playerXCarriedMovingSpeed = -32
            else:
                self.playerXCarriedMovingSpeed = 32

    def CrouchHandler(self, keys):
        if keys[Setup.pg.K_LCTRL] and self.state != "AIR":
            self.isCrouched = True

        elif not keys[Setup.pg.K_LCTRL]:
            self.isCrouched = False

        if self.isCrouched:
            self.keyPressVelocity = 3
        else:
            self.keyPressVelocity = 6     

    def Update(self):
        self.Inputs()

        if self.playerXCarriedMovingSpeed != 0:
            self.movementSpeeds[0] = self.playerXCarriedMovingSpeed

        self.movementSpeeds[1] = self.playerYFallingSpeed

        if self.playerXCarriedMovingSpeed < 0:
            self.playerXCarriedMovingSpeed += 1
        elif self.playerXCarriedMovingSpeed > 0:
            self.playerXCarriedMovingSpeed -= 1

        self.playerYFallingSpeed += self.gravity

        if self.playerYFallingSpeed > 30:
            self.playerYFallingSpeed = 30 

        collisions = self.Movement(self.gameHandler.blocks)

        if collisions['bottom']:
            self.currentSheet = self.idleSheet
            self.state = "IDLE"
            self.playerYFallingSpeed = 0
            self.gravity = Setup.setup.GRAVITY
            self.movementSpeeds[1] = 0
        else:
            self.state = "AIR"

        if collisions['top']:
            self.playerYFallingSpeed = 0
            self.movementSpeeds[1] = 0

        if collisions['left'] or collisions['right']: 
            self.movementSpeeds[0] = 0

        if self.mostRecentDirection == "LEFT":
            self.UpdateCurrentImage(True)
        else:
            self.UpdateCurrentImage(False)

        self.camera.Update()
        self.camera.DisplayMap()
        self.miniMap.ChangeScale()
        self.miniMap.DrawMap(self.gameHandler.blocks, self)
        self.miniMap.DrawWaypoints(self)
        self.miniMap.pathGuide.FindNearestNode(self)
        self.Attack()
        self.AbilitySpell()
        self.weapon.Update()
        self.spell.Update()

    def DrawFrame(self):
        if not self.miniMap.enlarged:
            drawX = self.worldX - self.camera.camera.left # always in centre of the screen
            drawY = self.worldY - self.camera.camera.top
            Setup.setup.screen.blit(self.currentImage, (drawX, drawY))

    def Attack(self):
        if Setup.pg.mouse.get_pressed()[0] and not self.weapon.isChargingAttack:
            self.weapon.isChargingAttack = True
            self.weapon.chargingStartTime = time.time()

        if not Setup.pg.mouse.get_pressed()[0] and self.weapon.isChargingAttack:
            currentTime = time.time()
            self.weapon.isChargingAttack = False
            self.weapon.Attack(currentTime)

    def AbilitySpell(self):
        keys = Setup.pg.key.get_pressed()

        if keys[Setup.pg.K_e]:
            currentTime = time.time()
            self.weapon.Ability(currentTime)

        if keys[Setup.pg.K_f]:
            self.spell.Attack(self.mana)

class GameBackground:
    def __init__(self, gameHandler):  
        self.gameHandler = gameHandler

        filePath = Setup.os.path.join("ASSETS", "BACKGROUND", "GAME_BACKGROUND_1_IMAGE")
        self.blockImage = Setup.setup.loadImage(filePath, Setup.setup.BLOCK_WIDTH * Setup.setup.BLOCKS_WIDE, Setup.setup.BLOCK_WIDTH * Setup.setup.BLOCKS_WIDE)

    def DrawImage(self):
        topLeftBlock = self.gameHandler.playableMap[0][0]
        Setup.setup.screen.blit(self.blockImage, (topLeftBlock.rect.left, topLeftBlock.rect.top))

class Prompt:
    def __init__(self, promptName, key):
        self.width = 64
        self.height = 64
        self.key = key
        self.imagePath = Setup.os.path.join("ASSETS", "PROMPTS", promptName)
        self.image = Setup.setup.loadImage(self.imagePath, self.width, self.height)
        self.active = False

    def Draw(self, parentBlock, camera):
        drawX = parentBlock.worldX - camera.left
        drawY = parentBlock.worldY - camera.top
        Setup.setup.screen.blit(self.image, (drawX, drawY))  
        
    def PromptInteractedWith(self):
        if self.active and Setup.setup.pressedKey == Setup.pg.key.key_code(self.key):
            return True

    def IsPlayerInRange(self, parentBlock, player, camera):
        if parentBlock.rect.colliderect(player.rect):
            self.active = True
            self.Draw(parentBlock, camera)
            return True
            
        self.active = False

class TreaureChest:
    def __init__(self, parentBlock, item):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.openedImage = MapCreator.mapDataHandler.mapGrid.blockSheetHandler.GetCorrectBlockImage(self.parent.blockNumber + 1, Setup.setup.BLOCK_WIDTH, Setup.setup.BLOCK_WIDTH, Setup.setup.BLOCK_WIDTH, Setup.setup.BLOCK_WIDTH, False, 0)
        self.chestOpened = False # TODO - saved data, has the waypoint been interacted with before
        self.reward = item

    def IsPlayerInRange(self, player, camera):
        if not self.chestOpened:
            if self.prompt.IsPlayerInRange(self.parent, player, camera):
                self.TreasureChestFunction()

    def TreasureChestFunction(self):
        if self.prompt.PromptInteractedWith():
            self.parent.image = self.openedImage
            self.chestOpened = True
            # TODO - reward item, save opened state

class Waypoint:
    def __init__(self, parentBlock):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.waypointActive = False # TODO - saved data, has the waypoint been interacted with before

    def IsPlayerInRange(self, player, camera):
        if self.prompt.IsPlayerInRange(self.parent, player, camera):
            self.MiniMapFunction(player)

    def MiniMapFunction(self, player):
        if self.prompt.PromptInteractedWith():
            self.waypointActive = True
            player.miniMap.enlarged = not player.miniMap.enlarged
            player.miniMap.seeWaypoints = True
            Setup.pg.mouse.set_visible(not Setup.pg.mouse.get_visible())
            player.miniMap.CreateWaypointButtons(player.gameHandler.waypoints)

class MiniMap(Setup.pg.sprite.Sprite):
    def __init__(self):
        self.width = 384
        self.height = 384
        self.enlarged = False
        self.seeWaypoints = False

        self.playerIconFile = Setup.os.path.join("ASSETS", "PROMPTS", "PLAYER_ICON_IMAGE")
        self.playerIconWidth = 32
        self.playerIconHeight = 32
        self.playerIconImage = Setup.setup.loadImage(self.playerIconFile, self.playerIconWidth, self.playerIconHeight)

        self.waypointButtons = Setup.pg.sprite.Group()
        
        self.pathGuide = PathGuide()

    def ChangeScale(self):
        if Setup.setup.pressedKey == Setup.pg.key.key_code("m"):
            self.enlarged = not self.enlarged 
            self.seeWaypoints = False
            Setup.pg.mouse.set_visible(False)

    def MapFragments(self, player, startX, startY, shrinkModifier):
        mapWidth = (48 * Setup.setup.BLOCK_WIDTH) / shrinkModifier
        fragmentWidthHeight = mapWidth / 2 # square fragements so widtgh and height are the same

        fragmentLocations = {1 : (startX, startY),
                              2 : (startX + mapWidth / 2, startY),
                              3 : (startX, startY + mapWidth / 2),
                              4 : (startX + mapWidth / 2, startY + mapWidth / 2)}

        for fragment, fragmentValue in player.mapFragments.items(): 
            if not fragmentValue:
                Setup.pg.draw.rect(Setup.setup.screen, (Setup.setup.BLACK), (fragmentLocations[fragment][0], fragmentLocations[fragment][1], fragmentWidthHeight, fragmentWidthHeight))

    def DrawMap(self, blocks, player):
        if not self.enlarged:
            shrinkModifier = 20
            startX = 20
            startY = Setup.setup.HEIGHT - 400
            Setup.pg.draw.rect(Setup.setup.screen, (Setup.setup.GREY), (startX, startY, self.width, self.height)) # background to draw on, easier to see map
        else:
            shrinkModifier = 8
            startX = 480
            startY = 60
            Setup.pg.draw.rect(Setup.setup.screen, (Setup.setup.GREY), (0, 0, Setup.setup.WIDTH, Setup.setup.HEIGHT))
        
        for block in blocks:
            newImage = Setup.pg.transform.scale(block.image, (block.width / shrinkModifier, block.height / shrinkModifier))
            newX, newY = block.worldX / shrinkModifier, block.worldY / shrinkModifier
            Setup.setup.screen.blit(newImage, (startX + newX, startY + newY))
        
        newPlayerX, newPlayerY = player.worldX / shrinkModifier, player.worldY / shrinkModifier
        
        self.pathGuide.DrawPathGuides(shrinkModifier, startX, startY, player.camera.camera, player)
        self.MapFragments(player, startX, startY, shrinkModifier)
        if not self.enlarged:  
            self.playerIconImage = Setup.setup.loadImage(self.playerIconFile, self.playerIconWidth, self.playerIconHeight)
            Setup.setup.screen.blit(self.playerIconImage, (startX + newPlayerX - (0.25 * 32), startY + newPlayerY - (0.5 * 32))) # adjusting icon location to be roughly centered on in-game player
        else:
            self.playerIconImage = Setup.setup.loadImage(self.playerIconFile, self.playerIconWidth * 2, self.playerIconHeight * 2)
            Setup.setup.screen.blit(self.playerIconImage, (startX + newPlayerX - (0.5 * 32), startY + newPlayerY - 32)) 

    def CreateWaypointButtons(self, waypoints):
        width, height = 64, 64
        shrinkModifier = 8
        startX = 480
        startY = 60

        self.waypointButtons.empty()

        for waypoint in waypoints:
            parentBlock = waypoint.parent
            locationX = startX + (parentBlock.worldX / shrinkModifier) + (0.25 * 64) - 6
            locationY = startY + (parentBlock.worldY / shrinkModifier) - (0.2 * 64)

            if not waypoint.waypointActive:
                canFastTravel = "NO"
                self.waypointButtons.add(Menus.Button(f"WAYPOINT {parentBlock.worldX} {parentBlock.worldY} {canFastTravel}", width, height, locationX, locationY, "INACTIVE_WAYPOINT_IMAGE"))
            else:
                canFastTravel = "YES"
                self.waypointButtons.add(Menus.Button(f"WAYPOINT {parentBlock.worldX} {parentBlock.worldY} {canFastTravel}", width, height, locationX, locationY, "ACTIVE_WAYPOINT_IMAGE"))

    def DrawWaypoints(self, player):
        if self.enlarged and self.seeWaypoints:
            self.waypointButtons.draw(Setup.setup.screen)
            self.ClickWaypoint(player)

    def ClickWaypoint(self, player):
        clicked = Menus.ButtonGroupMethods.CheckClicks(self.waypointButtons)

        if clicked != None:
            if "WAYPOINT" in clicked: 
                text = clicked.split()
                canFastTravel = text[3]

                if canFastTravel == "YES":
                    locationX = float(text[1])
                    locationY = float(text[2])
                    player.worldX = locationX
                    player.worldY = locationY
                    player.miniMap.enlarged = False
                    Setup.pg.mouse.set_visible(False)

class PathGuide:
    def __init__(self):
        self.path = []
        self.pathBlockObjects = []
        self.startNode = None
        self.endNode = None
        self.active = False
        self.mouseClickX, self.mouseClickY = None, None

    def FindNearestNode(self, player):
        keys = Setup.pg.key.get_pressed()
        pathfindingWaypointBlocks = player.gameHandler.pathfindingWaypointBlocks
        
        smallestDistancePlayer = Setup.sys.maxsize
        nearestNodePlayer = None

        smallestDistanceMouse = Setup.sys.maxsize
        nearestNodeMouse = None

        if player.miniMap.enlarged:
            if keys[Setup.pg.K_LCTRL]:
                Setup.pg.mouse.set_visible(True)

            if Setup.pg.mouse.get_visible():
                if Setup.pg.mouse.get_pressed()[0]: # left click
                    self.active = True
                    self.mouseClickX, self.mouseClickY = Setup.pg.mouse.get_pos()
                elif Setup.pg.mouse.get_pressed()[2]: # right click
                    self.active = False

        if self.active:
            for block in pathfindingWaypointBlocks:
                #----------------------------------------------------------- player
                distancePlayer = Setup.math.sqrt((block.originalLocationX - player.worldX) ** 2 + (block.originalLocationY - player.worldY) ** 2)
                
                if distancePlayer < smallestDistancePlayer:
                    if self.CheckIfBlockIsValid(player.gameHandler.blocks, player, block): # check if it doesnt intersect a block
                        smallestDistancePlayer = distancePlayer

                        if block.DoesTextExist("PATHFINDING"):
                            nearestNodePlayer = int(block.textList[0].text)
                #----------------------------------------------------------- mini map
                miniMapOffsetX, miniMapOffsetY = 480, 60
                miniMapScale = 8
                blockMiniMapX, blockMiniMapY = (block.originalLocationX // miniMapScale) + miniMapOffsetX, (block.originalLocationY // miniMapScale) + miniMapOffsetY

                distanceMouse = Setup.math.sqrt((blockMiniMapX - self.mouseClickX) ** 2 + (blockMiniMapY - self.mouseClickY) ** 2)

                if distanceMouse < smallestDistanceMouse:
                    smallestDistanceMouse = distanceMouse

                    if block.DoesTextExist("PATHFINDING"):
                        nearestNodeMouse = int(block.textList[0].text)

            if (nearestNodePlayer != self.startNode or nearestNodeMouse != self.endNode) and (nearestNodeMouse != None and nearestNodePlayer != None):         
                self.startNode = nearestNodePlayer
                self.endNode = nearestNodeMouse
                self.PerformAlgorithm(player) # only calculate new route if a node changes

    def CheckIfBlockIsValid(self, allBlocks, player, node):
        playerCoords = (player.worldX, player.worldY)
        nodeCoords = (node.originalLocationX, node.originalLocationY)

        for block in allBlocks:       
            if block.rect.clipline(playerCoords, nodeCoords) and block.collision:
                return False

        return True

    def PerformAlgorithm(self, player):
        blockNumberToObject = player.gameHandler.blockNumberToObject
        dijkstraGraph = player.gameHandler.dijkstraGraph

        dijkstraGraph.PerformAlgorithm(self.startNode, self.endNode)

        self.path = dijkstraGraph.RecallShortestPath(self.endNode)
        self.pathBlockObjects = []

        for blockNumber in self.path:
            if blockNumber in blockNumberToObject:
                self.pathBlockObjects.append(blockNumberToObject[blockNumber])

    def DrawPathGuides(self, shrinkModifier, startX, startY, camera, player): 
        if self.active: 
            if len(self.path) == 1: # draw from player to last waypoint
                playerCordsMini = (player.rect.centerx // shrinkModifier + startX, player.rect.centery // shrinkModifier + startY)
                blockCordsMini = ((self.pathBlockObjects[0].originalLocationX + Setup.setup.BLOCK_WIDTH // 2) // shrinkModifier + startX, (self.pathBlockObjects[0].originalLocationY + Setup.setup.BLOCK_WIDTH // 2) // shrinkModifier + startY)
                Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, playerCordsMini, blockCordsMini, 80 // shrinkModifier) 

                if not player.miniMap.enlarged:
                    playerCordsScreen = (player.rect.centerx - camera.left, player.rect.centery - camera.top)
                    blockCordsScreen = ((self.pathBlockObjects[0].originalLocationX + Setup.setup.BLOCK_WIDTH // 2) - camera.left, (self.pathBlockObjects[0].originalLocationY + Setup.setup.BLOCK_WIDTH // 2 - camera.top))
                    Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, playerCordsScreen, blockCordsScreen, 20)
                    Setup.pg.draw.circle(Setup.setup.screen, Setup.setup.RED, blockCordsScreen, 40)

            for blockIndex in range(0, len(self.path) - 1): 
                #----------------------------------------------------------- mini map
                blockStartX, blockStartY = self.pathBlockObjects[blockIndex].originalLocationX + Setup.setup.BLOCK_WIDTH // 2, self.pathBlockObjects[blockIndex].originalLocationY + Setup.setup.BLOCK_WIDTH // 2
                blockEndX, blockEndY = self.pathBlockObjects[blockIndex + 1].originalLocationX + Setup.setup.BLOCK_WIDTH // 2, self.pathBlockObjects[blockIndex + 1].originalLocationY + Setup.setup.BLOCK_WIDTH // 2
                playerCordsMini = (player.rect.centerx // shrinkModifier + startX, player.rect.centery // shrinkModifier + startY) 
                
                blockStartCordsMini = (blockStartX // shrinkModifier + startX, blockStartY // shrinkModifier + startY) 
                blockEndCordsMini = (blockEndX // shrinkModifier + startX, blockEndY // shrinkModifier + startY) 
                
                if blockIndex == 0: # draw from player to first waypoint
                    Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, playerCordsMini, blockStartCordsMini, 80 // shrinkModifier) 
                           
                Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, blockStartCordsMini, blockEndCordsMini, 80 // shrinkModifier) 
                #----------------------------------------------------------- main screen
                if not player.miniMap.enlarged:
                    playerCordsScreen = (player.rect.centerx - camera.left, player.rect.centery - camera.top) 
                    blockStartCordsScreen = (blockStartX - camera.left, blockStartY - camera.top) 
                    blockEndCordsScreen = (blockEndX - camera.left, blockEndY - camera.top) 
                   
                    if blockIndex == 0: # draw from player to first waypoint
                        Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, playerCordsScreen, blockStartCordsScreen, 20)         
                        
                    Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, blockStartCordsScreen, blockEndCordsScreen, 20)
                    Setup.pg.draw.circle(Setup.setup.screen, Setup.setup.RED, blockStartCordsScreen, 20)
                    Setup.pg.draw.circle(Setup.setup.screen, Setup.setup.RED, blockEndCordsScreen, 20)

class Camera:
    def __init__(self, player):
        self.width = Setup.setup.WIDTH
        self.height = Setup.setup.HEIGHT
        self.camera = Setup.pg.Rect(0, 0, self.width, self.height)
        self.player = player

    def Update(self):
        self.camera.center = self.player.rect.center

    def DisplayMap(self):
        blocks = self.player.gameHandler.blocks

        blocksWithPrompts = []
        waypoints = self.player.gameHandler.waypoints
        treasureChests = self.player.gameHandler.treasureChests
        friendlyCharacters = self.player.gameHandler.friendlyCharacters

        blocksWithPrompts.append(waypoints)
        blocksWithPrompts.append(treasureChests)
        blocksWithPrompts.append(friendlyCharacters)

        for block in blocks:
            drawX = block.worldX - self.camera.left
            drawY = block.worldY - self.camera.top
            Setup.setup.screen.blit(block.image, (drawX, drawY))

        for blocks in blocksWithPrompts:
            for block in blocks:
                block.IsPlayerInRange(self.player, self.camera)

class FriendlyCharacter(Setup.pg.sprite.Sprite):
    def __init__(self, parentBlock, friendlyCharacterNumber):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.textNumber = 0
        self.hasRewardedItem = False
        self.displayActive = False

        allItems = {0 : None,
                    1 : None,
                    2 : None,
                    3 : None,
                    4 : None}

        allText = {0 : ["Hi this is the first text, i will help you throughout the game", 
                        "Hi this is the second text", 
                        "Hi this is the third text",
                        "Hi this is the summary text"],
                    1 : ["Hi this is the first text, i will help you throughout the game"],
                    2 : ["Hi this is the first text, i will help you throughout the game"],
                    3 : ["Hi this is the first text, i will help you throughout the game"],
                    4 : ["Hi this is the first text, i will help you throughout the game"]}

        self.text = allText[friendlyCharacterNumber]
        self.item = allItems[friendlyCharacterNumber]

    def IsPlayerInRange(self, player, camera):
        if self.prompt.IsPlayerInRange(self.parent, player, camera):
            self.FriendlyCharacterChestFunction(player) 
        else:
            self.displayActive = False

    def FriendlyCharacterChestFunction(self, player):
        if self.prompt.PromptInteractedWith() or self.displayActive:
            self.displayActive = True
            Setup.pg.draw.rect(Setup.setup.screen, Setup.setup.BLACK, (500, Setup.setup.HEIGHT * (4 / 5), 920, Setup.setup.HEIGHT // 5))
            textToDraw = Setup.TextMethods.CreateText(f"{self.textNumber}", self.text[self.textNumber], Setup.setup.WHITE, Setup.setup.WIDTH // 2, Setup.setup.HEIGHT * (4.5 / 5), 30)
            textToDraw.Draw()

            if Setup.setup.pressedKey == Setup.pg.K_RETURN:
                if self.textNumber < len(self.text) - 1:
                    self.textNumber += 1
                else:
                    self.displayActive = False
                    # REWARD ITEM - use player parameter

gameHandler = GameHandler()
