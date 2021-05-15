import copy
import time
from typing import Dict
from Server import *
import grid
from tkinter import *
from marvelmind import MarvelmindHedge
import search
from Tile import *
import math
import SensorState
from PID import *

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

    def __init__(self):
        self.master: Tk = Tk()
        self.canvas: Canvas = None
        self.tile_dict: Dict[Tile, int] = None
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.last_iter_seen = set()
        # TODO Update this heading in the future...
        self.heading: int = 180
        self.curr_tile = self.grid.grid[int(self.grid.num_rows/2)][int(self.grid.num_cols/2)]
        # create Marvel Mind Hedge thread
        # get USB port with ls /dev/tty.usb*
        # adr is the address of the hedgehog beacon!
        self.hedge = MarvelmindHedge(tty=tty, adr=adr, debug=False)
        # start thread
        self.hedge.start()
        # REQUIRED SLEEP TIME in order for thread to start and init_pos to be correct
        time.sleep(1)
        # data in array's [x, y, z, timestamp]
        self.init_pos = self.hedge.position()
        self.update_loc()
        # planned path of tiles
        self.prev_draw_c1c0_ids = [None, None]
        self.create_widgets()
        self.server = Server()
        self.endPoint = self.server.receive_data()['end_point']
        print('got the end point to be, ', self.endPoint)
        self.path = search.a_star_search(self.grid, (self.curr_tile.x, self.curr_tile.y), self.endPoint, search.euclidean)
        self.path = search.segment_path(self.grid, self.path)
        self.path_set = set()
        self.generatePathSet()
        self.pathIndex = 0
        self.prev_tile = None
        self.prev_vector = None

        self.prev_line_id = []
        self.set_of_prev_path = []
        self.color_list = ['#2e5200', '#347800', '#48a600', '#54c200', '#60de00', 'None']
        self.index_fst_4 = 0
        self.drawPath()
        self.pid = PID(self.path, self.pathIndex, self.curr_tile.x, self.curr_tile.y)

        self.main_loop()
        self.master.mainloop()

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
        next_tile = self.path[self.pathIndex]
        d = math.sqrt((self.curr_tile.x - next_tile.x)**2 + (self.curr_tile.y - next_tile.y)**2)
        return d <= reached_tile_bound

    def main_loop(self):
        """
        """
        #  TODO 1: update location based on indoor GPS
        self.update_loc()
        self.drawC1C0()
        self.server.send_update((self.curr_tile.row, self.curr_tile.col))
        #  TODO 2: Update environment based on sensor data
        self.sensor_state = self.server.receive_data()

        self.visibilityDraw(self.sensor_state.get_lidar())

        if self.grid.update_grid_tup_data(self.curr_tile.x, self.curr_tile.y, self.sensor_state.get_lidar(), Tile.lidar, robot_radius, bloat_factor, self.path_set):
            self.generatePathSet()
            self.path = search.a_star_search(self.grid, (self.curr_tile.x, self.curr_tile.y), self.endPoint, search.euclidean)
            self.path = search.segment_path(self.grid, self.path)
            self.generatePathSet()
        self.drawPath()

        self.calcVector()
        if nextLoc():
            self.pathIndex += 1
            self.pid = PID(self.path, self.pathIndex, self.curr_tile.x, self.curr_tile.y)
        # return if we are at the end destination
        if self.curr_tile == self.path[-1]:
            return
        # recursively loop
        self.master.after(1, self.main_loop)

    def calcVector(self):
        """
        Returns the vector between the current location and the end point of the current line segment
        and draws this vector onto the canvas
        """
        vect = (0, 0)
        if self.pathIndex + 1 < len(self.path):
            vect = pid.newVec()
            if self.prev_vector is not None:
                # delete old drawings from previous iteration
                self.canvas.delete(self.prev_vector)
            start = self._scale_coords((self.curr_tile.x, self.curr_tile.y))
            end = self._scale_coords((self.curr_tile.x + vect[0], self.curr_tile.y + vect[1]))
            self.prev_vector = self.canvas.create_line(
                start[0], start[1], end[0], end[1], arrow='last', fill='red')
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

    def drawC1C0(self):
        """Draws C1C0's current location on the simulation"""
        # coordinates of robot center right now (in cm)
        center_x = self.curr_tile.x
        center_y = self.curr_tile.y
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

    def update_loc(self):
        """
        updates the current tile based on the GPS input
        """
        # call indoor gps get location function
        print(self.hedge.position())
        [_, x, y, z, ang, time] = self.hedge.position()
        self.heading = ang - self.init_pos[4]
        # map the position to the correct frame of reference
        x = (x - self.init_pos[1]) * 10
        y = (y - self.init_pos[2]) * 10
        x = int(tile_num_width/2) + int(x * 100 / tile_size)
        y = int(tile_num_height/2) + int(y * 100 / tile_size)
        # set self.curr_tile
        self.prev_tile = self.curr_tile
        self.curr_tile = self.grid.grid[x][y]
        self.pid.update_PID(self.curr_tile.x, self.curr_tile.y)


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
            x1, y1 = self._scale_coords((self.path[idx - 1].x, self.path[idx - 1].y))
            x2, y2 = self._scale_coords((self.path[idx].x, self.path[idx].y ))
            canvas_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1.5)
            self.prev_line_id.append(canvas_id)
            idx += 1

    def _scale_coords(self, coords):
        """scales coords (a tuple (x, y)) from real life cm to pixels"""
        scaled_x = coords[0] / tile_scale_fac
        scaled_y = coords[1] / tile_scale_fac
        return scaled_x, scaled_y

    def generatePathSet(self):
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
            new_tile = self.grid.get_tile(new_coor)
            if new_tile not in self.path_set:
                self.path_set.add(new_tile)

if __name__ == "__main__":
    ServerGUI()
