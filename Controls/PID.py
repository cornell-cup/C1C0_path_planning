import math
from Constants.Consts import *

def ptLineDist(a,b,x1,y1,x2,y2):
    """Returns distance from (a,b) to line segment connecting (x1,y1)
    and (x2, y2)"""
    A= y1-y2
    B= x2-x1
    C= x1*y2-x2*y1
    if math.sqrt(A**2+B**2) == 0:
        return 0
    else:
        return (A*a+B*b+C)/(math.sqrt(A**2+B**2))

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
        self.count_call = 0
        self.true_gainI = gainI

    def calc_dist(self):
        """
        returns the perpendicular distance from c1c0's current value to the line that c1c0 should be travelling on
        """
        return ptLineDist(self.curr_x, self.curr_y, self.path[self.pathIndex-1].x, self.path[self.pathIndex-1].y,
                          self.path[self.pathIndex].x, self.path[self.pathIndex].y)

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

    def update_path_index(self, pathidx):
        self.pathIndex = pathidx
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
        # print('getting new vector from PID')

        velocity = (self.path[self.pathIndex].x - self.curr_x, self.path[self.pathIndex].y - self.curr_y)
        v = (self.path[self.pathIndex].x - self.path[self.pathIndex-1].x, self.path[self.pathIndex].y - self.path[self.pathIndex-1].y)
        mag_v = (v[0]**2 + v[1]**2)**(1/2)
        mag_velocity = math.sqrt(velocity[0]**2 + velocity[1]**2)
        # error = 0
        norm_velocity = (0, 0)
        if mag_velocity != 0:
            norm_velocity = (velocity[0]/mag_velocity, velocity[1]/mag_velocity)
        perpendicular = (0, 0)
        if mag_v != 0:
            perpendicular = (-v[1]/mag_v, v[0]/mag_v)
        c = self.PID()
        maxControl = 30
        if abs(c) > maxControl:
            c = c*maxControl/abs(c)
        c = c*.3 / 30
        # print(c)
        # print(f'the correction is {c}')
        return [c * a + b for a, b in zip(perpendicular, norm_velocity)]
