import Menus
import Setup
import Game
import MapCreator

def main():
    Setup.SoundHandler.PlaySound("MENU_MUSIC")

    while Setup.setup.run:
        Setup.setup.update()
        Setup.setup.events()

        match Setup.setup.gameState:
            case "MENU":        
                Menus.menuManagement.background.DrawFrame()
                Menus.menuManagement.MenuChildActions("MENU")
                
            case "MAP":
                MapCreator.mapDataHandler.mapGrid.UpdateGridBlocks()
                Menus.menuManagement.MenuChildActions("MENU")

            case "GAME":
                Game.gameHandler.background.DrawImage()
                Game.gameHandler.player.Update()
                Game.gameHandler.UpdateEnemies()
                Menus.menuManagement.MenuChildActions("GAME")
                
        Setup.pg.display.update()

    MapCreator.mapDataHandler.mapGrid.SaveMapData()

if __name__ == "__main__":
    main()
    Setup.pg.quit()
