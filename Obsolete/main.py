# TODO main script
from time import sleep
from Obsolete import GPS, Map
import search

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
# interval = 2
# threading.Timer(interval, main()).start()


# starting and ending positions that will be somehow drawn from
# my man stanley Lin
startPos = (0, 0)
endPos = (100, 100)

GlobalPosition = GPS.GPSThread(1)
MapThread = Map.MapThread(2)


# function to use for search that returns the manahttan distance between two
# points


def manhattan(first, second):
    legX = abs(first[0] - second[0])
    legY = abs(first[1] - second[1])
    return legX + legY


path = search.a_star_search(MapThread.grid, startPos, endPos, manhattan)
MapThread.setPath(path)

# Variable to represent velocity of CICO: float in m/s
# Will need to pull inputs from pins- TEMPORARILY SET TO 1m/s
vel = 1

# Variable to represent heading of CICO: float between 0-360 degrees
# Will need to read from pins
heading = 0

sensorDataTop = []
sensorDataBot = []
lidarData = []

# Command loop to continuosuly run, we will eventually change while loop
# with condition that no input has terminated it
GlobalPosition.start()
MapThread.start()

while True:
    if (MapThread.collision == True):
        search.a_star_search(MapThread.grid, startPos, endPos, manhattan)
        MapThread.collision = False
    else:
        for i in range(4):
            GlobalPosition.update(vel, heading)
            sleep(.01)
        GlobalPosition.update(vel, heading)
        MapThread.update(sensorDataTop, sensorDataBot,
                         GlobalPosition.x, GlobalPosition.y, path)
        sleep(.01)
