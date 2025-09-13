from pygame.display import flip
import Setup
import MapCreator
import Menus
import Dijkstra

class GameHandler(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)
        self.player = None
        self.background = GameBackground(self)      
                                        
        self.weightedAdjacencyList = Dijkstra.AdjacencyList()
        self.dijkstraGraph = None
        self.pathfindingWaypointBlocks = []

        self.blocks = Setup.pg.sprite.Group() 
        self.enemies = Setup.pg.sprite.Group()
        self.bosses = Setup.pg.sprite.Group()
        self.hitBoxes = Setup.pg.sprite.Group()

        self.playableMap = []
        self.waypoints = []
        self.treasureChests = []
        self.friendlyCharacters = []

        self.blockAttributeDictionary = {0 : [False, 0, 0], # enemies and bosses all have no collision so no need for attributes
                                     1 : [True, 0, 10],
                                     2 : [True, 0, 10],
                                     3 : [True, 0, 10],
                                     4 : [True, 0, 10],
                                     5 : [True, 0, 10],
                                     6 : [True, 0, 10],
                                     7 : [True, 0, 10],
                                     8 : [True, 30, 20], # spike start
                                     9 : [True, 30, 20],
                                     10 : [True, 30, 20],
                                     11 : [True, 30, 20],
                                     12 : [True, 30, 20],
                                     13 : [True, 30, 20], # spike end
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
                                     }# [collision with player, damage if any, knockback when hit (is increased if player takes damage from block]

        self.enemyTypes = {29 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           30 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           31 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},   
                           32 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           33 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           34 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           35 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           36 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           37 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 224, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           38 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           39 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           40 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           41 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           42 : {"class": Enemy1, "health": 120, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                            }

    def DataToDictionary(self):
        objectListsToSave = ["enemies", "waypoints", "treasureChests", "friendlyCharacters"]

        dataToSave = {
            "player": self.player.DataToDictionary() if self.player else None
        }

        for attributeName in objectListsToSave:
            attributeList = getattr(self, attributeName)
            dataToSave[attributeName] = [attribute.DataToDictionary() for attribute in attributeList]

        return dataToSave

    def DataFromDictionary(self, data):
        if "player" in data:
            self.player = Player.DataFromDictionary(data["player"])
            self.player.gameHandler = self      

        attributesToUpdate = ["enemies", "waypoints", "treasureChests", "friendlyCharacters"]

        for attribute in attributesToUpdate:  # not creating new waypoints, only updating a small number of variables
            if attribute in data:
                newData = data[attribute]
                attributeSelf = getattr(self, attribute) # self.attribute

                if isinstance(attributeSelf, Setup.pg.sprite.Group):
                    attributeList = list(attributeSelf.sprites())
                else:
                    attributeList = attributeSelf

                for index in range(0, min(len(attributeList), len(newData))):
                    if attribute == "enemies":
                        attributeList[index].player = self.player

                    attributeList[index].LoadFromDictionary(newData[index])

    def SaveGame(self):
        if Setup.setup.currentSaveSlot != -1 and Setup.setup.saveGame:
            Setup.setup.saveGame = False

            filePath = Setup.os.path.join("ASSETS", "SAVED_DATA", f"SAVE_FILE_{Setup.setup.currentSaveSlot}.txt")     
            with open(filePath, "w") as file:
                Setup.json.dump(self.DataToDictionary(), file, indent=4)

    def LoadGame(self):
        if Setup.setup.changeSlot[0] and Setup.setup.changeSlot[1] != -1 and Setup.setup.currentSaveSlot != Setup.setup.changeSlot[1]:
            self.ResetData()
                      
            Setup.setup.currentSaveSlot = Setup.setup.changeSlot[1]
            Setup.setup.changeSlot = (False, -1)
                                             
            filePath = Setup.os.path.join("ASSETS", "SAVED_DATA", f"SAVE_FILE_{Setup.setup.currentSaveSlot}.txt")            
            if Setup.os.path.exists(filePath) and Setup.os.path.getsize(filePath) > 0:                            
                with open(filePath, "r") as file:
                    data = Setup.json.load(file)
                    self.DataFromDictionary(data)       

    def ResetData(self):
        self.player = Player("Player", self)
        self.blocks = Setup.pg.sprite.Group() 
        self.enemies = Setup.pg.sprite.Group()
        self.bosses = Setup.pg.sprite.Group()
        self.hitBoxes = Setup.pg.sprite.Group()
        self.playableMap = []
        self.waypoints = []
        self.treasureChests = []
        self.friendlyCharacters = []
        self.CreatePlayableMap()
               
    def CreatePlayableMap(self):
        Setup.setup.loadedMap = True

        for row in MapCreator.mapDataHandler.mapGrid.blockGrid:
            for block in row:          
                if block.blockNumber <= 20 or (block.blockNumber >= 43 and block.blockNumber <= 47): # a block and not an entity - friendly characters cannot move so are represented as a block
                    attributes = self.blockAttributeDictionary[block.blockNumber] 

                    if attributes:
                        if block.rotation <= -360:
                            block.rotation %= 360

                        mapBlock = MapBlock(block.blockNumber, block.rotation, block.rotation // -90, block.originalLocationX, block.originalLocationY, block.image, attributes[0], attributes[1], attributes[2])
                     
                        if block.blockNumber != 0: # self.blocks will be used to display the blocks, block 0 is a filler block for the map creator and should not be visible in game
                            self.blocks.add(mapBlock)

                        if block.blockNumber == 17 or block.blockNumber == 18: # waypoints
                            self.waypoints.append(Waypoint(mapBlock))

                        if block.blockNumber == 19: # treasure chests
                            self.treasureChests.append(TreasureChest(mapBlock, len(self.treasureChests)))

                        if block.blockNumber >= 43 and block.blockNumber <= 47: # friendly characters
                            self.friendlyCharacters.append(FriendlyCharacter(mapBlock, block.blockNumber - 43)) # between 0 and 4
                    else:
                        raise ValueError("block has not attributes")

                else: # entities (bosses, enemies, pathFinders)
                    if block.blockNumber >= 21 and block.blockNumber <= 28:
                        pass
                    elif block.blockNumber >= 29 and block.blockNumber <= 42:
                        self.enemies.add(self.CreateEnemy(block.blockNumber, block))
                    elif block.blockNumber == 48:    
                        self.pathfindingWaypointBlocks.append(block)                

        self.PopulateGraph(self.pathfindingWaypointBlocks)

    def CreateEnemy(self, enemyNumber, block):      
        filePath = Setup.os.path.join("ASSETS", "ENEMIES", f"ENEMY{enemyNumber - 28}_IMAGE") # first enemy image is ENEMY1_IMAGE, not ENEMY29_IMAGE so -28
        image = Setup.pg.image.load(filePath + ".png")
        
        enemyClass = self.enemyTypes[enemyNumber]      

        if not enemyClass:
            raise ValueError(f"Enemy number {enemyNumber} does not exist")
          
        width = enemyClass["size"]
        widthDifferenceToNormalBlock = width - Setup.setup.BLOCK_WIDTH 

        return enemyClass["class"](
            worldX = block.originalLocationX,
            worldY = block.originalLocationY - widthDifferenceToNormalBlock,
            image = image,
            health = enemyClass["health"],
            movementType = enemyClass["movementType"],
            velocity = enemyClass["velocity"],
            size = enemyClass["size"],
            suspicionRange = enemyClass["suspicionRange"],
            detectionRange = enemyClass["detectionRange"],
            enemyType = enemyNumber,
            player = self.player,
        )

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

        self.dijkstraGraph = Dijkstra.DijkstraImplementation(self.weightedAdjacencyList.weightedGraph)

    def UpdateEnemies(self):
        for enemy in self.enemies:
            enemy.PerformAction()

    def CollideWithObjects(self, mainObject):
        collided = []
        mainObject.rect.topleft = (mainObject.worldX, mainObject.worldY)

        for collidedBlock in Setup.pg.sprite.spritecollide(mainObject, self.blocks, False):
            if collidedBlock.collision:
                collided.append(collidedBlock)

        return collided

class MapBlock(Setup.pg.sprite.Sprite): 
    def __init__(self, blockNumber, rotation, smallRotation, originalLocationX, originalLocationY, image, hasCollision, damage, knockback):
        super().__init__()
        self.blockNumber = blockNumber
        self.rotation = rotation
        self.smallRotation = smallRotation
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

        directions = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.topFace = directions[self.smallRotation]

class Spell:
    spellNames = ["FIREBALL"]
    displayImages = {}

    for x in range(0, len(spellNames)):
        displayImages.update({spellNames[x] : f"SPELL{x + 1}_IMAGE"})

    def __init__(self, name, description, damage, manaCost, parentPlayer=None):

        self.name = name
        self.description = description
        self.damage = damage
        self.manaCost = manaCost
        self.parentPlayer = parentPlayer

        self.currentState = "NONE" # "NONE" "SPELL"
        self.tempCounter = 0 # used until spells have an actual function

        self.displayImagePath = Spell.displayImages[name] if name in Spell.spellNames else Spell.displayImages["FIREBALL"]
        
        self.statsToDisplay = ["description", "damage", "manaCost"]

    def DataToDictionary(self):
        return {
            "name": self.name,
            "description": self.description,
            "damage": self.damage,
            "manaCost": self.manaCost,
            "currentState": self.currentState,
            "tempCounter": self.tempCounter
        }

    @classmethod
    def DataFromDictionary(cls, data):
        return cls(
            name = data.get("name", ""),
            description = data.get("description", ""),
            damage = data.get("damage", 0),
            manaCost = data.get("manaCost", 0)
        )

    def Attack(self):
        if self.parentPlayer.UseMana(self.manaCost):
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

class Fireball(Spell):
    def __init__(self, name, description, damage, manaCost, parentPlayer):
        super().__init__(name, description, damage, manaCost, parentPlayer)

        self.images = None

    def UseSpell(self):
        if self.attackStart <= self.basicAttackLength:
            pass
            #attack     

class Armour:
    armourNames = ["NONE", "SKIN_OF_THE_WEEPING_MAW"]
    displayImages = {}

    for x in range(0, len(armourNames)):
        displayImages.update({armourNames[x] : f"PLAYER{x + 1}_IMAGE"})

    def __init__(self, name, description, resistance, parentPlayer = None):
        self.name = name
        self.description = description
        self.resistance = resistance
        self.parentPlayer = parentPlayer

        self.displayImagePath = Armour.displayImages[name] if name in Armour.armourNames else Armour.displayImages["NONE"]
        self.image = Setup.pg.image.load(Setup.os.path.join("ASSETS", "PLAYER", self.displayImagePath) + ".png")

        self.statsToDisplay = ["description", "resistance"]

    def DataToDictionary(self):
        return {
            "name": self.name,
            "description": self.description,
            "resistance": self.resistance,
        }

    @classmethod
    def DataFromDictionary(cls, data):
        return cls(
            name = data.get("name", ""),
            description = data.get("description", ""),
            resistance = data.get("resistance", 0),
        )    

class Weapon:
    weaponNames = ["WOODEN_SWORD"]
    displayImages = {}

    for x in range(0, len(weaponNames)):
        displayImages.update({weaponNames[x] : f"WEAPON{x + 1}_IMAGE"})

    def __init__(self, name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer=None):        
        self.name = name
        self.description = description
        self.abilityDescription = abilityDescription
        self.damage = damage
        self.chargedDamage = chargedDamage
        self.abilityDamage = abilityDamage
        self.abilityManaCost = abilityManaCost
        self.abilityCooldown = abilityCooldown
        self.parentPlayer = parentPlayer

        self.currentState = "NONE" # "NONE" "BASIC" "CHARGED" "ABILITY"
        self.isChargingAttack = False
        self.chargingStartTime = 0
        self.mostRecentAbilityTime = 0

        self.tempCounter = 0 # TODO - used until attacks have an actual function
        self.attackStart = 0
       
        self.displayImagePath = Weapon.displayImages[name] if name in Weapon.weaponNames else Weapon.displayImages["WOODEN_SWORD"]
        
        self.statsToDisplay = ["description", "abilityDescription", "damage", "chargedDamage", "abilityDamage", "abilityManaCost", "abilityCooldown"]

    def DataToDictionary(self):
        return {
            "name": self.name,
            "description": self.description,
            "abilityDescription": self.abilityDescription,
            "damage": self.damage,
            "chargedDamage": self.chargedDamage,
            "abilityDamage": self.abilityDamage,
            "abilityManaCost": self.abilityManaCost,
            "abilityCooldown": self.abilityCooldown,
        }

    @classmethod
    def DataFromDictionary(cls, data):
        return cls(
            name = data.get("name", ""),
            description = data.get("description", ""),
            abilityDescription = data.get("abilityDescription", ""),
            damage = data.get("damage", 0),
            chargedDamage = data.get("chargedDamage", 0),
            abilityDamage = data.get("abilityDamage", 0),
            abilityManaCost = data.get("abilityManaCost", 0),
            abilityCooldown = data.get("abilityCooldown", 0),
        )       

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
            if currentTime - self.mostRecentAbilityTime >= self.abilityCooldown and self.parentPlayer.UseMana(self.abilityManaCost):
                self.mostRecentAbilityTime = currentTime
                self.currentState = "ABILITY"

    def Update(self):
        match self.currentState:
            case "BASIC":
                self.attackStart = Setup.time.time()
                self.BasicAttack()
            case "CHARGED":
                self.attackStart = Setup.time.time()
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
    def __init__(self, name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer):
        super().__init__(name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer)

        self.basicAttackLength = 2 # seconds
        self.basicAttackSheet = None       

    def BasicAttack(self):
        if self.attackStart <= self.basicAttackLength:
            pass
            #attack     

class LongSword(Weapon):
    def __init__(self, name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer):
        super().__init__(name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer)

        self.basicAttackLength = 3 # seconds
        self.basicAttackSheet = None       

    def BasicAttack(self):
        if self.attackStart <= self.basicAttackLength:
            pass
            #attack    

class HitBox(Setup.pg.sprite.Sprite): # USE SPRITE FUNCTIONALITY FOR COLLISION - THIS WILL MOST LIKELY NOT BE IN THIS CLASS
    def __init__(self, worldX, worldY, width, height, parentObject):
        super().__init__()
        self.parent = parentObject
        self.worldX = worldX
        self.worldY = worldY
        self.width = width
        self.height = height
        self.rect = Setup.pg.Rect(self.worldX, self.worldY, self.width, self.height)

    def update(self):
        self.rect.topleft = (self.worldX, self.worldY)

class Inventory:
    allItems = {"DefaultArmour" : Armour,
                "DefaultWeapon" : Weapon,
                "DefaultSpell" : Spell,
                "WoodenSword" : WoodenSword, 
                "Fireball" : Fireball}

    def __init__(self, player, weapons=[], spells=[], armour=[]):
        self.weapons = weapons
        self.spells = spells
        self.armour = armour

        self.parentPlayer = player
        self.inventoryMainMenu = Menus.menuManagement.inventoryButtonGroup
        self.open = False

        self.weaponSlotButton = Menus.ButtonGroupMethods.GetButton("WEAPON_SLOT", self.inventoryMainMenu.buttons)
        self.spellSlotButton = Menus.ButtonGroupMethods.GetButton("SPELL_SLOT", self.inventoryMainMenu.buttons)
        self.armourSlotButton = Menus.ButtonGroupMethods.GetButton("ARMOUR_SLOT", self.inventoryMainMenu.buttons)
        self.buttons = {self.weaponSlotButton : "weapon", self.spellSlotButton : "spell", self.armourSlotButton : "armour"}

        self.itemTexts = {}

    def DataToDictionary(self):
        return {"weapons": [weapon.DataToDictionary() for weapon in self.weapons],
                "spells": [spell.DataToDictionary() for spell in self.spells],
                "armour": [armour.DataToDictionary() for armour in self.armour]
        }

    @classmethod
    def DataFromDictionary(cls, data):       
        itemData = {"weapons" : [], 
                    "spells" : [], 
                    "armour" : []}

        for attributeList in itemData.items():
            for data in data.get(attributeList[0], []):
                if data["name"] in Inventory.allItems:
                    itemClass = Inventory.allItems[data["name"]]
                    attributeList[1].append(itemClass().DataFromDictionary(data))

        return cls(weapons=itemData["weapons"], spells=itemData["spells"], armour=itemData["armour"])

    def AddItem(self, itemToAdd):
        classToList = {Weapon : self.weapons,
                       Spell : self.spells,
                       Armour : self.armour}

        for checkClass, listToAdd in classToList.items():
            if isinstance(itemToAdd, checkClass):
                if itemToAdd not in listToAdd:
                    itemToAdd.parentPlayer = self.parentPlayer
                    listToAdd.append(itemToAdd)

                break

    def UpdatePlayerModelScreen(self):
        Setup.pg.draw.rect(Setup.setup.screen, Setup.setup.GREY, (0, 0, Setup.setup.WIDTH, Setup.setup.HEIGHT)) # background
        enlargedPlayerImage = Setup.pg.transform.scale(self.parentPlayer.unflippedIdleImage, (Setup.setup.WIDTH / 4, Setup.setup.WIDTH / 4))
        enlargedPlayerTorso = Setup.pg.transform.scale(self.parentPlayer.armour.image, (Setup.setup.WIDTH / 4, Setup.setup.WIDTH / 4))

        Setup.setup.screen.blit(enlargedPlayerImage, (Setup.setup.WIDTH / 10, (Setup.setup.HEIGHT - Setup.setup.WIDTH / 4) / 2)) # current player image unrotated
        Setup.setup.screen.blit(enlargedPlayerTorso, (Setup.setup.WIDTH / 10, (Setup.setup.HEIGHT - Setup.setup.WIDTH / 4) / 2)) 

    def DrawHoveredItemStats(self, item):
        textToDraw = {}

        for index, attribute in enumerate(item.statsToDisplay):
            objectAttribute = getattr(item, attribute)
            uniqueIdentifier = (id(item), attribute)

            if uniqueIdentifier not in self.itemTexts:
                fontSize = 35
                spacing = fontSize * index
                newStatText = Setup.TextMethods.CreateText(item.name, f"{attribute} : {objectAttribute}", Setup.setup.WHITE, Setup.setup.WIDTH - (10 * fontSize), Setup.setup.HEIGHT // 2 + spacing, fontSize)
                self.itemTexts[uniqueIdentifier] = newStatText

            textToDraw[uniqueIdentifier] = self.itemTexts[uniqueIdentifier]

        Setup.TextMethods.UpdateText(textToDraw.values())
  
    def UpdateSelectionSlots(self):
        for button in self.buttons:
            playerAttribute = getattr(self.parentPlayer, self.buttons[button])

            if not button.hover:                
                button.ChangeImageClick(playerAttribute.displayImagePath)
            else:
                self.DrawHoveredItemStats(playerAttribute)

    def Draw(self):       
        self.UpdatePlayerModelScreen()
        self.UpdateSelectionSlots()
        
class Player(Setup.pg.sprite.Sprite):
    def __init__(self, name="Player", gameHandler=None, worldX=Setup.setup.WIDTH / 2, worldY=Setup.setup.HEIGHT / 2, health=500, maxHealth=800, mana=300, maxMana=400, mapFragments=None, mostRecentWaypointCords=None, weapon=None, spell=None, armour=None, inventory=None):
        super().__init__()
        self.name = name
        self.gameHandler = gameHandler
        self.worldX = worldX
        self.worldY = worldY
        self.health = health
        self.maxHealth = maxHealth
        self.mana = mana
        self.maxMana = maxMana
        self.mapFragments = mapFragments if mapFragments is not None else {"1": True, "2": True, "3": True, "4": False} # json converts int keys to strings, which forces a conversion later, it is safer to always use string keys
        self.mostRecentWaypointCords = mostRecentWaypointCords

        attributesAndDefault = {"weapon" : WoodenSword("WoodenSword", "weapon", "ability", 100, 200, 300, 20, 5, parentPlayer=self), 
                                "spell" : Fireball("Fireball", "fire", 100, 20, parentPlayer=self), 
                                "armour" : Armour("DefaultArmour", "no armour", 0, parentPlayer=self), 
                                "inventory" : Inventory(self)}
        
        for attributeName, default in attributesAndDefault.items():
            attributeValue = locals()[attributeName] # gets the variable passed in as an argument e.g. weapon

            if attributeValue is None:
                setattr(self, attributeName, default) # setattr creates a new self. variable with the given name and data
            else:
                attributeValue.parentPlayer = self
                setattr(self, attributeName, attributeValue)

        for equipped in [self.weapon, self.spell, self.armour]:
            self.inventory.AddItem(equipped)

        self.gameHandler = gameHandler

        self.dead = False
        self.width = Setup.setup.BLOCK_WIDTH
        self.height = Setup.setup.BLOCK_WIDTH
        self.manaRegenerationSpeed = 50 / 60 # 50 a second, divided by 60 for each frame
        self.manaRegenerationCooldown = 1 # second
        self.manaRegenDelayTimer = CooldownTimer(self.manaRegenerationCooldown)

        self.camera = Camera(self)
        self.miniMap = MiniMap()     
     
        self.idleFilePath = Setup.os.path.join("ASSETS", "PLAYER", "PLAYER_IDLE_SHEET")
        self.idleImageSheet = Setup.pg.image.load(self.idleFilePath + ".png").convert_alpha()
        self.idleSheet = Setup.SpriteSheet(self.idleImageSheet, self, self.width * 8)
        self.unflippedIdleImage = self.idleSheet.GetImage(0, self.width, self.height, 1)

        self.jumpFilePath = Setup.os.path.join("ASSETS", "PLAYER", "PLAYER_JUMP_SHEET")
        self.jumpImageSheet = Setup.pg.image.load(self.jumpFilePath + ".png").convert_alpha()
        self.jumpSheet = Setup.SpriteSheet(self.jumpImageSheet, self, self.width * 8)

        self.state = "IDLE"
        self.currentFrame = 0
        self.currentSheet = self.idleSheet
        self.startTime = Setup.time.time()
        self.isCrouched = False

        # movement
        self.movementSpeeds = [0, 0]
        self.keyPressVelocity = 6
        self.mostRecentDirection = None
        self.playerYFallingSpeed = 0
        self.playerXCarriedMovingSpeed = 0 # dashing etc
        self.gravity = Setup.setup.GRAVITY 

        self.UpdateCurrentImage(False)

    def DataToDictionary(self):
        return {"worldX": self.worldX,
                "worldY": self.worldY,
                "health": self.health,
                "maxHealth": self.maxHealth,
                "mana": self.mana,
                "maxMana": self.maxMana,
                "mostRecentWaypointCords": self.mostRecentWaypointCords,
                "weapon": self.weapon.DataToDictionary() if self.weapon else None,
                "spell": self.spell.DataToDictionary() if self.spell else None,
                "armour": self.armour.DataToDictionary() if self.armour else None,
                "inventory": self.inventory.DataToDictionary() if self.inventory else None,
                "mapFragments": self.mapFragments               
        }

    @classmethod
    def DataFromDictionary(cls, data):
        return cls(
            worldX = data.get("worldX", 0),
            worldY = data.get("worldY", 0),
            health = data.get("health", 100),
            maxHealth = data.get("maxHealth", 100),
            mana = data.get("mana", 50),
            maxMana = data.get("maxMana", 50),
            mapFragments = data.get("mapFragments", {"1": True, "2": True, "3": True, "4": False}),
            mostRecentWaypointCords = data.get("mostRecentWaypointCords", None),
            weapon = Weapon.DataFromDictionary(data.get("weapon")) if data.get("weapon") else None,
            spell = Spell.DataFromDictionary(data.get("spell")) if data.get("spell") else None,
            armour = Armour.DataFromDictionary(data.get("armour")) if data.get("armour") else None,
            inventory = Inventory.DataFromDictionary(data.get("items")) if data.get("items") else None,
        )

    def UpdateCurrentImage(self, flipImage):       
        self.torsoImage = Setup.pg.transform.flip(self.armour.image, flipImage, False)

        if self.currentSheet:
            self.currentSheet.Update()
            self.currentImage = self.currentSheet.GetImage(self.currentFrame, self.width, self.height, 1)
            self.currentImage = Setup.pg.transform.scale(self.currentImage, (self.width, self.height)) 
            self.currentImage = Setup.pg.transform.flip(self.currentImage, flipImage, False)

            self.mask = Setup.pg.mask.from_surface(self.currentImage) 
            self.rect = self.mask.get_rect()
            self.rect.topleft = (self.worldX, self.worldY)

    def Movement(self):
        collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

        # horizontal movement
        self.worldX += self.movementSpeeds[0]
        self.rect.topleft = (self.worldX, self.worldY)

        for block in self.gameHandler.CollideWithObjects(self):
            if self.movementSpeeds[0] > 0: # moving right so colliding with the left side of the block (right side of the player)
                self.worldX = block.worldX - self.rect.width # always snap the player to outside the block
                
                if self.BlockCollision(block, "LEFT"): # opposite to direction of travel - if the collided block is not something with knockback (make sure to not negate the knockback)                   
                    break # break out of loop to avoid mutliple spike collisions occuring on the same frame
                
                collisions['right'] = True # do not create a collision as the knockback forces the player out of the block (otherwise the falling logic won't work as the game resets the falling speed)

            elif self.movementSpeeds[0] < 0: # moving left so colliding with the right side of the block (left side of the player)
                self.worldX = block.worldX + block.rect.width
                
                if self.BlockCollision(block, "RIGHT"):   
                    break
                
                collisions['left'] = True    

            self.rect.topleft = (self.worldX, self.worldY)

        # vertical movement
        self.worldY += self.movementSpeeds[1]
        self.rect.topleft = (self.worldX, self.worldY)

        for block in self.gameHandler.CollideWithObjects(self):
            if self.movementSpeeds[1] > 0: # moving down so colliding with the top of the block (bottom of the player)
                self.worldY = block.worldY - self.rect.height
                
                if self.BlockCollision(block, "UP"):   
                    break
                
                collisions['bottom'] = True
                
            elif self.movementSpeeds[1] < 0: # moving up so colliding with the bottom of the block (top of the player)
                self.worldY = block.worldY + block.rect.height
                
                if self.BlockCollision(block, "DOWN"):   
                    break
                
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

    def DisplayInventoryIfOpen(self):
        if self.inventory.inventoryMainMenu in Menus.menuManagement.gameMenus: # draw 
            self.inventory.Draw()
            self.inventory.open = True
        else:
            self.inventory.open = False

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
                if self.gravity * 0.95 < Setup.setup.GRAVITY * 0.4:
                    self.gravity = Setup.setup.GRAVITY * 0.4
                else:
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
        if self.health <= 0:
            self.dead = True

        if not self.dead:
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

            collisions = self.Movement()

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
            self.miniMap.DrawMap(self.gameHandler.blocks, self.gameHandler.enemies, self)
            self.miniMap.DrawWaypoints(self)
            self.miniMap.pathGuide.FindNearestNode(self)
            self.Attack()
            self.AbilitySpell()
            self.PassiveManaRegeneration()
            self.weapon.Update()
            self.spell.Update()
            self.DrawPlayerAndUI()
            self.KillPlayerOnKeyPress()
            self.DisplayInventoryIfOpen()
        else:
            self.DrawDeathScreen()

    def TakeHealth(self, damage):
        self.health -= damage

    def UseMana(self, manaCost):
        if self.mana >= manaCost:
            self.manaRegenDelayTimer.StartTimer()
            self.mana -= manaCost
            return True

        return False

    def BlockCollision(self, block, directionOfKnockback):
        if block.topFace == directionOfKnockback and block.damage > 0: # if block has no damage, there is no knockback
            self.TakeHealth(block.damage)
            self.ApplyKnockback(block.knockback, directionOfKnockback)
            return True

        return False

    def ApplyKnockback(self, knockback, direction):
        self.gravity = 1

        if direction in ("RIGHT", "LEFT"):
            if direction == "RIGHT":
                self.playerXCarriedMovingSpeed = knockback # cannot dash out of a knockback
            else:
                self.playerXCarriedMovingSpeed = -knockback 

            self.playerYFallingSpeed = -abs(knockback / 1.25) # pushes the player slightly upwards           

        else: # "UP" or "DOWN" - No movement on the x axis
            if direction == "UP":
                self.playerYFallingSpeed = -knockback # pushes the player upwards
            else:
                self.playerYFallingSpeed = knockback / 2 # pushes the player downwards

        self.movementSpeeds[1] = self.playerYFallingSpeed # update speeds early to move the player before speed is reset (collision with the ground)

    def PassiveManaRegeneration(self):        
        if self.mana < self.maxMana and self.manaRegenDelayTimer.startTime is None:
            self.manaRegenDelayTimer.StartTimer()

        if self.manaRegenDelayTimer.CheckFinished():
            if self.mana + self.manaRegenerationSpeed > self.maxMana:
                self.mana += self.maxMana - self.mana
            else:
                self.mana += self.manaRegenerationSpeed

    def DrawPlayerAndUI(self):
        if not self.miniMap.enlarged:
            drawX = self.worldX - self.camera.camera.left # always in centre of the screen
            drawY = self.worldY - self.camera.camera.top
            Setup.setup.screen.blit(self.currentImage, (drawX, drawY)) # draw player image
            Setup.setup.screen.blit(self.torsoImage, (drawX, drawY))

            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("red4"), (0, 0, self.maxHealth, 50)) # red health bar (background of bar)
            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("forestgreen"), (0, 0, self.health, 50)) # green health bar

            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("dimgrey"), (0, 50, self.maxMana, 50)) # grey mana bar (background of bar)
            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("dodgerblue3"), (0, 50, self.mana, 50)) # blue mana bar

    def DrawDeathScreen(self):
        deathScreenText = Setup.TextMethods.CreateText("DEATH", "DEAD", Setup.setup.RED, Setup.setup.WIDTH // 2, Setup.setup.HEIGHT // 2, 100)
        respawnText = Setup.TextMethods.CreateText("RESPAWN", "Press ENTER / RETURN to respawn", Setup.setup.WHITE, Setup.setup.WIDTH // 2, Setup.setup.HEIGHT // 2 + 200, 40)
        deathScreenText.Draw()
        respawnText.Draw()

        if Setup.setup.pressedKey == Setup.pg.K_RETURN:
            self.Respawn()

    def KillPlayerOnKeyPress(self):
        if Setup.setup.pressedKey == Setup.pg.K_k:
            self.health = 0

    def Respawn(self):
        self.dead = False
        self.ResetHealthAndMana()

        if self.mostRecentWaypointCords:
            (self.worldX, self.worldY) = self.mostRecentWaypointCords
        else:
            self.worldX = Setup.setup.WIDTH / 2
            self.worldY = Setup.setup.HEIGHT / 2

    def ResetHealthAndMana(self):
        self.mana = self.maxMana
        self.health = self.maxHealth

    def Attack(self):
        if Setup.pg.mouse.get_pressed()[0] and not self.weapon.isChargingAttack:
            self.weapon.isChargingAttack = True
            self.weapon.chargingStartTime = Setup.time.time()

        if not Setup.pg.mouse.get_pressed()[0] and self.weapon.isChargingAttack:
            currentTime = Setup.time.time()
            self.weapon.isChargingAttack = False
            self.weapon.Attack(currentTime)

    def AbilitySpell(self):
        keys = Setup.pg.key.get_pressed()

        if keys[Setup.pg.K_e]:
            currentTime = Setup.time.time()
            self.weapon.Ability(currentTime)

        if keys[Setup.pg.K_f]:
            self.spell.Attack()

class GameBackground:
    def __init__(self, gameHandler):  
        self.gameHandler = gameHandler

        filePath = Setup.os.path.join("ASSETS", "BACKGROUND", "GAME_BACKGROUND_1_IMAGE")
        self.blockImage = Setup.setup.loadImage(filePath, Setup.setup.BLOCK_WIDTH * Setup.setup.BLOCKS_WIDE, Setup.setup.BLOCK_WIDTH * Setup.setup.BLOCKS_WIDE)

    def DrawImage(self):
        if len(self.gameHandler.blocks.sprites()) != 0:
            topLeftBlock = self.gameHandler.blocks.sprites()[0]
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

class TreasureChest:
    allRewards = {0 : LongSword("LONG_SWORD", "A long iron sword", "A powerful overhead slash", 40, 55, 75, 100, 5, None),
                    1 : None,
                    2 : None,
                    3 : None,
                    4 : None
    } 

    def __init__(self, parentBlock, chestNumber):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.openedImage = MapCreator.mapDataHandler.mapGrid.blockSheetHandler.GetCorrectBlockImage(self.parent.blockNumber + 1, Setup.setup.BLOCK_WIDTH, Setup.setup.BLOCK_WIDTH, False, 0)
        self.chestOpened = False 
        
        self.reward = TreasureChest.allRewards[chestNumber]

    def DataToDictionary(self):
        return {"chestOpened": self.chestOpened,
        }

    def LoadFromDictionary(self, data): # does not create a new instance
        self.chestOpened = data.get("chestOpened", False)

    def IsPlayerInRange(self, player, camera):
        if not self.chestOpened:
            if self.prompt.IsPlayerInRange(self.parent, player, camera):
                self.TreasureChestFunction(player)

        elif self.parent.image != self.openedImage: # change image to correct image when loading
            self.parent.image = self.openedImage
            self.reward = None

    def TreasureChestFunction(self, player):
        if self.prompt.PromptInteractedWith():
            self.parent.image = self.openedImage
            self.chestOpened = True
            player.inventory.AddItem(self.reward)
            self.reward = None

class Waypoint:
    def __init__(self, parentBlock=None, waypointActive=False):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.waypointActive = waypointActive

    def DataToDictionary(self):
        return {"waypointActive": self.waypointActive
        }

    def LoadFromDictionary(self, data): # does not create a new instance
        self.waypointActive = data.get("waypointActive", False)
   
    def IsPlayerInRange(self, player, camera):
        if self.prompt.IsPlayerInRange(self.parent, player, camera):
            self.MiniMapFunction(player)

    def MiniMapFunction(self, player):
        if self.prompt.PromptInteractedWith():
            self.waypointActive = True
            player.ResetHealthAndMana()
            player.mostRecentWaypointCords = (self.parent.worldX, self.parent.worldY)
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

        fragmentLocations = {"1" : (startX, startY),
                              "2" : (startX + mapWidth / 2, startY),
                              "3" : (startX, startY + mapWidth / 2),
                              "4" : (startX + mapWidth / 2, startY + mapWidth / 2)}

        for fragment, fragmentValue in player.mapFragments.items(): 
            if not fragmentValue:
                Setup.pg.draw.rect(Setup.setup.screen, (Setup.setup.BLACK), (fragmentLocations[fragment][0], fragmentLocations[fragment][1], fragmentWidthHeight, fragmentWidthHeight))

    def DrawMap(self, blocks, enemies, player):
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

        for enemy in enemies:
            newImage = Setup.pg.transform.scale(enemy.image, (enemy.width / shrinkModifier, enemy.height / shrinkModifier))
            newX, newY = enemy.worldX / shrinkModifier, enemy.worldY / shrinkModifier
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
        blocks = self.player.gameHandler.blocks.sprites()
        enemies = self.player.gameHandler.enemies.sprites()
        bosses = self.player.gameHandler.bosses.sprites()
        drawWithCameraLocation = blocks + enemies + bosses     

        for drawObject in drawWithCameraLocation:
            drawX = drawObject.worldX - self.camera.left
            drawY = drawObject.worldY - self.camera.top
            tempRect = Setup.pg.Rect(drawX, drawY, drawObject.width, drawObject.height)

            if Setup.setup.screenRect.colliderect(tempRect): # if on the screen
                Setup.setup.screen.blit(drawObject.image, (drawX, drawY))
        
        blocksWithPrompts = []
        waypoints = self.player.gameHandler.waypoints
        treasureChests = self.player.gameHandler.treasureChests
        friendlyCharacters = self.player.gameHandler.friendlyCharacters
        
        blocksWithPrompts.append(waypoints)
        blocksWithPrompts.append(treasureChests)
        blocksWithPrompts.append(friendlyCharacters)

        for blocks in blocksWithPrompts:
            for block in blocks:
                block.IsPlayerInRange(self.player, self.camera)

class CooldownTimer:
    def __init__(self, cooldown):
        self.cooldown = cooldown
        self.startTime = None

    def StartTimer(self):
        self.startTime = Setup.time.time()

    def CheckFinished(self):
        if self.startTime is None:
            return False

        if Setup.time.time() - self.startTime >= self.cooldown:
            return True

    def Reset(self):
        self.startTime = None

class Enemy(Setup.pg.sprite.Sprite):
    def __init__(self, worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, player):
        super().__init__()
        self.player = player
        self.enemyType = enemyType

        self.worldX = worldX
        self.worldY = worldY
        self.startLocationX = worldX
        self.startLocationY = worldY

        self.width = size
        self.height = size # square

        self.image = image
        self.mask = Setup.pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.worldX, self.worldY)

        self.health = health
        self.maxHealth = health
        self.velocity = velocity
        self.slowVelocity = velocity / 2

        # detection
        self.suspicionRange = suspicionRange
        self.detectionRange = detectionRange
        self.state = "NORMAL" # "NORMAL", "SUSPICIOUS", "DETECTED", "RETURNING"
        self.detectedPlayerLocation = None

        # timers
        self.suspicionTimer = CooldownTimer(5)
        self.suspicionWaitTimer = CooldownTimer(3) # how long the enemy waits at the detected player location before returning
        self.outsideSuspicionRangeWhenDetected = CooldownTimer(5) # how long the player must be outside the suspicion range for the enemy to go from DETECTED to SUSPICIOUS
        self.randomMovementTimer = CooldownTimer(3) # how often the enemy decides a new direction

        self.movementClasses = {"STATIONARY" : None,
                                  "GUARD" : GuardMovement,
                                  "RANDOM" : RandomMovement,
                                  "FIXED_PATROL" : self.FixedPatrolMovement,
                                  "MULTIPLE_PATROL" : self.MultiplePatrolMovement,
                                  "SMART_PATROL" : self.SmartPatrol,
                                  }

        if self.movementClasses[movementType] is not None:
            self.movementClass = self.movementClasses[movementType]()
        else:
            self.movementClass = None

    def DataToDictionary(self):
        return {"enemyType": self.enemyType,
                "worldX": self.worldX,
                "worldY": self.worldY,
                "health": self.health
        }

    def LoadFromDictionary(self, data):
        self.enemyType = data["enemyType"]
        self.worldX = data["worldX"]
        self.worldY = data["worldY"]
        self.health = data["health"]

    def DisplayHealthBar(self):
        if not self.player.miniMap.enlarged and not self.player.inventory.open:
            drawX = self.worldX - self.player.camera.camera.left
            drawY = self.worldY - self.player.camera.camera.top - 10 # shift up slightly to draw above enemy

            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("red4"), (drawX, drawY, self.maxHealth, 10)) # red health bar (background of bar)
            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("forestgreen"), (drawX, drawY, self.health, 10)) # green health bar

    def UpdateState(self):
        distanceFromPlayer = Setup.math.sqrt((self.worldX - self.player.worldX) ** 2 + (self.worldY - self.player.worldY) ** 2)

        if distanceFromPlayer <= self.detectionRange:
            self.state = "DETECTED"
            self.outsideSuspicionRangeWhenDetected.Reset()

        elif distanceFromPlayer <= self.suspicionRange:
            if self.state != "DETECTED" and self.state != "RETURNING": # must be within detection range to detect player while returning
                self.state = "SUSPICIOUS"
                self.detectedPlayerLocation = (self.player.worldX, self.player.worldY)

        elif distanceFromPlayer > self.suspicionRange and self.state == "DETECTED":
            self.TransitionFromDetectedToSuspicion()

    def TransitionFromDetectedToSuspicion(self):
        if self.outsideSuspicionRangeWhenDetected.startTime is None:
                self.outsideSuspicionRangeWhenDetected.StartTimer()
        else:
            if self.outsideSuspicionRangeWhenDetected.CheckFinished():
                self.state = "SUSPICIOUS"                   
                self.outsideSuspicionRangeWhenDetected.Reset()

                if self.player.worldX < self.worldX:
                    self.detectedPlayerLocation = (self.worldX - self.suspicionRange, self.worldY)
                else:
                    self.detectedPlayerLocation = (self.worldX + self.suspicionRange, self.worldY)

    def CalculateDistanceFromStart(self):
        return Setup.math.sqrt((self.worldX - self.startLocationX) ** 2 + (self.worldY - self.startLocationY))

    def PerformAction(self):
        self.DisplayHealthBar()

        if self.movementClass is not None: # stationary enemies cannot move
            self.UpdateState()

            match self.state:
                case "NORMAL":
                    self.PerformMovement()
                case "DETECTED":
                    self.Detected()
                case "SUSPICIOUS":
                    self.Suspicious()
                case "RETURNING":
                    self.Returning()

        self.rect.topleft = (self.worldX, self.worldY)

    def Detected(self):
        playerX = self.player.worldX # the current location

        self.MoveToPoint(playerX, self.velocity, self.player)

    def Suspicious(self):
        playerX = self.detectedPlayerLocation[0] # enemies move left and right

        if self.suspicionTimer.startTime is None:
            self.suspicionTimer.StartTimer()

        if self.MoveToPoint(playerX, self.slowVelocity, self.player) or self.suspicionTimer.CheckFinished():
            self.suspicionTimer.Reset()

            if self.suspicionWaitTimer.startTime is None:
               self.suspicionWaitTimer.StartTimer()

        if self.suspicionWaitTimer.CheckFinished():
            self.state = "RETURNING"
            self.suspicionWaitTimer.Reset()

    def Returning(self):    
        if self.MoveToPoint(self.startLocationX, self.slowVelocity, self.player):
            self.state = "NORMAL"

    def MoveToPoint(self, endLocation, velocity, player):
        if self.worldX == endLocation: 
            return True

        direction = None

        if self.worldX > endLocation: 
            if self.worldX - velocity < endLocation:
                self.worldX = endLocation
            else:
                self.worldX -= velocity

            direction = "LEFT"
        else:
            if self.worldX + velocity > endLocation:
                self.worldX = endLocation
            else:
                self.worldX += velocity

            direction = "RIGHT"

        self.rect.topleft = (self.worldX, self.worldY)

        for block in player.gameHandler.CollideWithObjects(self):
            if direction == "RIGHT":
                self.worldX = block.worldX - self.rect.width 

            elif direction == "LEFT": 
                self.worldX = block.worldX + block.rect.width            

            self.rect.topleft = (self.worldX, self.worldY)     

    def PerformMovement(self):
        self.movementClass.Movement(self)

    def StationaryMovement(self):
        pass

    def FixedPatrolMovement(self):
        pass

    def MultiplePatrolMovement(self):
        pass

    def SmartPatrol(self):
        pass

class GuardMovement:
    def Movement(self, enemy):
        enemy.MoveToPoint(enemy.startLocationX, enemy.velocity)

class RandomMovement:
    def __init__(self):
        self.directions = ["RIGHT", "LEFT"] # or return which forces the enemy back towards its start
        self.direction = None
        self.randomMovementTimer = CooldownTimer(3)
        self.maxDistanceFromStart = Setup.setup.BLOCK_WIDTH * 10

    def Movement(self, enemy):
        if self.randomMovementTimer.startTime is None:
            self.randomMovementTimer.StartTimer()

        elif self.randomMovementTimer.CheckFinished():
            if self.direction is None:
                if enemy.CalculateDistanceFromStart() >= self.maxDistanceFromStart:
                    self.direction = "RETURN"
                else:
                    randomDirection = Setup.random.randint(0, 1)
                    self.direction = self.directions[randomDirection]
            else:
                self.direction = None

            self.randomMovementTimer.Reset()

        if self.direction == "RETURN":
            enemy.MoveToPoint(enemy.startLocationX, enemy.slowVelocity, enemy.player) # return to start
        if self.direction == "RIGHT":
            enemy.MoveToPoint(Setup.sys.maxsize, enemy.slowVelocity, enemy.player) # anywhere to the right
        elif self.direction == "LEFT":
            enemy.MoveToPoint(-Setup.sys.maxsize, enemy.slowVelocity, enemy.player) # anywhere to the left

class Enemy1(Enemy):
    def __init__(self, worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, player):
        super().__init__(worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, player)

class FriendlyCharacter:
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

    def __init__(self, parentBlock, friendlyCharacterNumber):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.textNumber = 0
        self.displayActive = False

        self.text = FriendlyCharacter.allText[friendlyCharacterNumber]
        self.item = FriendlyCharacter.allItems[friendlyCharacterNumber]

    def DataToDictionary(self):
        return {"textNumber": self.textNumber,
        }

    def LoadFromDictionary(self, data): 
        self.textNumber = data.get("textNumber", 0)

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
                    player.inventory.AddItem(self.item)
                    self.item = None

gameHandler = GameHandler()
