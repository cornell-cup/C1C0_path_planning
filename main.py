# TODO main script
import grid
import numpy as np
import threading
import math
from time import sleep
import GPS

"""
1) create grid
2) determine goal's position in grid
3) Get IR sensor data
4) fill in obstacles
5) Plan path in grid
6) repeat 3 - 5 until reach goal

Recieve an input for global every .01 seconds
revieve an input for distance mappings every .05 seconds
Output every .2 seconds 
recalculate algorithm every .2 seconds
"""
# def main_driver(self, interval):
#     threading.Timer(interval, main).start()

# Repeatedly updating the grid for specific time interval
#interval = 2
#threading.Timer(interval, main()).start()


Global_Position = GPS.GPS(1)

# Variable to represent velocity of CICO: float in m/s
# Will need to pull inputs from pins- TEMPORARILY SET TO 1m/s
vel = 1

# Variable to represent heading of CICO: float between 0-360 degrees
# Will need to read from pins
heading = 0

# while True:
# Global_Position.
# sleep(.01)
