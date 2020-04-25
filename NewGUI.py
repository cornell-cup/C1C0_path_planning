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
speed = 10
# Tile size (3=very small, 5=small, 10=mediumish, 20=bigish)
tile_size = 4
# height of window
tile_num_height = 180
# width of window
tile_num_width = 180
# visibility radius
# INV: vis_radius/tile_size must be an int
vis_radius = 60


class RandomObjects():
    def __init__(self, grid):
        """A class to help generate a random enviroment with random objects

        Arguments:
            grid {grid.grid} -- The grid to fill in with obstacles

        FIELDS:
        gridObj {Grid} -- Grid object to generate on 
        grid {list (list Tile)} -- the actual grid of tiles
        height {int} -- height of grid
        width {int} -- width of grid
        """
        self.gridObj = grid
        self.grid = grid.grid
        self.height = grid.num_rows
        self.width = grid.num_cols

    def bloatTiles(self, radius, bloat_factor):
        """bloats the tiles in this grid
        """
        for i in range(self.height):
            for j in range(self.width):
                if(self.grid[i][j].isObstacle == True and self.grid[i][j].isBloated == False):
                    # print("i:" + str(i) + " j:" + str(j))
                    self.gridObj.bloat_tile(i, j, radius, bloat_factor)

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
            barY = self.height-barLength
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

        FIELDS:
            master {Tk} -- Tkinter GUI generator
            tile_dict {dict} -- a dictionary that maps tiles to rectangles
            canvas {Canvas} -- the canvas the GUI is made on 
            path {Tile list} -- the list of tiles visited by robot on path
            pathSet {Tile Set} -- set of tiles that have already been drawn (So GUI
                does not draw over the tiles)
            pathIndex {int} -- the index of the path the GUI is at in anumation
            curr_tile {Tile} -- the current tile the robot is at in animation
            grid {Grid} -- the Grid object that the simulation was run on
        """
        # Tinker master, used to create GUI
        self.master = master
        self.tile_dict = None
        self.canvas = None
        self.path = path
        self.pathSet = set()
        self.pathIndex = len(path)-1
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

        index_radius_inner = int(vis_radius/tile_size)
        index_rad_outer = index_radius_inner + 2

        row = self.curr_tile.row
        col = self.curr_tile.col
        lower_row = int(max(0, row-index_rad_outer))
        lower_col = int(max(0, col-index_rad_outer))
        upper_row = int(min(row+index_rad_outer, self.grid.num_rows-1))
        upper_col = int(min(col+index_rad_outer, self.grid.num_cols-1))
        # print("lower radius: " + str(index_radius_inner) +
        #      " upper radius: " + str(index_rad_outer))
       # print("lower col: " + str(lower_col) + " upper row: " + str(upper_col))
       # print("lower row: " + str(lower_row) + " upper row: " + str(upper_row))
        # print("++++++++++++++++++++++++++++++++++++++++")
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.grid.grid[j][i]
                curr_rec = self.tile_dict[curr_tile]
                x_dist = abs(i-row)
                y_dist = abs(j-col)
                dist = math.sqrt(x_dist*x_dist+y_dist*y_dist)
                if(dist < index_radius_inner):
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
        """USED TO ANIMATE THE SIMULATION
        Update function that is continuously called using the
        master.after command, any code before that will automatically
        run at every iteration, according to global variable, speed.
        """
        if(self.pathIndex != -1):
            curr_tile = self.path[self.pathIndex]
            curr_rec = self.tile_dict[curr_tile]
            self.curr_tile = curr_tile
            self.pathSet.add(curr_tile)
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


def largeGridSimulation():
    wMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates random enviroment on the grid
    generator = RandomObjects(wMap)
    # You can change the number of every type of object you want
    generator.create_env(20, 0, 0, 20, 4)
    generator.bloatTiles(10, 2)

    # Starting location
    topLeftX = 2.0
    topLeftY = 2.0

    # Ending Location
    botRightX = tile_size*tile_num_width-2.0
    botRightY = tile_size*tile_num_height-2.0

    # Run algorithm to get path
    dists, path = search.a_star_search(
        wMap, (topLeftX, topLeftY), (botRightX, botRightY), search.euclidean)
    root = Tk()
    print((path[-1].x, path[-1].y))
    print((path[0].x, path[0].y))
    # start GUI and run animation
    simulation = MapPathGUI(root, wMap, path)
    simulation.runSimulation()


if __name__ == "__main__":
    largeGridSimulation()
    # smallGridSimulation()