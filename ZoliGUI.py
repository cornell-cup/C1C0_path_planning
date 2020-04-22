import grid
import search
import tkinter as tk
from tkinter import *
import time
import datetime
import random
import math

###########GLOBAL VARIABLES############

# Speed ie time between updates
speed = 20
# Tile size (3=very small, 5=small, 10=mediumish, 20=bigish)
tile_size = 3
# height of window
tile_num_height = 260
# width of window
tile_num_width = 500


class RandomObjects():
    def __init__(self, grid):
        self.grid = grid.grid
        self.height = grid.num_rows
        self.width = grid.num_cols

    def generateBox(self):
        sizeScalarW = int(math.sqrt(self.height))
        sizeScalarH = int(math.sqrt(self.height))
        sizeScalar = int(min(sizeScalarH, sizeScalarW*1.4))
        randW = random.randint(int(sizeScalar/6), sizeScalar)
        randH = random.randint(int(sizeScalar/6), sizeScalar)
        goodLoc = False
        while not goodLoc:
            randX = random.randint(0, self.width-randW)
            randY = random.randint(0, self.height-randH)
            if(randY+randH >= self.height or randX+randW >= self.width):
                goodLoc = False
            else:
                goodLoc = self.grid[randY][randX].isObstacle == False and self.grid[randY+randH][randX].isObstacle == False and self.grid[randY][randX +
                                                                                                                                                 randW].isObstacle == False and self.grid[randY+randH][randX+randW].isObstacle == False

        for y in range(randY, randY+randH):
            for x in range(randX, randX+randW):
                self.grid[y][x].isObstacle = True

    def generateCirc(self):
        pass

    def generateCrec(self):
        pass

    def generateSeq(self):
        sizeScalarW = int(math.sqrt(self.height)*1.2)
        sizeScalarH = int(math.sqrt(self.height)*1.2)
        sizeScalar = min(sizeScalarH, sizeScalarW)
        sizeScalar = random.randint(int(sizeScalar/4), sizeScalar)
        goodLoc = False
        while not goodLoc:
            randX = random.randint(0, self.width-sizeScalar)
            randY = random.randint(0, self.height-sizeScalar)
            if(randY+sizeScalar >= self.height or randX+sizeScalar >= self.width or randY-sizeScalar <= 0 or randX-sizeScalar <= 0):
                goodLoc = False
            else:
                goodLoc = self.grid[randY][randX].isObstacle == False and self.grid[randY+sizeScalar][randX].isObstacle == False and self.grid[randY][randX +
                                                                                                                                                      sizeScalar].isObstacle == False and self.grid[randY+sizeScalar][randX+sizeScalar].isObstacle == False
        for i in range(sizeScalar*4):
            self.recursiveGen(sizeScalar, randX, randY)

    def recursiveGen(self, depth, x, y):
        if(depth == 0):
            return
        randNum = random.randint(1, 4)
        if(randNum == 1):
            self.grid[y][x-1].isObstacle = True
            self.recursiveGen(depth-1, x-1, y)
        if(randNum == 2):
            self.grid[y-1][x].isObstacle = True
            self.recursiveGen(depth-1, x, y-1)
        if(randNum == 3):
            self.grid[y][x+1].isObstacle = True
            self.recursiveGen(depth-1, x+1, y)
        if(randNum == 4):
            self.grid[y+1][x].isObstacle = True
            self.recursiveGen(depth-1, x, y+1)

    def create_env(self, numBoxes, numCirc, numCrec, numSeq):
        for i in range(numBoxes):
            self.generateBox()
        for i in range(numSeq):
            self.generateSeq()


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

    generator = RandomObjects(wMap)
    generator.create_env(50, 0, 0, 80)
    # randomTileFill(wMap)

    # search(map, start, goal, search)
    topLeftX = 2.0
    topLeftY = 2.0
    botRightX = tile_size*tile_num_width-2.0
    botRightY = tile_size*tile_num_height-2.0
    dists, path = search.a_star_search(
        wMap, (topLeftX, topLeftY), (botRightX, botRightY), search.euclidean)
    root = Tk()

    simulation = MapPath(root, wMap, path)
    simulation.runSimulation()
