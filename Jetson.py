from Networks import *
from SensorCode import *
import Grid_Classes.grid as grid
from Simulation_Helpers.EndpointInput import *
from time import sleep
import sys
import time


class Jetson:
    command_move = "(\'move forward\', 3)"
    command_turn = "(\'turn\', -30.0)"
    command_pos = "(5, 5)"
    command_no_change = "(\'move forward\', 0.0)"
    # +y == -90 degrees from original frame (left relative to down)
    # -y == +90 degrees from original frame (right relative to down)
    # +x == 0 degrees  from original frame (down relative to down)
    # -x == 180 degrees from original frame (up relative to down)

    def __init__(self, end_point=command_move, interactive=False):
        """
        """
        self.grid = grid.Grid(tile_num_height, tile_num_width, tile_size)
        self.client = Client()
        self.sensor_state = SensorState(client=not interactive)
        self.command_client = CommandClient("path-planning")
        # self.command_client.handshake()  # sets up socket connection
        # starting location for middle
        self.curr_tile = self.grid.grid[int(
            tile_num_width/2)][int(tile_num_height/2)]
        self.global_time = time.time()
        if not interactive:
            self.client.init_send_data({'end_point': end_point})
        else:
            print('Commands for C1C0:')
            print('> move (1)')
            print('> turn (2)')
            comm = input('Enter number corresponding to command: ')
            if comm == '1':
                dist = input('Enter distance to move in meters (0 - 5): ')
                self.client.init_send_data({'end_point': f"(\'move forward\', {dist})"})
            else:
                angle = input('Enter angle to turn in degrees (1 - 360): ')
                self.client.init_send_data({'end_point': f"(\'turn\', {angle})"})

        self.main_loop(sensor_available=not interactive)

    def main_loop(self, sensor_available=False):
        """
        main loop that reads motor power from server,
        powers robot with command, then
        returns sensor state object to server
        """
        motor_power = self.client.listen()
        print("motor power: ", motor_power)
        if type(motor_power) is str:
            print('completed')
            self.command_client.close()
            return
        finished = motor_power == []
        command_to_send = "locomotion (+0.00,+0.00)"
        if not finished:
            first_sign = "+" if motor_power[0] > 0.0 else ""
            second_sign = "+" if motor_power[1] > 0.0 else ""
            command_to_send = "locomotion (" + first_sign + str(
                motor_power[0]) + "," + second_sign + str(motor_power[1]) + ")"

        print(command_to_send)
        self.command_client.communicate(command_to_send)
        #self.sensor_state.update()
        #gap_size = (int)((((time.time() - self.global_time)%360)*40)%360)
        #print(360 - gap_size)
        #self.sensor_state.circle_gap(360 - gap_size)
        self.sensor_state.reset_data()

        if sensor_available:
            self.sensor_state.update()

        self.client.send_data(self.sensor_state.to_json())

        # TODO: find out if this sleep time is enough for command_client communication to work
        sleep(.001)
        if not finished:
            self.main_loop()
        else:
            self.command_client.close()


if __name__ == "__main__":
    #Jetson(sys.argv[1])
    Jetson()
    # Jetson(interactive=True)
