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

        self.init_phase = True

        self.broken_path = None
        self.broken_path_index = 0

        self.visited_set = set()
        self.path_set = set()
        for i in self.path:
            self.path_set.add(i)
        self.path_index = 0
        self.curr_tile = None

        self.grid_full = fullMap
        self.grid_empty = emptyMap

        self.recalc = False
        self.steps_since_recalc = 0

        self.create_widgets()
        self.generate_sensor = GenerateSensorData(
            self.grid_full)

        self.end_point = endPoint
        self.next_tile = None
        self.heading = 0
        # TODO: change to custom type or enum
        self.output_state = "stopped"
        self.desired_heading = None

    def create_widgets(self, empty=True):
        """Creates the canvas of the size of the inputted grid
        """
        self.master.geometry("+900+100")
        if (empty):
            map = self.grid_empty.grid
        else:
            map = self.grid_full.grid
        width = len(map[0]) * GUI_tile_size
        height = len(map) * GUI_tile_size
        visMap = Canvas(self.master, width=width, height=height)
        offset = GUI_tile_size / 2
        if (empty):
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
                if (empty):
                    tile_dict[tile] = visMap.create_rectangle(
                        x1, y1, x2, y2, outline=color, fill=color)
        visMap.pack()
        self.canvas = visMap
        if (empty):
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
        upper_row = int(min(row + index_rad_outer, self.grid_full.num_rows))
        upper_col = int(min(col + index_rad_outer, self.grid_full.num_cols))
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.grid_empty.grid[i][j]
                curr_rec = self.tile_dict[curr_tile]
                x_dist = abs(i - row)
                y_dist = abs(j - col)
                dist = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                if (dist < index_radius_inner):
                    if (curr_tile.isObstacle and not curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ff621f", fill="#ff621f")
                    elif (curr_tile.isBloated):
                        self.canvas.itemconfig(
                            curr_rec, outline="#ffc0cb", fill="#ffc0cb")
                    elif (curr_tile in self.visited_set):
                        self.canvas.itemconfig(
                            curr_rec, outline="#0C9F34", fill="#0C9F34")
                    elif (curr_tile not in self.visited_set):
                        self.canvas.itemconfig(
                            curr_rec, outline="#fff", fill="#fff")
                else:
                    if (
                            curr_tile.isObstacle == False and curr_tile.isBloated == False and curr_tile not in self.visited_set):
                        self.canvas.itemconfig(
                            curr_rec, outline="#545454", fill="#545454")

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
            ## x^2+y^2 = tile_size^2    &&     x/y = x_change/y_change
            y_step = math.sqrt(tile_size ** 2 / (inv_slope ** 2 + 1))
            y_step = y_step
            x_step = math.sqrt((tile_size ** 2 * inv_slope ** 2) / (inv_slope ** 2 + 1))
            x_step = x_step
        if x_change < 0 and x_step > 0:
            x_step = -x_step
        if y_change < 0 and y_step:
            y_step = -y_step

        for i in range(1, num_steps + 1):
            new_coor = (current_loc[0] + i * x_step, current_loc[1] + i * y_step)
            returner.append(new_coor)
            new_tile = self.grid_empty.get_tile(new_coor)
            if new_tile not in self.path_set:
                self.path_set.add(new_tile)

        return returner

    def getPathSet(self):
        """
        """
        prev_tile = self.curr_tile
        for next_tile in self.path:
            if next_tile not in self.path_set:
                self.path_set.add(next_tile)
            self.breakUpLine(prev_tile, next_tile)
            prev_tile = next_tile

    def printTiles(self):
        for row in self.grid_empty.grid:
            for col in row:
                print(str(col.x) + ', ' + str(col.y))

    def checkRecalc(self):
        for x, y in self.broken_path:
            check_tile = self.grid_empty.get_tile((x, y))
            if check_tile.isObstacle or check_tile.isBloated:
                self.recalc = True

    def updateDesiredHeading(self):
        """
        calculates the degrees between the current tile and the next tile and updates desired_heading. Estimates the
        degrees to the nearing int.
        """
        x_change = self.next_tile.x - self.curr_x
        y_change = self.next_tile.y - self.curr_y
        arctan = math.atan(x_change/y_change)
        if x_change > 0 and y_change > 0:
            self.desired_heading = 360-arctan
        elif x_change < 0 and y_change > 0:
            self.desired_heading = -arctan
        else:
            self.desired_heading = 180 - arctan

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion
        """
        # If this is the first tile loop is being iterated through we need to initialize
        if self.init_phase:
            print('IN INIT PHASE')
            curr_tile = self.path[0]
            self.curr_tile = curr_tile
            self.curr_x = self.curr_tile.x
            self.curr_y = self.curr_tile.y

            self.visited_set.add(curr_tile)
            self.getPathSet()
            lidar_data = self.generate_sensor.generateLidar(
                10, curr_tile.row, curr_tile.col)
            self.getPathSet()
            if (self.grid_empty.updateGridLidar(
                    curr_tile.x, curr_tile.y, lidar_data, robot_radius, bloat_factor, self.path_set,
                    self.grid_full)):
                self.recalc = True

            self.next_tile = self.path[1]
            self.broken_path = self.breakUpLine(self.curr_tile, self.next_tile)
            self.updateDesiredHeading()
            self.getPathSet()
            self.broken_path_index = 0
            self.visibilityDraw()

            self.init_phase = False
        elif self.heading == self.desired_heading and self.output_state != "move forward":
            self.output_state = "move forward"
            print(self.output_state)
            # Check to see if we need to turn, and turn if we need to
            # Angles defined as ccw direction is positive
        elif self.heading != self.desired_heading:
            # update output state (done)
            # do not overturn (done)
            # turn the correct direction to minimize turning angle (done)
            # when to update desired heading and how? (done)
            if self.heading < self.desired_heading:
                cw_turn_degrees = 360 + self.heading - self.desired_heading
                ccw_turn_degrees = self.desired_heading - self.heading
            else:
                cw_turn_degrees = self.heading - self.desired_heading
                ccw_turn_degrees = 360 - self.heading + self.desired_heading
            if abs(self.desired_heading - self.heading) < turn_speed:
                self.heading = self.desired_heading
            else:
                if cw_turn_degrees < ccw_turn_degrees:  # turn clockwise
                    self.heading = self.heading - turn_speed
                    print('turn left')
                    self.output_state = "turn right"
                else:  # turn counter clockwise
                    self.heading = self.heading + turn_speed
                    print('turn left')
                    self.output_state = "turn left"
            if self.heading < 0:
                self.heading = 360 + self.heading
            elif self.heading >= 360:
                self.heading = self.heading - 360
            print("heading: " + str(self.heading) + " desired: " + str(self.desired_heading))

        # If we need to iterate through a brokenPath
        elif self.broken_path_index < len(self.broken_path):
            #print('IN BROKEN PATH')
            lidar_data = self.generate_sensor.generateLidar(
                10, self.curr_tile.row, self.curr_tile.col)
            if (self.grid_empty.updateGridLidar(
                    self.curr_tile.x, self.curr_tile.y, lidar_data, robot_radius, bloat_factor, self.path_set,
                    self.grid_full)):
                self.recalc = True
            # Relcalculate the path if needed
            if self.recalc:
                #print('recalculating!')
                dists, self.path = search.a_star_search(
                    self.grid_empty, (self.curr_tile.x, self.curr_tile.y), self.end_point, search.euclidean)
                self.path = search.segment_path(self.grid_empty, self.path)
                self.path_index = 0
                self.smoothed_window.path = self.path
                self.smoothed_window.drawPath()
                self.curr_tile = self.path[0]
                self.next_tile = self.path[1]
                self.broken_path = self.breakUpLine(self.curr_tile, self.next_tile)
                self.updateDesiredHeading()
                self.getPathSet()
                self.visibilityDraw()
                self.path_set = set()
                self.getPathSet()
                self.path_index = 0
                self.broken_path_index = 0
                self.recalc = False
            else:
                x1 = self.broken_path[self.broken_path_index - 1][0]
                y1 = self.broken_path[self.broken_path_index - 1][1]
                x2 = self.broken_path[self.broken_path_index][0]
                y2 = self.broken_path[self.broken_path_index][1]
                # MAYBE CHANGE WIDTH TO SEE IF IT LOOKS BETTER?
                # TODO: CAN I JUST CAST THIS TO INT? DOES THAT LOOSE INFO?
                self.canvas.create_line(int(x1), int(y1), int(x2), int(y2), fill="#339933")
                self.curr_tile = self.grid_empty.get_tile((x2, y2))
                self.visited_set.add(self.curr_tile)

                self.broken_path_index += 1

        # If we have finished iterating through a broken path, we need to go to the
        # Next tile in path, and create a new broken path to iterate through
        else:
            if self.curr_tile == self.grid_empty.get_tile(self.end_point):
                print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
                return
            self.path_set = set()
            self.path_index += 1
            if self.path_index == len(self.path) - 1:
                print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
                return
            self.curr_tile = self.path[self.path_index]
            self.next_tile = self.path[self.path_index + 1]
            self.broken_path = self.breakUpLine(self.curr_tile, self.next_tile)
            self.updateDesiredHeading()
            self.getPathSet()
            self.broken_path_index = 0
            self.visibilityDraw()
        self.master.after(speed_dynamic, self.updateGridSmoothed)

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.smoothed_window = StaticGUI.SmoothedPathGUI(Toplevel(), self.grid_full, self.path)
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
    simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint)
    simulation.runSimulation()


if __name__ == "__main__":
    # staticGridSimulation()
    dynamicGridSimulation()
