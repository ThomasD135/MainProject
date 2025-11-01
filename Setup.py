import os
from pickle import FRAME
import time
import pygame as pg
import sys
import math
import random
import json

pg.mixer.init()
pg.font.init()

class Setup:
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
        self.BLOCK_WIDTH = self.WIDTH // 12
        self.BLOCKS_WIDE = 48
        self.NUM_OF_UNIQUE_BLOCKS_INDEX = 48

        self.GRAVITY = 1

        self.volume = 0

        self.pressedKey = None
        self.textInputBoxes = []
        textSize = 30
        self.fpsText = TextMethods.CreateText("FPS", "0", self.WHITE, self.WIDTH - textSize, textSize // 2, textSize)

        #map attributes
        self.gameState = "MENU"
        self.deletingBlocks = False

        #game settings
        self.gainHealthFromBosses = True
        self.changeSlot = (False, -1) # (shouldChange, newSlot)
        self.saveGame = False
        self.currentSaveSlot = -1 

    def events(self):
        for event in pg.event.get():
            for box in self.textInputBoxes:
                box.UserInteraction(event)

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

    def displayFrameRate(self):
        fps = self.clock.get_fps()
        self.fpsText.SetText(f"{round(fps, 1)}")
        TextMethods.UpdateText([self.fpsText])

    def loadImage(self, imagePath, width=160, height=160):
        image = pg.image.load(imagePath + ".png").convert_alpha()
        image = pg.transform.scale(image, (width, height))
        return image

class InputBox:
    def __init__(self, parent, name, maxLength, existingText=""):
        self.parent = parent
        self.name = name
        self.maxLength = maxLength # number of characters
        self.active = False # can enter text
        self.text = existingText

        self.parent.CreateText(self.name, self.text)

    def UserInteraction(self, event):
        self.rect = self.parent.rect

        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.parent.ChangeText(self.name, self.text)
            else:
                self.active = False

        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN:
                self.text = ""
                self.active = False
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
                self.parent.ChangeText(self.name, self.text)
            else:
                if len(self.text) < self.maxLength:
                    if (event.unicode).isnumeric():
                        self.text += event.unicode
                        self.parent.ChangeText(self.name, self.text)

class FontHandler:
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

class SpriteSheet:
    def __init__(self, imagePath, sheetObject, totalWidth, width, height, scale):
        self.sheet = pg.image.load(imagePath + ".png").convert_alpha()
        self.sheetObject = sheetObject
        self.totalWidth = totalWidth
        self.interval = 70 / 1000 # each frame is displayed for 70 milliseconds (applies to all animations)

        self.width = width
        self.height = height
        self.scale = scale

        self.frames = [] # load all images once
        self.flippedFrames = []
        self.totalFrames = int(totalWidth / width)

        for x in range(self.totalFrames):
            frameImage = pg.Surface((width, height), pg.SRCALPHA)
            frameImage.blit(self.sheet, (0, 0), (x * width, 0, width, height))
            
            if scale != 1:
                frameImage = pg.transform.scale(FRAME, (width * scale, height * scale))
            
            self.frames.append(frameImage)
            self.flippedFrames.append(pg.transform.flip(frameImage, True, False))

    def Update(self):
        sheet = self.sheetObject # the sprite sheet of the corresponding object e.g. player, background
        currentTime = time.time() # start a timer 

        if currentTime - sheet.startTime > self.interval: 
            sheet.currentFrame = (sheet.currentFrame + 1) % self.totalFrames
            sheet.startTime = currentTime # start a new timer. startTime is controlled within corresponding object e.g. player, background

    def GetImage(self, flipped=False):#, width, height, scale):
        if flipped:
            return self.flippedFrames[self.sheetObject.currentFrame]
        return self.frames[self.sheetObject.currentFrame]

class SoundHandler:
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

class TextMethods:
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