import grid
import search
import tkinter as tk
from tkinter import *
import time
import datetime
import random

###########GLOBAL VARIABLES############

# Speed ie time between updates
speed = 20
# Tile size (3=very small, 5=small, 10=mediumish, 20=bigish)
tile_size = 3
# height of window
tile_num_height = 260
# width of window
tile_num_width = 280


# Class for GUI simulations
class MapPath():
    def __init__(self, master, inputMap, path):
        # Tinker master, used to create GUI
        self.master = master

        self.tile_dict = None
        self.canvas = None
        self.path = path
        self.pathIndex = len(path)-1

        self.create_widgets(inputMap)

    def create_widgets(self, worldMap):
        width = len(worldMap.grid[0]) * worldMap.tileLength
        height = len(worldMap.grid) * worldMap.tileLength
        visMap = Canvas(self.master, width=width, height=height)
        offset = worldMap.tileLength/2
        tile_dict = {}
        for row in worldMap.grid:
            for tile in row:
                x = tile.x
                y = (len(worldMap.grid)*worldMap.tileLength) - tile.y
                x1 = x - offset
                y1 = y - offset
                x2 = x + offset
                y2 = y + offset
                color = "#ff6600" if tile.isObstacle else "#fff"
                tile_dict[tile] = visMap.create_rectangle(
                    x1, y1, x2, y2, outline=color, fill=color)
        visMap.pack()
        self.canvas = visMap
        self.tile_dict = tile_dict

    def updateGrid(self):
        if(self.pathIndex != -1):
            rec = self.tile_dict[self.path[self.pathIndex]]
            self.canvas.itemconfig(rec, outline="#339933", fill="#339933")
            self.pathIndex = self.pathIndex-1
            self.master.after(speed, self.updateGrid)

    def runSimulation(self):
        self.updateGrid()
        self.master.mainloop()


def randomTileFill(grid: grid.Grid):
    for grid_row in grid.grid:
        for tile in grid_row:
            randomNum = random.randint(1, 4)
            if(randomNum == 1):
                tile.isObstacle = True


if __name__ == "__main__":
    wMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    randomTileFill(wMap)

    #search(map, start, goal, search)
    topLeftX = 2.0
    topLeftY = 2.0
    botRightX = tile_size*tile_num_width-2.0
    botRightY = tile_size*tile_num_height-2.0
    dists, path = search.a_star_search(
        wMap, (topLeftX, topLeftY), (botRightX, botRightY), search.euclidean)
    root = Tk()
    simulation = MapPath(root, wMap, path)
    simulation.runSimulation()
