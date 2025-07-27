import time
import Setup
import MapCreator
import Menus

class GameHandler(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)
                                        
        self.playableMap = [] # 2d list of blocks
        self.entityMap = [] # will be format [[[]]]

        self.blocks = Setup.pg.sprite.Group() # a group of all blocks in the map for easier drawing

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
                                     }# (collision with player, damage if any, knockback when hit (is increased if player takes damage from block)

    def CreatePlayableMap(self):
        self.playableMap = []
        self.waypoints = []
        newRow = []

        for row in MapCreator.mapGrid.blockGrid:
            for block in row:
                if block.blockNumber <= 20: # a block and not an entity
                    attributes = self.blockAttributeDictionary.get(block.blockNumber)

                    mapBlock = MapBlock(block.blockNumber, block.rotation, block.originalLocationX, block.originalLocationY, block.image, attributes[0], attributes[1], attributes[2])
                    newRow.append(mapBlock)
                     
                    if block.blockNumber != 0: # self.blocks will be used to display the blocks, block 0 is a filler block for the map creator and should not be visible in game
                        self.blocks.add(mapBlock)

                    if block.blockNumber == 17 or block.blockNumber == 18: # waypoints
                        self.waypoints.append(Waypoint(mapBlock))

            self.playableMap.append(newRow)
            newRow = []

class MapBlock(Setup.pg.sprite.Sprite): 
    def __init__(self, blockNumber, rotation, originalLocationX, originalLocationY, image, hasCollision, damage, knockback):
        super().__init__() # init the sprite class
        self.blockNumber = blockNumber
        self.rotation = rotation
        self.world_x = originalLocationX
        self.world_y = originalLocationY

        self.width = 160
        self.height = 160

        self.image = Setup.pg.transform.scale(image, (self.width, self.height)) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.world_x, self.world_y)  

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

        self.tempCounter = 0 # used until attacks have an actual function
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
       

class Player(Setup.pg.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.width = 160
        self.height = 160
        self.world_x = Setup.setup.WIDTH // 2
        self.world_y = Setup.setup.HEIGHT // 2

        self.health = 100 # temp
        self.mana = 100 # temp

        self.camera = Camera(self)
        self.miniMap = MiniMap()
        self.weapon = Weapon("Wooden sword", "weapon", "ability", 100, 200, 300, 20, 5, None, self) # temp
        self.spell = Spell("Fireball", "fire", 100, 20, self) # temp

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
        self.keyPressVelocity = 8
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
        self.rect.topleft = (self.world_x, self.world_y)

    def CollideWithObject(self, mapBlocks):
        collided = []
        self.rect.topleft = (self.world_x, self.world_y)

        for block in mapBlocks:
            if block.collision: # if the block can be collided with
                block.rect.topleft = (block.world_x, block.world_y) # using original locations for both the player and block to make collision less confusing

                if self.rect.colliderect(block.rect):
                    collided.append(block)

        return collided

    def Movement(self, mapBlocks):
        collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

        # horizontal movement
        self.world_x += self.movementSpeeds[0]
        self.rect.topleft = (self.world_x, self.world_y)

        for block in self.CollideWithObject(mapBlocks):
            if self.movementSpeeds[0] > 0: # moving right so colliding with the left side of the block (right side of the player)
                self.world_x = block.world_x - self.rect.width
                collisions['right'] = True

            elif self.movementSpeeds[0] < 0: # moving left so colliding with the right side of the block (left side of the player)
                self.world_x = block.world_x + block.rect.width
                collisions['left'] = True

            self.rect.topleft = (self.world_x, self.world_y)

        # vertical movement
        self.world_y += self.movementSpeeds[1]
        self.rect.topleft = (self.world_x, self.world_y)

        for block in self.CollideWithObject(mapBlocks):
            if self.movementSpeeds[1] > 0: # moving down so colliding with the top of the block (bottom of the player)
                self.world_y = block.world_y - self.rect.height
                collisions['bottom'] = True

            elif self.movementSpeeds[1] < 0: # moving up so colliding with the bottom of the block (top of the player)
                self.world_y = block.world_y + block.rect.height
                collisions['top'] = True

            self.rect.topleft = (self.world_x, self.world_y)

        return collisions

    def Inputs(self):
        keys = Setup.pg.key.get_pressed()
        
        self.MovementKeyHandler(keys)
        self.JumpHandler(keys)
        self.DashHandler(keys)
        self.CrouchHandler(keys)

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
            if self.mostRecentDirection == "RIGHT":
                self.playerXCarriedMovingSpeed = 35
            elif self.mostRecentDirection == "LEFT":
                self.playerXCarriedMovingSpeed = -35

    def CrouchHandler(self, keys):
        if keys[Setup.pg.K_LCTRL] and self.state != "AIR":
            self.isCrouched = True

        elif not keys[Setup.pg.K_LCTRL]:
            self.isCrouched = False

        if self.isCrouched:
            self.keyPressVelocity = 4
        else:
            self.keyPressVelocity = 8     

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

        collisions = self.Movement(gameHandler.blocks)

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

        if collisions['left'] or collisions['right']: # to avoid background moving when player is stuck on an object
            self.movementSpeeds[0] = 0

        if self.mostRecentDirection == "LEFT":
            self.UpdateCurrentImage(True)
        else:
            self.UpdateCurrentImage(False)

        gameBackground.MoveImage(-self.movementSpeeds[0] * 0.75)
        self.camera.Update()
        self.camera.DisplayMap(gameHandler)
        self.miniMap.ChangeScale()
        self.miniMap.DrawMap(gameHandler.blocks, self)
        self.miniMap.DrawWaypoints(self)
        self.Attack()
        self.AbilitySpell()
        self.weapon.Update()
        self.spell.Update()

    def DrawFrame(self):
        if not self.miniMap.enlarged:
            draw_x = self.world_x - self.camera.camera.left # always in centre of the screen
            draw_y = self.world_y - self.camera.camera.top
            Setup.setup.screen.blit(self.currentImage, (draw_x, draw_y))

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

class Prompt:
    def __init__(self, promptName, key, typeOfPrompt):
        self.width = 64
        self.height = 64
        self.key = key
        self.typeOfPrompt = typeOfPrompt
        self.imagePath = Setup.os.path.join("ASSETS", "PROMPTS", promptName)
        self.image = Setup.setup.loadImage(self.imagePath, self.width, self.height)
        self.active = False

    def Draw(self, parentBlock, camera):
        draw_x = parentBlock.world_x - camera.left
        draw_y = parentBlock.world_y - camera.top
        Setup.setup.screen.blit(self.image, (draw_x, draw_y))    

class GameBackground:
    def __init__(self):
        self.width = 40 * 160 # 32 blocks, 160 pixels each plus extra to always be on screen
        self.height = Setup.setup.HEIGHT
        self.locationX, self.locationY = 0, 0
        self.filePath = Setup.os.path.join("ASSETS", "BACKGROUND", "GAME_BACKGROUND_1_IMAGE")
        self.image = Setup.setup.loadImage(self.filePath, self.width, self.height)

    def DrawImage(self):
        Setup.setup.screen.blit(self.image, (self.locationX, self.locationY))

    def MoveImage(self, moveX):
        self.locationX += moveX
        self.locationY = 0

class Waypoint:
    def __init__(self, parentBlock):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e", "MINI_MAP")
        self.active = False # saved data, has the waypoint been interacted with before

    def IsPlayerInRange(self, player, camera):
        if self.parent.rect.colliderect(player.rect):
            self.prompt.active = True
            self.prompt.Draw(self.parent, camera)
            self.PromptInteractedWith(player)

        self.prompt.active = False

    def PromptInteractedWith(self, player):
        if self.prompt.active and Setup.setup.pressedKey == Setup.pg.key.key_code(self.prompt.key):
            self.active = True

            match self.prompt.typeOfPrompt:
                case "MINI_MAP":
                    self.MiniMapFunction(player)

    def MiniMapFunction(self, player):
        player.miniMap.enlarged = not player.miniMap.enlarged
        player.miniMap.seeWaypoints = True
        Setup.pg.mouse.set_visible(not Setup.pg.mouse.get_visible())
        player.miniMap.CreateWaypointButtons(gameHandler.waypoints)

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

    def ChangeScale(self):
        if Setup.setup.pressedKey == Setup.pg.key.key_code("m"):
            self.enlarged = not self.enlarged 
            self.seeWaypoints = False
            Setup.pg.mouse.set_visible(False)

    def DrawMap(self, blocks, player):
        if not self.enlarged:
            shrinkModifier = 20
            start_x = 20
            start_y = Setup.setup.HEIGHT - 400
            Setup.pg.draw.rect(Setup.setup.screen, (Setup.setup.GREY), (start_x, start_y, self.width - (start_x / 2), self.height - (start_x / 2))) # background to draw on, easier to see map
        else:
            shrinkModifier = 8
            start_x = 480
            start_y = 60
            Setup.pg.draw.rect(Setup.setup.screen, (Setup.setup.GREY), (0, 0, Setup.setup.WIDTH, Setup.setup.HEIGHT))
        
        for block in blocks:
            newImage = Setup.pg.transform.scale(block.image, (block.width / shrinkModifier, block.height / shrinkModifier))
            new_x, new_y = block.world_x / shrinkModifier, block.world_y / shrinkModifier

            Setup.setup.screen.blit(newImage, (start_x + new_x, start_y + new_y))

        new_player_x, new_player_y = player.world_x / shrinkModifier, player.world_y / shrinkModifier
        
        if not self.enlarged:
            self.playerIconImage = Setup.setup.loadImage(self.playerIconFile, self.playerIconWidth, self.playerIconHeight)
            Setup.setup.screen.blit(self.playerIconImage, (start_x + new_player_x - (0.25 * 32), start_y + new_player_y - (0.5 * 32))) # adjusting icon location to be roughly centered on in-game player
        else:
            self.playerIconImage = Setup.setup.loadImage(self.playerIconFile, self.playerIconWidth * 2, self.playerIconHeight * 2)
            Setup.setup.screen.blit(self.playerIconImage, (start_x + new_player_x - (0.5 * 32), start_y + new_player_y - 32)) 

    def CreateWaypointButtons(self, waypoints):
        width, height = 64, 64
        shrinkModifier = 8
        start_x = 480
        start_y = 60

        self.waypointButtons.empty()

        for waypoint in waypoints:
            parentBlock = waypoint.parent
            location_x = start_x + (parentBlock.world_x / shrinkModifier) + (0.25 * 64) - 6
            location_y = start_y + (parentBlock.world_y / shrinkModifier) - (0.2 * 64)

            if not waypoint.active:
                canFastTravel = "NO"
                self.waypointButtons.add(Menus.Button(f"WAYPOINT {parentBlock.world_x} {parentBlock.world_y} {canFastTravel}", width, height, location_x, location_y, "INACTIVE_WAYPOINT_IMAGE"))
            else:
                canFastTravel = "YES"
                self.waypointButtons.add(Menus.Button(f"WAYPOINT {parentBlock.world_x} {parentBlock.world_y} {canFastTravel}", width, height, location_x, location_y, "ACTIVE_WAYPOINT_IMAGE"))

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
                    print("git test")
                    locationX = float(text[1])
                    locationY = float(text[2])
                    player.world_x = locationX
                    player.world_y = locationY
                    player.miniMap.enlarged = False
                    Setup.pg.mouse.set_visible(False)

class Camera:
    def __init__(self, player):
        self.width = Setup.setup.WIDTH
        self.height = Setup.setup.HEIGHT
        self.camera = Setup.pg.Rect(0, 0, self.width, self.height)
        self.player = player

    def Update(self):
        self.camera.center = self.player.rect.center

    def DisplayMap(self, gameHandler):
        blocks = gameHandler.blocks
        waypoints = gameHandler.waypoints

        for block in blocks:
            draw_x = block.world_x - self.camera.left
            draw_y = block.world_y - self.camera.top
            Setup.setup.screen.blit(block.image, (draw_x, draw_y))

        for waypoint in waypoints:
            waypoint.IsPlayerInRange(self.player, self.camera)

player = Player("Temporary") 
gameBackground = GameBackground()
gameHandler = GameHandler()
gameHandler.CreatePlayableMap()