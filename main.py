# TODO main script
import grid
import numpy as np
import threading

"""
1) create grid
2) determine goal's position in grid
3) Get IR sensor data
4) fill in obstacles
5) Plan path in grid
6) repeat 3 - 5 until reach goal
"""


class main():

    def __init__(self):
        self.grid = grid.Grid(500, 500, 20)
        self.x = 0
        self.y = 0
        self.heading = 0

    def update(self, cur_x, cur_y, sensorDataTop, sensorDataBot):
        self.grid = grid.updateGrid(cur_x, cur_y, sensorDataTop, sensorDataBot)

    def updateGlobalPos(self, vel, heading):
        self.x

    # def main_driver(self, interval):
    #     threading.Timer(interval, main).start()


# Repeatedly updating the grid for specific time interval
interval = 2
threading.Timer(interval, main()).start()
# First calculate golbal position

# Read IR data

# main.update()
