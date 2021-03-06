import search
import Obstacles
from typing import Dict
from Server import *
from grid import *

class ClientGUI:
    """
    Master file to run autonomous path planning and display visualization real-time
    Instance Attributes:
        master (Tk): Tkinter GUI object
        canvas (Canvas): Tkinter Canvas that represents the GUI
        tile_dict (Dict[Tile, Rectangle]): Mapping from tiles to rectangles on GUI
        grid (Grid): grid that represents the environment
        heading (int): integer to represent the angle that the robot is facing
    """
    def __init__(self, emptyMap, path):
        self.master: Tk = Tk()
        self.canvas: Canvas = None
        self.tile_dict: Dict[Tile, int] = None
        self.grid: Grid = emptyMap
        self.heading: int = 0
        self.endpoint = None
        self.curr_tile = None
        self.path = path
        self.prev_draw_c1c0_ids = [None, None]

        self.create_widgets()
        self.receiver = Server()
        self.main_loop()


    def create_widgets(self):
        """
        Creates the canvas of the size of the inputted grid
        """
        self.master.geometry("+900+100")
        canvas = Canvas(self.master, width=len(self.grid.grid[0]) * GUI_tile_size, height=len(self.grid.grid) * GUI_tile_size)
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

    def main_loop(self):
        """
        """
        print('running main loop')

        #  TODO 1: update location based on indoor GPS
        self.update_loc()
        self.drawC1C0()
        #  TODO 2: Update enviroment based on sensor data
        Obstacles.update_env()
        #  TODO 3: check if the previous path is obstructed
            # If valid continue execution
            # else replan path

        # TODO 4: Send movement command

        # TODO 5: return if we are at the end destiation

        # loop
        self.receiver.grid_update()
        self.master.after(1, self.main_loop())

    def update_loc(self):
        """
        updates the location of the robot on the grid, based on indoor GPS readings
        """
        pass

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

    def drawC1C0(self):
        """Draws C1C0's current location on the simulation"""

        def _scale_coords(coords):
            """scales coords (a tuple (x, y)) from real life cm to pixels"""
            scaled_x = coords[0] / tile_scale_fac
            scaled_y = coords[1] / tile_scale_fac
            return scaled_x, scaled_y

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
        top_left_coords_scaled = _scale_coords(top_left_coords)
        bot_right_coords_scaled = _scale_coords(bot_right_coords)

        # draw blue circle
        self.prev_draw_c1c0_ids[0] = self.canvas.create_oval(
            top_left_coords_scaled[0], top_left_coords_scaled[1],
            bot_right_coords_scaled[0], bot_right_coords_scaled[1],
            outline='black', fill='blue')

        center_coords_scaled = _scale_coords((center_x, center_y))

        # finding endpoint coords of arrow
        arrow_end_x = center_x + robot_radius * math.cos(heading_adj_rad)
        arrow_end_y = center_y + robot_radius * math.sin(heading_adj_rad)
        arrow_end_coords_scaled = _scale_coords((arrow_end_x, arrow_end_y))

        # draw white arrow
        self.prev_draw_c1c0_ids[1] = self.canvas.create_line(
            center_coords_scaled[0], center_coords_scaled[1],
            arrow_end_coords_scaled[0], arrow_end_coords_scaled[1], arrow='last', fill='white'
        )
def clientGridSimulation():
    emptyMap = Grid(tile_num_height, tile_num_width, tile_size)
    startPoint = (0, 0)
    endPoint = (20, 20)
    path = search.a_star_search(
        emptyMap, startPoint, endPoint, search.euclidean)
    simulation = ClientGUI(Tk(), emptyMap, path) #do we need to break the path up?
    simulation.main_loop()

if __name__ == "__main__":
    clientGridSimulation()
