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

        self.brokenPath = None
        self.brokenPathIndex = 0

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

    def BreakUpLine(self, next_tile: grid.Tile):
        """ breaks up a line into many consective endpoints and 
        puts them in a list

        Args:
            next_tile ([Tile]): next tile that should be visited

        Returns:
            [point list]: [a list of tile coordinates to visit in the form 
        [(x1,y1),(x2,y2),(x3,y3)...]]
        """
        current_loc = (self.curr_tile.x, self.curr_tile.y)
        next_loc = (next_tile.x, next_tile.y)
        # calculate the slope, rise/run
        x_change = next_loc[0]-current_loc[0]
        y_change = next_loc[1]-current_loc[1]
        slope = y_change/x_change
        dist = search.euclidean([current_loc, next_loc])

        if(dist<tile_size):
            return [(current_loc[0]+x_change, current_loc[1]+y_change)]

        num_steps = dist/tile_size
        returner = []

        for i in range(1,num_steps+1):
            new_coor = (current_loc[0] + i*tile_size,current_loc[1] + i*tile_size)
            returner.append(new_coor)
            self.pathSet.add(self.gridEmpty.get_tile(new_coor))

        return returner

            

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion  
        """
        ##check if we have iterated through the path
        if(self.pathIndex!=-1):
            ##If this is the first tile loop is being iterated through we need to initialize 
            if(self.pathIndex == len(self.path)-1):
                curr_tile = self.path[self.pathIndex]
                self.curr_tile = curr_tile
                self.visitedSet.add(curr_tile)
                lidar_data = self.generate_sensor.generateLidar(
                    10, curr_tile.row, curr_tile.col)
                if(self.gridEmpty.updateGridLidar(
                        curr_tile.x, curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet, self.gridFull)):
                    self.recalc = True

                self.visibilityDraw()
                #self.canvas.itemconfig(
                    #curr_rec, outline="#00FF13", fill="#00FF13")

                self.pathIndex = self.pathIndex-1
                self.stepsSinceRecalc = self.stepsSinceRecalc+1
                self.master.after(speed_dynamic, self.updateGridSmoothed)
            ##If no brokePath has been calculated yet, break up the path and update
            elif(self.brokenPath is None):
                self.brokenPath = self.BreakUpLine(curr_tile)
                self.brokenPathIndex=0
                self.visibilityDraw()
                self.master.after(speed_dynamic, self.updateGridSmoothed)
            ##If we need to iterate through a brokenPath
            elif(self.brokenPathIndex<len(self.brokenPath)):
                self.brokenPathIndex+=1
                x1 = self.brokenPath[self.brokenPathIndex-1][0] / tile_scale_fac
                y1 = self.brokenPath[self.brokenPathIndex-1][1] / tile_scale_fac
                x2 = self.brokenPath[self.brokenPathIndex][0] / tile_scale_fac
                y2 = self.brokenPath[self.brokenPathIndex][1] / tile_scale_fac
                ##MAYBE CHANGE WIDTH TO SEE IF IT LOOKS BETTER?
                self.canvas.create_line(x1, y1, x2, y2, fill="#339933")
                
                curr_tile = self.gridEmpty.get_tile(x2,y2)
                self.curr_tile = curr_tile
                self.visitedSet.add(curr_tile)
                lidar_data = self.generate_sensor.generateLidar(
                    10, curr_tile.row, curr_tile.col)
                if(self.gridEmpty.updateGridLidar(
                        curr_tile.x, curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet, self.gridFull)):
                    self.recalc = True

                self.visibilityDraw()
                ##Relcalculate the path if needed
                if(self.recalc):
                    print('recalculating!')
                    start = (curr_tile.x, curr_tile.y)

                    dists, self.path = search.a_star_search(
                        self.gridEmpty, start, self.endPoint, search.euclidean)
                    self.path = search.segment_path(self.path)
                    self.pathSet = set()
                    for i in self.path:
                        self.pathSet.add(i)
                    self.pathIndex = len(self.path)-1
                    self.brokenPath=None
                    self.brokenPathIndex=0
                    self.recalc = False
                    self.stepsSinceRecalc = 0

                self.stepsSinceRecalc = self.stepsSinceRecalc+1
                self.master.after(speed_dynamic, self.updateGridSmoothed)

        ##If we have finished iterating through a broken path, we need to go to the
        ##Next tile in path, and create a new broken path to iterate through
        else:
            self.brokenPath=None
            self.brokenPathIndex=0

            self.visibilityDraw()
            #self.canvas.itemconfig(
                #curr_rec, outline="#00FF13", fill="#00FF13")

            self.pathIndex = self.pathIndex-1
            self.master.after(speed_dynamic, self.updateGridSmoothed)

        self.path = search.segment_path_dyanmic(self.gridEmpty, self.path)
        self.master.after(speed_dynamic, self.updateGridSmoothed)

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        top = Toplevel()
        newGUI = StaticGUI.MapPathGUI(top, self.gridFull, [])
        self.updateGridSmoothed()
        self.master.mainloop()

def validLocation(text)->int:
    """
    takes in text and outputs 1 if the text is a valid location on the grid,
    ouptuts a 2 if the location is outside of the grid
    outputs a 3 if the location text is malformed
    """
    try:
        commaIndex = text.find(',')
        firstNum=int(text[1:commaIndex])
        print(firstNum)
        secondNum=int(text[commaIndex+1:-1])
        print(secondNum)
        if(firstNum>tile_size*tile_num_width/2 or firstNum <-(tile_size*tile_num_width/2)):
            return 2
        if(secondNum>tile_size*tile_num_height/2 or secondNum<-(tile_size*tile_num_height/2)):
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

def getLocation(text: str)->(int,int):
    """
    Precondion: String is a valid string of the form (int,int)
    Returns parsed string in the form of an int tuple
    """
    commaIndex = text.find(',')
    firstNum=int(text[1:commaIndex])
    secondNum=int(text[commaIndex+1:-1])
    #convert from meters to cm
    firstNum=int(firstNum*100)
    secondNum=int(secondNum*100)
    firstNum=firstNum+tile_num_width*tile_size/2
    secondNum=-secondNum+tile_num_height*tile_size/2
    return (firstNum,secondNum)

def userInput():
    printScreen()

    text = input("Please enter the coordinate you desire CICO to go to in the form (x,y):  ")
    #ending location
    while(validLocation(text)!=1):
        if(validLocation(text)==2):
            print("Your location was OUT OF THE RANGE of the specified grid")
            text = input("Please enter the coordinate you desire CICO to go to in the form (x,y):  ")

        elif(validLocation(text)==3):
            print("Your location input was MALFORMED")
            text = input("Please enter the coordinate you desire CICO to go to in the form (x,y): ")

    return getLocation(text)
    
def validLocation(text)->int:
    """
    takes in text and outputs 1 if the text is a valid location on the grid,
    ouptuts a 2 if the location is outside of the grid
    outputs a 3 if the location text is malformed
    """
    try:
        commaIndex = text.find(',')
        firstNum=int(text[1:commaIndex])
        secondNum=int(text[commaIndex+1:-1])
        if(firstNum>tile_size*tile_num_width/2 or firstNum <-(tile_size*tile_num_width/2)):
            return 2
        if(secondNum>tile_size*tile_num_height/2 or secondNum<-(tile_size*tile_num_height/2)):
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
    generator.create_env(20, 0, 0, 20, 7)

    #starting location for middle
    midX = tile_size*tile_num_width/2
    midY = tile_size*tile_num_height/2

    #Calculate and point and change coordinate system from user inputted CICO @(0,0) to the grid coordinates
    endPoint=userInput()

    # Run algorithm to get path
    dists, path = search.a_star_search(
        emptyMap, (midX, midY), endPoint, search.euclidean)
    # start GUI and run animation
    simulation = DynamicGUI(Tk(), fullMap, emptyMap, path, endPoint)
    simulation.runSimulation()


if __name__ == "__main__":
    # staticGridSimulation()
    dynamicGridSimulation()

