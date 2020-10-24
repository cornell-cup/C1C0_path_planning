import grid
import search
import tkinter as tk
from tkinter import *
import time
import datetime
import random
import math

from Consts import *
from RandomObjects import RandomObjects
import GenerateSensorData
import grid
import tkinter as tk
from tkinter import *
import time
import random
import math
import StaticGUI

from Consts import *
from GenerateSensorData import GenerateSensorData


class DynamicGUI():
    def __init__(self, master, fullMap, emptyMap, path, endPoint):
        """A class to represent a GUI with a map

        Arguments:
            master {Tk} -- Tkinter GUI generator
            inputMap {grid} -- The grid to draw on
            path {tile list} -- the path of grid tiles visited

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

        self.initPhase = True

        self.brokenPath = None
        self.brokenPathIndex = 0

        self.visitedSet = set()
        self.pathSet = set()
        for i in self.path:
            self.pathSet.add(i)
        self.pathIndex = 0
        self.curr_tile = None

        self.gridFull = fullMap
        self.gridEmpty = emptyMap

        self.recalc = False
        self.stepsSinceRecalc = 0

        self.create_widgets()
        self.generate_sensor = GenerateSensorData(
            self.gridFull)

        self.endPoint = endPoint
        self.next_tile = None

        self.last_iter_seen = []

    def create_widgets(self, empty=True):
        """Creates the canvas of the size of the inputted grid
        Create left side GUI with all obstacles visible
        If empty=True, draw empty grid (where robot doesn't know its surroundings)
        (function is run only at initialization of grid)
        """
        self.master.geometry("+900+100")
        if empty:
            map = self.gridEmpty.grid
        else:
            map = self.gridFull.grid
        width = len(map[0]) * GUI_tile_size
        height = len(map) * GUI_tile_size
        visMap = Canvas(self.master, width=width, height=height)
        offset = GUI_tile_size / 2
        if empty:
            tile_dict = {}
        for row in map:
            for tile in row:
                x = tile.x / tile_scale_fac
                y = tile.y / tile_scale_fac
                x1 = x - offset
                y1 = y - offset
                x2 = x + offset
                y2 = y + offset
                if tile.isBloated:
                    color = "#ffc0cb"
                elif tile.isObstacle:
                    color = "#ffCC99"
                else:
                    color = "#545454"
                if empty:
                    tile_dict[tile] = visMap.create_rectangle(
                        x1, y1, x2, y2, outline=color, fill=color)
        visMap.pack()
        self.canvas = visMap
        if empty:
            self.tile_dict = tile_dict

    def visibilityDraw(self):
        """Draws a circle of visibility around the robot
        """
        for tile in self.last_iter_seen:
            self.canvas.itemconfig(
                tile, outline="#FFFF00", fill="##FFFF00")
        self.last_iter_seen = []
        row = self.curr_tile.row
        col = self.curr_tile.col
        index_radius_inner = int(vis_radius / tile_size)
        index_radius_outer = index_radius_inner + 2

        # the bounds for the visibility circle
        lower_row = int(max(0, row - index_radius_outer))
        lower_col = int(max(0, col - index_radius_outer))
        upper_row = int(min(row + index_radius_outer, self.gridFull.num_rows))
        upper_col = int(min(col + index_radius_outer, self.gridFull.num_cols))

        lidar_data = self.generate_sensor.generateLidar(degree_freq, row, col)
        rad_inc = int(GUI_tile_size / 3)  # radius increment to traverse tiles

        def _color_normally(coords):
            """
            Colors the tile at coordinates based on its known attribute (obstacle, bloated, visited, or seen).
            (coordinates must be in bounds of GUI window)
            """
            curr_tile = self.gridEmpty.grid[int(coords[0])][int(coords[1])]
            curr_rec = self.tile_dict[curr_tile]
            if not curr_tile.isKnown:
                # tile has not been "seen" before; i.e. no information is known about this tile
                if not curr_tile.isObstacle:  # available path in range of sight
                    self.canvas.itemconfig(
                        curr_rec, outline="#fff", fill="#fff")  # white
                    self.last_iter_seen.append(curr_rec)
            else:
                if curr_tile in self.visitedSet:  # tile on path already travelled
                    self.canvas.itemconfig(
                        curr_rec, outline="#0C9F34", fill="#0C9F34")  # green
                elif curr_tile.isBloated:
                    self.canvas.itemconfig(
                        curr_rec, outline="#ffc0cb", fill="#ffc0cb")  # pink
                elif curr_tile.isObstacle:
                    self.canvas.itemconfig(
                        curr_rec, outline="#ff621f", fill="#ff621f")  # red
            curr_tile.isKnown = True

        for deg in range(0, 360, degree_freq):
            # iterating through 360 degrees surroundings of robot in increments of degree_freq
            angle_rad = deg * math.pi / 180
            if len(lidar_data) == 0 or (len(lidar_data) != 0 and lidar_data[0][0] != deg):
                # no object in sight at deg; color everything normally up to visibility radius
                for r in range(0, index_radius_inner, rad_inc):
                    coords = (r * math.sin(angle_rad) + row, r *
                              math.cos(angle_rad) + col)  # (row, col) of tile
                    if (coords[0] >= lower_row) and (coords[0] <= upper_row)\
                            and (coords[1] >= lower_col) and (coords[1] <= upper_col):
                        # make sure coords are in bounds of window
                        _color_normally(coords)
            else:  # obstacle in sight
                # color everything normally UP TO obstacle, color obstacle red, then color unknown tiles gray
                # coloring UP TO obstacle
                for r in range(0, math.ceil(lidar_data[0][1] / tile_size) + rad_inc, rad_inc):
                    coords = (r * math.sin(angle_rad) + row,
                              r * math.cos(angle_rad) + col)
                    if (coords[0] >= lower_row) and (coords[0] <= upper_row) \
                            and (coords[1] >= lower_col) and (coords[1] <= upper_col):
                        _color_normally(coords)
                lidar_data.pop(0)

    def breakUpLine(self, curr_tile, next_tile):
        current_loc = (curr_tile.x, curr_tile.y)
        next_loc = (next_tile.x, next_tile.y)
        # calculate the slope, rise/run
        x_change = next_loc[0] - current_loc[0]
        y_change = next_loc[1] - current_loc[1]
        dist = math.sqrt(x_change ** 2 + y_change ** 2)

        # if (dist < tile_size):
        #     return [(current_loc[0] + x_change, current_loc[1] + y_change)]

        num_steps = int(dist / tile_size)
        returner = []

        if y_change == 0:
            x_step = tile_size
            y_step = 0
        elif x_change == 0:
            x_step = 0
            y_step = tile_size
        else:
            inv_slope = x_change / y_change
            # x^2+y^2 = tile_size^2    &&     x/y = x_change/y_change
            y_step = math.sqrt(tile_size ** 2 / (inv_slope ** 2 + 1))
            y_step = y_step
            x_step = math.sqrt(
                (tile_size ** 2 * inv_slope ** 2) / (inv_slope ** 2 + 1))
            x_step = x_step
        if x_change < 0 and x_step > 0:
            x_step = -x_step
        if y_change < 0 and y_step:
            y_step = -y_step

        for i in range(1, num_steps + 1):
            new_coor = (current_loc[0] + i * x_step,
                        current_loc[1] + i * y_step)
            returner.append(new_coor)
            new_tile = self.gridEmpty.get_tile(new_coor)
            if new_tile not in self.pathSet:
                self.pathSet.add(new_tile)

        return returner

    def getPathSet(self):
        """
        """
        prev_tile = self.curr_tile
        for next_tile in self.path:
            if next_tile not in self.pathSet:
                self.pathSet.add(next_tile)
            self.breakUpLine(prev_tile, next_tile)
            prev_tile = next_tile

    def printTiles(self):
        for row in self.gridEmpty.grid:
            for col in row:
                print(str(col.x) + ', ' + str(col.y))

    def checkRecalc(self):
        for x, y in self.brokenPath:
            check_tile = self.gridEmpty.get_tile((x, y))
            if check_tile.isObstacle or check_tile.isBloated:
                self.recalc = True

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion
        """
        # try:
        # If this is the first tile loop is being iterated through we need to initialize
        if self.initPhase:
            print('IN INIT PHASE')
            curr_tile = self.path[0]
            self.curr_tile = curr_tile
            self.curr_x = self.curr_tile.x
            self.curr_y = self.curr_tile.y

            self.visitedSet.add(curr_tile)
            self.getPathSet()
            lidar_data = self.generate_sensor.generateLidar(
                degree_freq, curr_tile.row, curr_tile.col)
            self.getPathSet()
            if (self.gridEmpty.updateGridLidar(
                    curr_tile.x, curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet, self.gridFull)):
                self.recalc = True

            self.next_tile = self.path[1]
            self.brokenPath = self.breakUpLine(self.curr_tile, self.next_tile)
            self.getPathSet()
            self.brokenPathIndex = 0
            self.visibilityDraw()

            self.initPhase = False
            self.master.after(speed_dynamic, self.updateGridSmoothed)
            # If we need to iterate through a brokenPath
        elif self.brokenPathIndex < len(self.brokenPath):
            #print('IN BROKEN PATH')
            lidar_data = self.generate_sensor.generateLidar(
                degree_freq, self.curr_tile.row, self.curr_tile.col)
            if (self.gridEmpty.updateGridLidar(
                    self.curr_tile.x, self.curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet,
                    self.gridFull)):
                self.recalc = True
            # Relcalculate the path if needed
            if self.recalc:
                print('recalculating!')
                dists, self.path = search.a_star_search(
                    self.gridEmpty, (self.curr_tile.x, self.curr_tile.y), self.endPoint, search.euclidean)
                self.path = search.segment_path(self.gridEmpty, self.path)
                self.pathIndex = 0
                self.smoothed_window.path = self.path
                self.smoothed_window.drawPath()
                self.curr_tile = self.path[0]
                self.next_tile = self.path[1]
                self.brokenPath = self.breakUpLine(
                    self.curr_tile, self.next_tile)
                self.getPathSet()
                self.visibilityDraw()
                self.pathSet = set()
                self.getPathSet()
                self.pathIndex = 0
                self.brokenPathIndex = 0
                self.recalc = False
            else:
                x1 = self.brokenPath[self.brokenPathIndex - 1][0]
                y1 = self.brokenPath[self.brokenPathIndex - 1][1]
                x2 = self.brokenPath[self.brokenPathIndex][0]
                y2 = self.brokenPath[self.brokenPathIndex][1]
                # MAYBE CHANGE WIDTH TO SEE IF IT LOOKS BETTER?
                self.canvas.create_line(x1, y1, x2, y2, fill="#339933")
                self.curr_tile = self.gridEmpty.get_tile((x2, y2))
                self.visitedSet.add(self.curr_tile)

                self.visibilityDraw()
                self.brokenPathIndex += 1

            self.master.after(speed_dynamic, self.updateGridSmoothed)

        # If we have finished iterating through a broken path, we need to go to the
        # Next tile in path, and create a new broken path to iterate through
        else:
            if self.curr_tile == self.gridEmpty.get_tile(self.endPoint):
                print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
                return
            self.pathSet = set()
            self.pathIndex += 1
            if self.pathIndex == len(self.path) - 1:
                print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
                return
            self.curr_tile = self.path[self.pathIndex]
            self.next_tile = self.path[self.pathIndex+1]
            self.brokenPath = self.breakUpLine(self.curr_tile, self.next_tile)
            self.getPathSet()
            self.brokenPathIndex = 0
            self.visibilityDraw()
            self.master.after(speed_dynamic, self.updateGridSmoothed)
        # except:
            #print("C1C0: \"There is no path to the desired location. Beep Boop\"")

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.smoothed_window = StaticGUI.SmoothedPathGUI(
            Toplevel(), self.gridFull, self.path)
        self.smoothed_window.drawPath()
        self.updateGridSmoothed()
        self.master.mainloop()


def validLocation(text) -> int:
    """
    takes in text and outputs 1 if the text is a valid location on the grid,
    ouptuts a 2 if the location is outside of the grid
    outputs a 3 if the location text is malformed
    """
    try:
        commaIndex = text.find(',')
        firstNum = float(text[1:commaIndex])
        print(firstNum)
        secondNum = float(text[commaIndex + 1:-1])
        print(secondNum)
        if (firstNum > tile_size * tile_num_width / 2 or firstNum < -(tile_size * tile_num_width / 2)):
            return 2
        if (secondNum > tile_size * tile_num_height / 2 or secondNum < -(tile_size * tile_num_height / 2)):
            return 2
        return 1

    except:
        return 3


def printScreen():
    """
    prints welcome screen to simulation
    """
    # Print screen
    print("_________                            .__  .__    _________")
    print("\_   ___ \  ___________  ____   ____ |  | |  |   \_   ___ \ __ ________  ")
    print("/    \  \/ /  _ \_  __ \/    \_/ __ \|  | |  |   /    \  \/|  |  \____ \ ")
    print("\     \___(  <_> )  | \/   |  \  ___/|  |_|  |__ \     \___|  |  /  |_> >")
    print(" \______  /\____/|__|  |___|  /\___  >____/____/  \______  /____/|   __/ ")
    print("        \/                  \/     \/                    \/      |__|    ")

    print("===================================================================================")
    print("                    Welcome to CICO's path planning Simulation")
    print("===================================================================================")
    print("If you would like to edit the grid size or number of obstacles,")
    print("visit the file consts.py and edit the varaibles located in the python file")


def getLocation(text: str) -> (int, int):
    """
    Precondion: String is a valid string of the form (int,int)
    Returns parsed string in the form of an int tuple
    """
    commaIndex = text.find(',')
    firstNum = float(text[1:commaIndex])
    secondNum = float(text[commaIndex + 1:-1])
    # convert from meters to cm
    firstNum = firstNum * 100
    secondNum = secondNum * 100
    firstNum = firstNum + tile_num_width * tile_size / 2
    secondNum = -secondNum + tile_num_height * tile_size / 2

    return (firstNum, secondNum)


def userInput():
    printScreen()

    text = input(
        "Please enter the coordinate you desire CICO to go to in the form (x,y):  ")
    # ending location
    while (validLocation(text) != 1):
        if (validLocation(text) == 2):
            print("Your location was OUT OF THE RANGE of the specified grid")
            text = input(
                "Please enter the coordinate you desire CICO to go to in the form (x,y):  ")

        elif (validLocation(text) == 3):
            print("Your location input was MALFORMED")
            text = input(
                "Please enter the coordinate you desire CICO to go to in the form (x,y): ")

    return getLocation(text)


def validLocation(text) -> int:
    """
    takes in text and outputs 1 if the text is a valid location on the grid,
    ouptuts a 2 if the location is outside of the grid
    outputs a 3 if the location text is malformed
    """
    try:
        commaIndex = text.find(',')
        firstNum = float(text[1:commaIndex])
        secondNum = float(text[commaIndex + 1:-1])
        if (firstNum > tile_size * tile_num_width / 2 or firstNum < -(tile_size * tile_num_width / 2)):
            return 2
        if (secondNum > tile_size * tile_num_height / 2 or secondNum < -(tile_size * tile_num_height / 2)):
            return 2
        return 1

    except:
        return 3


def dynamicGridSimulation():
    emptyMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    fullMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates random enviroment on the grid
    generator = RandomObjects(fullMap)

    # You can change the number of every type of object you want
    generator.create_env(22, 0, 0, 22, 9)

    # starting location for middle
    midX = tile_size * tile_num_width / 2
    midY = tile_size * tile_num_height / 2

    # Calculate and point and change coordinate system from user inputted CICO @(0,0) to the grid coordinates
    endPoint = userInput()
    # Run algorithm to get path
    dists, path = search.a_star_search(
        emptyMap, (midX, midY), endPoint, search.euclidean)
    # start GUI and run animation
    simulation = DynamicGUI(Tk(), fullMap, emptyMap,
                            search.segment_path(emptyMap, path), endPoint)
    simulation.runSimulation()


if __name__ == "__main__":
    # staticGridSimulation()
    dynamicGridSimulation()
