import Menus
import Setup
import Game
import MapCreator

def main():
    while Setup.setup.run:
        Setup.setup.update()
        Setup.setup.events()

        match Setup.setup.gameState:
            case "MENU":        
                Menus.background.DrawFrame()
                Menus.menuManagement.MenuChildActions("MENU")
                
            case "MAP":
                MapCreator.mapGrid.UpdateGridBlocks()
                Menus.menuManagement.MenuChildActions("MENU")

            case "GAME":
                Game.gameBackground.DrawImage()
                Game.player.Update()
                Game.player.DrawFrame()
                Menus.menuManagement.MenuChildActions("GAME")
                

        Setup.pg.display.update()

    MapCreator.mapGrid.SaveMapData()

main()
Setup.pg.quit()
