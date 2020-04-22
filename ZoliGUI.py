import grid
import search
import tkinter as tk
from tkinter import *
import time
import datetime
import random

"""
Class MapPath to create simulations for 
"""


class MapPath():
    def __init__(self, master, inputMap, path):
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
                color = "red" if tile.isObstacle else "white"
                tile_dict[tile] = visMap.create_rectangle(
                    x1, y1, x2, y2, fill=color)
        visMap.pack()
        self.canvas = visMap
        self.tile_dict = tile_dict

    def updateGrid(self):
        if(self.pathIndex != -1):
            rec = self.tile_dict[self.path[self.pathIndex]]
            self.canvas.itemconfig(rec, fill="green")
            self.pathIndex = self.pathIndex-1
            self.master.after(500, self.updateGrid)

    def runSimulation(self):
        self.updateGrid()
        self.master.mainloop()


def randomTileFill(grid: grid.Grid):
    for grid_row in grid.grid:
        for tile in grid_row:
            randomNum = random.randint(1, 3)
            if(randomNum == 1):
                tile.isObstacle = True


if __name__ == "__main__":
    wMap = grid.Grid(100, 100, 5)
    randomTileFill(wMap)

    #search(map, start, goal, search)
    dists, path = search.a_star_search(
        wMap, (2.0, 390.0), (2.0, 20.0), search.euclidean)
    root = Tk()
    simulation = MapPath(root, wMap, path)
    simulation.runSimulation()
