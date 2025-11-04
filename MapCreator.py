import Setup
import Menus

class BlockSheetExtractor():
    def __init__(self):
        self.filePath = Setup.os.path.join("ASSETS", "BLOCK_SHEET", "ALL_BLOCK_SHEET_IMAGE")
        self.sheet = Setup.pg.image.load(self.filePath + ".png").convert_alpha()
        self.sheetHover = Setup.pg.image.load(self.filePath + "_HOVER.png").convert_alpha()

        self.blockWidth = Setup.setup.BLOCK_WIDTH
        self.blockHeight = Setup.setup.BLOCK_WIDTH
        self.zoomLevels = []
        for x in range(2, 21):
            self.zoomLevels.append(round(x * 0.05, 2))
       
        self.blockCache = {} # {(blockPos, isHover, rotation, zoom) : Surface}
        self.PreloadBlockImages()
        
    def PreloadBlockImages(self):
        totalBlocks = self.sheet.get_width() // self.blockWidth

        for blockPos in range(totalBlocks): # create a cache of all possible image
            for hover in [False, True]:
                availableRotations = [0]
                if blockPos <= 16: # only normal blocks can be rotated (lantern onwards cannot be rotated)
                    availableRotations = [0, 90, 180, 270]

                for rotation in availableRotations:
                    image = Setup.pg.Surface((self.blockWidth, self.blockHeight), Setup.pg.SRCALPHA)
                    
                    if hover:
                        sheetType = self.sheetHover
                    else:
                        sheetType = self.sheet

                    image.blit(sheetType, (0, 0), (blockPos * self.blockWidth, 0, self.blockWidth, self.blockHeight))

                    if rotation != 0:
                        image = Setup.pg.transform.rotate(image, rotation)

                    for zoom in self.zoomLevels:
                        if zoom != 1:
                            imageZoom = Setup.pg.transform.scale(image, (int(self.blockWidth * zoom), int(self.blockHeight * zoom)))
                        else:
                            imageZoom = image

                        self.blockCache[(blockPos, hover, rotation, zoom)] = imageZoom

    def GetCorrectBlockImage(self, blockPos, isHover=False, rotation=0, zoom=1):
        if blockPos > 16:
            rotation = 0
        rotation %= 360

        return self.blockCache[(blockPos, isHover, rotation, round(zoom, 2))]

class MapDataHandling():
    def __init__(self):
        self.filePath = Setup.os.path.join("ASSETS", "MAP", "MAP_DATA_FILE")
        self.mapGrid = MapGrid()

        self.LoadDataOrCreateMap()

    def SaveData(self, blockGrid):
        file = open(self.filePath + ".txt", "w")

        dataLine = ""

        for row in blockGrid:
            for block in row:
                if block.blockNumber >= 10:
                    dataLine += str(block.blockNumber) 
                else:
                    dataLine += "0" + str(block.blockNumber)

                if block.rotation <= -360:
                    block.rotation %= -360

                dataLine += str(block.rotation // -90) # 0 for no rotation, 1 for a 90 degree rotation. Keeps data stored as a single number. Using -90 to avoid storing a negative sign (fixed in data loading)
                
                if block.DoesTextExist("PATHFINDING"):
                    if len(block.textList[0].text) != 0:
                        blockNodeNumber = int(block.textList[0].text)
                    else:
                        blockNodeNumber = 99

                    if blockNodeNumber >= 10:
                        dataLine += str(blockNodeNumber)
                    else:
                        dataLine += "0" + str(blockNodeNumber)
                else:
                    dataLine += "99"
    
                dataLine += " "

            dataLine += "\n" 
        
        file.write(dataLine) 

        file.close()

    def LoadData(self):
        file = open(self.filePath + ".txt")

        blockWidth = Setup.setup.BLOCK_WIDTH

        row = []
        grid = []

        fileData = file.readlines()

        fileNumberOfLines = len(fileData)

        for YPosition in range(fileNumberOfLines):
            lineData = fileData[YPosition].split(' ')      
            lineData.remove('\n')
             
            for XPosition in range(len(lineData)):
                blockNumber = int(lineData[XPosition][0] + lineData[XPosition][1]) 
                rotation = int(lineData[XPosition][2]) * -90
                blockNodeNumber = lineData[XPosition][3] + lineData[XPosition][4]

                newBlock = Menus.BlockButton("BLOCK", blockWidth, blockWidth, XPosition * blockWidth, YPosition * blockWidth, blockNumber, rotation, self.mapGrid.blockSheetHandler.GetCorrectBlockImage(blockNumber, False, rotation, 1))
                self.mapGrid.PathFindingWaypoints(newBlock, blockNodeNumber)
                row.append(newBlock)

            grid.append(row)
            row = []

        file.close()

        return grid

    def LoadDataOrCreateMap(self):
        file = open(self.filePath + ".txt", "r")

        numberOfLines = len(file.readlines())

        if numberOfLines == 0:
            self.mapGrid.CreateGridBlocks()
        else:
            self.mapGrid.blockGrid = self.LoadData()

class MapGrid():
    def __init__(self):
        #note that entities will also use functions and variables named for "blocks" as that refers to both entities and map building blocks 
        #all entities will be the same size in the map placement for ease
        #these entities will be scaled up to their correct size in the main game

        self.blockGrid = [] # will become [[]] as a 2D list for rows and columns
        self.blockObjectsInView = Setup.pg.sprite.Group() 

        self.blockWidth = Setup.setup.BLOCK_WIDTH 
        self.originalBlockWidth = self.blockWidth
        self.zoomFactor = 1
        self.changedZoom = True

        self.blockSheetHandler = BlockSheetExtractor()
        self.selectedBlock = 0 #between 0 and 48
        self.numberOfBlocks = Setup.setup.NUM_OF_UNIQUE_BLOCKS_INDEX # 49 blocks in total

        #placement options
        self.deleting = False
        self.rotation = 0

        #moving around map 
        self.mouseDownPos = 0
        self.mouseButtonDown = False
        self.movedX = 0
        self.movedY = 0
        self.movedXTotal = 0
        self.movedYTotal = 0
        self.changedLocationMovement = False

    def SaveMapData(self):
        mapDataHandler.SaveData(self.blockGrid)

    def CreateGridBlocks(self):
        blockRow = []

        for gridYPosition in range(0, Setup.setup.BLOCKS_WIDE):
            for gridXPosition in range(0, Setup.setup.BLOCKS_WIDE): 
                blockRow.append(Menus.BlockButton("BLOCK", self.blockWidth, self.blockWidth, gridXPosition * self.blockWidth, gridYPosition * self.blockWidth, self.selectedBlock, self.rotation, self.blockSheetHandler.GetCorrectBlockImage(self.selectedBlock, False, self.rotation, 1)))

            self.blockGrid.append(blockRow)
            blockRow = [] 

    def CalculateBlocksWithinRange(self):  
        self.blockObjectsInView.empty()

        for row in self.blockGrid:
            for block in row:
                if Setup.setup.screenRect.colliderect(block.rect):
                    self.blockObjectsInView.add(block)
                         
    def UpdateGridBlocks(self):
        mousePressed = Setup.pg.mouse.get_pressed()
        mousePosition = Setup.pg.mouse.get_pos()
        self.CalculateBlocksWithinRange()    
        
        deleteButtonHover = Menus.ButtonGroupMethods.GetButton("DELETE", Menus.menuManagement.mapButtonGroup.buttons).hover
        exitButtonHover = Menus.ButtonGroupMethods.GetButton("EXIT", Menus.menuManagement.mapButtonGroup.buttons).hover

        for block in self.blockObjectsInView:
            if block.CheckClick(mousePressed, mousePosition) != None and not (deleteButtonHover or exitButtonHover):
                if not Setup.setup.deletingBlocks: # placing        
                    if (block.blockNumber != self.selectedBlock or block.rotation != self.rotation):
                        block.blockNumber = self.selectedBlock
                        block.rotation = self.rotation
                        block.textList = []
                        block.image = self.blockSheetHandler.GetCorrectBlockImage(block.blockNumber, isHover=False, rotation=block.rotation, zoom=self.zoomFactor)
                else: # deleting
                    block.blockNumber = 0
                    block.rotation = 0
                    block.textList = []
                    block.image = self.blockSheetHandler.GetCorrectBlockImage(0, isHover=False, rotation=0, zoom=self.zoomFactor)

            if block.hover:
                block.image = self.blockSheetHandler.GetCorrectBlockImage(block.blockNumber, isHover=True, rotation=block.rotation, zoom=self.zoomFactor)
            else:
                block.image = self.blockSheetHandler.GetCorrectBlockImage(block.blockNumber, isHover=False, rotation=block.rotation, zoom=self.zoomFactor)

        self.blockObjectsInView.update() 
        self.blockObjectsInView.draw(Setup.setup.screen)

        for block in self.blockObjectsInView:
            self.PathFindingWaypoints(block)

        if self.mouseButtonDown:
            self.MoveAroundMap()

        self.ChangeSelectedBlock()
        self.ShowSelectedBlock()
        self.UpdateBlockSizes() 

    def UpdateBlockSizes(self):
        if self.changedZoom or self.changedLocationMovement:
            self.blockWidth = self.originalBlockWidth * self.zoomFactor

            for row in self.blockGrid:
                for block in row:
                    block.locationX = (self.movedX + block.originalLocationX) * self.zoomFactor
                    block.locationY = (self.movedY + block.originalLocationY) * self.zoomFactor

                    block.width = self.blockWidth
                    block.height = self.blockWidth 

                    block.image = self.blockSheetHandler.GetCorrectBlockImage(block.blockNumber, isHover=block.hover, rotation=block.rotation, zoom=self.zoomFactor)
                    block.rect = block.image.get_rect()
                    block.rect.center = (block.locationX, block.locationY) 

    def MoveAroundMap(self):
        self.changedLocationMovement = True

        currentMousePos = Setup.pg.mouse.get_pos()

        panSpeed = 1 + (1 - self.zoomFactor)
        self.movedX = self.movedXTotal + panSpeed * (currentMousePos[0] - self.mouseDownPos[0])
        self.movedY = self.movedYTotal + panSpeed * (currentMousePos[1] - self.mouseDownPos[1]) 

    def PathFindingWaypoints(self, block, existingText=""):
        if block.blockNumber == 48 and not block.DoesTextExist("PATHFINDING"): # path finding waypoint
            Setup.setup.textInputBoxes.append(Setup.InputBox(block, "PATHFINDING", 2, existingText))

        block.UpdateText()

    def ChangeSelectedBlock(self):
        if Setup.pg.mouse.get_pressed()[2]: # right click 
            if not self.mouseButtonDown:
                self.mouseButtonDown = True
                self.mouseDownPos = Setup.pg.mouse.get_pos()
        else:
            if self.mouseButtonDown:
                self.movedXTotal += self.movedX - self.movedXTotal 
                self.movedYTotal += self.movedY - self.movedYTotal 
                self.mouseButtonDown = False

        match Setup.setup.pressedKey:      
            case Setup.pg.K_RIGHT: 
                if self.selectedBlock == self.numberOfBlocks:
                    self.selectedBlock = 0
                else:
                    self.selectedBlock += 1

            case Setup.pg.K_LEFT:
                if self.selectedBlock == 0: 
                    self.selectedBlock = self.numberOfBlocks
                else:
                    self.selectedBlock -= 1

            case 4: # mouse wheel scrolling up
                if self.zoomFactor < 1.0: # 1.0x larger so no change from initital size
                    self.changedZoom = True
                    self.zoomFactor += 0.05

            case 5: # mouse wheel scrolling down
                if self.zoomFactor > 0.2: # majority of the map is visible
                    self.changedZoom = True
                    self.zoomFactor -= 0.05

            case Setup.pg.K_r:
                self.rotation -= 90 

    def ShowSelectedBlock(self): 
        blockDisplay = Setup.TextMethods.CreateText("BLOCK", "Selected block: ", Setup.setup.WHITE, 150, 50, 30)
        Setup.TextMethods.UpdateText([blockDisplay])

        Setup.setup.screen.blit(self.blockSheetHandler.GetCorrectBlockImage(self.selectedBlock, False, self.rotation), (50, 100))
         
mapDataHandler = MapDataHandling()