import time
import Setup

Setup.pg.font.init()

class Button(Setup.pg.sprite.Sprite):
    def __init__(self, name, width, height, locationX, locationY, filePathImage):
        Setup.pg.sprite.Sprite.__init__(self)

        self.isBlock = False
        self.name = name
        self.textList = []

        self.width = width
        self.height = height
        self.locationX = locationX
        self.locationY = locationY
   
        self.filePath = Setup.os.path.join("ASSETS", "BUTTON_IMAGES", filePathImage)
        self.image = Setup.pg.image.load(self.filePath + ".png").convert_alpha();
        self.image = Setup.pg.transform.scale(self.image, (self.width, self.height)) 
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

        if not self.isBlock:
            self.ChangeImageHover()

    def ChangeImage(self, fileNameEnd):
        self.image = Setup.pg.image.load(self.filePath + fileNameEnd)
        self.image = Setup.pg.transform.scale(self.image, (self.width, self.height))

    def ChangeImageHover(self):
        if self.hover:
            self.ChangeImage("_HOVER.png") # change the image to corresponding hover image 
        else:
            self.ChangeImage(".png")

    def ChangeImageClick(self, fileName):
        self.filePath = Setup.os.path.join("ASSETS", "BUTTON_IMAGES", fileName) # change the image to a completely different image
        self.ChangeImage(".png")          

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

class BlockButton(Button):
    def __init__(self, name, width, height, locationX, locationY, blockNumber, rotation, sheetSurface):
        Setup.pg.sprite.Sprite.__init__(self)

        self.isBlock = True
        self.name = name
        self.textList = []

        self.width = width
        self.height = height
        self.originalLocationX = locationX
        self.originalLocationY = locationY 

        self.baseImage = sheetSurface
        self.image = sheetSurface         
        self.blockNumber = blockNumber
        self.rotation = rotation      
        self.imageType = "NORMAL" # either NORMAL or HOVER. Used to avoid changing image to the same image

        self.mask = Setup.pg.mask.from_surface(self.image) # mask allows for more accurate collision detection

        self.rect = self.image.get_rect()
        self.rect.center = (self.originalLocationX, self.originalLocationY)

        self.clicked = False
        self.hover = False

    def ChangeImageClick(self, sheetImage):
        self.image = sheetImage
        
class SlidingButton(Button):
    def __init__(self, name, width, height, locationX, locationY, filePathImage, length):
        super().__init__(name, width, height, locationX, locationY, filePathImage) 
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
        menuManagement.AddMenu(menuManagement.newGameButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "MENU") 

    def SettingsButton(self):
        menuManagement.AddMenu(menuManagement.settingsButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "MENU")

    def QuitGame(self):
        #save data
        Setup.setup.run = False

    def MapEditor(self):
        menuManagement.AddMenu(menuManagement.mapButtonGroup, "MENU")
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
        menuManagement.AddMenu(menuManagement.menuButtonGroup, "MENU") 
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
            muteButton.ChangeImageClick("UNMUTE_BUTTON")
        else:
            muteButton.ChangeImageClick("MUTE_BUTTON")
        
        Setup.SoundHandler.ChangeVolume(volume)

    def MuteButton(self):
        soundControlSlider = ButtonGroupMethods.GetButton("SOUND", self.buttons)
        muteButton = ButtonGroupMethods.GetButton("MUTE", self.buttons)

        volume = soundControlSlider.GetRelativeLocation()

        if Setup.SoundHandler.GetVolume() == 0: #unmute
            if volume != 0:
                muteButton.ChangeImageClick("MUTE_BUTTON")

            Setup.SoundHandler.ChangeVolume(volume)
                
        else: # mute
            Setup.SoundHandler.ChangeVolume(0)
            muteButton.ChangeImageClick("UNMUTE_BUTTON") 

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

    def newGameHandler(self, saveSlot):
        Setup.setup.SAVE_SLOT = saveSlot
        menuManagement.AddMenu(menuManagement.newGameSettingsButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "MENU")

    def NewGame1Button(self):
        self.newGameHandler(1)

    def NewGame2Button(self):
        self.newGameHandler(2)
    
    def NewGame3Button(self):
        self.newGameHandler(3)

    def ExitButton(self):
        menuManagement.AddMenu(menuManagement.menuButtonGroup, "MENU") 
        menuManagement.RemoveMenu(self, "MENU")

class NewGameSettings(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()

    def CreateButtons(self):
        width, height = 320, 320
        xLocation, yLocation = Setup.setup.WIDTH // 2, 300
        spacing = 400

        gainHealthFromBossesButton = ButtonGroupMethods.CreateButton("GAIN_HEALTH", width, height, xLocation, yLocation, "BONUS_HEALTH_BUTTON")
        confirmSettingsButton = ButtonGroupMethods.CreateButton("CONFIRM", width, height, xLocation, yLocation + spacing, "CONFIRM_BUTTON")

        xLocation, yLocation = 150, 1000
        exitButton = ButtonGroupMethods.CreateButton("EXIT", width, height, xLocation, yLocation, "QUIT_BUTTON")

        self.buttons.add(gainHealthFromBossesButton)
        self.buttons.add(confirmSettingsButton)
        self.buttons.add(exitButton)

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "GAIN_HEALTH":
                self.GainHealthFromBossesButton()
            case "CONFIRM":
                self.ConfirmSettingsButton()
            case "EXIT":
                self.ExitButton()

    def GainHealthFromBossesButton(self):
        # change settings in correct save file - can only be changed here once and never again (for this save file)
        # if settings = OFF, change image etc
        pass

    def ConfirmSettingsButton(self):
        Setup.setup.gameState = "GAME"
        menuManagement.RemoveMenu(self, "MENU")
        Setup.pg.mouse.set_visible(False)

    def ExitButton(self):
        menuManagement.AddMenu(menuManagement.menuButtonGroup, "MENU") 
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
        menuManagement.AddMenu(menuManagement.menuButtonGroup, "MENU") 
        menuManagement.RemoveMenu(self, "MENU")      

        Setup.setup.gameState = "MENU"

    def DeleteButton(self):
        deleteButton = ButtonGroupMethods.GetButton("DELETE", self.buttons)

        if Setup.setup.deletingBlocks:
            Setup.setup.deletingBlocks = False
            deleteButton.ChangeImageClick("DELETE_OFF_BUTTON")
        else:
            Setup.setup.deletingBlocks = True
            deleteButton.ChangeImageClick("DELETE_ON_BUTTON")

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

    def InventoryButton(self):
        menuManagement.AddMenu(menuManagement.inventoryButtonGroup, "GAME")
        menuManagement.RemoveMenu(self, "GAME")

    def SaveButton(self):
        pass

    def ExitButton(self):
        Setup.setup.gameState = "MENU"
        menuManagement.AddMenu(menuManagement.menuButtonGroup, "MENU")
        menuManagement.RemoveMenu(self, "GAME")

class CreateInventoryMenu(Setup.pg.sprite.Sprite):
    def __init__(self):
        Setup.pg.sprite.Sprite.__init__(self)

        self.buttons = Setup.pg.sprite.Group()

    def CreateButtons(self):       
        width, height = 160, 160
        xLocation, yLocation = 800, 200
        inventoryButton = ButtonGroupMethods.CreateButton("INVENTORY", width, height, xLocation, yLocation, "INVENTORY_BUTTON") 
        
        self.buttons.add(inventoryButton)

    def ChildActions(self):
        ButtonGroupMethods.UpdateChildButton(self.buttons)

        clicked = ButtonGroupMethods.CheckClicks(self.buttons)

        match clicked:
            case "INVENTORY":
                pass

class ButtonGroupMethods():
    @staticmethod
    def CreateButton(name, width, height, locationX, locationY, filePathImage):
        return Button(name, width, height, locationX, locationY, filePathImage)

    @staticmethod
    def CreateSlidingButton(name, width, height, locationX, locationY, filePathImage, length):
        return SlidingButton(name, width, height, locationX, locationY, filePathImage, length) 

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

        self.menuButtonGroup = CreateMainMenu() #create all menus and buttons, add / remove menus from MenuManagement to display / hide
        self.menuButtonGroup.CreateButtons()
        self.AddMenu(self.menuButtonGroup, "MENU")

        self.settingsButtonGroup = CreateSettingsMenu()
        self.settingsButtonGroup.CreateButtons()

        self.mapButtonGroup = CreateMapMenu()
        self.mapButtonGroup.CreateButtons()

        self.newGameButtonGroup = CreateNewGameMenu()
        self.newGameButtonGroup.CreateButtons()

        self.newGameSettingsButtonGroup = NewGameSettings()
        self.newGameSettingsButtonGroup.CreateButtons()

        self.inGameMenuButtonGroup = CreateInGameMenu()
        self.inGameMenuButtonGroup.CreateButtons()

        self.inventoryButtonGroup = CreateInventoryMenu()
        self.inventoryButtonGroup.CreateButtons()

        self.background = Background("BACKGROUND_SHEET_FULL")

    def RemoveMenu(self, menu, keyword):
        self.menus[keyword].remove(menu)

    def AddMenu(self, menu, keyword):
        self.menus[keyword].add(menu)

    def ChangeStateOfMenu(self, menu, keyword, cursor=False):
        if menu not in self.menus[keyword]:
            self.AddMenu(menu, keyword)
            if cursor:
                Setup.pg.mouse.set_visible(True)
        else:
            self.RemoveMenu(menu, keyword)
            if cursor:
                Setup.pg.mouse.set_visible(False)

    def MenuChildActions(self, keyword):
        for menu in self.menus[keyword]:
            menu.ChildActions()

menuManagement = MenuManagement()