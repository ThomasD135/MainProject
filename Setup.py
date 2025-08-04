import os
import time
import pygame as pg

pg.mixer.init()
pg.font.init()

class Setup():
    def __init__(self):
        self.FPS = 60 
        self.run = True
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.screenRect = self.screen.get_rect()
        self.clock = pg.time.Clock()

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREY = (50, 50, 50)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

        self.WIDTH = self.screen.get_size()[0]
        self.HEIGHT = self.screen.get_size()[1]
        self.BLOCK_WIDTH = 160
        self.BLOCKS_WIDE = 48
        self.NUM_OF_UNIQUE_BLOCKS_INDEX = 48

        self.GRAVITY = 1

        self.volume = 0

        self.pressedKey = None

        #map attributes
        self.gameState = "MENU"
        self.deletingBlocks = False

        #game settings
        self.gainHealthFromBosses = True

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: # closes if the user clicks the X button on the pygame window
                self.run = False
                return True # return true to only press once - important for rotation and changing selected block

            if event.type == pg.KEYDOWN:
                self.pressedKey = event.key
                return True

            if event.type == pg.MOUSEBUTTONDOWN:
                self.pressedKey = event.button
                return True

        self.pressedKey = None

    def update(self):
        self.screen.fill(self.BLACK) # make the screen completely black to hide previous frame
        self.clock.tick(self.FPS)

    def loadImage(self, imagePath, width=160, height=160):
        image = pg.image.load(imagePath + ".png").convert_alpha()
        image = pg.transform.scale(image, (width, height))
        return image


class FontHandler():
    def __init__(self, name, text, colour, locationX, locationY, size):
        self.name = name
        self.text = text
        self.colour = colour
        self.locationX = locationX
        self.locationY = locationY
        self.size = size

        self.font = pg.font.SysFont('Comic Sans MS', size)
        self.surface = self.font.render(text, True, colour)
        self.rect = self.surface.get_rect(center=(locationX, locationY))

    def Draw(self):     
        setup.screen.blit(self.surface, self.rect) # draw given text on the screen

    def SetText(self, newText):
        if newText != self.text:
            self.text = newText
            self.surface = self.font.render(self.text, True, self.colour)
            self.rect = self.surface.get_rect(center=(self.locationX, self.locationY))

class SpriteSheet():
    def __init__(self, image, sheetObject, totalWidth):
        self.sheet = image
        self.sheetObject = sheetObject
        self.totalWidth = totalWidth
        self.interval = 75 / 1000 # each frame is displayed for 75 milliseconds (applies to all animations)

    def Update(self):
        sheet = self.sheetObject # the sprite sheet of the corresponding object e.g. player, background

        currentTime = time.time() # start a timer 
        interval = currentTime - sheet.startTime # calculate how long the frame has been display for (milliseconds)

        if interval > self.interval: 
            sheet.currentFrame += 1
            sheet.startTime = time.time() # start a new timer. startTime is controlled within corresponding object e.g. player, background

        if sheet.currentFrame == (self.totalWidth / sheet.width): # reset sprite sheet to the first image if at the end of the sheet
            sheet.currentFrame = 0

    def GetImage(self, frame, width, height, scale):
        image = pg.Surface((width, height), pg.SRCALPHA)
        image.blit(self.sheet, (0,0), ((frame * width), 0, width, height)) # select specific region of the sprite sheet depending on the frame
        image = pg.transform.scale(image, (width * scale, height * scale))

        return image

class SoundHandler():
    @staticmethod
    def FindChannel(sound):
        channel = 0
        channelDictionary = {"MUSIC" : 0, "BUTTON" : 1} # different sound effects play on different channels

        for key in channelDictionary:
            if key in sound:
                channel = channelDictionary[key] # find the channel that the sound should be played in

        return channel

    @staticmethod
    def PlaySound(sound):
        filePath = sound + ".mp3"

        channel = SoundHandler.FindChannel(sound)

        pg.mixer.Channel(channel).play(pg.mixer.Sound(os.path.join("ASSETS", "SOUND", filePath)))
        pg.mixer.Channel(channel).set_volume(setup.volume) # set initial volume to 0

    @staticmethod
    def EndSound(sound):
        channel = SoundHandler.FindChannel(sound)

        pg.mixer.Channel(channel).stop()

    @staticmethod
    def PauseSound(sound):
        channel = SoundHandler.FindChannel(sound)

        pg.mixer.Channel(channel).pause()

    @staticmethod
    def ChangeVolume(volume):
        setup.volume = volume / 100 

        for x in range(0, 1):
            pg.mixer.Channel(x).set_volume(setup.volume) # between 0 and 1. Only changes sounds that are currently playing

    @staticmethod
    def GetVolume():
        return pg.mixer.Channel(0).get_volume()

class TextMethods():
    @staticmethod
    def CreateText(name, text, colour, locationX, locationY, size):
        return FontHandler(name, text, colour, locationX, locationY, size)

    @staticmethod
    def UpdateText(textList):
        for text in textList:
            text.Draw()

    @staticmethod
    def GetText(name, textList):
        for text in textList: 
            if name == text.name:
                return text # find text object with given name

setup = Setup()