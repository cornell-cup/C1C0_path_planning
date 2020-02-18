import threading
from time import sleep
import math


class GPSThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.active = True
        self.x = 250
        self.y = 250

    def run(self, vel, heading):
        self.x = self.x + vel*math.cos(heading)
        self.y = self.y + vel*math.sin(heading)

    def kill(self):
        self.active = False
