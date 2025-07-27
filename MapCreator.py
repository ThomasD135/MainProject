import Setup
import Menus

#NOTE TO SELF (DELETE LATER) 
#THE CURRENT BLOCK GRID IS MADE OF BUTTONS, THIS IS NOT CORRECT FOR THE PLAYABLE GAME
#IN THE MAIN GAME, MAKE A NEW GRID AND MAKE A NEW BLOCK CLASS TO STORE ALL APPROPRIATE DETALS
#ALSO, CREATE ENTITIES IN THEIR CORRECT SIZES IN THE MAIN GAME, PLACEMENT WILL HAVE ALL IMAGES BE THE SAME SIZES

class BlockSheetExtractor():
    def __init__(self):
        self.filePath = Setup.os.path.join("ASSETS", "BLOCK_SHEET", "ALL_BLOCK_SHEET_IMAGE")

        self.sheet = Setup.pg.image.load(self.filePath + ".png").convert_alpha()
        self.sheetHover = Setup.pg.image.load(self.filePath + "_HOVER.png").convert_alpha()

    def GetCorrectBlockImage(self, blockPos, originalWidth, originalHeight, currentWidth, currentHeight, isHover, rotation):
        image = Setup.pg.Surface((originalWidth, originalHeight), Setup.pg.SRCALPHA)

        if not isHover:
            image.blit(self.sheet, (0,0), ((blockPos * originalWidth), 0, originalWidth, originalHeight))
        else:
            image.blit(self.sheetHover, (0, 0), ((blockPos * originalWidth), 0, originalWidth, originalHeight))

        image = Setup.pg.transform.scale(image, (currentWidth, currentHeight))

        if blockPos <= 16: # only normal blocks can be rotated (lantern onwards cannot be rotated)
            image = Setup.pg.transform.rotate(image, rotation)
           
        return image

class MapDataHandling():
    def __init__(self):
        self.filePath = Setup.os.path.join("ASSETS", "MAP", "MAP_DATA_FILE")

    def SaveData(self, blockGrid):
        file = open(self.filePath + ".txt", "w")

        dataLine = ""

        for row in blockGrid:
            for block in row:
                if block.blockNumber >= 10:
                    dataLine += str(block.blockNumber) 
                else:
                    dataLine += "0" + str(block.blockNumber)

                if block.rotation < -360:
                    block.rotation %= -360

                dataLine += str(block.rotation // -90) # 0 for no rotation, 1 for a 90 degree rotation. Keeps data stored as a single number. Using -90 to avoid storing a negative sign (fixed in data loading)
                dataLine += " "

            dataLine += "\n" 
        
        file.write(dataLine) 

        file.close()

    def LoadData(self):
        file = open(self.filePath + ".txt")

        blockWidth = 160

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

                row.append(Menus.Button("BLOCK", blockWidth, blockWidth, XPosition * blockWidth - (0.5 * blockWidth), YPosition * blockWidth - (0.5 * blockWidth), "", True, mapGrid.blockSheetHandler.GetCorrectBlockImage(blockNumber, blockWidth, blockWidth, blockWidth, blockWidth, False, rotation), blockNumber, rotation))

            grid.append(row)
            row = []

        file.close()

        return grid

    def LoadDataOrCreateMap(self):
        file = open(self.filePath + ".txt", "r")

        numberOfLines = len(file.readlines())

        if numberOfLines == 0:
            mapGrid.CreateGridBlocks()
        else:
            mapGrid.blockGrid = self.LoadData()

class MapGrid():
    def __init__(self):
        #note that entities will also use functions and variables named for "blocks" as that refers to both entities and map building blocks 
        #all entities will be the same size in the map placement for ease
        #these entities will be scaled up to their correct size in the main game

        self.blockGrid = [] # will become [[]] as a 2D list for rows and columns
        self.blockObjectsInView = Setup.pg.sprite.Group() 

        self.blockWidth = 160 
        self.originalBlockWidth = self.blockWidth
        self.zoomFactor = 1
        self.changedZoom = True

        self.blockSheetHandler = BlockSheetExtractor()
        self.selectedBlock = 0 # between 0 and 47
        self.numberOfBlocks = 47 # 49 blocks in total

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

        for gridYPosition in range(0, 48): 
            for gridXPosition in range(0, 48): 
                blockRow.append(Menus.Button("BLOCK", self.blockWidth, self.blockWidth, gridXPosition * self.blockWidth - (0.5 * self.blockWidth), gridYPosition * self.blockWidth - (0.5 * self.blockWidth), "", True, self.blockSheetHandler.GetCorrectBlockImage(self.selectedBlock, self.blockWidth, self.blockWidth, self.blockWidth, self.blockWidth, False, self.rotation), self.selectedBlock, self.rotation))

            self.blockGrid.append(blockRow)
            blockRow = [] 

    def CalculateBlocksWithinRange(self):  
        if self.changedZoom or self.changedLocationMovement:
            self.changedLocationMovement = False

            self.blockObjectsInView.empty()

            userXCordCenter = Setup.setup.WIDTH // 2
            userYCordCenter = Setup.setup.HEIGHT // 2
             
            for row in self.blockGrid:
                for block in row:   
                    if abs(block.locationX - userXCordCenter) < (Setup.setup.WIDTH // 2) + self.blockWidth and abs(block.locationY - userYCordCenter) < (Setup.setup.HEIGHT // 2) + self.blockWidth:
                        self.blockObjectsInView.add(block)  
                         
    def UpdateGridBlocks(self):
        self.CalculateBlocksWithinRange()       

        for block in self.blockObjectsInView:
            if block.CheckClick() != None and not Menus.ButtonGroupMethods.GetButton("DELETE", Menus.mapButtonGroup.buttons).hover:
                if not Setup.setup.deletingBlocks:
                    block.ChangeImageClick("", self.blockSheetHandler.GetCorrectBlockImage(self.selectedBlock, self.originalBlockWidth, self.originalBlockWidth, block.width, block.height, False, self.rotation))
                    block.blockNumber = self.selectedBlock
                    block.rotation = self.rotation
                else:
                    block.ChangeImageClick("", self.blockSheetHandler.GetCorrectBlockImage(0, self.originalBlockWidth, self.originalBlockWidth, block.width, block.height, False, 0))        
                    block.blockNumber = 0
                    block.rotation = 0

            if block.hover and block.imageType == "NORMAL":
                block.ChangeImageClick("", self.blockSheetHandler.GetCorrectBlockImage(block.blockNumber, self.originalBlockWidth, self.originalBlockWidth, block.width, block.height, True, block.rotation))
                block.imageType = "HOVER"

        for row in self.blockGrid:
            for block in row:
                if not block.hover and (block.imageType == "HOVER" or self.changedZoom):  
                    block.ChangeImageClick("", self.blockSheetHandler.GetCorrectBlockImage(block.blockNumber, self.originalBlockWidth, self.originalBlockWidth, block.width, block.height, False, block.rotation))
                    block.imageType = "NORMAL"

        self.changedZoom = False

        self.blockObjectsInView.update() 
        self.blockObjectsInView.draw(Setup.setup.screen)

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

                    block.image = Setup.pg.transform.scale(block.image, (block.width, block.height)) 
                    block.rect = block.image.get_rect()
                    block.rect.center = (block.locationX, block.locationY) 

    def MoveAroundMap(self):
        self.changedLocationMovement = True

        currentMousePos = Setup.pg.mouse.get_pos()

        self.movedX = self.movedXTotal + (currentMousePos[0] - self.mouseDownPos[0])
        self.movedY = self.movedYTotal + (currentMousePos[1] - self.mouseDownPos[1]) 

    def ChangeSelectedBlock(self):
        if Setup.pg.mouse.get_pressed()[2]: #right click 
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
                if self.zoomFactor > 0.25: # 4x smaller 
                    self.changedZoom = True
                    self.zoomFactor -= 0.05

            case Setup.pg.K_r:
                self.rotation -= 90 

    def ShowSelectedBlock(self): 
        blockDisplay = Setup.TextMethods.CreateText("BLOCK", "Selected block: ", Setup.setup.WHITE, 150, 50, 30)
        Setup.TextMethods.UpdateText([blockDisplay])

        Setup.setup.screen.blit(self.blockSheetHandler.GetCorrectBlockImage(self.selectedBlock, self.originalBlockWidth, self.originalBlockWidth, self.originalBlockWidth, self.originalBlockWidth, False, self.rotation), (50, 100))
         
mapGrid = MapGrid() 
mapDataHandler = MapDataHandling()

mapDataHandler.LoadDataOrCreateMap()