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
speed = 40
# Tile size (3=very small, 5=small, 10=mediumish, 20=bigish)
tile_size = 3
# height of window
tile_num_height = 260
# width of window
tile_num_width = 260
# visibility radius
# INV: vis_radius/tile_size must be an int
vis_radius = 45


class RandomObjects():
    def __init__(self, grid):
        """A class to help generate a random enviroment with random objects

        Arguments:
            grid {grid.grid} -- The grid to fill in with obstacles
        """
        self.gridObj = grid
        self.grid = grid.grid
        self.height = grid.num_rows
        self.width = grid.num_cols

    def bloatTiles(self):
        """bloats the tiles in this grid
        """
        a = False
        for i in range(self.height):
            for j in range(self.width):
                a = self.gridObj.bloat_tile(i, j)

    def generateBox(self):
        """Generates a random box of a random size in the grid
        """
        sizeScalarW = int(math.sqrt(self.height))
        sizeScalarH = int(math.sqrt(self.height))
        sizeScalar = int(min(sizeScalarH, sizeScalarW*1.4))
        randW = random.randint(int(sizeScalar/6), sizeScalar)
        randH = random.randint(int(sizeScalar/6), sizeScalar)

        randX = random.randint(0, self.width-randW)
        randY = random.randint(0, self.height-randH)

        for y in range(randY, randY+randH):
            for x in range(randX, randX+randW):
                self.grid[y][x].isObstacle = True

    def generateCirc(self):
        pass

    def generateCrec(self):
        pass

    def generateBar(self):
        """generates a bar of width 1, 2 or three
        """
        barWidth = random.randint(1, 3)
        barLength = random.randint(int(self.height/6), int(2*self.height/3))
        barX = random.randint(1, self.width)
        barY = random.randint(0, self.height-barLength)
        randomChance = random.randint(1, 4)
        if (randomChance == 1):
            barY = 0
        elif(randomChance == 2):
            barY = self.height-barLength-1
        for i in range(barWidth):
            for j in range(barLength):
                if (barY+j < self.height and barX+i < self.width-1):
                    self.grid[barY+j][barX+i].isObstacle = True

    def generateSeq(self):
        """Calculates a random size and location to generate a randomized shape
        then calls recursiveGen() many times to generate the shape
        """
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
        """This recursive function starts at the grid located at x y,
        and then fills in tiles as obstacles randomly jumping to locations
        next to the grid depth times

        Arguments:
            depth {int} -- Home many tiles to fill in as obstacles
            x {int} -- column of grid to fill in
            y {int} -- row of grid to fill in
        """
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

    def create_env(self, numBoxes, numCirc, numCrec, numSeq, numBars):
        """Generates an enviroment with many randomized obstacles of different
        shapes and sizes, each argument corresponds to how many
        of those obstacles should be generated

        Arguments:
            numBoxes {int} -- [description]
            numCirc {int} -- [description]
            numCrec {[type]} -- [description]
            numSeq {[type]} -- [description]
        """
        for i in range(numBoxes):
            self.generateBox()
        for j in range(numSeq):
            self.generateSeq()
        for k in range(numBars):
            self.generateBar()
        # self.create_rand_env(8)

    def create_rand_env(self, prob):
        """Fills in grid rorally randomly

        Arguments:
        prob {int} -- 1/prob = the probability any tile is an obstacle
        """
        for grid_row in self.grid:
            for tile in grid_row:
                randomNum = random.randint(1, prob)
                if(randomNum == 1):
                    tile.isObstacle = True


class MapPathGUI():
    def __init__(self, master, inputMap, path):
        """A class to represent a GUI with a map

        Arguments:
            master {Tk} -- Tkinter GUI generator
            inputMap {grid} -- The grid to draw on
            path {list} -- the path of grid tiles visited
        """
        # Tinker master, used to create GUI
        self.master = master
        self.tile_dict = None
        self.canvas = None
        self.path = path
        self.pathSet = set()
        self.pathIndex = len(path)-1
        self.curr_x = 0
        self.curr_y = 0
        self.curr_tile = None
        self.grid = inputMap

        self.create_widgets()

    def create_widgets(self):
        """Creates the canvas of the size of the inputted grid
        """
        map = self.grid.grid
        width = len(map[0]) * tile_size
        height = len(map) * tile_size
        visMap = Canvas(self.master, width=width, height=height)
        offset = tile_size/2
        tile_dict = {}
        for row in map:
            for tile in row:
                x = tile.x
                y = tile.y
                x1 = x - offset
                y1 = y - offset
                x2 = x + offset
                y2 = y + offset
                if(tile.isBloated):
                    color = "#ffc0cb"
                elif(tile.isObstacle):
                    color = "#ffCC99"
                else:
                    color = "#545454"
                tile_dict[tile] = visMap.create_rectangle(
                    x1, y1, x2, y2, outline=color, fill=color)
        visMap.pack()
        self.canvas = visMap
        self.tile_dict = tile_dict

    def visibilityDraw(self):
        """Draws a circle of visibility around the robot
        """
        index_rad = vis_radius/tile_size
        curr_x_index = self.curr_tile.row
        curr_y_index = self.curr_tile.col
        lower_row = int(max(0, curr_x_index-index_rad))
        lower_col = int(max(0, curr_y_index-index_rad))
        upper_row = int(min(curr_x_index+index_rad, self.grid.num_rows-1))
        upper_col = int(min(curr_y_index+index_rad, self.grid.num_cols-1))

        for row in range(lower_row, upper_row):
            for col in range(lower_col, upper_col):
                curr_tile = self.grid.grid[self.grid.num_cols-col-1][row]
                curr_rec = self.tile_dict[curr_tile]
                x_dist = abs(curr_tile.x-self.curr_x)
                y_dist = abs(curr_tile.y-self.curr_y)
                dist = math.sqrt(x_dist*x_dist+y_dist*y_dist)
                if(dist < (vis_radius-15)):
                    if(curr_tile.isObstacle and curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ffc0cb", fill="#ffc0cb")
                    elif(curr_tile.isObstacle and not curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ff621f", fill="#ff621f")
                    elif(curr_tile not in self.pathSet):
                        self.canvas.itemconfig(
                            curr_rec, outline="#fff", fill="#fff")
                else:
                    if(curr_tile.isObstacle == False and curr_tile not in self.pathSet):
                        self.canvas.itemconfig(
                            curr_rec, outline="#545454", fill="#545454")

    def updateGrid(self):
        """Update function that is continuously called using the
        master.after command, any code before that will automatically
        run at every iteration, according to global variable, speed.
        """
        if(self.pathIndex != -1):
            curr_tile = self.path[self.pathIndex]
            curr_rec = self.tile_dict[curr_tile]
            self.curr_tile = curr_tile
            self.pathSet.add(curr_tile)
            self.curr_x = curr_tile.x
            self.curr_y = curr_tile.y
            self.visibilityDraw()
            self.canvas.itemconfig(
                curr_rec, outline="#339933", fill="#339933")
            self.pathIndex = self.pathIndex-1

            self.master.after(speed, self.updateGrid)

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.updateGrid()
        self.master.mainloop()


if __name__ == "__main__":
    wMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    generator = RandomObjects(wMap)
    # creates enviroment with 50 blocks and 80 blobs
    generator.create_env(20, 0, 0, 20, 2)

    generator.bloatTiles()

    # generator.create_rand_env(4)

    # search(map, start, goal, search)
    topLeftX = 2.0
    topLeftY = 2.0
    botRightX = tile_size*tile_num_width-2.0
    botRightY = tile_size*tile_num_height-2.0
    dists, path = search.a_star_search(
        wMap, (topLeftX, topLeftY), (botRightX, botRightY), search.euclidean)
    root = Tk()

    simulation = MapPathGUI(root, wMap, path)
    simulation.runSimulation()
