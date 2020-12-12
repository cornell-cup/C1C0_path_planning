import search
from RandomObjects import RandomObjects
import GenerateSensorData
import grid
from tkinter import *
import math
import StaticGUI
import copy
from Consts import *
from GenerateSensorData import GenerateSensorData


class DynamicGUI():
    def __init__(self, master, fullMap, emptyMap, path, endPoint, desired_heading):
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

        self.last_iter_seen = set()  # set of tiles that were marked as available path in simulation's previous iteration

        # TODO: This is a buggggg..... we must fix the entire coordinate system? change init heading to 0
        self.heading = 180
        # TODO: change to custom type or enum
        self.output_state = "stopped"
        self.desired_heading = desired_heading
        self.angle_trace = None
        self.des_angle_trace = None
        self.just_turn = desired_heading

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
        if (empty):
            self.tile_dict = tile_dict

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
       upper_row = min(row + index_radius_outer, self.gridFull.num_rows)
       upper_col = min(col + index_radius_outer, self.gridFull.num_cols)

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
            if check_tile.isObstacle or check_tile.isBloated:
                self.recalc = True

    def updateDesiredHeading(self):
        """
        calculates the degrees between the current tile and the next tile and updates desired_heading. Estimates the
        degrees to the nearing int.
        """
        if self.just_turn != 0:
            self.desired_heading = self.just_turn
        else:
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
        if(self.curr_tile == None):
            self.curr_tile = self.gridEmpty.grid[int(tile_num_width/2)][int(tile_num_height/2)]
        line_coor = self.get_direction_coor(self.curr_tile.x, self.curr_tile.y, self.heading)
        self.angle_trace = self.canvas.create_line(self.curr_tile.x / tile_scale_fac, self.curr_tile.y / tile_scale_fac,
                                                   line_coor[0],
                                                   line_coor[1], fill='#FF69B4', width=1.5)
        des_line_coor = self.get_direction_coor(self.curr_tile.x, self.curr_tile.y, self.desired_heading)
        self.des_angle_trace = self.canvas.create_line(self.curr_tile.x / tile_scale_fac, self.curr_tile.y / tile_scale_fac,
                                                       des_line_coor[0],
                                                       des_line_coor[1], fill='#FF0000', width=1.5)
        self.canvas.pack()

    def updateGridSmoothed(self):
        """
        updates the grid in a smoothed fashion
        """
        try:
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
                    if self.just_turn != 0:
                        print("C1C0 has turned to face the correct angle")
                        return
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
                if self.desired_heading == self.heading and self.just_turn!=0:
                    self.draw_headings()
                    print("C1C0 has turned to face the correct angle")
                    return
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
                if self.path is not None and len(self.path) > 1:
                    self.next_tile = self.path[1]
                    self.brokenPath = self.breakUpLine(self.curr_tile, self.next_tile)
                    self.getPathSet()
                    self.brokenPathIndex = 0
                    self.visibilityDraw(lidar_data)
                    self.updateDesiredHeading()

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
                    self.draw_line(self.curr_x, self.curr_y, self.path[0].x, self.path[0].y)
                    self.curr_tile = self.path[0]
                    self.curr_x = self.curr_tile.x
                    self.curr_y = self.curr_tile.y
                    self.next_tile = self.path[1]
                    self.brokenPath = self.breakUpLine(self.curr_tile, self.next_tile)
                    self.updateDesiredHeading()
                    self.getPathSet()
                    self.visibilityDraw(lidar_data)
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

                self.draw_line(self.curr_x, self.curr_y, self.path[self.pathIndex].x, self.path[self.pathIndex].y)
                self.curr_tile = self.path[self.pathIndex]
                self.curr_x = self.curr_tile.x
                self.curr_y = self.curr_tile.y
                self.next_tile = self.path[self.pathIndex+1]
                self.brokenPath = self.breakUpLine(self.curr_tile, self.next_tile)
                self.getPathSet()
                self.brokenPathIndex = 0
                self.visibilityDraw(lidar_data)
                self.updateDesiredHeading()
                self.master.after(speed_dynamic, self.updateGridSmoothed)
        except Exception as e:
            print(e)
            print("C1C0: \"There is no path to the desired location. Beep Boop\"")

    def runSimulation(self):
        """Runs a sumulation of this map, with its enviroment and path
        """
        self.smoothed_window = StaticGUI.SmoothedPathGUI(Toplevel(), self.gridFull, self.path)
        self.smoothed_window.drawPath()
        self.updateGridSmoothed()
        self.master.mainloop()

