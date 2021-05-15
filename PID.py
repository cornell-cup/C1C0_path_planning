import grid
from Tile import *
import math
from Consts import *

def ptLineDist(a,b,x1,y1,x2,y2):
    """Returns distance from (a,b) to line segment connecting (x1,y1)
    and (x2, y2)"""
    A= y1-y2
    B= x2-x1
    C= x1*y2-x2*y1
    d= (A*a+B*b+C)/(math.sqrt(A**2+B**2))
    return d

class PID:
    """
    File that handles locomotion errors with the PID algorithm
    Instance Attributes:
        path : The desired list of tiles that c1c0 should be moving along
        pathIdx : The iteration of the path tiles that C1C0 should be going torwards
        curr_tile: The current tile that c1c0 is on
        prev_tile : The previous tile that c1c0 was on
    """

    def __init__(self, path, pathidx, curr_x, curr_y):
        self.curr_x = curr_x
        self.curr_y = curr_y
        self.path = path
        self.errorHistory = 0
        self.oldError = 0
        self.pathIndex = pathidx
        self.count_call= 0
        self.true_gainI= gainI

    def calc_dist(self):
        """
        returns the perpendicular distance from c1c0's current value to the line that c1c0 should be travelling on
        """
        return ptLineDist(self.curr_x, self.curr_y, self.path[self.pathIndex-1].x, self.path[self.pathIndex-1].y,
                          self.path[self.pathIndex].x, self.path[self.pathIndex].y)
        # b = self.path[self.pathIndex].x - self.path[self.pathIndex - 1].x
        # a = self.path[self.pathIndex].y - self.path[self.pathIndex - 1].y
        # den = 0
        # if a != 0 and b != 0:
        #     den = (b/a) + (a/b)
        # d = 0
        # if den != 0:
        #     c = self.path[self.pathIndex - 1].y - (a/b)*self.path[self.pathIndex - 1].x
        #     x = (self.curr_x + (b/a)*self.curr_x - self.path[self.pathIndex - 1].y + (a/b) *
        #          self.path[self.pathIndex - 1].x)/den
        #     y = (a/b)*x + c
        #     d = ((x - self.curr_x)**2 + (y - self.curr_y)**2)**(1/2)
        # return d


    def PID(self):
        """
        returns the control value function for the P, I, and D terms
        """
        self.count_call += 1
        error = self.calc_dist()
        der = error - self.oldError
        self.oldError = error
        self.errorHistory += error
        return (error * gaine) + (der * gaind) + (self.errorHistory * self.true_gainI)

    def update_PID(self, curr_x, curr_y):
        """
        updates the previous and current values
        """
        self.curr_x = curr_x
        self.curr_y = curr_y

    def newVec(self):
        """
        return the new velocity vector based on the PID value
        """
        velocity = (self.path[self.pathIndex].x - self.curr_x, self.path[self.pathIndex].y - self.curr_y)
        v = (self.path[self.pathIndex].x - self.path[self.pathIndex-1].x, self.path[self.pathIndex].y - self.path[self.pathIndex-1].y)
        mag = (v[0]**2 + v[1]**2)**(1/2)
        perpendicular = (0, 0)
        if mag > 0:
            perpendicular = (-v[1]/mag, v[0]/mag)
        c = self.PID()
        maxControl = 30
        if abs(c) > maxControl:
            c = c*maxControl/abs(c)
            print(c)
        return [c * a + b for a, b in zip(perpendicular, velocity)]
