import grid
from Tile import *
import math
from Consts import *

class PID:
    """
    File that handles locomotion errors with the PID algorithm
    Instance Attributes:
        path : The desired list of tiles that c1c0 should be moving along
        pathIdx : The iteration of the path tiles that C1C0 should be going torwards
        curr_tile: The current tile that c1c0 is on
        prev_tile : The previous tile that c1c0 was on
    """

    def __init__(self, path, pathidx, curr_x, curr_y, prev_x, prev_y):
        self.curr_x = curr_x
        self.curr_y = curr_y
        self.path = path
        self.errorHistory = 0
        self.oldError = 0
        self.pathIndex = pathidx
        self.prev_x = prev_x
        self.prev_y = prev_y

    def calc_dist(self):
        """
        returns the perpendicular distance from c1c0's current value to the line that c1c0 should be travelling on
        """
        b = self.path[self.pathIndex].x - self.path[self.pathIndex - 1].x
        a = self.path[self.pathIndex].y - self.path[self.pathIndex - 1].y
        den = 0
        if a != 0 and b != 0:
            den = (b/a) + (a/b)
        d = 0
        if den != 0:
            c = self.path[self.pathIndex - 1].y - (a/b)*self.path[self.pathIndex - 1].x
            x = (self.curr_x + (b/a)*self.curr_x - self.path[self.pathIndex - 1].y + (a/b) *
                 self.path[self.pathIndex - 1].x)/den
            y = (a/b)*x + c
            d = ((x - self.curr_x)**2 + (y - self.curr_y)**2)**(1/2)
        return d


    def PID(self):
        """
        returns the control value function for the P, I, and D terms
        """
        error = self.calc_dist()
        der = error - self.oldError
        self.oldError = error
        self.errorHistory += error
        return (error * gaine) + (der * gaind) + (self.errorHistory * gainI)


    def newVec(self):
        """
        return the new velocity vector based on the PID value
        """
        velocity = (self.curr_x - self.prev_x, self.curr_y - self.prev_y)
        mag = (velocity[0]**2 + velocity[1]**2)**(1/2)
        perpendicular = (0, 0)
        if mag > 0:
            perpendicular = (-velocity[1]/mag, velocity[0]/mag)
        c = self.PID()
        return [c * a + b for a, b in zip(perpendicular, velocity)]