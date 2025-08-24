import time
import Setup

Setup.pg.font.init()

class Button(Setup.pg.sprite.Sprite):
    def __init__(self, name, width, height, locationX, locationY, filePathImage, isSheetImage=False, sheetSurface=None, blockNumber=-1, rotation=0):
        Setup.pg.sprite.Sprite.__init__(self)

        self.name = name
        self.textList = []

        self.width = width
        self.height = height
        self.locationX = locationX
        self.locationY = locationY

        self.canHover = not isSheetImage

        if not isSheetImage: # normal buttons
            self.filePath = Setup.os.path.join("ASSETS", "BUTTON_IMAGES", filePathImage)
            self.image = Setup.pg.image.load(self.filePath + ".png").convert_alpha();
            self.image = Setup.pg.transform.scale(self.image, (self.width, self.height)) 
            self.isBlock = False
        else: # blocks and entities
            self.baseImage = sheetSurface
            self.image = sheetSurface         
            self.blockNumber = blockNumber
            self.rotation = rotation
            self.originalLocationX = self.locationX
            self.originalLocationY = self.locationY 
            self.imageType = "NORMAL" # either NORMAL or HOVER. Used to avoid changing image to the same image
            self.isBlock = True

        self.mask = Setup.pg.mask.from_surface(self.image) # mask allows for more accurate collision detection

        self.rect = self.image.get_rect()
        self.rect.center = (self.locationX, self.locationY)

        self.clicked = False
        self.hover = False

    def CheckClick(self):
        mousePosition = Setup.pg.mouse.get_pos()
        positionInMask = mousePosition[0] - self.rect.x, mousePosition[1] - self.rect.y
        
        if self.rect.collidepoint(mousePosition) and (self.mask.get_at(positionInMask) or self.isBlock): # if hovering
            if not self.hover:
                Setup.SoundHandler.PlaySound("BUTTON_HOVER")

            self.hover = True          

            if Setup.pg.mouse.get_pressed()[0] == 1 and not self.clicked: # [0] = left click
                self.clicked = True
                Setup.SoundHandler.PlaySound("BUTTON_CLICK")
                return self.name
        else:
            self.hover = False

        if Setup.pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        self.ChangeImageHover()

    def ChangeImage(self, fileNameEnd):
        if self.canHover:
            self.image = Setup.pg.image.load(self.filePath + fileNameEnd)
            self.image = Setup.pg.transform.scale(self.image, (self.width, self.height))

    def ChangeImageHover(self):
        if self.hover:
            self.ChangeImage("_HOVER.png") # change the image to corresponding hover image 
        else:
            self.ChangeImage(".png")

    def ChangeImageClick(self, fileName, sheetImage):
        if self.canHover:
            self.filePath = Setup.os.path.join("ASSETS", "BUTTON_IMAGES", fileName) # change the image to a completely different image
            self.ChangeImage(".png")
        else:
            self.image = sheetImage

    def CenterText(self):
        for text in self.textList:
            text.locationX = self.rect.center[0]
            text.locationY = self.rect.center[1]
            text.rect = text.surface.get_rect(center=(text.locationX, text.locationY))

    def ChangeText(self, name, newText):
        searchedText = Setup.TextMethods.GetText(name, self.textList)

        if searchedText != None:
            searchedText.SetText(newText)

    def CreateText(self, name, text):
        text = Setup.TextMethods.CreateText(name, text, Setup.setup.BLUE, 0, 0, 10)
        self.textList.append(text)

    def UpdateText(self):
        self.CenterText()
        Setup.TextMethods.UpdateText(self.textList)

    def DoesTextExist(self, name):
        searchedText = Setup.TextMethods.GetText(name, self.textList)

        if searchedText == None:
            return False

        return True
        
class SlidingButton(Button):
    def __init__(self, name, width, height, locationX, locationY, filePathImage, length, isSheetImage, sheetSurface):
        super().__init__(name, width, height, locationX, locationY, filePathImage, isSheetImage, sheetSurface) # calls the Button __init__ function
        self.length = length

    def CheckClick(self):
        super().CheckClick() # calls the Button function

        if self.clicked:
            self.Drag(Setup.pg.mouse.get_pos()) 
            return self.name

    def Drag(self, mousePosition):
        mousePositionX = mousePosition[0]

        if mousePositionX < self.locationX: # to the left of the boundaries
            self.rect.center = (self.locationX, self.locationY)

        elif mousePositionX > self.locationX + self.length: # to the right of the boundaries
            self.rect.center = (self.locationX + self.length, self.locationY)

        else:
            self.rect.center = (mousePositionX, self.locationY) # move slider to mouse X coordinate if within boundaries

    def GetRelativeLocation(self): # how far along the slider the button is
        return int(((self.rect.center[0] - self.locationX) / self.length) * 100) # between 0 and 100 (text display)

class Background():
    def __init__(self, filePathImage):
        self.filePath = Setup.os.path.join("ASSETS", "BACKGROUND", filePathImage)
        self.image = Setup.pg.image.load(self.filePath + ".png").convert_alpha()    

        self.width = 1920
        self.height = 1080
        self.totalWidth = 1920 * 12

        self.sheet = Setup.SpriteSheet(self.image, self, self.totalWidth)
        self.currentFrame = 0
        self.startTime = time.time()       
        
        self.BLACK = ()

    def DrawFrame(self):    
        self.sheet.Update()

        Setup.setup.screen.blit(self.sheet.GetImage(self.currentFrame, self.width, self.height, 1), (0, 0))

class CreateMainMenu(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()

    def CreateButtons(self):
        width, height = 320, 320
        xLocation, yLocation = Setup.setup.WIDTH // 2, 300
        spacing = 150
        playButton = ButtonGroupMethods.CreateButton("PLAY", width, height, xLocation, yLocation, "PLAY_BUTTON")
        settingsButton = ButtonGroupMethods.CreateButton("SETTINGS", width, height, xLocation, yLocation + spacing, "SETTINGS_BUTTON")
        mapButton = ButtonGroupMethods.CreateButton("MAP", width, height, xLocation, yLocation + (2 * spacing), "MAP_BUTTON")  
        quitButton = ButtonGroupMethods.CreateButton("QUIT", width, height, xLocation, yLocation + (3 * spacing), "QUIT_BUTTON")

        self.buttons.add(playButton)
        self.buttons.add(settingsButton)
        self.buttons.add(mapButton)
        self.buttons.add(quitButton) 

        menuManagement.AddMenu(self, "MENU") 

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "PLAY":
                self.PlayButton()
            case "SETTINGS":
                self.SettingsButton()
            case "QUIT":
                self.QuitGame()          
            case "MAP":
                self.MapEditor()

    def PlayButton(self):
        menuManagement.AddMenu(newGameButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "MENU") 

    def SettingsButton(self):
        menuManagement.AddMenu(settingsButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "MENU")

    def QuitGame(self):
        #save data
        Setup.setup.run = False

    def MapEditor(self):
        menuManagement.AddMenu(mapButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "MENU")

        Setup.setup.gameState = "MAP"

        
class CreateSettingsMenu(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()
        self.textList = [] # any text that must be drawn onto the screen (not images)

    def CreateButtons(self):      
        width, height = 320, 320
        xLocation, yLocation = 150, 1000
        exitButton = ButtonGroupMethods.CreateButton("EXIT", width, height, xLocation, yLocation, "QUIT_BUTTON")   
        
        xLocation, yLocation = Setup.setup.WIDTH // 2, 300
        toggleCrouchButton = ButtonGroupMethods.CreateButton("CROUCH", width, height, xLocation, yLocation, "CROUCH_BUTTON")

        width, height = 160, 160
        xLocation, yLocation = Setup.setup.WIDTH // 2 - 450, 500
        muteButton = ButtonGroupMethods.CreateButton("MUTE", width, height, xLocation, yLocation, "UNMUTE_BUTTON")

        xLocation = Setup.setup.WIDTH // 2 - 250
        soundControlSlider = ButtonGroupMethods.CreateSlidingButton("SOUND", width, height, xLocation, yLocation, "SOUND_BUTTON", 500)

        size = 75
        soundControlSliderText = Setup.TextMethods.CreateText("SOUND", "0", Setup.setup.BLACK, xLocation, yLocation, size)
        
        self.buttons.add(exitButton) 
        self.buttons.add(toggleCrouchButton)
        self.buttons.add(soundControlSlider)
        self.buttons.add(muteButton)

        self.textList.append(soundControlSliderText)

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)
        Setup.TextMethods.UpdateText(self.textList)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "EXIT":
                self.ExitButton()
            case "CROUCH":
                self.CrouchButton()
            case "SOUND":
                self.SoundButton()
            case "MUTE":
                self.MuteButton()

    def ExitButton(self):
        menuManagement.AddMenu(menuButtonGroup, "MENU") 
        menuManagement.RemoveMenu(self, "MENU")

    def CrouchButton(self):
        pass
        #Add functionality

    def SoundButton(self):
        soundControlSlider = ButtonGroupMethods.GetButton("SOUND", self.buttons)
        soundControlSliderText = Setup.TextMethods.GetText("SOUND", self.textList)
        muteButton = ButtonGroupMethods.GetButton("MUTE", self.buttons)

        volume = soundControlSlider.GetRelativeLocation()

        soundControlSliderText.locationX = soundControlSlider.rect.center[0]
        soundControlSliderText.locationY = soundControlSlider.rect.center[1]

        soundControlSliderText.SetText(f"{volume}")

        if volume == 0:
            muteButton.ChangeImageClick("UNMUTE_BUTTON", None)
        else:
            muteButton.ChangeImageClick("MUTE_BUTTON", None)
        
        Setup.SoundHandler.ChangeVolume(volume)

    def MuteButton(self):
        soundControlSlider = ButtonGroupMethods.GetButton("SOUND", self.buttons)
        muteButton = ButtonGroupMethods.GetButton("MUTE", self.buttons)

        volume = soundControlSlider.GetRelativeLocation()

        if Setup.SoundHandler.GetVolume() == 0: #unmute
            if volume != 0:
                muteButton.ChangeImageClick("MUTE_BUTTON", None)

            Setup.SoundHandler.ChangeVolume(volume)
                
        else: # mute
            Setup.SoundHandler.ChangeVolume(0)
            muteButton.ChangeImageClick("UNMUTE_BUTTON", None) 

class CreateNewGameMenu(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()

    def CreateButtons(self):       
        width, height = 320, 320
        xLocation, yLocation = 600, Setup.setup.HEIGHT // 2
        spacing = 400
        newGame1Button = ButtonGroupMethods.CreateButton("NEWGAME1", width, height, xLocation, yLocation, "NEW_GAME_BUTTON")       
        newGame2Button = ButtonGroupMethods.CreateButton("NEWGAME2", width, height, xLocation + spacing, yLocation, "NEW_GAME_BUTTON")
        newGame3Button = ButtonGroupMethods.CreateButton("NEWGAME3", width, height, xLocation + (2 * spacing), yLocation, "NEW_GAME_BUTTON")

        xLocation, yLocation = 150, 1000
        exitButton = ButtonGroupMethods.CreateButton("EXIT", width, height, xLocation, yLocation, "QUIT_BUTTON") 
        
        self.buttons.add(newGame1Button) 
        self.buttons.add(newGame2Button)
        self.buttons.add(newGame3Button)
        self.buttons.add(exitButton)

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "NEWGAME1":
                self.NewGame1Button()
            case "NEWGAME2":
                self.NewGame2Button()
            case "NEWGAME3":
                self.NewGame3Button()
            case "EXIT":
                self.ExitButton()

    def newGameHandler(self):
        Setup.setup.gameState = "GAME"
        menuManagement.AddMenu(inGameButtonGroup, "GAME")
        menuManagement.RemoveMenu(self, "MENU")
        Setup.pg.mouse.set_visible(False)

    def NewGame1Button(self):
        # create new save file, and change button to a save slot (new button object)
        self.newGameHandler()

    def NewGame2Button(self):
        self.newGameHandler()
    
    def NewGame3Button(self):
        self.newGameHandler()

    def ExitButton(self):
        menuManagement.AddMenu(menuButtonGroup, "MENU") 
        menuManagement.RemoveMenu(self, "MENU")

class CreateMapMenu(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()

    def CreateButtons(self):       
        width, height = 320, 320
        xLocation, yLocation = 150, 1000
        exitButton = ButtonGroupMethods.CreateButton("EXIT", width, height, xLocation, yLocation, "QUIT_BUTTON") 
        
        width, height = 160, 160
        xLocation, yLocation = 1750, 1000
        deleteButton = ButtonGroupMethods.CreateButton("DELETE", width, height, xLocation, yLocation, "DELETE_OFF_BUTTON")       
         
        self.buttons.add(exitButton)
        self.buttons.add(deleteButton) 

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "EXIT":
                self.ExitButton()
            case "DELETE":
                self.DeleteButton()

    def ExitButton(self):
        menuManagement.AddMenu(menuButtonGroup, "MENU") 
        menuManagement.RemoveMenu(self, "MENU")      

        Setup.setup.gameState = "MENU"

    def DeleteButton(self):
        deleteButton = ButtonGroupMethods.GetButton("DELETE", self.buttons)

        if Setup.setup.deletingBlocks:
            Setup.setup.deletingBlocks = False
            deleteButton.ChangeImageClick("DELETE_OFF_BUTTON", None)
        else:
            Setup.setup.deletingBlocks = True
            deleteButton.ChangeImageClick("DELETE_ON_BUTTON", None)

class CreateInGameMenu(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()

    def CreateButtons(self):       
        width, height = 160, 160
        xLocation, yLocation = 80, 200
        spacing = height - 5
        inventoryButton = ButtonGroupMethods.CreateButton("INVENTORY", width, height, xLocation, yLocation, "INVENTORY_BUTTON") 
        saveButton = ButtonGroupMethods.CreateButton("SAVE", width, height, 80, yLocation + spacing, "SAVE_BUTTON") # -5 to overlap images slightly
        exitButton = ButtonGroupMethods.CreateButton("EXIT", width, height, 80, yLocation + (2 * spacing), "RETURN_MENU_BUTTON") 
        
        self.buttons.add(inventoryButton)
        self.buttons.add(saveButton) 
        self.buttons.add(exitButton)

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "INVENTORY":
                self.InventoryButton()
            case "SAVE":
                self.SaveButton()
            case "EXIT":
                self.ExitButton()

        if Setup.setup.pressedKey == Setup.pg.K_TAB: # opening in-game menu using tab
            if len(self.buttons) == 0:
                Setup.pg.mouse.set_visible(True)
                self.CreateButtons()
            else:
                Setup.pg.mouse.set_visible(False)
                self.buttons.empty()

    def InventoryButton(self):
        pass

    def SaveButton(self):
        pass

    def ExitButton(self):
        Setup.setup.gameState = "MENU"
        menuManagement.AddMenu(menuButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "GAME")
        self.buttons.empty()

class ButtonGroupMethods():
    @staticmethod
    def CreateButton(name, width, height, locationX, locationY, filePathImage, isSheetImage=False, sheetSurface=None):
        return Button(name, width, height, locationX, locationY, filePathImage, isSheetImage, sheetSurface)

    @staticmethod
    def CreateSlidingButton(name, width, height, locationX, locationY, filePathImage, length, isSheetSurface=False, sheetSurface=None):
        return SlidingButton(name, width, height, locationX, locationY, filePathImage, length, isSheetSurface, sheetSurface) 

    @staticmethod
    def UpdateChildButton(buttonList):
        buttonList.update()
        buttonList.draw(Setup.setup.screen)

    @staticmethod
    def CheckClicks(buttons):
        for button in buttons:  
            returnedValue = button.CheckClick() # get the name of clicked button e.g. QUIT

            if (returnedValue != None):
                return returnedValue

    def GetButton(name, buttons):
        for button in buttons:
            if button.name == name:
                return button

class MenuManagement(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.menuMenus = Setup.pg.sprite.Group()
        self.gameMenus = Setup.pg.sprite.Group()
        self.menus = {"MENU" : self.menuMenus, "GAME" : self.gameMenus}

    def RemoveMenu(self, menu, keyword):
        self.menus[keyword].remove(menu)

    def AddMenu(self, menu, keyword):
        self.menus[keyword].add(menu)

    def MenuChildActions(self, keyword):
        for menu in self.menus[keyword]:
            menu.ChildActions()

menuManagement = MenuManagement()

menuButtonGroup = CreateMainMenu() #create all menus and buttons, add / remove menus from MenuManagement to display / hide
menuButtonGroup.CreateButtons()

settingsButtonGroup = CreateSettingsMenu()
settingsButtonGroup.CreateButtons()

mapButtonGroup = CreateMapMenu()
mapButtonGroup.CreateButtons()

newGameButtonGroup = CreateNewGameMenu()
newGameButtonGroup.CreateButtons()

inGameButtonGroup = CreateInGameMenu()

background = Background("BACKGROUND_SHEET_FULL")

Setup.SoundHandler.PlaySound("MENU_MUSIC")