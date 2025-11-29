from turtle import up
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
        self.hitboxes = Setup.pg.sprite.Group()
        self.enemyHitboxes = Setup.pg.sprite.Group()

        self.collisionMap = [] # 1 indicates a block with collision, 0 is for anything else
        self.waypoints = []
        self.treasureChests = []
        self.friendlyCharacters = []

        # enemies and bosses all have no collision so no need for attributes
        self.blockAttributeDictionary = {
            0:  {"collision": False, "damage": 0,  "knockback": 0},
            # collidable blocks
            1:  {"collision": True,  "damage": 0,  "knockback": 20},
            2:  {"collision": True,  "damage": 0,  "knockback": 20},
            3:  {"collision": True,  "damage": 0,  "knockback": 20},
            4:  {"collision": True,  "damage": 0,  "knockback": 20},
            5:  {"collision": True,  "damage": 0,  "knockback": 20},
            6:  {"collision": True,  "damage": 0,  "knockback": 20},
            7:  {"collision": True,  "damage": 0,  "knockback": 20},
            # spikes
            8:  {"collision": True,  "damage": 50, "knockback": 20},
            9:  {"collision": True,  "damage": 50, "knockback": 20},
            10: {"collision": True,  "damage": 60, "knockback": 20},
            11: {"collision": True,  "damage": 60, "knockback": 20},
            12: {"collision": True,  "damage": 70, "knockback": 20},
            13: {"collision": True,  "damage": 70, "knockback": 20},
            # non collidable blocks
            14: {"collision": False, "damage": 0,  "knockback": 0},
            15: {"collision": False, "damage": 0,  "knockback": 0},
            16: {"collision": False, "damage": 0,  "knockback": 0},
            17: {"collision": False, "damage": 0,  "knockback": 0},
            18: {"collision": False, "damage": 0,  "knockback": 0},
            19: {"collision": False, "damage": 0,  "knockback": 0},
            20: {"collision": False, "damage": 0,  "knockback": 0},
            # friendly characters
            43: {"collision": False, "damage": 0,  "knockback": 0},
            44: {"collision": False, "damage": 0,  "knockback": 0},
            45: {"collision": False, "damage": 0,  "knockback": 0},
            46: {"collision": False, "damage": 0,  "knockback": 0},
            47: {"collision": False, "damage": 0,  "knockback": 0},
        }

        self.enemyTypes = {29 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           30 : {"class": Enemy2, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           31 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},   
                           32 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           33 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           34 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           35 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           36 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           37 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 224, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           38 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           39 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 192, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           40 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           41 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           42 : {"class": Enemy1, "health": 200, "movementType": "RANDOM", "velocity": 5, "size": 160, "suspicionRange": Setup.setup.BLOCK_WIDTH * 4.5, "detectionRange": Setup.setup.BLOCK_WIDTH * 3},
                           }

        self.bossTypes = {21 : {"class": Boss1, "health": 500, "velocity": 5, "size": 160, "phases": 1, "name": "Glod the Infected"},
                          22 : {"class": Boss2, "health": 700, "velocity": 4, "size": 160, "phases": 1, "name": "The Wretched Growth"},
                          23 : {"class": Boss3, "health": 1000, "velocity": 0, "size": 320, "phases": 1, "name": "The Weeping Maw"},
                          24 : {"class": Boss4, "health": 700, "velocity": 6, "size": 160, "phases": 1, "name": "The Forgotten Champion"},
                          25 : {"class": Boss5, "health": 2500, "velocity": 8, "size": 160, "phases": 3, "name": "Malakar, the Eclipse Stalker"},
                          26 : {"class": Boss6, "health": 3000, "velocity": 6, "size": 320, "phases": 3, "name": "Glod, Harbinger of Plague"},
                          27 : {"class": Boss7, "health": 2000, "velocity": 10, "size": 160, "phases": 1, "name": "Rychard, Brother of Richard"},
                          28 : {"class": Boss8, "health": 1750, "velocity": 12, "size": 224, "phases": 2, "name": "Vaelin the Sound Born"}
                          }

        self.bossGauntlet = PostGameBossGauntlet(self)        

    def DataToDictionary(self):
        objectListsToSave = ["enemies", "bosses", "waypoints", "treasureChests", "friendlyCharacters"]

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

        attributesToUpdate = ["enemies", "bosses", "waypoints", "treasureChests", "friendlyCharacters"]

        for attribute in attributesToUpdate:  # not creating new waypoints, only updating a small number of variables
            if attribute in data:
                newData = data[attribute]
                attributeSelf = getattr(self, attribute) # self.attribute

                if isinstance(attributeSelf, Setup.pg.sprite.Group):
                    attributeList = list(attributeSelf.sprites())
                else:
                    attributeList = attributeSelf

                for index in range(0, min(len(attributeList), len(newData))):
                    attributeList[index].LoadFromDictionary(newData[index])

        for boss in self.bosses:
            boss.ResetSelf()

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
        self.hitboxes = Setup.pg.sprite.Group()
        self.enemyHitboxes = Setup.pg.sprite.Group()
        self.playableMap = []
        self.waypoints = []
        self.treasureChests = []
        self.friendlyCharacters = []
        self.CreatePlayableMap()
               
    def CreatePlayableMap(self):
        AIR_BLOCK = 0

        NON_COLLISION_END   = 20

        FRIENDLY_CHAR_START = 43
        FRIENDLY_CHAR_END   = 47

        BOSS_START   = 21
        BOSS_END     = 28
        ENEMY_START  = 29
        ENEMY_END    = 42

        PATHFINDING_WAYPOINT = 48
        WAYPOINT_BLOCKS = {17, 18}
        TREASURE_CHEST_BLOCK  = 19

        Setup.setup.loadedMap = True

        for row in MapCreator.mapDataHandler.mapGrid.blockGrid:
            collisionMapRow = []

            for block in row:    
                if block.blockNumber <= NON_COLLISION_END or (block.blockNumber >= FRIENDLY_CHAR_START and block.blockNumber <= FRIENDLY_CHAR_END): # a block and not an entity - friendly characters cannot move so are represented as a block
                    attributes = self.blockAttributeDictionary[block.blockNumber] 

                    if attributes:
                        if attributes["collision"]:
                            collisionMapRow.append(1)
                        else:
                            collisionMapRow.append(0)

                        if block.rotation <= -360:
                            block.rotation %= 360

                        mapBlock = MapBlock(block.blockNumber, block.rotation, block.rotation // -90, block.originalLocationX, block.originalLocationY, block.image, attributes["collision"], attributes["damage"], attributes["knockback"])
                     
                        if block.blockNumber != AIR_BLOCK: # self.blocks will be used to display the blocks, block 0 is a filler block for the map creator and should not be visible in game
                            self.blocks.add(mapBlock)

                        if block.blockNumber in WAYPOINT_BLOCKS: # waypoints
                            self.waypoints.append(Waypoint(mapBlock))

                        if block.blockNumber == TREASURE_CHEST_BLOCK: # treasure chests
                            self.treasureChests.append(TreasureChest(mapBlock, len(self.treasureChests)))

                        if block.blockNumber >= FRIENDLY_CHAR_START and block.blockNumber <= FRIENDLY_CHAR_END: # friendly characters
                            self.friendlyCharacters.append(FriendlyCharacter(mapBlock, block.blockNumber - FRIENDLY_CHAR_START)) # between 0 and 4
                    else:
                        raise ValueError("block has not attributes")

                else: # entities (bosses, enemies, pathFinders)
                    collisionMapRow.append(0)

                    if block.blockNumber >= BOSS_START and block.blockNumber <= BOSS_END:
                        self.bosses.add(self.CreateBoss(block.blockNumber, block))
                    elif block.blockNumber >= ENEMY_START and block.blockNumber <= ENEMY_END:
                        self.enemies.add(self.CreateEnemy(block.blockNumber, block))
                    elif block.blockNumber == PATHFINDING_WAYPOINT:    
                        self.pathfindingWaypointBlocks.append(block)      

            self.collisionMap.append(collisionMapRow)
                        
        self.PopulateGraph(self.pathfindingWaypointBlocks)

    def CreateBoss(self, bossNumber, block=None, locationX=100, locationY=100):
        filePath = Setup.os.path.join("ASSETS", "ENEMIES", f"BOSS{bossNumber - 20}_IMAGE")
        image = Setup.pg.image.load(filePath + ".png")        
        bossClass = self.bossTypes[bossNumber]  

        if not bossClass:
            raise ValueError(f"Enemy number {bossNumber} does not exist")
          
        width = bossClass["size"]
        widthDifferenceToNormalBlock = width - Setup.setup.BLOCK_WIDTH 
       
        if block is None:
            bossWorldX = locationX
            bossWorldY = locationY - widthDifferenceToNormalBlock
        else:
            bossWorldX = block.originalLocationX
            bossWorldY = block.originalLocationY - widthDifferenceToNormalBlock

        return bossClass["class"](
            worldX = bossWorldX,
            worldY = bossWorldY,
            image = image,
            health = bossClass["health"],
            velocity = bossClass["velocity"],
            size = bossClass["size"],
            phases = bossClass["phases"],
            name = bossClass["name"],
            bossType = bossNumber,
            gameHandler = self,
        )

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
            gameHandler = self,
        )

    def PopulateGraph(self, blocks):
        self.blockNumberToObject = {}

        unweightedAdjacencyList = {0 : [1],
                                   1 : [0, 2, 38],
                                   2 : [3, 36], # cannot return to 1
                                   3 : [2, 4],
                                   4 : [3, 5, 7],
                                   5 : [4, 6, 39],
                                   6 : [5],
                                   7 : [4, 8],
                                   8 : [34, 41], # cannot return to 7
                                   9 : [10, 41],
                                   10 : [9, 11, 14],
                                   11 : [10, 12, 13],
                                   12 : [11, 37],
                                   13 : [11],
                                   14 : [42], # cannot return to 10
                                   15 : [16, 40, 42],
                                   16 : [15, 17, 18],
                                   17 : [16],
                                   18 : [16, 19, 21],
                                   19 : [18, 20, 35],
                                   20 : [19],
                                   21 : [22], # cannot return to 18
                                   22 : [21, 23, 40],
                                   23 : [22, 24],
                                   24 : [23, 25],
                                   25 : [24, 26, 28],
                                   26 : [25, 27],
                                   27 : [26],
                                   28 : [25, 29],
                                   29 : [28, 30],
                                   30 : [29, 31],
                                   31 : [30, 32],
                                   32 : [31, 33],
                                   33 : [32],
                                   34 : [8, 35],
                                   35 : [19, 34],
                                   36 : [2, 37],
                                   37 : [12, 36],
                                   38 : [1, 39],
                                   39 : [5, 38],
                                   40 : [15, 22],
                                   41 : [8, 9],
                                   42 : [14, 15]
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

        self.weightedAdjacencyList.FinaliseGraph(allNodes=unweightedAdjacencyList.keys())
        self.dijkstraGraph = Dijkstra.DijkstraImplementation(self.weightedAdjacencyList.weightedGraph)

    def UpdateSprites(self):
        allEntities = self.enemies.sprites() + self.bosses.sprites()

        for entity in allEntities:
            if not entity.dead:
                entity.PerformAction()
                entity.UpdateImage()

        hitboxesToRemove = []

        for hitbox in self.hitboxes: # player attack hitboxes
            hitbox.Update()
            
            collidedBlocks = self.CollideWithObjects(hitbox, self.blocks)
            for block in collidedBlocks:
                if "SPELL" not in hitbox.name: # delete hitbox but do not knockback player
                    if hitbox.direction == "RIGHT":
                        self.player.ApplyKnockback(block.knockback, "LEFT")
                    elif hitbox.direction == "LEFT":
                        self.player.ApplyKnockback(block.knockback, "RIGHT")

                    elif block.damage != 0:    
                        if hitbox.direction == "UP": # blocks only have vertical knockback if they also deal damage (spikes)
                            self.player.ApplyKnockback(block.knockback, "DOWN")
                        elif hitbox.direction == "DOWN":
                            self.player.ApplyKnockback(block.knockback, "UP")
                        
                hitboxesToRemove.append(hitbox)
            
            for entity in self.CollideWithObjects(hitbox, allEntities):
                if not entity.dead :
                    entity.TakeDamage(hitbox.damage, hitbox.direction)

                    if hitbox.direction == "UP": # blocks only have vertical knockback if they also deal damage (spikes)
                        self.player.ApplyKnockback(20, "DOWN")
                    elif hitbox.direction == "DOWN":
                        self.player.ApplyKnockback(20, "UP")

                    hitboxesToRemove.append(hitbox)

        for hitbox in hitboxesToRemove:
            self.hitboxes.remove(hitbox)

        hitboxesToRemove = []

        for hitbox in self.enemyHitboxes:
            hitbox.Update()

            if len(self.CollideWithObjects(hitbox, self.blocks)) > 0:
                hitboxesToRemove.append(hitbox)

            if self.CollideWithObject(hitbox, self.player) and not self.player.IsInvincible():
                self.player.TakeHealth(hitbox.damage)
                self.player.ApplyKnockback(20, hitbox.direction)

                hitboxesToRemove.append(hitbox)
                break

        for hitbox in hitboxesToRemove:
            self.enemyHitboxes.remove(hitbox)

        self.bossGauntlet.CheckStateOfBossAndPlayer(self.player)

    def ResetEntities(self):
        for entity in self.enemies.sprites() + self.bosses.sprites():
            entity.ResetSelf()

    def CollideWithObjects(self, mainObject, listOfObjects):
        collided = []
        mainObject.rect.topleft = (mainObject.worldX, mainObject.worldY)

        for collidedObject in Setup.pg.sprite.spritecollide(mainObject, listOfObjects, False):
            if hasattr(collidedObject, "collision"):
                if collidedObject.collision:
                    collided.append(collidedObject)
            else:
                collided.append(collidedObject)

        return collided

    def CollideWithObject(self, mainObject, secondObject):
        mainObject.rect.topleft = (mainObject.worldX, mainObject.worldY)
        secondObject.rect.topleft = (secondObject.worldX, secondObject.worldY)

        if Setup.pg.sprite.collide_rect(mainObject, secondObject):
            return True

        return False

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
    spellNames = ["Fireball"]
    displayImages = {}

    for x in range(0, len(spellNames)):
        displayImages.update({spellNames[x] : f"SPELL{x + 1}_IMAGE"})

    def __init__(self, name=None, description=None, damage=None, manaCost=None, parentPlayer=None):
        self.name = name
        self.description = description
        self.damage = damage
        self.manaCost = manaCost
        self.parentPlayer = parentPlayer

        self.attackToHitbox = {}
        self.instanceHandler = MultipleSpellInstancesHandler()

        self.displayImagePath = Spell.displayImages[name] if name in Spell.spellNames else Spell.displayImages["Fireball"]
        
        self.statsToDisplay = ["description", "damage", "manaCost"]

    def DataToDictionary(self):
        return {
            "name": self.name,
            "description": self.description,
            "damage": self.damage,
            "manaCost": self.manaCost,
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
            self.CreateNewInstance()

    def Update(self):
        self.UseSpell()

    def CreateNewInstance(self):
        pass
                
    def UseSpell(self):
        pass

class Fireball(Spell):
    def __init__(self, name="Fireball", description="A burning ball of fire", damage=None, manaCost=None, parentPlayer=None):
        super().__init__(name, description, damage, manaCost, parentPlayer)
      
        self.spellLength = 3
        self.spellSheet = None
        self.spellDimentions = (160, 160)
        self.velocityX = 8
        self.velocityY = 0

    def CreateNewInstance(self):
        if self.parentPlayer.mostRecentDirection == "LEFT":
            velocityX = -8
        else:
            velocityX = 8

        velocityY = 0

        self.instanceHandler.CreateNewInstance(self.spellLength, velocityX, velocityY)

    def UseSpell(self):
        finishedinstances = []

        for instanceID, attributes in self.instanceHandler.instances.items():
            timer, velocityX, velocityY = attributes

            if timer.CheckFinished():
                finishedinstances.append(instanceID)

            AttackHitboxHandler.AttackStartAndEndHandler(self, timer, f"SPELL_{instanceID}", self.spellDimentions, self.damage, velocityX, velocityY, lockMovement=False, followPlayer=False, groundOnlyAttack=False, useCenter=False)                

        for instanceID in finishedinstances:
            self.instanceHandler.instances.pop(instanceID)

class MultipleSpellInstancesHandler:
    def __init__(self):
        self.instances = {}
        self.instanceID = 0

    def CreateNewInstance(self, spellLength, velocityX, velocityY):
        self.instances.update({self.instanceID : [CooldownTimer(spellLength), velocityX, velocityY]})
        self.instanceID += 1

class Armour:
    armourNames = ["DefaultArmour", "SkinOfTheWeepingMaw"]
    displayImages = {}
    inGameImages = {}

    for x in range(0, len(armourNames)):
        displayImages.update({armourNames[x] : f"PLAYER{x + 1}_IMAGE"})
        inGameImages.update({armourNames[x] : f"PLAYER{x + 1}_WEAPON_IMAGE"})

    def __init__(self, name=None, description=None, resistance=None, armourType=None, parentPlayer=None):
        self.name = name
        self.description = description
        self.resistance = resistance
        self.armourType = armourType
        self.parentPlayer = parentPlayer

        self.displayImagePath = Armour.displayImages[name] if name in Armour.armourNames else Armour.displayImages["DefaultArmour"]
        self.image = Setup.pg.image.load(Setup.os.path.join("ASSETS", "PLAYER", self.displayImagePath) + ".png")

        self.inGameImagePath = Armour.inGameImages[name] if name in Armour.armourNames else Armour.inGameImages["DefaultArmour"]
        self.imageForGame = Setup.pg.image.load(Setup.os.path.join("ASSETS", "PLAYER", self.inGameImagePath) + ".png")

        self.statsToDisplay = ["description", "resistance"]

    def DataToDictionary(self):
        return {
            "name": self.name,
            "description": self.description,
            "resistance": self.resistance,
            "armourType": self.armourType,
        }

    @classmethod
    def DataFromDictionary(cls, data):
        return cls(
            name = data.get("name", ""),
            description = data.get("description", ""),
            resistance = data.get("resistance", 0),
            armourType = data.get("armourType", 1),
        )    

class Weapon:
    weaponNames = ["WoodenSword", "Longsword"]
    displayImages = {}

    for x in range(0, len(weaponNames)):
        displayImages.update({weaponNames[x] : f"WEAPON{x + 1}_IMAGE"})

    def __init__(self, name=None, description=None, abilityDescription=None, damage=None, chargedDamage=None, abilityDamage=None, abilityManaCost=None, abilityCooldown=None, parentPlayer=None):        
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

        self.attackToHitbox = {} # attack type e.g. basic to corresponding hitbox
       
        self.displayImagePath = Weapon.displayImages[name] if name in Weapon.weaponNames else Weapon.displayImages["WoodenSword"]
        self.image = Setup.pg.image.load(Setup.os.path.join("ASSETS", "WEAPONS", self.displayImagePath) + ".png")
        
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
        chargeAttackThreshold = 0.35 # seconds

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
                self.BasicAttack()
            case "CHARGED":
                self.ChargedAttack()
            case "ABILITY":
                self.PerformAbility()

class WoodenSword(Weapon):
    def __init__(self, name="WoodenSword", description="A weak wooden sword", abilityDescription="A quick thrust", damage=None, chargedDamage=None, abilityDamage=None, abilityManaCost=None, abilityCooldown=None, parentPlayer=None):
        super().__init__(name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer)

        self.basicAttackLengthTimer = CooldownTimer(0.5) # seconds
        self.basicAttackSheet = None
        self.basicAttackDimentions = (160, 80)

        self.chargedAttackLengthTimer = CooldownTimer(0.75)
        self.chargedAttackSheet = None
        self.chargedAttackDimentions = (240, 80)

        self.abilityAttackLengthTimer = CooldownTimer(0.7)
        self.abilityAttackSheet = None
        self.abilityAttackDimentions = (160, 80)

    def BasicAttack(self): # player stands still and slashes
        AttackHitboxHandler.AttackStartAndEndHandler(self, self.basicAttackLengthTimer, "BASIC_WOODENSWORD", self.basicAttackDimentions, self.damage, verticalAttack=True)

    def ChargedAttack(self): # player stands still and slashes heavily 
        AttackHitboxHandler.AttackStartAndEndHandler(self, self.chargedAttackLengthTimer, "CHARGED_WOODENSWORD", self.chargedAttackDimentions, self.chargedDamage)

    def PerformAbility(self): # player thrusts with the sword
        if AttackHitboxHandler.AttackStartAndEndHandler(self, self.abilityAttackLengthTimer, "ABILITY_WOODENSWORD", self.abilityAttackDimentions, self.abilityDamage, groundOnlyAttack=False):
            if self.parentPlayer.mostRecentDirection == "LEFT": # movement inputs are restricted but player can carry speed
                self.parentPlayer.carriedSpeedX = -20
            else:
                self.parentPlayer.carriedSpeedX = 20

class Longsword(Weapon):
    def __init__(self, name="Longsword", description="A long iron sword", abilityDescription="A powerful overhead swing", damage=None, chargedDamage=None, abilityDamage=None, abilityManaCost=None, abilityCooldown=None, parentPlayer=None):
        super().__init__(name, description, abilityDescription, damage, chargedDamage, abilityDamage, abilityManaCost, abilityCooldown, parentPlayer)

        self.basicAttackLengthTimer = CooldownTimer(0.6) # seconds
        self.basicAttackSheet = None
        self.basicAttackDimentions = (160, 80)

        self.chargedAttackLengthTimer = CooldownTimer(0.8)
        self.chargedAttackSheet = None
        self.chargedAttackDimentions = (240, 80)

        self.abilityAttackLengthTimer = CooldownTimer(1)
        self.abilityAttackSheet = None
        self.abilityAttackDimentions = (160, 80)

    def BasicAttack(self): # player stands still and slashes
        AttackHitboxHandler.AttackStartAndEndHandler(self, self.basicAttackLengthTimer, "BASIC_LONGSWORD", self.basicAttackDimentions, self.damage, verticalAttack=True)

    def ChargedAttack(self): # player stands still and slashes heavily 
        AttackHitboxHandler.AttackStartAndEndHandler(self, self.chargedAttackLengthTimer, "CHARGED_LONGSWORD", self.chargedAttackDimentions, self.chargedDamage)

    def PerformAbility(self): # player does an overhead swing
        AttackHitboxHandler.AttackStartAndEndHandler(self, self.abilityAttackLengthTimer, "ABILITY_LONGSWORD", self.abilityAttackDimentions, self.abilityDamage)

class AttackHitboxHandler:
    @staticmethod
    def AttackStartAndEndHandler(parentObject, timer, attackType, hitboxDimentions, damage, velocityX=0, velocityY=0, lockMovement=True, followPlayer=True, groundOnlyAttack=True, verticalAttack=False, useCenter=True):
        parentPlayer = getattr(parentObject, "parentPlayer", None)
       
        if verticalAttack:
            direction = parentPlayer.mostRecentDirectionAll
        else:
            direction = parentPlayer.mostRecentDirection

        if direction is None or attackType is None:
            AttackHitboxHandler.EndAttack(parentObject)
            return
    
        if timer.startTime is None:
            if direction in ("LEFT", "RIGHT"): # not attack up or down
                parentPlayer.movementLocked = lockMovement

                if parentPlayer.state == "AIR" and groundOnlyAttack:
                    AttackHitboxHandler.EndAttack(parentObject)
                    return
                
            timer.StartTimer()

            match direction:
                case "LEFT":
                    attackHitBox = Hitbox(attackType, "LEFT", -hitboxDimentions[0], 0, hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, velocityY, followPlayer, useCenter, parentPlayer)
                case "RIGHT":
                    attackHitBox = Hitbox(attackType,"RIGHT", hitboxDimentions[0], 0, hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, velocityY, followPlayer, useCenter, parentPlayer)
                case "UP":
                    attackHitBox = Hitbox(attackType, "UP", 0, -hitboxDimentions[1], hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, velocityY, followPlayer, useCenter, parentPlayer)
                case "DOWN":
                    attackHitBox = Hitbox(attackType, "DOWN", 0, hitboxDimentions[1], hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, velocityY, followPlayer, useCenter, parentPlayer)

            parentPlayer.gameHandler.hitboxes.add(attackHitBox)
            parentObject.attackToHitbox.update({attackType : attackHitBox})

            return True # attack start

        if timer.CheckFinished():
            AttackHitboxHandler.EndAttack(parentObject, attackType=attackType)
            timer.Reset()

    @staticmethod
    def EnemyAttackStartAndEndHandler(enemy, timer, attackType, hitboxDimentions, damage, velocityX=0, velocityY=0, lockMovement=False):
        direction = enemy.mostRecentDirection

        if direction is None or attackType is None:
            AttackHitboxHandler.EnemyEndAttack(enemy)
            return

        if timer.startTime is None:
            enemy.movementLocked = lockMovement
            timer.StartTimer()
            
            match direction:
                case "LEFT":
                    attackHitBox = Hitbox(attackType, "LEFT", -hitboxDimentions[0], 0, hitboxDimentions[0], hitboxDimentions[1], damage, -velocityX, velocityY, parentObject=enemy)
                case "RIGHT":
                    attackHitBox = Hitbox(attackType,"RIGHT", hitboxDimentions[0], 0, hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, velocityY, parentObject=enemy)
                case "UP":
                    attackHitBox = Hitbox(attackType, "UP", 0, -hitboxDimentions[1], hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, -velocityY, parentObject=enemy)
                case "DOWN":
                    attackHitBox = Hitbox(attackType, "DOWN", 0, hitboxDimentions[1], hitboxDimentions[0], hitboxDimentions[1], damage, velocityX, velocityY, parentObject=enemy)

            enemy.gameHandler.enemyHitboxes.add(attackHitBox)
            enemy.attackToHitbox.update({attackType : attackHitBox})

            return True

        if timer.CheckFinished():
            AttackHitboxHandler.EnemyEndAttack(enemy, attackType=attackType)
            timer.Reset()

    @staticmethod
    def EnemyEndAttack(enemy, attackType=None):
        if attackType:
            enemy.gameHandler.enemyHitboxes.remove(enemy.attackToHitbox[attackType])
            enemy.attackToHitbox.pop(attackType, None)
            
        enemy.currentAttackAttributes = None
        enemy.movementLocked = False

    @staticmethod
    def EndAttack(parentObject, attackType=None):
        if attackType:
            parentObject.parentPlayer.gameHandler.hitboxes.remove(parentObject.attackToHitbox[attackType])           
            parentObject.attackToHitbox.pop(attackType, None)

        parentObject.currentState = "NONE"
        parentObject.parentPlayer.movementLocked = False

class Hitbox(Setup.pg.sprite.Sprite):
    def __init__(self, hitboxType, direction, offsetX, offsetY, width, height, damage, velocityX, velocityY, followPlayer=False, useCenter=True, parentObject=None):
        super().__init__()
        self.parent = parentObject # normally player
        self.followPlayer = followPlayer      
        self.name = hitboxType
        self.useCenter = useCenter
       
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.width = width
        self.height = height
        self.velocityX = velocityX
        self.velocityY = velocityY

        self.damage = damage
        self.direction = direction

        self.rect = Setup.pg.Rect(0, 0, self.width, self.height)
        self.SetPositionFromObject()

    def SetPositionFromObject(self):
        if self.useCenter:                      
            self.worldX = self.parent.rect.centerx + self.offsetX
            self.worldY = self.parent.rect.centery + self.offsetY
            self.rect.center = (self.worldX, self.worldY)
        else:
            self.worldX = self.parent.rect.x + self.offsetX
            self.worldY = self.parent.rect.y + self.offsetY
            self.rect.topleft = (self.worldX, self.worldY)

    def UpdatePositionFromObject(self):
        if self.useCenter:
            self.rect.center = (self.worldX, self.worldY)
        else:
            self.rect.topleft = (self.worldX, self.worldY)

    def Update(self):        
        if self.followPlayer:
            self.SetPositionFromObject()
        else:
            self.worldX += self.velocityX
            self.worldY += self.velocityY           
            self.UpdatePositionFromObject()

        # visualise
        if not gameHandler.player.dead and not gameHandler.player.miniMap.enlarged and not (gameHandler.player.inventory.mainMenuOpen or gameHandler.player.inventory.equipMenuOpen):
            drawX = self.rect.x - gameHandler.player.camera.camera.left
            drawY = self.rect.y - gameHandler.player.camera.camera.top
            Setup.pg.draw.rect(Setup.setup.screen, Setup.setup.RED, (drawX, drawY, self.width, self.height))

class Inventory:
    allItems = {"DefaultArmour" : Armour,
                "DefaultWeapon" : Weapon,
                "DefaultSpell" : Spell,
                "WoodenSword" : WoodenSword, 
                "Longsword" : Longsword,
                "Fireball" : Fireball,
                "SkinOfTheWeepingMaw" : Armour,
    }

    def __init__(self, player=None, weapons=None, spells=None, armour=None, itemNames=None):
        self.weapons = weapons if weapons is not None else []
        self.spells = spells if spells is not None else []
        self.armour = armour if armour is not None else []
        self.itemNames = itemNames if itemNames is not None else [] # used to only allow for one type of item e.g. only one fireball

        self.parentPlayer = player
        self.inventoryMainMenu = Menus.menuManagement.inventoryButtonGroup
        self.inventoryEquipDisplayMenu = Menus.menuManagement.inventoryEquipDisplayButtonGroup
        self.mainMenuOpen = False
        self.equipMenuOpen = False

        self.weaponSlotButton = Menus.ButtonGroupMethods.GetButton("WEAPON_SLOT", self.inventoryMainMenu.buttons)
        self.spellSlotButton = Menus.ButtonGroupMethods.GetButton("SPELL_SLOT", self.inventoryMainMenu.buttons)
        self.armourSlotButton = Menus.ButtonGroupMethods.GetButton("ARMOUR_SLOT", self.inventoryMainMenu.buttons)
        self.buttons = {self.weaponSlotButton : "weapon", self.spellSlotButton : "spell", self.armourSlotButton : "armour"}

        self.itemTexts = {}

    def DataToDictionary(self):
        return {"itemNames": self.itemNames,
                "weapons": [weapon.DataToDictionary() for weapon in self.weapons],
                "spells": [spell.DataToDictionary() for spell in self.spells],
                "armour": [armour.DataToDictionary() for armour in self.armour]          
        }

    @classmethod
    def DataFromDictionary(cls, data):       
        itemNameToObjects = {"weapons" : [], 
                    "spells" : [], 
                    "armour" : []}

        for category, itemList in itemNameToObjects.items():
            for itemData in data.get(category, []):
                if itemData["name"] in Inventory.allItems:
                    itemClass = Inventory.allItems[itemData["name"]]
                    createdItem = itemClass().DataFromDictionary(itemData)
                    createdItem.parentPlayer = gameHandler.player
                    itemList.append(createdItem)

        return cls(weapons=itemNameToObjects["weapons"], spells=itemNameToObjects["spells"], armour=itemNameToObjects["armour"], itemNames=data["itemNames"])

    def AddItem(self, itemToAdd):
        classToList = {Weapon : self.weapons,
                       Spell : self.spells,
                       Armour : self.armour}

        for checkClass, listToAdd in classToList.items():
            if isinstance(itemToAdd, checkClass):
                if itemToAdd.name not in self.itemNames:
                    itemToAdd.parentPlayer = self.parentPlayer
                    listToAdd.append(itemToAdd)
                    self.itemNames.append(itemToAdd.name)

                break

    def DrawBackground(self):
        Setup.pg.draw.rect(Setup.setup.screen, Setup.setup.GREY, (0, 0, Setup.setup.WIDTH, Setup.setup.HEIGHT))
    
    def UpdatePlayerModelScreen(self):       
        enlargedPlayerImage = Setup.pg.transform.scale(self.parentPlayer.heads[self.parentPlayer.armour.armourType], (Setup.setup.WIDTH / 4, Setup.setup.WIDTH / 4))
        enlargedPlayerTorso = Setup.pg.transform.scale(self.parentPlayer.armour.image, (Setup.setup.WIDTH / 4, Setup.setup.WIDTH / 4))
        enlargedPlayerLegs = Setup.pg.transform.scale(self.parentPlayer.legs[self.parentPlayer.armour.armourType], (Setup.setup.WIDTH / 4, Setup.setup.WIDTH / 4))

        Setup.setup.screen.blit(enlargedPlayerImage, (Setup.setup.WIDTH / 10, (Setup.setup.HEIGHT - Setup.setup.WIDTH / 4) / 2)) # current player image unrotated
        Setup.setup.screen.blit(enlargedPlayerTorso, (Setup.setup.WIDTH / 10, (Setup.setup.HEIGHT - Setup.setup.WIDTH / 4) / 2)) 
        Setup.setup.screen.blit(enlargedPlayerLegs, (Setup.setup.WIDTH / 10, (Setup.setup.HEIGHT - Setup.setup.WIDTH / 4) / 2)) 

    def DrawHoveredItemStats(self, item):
        textToDraw = {}

        for index, attribute in enumerate(item.statsToDisplay):
            objectAttribute = getattr(item, attribute)
            uniqueIdentifier = (id(item), attribute)

            if uniqueIdentifier not in self.itemTexts:
                fontSize = 35
                spacing = fontSize * index
                newStatText = Setup.TextMethods.CreateText(item.name, f"{attribute} : {objectAttribute}", Setup.setup.WHITE, Setup.setup.WIDTH - (15 * fontSize), Setup.setup.HEIGHT // 2 + spacing, fontSize)
                self.itemTexts[uniqueIdentifier] = newStatText

            textToDraw[uniqueIdentifier] = self.itemTexts[uniqueIdentifier]

        Setup.TextMethods.UpdateText(textToDraw.values())
  
    def UpdateSelectionSlots(self):
        for button in self.buttons:
            playerAttribute = getattr(self.parentPlayer, self.buttons[button])
            
            if button.hover:                
                self.DrawHoveredItemStats(playerAttribute)
            else:
                button.ChangeImageClick(playerAttribute.displayImagePath)

    def UpdateEquipSlots(self):
        itemList = getattr(self, Menus.menuManagement.inventoryEquipDisplayButtonGroup.displayType)
        displayTypeToAttribute = {"weapons" : "weapon",
                                  "spells" : "spell",
                                  "armour" : "armour"
                                  }

        clicked = Menus.menuManagement.inventoryEquipDisplayButtonGroup.ChildActions()

        for button in Menus.menuManagement.inventoryEquipDisplayButtonGroup.buttons:           
            for item in itemList:
                if clicked == item.name:
                    item.parentPlayer = self.parentPlayer
                    setattr(self.parentPlayer, displayTypeToAttribute[Menus.menuManagement.inventoryEquipDisplayButtonGroup.displayType], item)
                    Menus.menuManagement.inventoryEquipDisplayButtonGroup.ExitButton()
                    break

                if button.name == item.name and button.hover:
                    self.DrawHoveredItemStats(item)
                    break

    def DrawItemEquipSlots(self): # in menu to equip items
        menuType = getattr(self, Menus.menuManagement.inventoryEquipDisplayButtonGroup.displayType)

        if len(Menus.menuManagement.inventoryEquipDisplayButtonGroup.buttons) != len(menuType) + 1: # check for buttons + exit button      
            width, height = 320, 320
            xLocation, yLocation = width, 200
            maxNumberOfItemsWidth = (Setup.setup.WIDTH - (width * 2)) // width
            row = 0
            index = 0

            for item in menuType:
                if index > maxNumberOfItemsWidth:
                    index = 0
                    row += 1

                itemButton = Menus.ButtonGroupMethods.CreateButton(item.name, width, height, xLocation + (width * index), yLocation + (height * row), item.displayImagePath)  
                self.inventoryEquipDisplayMenu.buttons.add(itemButton)
                index += 1
                                
    def DrawEquipMenu(self):
        self.DrawBackground()
        self.DrawItemEquipSlots()
        self.UpdateEquipSlots()
                
    def DrawMainMenu(self):      
        self.DrawBackground()
        self.UpdatePlayerModelScreen()
        self.UpdateSelectionSlots()
        
class Player(Setup.pg.sprite.Sprite):
    def __init__(self, name="Player", gameHandler=None, worldX=Setup.setup.BLOCK_WIDTH, worldY=Setup.setup.BLOCK_WIDTH, health=800, maxHealth=800, mana=300, maxMana=300, mapFragments=None, mostRecentWaypointCords=(Setup.setup.BLOCK_WIDTH, Setup.setup.BLOCK_WIDTH), weapon=None, spell=None, armour=None, inventory=None):
        super().__init__()
        self.name = name
        self.gameHandler = gameHandler
        self.worldX = worldX
        self.worldY = worldY
        self.health = health
        self.maxHealth = maxHealth
        self.damageTakenMultiplier = 1
        self.mana = mana
        self.maxMana = maxMana
        self.mapFragments = mapFragments if mapFragments is not None else {"1": True, "2": True, "3": True, "4": True} # json converts int keys to strings, which forces a conversion later, it is safer to always use string keys
        self.mostRecentWaypointCords = mostRecentWaypointCords

        attributesAndDefault = {"weapon" : WoodenSword(damage=50, chargedDamage=75, abilityDamage=125, abilityManaCost=125, abilityCooldown=5, parentPlayer=self), 
                                "spell" : Fireball(damage=60, manaCost=75, parentPlayer=self), 
                                "armour" : Armour("DefaultArmour", "No armour", resistance=0, armourType=1, parentPlayer=self), 
                                "inventory" : Inventory(self)}
        
        for attributeName, default in attributesAndDefault.items():
            attributeValue = locals()[attributeName] # gets the variable passed in as an argument e.g. weapon

            if attributeValue is None:
                setattr(self, attributeName, default) # setattr creates a new self.variable with the given name and data
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

        numberOfVariants = 2 # number of different armour types (legs and head)
        self.legs = {}
        self.heads = {}
        self.idleSheets = {}
        self.walkSheets = {}

        for x in range(1, numberOfVariants + 1):
            self.legs[x] = Setup.pg.image.load(Setup.os.path.join("ASSETS", "PLAYER", f"PLAYER{x}_LEGS_IMAGE.png"))
            self.heads[x] = Setup.pg.image.load(Setup.os.path.join("ASSETS", "PLAYER", f"PLAYER{x}_HEAD_IMAGE.png"))
            self.idleSheets[x] = Setup.SpriteSheet(Setup.os.path.join("ASSETS", "PLAYER", f"PLAYER{x}_IDLE_SHEET"), self, self.width * 8, self.width, self.height, 1)
            self.walkSheets[x] = Setup.SpriteSheet(Setup.os.path.join("ASSETS", "PLAYER", f"PLAYER{x}_WALK_SHEET"), self, self.width * 8, self.width, self.height, 1)

        self.state = "IDLE"
        self.currentFrame = 0
        self.currentSheet = self.idleSheets[1]
        self.startTime = Setup.time.time()
        self.isCrouched = False

        # movement
        self.lastNearestNode = None
        self.lastNearestNodeTimer = CooldownTimer(0.1)

        self.movementLocked = False
        self.movementSpeeds = [0, 0]
        self.keyPressVelocity = 6
        self.mostRecentDirection = "RIGHT" # LEFT AND RIGHT
        self.mostRecentDirectionAll = "RIGHT" # LEFT, RIGHT, UP AND DOWN
        self.playerYFallingSpeed = 0
        self.carriedSpeedX = 0 # dashing etc
        self.dashInvincibilityTimer = CooldownTimer(0.45)
        self.gravity = Setup.setup.GRAVITY 

        self.UpdateCurrentImage(False)       

    def DataToDictionary(self):
        return {"worldX": self.worldX if self.gameHandler.bossGauntlet.currentBoss is None else self.mostRecentWaypointCords[0],
                "worldY": self.worldY if self.gameHandler.bossGauntlet.currentBoss is None else self.mostRecentWaypointCords[1],
                "health": self.health if self.gameHandler.bossGauntlet.currentBoss is None else self.maxHealth,
                "maxHealth": self.maxHealth,
                "mana": self.mana if self.gameHandler.bossGauntlet.currentBoss is None else self.maxMana,
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
            health = data.get("health", 800),
            maxHealth = data.get("maxHealth", 800),
            mana = data.get("mana", 300),
            maxMana = data.get("maxMana", 300),
            mapFragments = data.get("mapFragments", {"1": False, "2": False, "3": False, "4": False}),
            mostRecentWaypointCords = data.get("mostRecentWaypointCords", None),
            weapon = Inventory.allItems[data.get("weapon")["name"]].DataFromDictionary(data.get("weapon")) if data.get("weapon") else None,
            spell = Inventory.allItems[data.get("spell")["name"]].DataFromDictionary(data.get("spell")) if data.get("spell") else None,
            armour = Inventory.allItems[data.get("armour")["name"]].DataFromDictionary(data.get("armour")) if data.get("armour") else None,
            inventory = Inventory.DataFromDictionary(data.get("inventory")) if data.get("inventory") else None,
        )

    def UpdateCurrentImage(self, flipImage):       
        self.torsoImage = Setup.pg.transform.flip(self.armour.imageForGame, flipImage, False)
        self.weaponImage = Setup.pg.transform.flip(self.weapon.image, flipImage, False)
        self.legsImage = Setup.pg.transform.flip(self.legs[self.armour.armourType], flipImage, False)
        self.headImage = Setup.pg.transform.flip(self.heads[self.armour.armourType], flipImage, False)

        if self.currentSheet:
            self.currentSheet.Update()
            self.currentImage = self.currentSheet.GetImage(flipImage)
            self.rect = self.currentImage.get_rect()
            self.rect.topleft = (self.worldX, self.worldY)

    def Movement(self):
        collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

        # horizontal movement
        self.worldX += self.movementSpeeds[0]
        self.rect.topleft = (self.worldX, self.worldY)

        for block in self.gameHandler.CollideWithObjects(self, self.gameHandler.blocks):
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

        for block in self.gameHandler.CollideWithObjects(self, self.gameHandler.blocks):
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
            self.movementSpeeds, self.carriedSpeedX = [0, 0], 0
        else:           
            self.OpenCloseInGameMenu()

            if not self.movementLocked and not self.inventory.mainMenuOpen and not self.inventory.equipMenuOpen:
                self.MovementKeyHandler(keys)
                self.JumpHandler(keys)
                self.DashHandler(keys)
                self.CrouchHandler(keys)

    def DisplayInventoryIfOpen(self):       
        if self.inventory.inventoryEquipDisplayMenu in Menus.menuManagement.gameMenus: # equip menu 
            self.inventory.DrawEquipMenu()
            self.inventory.equipMenuOpen = True
            self.inventory.mainMenuOpen = False
        else:
            self.inventory.equipMenuOpen = False

            if self.inventory.inventoryMainMenu in Menus.menuManagement.gameMenus: # draw main menu if open and equip menu not open 
                self.inventory.DrawMainMenu()
                self.inventory.mainMenuOpen = True
            else:
                self.inventory.mainMenuOpen = False

    def OpenCloseInGameMenu(self):
        if Setup.setup.pressedKey == Setup.pg.K_TAB and not (self.inventory.mainMenuOpen or self.inventory.equipMenuOpen):
            Menus.menuManagement.ChangeStateOfMenu(Menus.menuManagement.inGameMenuButtonGroup, "GAME", cursor=True)

    def MovementKeyHandler(self, keys):
        if keys[Setup.pg.K_d] or keys[Setup.pg.K_RIGHT]: # d key or right arrow key
            self.movementSpeeds[0] = self.keyPressVelocity

            if self.mostRecentDirection == "LEFT": # can cancel the dash if you press the opposite movemnt key
                self.carriedSpeedX = 0

            self.mostRecentDirection = "RIGHT"
            self.mostRecentDirectionAll = "RIGHT"

        elif keys[Setup.pg.K_a] or keys[Setup.pg.K_LEFT]: # a key or left arrow key
            self.movementSpeeds[0] = -self.keyPressVelocity

            if self.mostRecentDirection == "RIGHT":
                self.carriedSpeedX = 0

            self.mostRecentDirection = "LEFT"
            self.mostRecentDirectionAll = "LEFT"
        else:
            self.movementSpeeds[0] = 0

        if keys[Setup.pg.K_w] or keys[Setup.pg.K_UP]:
            self.mostRecentDirectionAll = "UP"
        elif keys[Setup.pg.K_s] or keys[Setup.pg.K_DOWN]:
            self.mostRecentDirectionAll = "DOWN"
        
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
        if keys[Setup.pg.K_LSHIFT] and (self.dashInvincibilityTimer.CheckFinished() or self.dashInvincibilityTimer.startTime is None): # pressing shift (dash) and not already in a dash
            self.dashInvincibilityTimer.StartTimer()

            if self.mostRecentDirection == "LEFT":
                self.carriedSpeedX = -32
            else:
                self.carriedSpeedX = 32

        if self.dashInvincibilityTimer.CheckFinished():
            self.dashInvincibilityTimer.Reset()

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
            self.movementSpeeds[0] = 0
            self.Inputs()
            self.ChangeSheet()
            self.UpdatePlayerMovementSpeeds()         
            self.StopPlayerOnBlockCollision()

            self.camera.Update()
            self.camera.DisplayMap()
            self.MiniMapFunctions()

            self.Attack()
            self.AbilitySpell()            
            self.weapon.Update()
            self.spell.Update()

            self.PlayerMaintenanceFunctions()       
        else:
            self.DrawDeathScreen()

    def IsInvincible(self):
        return not self.dashInvincibilityTimer.CheckFinished() and self.dashInvincibilityTimer.startTime is not None

    def TakeHealth(self, damage, fromBlock=False):
        if not self.IsInvincible() or fromBlock:
            self.health -= (1 - self.armour.resistance / 100) * damage * self.damageTakenMultiplier # resistance of 20 (reduction of 20%) = (1 - 0.2) = 0.8

    def UseMana(self, manaCost):
        if self.mana >= manaCost:
            self.manaRegenDelayTimer.StartTimer()
            self.mana -= manaCost
            return True

        return False

    def ChangeSheet(self):
        if self.state != getattr(self, "previousState", None) or self.armour.armourType != getattr(self, "previousArmourType", None):
            match self.state:
                case "IDLE":
                    self.currentSheet = self.idleSheets[self.armour.armourType]
                case "AIR":
                    self.currentSheet =  self.idleSheets[self.armour.armourType]
                case "WALK":
                    self.currentSheet = self.walkSheets[self.armour.armourType]

            self.previousState = self.state
            self.previousArmourType = self.armour.armourType
            self.currentFrame = 0

    def PlayerMaintenanceFunctions(self):
        self.PassiveManaRegeneration()
        self.DrawPlayerAndUI()
        self.KillPlayerOnKeyPress()
        self.DisplayInventoryIfOpen()

    def MiniMapFunctions(self):
        self.miniMap.ChangeScale()
        self.miniMap.DrawMap(self.gameHandler.blocks, self.gameHandler.enemies, self.gameHandler.bosses, self)
        self.miniMap.DrawWaypoints(self)
        self.UpdateNearestNode()

    def UpdateNearestNode(self):
        if self.lastNearestNodeTimer.CheckFinished() or self.lastNearestNodeTimer.startTime is None:
            self.lastNearestNodeTimer.Reset()
            self.lastNearestNodeTimer.StartTimer()

            self.lastNearestNode = self.miniMap.pathGuide.FindNearestNode(self)

    def UpdatePlayerMovementSpeeds(self):           
        if self.carriedSpeedX != 0:
            self.movementSpeeds[0] = self.carriedSpeedX

        self.movementSpeeds[1] = self.playerYFallingSpeed

        if self.carriedSpeedX < 0:
            self.carriedSpeedX = min(0, self.carriedSpeedX + 1)
        elif self.carriedSpeedX > 0:
            self.carriedSpeedX = max(0, self.carriedSpeedX - 1)

        self.playerYFallingSpeed += self.gravity

        if self.playerYFallingSpeed > 30:
            self.playerYFallingSpeed = 30 

    def StopPlayerOnBlockCollision(self):
        collisions = self.Movement()

        if collisions['bottom']:
            self.state = "IDLE"
            self.playerYFallingSpeed = 0
            self.gravity = Setup.setup.GRAVITY
            self.movementSpeeds[1] = 0

            if self.movementSpeeds[0] != 0 and self.carriedSpeedX == 0:
                self.state = "WALK"
            else:
                self.state = "IDLE"

        elif self.movementSpeeds[1] != 0:
            self.state = "AIR"

        if collisions['top']:
            self.playerYFallingSpeed = 0
            self.movementSpeeds[1] = 0

        if collisions['left'] or collisions['right']: 
            self.movementSpeeds[0] = 0

    def BlockCollision(self, block, directionOfKnockback):
        if block.topFace == directionOfKnockback and block.damage > 0: # if block has no damage, there is no knockback
            self.TakeHealth(block.damage, fromBlock=True)
            self.ApplyKnockback(block.knockback, directionOfKnockback)
            return True

        return False

    def ApplyKnockback(self, knockback, direction):
        self.gravity = 1

        if direction in ("RIGHT", "LEFT"):
            if direction == "RIGHT":
                self.carriedSpeedX = knockback # cannot dash out of a knockback
            else:
                self.carriedSpeedX = -knockback 

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
            Setup.setup.screen.blit(self.weaponImage, (drawX, drawY))

            if self.mostRecentDirection == "LEFT":
                self.UpdateCurrentImage(flipImage=True)
            else:
                self.UpdateCurrentImage(flipImage=False)

            if self.state != "WALK":
                Setup.setup.screen.blit(self.legsImage, (drawX, drawY))

            if self.state != "IDLE" and self.state != "AIR": # temp second condition
                Setup.setup.screen.blit(self.headImage, (drawX, drawY))

            self.DrawBar("HEALTH", self.health, self.maxHealth, 0, "red4", "forestgreen", "healthText")
            self.DrawBar("MANA", self.mana, self.maxMana, 50, "dimgrey", "dodgerblue3", "manaText")

    def DrawBar(self, name, currentValue, maxValue, locationY, backgroundColour, foregroundColour, textAttribute):
        if getattr(self, textAttribute, None) is None:
            fontSize = 30
            setattr(self, textAttribute, Setup.TextMethods.CreateText(name, f"{currentValue} / {maxValue}", Setup.setup.BLACK, maxValue / 2, locationY + 25, fontSize))

        Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color(backgroundColour), (0, locationY, maxValue, 50))
        Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color(foregroundColour), (0, locationY, currentValue, 50))

        textObject = getattr(self, textAttribute)
        textObject.SetText(f"{round(currentValue)} / {maxValue}")
        Setup.TextMethods.UpdateText([textObject])

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
        self.gameHandler.ResetEntities()
        self.ResetToLastLocation()
        
    def ResetToLastLocation(self):
        (self.worldX, self.worldY) = self.mostRecentWaypointCords # initialised to start location

    def ResetHealthAndMana(self):
        self.mana = self.maxMana
        self.health = self.maxHealth

    def Attack(self):
        if not self.inventory.mainMenuOpen and not self.inventory.equipMenuOpen and not self.IsInvincible() and not self.miniMap.enlarged:
            if Setup.pg.mouse.get_pressed()[0] and not self.weapon.isChargingAttack:
                self.weapon.isChargingAttack = True
                self.weapon.chargingStartTime = Setup.time.time()

            if not Setup.pg.mouse.get_pressed()[0] and self.weapon.isChargingAttack:
                currentTime = Setup.time.time()
                self.weapon.isChargingAttack = False
                self.weapon.Attack(currentTime)

    def AbilitySpell(self):    
        if not self.inventory.mainMenuOpen and not self.inventory.equipMenuOpen:
            if Setup.setup.pressedKey == Setup.pg.K_e: # has cooldown
                currentTime = Setup.time.time()
                self.weapon.Ability(currentTime)

            if Setup.setup.pressedKey == Setup.pg.K_f: # no cooldown
                self.spell.Attack()

            if Setup.setup.pressedKey == Setup.pg.K_g:
                self.gameHandler.bossGauntlet.SpawnBoss(bossNumber=21, difficulty=1) # defaults

            if Setup.setup.pressedKey == Setup.pg.K_p:
                Setup.setup.saveGame = True
                self.gameHandler.SaveGame()

class GameBackground:
    def __init__(self, gameHandler):  
        self.gameHandler = gameHandler

    def Draw(self):
        Setup.setup.screen.fill(Setup.pg.Color("gray15"))

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
    def __init__(self, parentBlock, chestNumber):
        self.parent = parentBlock
        self.prompt = Prompt("E_PROMPT_IMAGE", "e")
        self.openedImage = MapCreator.mapDataHandler.mapGrid.blockSheetHandler.GetCorrectBlockImage(self.parent.blockNumber + 1)
        self.chestOpened = False 
        
        allRewards = {0 : Longsword(damage=80,  chargedDamage=120, abilityDamage=200, abilityManaCost=150, abilityCooldown=5, parentPlayer=None),
                    1 : Armour("SkinOfTheWeepingMaw", "The skin of the weeping maw", resistance=30, armourType=2)
        } 
        
        self.reward = allRewards[chestNumber]        

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

            if self.reward:
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
            player.gameHandler.ResetEntities()
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
        self.playerIconImageEnlarged = Setup.setup.loadImage(self.playerIconFile, self.playerIconWidth * 2, self.playerIconHeight * 2)

        self.cachedMapSurface = None
        self.cachedShrinkModifier = None
        self.cachedStartX = None
        self.cachedStartY = None
        self.needsRedraw = True

        self.waypointButtons = Setup.pg.sprite.Group()
        
        self.pathGuide = PathGuide()

    def ChangeScale(self):
        if Setup.setup.pressedKey == Setup.pg.key.key_code("m"):
            self.enlarged = not self.enlarged 
            self.seeWaypoints = False
            self.needsRedraw = True
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

    def DrawMap(self, blocks, enemies, bosses, player):
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

        scaledWidth = (Setup.setup.BLOCKS_WIDE * Setup.setup.BLOCK_WIDTH) / shrinkModifier
        scaledHeight = (Setup.setup.BLOCKS_WIDE * Setup.setup.BLOCK_WIDTH) / shrinkModifier

        if (self.needsRedraw or self.cachedMapSurface is None or self.cachedShrinkModifier != shrinkModifier):
            mapImage = Setup.pg.Surface((scaledWidth, scaledHeight))
            mapImage.fill(Setup.setup.GREY)

            for block in blocks:
                newImage = Setup.pg.transform.scale(block.image, (block.width / shrinkModifier, block.height / shrinkModifier))
                newX, newY = block.worldX / shrinkModifier, block.worldY / shrinkModifier
                mapImage.blit(newImage, (newX, newY))
            
            self.cachedMapSurface = mapImage.convert()
            self.cachedShrinkModifier = shrinkModifier
            self.cachedStartX = startX
            self.cachedStartY = startY
            self.needsRedraw = False

        Setup.setup.screen.blit(self.cachedMapSurface, (self.cachedStartX, self.cachedStartY))

        for entity in enemies.sprites() + bosses.sprites():
            if not entity.dead:
                newImage = Setup.pg.transform.scale(entity.image, (entity.width / shrinkModifier, entity.height / shrinkModifier))
                newX, newY = entity.worldX / shrinkModifier, entity.worldY / shrinkModifier
                Setup.setup.screen.blit(newImage, (startX + newX, startY + newY))
        
        newPlayerX, newPlayerY = player.worldX / shrinkModifier, player.worldY / shrinkModifier
        
        self.pathGuide.DrawPathGuides(shrinkModifier, startX, startY, player.camera.camera, player)
        self.MapFragments(player, startX, startY, shrinkModifier)
        
        if not self.enlarged:  
            Setup.setup.screen.blit(self.playerIconImage, (startX + newPlayerX - (0.25 * 32), startY + newPlayerY - (0.5 * 32))) # adjusting icon location to be roughly centered on in-game player
        else:
            Setup.setup.screen.blit(self.playerIconImageEnlarged, (startX + newPlayerX - (0.5 * 32), startY + newPlayerY - 32)) 

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
        newEnd = False

        if player.miniMap.enlarged: # place and delete waypoints
            if keys[Setup.pg.K_LCTRL]:
                Setup.pg.mouse.set_visible(True)

            if Setup.pg.mouse.get_visible():
                if Setup.pg.mouse.get_pressed()[0]: # left click
                    self.active = True
                    self.mouseClickX, self.mouseClickY = Setup.pg.mouse.get_pos()
                    self.endNode = self.NearestNodeToMouseClick(player)
                    newEnd = True
                elif Setup.pg.mouse.get_pressed()[2]: # right click
                    self.ResetPath()

        if not self.active or self.endNode is None:
            return

        updatedStart = self.NearestNodeToPlayer(player)
        if updatedStart is None:
            return

        if updatedStart != self.startNode or newEnd:
            self.startNode = updatedStart
            self.PerformAlgorithm(player)

    def NearestNodeToMouseClick(self, player):
        pathfindingWaypointBlocks = player.gameHandler.pathfindingWaypointBlocks

        smallestDistanceMouse = Setup.sys.maxsize
        nearestNodeMouse = None
        miniMapOffsetX, miniMapOffsetY = 480, 60
        miniMapScale = 8

        for block in pathfindingWaypointBlocks: # get nearest node to click
            blockMiniMapX, blockMiniMapY = (block.originalLocationX // miniMapScale) + miniMapOffsetX, (block.originalLocationY // miniMapScale) + miniMapOffsetY

            distanceMouse = Setup.math.sqrt((blockMiniMapX - self.mouseClickX) ** 2 + (blockMiniMapY - self.mouseClickY) ** 2)

            if distanceMouse < smallestDistanceMouse:
                if block.DoesTextExist("PATHFINDING"):
                    smallestDistanceMouse = distanceMouse
                    nearestNodeMouse = int(block.textList[0].text)            

        return nearestNodeMouse

    def NearestNodeToPlayer(self, player):
        pathfindingWaypointBlocks = player.gameHandler.pathfindingWaypointBlocks

        smallestDistancePlayer = Setup.sys.maxsize
        nearestNodePlayer = None

        for block in pathfindingWaypointBlocks:
            distancePlayer = Setup.math.sqrt((block.originalLocationX - player.worldX) ** 2 + (block.originalLocationY - player.worldY) ** 2)
                
            if distancePlayer < smallestDistancePlayer:
                if self.CheckIfBlockIsValid(player.gameHandler.blocks, player, block): # check if it doesnt intersect a block
                    if block.DoesTextExist("PATHFINDING"):
                        smallestDistancePlayer = distancePlayer
                        nearestNodePlayer = int(block.textList[0].text)
            
        return nearestNodePlayer

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

        if self.path is None:
            return

        for blockNumber in self.path:
            if blockNumber in blockNumberToObject:
                self.pathBlockObjects.append(blockNumberToObject[blockNumber])

    def ResetPath(self):
        self.path = []
        self.pathBlockObjects = []
        self.startNode = None
        self.endNode = None
        self.active = False

    def DrawPathGuides(self, shrinkModifier, startX, startY, camera, player): 
        if self.active and self.path is not None: 
            if len(self.path) == 1: # draw from player to last waypoint
                playerCordsMini = (player.rect.centerx // shrinkModifier + startX, player.rect.centery // shrinkModifier + startY)
                blockCordsMini = ((self.pathBlockObjects[0].originalLocationX + Setup.setup.BLOCK_WIDTH // 2) // shrinkModifier + startX, (self.pathBlockObjects[0].originalLocationY + Setup.setup.BLOCK_WIDTH // 2) // shrinkModifier + startY)
                
                if Setup.math.sqrt((playerCordsMini[0] - blockCordsMini[0]) ** 2 + (playerCordsMini[1] - blockCordsMini[1]) ** 2) > 100 // shrinkModifier:
                    Setup.pg.draw.line(Setup.setup.screen, Setup.setup.RED, playerCordsMini, blockCordsMini, 80 // shrinkModifier) 
                else:
                    self.ResetPath()

                if not player.miniMap.enlarged and self.active:
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
              
        for drawObject in blocks + enemies + bosses:
            if getattr(drawObject, "dead", False):
                continue

            # check if object is on screen
            if (drawObject.worldX + drawObject.width > self.camera.left and drawObject.worldX < self.camera.right and drawObject.worldY + drawObject.height > self.camera.top and drawObject.worldY < self.camera.bottom):
                drawX = drawObject.worldX - self.camera.left
                drawY = drawObject.worldY - self.camera.top
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

class BaseEnemy(Setup.pg.sprite.Sprite):
    def __init__(self, worldX, worldY, image, health, velocity, size, enemyType, gameHandler):
        super().__init__()
        self.gameHandler = gameHandler
        self.enemyType = enemyType
        self.dead = False
        
        self.worldX = worldX
        self.worldY = worldY
        self.startLocationX = worldX
        self.startLocationY = worldY
        self.width = size
        self.height = size
        self.image = image
        self.baseImage = image
        self.rect = self.image.get_rect(topleft=(self.worldX, self.worldY))
        
        self.health = health
        self.maxHealth = health
        self.velocity = velocity
        self.slowVelocity = velocity / 2
        self.knockbackSpeedX = 0
        self.verticalSpeedY = 0
        
        #attacks
        self.currentAttackAttributes = None
        self.currentAttackTimer = CooldownTimer(10000000)
        self.attackToHitbox = {}
        self.mostRecentDirection = "LEFT"
        self.movementLocked = False
        self.attackCooldownTimer = CooldownTimer(1.5)

    def DataToDictionary(self):
        return {"enemyType": self.enemyType,
                "worldX": self.worldX,
                "worldY": self.worldY,
                "health": self.health,
                "dead": self.dead
        }

    def LoadFromDictionary(self, data):
        self.enemyType = data["enemyType"]
        self.worldX = data["worldX"]
        self.worldY = data["worldY"]
        self.health = data["health"]
        self.dead = data["dead"]

    def TakeDamage(self, damage, direction=None):
        self.health -= damage

        if direction == "RIGHT": # no knockback when hit from above or below
            self.knockbackSpeedX = 20
        elif direction == "LEFT":
            self.knockbackSpeedX = -20
        
        if self.health <= 0:
            self.dead = True

            for hitbox in self.attackToHitbox.values():
                self.gameHandler.enemyHitboxes.remove(hitbox)

            if isinstance(self, Boss) and Boss.rewards[self.enemyType] is not None:
                self.gameHandler.player.inventory.AddItem(Boss.rewards[self.enemyType])
                self.gameHandler.player.maxHealth += 100 # player gains 100 max health every time a boss is killed
                Boss.rewards[self.enemyType] = None

    def CalculateDistanceFromStart(self):
        return Setup.math.sqrt((self.worldX - self.startLocationX) ** 2 + (self.worldY - self.startLocationY))

    def CalculateDistanceFromPlayer(self, fromStartLocation=False):
        if fromStartLocation:
            return Setup.math.sqrt((self.startLocationX - self.gameHandler.player.worldX) ** 2 + (self.startLocationY - self.gameHandler.player.worldY) ** 2)

        return Setup.math.sqrt((self.worldX - self.gameHandler.player.worldX) ** 2 + (self.worldY - self.gameHandler.player.worldY) ** 2)

    def CheckCollisionWithGround(self):
        hasCollision = True

        self.worldY += 1
        self.rect.topleft = (self.worldX, self.worldY)

        collidedBlock = self.CheckCollisionMap()
        if collidedBlock is None:
            hasCollision = False

        self.worldY -= 1
        self.rect.topleft = (self.worldX, self.worldY)

        return hasCollision

    def UpdateImage(self):
        if self.mostRecentDirection == "RIGHT":
            self.image = Setup.pg.transform.flip(self.baseImage, True, False)
        else:
            self.image = self.baseImage

    def ApplyKnockback(self):
        if getattr(self, "knockbackSpeedX", 0) != 0:
            self.worldX += self.knockbackSpeedX

            if self.knockbackSpeedX < 0:
                self.knockbackSpeedX = min(0, self.knockbackSpeedX + 1)
            elif self.knockbackSpeedX > 0:
                self.knockbackSpeedX = max(0, self.knockbackSpeedX - 1)

            self.rect.topleft = (self.worldX, self.worldY)

            collidedBlock = self.CheckCollisionMap()
            if collidedBlock is not None:
                if self.knockbackSpeedX > 0:
                    self.worldX = collidedBlock - self.rect.width
                elif self.knockbackSpeedX < 0:
                    self.worldX = collidedBlock + Setup.setup.BLOCK_WIDTH

                self.knockbackSpeedX = 0 
                self.rect.topleft = (self.worldX, self.worldY)

    def Falling(self):
        self.worldY += self.verticalSpeedY

        if not self.CheckCollisionWithGround():
            self.verticalSpeedY += Setup.setup.GRAVITY

            if self.verticalSpeedY > 30:
                self.verticalSpeedY = 30 
        else:
            if self.verticalSpeedY >= Setup.setup.GRAVITY * 10:          
                self.health = -1 # fall damage
                self.dead = True

            self.worldY -= self.verticalSpeedY
            self.verticalSpeedY = 0   
            
    def CheckCollisionMap(self):
        collisionMap = self.gameHandler.collisionMap
        blockSize = Setup.setup.BLOCK_WIDTH

        startX = int(self.worldX // blockSize)
        endX   = int((self.worldX + self.rect.width) // blockSize)
        startY = int(self.worldY // blockSize)
        endY   = int((self.worldY + self.rect.height) // blockSize)

        maxRows = len(collisionMap)
        maxCols = len(collisionMap[0]) if maxRows > 0 else 0
        startX = max(0, min(startX, maxCols - 1))
        endX   = max(0, min(endX, maxCols - 1))
        startY = max(0, min(startY, maxRows - 1))
        endY   = max(0, min(endY, maxRows - 1))

        for y in range(startY, endY + 1):
            for x in range(startX, endX + 1):
                if collisionMap[y][x] == 1: # block has collision
                    blockRect = Setup.pg.Rect(x * blockSize, y * blockSize, blockSize, blockSize)
                    if self.rect.colliderect(blockRect):
                        return blockRect.left
        return None
            
    def MoveToPoint(self, endLocation, velocity):
        if self.movementLocked:
            return False

        velocity *= max(0.8, Setup.random.random())

        direction = None
        changeInLocationX = 0
        distanceToEndLocation = abs(endLocation - self.worldX)

        if distanceToEndLocation < self.velocity:
            return True
                     
        if self.worldX > endLocation: 
            changeInLocationX = -velocity - self.width 
            direction = "LEFT"
        else:
            changeInLocationX = velocity + self.width 
            direction = "RIGHT"

        self.mostRecentDirection = direction
        self.worldX += changeInLocationX # +/- self.width checks if any part of the enemy has no contact with the ground 
        self.rect.topleft = (self.worldX, self.worldY)
        
        if not self.CheckCollisionWithGround():
            self.worldX -= changeInLocationX      
        elif direction == "RIGHT":
            self.worldX -= self.width
        elif direction == "LEFT":
            self.worldX += self.width

        collidedBlock = self.CheckCollisionMap()
        if collidedBlock is not None:
            if direction == "RIGHT":
                self.worldX = collidedBlock - self.rect.width 

            elif direction == "LEFT": 
                self.worldX = collidedBlock + Setup.setup.BLOCK_WIDTH           

        self.rect.topleft = (self.worldX, self.worldY)    

    def PerformAttack(self):   
        self.ChooseAttack()

        if self.currentAttackAttributes:
            attackType = self.currentAttackAttributes["attackType"]
            dimentions = self.currentAttackAttributes["dimentions"]
            damage = self.currentAttackAttributes["damage"]
            velocityX = self.currentAttackAttributes.get("velocityX", 0)
            velocityY = self.currentAttackAttributes.get("velocityY", 0)
            lockMovement = True

            AttackHitboxHandler.EnemyAttackStartAndEndHandler(self, self.currentAttackTimer, attackType, dimentions, damage, velocityX, velocityY, lockMovement)

    def ChooseAttack(self):     
        availableAttacks = []

        if self.attackCooldownTimer.startTime is None:
            for attack, attackAttributes in self.attacks.items():
                if self.CalculateDistanceFromPlayer() <= attackAttributes["range"]:
                    availableAttacks.append((attack, attackAttributes))

            if availableAttacks and self.currentAttackTimer.startTime is None:
                attack, attackAttributes = Setup.random.choice(availableAttacks)

                self.currentAttackAttributes = dict(attackAttributes)
                self.currentAttackAttributes.update({"attackType" : attack})
                self.currentAttackTimer.cooldown = attackAttributes["length"]
                self.attackCooldownTimer.StartTimer()

        if self.attackCooldownTimer.CheckFinished():
            self.attackCooldownTimer.Reset()

class Enemy(BaseEnemy):
    def __init__(self, worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, enemyType, gameHandler)

        # detection
        self.suspicionRange = suspicionRange
        self.detectionRange = detectionRange
        self.state = "NORMAL" # "NORMAL", "SUSPICIOUS", "DETECTED", "RETURNING"       
        self.detectedPlayerLocation = None
        self.suspicionTimer = CooldownTimer(5)
        self.suspicionWaitTimer = CooldownTimer(3) # how long the enemy waits at the detected player location before returning
        self.outsideSuspicionRangeWhenDetected = CooldownTimer(5) # how long the player must be outside the suspicion range for the enemy to go from DETECTED to SUSPICIOUS
        self.randomMovementTimer = CooldownTimer(3) # how often the enemy decides a new direction

        self.movementClasses = {"STATIONARY" : None,
                                  "GUARD" : GuardMovement,
                                  "RANDOM" : RandomMovement
                                  }

        if self.movementClasses[movementType] is not None:
            self.movementClass = self.movementClasses[movementType]()
        else:
            self.movementClass = None  

    def ResetSelf(self):
        if self.dead:
            self.dead = False
            
        self.health = self.maxHealth           
        self.worldX, self.worldY = (self.startLocationX, self.startLocationY)
        self.rect.topleft = (self.worldX, self.worldY)
        self.state = "NORMAL"
        self.knockbackSpeedX = 0
        self.verticalSpeedY = 0
        self.detectedPlayerLocation = 0
        self.suspicionTimer.Reset()
        self.suspicionWaitTimer.Reset()
        self.outsideSuspicionRangeWhenDetected.Reset()
        self.randomMovementTimer.Reset()

    def DisplayHealthBar(self):
        if not self.gameHandler.player.dead and not self.gameHandler.player.miniMap.enlarged and not (self.gameHandler.player.inventory.mainMenuOpen or self.gameHandler.player.inventory.equipMenuOpen):
            drawX = self.worldX - self.gameHandler.player.camera.camera.left
            drawY = self.worldY - self.gameHandler.player.camera.camera.top - 10 # shift up slightly to draw above enemy

            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("red4"), (drawX, drawY, self.maxHealth, 10)) # red health bar (background of bar)
            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("forestgreen"), (drawX, drawY, self.health, 10)) # green health bar

    def UpdateState(self):
        distanceFromPlayer = self.CalculateDistanceFromPlayer()

        if distanceFromPlayer <= self.detectionRange:
            self.state = "DETECTED"
            self.outsideSuspicionRangeWhenDetected.Reset()

        elif distanceFromPlayer <= self.suspicionRange:
            if self.state != "DETECTED" and self.state != "RETURNING": # must be within detection range to detect player while returning
                self.state = "SUSPICIOUS"
                self.detectedPlayerLocation = (self.gameHandler.player.worldX, self.gameHandler.player.worldY)

        elif distanceFromPlayer > self.suspicionRange and self.state == "DETECTED":
            self.TransitionFromDetectedToSuspicion()

    def TransitionFromDetectedToSuspicion(self):
        if self.outsideSuspicionRangeWhenDetected.startTime is None:
                self.outsideSuspicionRangeWhenDetected.StartTimer()
        else:
            if self.outsideSuspicionRangeWhenDetected.CheckFinished():
                self.state = "SUSPICIOUS"                   
                self.outsideSuspicionRangeWhenDetected.Reset()

                if self.gameHandler.player.worldX < self.worldX:
                    self.detectedPlayerLocation = (self.worldX - self.suspicionRange, self.worldY)
                else:
                    self.detectedPlayerLocation = (self.worldX + self.suspicionRange, self.worldY)

    def PerformAction(self):
        self.DisplayHealthBar()
        self.PerformAttack()
        self.ApplyKnockback()
        self.Falling()

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
        playerX = self.gameHandler.player.worldX # the current location

        self.MoveToPoint(playerX, self.velocity)

    def Suspicious(self):
        playerX = self.detectedPlayerLocation[0] # enemies move left and right

        if self.suspicionTimer.startTime is None:
            self.suspicionTimer.StartTimer()

        if self.MoveToPoint(playerX, self.slowVelocity) or self.suspicionTimer.CheckFinished():
            self.suspicionTimer.Reset()

            if self.suspicionWaitTimer.startTime is None:
               self.suspicionWaitTimer.StartTimer()

        if self.suspicionWaitTimer.CheckFinished():
            self.state = "RETURNING"
            self.suspicionWaitTimer.Reset()

    def Returning(self):    
        if self.MoveToPoint(self.startLocationX, self.slowVelocity):
            self.state = "NORMAL"
                    
    def PerformMovement(self):
        self.movementClass.Movement(self)

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
            enemy.MoveToPoint(enemy.startLocationX, enemy.slowVelocity) # return to start
        if self.direction == "RIGHT":
            targetX = min(enemy.startLocationX + self.maxDistanceFromStart, enemy.worldX + self.maxDistanceFromStart)
            enemy.MoveToPoint(targetX, enemy.slowVelocity) # anywhere to the right
        elif self.direction == "LEFT":
            targetX = max(enemy.startLocationX - self.maxDistanceFromStart, enemy.worldX - self.maxDistanceFromStart)
            enemy.MoveToPoint(targetX, enemy.slowVelocity) # anywhere to the left    

class Enemy1(Enemy):
    def __init__(self, worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, gameHandler):
        super().__init__(worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 50, "range" : Setup.setup.BLOCK_WIDTH * 1.25, "length" : 1, "dimentions" : [160, 80]},
                        "ATTACK_2" : {"damage" : 75, "range" : Setup.setup.BLOCK_WIDTH * 1.25, "length" : 1, "dimentions" : [240, 80]}}

class Enemy2(Enemy):
    def __init__(self, worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, gameHandler):
        super().__init__(worldX, worldY, image, health, movementType, velocity, size, suspicionRange, detectionRange, enemyType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 25, "range" : Setup.setup.BLOCK_WIDTH * 1, "length" : 1, "dimentions" : [160, 80]},
                        "ATTACK_2" : {"damage" : 40, "range" : self.detectionRange, "length" : 2, "dimentions" : [80, 80], "velocityX" : 10}}

class Boss(BaseEnemy):
    rewards = {21 : None,
               22 : None,
               23 : None,
               24 : None,
               25 : None,
               26 : None,
               27 : None,
               28 : None
    }

    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, bossType, gameHandler)
        self.name = name
        self.nameText = None

        self.currentPhase = 1
        self.numberOfPhases = phases 
        self.bossDetectionRange = Setup.setup.BLOCK_WIDTH * 3 # all bosses have the same range - if the player is within this range then the boss fight begins
        self.bossFightRange = Setup.setup.BLOCK_WIDTH * 10 # if the player leaves the fight range (from the bosses start location), the fight resets
        self.state = "NORMAL" # "NORMAL", "DETECTED"

    def PerformAction(self):
        self.PerformPhaseChange()
        self.PerformAttack()
        self.IsPlayerWithinRange()
        self.ApplyKnockback()
        self.Falling()

        if self.state == "DETECTED":
            self.Detected()

    def Detected(self):
        playerX = self.gameHandler.player.worldX # the current location
        self.MoveToPoint(playerX, self.velocity)

        self.DisplayHealthBar()

    def DisplayHealthBar(self):       
        if self.nameText is None:
            fontSize = 30
            self.nameText = Setup.TextMethods.CreateText(f"BOSS_{self.enemyType}", self.name, Setup.setup.BLACK, Setup.setup.WIDTH // 2, Setup.setup.HEIGHT - 75, fontSize)

        if not self.gameHandler.player.dead and not self.gameHandler.player.miniMap.enlarged and not (self.gameHandler.player.inventory.mainMenuOpen or self.gameHandler.player.inventory.equipMenuOpen):
            scale = 0.5
            barMaxWidth = self.maxHealth * scale
            barCurrentWidth = self.health * scale
            
            drawX = (Setup.setup.WIDTH // 2) - (barMaxWidth // 2) 
            drawY = Setup.setup.HEIGHT - 100
            
            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("red4"), (drawX, drawY, barMaxWidth, 50)) # red health bar (background of bar)
            Setup.pg.draw.rect(Setup.setup.screen, Setup.pg.Color("forestgreen"), (drawX, drawY, barCurrentWidth, 50)) # green health bar
            Setup.TextMethods.UpdateText([self.nameText])

    def IsPlayerWithinRange(self):
        distance = self.CalculateDistanceFromPlayer(fromStartLocation=True)

        if distance < self.bossDetectionRange or (self.health < self.maxHealth and (self.worldX, self.worldY) == (self.startLocationX, self.startLocationY)): # if the player damages the boss, it detects the player
            self.state = "DETECTED"
        elif distance > self.bossFightRange:
            self.ResetSelf()

    def PerformPhaseChange(self):
        if self.currentPhase < self.numberOfPhases:
            if self.numberOfPhases == 2:
                if self.health <= self.maxHealth // 2:
                    self.UpdatePhase("Two")

            elif self.numberOfPhases == 3:
                if self.health <= (1 / 3) * self.maxHealth:
                    self.UpdatePhase("Two")
                elif self.health <= (2 / 3) * self.maxHealth:
                    self.UpdatePhase("Three")

    def UpdatePhase(self, phase):
        self.health = min(self.health * 2, self.maxHealth)
        self.currentPhase += 1
        newAttacks = getattr(self, f"phase{phase}Attacks", None)

        if newAttacks:
            self.attacks.update(newAttacks)

    def ResetSelf(self):
        self.state = "NORMAL"
        self.health = self.maxHealth
        self.worldX, self.worldY = self.startLocationX, self.startLocationY
        self.rect.topleft = (self.worldX, self.worldY)
        self.currentPhase = 1

class Boss1(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 50, "range" : Setup.setup.BLOCK_WIDTH * 1.25, "length" : 1, "dimentions" : [160, 80]},
                        "ATTACK_2" : {"damage" : 75, "range" : Setup.setup.BLOCK_WIDTH * 1.25, "length" : 1.25, "dimentions" : [240, 80]}}

        self.phaseTwoAttacks = {"ATTACK_3" : {"damage" : 100, "range" : Setup.setup.BLOCK_WIDTH * 1.25, "length" : 2, "dimentions" : [160, 80]}}

class Boss2(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 50, "range" : Setup.setup.BLOCK_WIDTH * 1.5, "length" : 1.25, "dimentions" : [240, 80]},
                        "ATTACK_2" : {"damage" : 125, "range" : Setup.setup.BLOCK_WIDTH * 3, "length" : 2, "dimentions" : [240, 80], "velocityX" : 8},
                        "ATTACK_3" : {"damage" : 100, "range" : Setup.setup.BLOCK_WIDTH * 3, "length" : 2, "dimentions" : [160, 80], "velocityX" : 10}}

class Boss3(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 50, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 1, "dimentions" : [160, 160]},
                        "ATTACK_2" : {"damage" : 125, "range" : Setup.setup.BLOCK_WIDTH * 2.5, "length" : 1.5, "dimentions" : [240, 160]},
                        "ATTACK_3" : {"damage" : 100, "range" : Setup.setup.BLOCK_WIDTH * 4, "length" : 2, "dimentions" : [160, 160], "velocityX" : 16}}

class Boss4(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 50, "range" : Setup.setup.BLOCK_WIDTH * 0.5, "length" : 0.5, "dimentions" : [80, 80]},
                        "ATTACK_2" : {"damage" : 80, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 1.5, "dimentions" : [160, 80]},
                        "ATTACK_3" : {"damage" : 150, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 2, "dimentions" : [240, 80]},
                        "ATTACK_4" : {"damage" : 200, "range" : Setup.setup.BLOCK_WIDTH * 0.5, "length" : 2.5, "dimentions" : [80, 40]}}

class Boss5(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 100, "range" : Setup.setup.BLOCK_WIDTH * 1.5, "length" : 1.5, "dimentions" : [160, 80]},
                        "ATTACK_2" : {"damage" : 150, "range" : Setup.setup.BLOCK_WIDTH * 1.25, "length" : 1.25, "dimentions" : [160, 160]},
                        "ATTACK_3" : {"damage" : 75, "range" : Setup.setup.BLOCK_WIDTH * 2.5, "length" : 1, "dimentions" : [420, 80]}}

        self.phaseTwoAttacks = {"ATTACK_4" : {"damage" : 200, "range" : Setup.setup.BLOCK_WIDTH * 1.5, "length" : 1.25, "dimentions" : [160, 240]}}

        self.phaseThreeAttacks = {"ATTACK_5" : {"damage" : 300, "range" : Setup.setup.BLOCK_WIDTH * 1, "length" : 1, "dimentions" : [160, 160]}}

class Boss6(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 100, "range" : Setup.setup.BLOCK_WIDTH * 1.5, "length" : 1.5, "dimentions" : [240, 240]},
                        "ATTACK_2" : {"damage" : 150, "range" : Setup.setup.BLOCK_WIDTH * 2.5, "length" : 1.25, "dimentions" : [420, 240]},
                        "ATTACK_3" : {"damage" : 100, "range" : Setup.setup.BLOCK_WIDTH * 3, "length" : 1.5, "dimentions" : [500, 160]}}

        self.phaseTwoAttacks = {"ATTACK_4" : {"damage" : 175, "range" : Setup.setup.BLOCK_WIDTH * 2.5, "length" : 2, "dimentions" : [400, 240]}}

        self.phaseThreeAttacks = {"ATTACK_5" : {"damage" : 400, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 3, "dimentions" : [240, 420]}}

class Boss7(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 125, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 1, "dimentions" : [320, 40]},
                        "ATTACK_2" : {"damage" : 125, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 1.25, "dimentions" : [240, 80]},
                        "ATTACK_3" : {"damage" : 200, "range" : Setup.setup.BLOCK_WIDTH * 1, "length" : 1.5, "dimentions" : [240, 80]},
                        "ATTACK_4" : {"damage" : 200, "range" : Setup.setup.BLOCK_WIDTH * 0.5, "length" : 1, "dimentions" : [160, 120]}}

class Boss8(Boss):
    def __init__(self, worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler):
        super().__init__(worldX, worldY, image, health, velocity, size, phases, name, bossType, gameHandler)

        self.attacks = {"ATTACK_1" : {"damage" : 150, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 1.25, "dimentions" : [240, 100]},
                        "ATTACK_2" : {"damage" : 200, "range" : Setup.setup.BLOCK_WIDTH * 1.5, "length" : 1.5, "dimentions" : [160, 80]},
                        "ATTACK_3" : {"damage" : 400, "range" : Setup.setup.BLOCK_WIDTH * 0.5, "length" : 3, "dimentions" : [80, 80]}}

        self.phaseTwoAttacks = {"ATTACK_4" : {"damage" : 200, "range" : Setup.setup.BLOCK_WIDTH * 3, "length" : 3, "dimentions" : [80, 80] , "velocityX" : 5},
                        "ATTACK_5" : {"damage" : 150, "range" : Setup.setup.BLOCK_WIDTH * 2, "length" : 2, "dimentions" : [160, 80] , "velocityX" : 10},
                        "ATTACK_6" : {"damage" : 50, "range" : Setup.setup.BLOCK_WIDTH * 5, "length" : 1.5, "dimentions" : [240, 40], "velocityX" : 20}}

class FriendlyCharacter:
    allItems = {0 : "map",
                    1 : "map",
                    2 : "map",
                    3 : "map",
                    4 : Armour("SkinOfTheWeepingMaw", "The skin of the weeping maw", resistance=20, armourType=2)}

    allText = {0 : ["Hello, I haven't seen you here before", 
                        "I'm Richard, nice to meet you!",
                        "Just a warning, you should be careful around here", 
                        "Good luck on your journey, take this map to help you!"],

                    1 : ["I didn't think I would see you again!",
                         "I hope that my map was of assistance",
                         "But anyway, more about this world",
                         "Every day our world becomes more corrupt", 
                         "I'm certian you've already experienced it",
                         "I would recommend not travelling too far", 
                         "You don't want to see how this ends",
                         "For now, take another map, you'll need it!"],

                    2 : ["Hey, you really should stop, it's too dangerous to continue",
                         "I'm losing a part of myself staying here, but it was already too late",
                         "I belong here, you will never understand what we have all been through",
                         "My brother is still out here, wandering aimlessly", 
                         "But i'm afraid that he has already lost his soul",
                         "Yet again, i'll give you what I have left"],

                    3 : ["Well, you've ignored my warnings",
                         "You've seen what i've become",
                         "Was it worth it?",
                         "...",
                         "You're coming closer to meeting him",
                         "The reason it all started",
                         "But believe me, he is unstoppable",
                         "Just give up",
                         "I have another map, maybe find some more equippment first",
                         "Then return back to when I first met you",
                         "I fear this is the last time we will see eachother",
                         "...",
                         "Goodbye..."],

                    4 : ["...",
                         "A rotting corpse",
                         "Merely a shell of what once existed",
                         "The epitome of plague",
                         "..."]}

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
            self.FriendlyCharacterFunction(player) 
        else:
            self.displayActive = False

    def FriendlyCharacterFunction(self, player):
        if self.prompt.PromptInteractedWith() or self.displayActive:
            self.displayActive = True
            Setup.pg.draw.rect(Setup.setup.screen, Setup.setup.GREY, (410, Setup.setup.HEIGHT * (4 / 5), 1100, Setup.setup.HEIGHT // 5)) # background

            textSize = 30
            dialogueText = Setup.TextMethods.CreateText(f"{self.textNumber}", self.text[self.textNumber], Setup.setup.WHITE, Setup.setup.WIDTH // 2, Setup.setup.HEIGHT * (4.5 / 5), textSize)
            lineNumberText = Setup.TextMethods.CreateText(f"LINE_NUMBER", f"{self.textNumber + 1} / {len(self.text)}", Setup.setup.WHITE, 410 + (textSize * 1.5), Setup.setup.HEIGHT * (4 / 5) + textSize, textSize)
            nameText = Setup.TextMethods.CreateText(f"NPC_NAME", "Richard", Setup.setup.WHITE, 410 + (textSize * 2), Setup.setup.HEIGHT - textSize, textSize)

            Setup.TextMethods.UpdateText([dialogueText, lineNumberText, nameText])

            if Setup.setup.pressedKey == Setup.pg.K_RETURN:
                if self.textNumber < len(self.text) - 1:
                    self.textNumber += 1
                else:
                    self.displayActive = False
                    if self.item != "map":
                        player.inventory.AddItem(self.item)
                        self.item = None
                    else:
                        for fragment, value in player.mapFragments.items():
                            if not value:
                                player.mapFragments[fragment] = True
                                self.item = None
                                break

                        self.item = None

class PostGameBossGauntlet:
    def __init__(self, gameHandler):
        self.gameHandler = gameHandler

        self.bossLocationX, self.bossLocationY = 7000, 7360
        self.currentBoss = None
        self.selectedDifficulty = 1
        self.selectedBoss = 21

    def SpawnBoss(self, bossNumber, difficulty):
        if self.currentBoss is not None:
            return
        
        self.currentBoss = self.gameHandler.CreateBoss(bossNumber, locationX=self.bossLocationX, locationY=self.bossLocationY)
        self.gameHandler.bosses.add(self.currentBoss)
        self.TeleportPlayer(self.gameHandler.player, difficulty)

    def TeleportPlayer(self, player, difficulty):
        player.worldX, player.worldY = self.bossLocationX - (Setup.setup.BLOCK_WIDTH * 5), self.bossLocationY 
        player.health = player.maxHealth
        player.mana = player.maxMana

        if difficulty == 2: # player takes double damage and has half the mana regeneration speed
            player.damageTakenMultiplier = 2 
            player.manaRegenerationSpeed = 25 / 60 
        elif difficulty == 3: # player dies in one hit and does not regenerate mana
            player.damageTakenMultiplier = 1000
            player.manaRegenerationSpeed = 0

    def ChangeDifficulty(self, difficulty, player):
        self.selectedDifficulty = difficulty
        self.selectedBoss = self.currentBoss.enemyType

        self.ResetPlayerAndBoss(player)  

        self.SpawnBoss(self.selectedBoss, self.selectedDifficulty)

    def ChangeBoss(self, bossNumber, player):
        if bossNumber > 28:
            bossNumber = 21

        if bossNumber < 21:
            bossNumber = 28

        self.selectedBoss = bossNumber

        self.ResetPlayerAndBoss(player)

        self.SpawnBoss(self.selectedBoss, self.selectedDifficulty)

    def CheckStateOfBossAndPlayer(self, player):
        if self.currentBoss is None:
            return

        if Setup.setup.pressedKey == Setup.pg.K_1:
            self.ChangeDifficulty(1, player)
        elif Setup.setup.pressedKey == Setup.pg.K_2:
            self.ChangeDifficulty(2, player)
        elif Setup.setup.pressedKey == Setup.pg.K_3:
            self.ChangeDifficulty(3, player)

        if Setup.setup.pressedKey == Setup.pg.K_i:
            self.ChangeBoss(self.selectedBoss - 1, player)
        elif Setup.setup.pressedKey == Setup.pg.K_o:
            self.ChangeBoss(self.selectedBoss + 1, player)        

        if self.currentBoss.dead or player.dead:
            self.ResetPlayerAndBoss(player)
            self.selectedDifficulty = 1
            self.selectedBoss = 21

    def ResetPlayerAndBoss(self, player):
        self.gameHandler.bosses.remove(self.currentBoss)
        self.currentBoss = None   
        player.damageTakenMultiplier = 1
        player.manaRegenerationSpeed = 50 / 60
        player.Respawn()

gameHandler = GameHandler()