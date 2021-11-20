from Networks.Client import *
from Networks.CommandClient import *
from SensorCode.SensorState import *
import Grid_Classes.grid as grid
from tkinter import *
from Simulation_Helpers.EndpointInput import *
from time import sleep


class Jetson:
    command_move = "(\'move forward\', 10.0)"
    command_turn = "(\'turn\', 30.0)"
    command_pos = "(-10, 25)"
    # +y == -90 degrees from original frame (left relative to down)
    # -y == +90 degrees from original frame (right relative to down)
    # +x == 0 degrees from original frame (down relative to down)
    # -x == 180 degrees from original frame (up relative to down)

    def __init__(self, end_point=command_move):
        """
        """
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.client = Client()
        self.sensor_state = SensorState()
        self.command_client = CommandClient("path-planning")
        # self.command_client.handshake()  # sets up socket connection
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
        command_to_send = "locomotion (0.00, 0.00)"
        if not finished:
            command_to_send = "locomotion (" + str(
                motor_power[0]) + ", " + str(motor_power[1]) + ")"
        print(command_to_send)
        self.command_client.communicate(command_to_send)
        self.sensor_state = SensorState()
        self.client.send_data(self.sensor_state)

        # TODO: find out if this sleep time is enough for command_client communication to work
        sleep(.001)
        if not finished:
            self.main_loop()
        else:
            self.command_client.close()


if __name__ == "__main__":
    Jetson()
