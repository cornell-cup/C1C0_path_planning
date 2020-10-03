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


class MapPathGUI():
    def __init__(self, master, inputMap, path):
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
        self.pathSet = set()
        self.pathIndex = len(path) - 1
        self.curr_tile = None
        self.grid = inputMap
        self.create_widgets()
        self.generate_sensor = GenerateSensorData(self.grid)

    def create_widgets(self):
        """Creates the canvas of the size of the inputted grid
        """
        map = self.grid.grid
        width = len(map[0]) * GUI_tile_size
        height = len(map) * GUI_tile_size
        visMap = Canvas(self.master, width=width, height=height)
        offset = GUI_tile_size / 2
        tile_dict = {}
        for row in map:
            for tile in row:
                x = tile.x / tile_scale_fac
                y = tile.y / tile_scale_fac
                x1 = x - offset
                y1 = y - offset
                x2 = x + offset
                y2 = y + offset
                if (tile.isBloated):
                    color = "#ffc0cb"
                elif (tile.isObstacle):
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

        index_radius_inner = int(vis_radius / tile_size)
        index_rad_outer = index_radius_inner + 2

        row = self.curr_tile.row
        col = self.curr_tile.col
        lower_row = int(max(0, row - index_rad_outer))
        lower_col = int(max(0, col - index_rad_outer))
        upper_row = int(min(row + index_rad_outer, self.grid.num_rows))
        upper_col = int(min(col + index_rad_outer, self.grid.num_cols))
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.grid.grid[i][j]
                curr_rec = self.tile_dict[curr_tile]
                x_dist = abs(i - row)
                y_dist = abs(j - col)
                dist = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                if (dist < index_radius_inner):
                    if (curr_tile.isObstacle and curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ffc0cb", fill="#ffc0cb")
                    elif (curr_tile.isObstacle and not curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ff621f", fill="#ff621f")
                    elif (curr_tile.isObstacle):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ffCC99", fill="#ffCC99")
                    elif (curr_tile not in self.pathSet):
                        self.canvas.itemconfig(
                            curr_rec, outline="#fff", fill="#fff")
                else:
                    if (curr_tile.isObstacle == False and curr_tile not in self.pathSet):
                        self.canvas.itemconfig(
                            curr_rec, outline="#545454", fill="#545454")

    def updateGrid(self):
        """USED TO ANIMATE THE SIMULATION
        Update function that is continuously called using the
        master.after command, any code before that will automatically
        run at every iteration, according to global variable, speed.
        """
        if (self.pathIndex != -1):
            curr_tile = self.path[self.pathIndex]
            curr_rec = self.tile_dict[curr_tile]
            self.curr_tile = curr_tile
            self.pathSet.add(curr_tile)
            lidar_data = self.generate_sensor.generateLidar(
                10, curr_tile.row, curr_tile.col)
            self.visibilityDraw()
            self.canvas.itemconfig(
                curr_rec, outline="#339933", fill="#339933")
            self.pathIndex = self.pathIndex - 1

            self.master.after(speed_static, self.updateGrid)

    def runSimulation(self, smoothPath):
        """Runs a sumulation of this map, with its enviroment and path
        """
        if smoothPath:
            segmented_path = search.segment_path(self.grid, self.path, 0.01)
            # print([(tile.x, tile.y) for tile in segmented_path])
            top = Toplevel()
            smoothed_window = SmoothedPathGUI(top, self.grid, segmented_path)
            smoothed_window.drawPath()
        self.updateGrid()
        self.master.mainloop()


class SmoothedPathGUI(MapPathGUI):
    def __init__(self, master, inputMap, path):
        super().__init__(master, inputMap, path)
        self.prev_line_id = []
        self.set_of_prev_path = []
        self.color_list = ['#2e5200', '#347800', '#48a600', '#54c200', '#60de00', 'None']
        self.index_fst_4=0

    def drawPath(self):
        # change previous 5 paths with green gradual gradient

        # set default/initial color
        color = self.color_list[4]

        # if there is any path that the bot walked through, it gets added to set_of_prev_path
        if self.prev_line_id:
            self.set_of_prev_path.append(self.prev_line_id)

        # if there is any previous path in the set_of_prev_path, then we check if there is less than 5 lines,
        # if so we change the color of the newest path to a color from the list. If there is more than 5 lines,
        # we delete the oldest line and change the colors of remaining previous colors to a lighter shade.
        if self.set_of_prev_path:
            if len(self.set_of_prev_path) > 4:
                for fst_id in self.set_of_prev_path[0]:
                    self.canvas.delete(fst_id)
                self.set_of_prev_path.pop(0)
            for x in range(len(self.set_of_prev_path)):
                for ids in self.set_of_prev_path[x]:
                    self.canvas.itemconfig(ids, fill=self.color_list[x])
        # clear current path
        self.prev_line_id = []

        # continuously draw segments of the path, and add it to the prev_line_id list
        idx = 1
        while idx < len(self.path):
            x1 = self.path[idx - 1].x / tile_scale_fac
            y1 = self.path[idx - 1].y / tile_scale_fac
            x2 = self.path[idx].x / tile_scale_fac
            y2 = self.path[idx].y / tile_scale_fac
            canvas_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1.5)
            self.prev_line_id.append(canvas_id)
            idx += 1


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
        simulation = MapPathGUI(root, wMap, path)
        simulation.runSimulation(True)
    except:
        print("C1C0: \"There is no path to the desired location. Beep Boop\"")

    if __name__ == "__main__":
        staticGridSimulation()
