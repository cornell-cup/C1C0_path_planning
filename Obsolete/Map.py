import threading
from time import sleep
import math
import grid

FREQUENCY = .05


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
        self.path = None
        self.collision = False
        self.newPath = False

    def run(self):
        while self.active:
            sleep(FREQUENCY)
            collisionDetection = self.grid.updateGrid(self.x,
                                                      self.y, self.sensorDataBot,
                                                      self.sensorDataTop,
                                                      self.path)
            if (collisionDetection == True):
                self.collision = True

    def update(self, sensorDataTop, sensorDataBot, x, y, path):
        self.sensorDataTop = sensorDataTop
        self.sensorDataBot = sensorDataBot
        self.x = x
        self.y = y
        self.path = path

    def setPath(self, path):
        self.path = path

    def kill(self):
        self.active = False
