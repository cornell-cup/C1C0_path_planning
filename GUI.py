import tkinter as tk
from tkinter import *
import time
import random
import math

from Consts import *
from GenerateSensorData import GenerateSensorData


class GUI:
    def __init__(self, master, fullMap, emptyMap, path, squareList, index):
        """A class to represent a GUI with a map

                Arguments:
                    master {Tk} -- Tkinter GUI generator
                    inputMap {grid} -- The grid to draw on
                    path {tile list} -- the path of grid tiles visited
                    squareList -- the list of all the square objects

                FIELDS:
                    master {Tk} -- Tkinter GUI generator
                    tile_dict {dict} -- a dictionary that maps tiles to rectangles
                    canvas {Canvas} -- the canvas the GUI is made on
                    path {Tile list} -- the list of tiles visited by robot on path
                    squareList -- the list of all the square objects
        """
        self.master = master
        self.tile_dict = None
        self.canvas = None
        self.path = path
        self.pathSet = set()
        self.pathIndex = index
        self.squareList = squareList
        self.curr_tile = None
        self.gridFull = fullMap
        self.gridEmpty = emptyMap
        self.prev_line_id = []
        self.set_of_prev_path = []
        self.color_list = ['#2e5200', '#347800',
                           '#48a600', '#54c200', '#60de00', 'None']
        self.index_fst_4 = 0
        self.next_tile = None

    def create_widgets(self, empty):
        """Creates the canvas of the size of the inputted grid
        """
        self.master.geometry("+900+100")
        if (empty):
            map = self.gridEmpty.grid
        else:
            map = self.gridFull.grid
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
            canvas_id = self.canvas.create_line(
                x1, y1, x2, y2, fill=color, width=1.5)
            self.prev_line_id.append(canvas_id)
            idx += 1

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

    def moveSquare(self, square):
        x = square.getX()
        y = square.getY()
        height = square.getHeight()
        width = square.getWidth()
        velocity = square.getVelocity()
        counter = square.getCounter()
        randNum = random.randint(1, 4)
        valid = True
        if velocity < 1 and (counter + 1) * velocity < 1:
            square.setCounter(counter + 1)
        else:
            if velocity < 1:
                velocity = 1
                square.setCounter(0)
            if (randNum == 1):
                for i in range(y, y + height):
                    if checkBounds(x - velocity, i) == False:
                        valid = False
                if valid == True:
                    for j in range(1, velocity):
                        for i in range(y, y + height):
                            self.grid[i][x - j].isObstacle = True
                            self.grid[i][x + width - j] = False
                else:
                    self.moveSquare(square)
            if (randNum == 2):
                for i in range(y, y + height):
                    if checkBounds(x + width + velocity, i) == False:
                        valid = False
                if valid == True:
                    for j in range(1, velocity):
                        for i in range(y, y + height):
                            self.grid[i][x + width + j].isObstacle = True
                            self.grid[i][x + j] = False
                else:
                    self.moveSquare(square)
            if (randNum == 3):
                for i in range(x, x + width):
                    if checkBounds(i, y - velocity) == False:
                        valid = False
                if valid == True:
                    for j in range(1, velocity):
                        for i in range(x, x + width):
                            self.grid[y - j][i].isObstacle = True
                            self.grid[y + height - j][i] = False
                else:
                    self.moveSuare(square)
            if (randNum == 4):
                for i in range(x, x + width):
                    if checkBounds(i, y + height + velocity) == False:
                        valid = False
                if valid == True:
                    for j in range(1, velocity):
                        for i in range(x, x + width):
                            self.grid[y + height + j][i].isObstacle = True
                            self.grid[y + j][i] = False
                else:
                    self.moveSquare(square)
