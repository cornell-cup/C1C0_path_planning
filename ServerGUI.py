import copy
import sys
import time
import math
import numpy as np
from typing import Dict
from Networks.Server import *
import Grid_Classes.grid as grid
from tkinter import *
from Grid_Classes import search
from Grid_Classes.Tile import *
from Controls.PID import *
from Indoor_GPS.GPS import GPS
from SensorCode import SensorState


class ServerGUI:
    """
    Master file to run autonomous path planning and display visualization real-time
    Instance Attributes:
        master (Tk): Tkinter GUI object
        canvas (Canvas): Tkinter Canvas that represents the GUI
        tile_dict (Dict[Tile, Rectangle]): Mapping from tiles to rectangles on GUI
        grid (Grid): grid that represents the environment
        heading (int): integer to represent the angle that the robot is facing
    """

    def __init__(self, input_server, init_input=None, generateLidar=None, error=0):
        self.error = error
        self.debug = False # use the termination time limit
        self.run_mock = init_input is not None
        self.sensor_state = SensorState(False)
        self.master: Tk = Tk()
        self.canvas: Canvas = None
        self.tile_dict: Dict[Tile, int] = None
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.last_iter_seen = set()
        try:
            with open("heading_data.txt", "r") as file:
                s = file.readline().strip()
                # self.base_heading = int(s)
                self.base_heading = 0
        except FileNotFoundError:
            self.base_heading = 0
        self.heading: int = self.base_heading
        self.curr_tile = self.grid.grid[int(
            self.grid.num_rows/2)][int(self.grid.num_cols/2)]
        self.curr_pos = (self.curr_tile.x, self.curr_tile.y)
        # planned path of tiles
        self.prev_draw_c1c0_ids = [None, None]
        self.create_widgets()
        self.server = input_server

        if generateLidar is None:
            receive_data = self.server.receive_data_init()

        # print(receive_data)
        self.count = 0

        if generateLidar is None:
            self.processEndPoint(receive_data['end_point'])
        else:
            self.endPoint = init_input
            self.desired_heading = self.heading

        print("endpoint: " + str(self.endPoint))
        self.expiry_time = time.time() + 30 # finish after x seconds
        #print('got the end point to be, ', self.endPoint)
        self.path = search.a_star_search(
            self.grid, (self.curr_pos[0], self.curr_pos[1]), self.endPoint, search.euclidean)
        self.path = search.segment_path(self.grid, self.path)
        self.path_set = set()
        self.generatePathSet()
        self.pathIndex = 0
        self.prev_tile = None
        self.prev_pos = None
        self.prev_vector = None
        self.way_point = None
        self.loop_it = 0

        self.prev_line_id = []
        self.set_of_prev_path = []
        self.color_list = ['#2e5200', '#347800',
                           '#48a600', '#54c200', '#60de00', 'None']
        self.index_fst_4 = 0
        self.drawPath()

        # print("initialize cur_tile: " + str(self.curr_tile))
        # print("first tile on path: " + str(self.path[self.pathIndex]))
        self.pid = PID(self.path, self.pathIndex,
                       self.curr_pos[0], self.curr_pos[1])
        self.calcVector()

        self.drawWayPoint(self.path[self.pathIndex])
        print('init draw waypoint')
        self.updateDesiredHeading(self.path[self.pathIndex], (self.path[self.pathIndex].x, self.path[self.pathIndex].y))
        self.gps = GPS(self.grid, self.pid)
        self.prev_tile, self.curr_tile = self.gps.update_loc(self.curr_tile)
        self.global_time = time.time()
        self.enclosed = False
        self.t = time.time()
        print(f'beginning desired heading: {self.desired_heading}')
        self.main_loop(lidarGenerate=generateLidar)
        self.master.mainloop()
        if self.curr_tile == self.path[-1]:
            print("Reached endpoint")
            # self.hedge.stop()
        print("ended master mainloop")

    def processEndPoint(self, endPoint):
        """
        Processes the endpoint and returns the corresponding tuple.
        Input examples:
            ("move forward", m) where m is in meters
            ("turn", deg) where deg is positive for clockwise turns, negative for counterclockwise
            (x, y) where x and y are coordinates to move to 
        Updates self.endPoint to be the final coordinates to move to,
        and updates self.desired_heading
        """
        #    firstNum = firstNum + tile_num_width * tile_size / 2
        #    secondNum = -secondNum + tile_num_height * tile_size / 2
        start = endPoint.find("(")
        comma = endPoint.find(",")
        end = endPoint.find(")")
        processedEndPoint = (
            endPoint[start+1:comma], float(endPoint[comma+2:end]))
        """
        print(
            f"EndPoint[0]: {processedEndPoint[0]}    EndPoint[1]: {processedEndPoint[1]}")
        """
        if processedEndPoint[0] == "'move forward'":
            self.endPoint = (self.curr_tile.x,
                             self.curr_tile.y + processedEndPoint[1] * 100 * tile_unit_per_cent)
            self.desired_heading = self.heading
        elif processedEndPoint[0] == "'turn'":
            self.endPoint = (self.curr_tile.x, self.curr_tile.y)
            self.desired_heading = self.heading + processedEndPoint[1]
            #print(f"Ang[0]: {self.heading}    Ang[1]: {self.desired_heading}")
        else:
            self.endPoint = (self.curr_tile.x - int(processedEndPoint[0]) * 100 * tile_unit_per_cent,
                             self.curr_tile.y + processedEndPoint[1] * 100 * tile_unit_per_cent)
            self.desired_heading = self.heading

    def create_widgets(self):
        """
        Creates the canvas of the size of the inputted grid
        """
        self.master.geometry("+900+100")
        canvas = Canvas(self.master, width=len(self.grid.grid[0]) * GUI_tile_size,
                        height=len(self.grid.grid) * GUI_tile_size)
        offset = GUI_tile_size / 2
        tile_dict = {}
        for row in self.grid.grid:
            for tile in row:
                x = tile.x / tile_scale_fac
                y = tile.y / tile_scale_fac
                tile_dict[tile] = canvas.create_rectangle(
                    x - offset, y - offset, x + offset, y + offset, outline=tile.get_color(), fill=tile.get_color())
        canvas.pack()
        self.canvas = canvas
        self.tile_dict = tile_dict

    def nextLoc(self):
        """
		Returns true if robot is within correct distance bound AND is facing the right way
        """
        next_tile = self.path[self.pathIndex]
        d = math.sqrt((self.curr_pos[0] - next_tile.x)**2 +
                      (self.curr_pos[1] - next_tile.y)**2)
        print(f"d : {d}, diff heading: {(abs(self.heading - self.desired_heading) + 360) % 360}")
        return d <= reached_tile_bound and (abs(self.heading - self.desired_heading) + 360) % 360 <= 5

    def updateDesiredHeading(self, next_tile, pos):
        """
        Calculates the degrees between the current tile and the next tile and updates desired_heading. Estimates the
        degrees to the nearing int.
        """

        x_change = pos[0] - self.curr_pos[0]
        y_change = pos[1] - self.curr_pos[1]
        print(f'x change: {x_change} y change: {y_change}    next tile: {next_tile}')
        #print(f"x: {x_change}    y: {y_change}")
        if x_change == 0 and y_change == 0:
            # no movement, only turning command was given
            self.desired_heading = self.desired_heading
        else:
            self.desired_heading = round(math.degrees(math.atan2(x_change*-1, y_change)))
            # there's some movement necessary
            #self.desired_heading = self.heading + \
                #round(math.degrees(math.atan2(y_change, x_change))) - \
                #90.0  # -90 fixes the transformed value
            #if self.desired_heading < -180.0:
                #self.desired_heading = self.desired_heading + 360
            #elif self.desired_heading > 180.0:
                #self.desired_heading = self.desired_heading - 360

    def computeMotorSpeed(self):
        """
        Currently assuming:
            if desired angle > current angle, turn right
            if desired angle < current angle, turn left
            Threshold of 2 degrees, will only try to rotate if the rotation
            is more than 2 degrees.
            Threshold of (5 centimeters, need to change after testing) for the x and y end points.
        """
        # TODO: Test angle and distance thresholds with C1C0
        absolute = self.desired_heading % 360
        wrapped_heading = self.heading if self.heading <= 180 else self.heading - 360
        print(
            f"curr tile x: {self.curr_tile.x}    curr tile y {self.curr_tile.y}")
        print(
            f"end point x: {self.endPoint[0]}    end point y {self.endPoint[1]}")
        print(
            f"self.desired_heading: {self.desired_heading}    self.heading {self.heading}")
        print(
            f"self.waypoint x: {self.path[self.pathIndex].x}    self.waypoint y: {self.path[self.pathIndex].y}"
        )
        if abs(self.curr_pos[0]-self.endPoint[0]) <= position_threshold and abs(self.curr_pos[1]-self.endPoint[1]) <= position_threshold and (abs(self.desired_heading - self.heading) <= angle_threshold):
            # if within position_threshold distance of end, and also facing a good enough direction
            return ()
        elif abs(self.heading - absolute) > angle_threshold:
            if (self.desired_heading >= 0 and wrapped_heading >= 0) or (self.desired_heading <= 0 and wrapped_heading <= 0):
                if self.desired_heading - wrapped_heading > angle_threshold:
                    return rotation_right
                elif self.desired_heading - wrapped_heading < -1*angle_threshold:
                    return rotation_left
            elif self.desired_heading >= 0 and wrapped_heading <= 0:
                diff = self.desired_heading - wrapped_heading
                if diff <= 180 and diff > angle_threshold:
                    return rotation_right
                elif diff > 180 and 360-diff > angle_threshold:
                    return rotation_left
            elif self.desired_heading <= 0 and wrapped_heading >= 0:
                diff = wrapped_heading - self.desired_heading
                if diff <= 180 and diff > angle_threshold:
                    return rotation_left
                elif diff > 180 and 360-diff > angle_threshold:
                    return rotation_right
        else:
            # forward motor speed
            return motor_speed

    def update_grid_wrapper(self):
        t_bot, t_mid, t_top = self.sensor_state.get_terabee()
        lidar_data = self.filter_lidar(self.sensor_state.lidar)
        t_bot = self.filter_terabee(t_bot)
        t_mid = self.filter_terabee(t_mid)
        t_top = self.filter_terabee(t_top)
        #print(lidar_data)

        lidar_ret = self.grid.update_grid_tup_data(self.curr_pos[0], self.curr_pos[1], lidar_data,
                                                   Tile.lidar, robot_radius, bloat_factor, self.path_set)
        bot_ter_ret = self.grid.update_grid_tup_data(self.curr_pos[0], self.curr_pos[1], t_bot, Tile.bottom_terabee,
                                                     robot_radius, bloat_factor, self.path_set)
        mid_ter_ret = self.grid.update_grid_tup_data(self.curr_pos[0], self.curr_pos[1], t_mid, Tile.mid_terabee,
                                                      robot_radius, bloat_factor, self.path_set)
        top_ter_ret = self.grid.update_grid_tup_data(self.curr_pos[0], self.curr_pos[1], t_top, Tile.top_terabee,
                                                      robot_radius, bloat_factor, self.path_set)
        self.heading = (self.sensor_state.heading + self.base_heading) % 360
        # if self.heading > 180:
        #     self.heading -= 360
        return lidar_ret and bot_ter_ret and mid_ter_ret and top_ter_ret

    def filter_lidar(self, lidar):
        # print(lidar)
        lidar_ret = []
        for (ang, dist) in lidar:
            if dist > 400:
                lidar_ret.append(((ang + lidar_shift_ang) % 360, dist))
        return lidar_ret

    def filter_terabee(self, terabee):
        terabee_ret = []
        for (ang, dist) in terabee:
            if 100 < dist < 50000:
                terabee_ret.append((ang, dist))
        return terabee_ret

    def move_one(self, curr_pos, error):
        angle = 90
        if error < 0:
            angle = -90
        angle = (angle + self.heading) % 360
        error_x = -1*math.sin(math.radians(angle)) * error
        error_y = math.cos(math.radians(angle)) * error

        new_x = -1*math.sin(math.radians(self.heading)) * tile_size + curr_pos[0] + error_x
        new_y = math.cos(math.radians(self.heading)) * tile_size + curr_pos[1] + error_y
        next_tile = self.grid.get_tile((new_x, new_y))
        return (new_x, new_y), next_tile

    def regenerate_path(self):
        try:
            self.path = search.a_star_search(
                self.grid, (self.curr_pos[0], self.curr_pos[1]), self.endPoint, search.euclidean)
            self.enclosed = False
            self.path = search.segment_path(self.grid, self.path)
            self.pathIndex = 1  # might need to change this based on current position?

            # self.pid = PID(self.path, self.pathIndex,
            #                self.curr_tile.x, self.curr_tile.y)

            self.drawWayPoint(self.path[self.pathIndex])
            self.generatePathSet()
            self.updateDesiredHeading(self.path[self.pathIndex], (self.path[self.pathIndex].x, self.path[self.pathIndex].y))
            self.pid = PID(self.path, self.pathIndex, self.curr_pos[0], self.curr_pos[1])
        except Exception as e:
            print(e, 'in an obstacle right now... oof ')
            self.enclosed = True

    def main_loop(self, lidarGenerate=None):
        """
        """
        # new_t = time.time();
        # print("recursiontime: " + str(new_t - self.t));
        # self.t = time.time()

        # refresh bloating every 6 iterations
        self.loop_it += 1
        if self.loop_it % 6 == 0:
            self.refresh_bloating()

        # update location based on indoor GPS
        #self.prev_tile, self.curr_tile = self.gps.update_loc(self.curr_tile)
        self.drawC1C0()
        if lidarGenerate is None:
            if self.run_mock:
                self.server.send_update((self.curr_tile.row, self.curr_tile.col))
            else:
                motor_speed = self.computeMotorSpeed()
                print(motor_speed)
                self.server.send_update(motor_speed)
        else:
            motor_speed = self.computeMotorSpeed()
            print(motor_speed)
        #  TODO 2: Update environment based on sensor data
        #self.sensor_state = SensorState()

        if lidarGenerate is None:
            received_json = self.server.receive_data()
        else:
            self.sensor_state.lidar = lidarGenerate(degree_freq, self.curr_tile.row, self.curr_tile.col)
            print(self.sensor_state.lidar)
        #print("received json:", received_json)
        # self.sensor_state.from_json(json.loads(received_json))
        # self.sensor_state.reset_data()
        if motor_speed == rotation_left:
            print("left")
            # self.sensor_state.heading = (self.sensor_state.heading-1)%360
            self.sensor_state.heading = (self.sensor_state.heading-1)%360
            print(self.sensor_state.heading)
        if motor_speed == rotation_right:
            print("right")
            self.sensor_state.heading = (self.sensor_state.heading+1)%360
        if motor_speed == (0.25, 0.25):
            print("forward")
            if self.count % 2 == 0:
                # error = np.random.normal(loc=0, scale=20, size=None)
                self.prev_tile, self.prev_pos = self.curr_tile, self.curr_pos
                self.curr_pos, self.curr_tile = self.move_one(self.curr_pos, self.error)
                self.pid.update_PID(self.curr_pos[0], self.curr_pos[1])
            self.count = self.count + 1

        # self.sensor_state.front_obstacles()
        # self.sensor_state.four_corners()
        # self.sensor_state.spawn_inside_obstacle_line()
        # self.sensor_state.diamond()
        # gap_size = (int)((((time.time() - self.global_time)%360)*40)%360)
        # print(360 - gap_size)
        # if time.time() - self.global_time > 10:
        #     self.sensor_state.reset_data()
        # else:
        # self.sensor_state.circle_gap(360 - gap_size)
        # print(self.sensor_state.to_json())
        # print(self.sensor_state)
        self.update_grid_wrapper()
        self.visibilityDraw(self.filter_lidar(self.sensor_state.lidar))

        update = self.grid.update_grid_tup_data(self.curr_pos[0], self.curr_pos[1], self.filter_lidar(self.sensor_state.lidar), Tile.lidar, robot_radius, bloat_factor, self.path_set)
		#this condition is true if an obstacle is blocking the original path

        if update or self.enclosed:
            # re calculating the path

            # if self.enclosed and not update:
            #     self.enclosed = False
            self.generatePathSet()
            #print('current location x', self.curr_tile.x)
            #print('current location y', self.curr_tile.y)

            self.regenerate_path()
            # try:
            #     self.path = search.a_star_search(
            #         self.grid, (self.curr_pos[0], self.curr_pos[1]), self.endPoint, search.euclidean)
            #     self.enclosed = False
            #     self.path = search.segment_path(self.grid, self.path)
            #     self.pathIndex = 1 # might need to change this based on current position?
            #
            #     # self.pid = PID(self.path, self.pathIndex,
            #     #                self.curr_tile.x, self.curr_tile.y)
            #
            #     self.drawWayPoint(self.path[self.pathIndex])
            #     self.generatePathSet()
            #     self.updateDesiredHeading(self.path[self.pathIndex])
            #     self.pid = PID(self.path, self.pathIndex, self.curr_pos[0], self.curr_pos[1])
            # except Exception as e:
            #     print(e, 'in an obstacle right now... oof ')
            #     self.enclosed = True
                

        # recalculate path if C1C0 is totally off course (meaning that PA + PB > 2*AB)
        if self.pathIndex != 0:
            if self.pid.getError() > regenerate_threshold:
                self.regenerate_path()
            # # distance to previous waypoint
            # dist1 = (self.curr_pos[0] - self.path[self.pathIndex-1].x)**2 + (
            #     self.curr_pos[1] - self.path[self.pathIndex-1].y) ** 2
            # # distance to next waypoint
            # dist2 = (self.curr_pos[0] - self.path[self.pathIndex].x) ** 2 + (
            #     self.curr_pos[1] - self.path[self.pathIndex].y) ** 2
            # # distance between waypoints
            # dist = (self.path[self.pathIndex-1].x - self.path[self.pathIndex].x) ** 2\
            #     + (self.path[self.pathIndex-1].y -
            #        self.path[self.pathIndex].y) ** 2
            # if 1.5 * dist < dist1 + dist2:
            #     print('regerate in off path')
            #     self.regenerate_path()


                # try:
                #     self.path = search.a_star_search(self.grid, (self.curr_pos[0], self.curr_pos[1]), self.endPoint,
                #                                      search.euclidean)
                #     self.path = search.segment_path(self.grid, self.path)
                #     self.pathIndex = 1
                #     self.pid = PID(self.path, self.pathIndex,
                #                    self.curr_pos[0], self.curr_pos[1])
                #     self.generatePathSet()
                #     self.drawWayPoint(self.path[self.pathIndex])
                #     self.updateDesiredHeading(self.path[self.pathIndex])
                # except Exception as e:
                #     print(e, 'in an obstacle right now... oof ')
                #     self.enclosed = True

        # has segmented path as self.path, way points
        # pathIndex points at the point bot is trying to get to
        # the robot moving will be turning into the desired heading direction and move one tile forward

        self.drawPath()

        pidx, pidy = self.calcVector()
        new_x = pidx * 80 + self.curr_pos[0]
        new_y = pidy * 80 + self.curr_pos[1]
        self.updateDesiredHeading(self.grid.get_tile((new_x, new_y)), (new_x, new_y))
        print(f"pidx: {pidx}    pidy: {pidy}    new desired heading: {self.desired_heading}")
        # print("pidx: " + str(pidx) + "      pidy: " + str(pidy))
        # pid_heading_deg = (math.degrees(math.atan2(pidy, pidx)) + 360)%360
        # if pid_heading_deg != self.heading:
        #     print("pid_heading_deg: " + str(pid_heading_deg))
        #     self.desired_heading = pid_heading_deg
        # # this condition is true if we're at the tile and facing the right way
        # elif self.nextLoc():

        if self.nextLoc():
            print("get in nextLoc()")
            self.pathIndex += 1
            self.pid.update_path_index(self.pathIndex)

            if self.pathIndex >= len(self.path):
                return
            # self.pid = PID(self.path, self.pathIndex,
            #                self.curr_tile.x, self.curr_tile.y)
            self.drawWayPoint(self.path[self.pathIndex])
            print('next loc draw waypoint')
            print(self.pathIndex)
            # self.updateDesiredHeading(self.path[self.pathIndex])
            self.updateDesiredHeading(self.path[self.pathIndex], (self.path[self.pathIndex].x, self.path[self.pathIndex].y))
            print("desired heading" + str(self.desired_heading))

        # return if we are at the end destination
        if self.curr_tile == self.path[-1] and abs(self.heading - self.desired_heading) <= angle_threshold:
            return
        if self.debug and 0 < self.expiry_time < time.time():
            print("Ran out of time")
            self.master.quit()
            return

        # recursively loop
        self.t = time.time()
        self.master.after(1, lambda: self.main_loop(lidarGenerate))
        # time.sleep(0.001)
        # self.main_loop(lidarGenerate)

    def calcVector(self):
        """
        Returns the unit vector between the current location and the end point of the current line segment
        and draws this vector onto the canvas
        """
        #print('calc vector was called')
        if self.pathIndex < len(self.path):
            vect = self.pid.newVec()
            # print("newvec velocity vector: " + str(vect))
            if self.prev_vector is not None:
                # delete old drawings from previous iteration
                self.canvas.delete(self.prev_vector)
            if self.pathIndex == 0:
                print(self.path[0])
                print(self.path[1])
                vect[0] = self.path[1].x - self.curr_pos[0]
                vect[1] = self.path[1].y - self.curr_pos[1]

            start = self._scale_coords((self.curr_pos[0], self.curr_pos[1]))
            end = self._scale_coords((self.curr_pos[0] + vector_draw_length *
                                     vect[0], self.curr_pos[1] + vector_draw_length * vect[1]))
            self.prev_vector = self.canvas.create_line(
                start[0], start[1], end[0], end[1], arrow='last', fill='red')
            # unit vector
            mag = math.sqrt(vect[0]**2 + vect[1]**2)
            if mag != 0:
                # vect = (vect[0]/mag, vect[0]/mag)
                vect[0] = vect[0]/mag
                vect[1] = vect[1]/mag
        print(f"vect: {vect}")
        return vect

    def refresh_bloating(self):
        for row in self.grid.grid:
            for tile in row:
                if tile.is_bloated:
                    tile.is_bloated = False
                    tile.is_obstacle = False
        for row in self.grid.grid:
            for tile in row:
                if tile.is_obstacle and not tile.is_bloated:
                    self.grid.bloat_tile(tile, 80, 2, set())

    def visibilityDraw(self, lidar_data):
        """Draws a circle of visibility around the robot
       """
        # coloring all tiles that were seen in last iteration light gray
        # while self.last_iter_seen:
        #     curr_rec = self.last_iter_seen.pop()
        #     self.canvas.itemconfig(
        #         curr_rec, outline="#C7C7C7", fill="#C7C7C7")  # light gray
        row = self.curr_tile.row
        col = self.curr_tile.col
        index_radius_inner = int(vis_radius / tile_size)
        index_radius_outer = index_radius_inner + 2
        # the bounds for the visibility circle
        lower_row = max(0, row - index_radius_outer)
        lower_col = max(0, col - index_radius_outer)
        upper_row = min(row + index_radius_outer, self.grid.num_rows - 1)
        upper_col = min(col + index_radius_outer, self.grid.num_cols - 1)
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
                curr_tile = self.grid.grid[int(coords[0])][int(coords[1])]
                curr_rec = self.tile_dict[curr_tile]
                if curr_tile.is_bloated:
                    self.canvas.itemconfig(
                        curr_rec, outline="#ffc0cb", fill="#ffc0cb")  # pink
                elif curr_tile.is_obstacle:
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

    def drawC1C0(self):
        """Draws C1C0's current location on the simulation"""
        # coordinates of robot center right now (in cm)
        center_x = self.curr_pos[0]
        center_y = self.curr_pos[1]
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
        arrow_end_coords_scaled = self._scale_coords(
            (arrow_end_x, arrow_end_y))
        # draw white arrow
        self.prev_draw_c1c0_ids[1] = self.canvas.create_line(
            center_coords_scaled[0], center_coords_scaled[1],
            arrow_end_coords_scaled[0], arrow_end_coords_scaled[1], arrow='last', fill='white'
        )

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
            x1, y1 = self._scale_coords(
                (self.path[idx - 1].x, self.path[idx - 1].y))
            x2, y2 = self._scale_coords((self.path[idx].x, self.path[idx].y))
            canvas_id = self.canvas.create_line(
                x1, y1, x2, y2, fill=color, width=1.5)
            self.prev_line_id.append(canvas_id)
            idx += 1

    def _scale_coords(self, coords):
        """scales coords (a tuple (x, y)) from real life cm to pixels"""
        scaled_x = coords[0] / tile_scale_fac
        scaled_y = coords[1] / tile_scale_fac
        return scaled_x, scaled_y

    def generatePathSet(self):
        '''
        sets `self.path_set` to all the tiles along the path
        '''
        self.path_set = set()
        for i in range(len(self.path)-1):
            self.breakUpLine(self.path[i], self.path[i+1])

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
            new_tile = self.grid.get_tile(new_coor)
            if new_tile not in self.path_set:
                self.path_set.add(new_tile)

    def drawWayPoint(self, new_tile):
        if self.way_point is not None:
            self.canvas .delete(self.way_point)
        offset = GUI_tile_size
        x = new_tile.x / tile_scale_fac
        y = new_tile.y / tile_scale_fac
        self.way_point = self.canvas.create_oval(
            x - offset, y - offset, x + offset, y + offset, outline="#FF0000", fill="#FF0000")


if __name__ == "__main__":
    big_server = Server()
    count = 1
    while True:
        s = ServerGUI(big_server, error=0)
        s.server.send_update("path planning is over")
        with open("heading_data.txt", "w") as file:
            file.write(str(int(s.heading)) + "\n")
        s.master.destroy()
        # print(count)
        count = count + 1
