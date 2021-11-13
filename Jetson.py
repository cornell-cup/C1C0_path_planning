from Networks.Client import *
from Networks.CommandClient import *
from SensorCode.SensorState import *
import Grid_Classes.grid as grid
from tkinter import *
from Simulation_Helpers.EndpointInput import *
from time import sleep


class Jetson:
    def __init__(self, end_point="(\'move forward\', 5.0)"):
        """
        """
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.client = Client()
        self.sensor_state = SensorState()
        self.command_client = CommandClient("path-planning")
        #self.command_client.handshake()  # sets up socket connection
        # starting location for middle
        self.curr_tile = self.grid.grid[int(
            tile_num_width/2)][int(tile_num_height/2)]

        self.client.init_send_data({'end_point': end_point})
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
        #command_to_send = "locomotion (0.00, 0.00)"
        if not finished:
            command_to_send = "locomotion (" + str(
                motor_power[0]) + ", " + str(motor_power[1]) + ")"
        self.command_client.communicate(command_to_send)
        self.sensor_state = SensorState()
        self.sensor_state.update()
        self.client.send_data(self.sensor_state)


        # For Angela: does this sleep time need to be increased for communicate to work?
        sleep(.001)
        if not finished:
            self.main_loop()
        else:
            self.command_client.close()


if __name__ == "__main__":
    Jetson()
