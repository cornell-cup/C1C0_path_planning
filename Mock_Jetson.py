from Networks.Client import *
from SensorCode.SensorState import *
from Simulation_Helpers.RandomObjects import RandomObjects
import Grid_Classes.grid as grid
import Grid_Classes.grid as grid
from tkinter import *
import math
from Simulation_Helpers.GenerateSensorData import GenerateSensorData
from Simulation_Helpers.EndpointInput import *
from scripts.NumSeeds import *

class Mock_Jetson:
    def __init__(self, end_point):
        """
        """
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.client = Client()
        self.sensor_state = SensorState()

        #Visualization
        self.master: Tk = Tk()
        self.canvas: Canvas = None
        #TODO: update heading 
        self.heading = 0
        self.prev_draw_c1c0_ids = [None, None]
        self.tile_dict: Dict[grid.Tile, int] = None

        # Generates random enviroment on the grid
        generator = RandomObjects(self.grid)
        generator.create_env(22, 0, 0, 22, 9)
        self.sensor_generator = GenerateSensorData(self.grid)

        self.create_widgets()
        # starting location for middle
        self.curr_tile = self.grid.grid[int(tile_num_width/2)][int(tile_num_height/2)]

        self.client.send_data({'end_point': userInput(end_point)})
        print("sent")
        self.main_loop()
        self.master.mainloop()

    def main_loop(self):
        """
        """
        # TODO: update the curr tile from read
        new_coor = self.client.listen()
        self.curr_tile = self.grid.grid[new_coor[0]][new_coor[1]]
        self.drawC1C0()
        self.sensor_state = SensorState()
        self.sensor_state.set_lidar(self.sensor_generator.generateLidar(degree_freq, self.curr_tile.row, self.curr_tile.col))
        self.client.send_data(self.sensor_state)
        self.drawC1C0()
        self.master.after(1, self.main_loop)


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



if __name__ == "__main__":
    # numericalSeed()
    Mock_Jetson(end_point=sys.argv[1])
