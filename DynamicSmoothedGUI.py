import search
from RandomObjects import RandomObjects
import GenerateSensorData
import grid
from tkinter import *
import math
import StaticGUI
from GUI import *
import copy
from Consts import *
from GenerateSensorData import GenerateSensorData


class DynamicGUI(GUI):
    def __init__(self, master, fullMap, emptyMap, path, endPoint, squareList, state):
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
            pathSet {Tile Set} -- set of tiles that have already been drawn (So GUI
                does not draw over the tiles)
            pathIndex {int} -- the index of the path the GUI is at in anumation
            curr_tile {Tile} -- the current tile the robot is at in animation
            grid {Grid} -- the Grid object that the simulation was run on
            squareList -- the list of all the square objects
        """
        # Tinker master, used to create GUI
        super().__init__(master, fullMap, emptyMap, path, squareList, 0)

        self.initPhase = True

        self.brokenPath = None
        self.brokenPathIndex = 0

        self.visitedSet = set()
        for i in self.path:
            self.pathSet.add(i)

        self.recalc = False
        self.stepsSinceRecalc = 0

        self.create_widgets(True)
        self.generate_sensor = GenerateSensorData(
            self.gridFull)

        self.endPoint = endPoint
        self.next_tile = None

        self.obstacleState = state

        # set of tiles that were marked as available path in simulation's previous iteration
        self.last_iter_seen = set()

        # TODO: This is a buggggg..... we must fix the entire coordinate system? change init heading to 0
        self.heading = 180
        # TODO: change to custom type or enum
        self.output_state = "stopped"
        self.desired_heading = None
        self.angle_trace = None
        self.des_angle_trace = None

        self.robot_tile_set = set()

    def visibilityDraw(self, lidar_data):
        """Draws a circle of visibility around the robot
        """
        # coloring all tiles that were seen in last iteration light gray
        while self.last_iter_seen:
            curr_rec = self.last_iter_seen.pop()
            self.canvas.itemconfig(
                curr_rec, outline="#C7C7C7", fill="#C7C7C7")  # light gray

        row = self.curr_tile.row
        col = self.curr_tile.col
        index_radius_inner = int(vis_radius / tile_size)
        index_radius_outer = index_radius_inner + 2

        # the bounds for the visibility circle
        lower_row = max(0, row - index_radius_outer)
        lower_col = max(0, col - index_radius_outer)
        upper_row = min(row + index_radius_outer, self.gridFull.num_rows - 1)
        upper_col = min(col + index_radius_outer, self.gridFull.num_cols - 1)

        lidar_data_copy = copy.copy(lidar_data)
        rad_inc = int(GUI_tile_size / 3)  # radius increment to traverse tiles

        def _color_normally(r, angle_rad):
            """
            Colors the tile at the location that is at a distance r at heading angle_rad from robot's current location.
            Colors the tile based on its known attribute (obstacle, bloated, visited, or visible).
            """
            coords = (r * math.sin(angle_rad) + row, r *
                      math.cos(angle_rad) + col)  # (row, col) of tile we want to color
            # make sure coords are in bounds of GUI window
            if (coords[0] >= lower_row) and (coords[0] <= upper_row) \
                    and (coords[1] >= lower_col) and (coords[1] <= upper_col):
                curr_tile = self.gridEmpty.grid[int(coords[0])][int(coords[1])]
                curr_rec = self.tile_dict[curr_tile]
                if curr_tile.isBloated:
                    self.canvas.itemconfig(
                        curr_rec, outline="#ffc0cb", fill="#ffc0cb")  # pink
                elif curr_tile.isObstacle:
                    self.canvas.itemconfig(
                        curr_rec, outline="#ff621f", fill="#ff621f")  # red
                else:
                    self.canvas.itemconfig(
                        curr_rec, outline="#fff", fill="#fff")  # white
                    self.last_iter_seen.add(curr_rec)

        # iterating through 360 degrees surroundings of robot in increments of degree_freq
        for deg in range(0, 360, degree_freq):
            angle_rad = deg * math.pi / 180
            if len(lidar_data_copy) == 0 or lidar_data_copy[0][0] != deg:
                # no object in sight at deg; color everything normally up to visibility radius
                for r in range(0, index_radius_inner, rad_inc):
                    _color_normally(r, angle_rad)
            else:  # obstacle in sight
                # color everything normally UP TO obstacle, and color obstacle red
                for r in range(0, math.ceil(lidar_data_copy[0][1] / tile_size) + rad_inc, rad_inc):
                    _color_normally(r, angle_rad)
                lidar_data_copy.pop(0)

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

    def updateDesiredHeading(self):
        """
        calculates the degrees between the current tile and the next tile and updates desired_heading. Estimates the
        degrees to the nearing int.
        """
        x_change = self.next_tile.x - self.curr_x
        y_change = self.next_tile.y - self.curr_y
        if y_change == 0:
            arctan = 90 if x_change < 0 else -90
        else:
            arctan = math.atan(x_change/y_change) * (180 / math.pi)
        if x_change >= 0 and y_change > 0:
            self.desired_heading = (360-arctan) % 360
        elif x_change < 0 and y_change > 0:
            self.desired_heading = -arctan
        else:
            self.desired_heading = 180 - arctan
        self.desired_heading = round(self.desired_heading)
        # print("updated desired heading to : " + str(self.desired_heading))

    def get_direction_coor(self, curr_x, curr_y, angle):
        """
        returns a coordinate on on the visibility radius at angle [angle] from the robot
        """
        x2 = math.cos(math.radians(angle+90)) * vis_radius + curr_x
        y2 = math.sin(math.radians(angle+90)) * vis_radius + curr_y
        return (x2 / tile_scale_fac, y2 / tile_scale_fac)

    def update_robot_tile_set(self):
        robot_tile_radius = int(robot_radius/ tile_size)

        minXBound = min(max(self.curr_tile.col - robot_tile_radius,0),tile_num_width)
        minYBound = min(max(self.curr_tile.row - robot_tile_radius, 0),tile_num_height)
        self.robot_tile_set = set()
        for i in range(minXBound, minXBound + 2 * robot_tile_radius):
            for j in range(minYBound, minYBound + 2 * robot_tile_radius):
                self.robot_tile_set.add(self.gridEmpty.grid[j][i])


    def draw_line(self, curr_x, curr_y, next_x, next_y):
        """
        Draw a line from the coordinate (curr_x, curr_y) to the coordinate (next_x, next_y)
        """
        self.canvas.create_line(curr_x / tile_scale_fac, curr_y / tile_scale_fac, next_x / tile_scale_fac,
                                next_y / tile_scale_fac, fill="#339933", width=1.5)

    def draw_headings(self):
        """
        Draws a line showing the heading and desired heading of the robot
        """
        self.canvas.delete(self.angle_trace)
        self.canvas.delete(self.des_angle_trace)
        line_coor = self.get_direction_coor(
            self.curr_tile.x, self.curr_tile.y, self.heading)
        self.angle_trace = self.canvas.create_line(self.curr_tile.x / tile_scale_fac, self.curr_tile.y / tile_scale_fac,
                                                   line_coor[0],
                                                   line_coor[1], fill='#FF69B4', width=1.5)
        des_line_coor = self.get_direction_coor(
            self.curr_tile.x, self.curr_tile.y, self.desired_heading)
        self.des_angle_trace = self.canvas.create_line(self.curr_tile.x / tile_scale_fac, self.curr_y / tile_scale_fac,
                                                       des_line_coor[0],
                                                       des_line_coor[1], fill='#FF0000', width=1.5)
        self.canvas.pack()

    def moveDynamic(self, square):
        """
        The function that handles all move of squares
        check if it is a valid move by calling checkBounds
        if valid, return the valid direction
        if invalid, recurse the function to find a valid direction
        """
        rand_nums = []
        for i in range(4):
            for j in range(square.dir_req_list[i]):
                rand_nums.append(i+1)

        rand_num = rand_nums.pop(random.randrange(len(rand_nums)))
        while True:
            if self.canMove(square, rand_num):
                return rand_num
            else:
                filter(lambda el: el != rand_num, rand_nums)
            if len(rand_nums) == 0:
                curr_tile = self.gridEmpty[square.x][square.y]
                curr_rec = self.tile_dict[curr_tile]
                self.canvas.itemconfig(
                    curr_rec, outline="#ff0000", fill="#ff0000")  # pink
                print('cant move object located at: ' + str(square.x) + ', ' + str(square.y))
                return -1
            rand_num = rand_nums.pop(random.randrange(len(rand_nums)))

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion
        """
        # try:
        if self.obstacleState == "dynamic":
            for i in range(0, len(self.squareList)):
                direc = self.moveDynamic(self.squareList[i])
                if direc != -1:
                    self.move(self.squareList[i], direc)
                    self.smoothed_window.move(self.squareList[i], direc)
        # If this is the first tile loop is being iterated through we need to initialize
        if self.desired_heading is not None and self.heading == self.desired_heading:
            self.draw_headings()
            self.output_state = "move forward"
            print(self.output_state)

        if self.desired_heading is not None and self.heading != self.desired_heading:
            self.draw_headings()
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
                    print('turn right')
                    self.output_state = "turn left"
            if self.heading < 0:
                self.heading = 360 + self.heading
            elif self.heading >= 360:
                self.heading = self.heading - 360
            self.master.after(speed_dynamic, self.updateGridSmoothed)

        elif self.initPhase:
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
            self.brokenPath = self.breakUpLine(
                self.curr_tile, self.next_tile)
            self.getPathSet()
            self.brokenPathIndex = 0
            self.visibilityDraw(lidar_data)
            self.updateDesiredHeading()
            self.update_robot_tile_set()
            self.initPhase = False
            self.master.after(speed_dynamic, self.updateGridSmoothed)
            # If we need to iterate through a brokenPath

        elif self.brokenPathIndex < len(self.brokenPath):
            lidar_data = self.generate_sensor.generateLidar(
                degree_freq, self.curr_tile.row, self.curr_tile.col)
            if (self.gridEmpty.updateGridLidar(
                    self.curr_tile.x, self.curr_tile.y, lidar_data, robot_radius, bloat_factor, self.pathSet,
                    self.gridFull)):
                self.recalc = True
            # Relcalculate the path if needed
            if self.recalc:
                # print('recalculating!')
                dists, self.path = search.a_star_search(
                    self.gridEmpty, (self.curr_tile.x, self.curr_tile.y), self.endPoint, search.euclidean)
                self.path = search.segment_path(self.gridEmpty, self.path)
                self.pathIndex = 0
                self.smoothed_window.path = self.path
                self.smoothed_window.drawPath()
                self.draw_line(self.curr_x, self.curr_y,
                               self.path[0].x, self.path[0].y)
                self.curr_tile = self.path[0]
                self.curr_x = self.curr_tile.x
                self.curr_y = self.curr_tile.y
                self.next_tile = self.path[1]
                self.brokenPath = self.breakUpLine(
                    self.curr_tile, self.next_tile)
                self.updateDesiredHeading()
                self.getPathSet()
                self.visibilityDraw(lidar_data)
                self.update_robot_tile_set()
                self.pathSet = set()
                self.getPathSet()
                self.pathIndex = 0
                self.brokenPathIndex = 0
                self.recalc = False
            else:
                if self.brokenPathIndex == 0:
                    x1 = self.curr_x
                    y1 = self.curr_y
                else:
                    x1 = self.brokenPath[self.brokenPathIndex - 1][0]
                    y1 = self.brokenPath[self.brokenPathIndex - 1][1]
                x2 = self.brokenPath[self.brokenPathIndex][0]
                y2 = self.brokenPath[self.brokenPathIndex][1]
                # MAYBE CHANGE WIDTH TO SEE IF IT LOOKS BETTER?
                self.draw_line(x1, y1, x2, y2)
                self.curr_x = x2
                self.curr_y = y2
                self.curr_tile = self.gridEmpty.get_tile((x2, y2))
                self.visitedSet.add(self.curr_tile)
                self.update_robot_tile_set()
                self.visibilityDraw(lidar_data)
                self.brokenPathIndex += 1

            self.master.after(speed_dynamic, self.updateGridSmoothed)

        # If we have finished iterating through a broken path, we need to go to the
        # Next tile in path, and create a new broken path to iterate through
        else:
            lidar_data = self.generate_sensor.generateLidar(
                degree_freq, self.curr_tile.row, self.curr_tile.col)
            if self.curr_tile == self.gridEmpty.get_tile(self.endPoint):
                print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
                return
            self.pathSet = set()
            self.pathIndex += 1
            if self.pathIndex == len(self.path) - 1:
                print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
                return

            self.draw_line(
                self.curr_x, self.curr_y, self.path[self.pathIndex].x, self.path[self.pathIndex].y)
            self.curr_tile = self.path[self.pathIndex]
            self.curr_x = self.curr_tile.x
            self.curr_y = self.curr_tile.y
            self.next_tile = self.path[self.pathIndex+1]
            self.brokenPath = self.breakUpLine(
                self.curr_tile, self.next_tile)
            self.getPathSet()
            self.brokenPathIndex = 0
            self.visibilityDraw(lidar_data)
            self.update_robot_tile_set()
            self.updateDesiredHeading()
            self.master.after(speed_dynamic, self.updateGridSmoothed)
        # except Exception as e:
        #     print(e)
        #     print("C1C0: \"There is no path to the desired location. Beep Boop\"")

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.smoothed_window = StaticGUI.SmoothedPathGUI(
            Toplevel(), self.gridFull, self.path, self.squareList)
        self.smoothed_window.drawPath()
        # if self.obstacleState == "dynamic":
        #     for i in range(0, len(self.squareList)):
        #         self.smoothed_window.move(self.squareList[i], self.moveDynamic(self.squareList[i]))
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
        secondNum = float(text[commaIndex + 1:-1])
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


def userInputObstacles():
    text = input(
        "Please enter whether you want dynamic or static obstacles:  ")
    while validUserInputObstacles(text) == "-1":
        print("Your input was MALFORMED")
        text = input(
            "Please enter whether you want dynamic or static obstacles:  ")
    if validUserInputObstacles(text) == "static":
        return "static"
    else:
        return "dynamic"


def validUserInputObstacles(text):
    lowercase_text = text.lower()
    static = lowercase_text.find("static")
    dynamic = lowercase_text.find("dynamic")
    if static != -1:
        return lowercase_text[static: static + 5]
    elif dynamic != -1:
        return lowercase_text[dynamic: dynamic + 6]
    else:
        return "-1"


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
    obstacle = userInputObstacles()
    # Run algorithm to get path
    dists, path = search.a_star_search(
        emptyMap, (midX, midY), endPoint, search.euclidean)
    # start GUI and run animation
    simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(
        emptyMap, path), endPoint, generator.squares, obstacle)
    simulation.runSimulation()


if __name__ == "__main__":
    # staticGridSimulation()
    dynamicGridSimulation()
