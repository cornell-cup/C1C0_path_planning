import numpy as np
import Tile

class Grid:

   #Comments:
   #Want the tile size to be 0.1 m for now

    """
    Initializer for grid
    Parameters: grid - size of the grid in meters
                tile - length of the tile
    """
    def __init__(self, tile):
        self.tileLength = tile
        self.grids = self.createGrid() #2d list of tiles

    """
    Updates the grid with obstacles
    """
    def updateGridWithObstacles(self, current, new):


    def createGrid(self):
        grid = []
        for row in range(2/tileLength): #the sensor readings are 2 meters
            inner = []
            for col in range(2/tileLength):
                tile = Tile(tileLength) #0.1 meters
                inner.append(tile)
            grid.append(inner)
        return grid

    def printGrid(self):
        for row in range (2 / tileLength):
            accum = ""
            for col in range (2 / tileLength):
                if grids[row][col].isOccupied:
                    accum = accum + "#"
                else:
                    accum = accum + "_"
            print(accum)
