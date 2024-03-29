from Grid_Classes import search

from Simulations.MapPathGUI import MapPathGUI
from Simulation_Helpers.RandomObjects import RandomObjects
import Grid_Classes.grid as grid
from Simulations.GUI import *
from Constants.Consts import *
from Simulation_Helpers.GenerateSensorData import GenerateSensorData


class SmoothedPathGUI(GUI):
    def __init__(self, master, inputMap, path, squareList):
        super().__init__(master, inputMap, None, path, squareList, len(path) - 1)
        self.create_widgets(False)
        self.generate_sensor = GenerateSensorData(self.gridFull)

    def runSimulation(self, smoothPath):
        """Runs a sumulation of this map, with its enviroment and path
        """
        if smoothPath:
            self.drawPath()
        self.updateGrid()
        self.master.mainloop()


def staticGridSimulation():
    wMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates random enviroment on the grid
    generator = RandomObjects(wMap)
    # You can change the number of every type of object you want
    generator.create_env(20, 0, 0, 20, 7)
    generator.bloatTiles(robot_radius, bloat_factor)

    # Starting location
    topLeftX = 2.0
    topLeftY = 2.0

    # Ending Location
    botRightX = tile_size * tile_num_width - 2.0
    botRightY = tile_size * tile_num_height - 2.0

    # Run algorithm to get path
    try:
        dists, path = search.a_star_search(
            wMap, (topLeftX, topLeftY), (botRightX, botRightY), search.euclidean)

        root = Tk()
        # start GUI and run animation
        simulation = MapPathGUI(root, wMap, path, generator.squares)
        simulation.runSimulation(True)
    except:
        print("C1C0: \"There is no path to the desired location. Beep Boop\"")

    if __name__ == "__main__":
        staticGridSimulation()
