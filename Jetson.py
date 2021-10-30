from Networks.Client import *
from SensorCode.SensorState import *
import Grid_Classes.grid as grid
from tkinter import *
from Simulation_Helpers.EndpointInput import *
from time import sleep

class Jetson:
    def __init__(self, end_point):
        """
        """
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.client = Client()
        self.sensor_state = SensorState()

        # starting location for middle
        self.curr_tile = self.grid.grid[int(tile_num_width/2)][int(tile_num_height/2)]

        self.client.send_data({'end_point': end_point})
        self.main_loop()

    def main_loop(self):
        """
        main loop that reads motor power from server,
        powers robot with command, then
        returns sensor state object to server
        """
        motor_power = self.client.listen()
        finished = motor_power == ()
        # TODO: Integrate with locomotion to actually power with motor power

        self.sensor_state = SensorState()
        self.client.send_data(self.sensor_state)

        sleep(.001)
        if not finished:
            self.main_loop()

if __name__ == "__main__":
    Jetson(sys.argv[1])
