import time
import search
from RandomObjects import RandomObjects
import GenerateSensorData
import grid
from tkinter import *
import math
import StaticGUI
import copy
import random
from Tile import *
from GenerateSensorData import GenerateSensorData
from EndpointInput import *
import numpy as np
from PID import *

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
        self.pathIndex = 0
        self.curr_tile = None
        self.prev_tile = None

        self.gridFull = fullMap
        self.gridEmpty = emptyMap

        self.recalc = False
        self.stepsSinceRecalc = 0

        self.create_widgets()
        self.generate_sensor = GenerateSensorData(
            self.gridFull)

        self.endPoint = endPoint
        self.next_tile = None
        self.prev_vector = None

        self.recalc_count = recalc_wait
        self.recalc_cond = False

        self.last_iter_seen = set()  # set of tiles that were marked as available path in simulation's previous iteration

        # TODO: This is a buggggg..... we must fix the entire coordinate system? change init heading to 0
        self.heading = 180
        # TODO: change to custom type or enum
        self.output_state = "stopped"
        self.desired_heading = None
        self.angle_trace = None
        self.des_angle_trace = None
        self.oldError = 0
        self.errorHistory = 0
        self.mean = random.randint(-1, 1)/12.0
        self.standard_deviation = random.randint(0, 1.0)/10.0

        self.prev_draw_c1c0_ids = [None, None]   # previous IDs representing drawing of C1C0 on screen

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
                if tile.is_bloated:
                    color = "#ffc0cb"
                elif tile.is_obstacle:
                    color = "#ffCC99"
                else:
                    color = "#545454"
                if empty:
                    tile_dict[tile] = visMap.create_rectangle(
                        x1, y1, x2, y2, outline=color, fill=color)
        visMap.pack()
        self.canvas = visMap
        if (empty):
            self.tile_dict = tile_dict

    def calc_dist(self):
        """
        returns the perpendicular distance from c1c0's current value to the line that c1c0 should be travelling on
        """
        #(y2-y1)x-(x2-x1)y=(y2-y1)x1-(x2-x1)y1
        #C = x2y1-x1y2
        b = self.path[self.pathIndex + 1].x - self.path[self.pathIndex].x
        a = self.path[self.pathIndex + 1].y - self.path[self.pathIndex].y
        #c = self.path[self.pathIndex + 1].x * self.path[self.pathIndex].y \
        #    - self.path[self.pathIndex].x * self.path[self.pathIndex + 1].y
        den = 0
        if a != 0 and b != 0:
            den = (b/a) +(a/b)
        d = 0
        if den != 0:
            c = self.path[self.pathIndex].y - (a/b)*self.path[self.pathIndex].x
            x = (self.curr_y + (b/a)*self.curr_x - self.path[self.pathIndex].y + (a/b) *
                 self.path[self.pathIndex].x)/den
            y = (a/b)*x + c
            d = ((x - self.curr_x)**2 + (y - self.curr_y)**2)**(1/2)
        return d

    def PID(self):
        """
        returns the control value function for the P, I, and D terms
        """
        error = self.calc_dist()
        der = error - self.oldError
        self.oldError = error
        self.errorHistory += error
        return (error * gaine) + (der * gaind) + (self.errorHistory * gainI)

    def newVec(self):
        """
        return the new velocity vector based on the PID value
        """
        velocity = (self.curr_x - self.prev_x, self.curr_y - self.prev_y)
        mag = (velocity[0]**2 + velocity[1]**2)**(1/2)
        perpendicular = (0, 0)
        if mag > 0:
            perpendicular = (-velocity[1]/mag, velocity[0]/mag)
        c = self.PID()
        return [c * a + b for a, b in zip(perpendicular, velocity)]

    def calcVector(self):
        """
        Returns the vector between the current location and the end point of the current line segment
        and draws this vector onto the canvas
        """
        vect = (0, 0)
        if self.pathIndex + 1 < len(self.path):
            if self.pathIndex == 0:
                x_diff = self.path[1].x - self.path[0].x
                y_diff = self.path[1].y - self.path[0].y
                vect = (x_diff, y_diff)
            else:
                pid = PID(self.path, self.pathIndex + 1, self.curr_x, self.curr_y, self.prev_x, self.prev_y)
                vect = pid.newVec()
            if self.prev_vector is not None:
                # delete old drawings from previous iteration
                self.canvas.delete(self.prev_vector)

            mag = (vect[0]**2 + vect[1]**2)**(1/2)
            norm_vect = (int(vector_draw_length * (vect[0] / mag)), int(vector_draw_length * (vect[1] / mag)))
            end = self._scale_coords((self.curr_x + norm_vect[0], self.curr_y + norm_vect[1]))
            start = self._scale_coords((self.curr_x, self.curr_y))
            self.prev_vector = self.canvas.create_line(
                start[0], start[1], end[0], end[1], arrow='last', fill='red')
            # self.canvas.tag_raise(self.prev_vector)
        return vect

    def visibilityDraw(self, lidar_data):
       """Draws a circle of visibility around the robot
       """
       # coloring all tiles that were seen in last iteration light gray
       while self.last_iter_seen:
           curr_rec = self.last_iter_seen.pop()
           self.canvas.itemconfig(curr_rec, outline="#C7C7C7", fill="#C7C7C7")  # light gray

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
               if curr_tile.is_bloated:
                   self.canvas.itemconfig(
                       curr_rec, outline="#ffc0cb", fill="#ffc0cb")  # pink
               elif curr_tile.is_obstacle:
                   self.canvas.itemconfig(
                       curr_rec, outline="#ff621f", fill="#ff621f")  # red
               else:
                   self.canvas.itemconfig(curr_rec, outline="#fff", fill="#fff")  # white
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

    def _scale_coords(self, coords):
        """scales coords (a tuple (x, y)) from real life cm to pixels"""
        scaled_x = coords[0] / tile_scale_fac
        scaled_y = coords[1] / tile_scale_fac
        return scaled_x, scaled_y

    def drawC1C0(self):
        """Draws C1C0's current location on the simulation"""

        # coordinates of robot center right now (in cm)
        center_x = self.curr_x
        center_y = self.curr_y

        # converting heading to radians, and adjusting so that facing right = 0 deg
        heading_adj_rad = math.radians(self.heading + 90)

        if self.prev_draw_c1c0_ids is not None:
            # delete old drawings from previous iteration
            self.canvas.delete(self.prev_draw_c1c0_ids[0])
            self.canvas.delete(self.prev_draw_c1c0_ids[1])
        # coordinates of bounding square around blue circle
        top_left_coords = (center_x - robot_radius, center_y + robot_radius)
        bot_right_coords = (center_x + robot_radius, center_y - robot_radius)
        # convert coordinates from cm to pixels
        top_left_coords_scaled = self._scale_coords(top_left_coords)
        bot_right_coords_scaled = self._scale_coords(bot_right_coords)

        # draw blue circle
        self.prev_draw_c1c0_ids[0] = self.canvas.create_oval(
            top_left_coords_scaled[0], top_left_coords_scaled[1],
            bot_right_coords_scaled[0], bot_right_coords_scaled[1],
            outline='black', fill='blue')

        center_coords_scaled = self._scale_coords((center_x, center_y))

        # finding endpoint coords of arrow
        arrow_end_x = center_x + robot_radius * math.cos(heading_adj_rad)
        arrow_end_y = center_y + robot_radius * math.sin(heading_adj_rad)
        arrow_end_coords_scaled = self._scale_coords((arrow_end_x, arrow_end_y))

        # draw white arrow
        self.prev_draw_c1c0_ids[1] = self.canvas.create_line(
            center_coords_scaled[0], center_coords_scaled[1],
            arrow_end_coords_scaled[0], arrow_end_coords_scaled[1], arrow='last', fill='white'
        )


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
            x_step = math.sqrt((tile_size ** 2 * inv_slope ** 2) / (inv_slope ** 2 + 1))
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
            if check_tile.is_obstacle or check_tile.is_bloated:
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
        line_coor = self.get_direction_coor(self.curr_x, self.curr_y, self.heading)
        self.angle_trace = self.canvas.create_line(self.curr_x / tile_scale_fac, self.curr_y / tile_scale_fac,
                                                   line_coor[0],
                                                   line_coor[1], fill='#FF69B4', width=1.5)
        des_line_coor = self.get_direction_coor(self.curr_x, self.curr_y, self.desired_heading)
        self.des_angle_trace = self.canvas.create_line(self.curr_x / tile_scale_fac, self.curr_y / tile_scale_fac,
                                                       des_line_coor[0],
                                                       des_line_coor[1], fill='#FF0000', width=1.5)
        self.canvas.pack()

    def init_phase(self):
        curr_tile = self.path[0]
        self.prev_tile = self.curr_tile
        self.curr_tile = curr_tile
        self.curr_x = self.curr_tile.x
        self.curr_y = self.curr_tile.y
        self.prev_x = self.curr_tile.x
        self.prev_y = self.curr_tile.y

        self.visitedSet.add(curr_tile)
        self.getPathSet()
        lidar_data = self.generate_sensor.generateLidar(
            degree_freq, curr_tile.row, curr_tile.col)
        self.getPathSet()
        self.recalc = self.gridEmpty.update_grid_tup_data(self.curr_x,
                                                       self.curr_y, lidar_data, Tile.lidar, robot_radius, bloat_factor,
                                                       self.pathSet)
        self.next_tile = self.path[1]
        self.brokenPath = self.breakUpLine(self.curr_tile, self.next_tile)
        self.getPathSet()
        self.brokenPathIndex = 0
        self.visibilityDraw(lidar_data)
        self.updateDesiredHeading()

        self.master.after(fast_speed_dynamic, self.updateGridSmoothed)

    def turn(self):
        while self.desired_heading is not None and self.heading != self.desired_heading:
            self.drawC1C0()
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
            time.sleep(.001 * fast_speed_dynamic)

    def recalculate_path(self, lidar_data):
        self.path = search.a_star_search(
            self.gridEmpty, (self.curr_tile.x, self.curr_tile.y), self.endPoint, search.euclidean)
        self.path = search.segment_path(self.gridEmpty, self.path)
        self.pathIndex = 0
        self.smoothed_window.path = self.path
        self.smoothed_window.drawPath()
        self.draw_line(self.curr_x, self.curr_y, self.path[0].x, self.path[0].y)
        self.prev_tile = self.curr_tile
        self.curr_tile = self.path[0]
        self.next_tile = self.path[1]
        self.updateDesiredHeading()
        self.getPathSet()
        self.visibilityDraw(lidar_data)
        self.pathSet = set()
        self.getPathSet()
        self.pathIndex = 0
        self.recalc = False
        self.recalc_count = 0
        self.recalc_cond = False

    def step(self, lidar_data):
        """
        steps in the direction of the vector
        """
        vec = self.calcVector()
        mag = math.sqrt(vec[0]**2 + vec[1]**2)
        error = np.random.normal(self.mean, self.standard_deviation)
        norm_vec = (10*vec[0]/mag, 10*vec[1]/mag)
        norm_vec = (norm_vec[0] * math.cos(error) - norm_vec[1] * math.sin(error), norm_vec[0] * math.sin(error) + norm_vec[1] * math.cos(error))

        x2 = self.curr_x + norm_vec[0]
        y2 = self.curr_y + norm_vec[1]
        self.draw_line(self.curr_x, self.curr_y, x2, y2)
        self.prev_x = self.curr_x
        self.prev_y = self.curr_y
        self.curr_x = x2
        self.curr_y = y2
        self.prev_tile = self.curr_tile
        self.curr_tile = self.gridEmpty.get_tile((x2, y2))
        self.visitedSet.add(self.curr_tile)
        self.visibilityDraw(lidar_data)
        self.drawC1C0()
        self.recalc_count += 1

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion
        """
        if self.curr_tile == self.gridEmpty.get_tile(self.endPoint):
            print('C1C0 has ARRIVED AT THE DESTINATION, destination tile')
            return
        self.drawC1C0()
        self.turn()
        lidar_data = self.generate_sensor.generateLidar(
                degree_freq, self.curr_tile.row, self.curr_tile.col)
        self.recalc = self.gridEmpty.update_grid_tup_data(self.curr_x,
                                                           self.curr_y, lidar_data, Tile.lidar, robot_radius, bloat_factor,
                                                           self.pathSet)

        self.recalc_cond = self.recalc_cond or self.recalc or self.curr_tile.is_obstacle
        # if we need to recalculate then recurse
        if self.recalc_cond and self.recalc_count >= recalc_wait:
            self.recalculate_path(lidar_data)
        elif self.curr_tile == self.path[self.pathIndex + 1]:
            self.mean = random.randint(-1, 1)/12.0
            self.standard_deviation = random.randint(0, 1)/10.0
            self.pathIndex += 1
            self.next_tile = self.path[self.pathIndex+1]
            self.updateDesiredHeading()
        else:
            self.step(lidar_data)
        self.master.after(fast_speed_dynamic, self.updateGridSmoothed)

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.smoothed_window = StaticGUI.SmoothedPathGUI(Toplevel(), self.gridFull, self.path)
        self.smoothed_window.drawPath()
        self.init_phase()
        self.master.mainloop()

    def generate_error(self, vec):
        """
        Returns a new vector with error in the step
        """
        raise(NotImplementedError)
        return new_vec

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

def dynamicGridSimulation(text_file: str):
    emptyMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    fullMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates random enviroment on the grid
    generator = RandomObjects(fullMap)

    # You can change the number of every type of object you want
    if text_file == '':
        generator.create_env(22, 0, 0, 22, 9)
    else:
        generator.create_env_json(text_file)

    # starting location for middle
    midX = tile_size * tile_num_width / 2
    midY = tile_size * tile_num_height / 2

    # Calculate and point and change coordinate system from user inputted CICO @(0,0) to the grid coordinates
    endPoint = userInput()
    # Run algorithm to get path
    path = search.a_star_search(
        emptyMap, (midX, midY), endPoint, search.euclidean)
    # start GUI and run animation
    simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint)
    simulation.runSimulation()


def seededSimulation():
    text_file = input("Please enter the name of the text file that contains the json of obstacles, or hit enter to use a random "
                      "environment seed: ")
    if text_file.find('txt') == -1:
        text_file = ''
        try:
            x = int(input("Please enter a seed (1 to 10^9): "))
            random.seed(x)
            print("The seed is " + str(x))
        except:
            x = random.randint(1, 10**9)
            print("That didn't work. The seed is " + str(x))
            random.seed(x)
    dynamicGridSimulation(text_file)


if __name__ == "__main__":
    # staticGridSimulation()
    seededSimulation()
