import math
from tkinter import Canvas

from Constants.Consts import *
from Simulation_Helpers.GenerateSensorData import GenerateSensorData


class MapPathGUI():
    def __init__(self, master, fullMap, emptyMap, path):
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

        self.gridFull = fullMap
        self.gridEmpty = emptyMap

        self.create_widgets()
        self.generate_sensor = GenerateSensorData(self.gridFull)

    def create_widgets(self, empty=True):
        """Creates the canvas of the size of the inputted grid
        """
        if (empty):
            map = self.gridEmpty.grid
        else:
            map = self.gridFull.grid
        width = len(map[0]) * GUI_tile_size
        height = len(map) * GUI_tile_size
        vis_map = Canvas(self.master, width=width, height=height)
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
                if tile.is_bloated:
                    color = "#ffc0cb"
                elif tile.is_obstacle:
                    color = "#ffCC99"
                else:
                    color = "#545454"
                if empty:
                    tile_dict[tile] = visMap.create_rectangle(
                        x1, y1, x2, y2, outline=color, fill=color)
        vis_map.pack()
        self.canvas = vis_map
        if empty:
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
        upper_row = int(min(row + index_rad_outer, self.gridFull.num_rows - 1))
        upper_col = int(min(col + index_rad_outer, self.gridFull.num_cols - 1))
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.gridEmpty.grid[i][j]
                curr_rec = self.tile_dict[curr_tile]
                x_dist = abs(i - row)
                y_dist = abs(j - col)
                dist = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                if dist < index_radius_inner:
                    if curr_tile.is_obstacle and curr_tile.is_bloated:
                        self.canvas.itemconfig(
                            curr_rec, outline="#ffc0cb", fill="#ffc0cb")
                    elif curr_tile.is_obstacle and not curr_tile.is_bloated and curr_tile.isFound:
                        self.canvas.itemconfig(
                            curr_rec, outline="#ff621f", fill="#ff621f")
                elif curr_tile.is_obstacle:
                    self.canvas.itemconfig(
                        curr_rec, outline="#ffCC99", fill="#ffCC99")
                elif curr_tile not in self.pathSet:
                    self.canvas.itemconfig(
                        curr_rec, outline="#fff", fill="#fff")
                else:
                    if curr_tile.is_obstacle is False and curr_tile not in self.pathSet:
                        self.canvas.itemconfig(
                            curr_rec, outline="#545454", fill="#545454")


def updateGrid(self):
    """USED TO ANIMATE THE SIMULATION
    Update function that is continuously called using the
    master.after command, any code before that will automatically
    run at every iteration, according to global variable, speed.
    """
    if self.pathIndex != -1:
        curr_tile = self.path[self.pathIndex]
        curr_rec = self.tile_dict[curr_tile]
        self.curr_tile = curr_tile
        self.pathSet.add(curr_tile)
        lidar_data = self.generate_sensor.generateLidar(
            10, curr_tile.row, curr_tile.col)
        self.gridEmpty.update_grid_tup_data(
            curr_tile.x, curr_tile.y, lidar_data, Tile.lidar, robot_radius, bloat_factor, self.pathSet)
        self.visibilityDraw()
        self.canvas.itemconfig(
            curr_rec, outline="#339933", fill="#339933")
        self.pathIndex = self.pathIndex - 1

        self.master.after(speed, self.updateGrid)


def run_static_simulation(self):
    """Runs a sumulation of this map, with its enviroment and path
    """
    self.updateGrid()
    self.master.mainloop()
