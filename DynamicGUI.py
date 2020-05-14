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
        self.visitedSet = set()
        self.pathSet = set()
        for i in self.path:
            self.pathSet.add(i)
        self.pathIndex = len(path)-1
        self.curr_tile = None

        self.gridFull = fullMap
        self.gridEmpty = emptyMap

        self.recalc = False
        self.stepsSinceRecalc = 0

        self.create_widgets()
        self.generate_sensor = GenerateSensorData(
            self.gridFull)

        self.endPoint = endPoint

    def create_widgets(self, empty=True):
        """Creates the canvas of the size of the inputted grid
        """
        if(empty):
            map = self.gridEmpty.grid
        else:
            map = self.gridFull.grid
        width = len(map[0]) * GUI_tile_size
        height = len(map) * GUI_tile_size
        visMap = Canvas(self.master, width=width, height=height)
        offset = GUI_tile_size/2
        if(empty):
            tile_dict = {}
        for row in map:
            for tile in row:
                x = tile.x/tile_scale_fac
                y = tile.y/tile_scale_fac
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
                if(empty):
                    tile_dict[tile] = visMap.create_rectangle(
                        x1, y1, x2, y2, outline=color, fill=color)
        visMap.pack()
        self.canvas = visMap
        if(empty):
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
        upper_row = int(min(row+index_rad_outer, self.gridFull.num_rows))
        upper_col = int(min(col+index_rad_outer, self.gridFull.num_cols))
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.gridEmpty.grid[i][j]
                curr_rec = self.tile_dict[curr_tile]
                x_dist = abs(i-row)
                y_dist = abs(j-col)
                dist = math.sqrt(x_dist*x_dist+y_dist*y_dist)
                if(dist < index_radius_inner):
                    if(curr_tile.isObstacle and not curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ff621f", fill="#ff621f")
                    elif(curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ffc0cb", fill="#ffc0cb")
                    elif(curr_tile in self.visitedSet):
                        self.canvas.itemconfig(
                            curr_rec, outline="#0C9F34", fill="#0C9F34")
                    elif(curr_tile not in self.visitedSet):
                        self.canvas.itemconfig(
                            curr_rec, outline="#fff", fill="#fff")
                else:
                    if(curr_tile.isObstacle == False and curr_tile.isBloated == False and curr_tile not in self.visitedSet):
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
            self.visitedSet.add(curr_tile)
            lidar_data = self.generate_sensor.generateLidar(
                10, curr_tile.row, curr_tile.col)
            if(self.gridEmpty.updateGridLidar(
                    curr_tile.x, curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet, self.gridFull)):
                self.recalc = True

            nextTileIndex = min(self.pathIndex+2, len(self.path)-1)
            emergencyRecalc = False
            if(self.path[nextTileIndex].isBloated or self.path[nextTileIndex].isObstacle):
                emergencyRecalc = True

            if((self.stepsSinceRecalc >= steps_to_recalc and self.recalc) or emergencyRecalc):
                print('recalculating!')
                start = (curr_tile.x, curr_tile.y)
                dists, self.path = search.a_star_search(
                    self.gridEmpty, start, self.endPoint, search.euclidean)
                self.pathSet = set()
                for i in self.path:
                    self.pathSet.add(i)
                self.pathIndex = len(self.path)-1
                self.recalc = False
                emergencyRecalc = False
                self.stepsSinceRecalc = 0

            self.visibilityDraw()
            self.canvas.itemconfig(
                curr_rec, outline="#00FF13", fill="#00FF13")

            self.pathIndex = self.pathIndex-1
            self.stepsSinceRecalc = self.stepsSinceRecalc+1
            self.master.after(speed_dynamic, self.updateGrid)

    def BreakUpLine(self, next_tile):
        """
        breaks up a line into many consective endpoints and 
        puts them in a list
        """
        pass
        current_loc = (self.curr_tile.x, self.curr_tile.y)
        next_loc = (next_tile.x, next_tile.y)
        # calculate the slope, rise/run
        slope = (next_loc[1]-current_loc[1])/(next_loc[0]-current_loc[0])
        dist = search.euclidean([current_loc, next_loc])
        iterations = int(dist)
        returner = []
        for i in range(iterations):
            pass

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion 
        """
        for i in range(len(self.path)-1, -1, -1):
            curr_tile = self.path[i]
            # dist=search.euclidean([(self.curr_tile.x,self.curr_tile.y),
            # (curr_tile.x,curr_tile.y)])
            if self.curr_tile is not None:
                x1 = curr_tile.x / tile_scale_fac
                y1 = curr_tile.y/tile_scale_fac
                x2 = self.curr_tile.x/tile_scale_fac
                y2 = self.curr_tile.y/tile_scale_fac
                self.canvas.create_line(x1, y1, x2, y2, fill="#339933")
            self.curr_tile = curr_tile
            curr_rec = self.tile_dict[curr_tile]
            self.visitedSet.add(curr_tile)
            lidar_data = self.generate_sensor.generateLidar(
                10, curr_tile.row, curr_tile.col)
            if(self.gridEmpty.updateGridLidar(
                    curr_tile.x, curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet, self.gridFull)):
                self.recalc = True
            self.visibilityDraw()
            self.canvas.itemconfig(
                curr_rec, outline="#00FF13", fill="#00FF13")

        start = (curr_tile.x, curr_tile.y)
        dists, self.path = search.a_star_search(
            self.gridEmpty, start, self.endPoint, search.euclidean)
        self.path = search.segment_path_dyanmic(self.gridEmpty, self.path)
        self.master.after(speed_dynamic, self.updateGrid)

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.updateGridSmoothed()
        self.master.mainloop()


def dynamicGridSimulation():
    emptyMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    fullMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    # Generates random enviroment on the grid
    generator = RandomObjects(fullMap)
    # You can change the number of every type of object you want
    generator.create_env(20, 0, 0, 20, 7)
    # Starting location
    topLeftX = 2.0
    topLeftY = 2.0
    # Ending Location
    botRightX = tile_size*tile_num_width-2.0
    botRightY = tile_size*tile_num_height-2.0
    endPoint = (botRightX, botRightY)
    # Run algorithm to get path
    dists, path = search.a_star_search(
        emptyMap, (topLeftX, topLeftY), (botRightX, botRightY), search.euclidean)
    root = Tk()
    # start GUI and run animation
    simulation = DynamicGUI(root, fullMap, emptyMap, path, endPoint)
    simulation.runSimulation()


if __name__ == "__main__":
    # staticGridSimulation()
    dynamicGridSimulation()
