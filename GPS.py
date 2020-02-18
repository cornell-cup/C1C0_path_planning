import threading
from time import sleep
import math

FREQUENCY= .01

class GPSThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.active = True
        self.x = 250
        self.y = 250
        self.vel = 0
        self.heading = 0

    def run(self):
        while self.active:
            sleep(FREQUENCY)
            self.x = self.x + FREQUENCY * self.vel * math.cos(self.heading)
            self.y = self.y + FREQUENCY * self.vel * math.sin(self.heading)

    def update(self,vel,heading):
        self.vel=vel
        self.heading = heading

    def kill(self):
        self.active = False
