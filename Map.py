import threading
from time import sleep
import math
import grid

FREQUENCY = .5


class MapThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.active = True
        self.grid = grid.Grid(500, 500, .2)
        self.sensorDataTop = []
        self.sensorDataBot = []
        self.x = 250
        self.y = 250

    def run(self):
        while self.active:
            sleep(FREQUENCY)
            self.grid.updateGrid(
                self.x, self.y, self.sensorDataBot, self.sensorDataTop)

    def update(self, sensorDataTop, sensorDataBot, x, y):
        self.sensorDataTop = sensorDataTop
        self.sensorDataBot = sensorDataBot
        self.x = x
        self.y = y

    def kill(self):
        self.active = False
